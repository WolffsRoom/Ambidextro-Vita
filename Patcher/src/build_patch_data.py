"""Build proprietary-free binary delta pack for Ambidextro PS Vita.

Developer-only: requires the locally recovered *original* PCK and the
verified Vita game_data tree. Never ship the source or target directory.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import struct
import sys
import zipfile
from pathlib import Path

import bsdiff4
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
SOURCE_PCK = ROOT / "SteamFiles" / "Ambidextro.pck"
BASELINE = ROOT / "work" / "patcher_recovery_test" / "steam_extracted"
REFERENCE = ROOT / "releases" / "latest" / "game_data"
DATA = BUILD / "patch_data"
VERSION = "1.0"
VITA_BUILD = "ambidextro-gxm-20261014T053722Z"
PCK_SHA256 = "fceb974dba3c458255efe04e2516ca88af9e9dc7fabe6ad3a3d1815441214284"
PREFIX = "entries/"
GDRE_VERSION = "2.7.4"


def digest(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def convert_ctex(raw: bytes) -> bytes | None:
    """Convert the Godot 4 GST2 WebP payload to PNG for GXM, byte-stable."""
    if not raw.startswith(b"GST2") or len(raw) < 56:
        return None
    dataformat, width, height, mips, imageformat = struct.unpack_from("<IHHII", raw, 36)
    if dataformat != 2 or imageformat not in (0, 1, 2, 3, 4, 5):
        return None
    try:
        cursor = 52
        out = bytearray(raw[:52])
        struct.pack_into("<I", out, 36, 1)
        # GST2 data-version flag used by Godot's imported PNG variant.
        out[19] = 12
        for i in range(mips + 1):
            size = struct.unpack_from("<I", raw, cursor)[0]
            cursor += 4
            chunk = raw[cursor:cursor + size]
            cursor += size
            if len(chunk) != size or chunk[:4] != b"RIFF" or chunk[8:12] != b"WEBP":
                return None
            image = Image.open(io.BytesIO(chunk))
            image.load()
            if image.size != (max(1, width >> i), max(1, height >> i)):
                return None
            image = image.convert({0: "L", 1: "LA", 2: "L", 3: "LA", 4: "RGB", 5: "RGBA"}[imageformat])
            b = io.BytesIO()
            image.save(b, format="PNG", optimize=True)
            png = b.getvalue()
            out += struct.pack("<I", len(png) + 4) + b"PNG " + png
        if cursor != len(raw):
            return None
        return bytes(out)
    except (OSError, ValueError, EOFError, IndexError, struct.error):
        return None


def validate_inputs() -> None:
    assert SOURCE_PCK.is_file(), SOURCE_PCK
    if digest(SOURCE_PCK) != PCK_SHA256:
        raise RuntimeError("O PCK original mudou; gere um novo manifest apos revisar a versao.")
    for required in ("gdre_export.log", "project.godot", "scenes/main/main_scene.tscn"):
        if not (BASELINE / required).is_file():
            raise RuntimeError(f"Baseline de recovery ausente: {required}")
    assert REFERENCE.is_dir(), REFERENCE


def make() -> None:
    validate_inputs()
    DATA.mkdir(parents=True, exist_ok=True)
    patchzip = DATA / "ambidextro_patch_data.zip"
    manifest = {
        "format": 1,
        "patcher_version": VERSION,
        "title": "Ambidextro Vita",
        "steam_version": "PC/Steam 1.2.5 (Godot 4.3)",
        "supported_pck": {"filename": "Ambidextro.pck", "size": SOURCE_PCK.stat().st_size, "sha256": PCK_SHA256},
        "required_gdre_version": GDRE_VERSION,
        "vita_runtime": VITA_BUILD,
        "output_prefix": "ambidextrovita/game_data",
        "files": {}
    }
    counts = {"copy": 0, "patch": 0, "embedded": 0, "convert_ctex_png": 0}
    totals = {"copied_bytes": 0, "patch_bytes": 0, "embedded_bytes": 0}
    with zipfile.ZipFile(patchzip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for i, dest in enumerate(sorted(p for p in REFERENCE.rglob("*") if p.is_file())):
            relative = dest.relative_to(REFERENCE).as_posix()
            # GDRE full recovery does not recreate Godot's compiled CSV
            # translation resources. Their source is the original Steam CSV.
            # Build binary deltas FROM that user-owned file (like VoidStranger
            # patches from the original data.win), never embed the translation.
            csv_derived = (relative == "assets/texts/text.csv.import" or
                relative.startswith("assets/texts/text.") and relative.endswith(".translation") or
                relative.startswith(".godot/imported/text.csv-") and relative.endswith(".md5"))
            source_rel = "assets/texts/text.csv" if csv_derived else relative
            orig = BASELINE / source_rel
            want = dest.read_bytes()
            info = {"size": len(want), "sha256": hashlib.sha256(want).hexdigest()}
            if orig.is_file():
                existing = orig.read_bytes()
                info["input_sha256"] = hashlib.sha256(existing).hexdigest()
                if source_rel != relative:
                    info["source"] = source_rel
                if existing == want:
                    info["method"] = "copy"
                    totals["copied_bytes"] += len(want)
                else:
                    converted = convert_ctex(existing) if relative.endswith(".ctex") else None
                    if converted == want:
                        info["method"] = "convert_ctex_png"
                    else:
                        delta = bsdiff4.diff(existing, want)
                        info["method"] = "patch"
                        name = PREFIX + f"{i:04d}.bsdiff"
                        info["blob"] = name
                        z.writestr(name, delta)
                        totals["patch_bytes"] += len(delta)
            else:
                # Missing entries are custom Vita CRT masks, Godot-generated
                # UIDs/import metadata, and our own new main_scene.gd.
                # Never embed large proprietary PC assets.
                if not (relative.startswith("assets/vita_crt/") or
                        relative.startswith(".godot/imported/crt_mask_") or
                        relative.endswith((".gd.uid", ".gdshader.uid")) or
                        relative == "scenes/main/main_scene.gd"):
                    raise RuntimeError(f"Unrecognized new asset (possible commercial file): {relative}")
                info["method"] = "embedded"
                name = PREFIX + f"{i:04d}.new"
                info["blob"] = name
                z.writestr(name, want)
                totals["embedded_bytes"] += len(want)
            counts[info["method"]] += 1
            manifest["files"][relative] = info
        manifest["statistics"] = {"files": len(manifest["files"]), "methods": counts, **totals}
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    print("PATCH_DATA", patchzip, "bytes", patchzip.stat().st_size)
    print("METHODS", counts, "TOTALS", totals)
    print("PATCH_SHA256", digest(patchzip))
    # Development manifest (not a full game folder).
    (DATA / "build_report.json").write_text(json.dumps({
        "patch_data_sha256": digest(patchzip),
        "patch_data_bytes": patchzip.stat().st_size,
        "pck_sha256": PCK_SHA256,
        "statistics": manifest["statistics"]
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    make()
