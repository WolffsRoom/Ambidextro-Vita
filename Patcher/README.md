# Ambidextro Vita — Windows Patcher

Port game-data generator for owners of the original [Ambidextro](https://store.steampowered.com/app/3445580/Ambidextro/) PC game.

## Download

See the [latest pre-release](https://github.com/WolffsRoom/Ambidextro-Vita/releases). The Windows ZIP contains the patcher executable plus open-source GDRE Tools 2.7.4.

## Supported source

- Godot 4.3 PC/Steam **Ambidextro v1.2.5**.
- Original file: **Ambidextro.pck**, SHA-256 **FCEB974DBA3C458255EFE04E2516CA88AF9E9DC7FABE6AD3A3D1815441214284**.
- Only this version is supported; other input hashes are rejected.

## How it works

1. Validates the source PCK by size and SHA-256.
2. Runs GDRE Tools 2.7.4 to recover the user's own Godot project data.
3. Copies unchanged files, applies binary diffs to modified resources, converts applicable GST2 WebP imported textures into Vita-compatible PNG payloads, and supplies the port-generated CRT masks and metadata.
4. Verifies the size and SHA-256 of **all 3,052** output files.
5. Installs into an isolated staging directory, then atomically renames to the user's destination. The user's Steam source is never modified.

Output: **VitaFiles/ambidextrovita/game_data/**. Copy the **ambidextrovita** folder to **ux0:data/** on your PS Vita and install the lightweight VPK from the same Release.

## Source / development files

- **src/ambidextro_vita_patcher.py**: command-line patcher, input validation, extraction, safe staging.
- **src/vita_ctex.py**: deterministic Godot GST2 WebP-to-PNG conversion.
- **src/build_patch_data.py**: developer-only delta generator (requires a local legitimate source PCK and local verified Vita game_data reference).
- **src/AmbidextroVitaPatcher.spec**: PyInstaller build definition.
- **src/package_release.py**: Windows distribution packager.
- **Build_Patcher.bat**: development build runner.

Required build dependencies: Python 3.12+, bsdiff4, Pillow, PyInstaller. To regenerate patch data, the developer also needs GDRE 2.7.4 and their own validated Steam input and reference output.

## Important

No commercial Ambidextro.pck, reconstructed game_data, music, levels, or game executable are distributed. The patcher is not a substitute for owning the game. You must supply the original source yourself.

GDRE Tools is distributed under the MIT license by bruvzg and the [GDRETools contributors](https://github.com/GDRETools/gdsdecomp); its license notice is included with the Windows ZIP.
