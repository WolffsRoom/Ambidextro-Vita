# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

spec_dir = Path(SPECPATH)
if spec_dir.is_file():
    spec_dir = spec_dir.parent
patch_data = spec_dir.parent / "patch_data" / "ambidextro_patch_data.zip"
a = Analysis(
    [str(spec_dir / "ambidextro_vita_patcher.py")],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=[(str(patch_data), ".")],
    hiddenimports=["bsdiff4", "PIL.WebPImagePlugin", "PIL.PngImagePlugin"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="AmbidextroVitaPatcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False, upx=False, console=True,
    disable_windowed_traceback=False,
    # Works in this development layout and in the published Patcher/src tree.
    icon=str(next(p for p in (
        spec_dir.parent.parent / "icon.ico",
        spec_dir.parent / "icon.ico"
    ) if p.is_file())),
)
