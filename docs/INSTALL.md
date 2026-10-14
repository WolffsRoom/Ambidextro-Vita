# Installing Ambidextro Vita beta

Download both beta assets from [Releases](https://github.com/WolffsRoom/Ambidextro-Vita/releases): the lite VPK and the Windows patcher ZIP.

1. Extract the patcher ZIP on Windows. Keep **GDRE** next to **AmbidextroVitaPatcher.exe**.
2. Run the EXE, point it to your legitimate PC/Steam Ambidextro installation folder (or directly to Ambidextro.pck). The tested supported PC version is **1.2.5**.
3. The patcher generates and verifies **3,052** files inside **VitaFiles/ambidextrovita/game_data/**.
4. Copy **VitaFiles/ambidextrovita/** to **ux0:data/** with VitaShell; the resulting path must be **ux0:data/ambidextrovita/game_data/**.
5. Install the **AmbidextroVita-v0.1.0-beta.1.vpk** using VitaShell.

The patcher does not modify the Steam game or ship a playable copy. There is no need to install a full VPK or download pre-generated game_data from third-party sites.

On-device logs are stored inside **ux0:data/ambidextrovita/logs/**. Stable 60 FPS is not guaranteed in demanding rooms; shader/CanvasGroup cutscene support remains experimental. Exit to LiveArea and the latest direct menu boot await final physical-console retesting.

See [Patcher](../Patcher/README.md) and [Development Status](PORT_STATUS.md).
