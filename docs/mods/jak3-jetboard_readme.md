# Mod Readme — Jak 3 Jetboard Mechanics Port to Jak 2

> **Game:** Jak 2  
> **Branch:** `jak2/features/jak3-jetBoard`  
> **Target Subsystem:** Target Jetboard (`goal_src/jak2/engine/target/board/`) & Sound Bank / Art Group Pipelines

---

## 1. Description & Features

This mod ports three core Jetboard mechanics introduced in Jak 3 into Jak 2's native jetboard system:

1. **Chargeable High Jump:**
   - **Controls:** Hold `L1` (crouch on board) then release `X` / Jump.
   - **Behavior:** Charges dynamic upward kinetic energy and launches Jak much higher than standard board jumps (`jakb-board-jump-high-ja`). Plays dedicated charge & launch audio.
2. **Board Zap Attack (Area-of-Effect & I-Frames):**
   - **Controls:** Press `Circle` while riding the board.
   - **Behavior:** Unleashes a radial electric shockwave dealing damage to nearby enemies with invincibility frames during the discharge. Plays `BOARD_ZAP` and `BOARD_ZAP_HIT`.
3. **180-Degree Quick Turn-Around:**
   - **Controls:** Press `Triangle` while riding the board.
   - **Behavior:** Executes a rapid 180° snap rotation (`jakb-board-turn-around-ja`).

---

## 2. Technical Architecture & Modifications

- **Sound Bank Tooling (`SBK`):**
  - Added `extract_sbk` (SPU-ADPCM extraction in `decompiler/data/extract_sbk.cpp`) and `build_sbk` (sound injection in `goalc/build_sbk/`).
  - Appended 4 custom audio samples into Jak 2's native `BOARD.SBK` (`BOARD_CHARGE`, `BOARD_LAUNCH`, `BOARD_ZAP`, `BOARD_ZAP_HIT`).
- **Animation & Art-Group Injection:**
  - Injected Jak 3 animations into custom `.glb` art-groups (`jakb-jak3-board-import.glb`, `daxter-jak3-board-import.glb`) with bone remapping matching Jak 2's skeleton.
  - Relocated and linked into native art-groups dynamically via `link-art!` in `joint.gc`.
- **GOAL Logic:**
  - `goal_src/jak2/engine/target/board/board-h.gc`: Extended `board-info` with charge & zap timing fields.
  - `goal_src/jak2/engine/target/board/board-states.gc`: Implemented charge jump and quick turn states.
  - `goal_src/jak2/engine/target/board/target-board.gc`: Handled board input triggers and zap attack logic.

---

## 3. How to Test & Play

1. Set the active game to Jak 2:
   ```bash
   task set-game-jak2
   ```
2. Build custom sound assets and recompile:
   ```bash
   task extract
   ```
3. In REPL (`task repl`), build the project:
   ```lisp
   (mi)
   ```
4. Boot the game:
   ```bash
   task boot-game
   ```
5. Equip the Jetboard (`R2`) and test:
   - **Charge Jump:** Hold `L1`, then release `X`.
   - **Zap Attack:** Press `Circle`.
   - **Quick Turn:** Press `Triangle`.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-14 | `decompiler/data/extract_sbk.cpp`<br>`goalc/build_sbk/`<br>`goal_src/jak2/engine/target/board/*`<br>`custom_assets/jak2/sounds/sfx/MODEBORD/*`<br>`docs/backport-analysis.md` | Ported Jak 3 jetboard mechanics (charged jump, circle zap attack, triangle quick turnaround), added `build_sbk`/`extract_sbk` tooling, injected custom Jak 3 animation assets and SBK sounds into Jak 2 runtime. | Port Jak 3's advanced jetboard gameplay into Jak 2. |
