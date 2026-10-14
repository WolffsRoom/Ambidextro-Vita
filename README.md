<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/AmbidextroVita.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/brand/Ambidextro-Vita-Black.png">
    <img src="assets/brand/Ambidextro-Vita-Black.png" alt="Ambidextro Vita" width="280">
  </picture>
</p>
<img width="3840" height="1732" alt="VitaLayout" src="https://github.com/user-attachments/assets/6cd76352-2fd6-4e70-a2ef-30473c1de45b" />

<p align="center">
  An experimental, unofficial port of <a href="https://store.steampowered.com/app/3445580/Ambidextro/"><strong>Ambidextro</strong></a> for PlayStation Vita.
</p>

<p align="center">
  <em>Powered by a customized <a href="https://github.com/WolffsRoom/godot4-vita">Godot 4 Vita</a> runtime, with native GXM 2D rendering.</em>
</p>

> [!IMPORTANT]
> **Work in progress!**
> No public release or patcher is available yet. This repository currently contains documentation and screenshots only. It does **not** provide a VPK, game files, or a playable download. A legally obtained PC copy of *Ambidextro* will be required once the patcher is ready.

## Project status

<div align="center">
  <img src="https://img.shields.io/badge/STATE-IN%20DEVELOPMENT-ffc107?style=for-the-badge" alt="In development">
  <img src="https://img.shields.io/badge/TESTING-REAL%20PS%20VITA-377bb5?style=for-the-badge" alt="Testing on PS Vita">
  <br>
  <img src="https://img.shields.io/badge/PATCHER-WIP-ff9800?style=for-the-badge" alt="Patcher in development">
  <img src="https://img.shields.io/badge/RELEASE-NOT%20AVAILABLE-555555?style=for-the-badge" alt="No public release yet">
  <img src="https://img.shields.io/badge/ENGINE-GODOT%204%20%2B%20GXM-478cbf?style=for-the-badge&logo=godotengine&logoColor=white" alt="Godot 4 and native GXM">
</div>

<br>

The port currently boots and runs on real PS Vita hardware. Menu navigation, gameplay, audio and save/settings systems are under active testing. **Performance is not yet stable at 60 FPS**, and some effects in the opening cutscene still require GXM compatibility fixes.

| Component | Current state |
| :--- | :--- |
| Boot / LiveArea | Animated 960 × 544 startup and in-game boot working, return to LiveArea is being verified |
| Gameplay | Playable on physical hardware, further compatibility and performance testing in progress |
| Rendering | Native GXM 2D backend, remaining shader and <code>CanvasGroup</code> limitations |
| Audio | Music playback and transitions implemented, regression testing ongoing |
| Video settings | FPS cap (30 / 40 / 60 / Unlocked), software brightness and Screen Effects submenu |
| Performance | 60 FPS in some scenes, drops remain in heavier gameplay and during transitions |
| PC-to-Vita patcher | **Not ready**, being designed and validated |
| Public VPK / Release | **Not published** |

See [development status and known issues](docs/PORT_STATUS.md) for details. These are development milestones, **not** a claim that the full game has passed end-to-end testing.

## About the port

*Ambidextro* is a precision platformer by **Majorariatto** in which you control two halves of a wizard independently. This project explores running the original game's Godot content through a PlayStation Vita-specific runtime rather than recreating its gameplay in a different engine.

The Vita implementation uses a customized Godot 4.x runtime and direct GXM drawing for 2D graphics. Platform-specific work includes controller integration, memory management, texture handling, boot animation, audio adjustments, settings, and performance profiling.

This is an **unofficial fan project**, not affiliated with or endorsed by Majorariatto, Sony, or the Godot Engine project.

## Screenshots 

<p align="center">
  <a href="assets/prints/2026-10-14-022906-629907.png"><img src="assets/prints/2026-10-14-022906-629907.png" alt="Ambidextro Vita LiveArea" width="65%"></a>
</p>
<p align="center">
  <a href="assets/prints/2026-10-14-023009-436260.png"><img src="assets/prints/2026-10-14-023009-436260.png" alt="Ambidextro Vita main menu" width="48%"></a>
  <a href="assets/prints/2026-10-14-023048-474905.png"><img src="assets/prints/2026-10-14-023048-474905.png" alt="Ambidextro Vita gameplay" width="48%"></a>
</p>
<p align="center">
  <a href="assets/prints/2026-10-14-023016-309599.png"><img src="assets/prints/2026-10-14-023016-309599.png" alt="Ambidextro Vita level selection" width="48%"></a>
  <a href="assets/prints/2026-10-14-023054-814698.png"><img src="assets/prints/2026-10-14-023054-814698.png" alt="Ambidextro Vita FPS, brightness and effects options" width="48%"></a>
</p>
<p align="center">
  <a href="assets/prints/2026-10-14-023029-076185.png"><img src="assets/prints/2026-10-14-023029-076185.png" alt="Ambidextro Vita gameplay and performance overlay" width="48%"></a>
  <a href="assets/prints/2026-10-14-023117-503942.png"><img src="assets/prints/2026-10-14-023117-503942.png" alt="Ambidextro Vita opening cutscene" width="48%"></a>
</p>
<p align="center">
<sub>Captured during development on PS Vita. Screenshots may show debugging overlays, incomplete effects, or performance that differs from later builds.</sub>
</p>

## Planned installation and patcher

The patcher is **still in development**, so the steps below describe the intended layout and **are not installation instructions for a released build**.

The goal is to let owners use files from their own legitimate [Ambidextro PC / Steam installation](https://store.steampowered.com/app/3445580/Ambidextro/) to prepare the Vita-compatible external game data. The intended target directory is:

<pre>ux0:data/ambidextrovita/game_data/</pre>

**Do not download unrelated game-data packages from third-party sites.** The patcher will be documented and published only after its output has been verified. No original commercial game data, soundtrack, or other proprietary assets are distributed through this repository.

## Current development priorities

- Finish and validate the PC-to-Vita patcher.
- Improve FPS consistency and reduce stage-loading/restart stalls.
- Resolve remaining cutscene alpha, shader and CanvasGroup rendering differences.
- Verify the in-game **Exit → LiveArea** path and settings on real hardware.
- Complete stability and end-to-end gameplay testing before publishing a release.

## Technical background

This port is built around [Godot 4 Vita](https://github.com/WolffsRoom/godot4-vita), [VitaSDK](https://vitasdk.org), a native [GXM](https://www.psdevwiki.com/vita/SceGxm) rendering path and Vita runtime integrations. It currently targets a Godot 4.8 development build adapted for the Vita.

Unlike the original PC renderer, the Vita renderer has specific limitations. Not every desktop shader or compositing effect is supported yet. Screenshots and performance results should be understood as work-in-progress.

## AI Notice

GPT-5.6 Sol through Codex was used as a development assistant for diagnostics, implementation support, project organization and technical documentation. 

## Credits

- [Majorariatto - Ambidextro](https://store.steampowered.com/app/3445580/Ambidextro/): original game, characters, artwork, sound, and design.
- [Godot Engine](https://godotengine.org): original engine.
- [WolffsRoom / Godot 4 Vita](https://github.com/WolffsRoom/godot4-vita): experimental Vita runtime and rendering backend.
- [VitaSDK](https://vitasdk.org) and the wider PS Vita homebrew development community.

---
<p align="center">
<em>This repository is documentation-only during development.
The original game and all of its associated intellectual property remain the property of their respective rights holders.</em>
<p>
