# Development status — Ambidextro for PS Vita

**Public status: v0.1.0 Beta 1 — experimental pre-release available.**

These are development tests, not guarantees about a release build.

| Area | Status | Notes |
| --- | --- | --- |
| Boot | Working on physical Vita | 960×544 animated splash and native GXM |
| Main menus | Working in tests | Navigation, video and display options |
| Gameplay | Playable, undergoing optimization | Frame drops in heavier rooms |
| Graphics | Experimental native GXM 2D | Shader and CanvasGroup limitations |
| Audio | Implemented and under observation | Playback and music transitions |
| Save/settings | Implemented | Regression testing ongoing |
| Exit to LiveArea | Pending device verification | Native exit path compiled locally |
| PC-to-Vita patcher | v1.0 Windows | Tested with original Steam 1.2.5 input |
| Public downloadable build | First beta | Lite VPK and source-to-Vita patcher, no commercial game files |

## Performance

Some scenes approach 60 FPS, while heavier rooms and transitions still drop frames. Native rendering work has included batching, texture lookup caching, transforms and screen-space culling. Sustained 60 FPS has **not** been confirmed.

## In testing (next build, not released)

Internal build PCK2 (2026-10-28), waiting for hardware results. It replaces PCK1, which made no visible difference on hardware and caused audio crackling.

- **Newer runtime:** the port now uses the same Godot 4 Vita 2D runtime as the Tenebrarium port. Audio is mixed like the Godot 3 Vita driver (44.1 kHz, small blocks), the GDScript VM is compiled for speed, SubViewports render to real GPU targets, and tiles outside the screen are skipped.
- **Faster first load:** the music (87 MB) no longer loads before the main menu. It loads in the background after the menu appears, or when a level needs it. On PC the main scene now loads in about a third of the time.
- **Packed game data:** game files ship as a single `game.pck` (about 112 MB). Scenes are binary and scripts are pre-tokenized.
- **Boot:** the 30 FPS boot animation plays all 180 frames, and its last frame stays on screen while the game loads instead of a black screen.
- **Known issue under investigation:** restarting a level stalls for about 4 seconds in the first physics step of the new level.

## Known issues

- Desktop CanvasGroup composition and unsupported shaders can change the opening cutscene on Vita.
- Additional performance profiling and loading/restart optimizations are required.
- LiveArea exit behavior needs final on-device confirmation.
- The patcher must validate legal PC game input and reproduce the correct Vita data layout before any public release.

## Public files policy

This repository contains documentation and real-device screenshots only. No VPK, compiled port, proprietary game files, commercial audio/art bundles, imported game caches or unvalidated patcher are provided.

## References

- [Ambidextro on Steam](https://store.steampowered.com/app/3445580/Ambidextro/)
- [Godot 4 Vita](https://github.com/WolffsRoom/godot4-vita)
- [README](../README.md)
