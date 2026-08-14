# Mod Readme — City Behavior (Jak 3)

> **Game:** Jak 3  
> **Branch:** `jak3/features/city-behavior`  
> **Target Subsystems:** Haven City Faction System (`goal_src/jak3/levels/wascity/cty-faction.gc`), Traffic & Guard AI (`goal_src/jak3/levels/city/traffic/citizen/`), PC Debug Menu (`goal_src/jak3/pc/debug/default-menu-pc.gc`)

---

## 1. Description & Features

The **City Behavior** mod revamps Haven City's faction AI, traffic spawner systems, and guard combat logic in Jak 3. It introduces dynamic city operating modes switchable at any moment via the in-game PC Debug Menu:

1. **Mode Default (Post-Game Canon - Default):**
   - Restores post-game faction balance (`city-power-game-resolution`).
   - Freedom Faction (FF) guards patrol Haven City. In calm zones, attacking a guard triggers local squad defense while others remain neutral. In active warzones (Industrial, Slums), FF guards fight KG and Metalheads. Ambient city music plays continuously without interruption.
2. **Mode Jak 2 (Peaceful Patrols & Collective Chase):**
   - Recreates the iconic Jak 2 city dynamic: FF guards patrol peaceful streets without enemy monsters.
   - Attacking any guard triggers an immediate city-wide alert: combat music (`cityfi`) fires up, and all surrounding FF guards draw weapons to engage Jak.
   - Fast alert cooldown (~3 seconds) once Jak breaks line of sight and hides.
3. **Mode Chaos (All-Out Urban War):**
   - Transforms the entirety of Haven City into an active warzone.
   - Continuous battles between Freedom Faction guards, Krimzon Guards, and Metalhead predators across every district.
4. **City-Wide Polish & Hijack Fixes:**
   - Ejection and vertical ground search improved to 40m in `civilian.gc` / `citizen.gc` to prevent vehicle hijacking pilot ejection glitches.
   - Guaranteed RAM retention for `ctypepa.DGO`.

---

## 2. Technical Architecture & Modifications

- `goal_src/jak3/levels/wascity/cty-faction.gc`: Core dynamic city mode implementation (`*city-mode*`, `set-city-mode!`) and faction table assignments.
- `goal_src/jak3/levels/city/traffic/citizen/guard.gc`: Collective alert triggers, hostile state transitions, and combat music management (`cityfi`).
- `goal_src/jak3/levels/city/common/ff-squad-control.gc`: Freedom Faction squad alert synchronization across sectors.
- `goal_src/jak3/levels/city/traffic/citizen/citizen.gc` & `civilian.gc`: Hijacking pilot search radius fix.
- `goal_src/jak3/pc/debug/default-menu-pc.gc`: Added `"City Mods"` menu with visual checkbox `[X]` for live mode toggling.

---

## 3. How to Test & Play

1. Set the active game to Jak 3:
   ```bash
   task set-game-jak3
   ```
2. Hot-recompile in REPL:
   ```lisp
   (mi)
   ```
3. Boot the game:
   ```bash
   task boot-game
   ```
4. Open the **PC Debug Menu** (`R3` or Debug hotkey).
5. Navigate to **`City Mods`** and select between:
   - `Mode Default (Fin du Jeu - Canon)`
   - `Mode Jak 2 (Gardes Neutres & Chasse)`
   - `Mode Chaos (Guerre Totale)`
6. Travel across Haven City sectors to test patrols, combat alerts, or urban warfare.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) integrated directly into the OpenGOAL PC Debug Menu under "City Mods" (Jak 2 Mode vs Chaos Mode). | Implement "[Mod] City Behavior": Jak 2-style guard hostility & dynamic City War / Jak 2 mode switcher via Debug Menu. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Added third City Mode `'default` representing post-game state (`city-power-game-resolution` faction strengths and default traffic/spawner quotas). Integrated option in PC Debug Menu under "City Mods". | Provide full end-game spawn behavior option alongside Jak 2 mode and Chaos mode. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extended move-to-ground vertical search radius to 40m in citizen.gc and civilian.gc, and appended 'ctypepa to *territory-list* in cty-faction.gc for Jak 2 and Chaos modes. | Fix vehicle hijack pilot ejection on carjacking across Haven City and guarantee ctypepa.DGO RAM retention. |
