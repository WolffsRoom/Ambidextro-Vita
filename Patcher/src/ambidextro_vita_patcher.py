"""Ambidextro Vita Patcher v1.0.

Works from the purchaser's Ambidextro.pck (Godot 4.3 game).
Like Void Stranger Vita's patcher, it validates source and generated
file SHA-256, writes through staging, and never embeds the full game.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import bsdiff4
from PIL import Image

# Shared offline conversion implementation is intentionally bundled in src/
from vita_ctex import convert_ctex

VERSION = "1.0"
EXPECTED_LAYOUT = "ambidextrovita/game_data"


def digest(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def app_dir() -> Path:
    return Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent


def source_zip() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    for p in [base / "ambidextro_patch_data.zip", base / "patch_data" / "ambidextro_patch_data.zip"]:
        if p.is_file():
            return p
    raise FileNotFoundError("Pacote de patches nao encontrado (ambidextro_patch_data.zip).")


def clean_path(value: str) -> Path:
    return Path(value.strip().lstrip("\ufeff").strip("'").strip('"')).expanduser().resolve()


def get_pck(path: Path) -> Path:
    if path.is_file() and path.name.lower() == "ambidextro.pck":
        return path
    if path.is_dir():
        possible = (path / "Ambidextro.pck", path / "Ambidextro" / "Ambidextro.pck")
        for p in possible:
            if p.is_file():
                return p
    raise ValueError("Selecione a instalacao oficial do Ambidextro ou seu arquivo Ambidextro.pck.")


def get_gdre(explicit: str | None) -> Path:
    if explicit:
        path = clean_path(explicit)
        if path.is_file():
            return path
        raise FileNotFoundError("gdre_tools.exe nao encontrado: " + str(path))
    for root in [app_dir(), app_dir().parent, Path.cwd()]:
        for relative in ("GDRE/gdre_tools.exe", "Tools/GDRE/gdre_tools.exe", "gdre_tools.exe"):
            path = root / relative
            if path.is_file():
                return path
    p = shutil.which("gdre_tools") or shutil.which("gdre_tools.exe")
    if p:
        return Path(p)
    raise FileNotFoundError(
        "GDRE Tools 2.7.4 nao encontrado. Coloque a pasta GDRE ao lado do patcher "
        "ou use --gdre C:\\caminho\\gdre_tools.exe.")


def safe_file(name: str) -> Path:
    rel = PurePosixPath(name)
    if (rel.is_absolute() or ".." in rel.parts or
            not rel.parts or any(":" in part or "\\" in part for part in rel.parts)):
        raise ValueError(f"Caminho malformado dentro do manifesto: {name!r}")
    return Path(*rel.parts)


def check_directory_overlap(path: Path, pck: Path) -> None:
    steam = pck.parent.resolve()
    if path == steam or steam in path.parents:
        raise ValueError("Por seguranca, escolha um destino fora da instalacao original do jogo.")


def read_patch_manifest(z: zipfile.ZipFile) -> dict:
    info = json.loads(z.read("manifest.json"))
    if info.get("format") != 1 or info.get("output_prefix") != EXPECTED_LAYOUT:
        raise ValueError("Pacote de patches incompatível com esta versao do patcher.")
    if len(info.get("files", {})) < 3000:
        raise ValueError("Manifesto incompleto.")
    for name, spec in info["files"].items():
        safe_file(name)
        method = spec.get("method")
        if method not in ("copy", "convert_ctex_png", "patch", "embedded"):
            raise ValueError("Metodo desconhecido no pacote: " + str(method))
        if method in ("patch", "embedded"):
            blob = spec.get("blob", "")
            if not blob.startswith("entries/") or safe_file(blob).as_posix() not in z.namelist():
                raise ValueError("Patch ausente ou invalido: " + name)
    return info


def verify_gdre(binary: Path, version: str) -> None:
    proc = subprocess.run([str(binary), "--headless", "--version"], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=30)
    combined = proc.stdout + proc.stderr
    # GDRE Tools 2.7.4 returns code 1 for informational --version.
    # Check its actual version banner, not this non-standard exit status.
    if version not in combined or "Godot RE Tools" not in combined or proc.returncode not in (0, 1):
        raise ValueError(f"GDRE Tools {version} necessario. Detectado: {combined[:350]!r}")


def recover_game(pck: Path, gdre: Path, destination: Path, log: Path) -> None:
    print("  Extraindo e reconstruindo projeto Godot a partir da copia do usuario...", flush=True)
    with log.open("w", encoding="utf-8", errors="replace") as stream:
        p = subprocess.run(
            [str(gdre), "--headless", "--recover=" + str(pck), "--output=" + str(destination)],
            cwd=str(pck.parent), stdout=stream, stderr=subprocess.STDOUT, timeout=900, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"GDRE falhou ({p.returncode}). Consulte: {log}")
    export_log = destination / "gdre_export.log"
    if not export_log.is_file() or not (destination / "project.godot").is_file():
        raise RuntimeError(f"Recuperacao incompleta. Consulte: {log}")
    status = export_log.read_text(errors="replace")
    if "Scripts not decompiled:                 0" not in status:
        raise RuntimeError("Ha scripts nao recuperados; dados de entrada incompativeis.")
    if "Failed conversions:                     0" not in status:
        raise RuntimeError("Ha recursos cuja conversao falhou; dados de entrada incompativeis.")


def convert_and_patch(extracted: Path, data: Path, z: zipfile.ZipFile, specs: dict) -> dict:
    stats = {"copy": 0, "patch": 0, "embedded": 0, "convert_ctex_png": 0}
    for n, (rel, spec) in enumerate(specs.items(), 1):
        relative = safe_file(rel)
        original = extracted / safe_file(spec.get("source", rel))
        target = data / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        kind = spec["method"]
        if kind == "embedded":
            result = z.read(spec["blob"])
            target.write_bytes(result)
        else:
            if not original.is_file():
                raise ValueError(f"Arquivo original nao recuperado: {rel}")
            # Verify specific recovered files for deterministic GDRE 2.7.4 behavior.
            original_digest = digest(original)
            if original_digest != spec["input_sha256"]:
                raise ValueError(
                    "Recurso diferente da versao de referencia: " + rel +
                    " (verifique GDRE 2.7.4 e versao Steam 1.2.5).")
            if kind == "copy":
                shutil.copy2(original, target)
            elif kind == "patch":
                result = bsdiff4.patch(original.read_bytes(), z.read(spec["blob"]))
                target.write_bytes(result)
            elif kind == "convert_ctex_png":
                result = convert_ctex(original.read_bytes())
                if result is None:
                    raise ValueError(f"Nao foi possivel converter GST2 para PNG: {rel}")
                target.write_bytes(result)

        if target.stat().st_size != spec["size"] or digest(target) != spec["sha256"]:
            raise ValueError(f"Hash ou tamanho inesperado na saida: {rel}")
        stats[kind] += 1
        if n % 300 == 0 or n == len(specs):
            print(f"\r  Gerando e validando game_data: {n:4}/{len(specs)} ({100*n//len(specs):3}%)", end="", flush=True)
    print()
    return stats


def generate(pck: Path, output_root: Path, gdre: Path, force: bool) -> tuple[Path, dict]:
    pck = pck.resolve()
    output_root = output_root.resolve()
    check_directory_overlap(output_root, pck)
    package = source_zip()
    with zipfile.ZipFile(package) as z:
        manifest = read_patch_manifest(z)
        if pck.stat().st_size != manifest["supported_pck"]["size"] or digest(pck) != manifest["supported_pck"]["sha256"]:
            raise ValueError(
                "Ambidextro.pck nao corresponde a versao Steam/PC 1.2.5 suportada. "
                "Este patcher nao aceita outras builds do jogo.")
        verify_gdre(gdre, manifest["required_gdre_version"])

        output_root.mkdir(parents=True, exist_ok=True)
        dest = output_root / "ambidextrovita"
        if dest.exists() and not force:
            raise FileExistsError(f"Destino ja existe: {dest}. Escolha outra pasta ou passe --force.")

        print("Fonte Steam validada por SHA-256.")
        print("GDRE 2.7.4 validado.")
        with tempfile.TemporaryDirectory(prefix="ambidextrovita-patcher-", dir=output_root) as temporary:
            stage = Path(temporary)
            source = stage / "recovered"
            folder = stage / "ambidextrovita"
            out = folder / "game_data"
            gdre_log = stage / "gdre-recovery.log"
            source.mkdir()
            out.mkdir(parents=True)
            recover_game(pck, gdre, source, gdre_log)
            stats = convert_and_patch(source, out, z, manifest["files"])
            expected = len(manifest["files"])
            generated = sum(p.is_file() for p in out.rglob("*"))
            if generated != expected:
                raise ValueError(f"Numero de arquivos divergente ({generated} != {expected}).")
            report = {
                "patcher_version": VERSION,
                "game_pck_sha256": manifest["supported_pck"]["sha256"],
                "vita_runtime": manifest["vita_runtime"],
                "verified_game_data_files": generated,
                "methods": stats,
                "install_dir": "ux0:data/ambidextrovita/game_data/"
            }
            (folder / "patcher-report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
            with (folder / "manifest-sha256.txt").open("w", encoding="utf-8") as f:
                for name, entry in manifest["files"].items():
                    f.write(f"{entry['sha256']} *game_data/{name}\n")
            # Atomic rename of complete data only; stale user folders are
            # never partially modified. On overwrite, retain a rollback copy.
            backup = output_root / "ambidextrovita.previous"
            if dest.exists():
                if backup.exists():
                    raise FileExistsError(f"Backup antigo ja existe: {backup}. Mova-o antes de usar --force.")
                os.replace(dest, backup)
            try:
                os.replace(folder, dest)
            except Exception:
                if backup.exists() and not dest.exists():
                    os.replace(backup, dest)
                raise
            return dest, report


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Ambidextro Vita Patcher — Steam 1.2.5 -> game_data")
    parser.add_argument("--steam", help="Pasta Steam contendo Ambidextro.pck (ou o arquivo .pck)")
    parser.add_argument("--output", help="Diretorio base de destino (cria ambidextrovita/game_data)")
    parser.add_argument("--gdre", help="Caminho para gdre_tools.exe 2.7.4")
    parser.add_argument("--force", action="store_true", help="Faz backup da pasta anterior e a substitui")
    parser.add_argument("--non-interactive", action="store_true", help="Nao aguarda entrada do usuario")
    args = parser.parse_args()
    try:
        print("="*68)
        print(" AMBIDEXTRO VITA PATCHER v1.0 — Windows")
        print("="*68)
        print(" Requer Ambidextro PC/Steam 1.2.5 comprado legalmente.")
        print(" O patcher nao distribui os arquivos do jogo original.\n")
        steam_value = args.steam
        if not steam_value:
            if args.non_interactive:
                raise ValueError("Informe --steam.")
            steam_value = input("Arraste a pasta do jogo ou Ambidextro.pck para a janela:\n> ")
        pck = get_pck(clean_path(steam_value))
        output = clean_path(args.output) if args.output else app_dir() / "VitaFiles"
        gdre = get_gdre(args.gdre)
        print(f"\n Steam PCK: {pck}\n GDRE:      {gdre}\n Saida:     {output / 'ambidextrovita'}\n")
        destination, report = generate(pck, output, gdre, args.force)
        print("\nSUCESSO: arquivos do Vita gerados e verificados por SHA-256.")
        print(f"Destino: {destination}")
        print("Copie a pasta ambidextrovita para ux0:data/ no Vita.")
        print("Instale o VPK leve da mesma versao.")
        print("Arquivos:", report["verified_game_data_files"])
        if not args.non_interactive and sys.stdin.isatty():
            input("\nPressione ENTER para sair...")
        return 0
    except Exception as error:
        print(f"\nFALHA: {error}", file=sys.stderr)
        if not args.non_interactive and sys.stdin.isatty():
            input("\nPressione ENTER para sair...")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
