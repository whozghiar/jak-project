# REPL Workflow, Heap Management & Ghost Memory Pitfalls

This document details the interactive development cycle of OpenGOAL, the heap memory architecture, and the critical pitfalls of REPL hot-reloading ("Ghost Memory").

---

## 1. REPL Lifecycle & Interactive Iteration

The `goalc` REPL allows live hot-reloading of GOAL code into a running game without restarting the application or rebuilding C++ binaries.

### Standard Daily Workflow
1. Launch game: `task boot-game` (or run in debug mode)
2. In a separate terminal, launch REPL: `task repl`
3. Connect to game runtime:
   ```lisp
   (lt)   ;; "Listen to Target" — attaches REPL to the running gk process
   ```
4. Modify your `.gc` code in your editor.
5. In REPL, compile and hot-reload changes immediately:
   ```lisp
   (mi)   ;; "Make Incremental" — compiles only modified .gc files and uploads to gk
   ```
   Changes take effect within seconds.

---

## 2. Memory & Heap Architecture

The C++ runtime (`gk`) reserves a single contiguous block of virtual memory using `mmap` (`EE_MAIN_MEM_SIZE`), accurately mimicking the PS2 Emotion Engine RAM. All GOAL allocations occur inside this block:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SIMULATED PS2 EE RAM                            │
│ ┌───────────────┬───────────────────────┬──────────────┬─────────────┐ │
│ │  Global Heap  │      Level Heap       │  Debug Heap  │   Process   │ │
│ │   ('global)   │       ('level)        │   ('debug)   │  ('process) │ │
│ └───────────────┴───────────────────────┴──────────────┴─────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

| Heap | Role & Contents | Lifetime | Target Usage |
|---|---|---|---|
| **Global Heap (`'global`)** | Symbol table, type descriptors, kernel, permanent processes (e.g. `*target*`). | Entire game session | Permanent systems and singleton managers. **Do not leak transient data here.** |
| **Level Heap (`'level`)** | Level geometry, resident DGO art-groups, level textures, spawned actors. | Level lifespan (cleared on level transition) | Actor spawning, level geometry, level art data. |
| **Debug Heap (`'debug`)** | Debug menu entries, profiler hooks, visualizer state. | Entire session | Debug-only code. Disappears cleanly in release builds. |
| **Process Heap (`'process`)**| Process execution stack and private fields. | Process lifespan | Actor private state (`(new 'process 'my-struct)`). |

---

## 3. The "Ghost Memory" Pitfall (Mémoire Fantôme)

### The Problem
When you hot-reload code via `(mi)`, GOAL updates function code pointers and symbols in-place within the live memory block.

However:
1. **Struct Layout Changes:** If you alter a `deftype` by adding fields, reordering fields, or changing sizes, existing instances already allocated in RAM retain the **old memory layout**. Functions compiled with the new offsets reading old memory layouts cause silent data corruption or crashes.
2. **Order of Declaration / Forward References:** If file B depends on file A, but you previously loaded file B while A was already in memory from an earlier session, `(mi)` succeeds. However, on a fresh boot, file A might not be loaded yet when file B compiles, causing compilation failure.
3. **Lingering Symbols & Functions:** Renaming or deleting a function/symbol does not remove it from the active REPL memory. Code referencing the deleted name will continue to work in the hot session, masking broken references.

### Mandatory Cold Boot Verification Rule
> [!CAUTION]
> **Always validate code with a Cold Boot before committing!**
> Never conclude a task based solely on hot-reloading via `(mi)`.
> Always close the game and test a clean start:
> ```bash
> task boot-game
> ```
> This ensures that:
> - The declaration and compilation order in `.gp` is strictly correct.
> - Struct layouts are clean and initialized without legacy offsets.
> - All symbols and dependencies resolve without relying on residual session memory.

---

## 4. Project File Registration (`.gp`)

Hot-reloading a `.gc` file in the REPL does not mean the game knows how to build it during a clean boot.

Whenever you create a new `.gc` file:
1. Open the project file for your target game:
   - Jak 1: `goal_src/jak1/game.gp`
   - Jak 2: `goal_src/jak2/jak2-game.gp`
   - Jak 3: `goal_src/jak3/jak3-game.gp`
2. Add your file under the appropriate CGO/DGO group:
   ```lisp
   (cgo-file "engine/mods/my-mod-feature.gc")
   ```
3. Ensure dependent type definitions are declared in files listed **above** your file in `.gp`.

---

## 5. Save Slot 1 Auto-Load & PC Settings/Cheats Persistence

### Default Auto-Load (Save Slot 1)
- On startup (`task boot-game` / cold boot), OpenGOAL reads the virtual memory card in `%APPDATA%/OpenGOAL/jak[x]/saves/BASCUS-.../`.
- If an existing save file is present in **Slot 1** (`bank0.bin` / `bank1.bin`), the engine **restores Save Slot 1 by default**.
- **Testing Tip:** If testing a clean, unmodified initial state without prior quest progression, start a new game via the title menu or temporarily rename/remove `bank0.bin` / `bank1.bin`.

### OpenGOAL Cheats & PC Settings Persistence
- OpenGOAL settings and toggled cheats are saved on disk in `%APPDATA%/OpenGOAL/jak[x]/settings/pc-settings.gc`.
- When cheats (such as `city-peace`, `turbo-board`, `music-player`) are toggled via the in-game Debug menu (`Game > OpenGOAL Cheats`) or the Pause Secrets menu, `(pc-settings-save)` writes the active cheat bitmask directly to `pc-settings.gc`:
  ```lisp
  (cheats #x8041)  ;; e.g. #x8000 = city-peace, #x40 = music-player, #x1 = turbo-board
  ```
- **Result:** Cheats remain **permanently active on every subsequent launch** until toggled off in-game or cleared from `pc-settings.gc`.
- To deactivate via REPL or code:
  ```lisp
  (logclear! (-> *pc-settings* cheats) (pc-cheats city-peace))
  (pc-settings-save)
  ```
