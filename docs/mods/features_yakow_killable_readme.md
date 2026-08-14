# Mod Readme — Yakow Killable & Behaviors (Jak 2)

> **Game:** Jak 2  
> **Branch:** `features_yakow_killable`  
> **Target Entity:** `yakow` (`goal_src/jak2/levels/city/farm/yakow.gc`)

---

## 1. Description & Features

This mod enhances the Yakow animals located in the Hip Hog farm in Jak 2 by bringing back authentic Jak 1-style behaviors and adding a combat/death loop:

- **Jak 1-Style Behaviors:**
  - **Flee Mechanic (`run-away`):** When approached or attacked by Jak, Yakows turn and flee in the opposite direction.
  - **Graze System (`graze` / `graze-kicked`):** Yakows alternate between idle grazing and active walking.
  - **Kick Reaction (`kicked`):** Authentic animation selection between traveling kick (`yakow-kicked-ja`) and stationary kick (`yakow-kicked-in-place-ja`) depending on movement vector.
- **Combat & Death Mechanic (`die`):**
  - Yakows have 4 hit points (`default-hit-points = 4`).
  - Upon death, the Yakow drops **6 dark eco pills** dispersed around its position.
  - Triggers a death dust poof particle effect (`group-land-poof-drt`) and plays sound `"enemy-fizz"`.

---

## 2. Technical Architecture & Modifications

- **Modified Files:**
  - `goal_src/jak2/levels/city/farm/yakow.gc`: Added `run-away`, `graze`, `graze-kicked`, `die` states, adjusted collision and `damage-amount-from-attack` to 1.
  - `decompiler/config/jak2/jak2_config.jsonc`: Animation config bindings.
  - Custom assets under `custom_assets/jak2/levels/cityfarmb/`.

---

## 3. How to Test & Play

1. Set the active game to Jak 2:
   ```bash
   task set-game-jak2
   ```
2. Hot-recompile in REPL:
   ```lisp
   (mi)
   ```
3. Boot the game and travel to the Hip Hog farm in Haven City:
   ```bash
   task boot-game
   ```
4. Attack a Yakow with melee punches/spins or weapons to observe the kick animation, fleeing behavior, and dark eco drop on defeat.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2025-07-19 | `goal_src/jak2/levels/city/farm/yakow.gc` | Added Jak 1-style states (`run-away`, `graze`, `graze-kicked`, `die`), added tracking fields (`grazing`, `walk-run-blend`, `run-mode`, `home-base`), set `damage-amount-from-attack` to 1. | Recreate Jak 1 Yakow behaviors in Jak 2 with dark eco drop. |
| 2026-08-13 | `goal_src/jak2/levels/city/farm/yakow.gc` | Polished `kicked` state (traveling vs in-place kick based on nav travel), raised HP to 4 hits, drop 6 dark eco pills, replaced particle effect with `group-land-poof-drt`. | Authentic Jak 1 feel, robust death VFX and balanced reward. |
