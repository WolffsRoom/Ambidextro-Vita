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
