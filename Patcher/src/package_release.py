"""Stage verified redistributable tools and patcher without any game_data."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BUILD = Path(__file__).resolve().parents[1]
PKG = ROOT / "Patcher" / "release-v1.0"
GDRE = ROOT / "Tools" / "GDRE"
exe = BUILD / "dist" / "AmbidextroVitaPatcher.exe"
assert exe.is_file() and exe.stat().st_size > 2_000_000
assert (BUILD / "patch_data" / "ambidextro_patch_data.zip").is_file()
license_path = BUILD / "LICENSE-GDRE-MIT.txt"
assert license_path.is_file()
PKG.mkdir(parents=True,exist_ok=True)
out = PKG / "AmbidextroVitaPatcher-v1.0-Windows.zip"
docs = [BUILD / "README.txt", license_path]
for p in docs:
    assert p.exists(),p
with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    z.write(exe,exe.name)
    for p in docs:
        z.write(p,p.name)
    for name in ["gdre_tools.exe","gdre_tools.pck","GodotMonoDecompNativeAOT.dll"]:
        p=GDRE/name
        assert p.is_file(),p
        z.write(p,"GDRE/"+name)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={
      "AmbidextroVitaPatcher.exe","README.txt","LICENSE-GDRE-MIT.txt",
      "GDRE/gdre_tools.exe","GDRE/gdre_tools.pck","GDRE/GodotMonoDecompNativeAOT.dll"}
m={
"package":out.name,"bytes":out.stat().st_size,
"sha256":hashlib.file_digest(out.open("rb"),"sha256").hexdigest(),
"exe_bytes":exe.stat().st_size,
"exe_sha256":hashlib.file_digest(exe.open("rb"),"sha256").hexdigest(),
"game_data_distributed":False,
"contains_original_steam_pck":False,
"gdre_version":"2.7.4",
}
(PKG/"package-manifest.json").write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
print("PATCHER_RELEASE_PACKAGE",out)
print(json.dumps(m,indent=2))
