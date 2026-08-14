# Mod Readme — Start Menu Wheel Fast Navigation (Jak 2)

> **Game:** Jak 2  
> **Branch:** `jak2/config/start_menu_wheel`  
> **Target Subsystem:** UI Progress & In-Game Pause Menu (`goal_src/jak2/engine/ui/progress/` & `goal_src/jak2/pc/progress/`)

---

## 1. Description & Features

This quality-of-life (QoL) mod modernizes the in-game Start / Pause menu wheel navigation in Jak 2 to match the fluidity and responsiveness of Jak 3:

- **Doubled Ring Rotation Speed:** In original Jak 2, the menu ring rotation animation was capped at half the speed of Jak 3, locking new user inputs until the animation completed. The seek speed is doubled to provide instant feedback.
- **Hold-to-Repeat Navigation:** Holding down directional inputs (D-Pad / Analog Sticks Up/Down and Left/Right) now automatically cycles through options smoothly with a 0.175s throttle window, eliminating the need to repeatedly mash the direction buttons.

---

## 2. Technical Architecture & Modifications

- **Modified Files:**
  - `goal_src/jak2/engine/ui/progress/progress-h.gc`: Added timer fields for input repeat throttling in `progress-control`.
  - `goal_src/jak2/engine/ui/progress/progress.gc`: Updated `respond-to-cpad` and ring rotation seek rate to match Jak 3 speeds.
  - `goal_src/jak2/pc/progress/progress-generic-pc.gc`: Enhanced PC option menu navigation handling.
  - `goal_src/jak2/pc/progress/progress-pc.gc`: Initialized repeat timer variables.

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
3. Boot the game:
   ```bash
   task boot-game
   ```
4. Press `Start` / `Escape` to enter the Pause Menu.
5. Use the D-Pad or Left Stick (or hold up/down/left/right) to navigate the options ring and observe the snappy, continuous scrolling.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-13 | `goal_src/jak2/engine/ui/progress/progress-h.gc`<br>`goal_src/jak2/engine/ui/progress/progress.gc`<br>`goal_src/jak2/pc/progress/progress-generic-pc.gc`<br>`goal_src/jak2/pc/progress/progress-pc.gc` | Doubled ring seek rotation rate to match Jak 3. Implemented hold-to-repeat input logic with a 0.175s repeat throttle for Up/Down and Left/Right progress navigation. | Make Start menu wheel navigation responsive and fluid like Jak 3. |
