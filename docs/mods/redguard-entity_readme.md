# Mod Readme — Crimson Redguard Entity (Jak 3)

> **Game:** Jak 3  
> **Branch:** `jak3/features/redguard-entity`  
> **Target Subsystems:** Traffic Guards (`goal_src/jak3/levels/city/traffic/citizen/guard.gc`), Level `ctypesa` DGO, Custom Model Pipeline (`custom_assets/jak3/models/`)

---

## 1. Description & Features

This mod introduces the **Crimson Redguard** custom entity to Haven City in Jak 3:

- **Red Freedom Faction Guard:** A red-armored guard variant inspired by the classic Krimzon Guard aesthetic, patrolling alongside blue Freedom Faction guards and yellow Dark Guards in Haven City.
- **Exclusive City Mode Integration:** Appears dynamically when City Mode is set to `"Jak 2"` via a 3-way random spawner roll (`blue` / `dark-guard` / `red-guard`).
- **Non-Destructive Mesh Overriding:** Uses a dedicated high-fidelity 3D model (`crimson-redguard-lod0.glb`) while seamlessly reusing the existing `skel-crimson-guard` joint and animation tree without duplicating memory buffers.

---

## 2. Technical Architecture & Modifications

- **Custom Assets & Models:**
  - `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb`: Custom red geometry and textures injected into level `ctypesa`.
  - `goal_src/jak3/dgos/ctypesa.gd`: Registered `crimson-redguard-ag.go`.
  - `goal_src/jak3/game.gp`: Declared `(build-actor "crimson-redguard")` with file-entry map registration.
- **GOAL Logic:**
  - `goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc`: Added `citizen-flag red-guard` bit.
  - `goal_src/jak3/levels/city/traffic/citizen/guard.gc`: Implemented 3-way random spawner distribution in `citizen-method-194` and dynamic `mgeo` overriding in `crimson-guard-method-267`.

---

## 3. How to Test & Play

1. Set active game to Jak 3:
   ```bash
   task set-game-jak3
   ```
2. Run extraction to compile custom model assets:
   ```bash
   task extract
   ```
3. Recompile the game in REPL (`task repl`):
   ```lisp
   (mi)
   ```
4. Boot the game:
   ```bash
   task boot-game
   ```
5. In the PC Debug Menu (`R3`), navigate to **`City Mods`** and select **`Mode Jak 2`**.
6. Travel to Haven City South (`ctypesa`) to encounter patrolling Crimson Redguards.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) in PC Debug Menu. | Implement City Behavior modes. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Added `'default` post-game city mode to Debug Menu. | Provide full end-game spawn behavior option. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extended move-to-ground vertical search radius to 40m in citizen.gc and civilian.gc, appended 'ctypepa to *territory-list*. | Fix vehicle hijack pilot ejection and guarantee ctypepa RAM retention. |
| 2026-08-11 | `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb`<br>`goal_src/jak3/game.gp`<br>`goal_src/jak3/dgos/ctypesa.gd`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/guard.gc` | Added custom Crimson Redguard model into `ctypesa`, configured actor build in `game.gp`, added `citizen-flag red-guard`, and implemented random 3-way guard roll with mesh override in `guard.gc`. | Add new Crimson Redguard entity variant in City Mode "Jak 2". |
