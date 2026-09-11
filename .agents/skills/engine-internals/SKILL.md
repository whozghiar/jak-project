---
name: engine-internals
description: Architecture of the OpenGOAL C++ runtime, compiler, decompiler, Taskfile commands, and multi-layer build workflow.
---

# Engine Internals & Build System Architecture

OpenGOAL ports the Jak & Daxter trilogy to native x86-64. Understanding the relationship between the C++ runtime, the offline decompiler, the `goalc` compiler, and the GOAL game code is essential for fast iteration and avoiding unnecessary full builds.

---

## 1. The 3-Layer Mental Model

Never wait for a build you don't need. The codebase is organized into three independent layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1 — C++ Runtime & Compiler (gk, goalc)                                │
│   Source: game/  common/  goalc/  + third-party                             │
│   Build command: task build-release-game                                    │
│   Needed when: Editing engine C++, renderers (Merc2/Tfrag), mips2c, goalc   │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2 — Decompiler & Asset Extraction (decompiler)                        │
│   Source: decompiler/  common/                                              │
│   Build command: task build-release-decomp                                  │
│   Needed when: Editing extraction configs (decompiler/config/jak[x]/*.jsonc)│
│                or decompiler C++ code. MUST re-run 'task extract' after.    │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3 — GOAL Game Code (*.gc, *.gp, *.gd)                                 │
│   Source: goal_src/jak[x]/                                                  │
│   Build workflow: Interactive REPL — task repl, then (mi)                   │
│   Needed when: Editing gameplay logic, states, types, actors, levels        │
│   NO C++ build required! Hot-reloads in seconds into the running game.      │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Rule of Thumb:** Over 90% of modding occurs in **Layer 3**. Do not run C++ rebuilds if you only modified `.gc` files.

---

## 2. Core Binaries & Engine Responsibilities

1. **`gk` (Game Kernel Runtime):**
   - Implements the virtual PS2 machine in native C++.
   - Allocates one contiguous memory block via `mmap` (`EE_MAIN_MEM_SIZE`) to simulate Emotion Engine RAM.
   - Hosts the OpenGL/Vulkan PC renderers (`Merc2`, `Tfrag`, `Tie`, `Shrub`, `Direct`).
   - Runs `overlord` (the audio engine handling SBK sound banks and streaming audio).
   - Listens on a local socket for connections from `goalc`.
2. **`goalc` (OpenGOAL Compiler):**
   - Compiles GOAL source code (`.gc`) directly into native x86-64 machine instructions.
   - Acts as an interactive REPL capable of live hot-reloading code into the running `gk` instance via network socket.
   - Packs objects into DGO/CGO container files.
3. **`decompiler`:**
   - Extracts assets, textures, collision geometry, and game objects from retail PS2 ISOs.
   - Disassembles MIPS assembly into decompiled GOAL code.
   - Bakes level geometry and extra models into `.fr3` files consumed by PC renderers.

---

## 3. Taskfile Command Reference

Commands are executed via [Taskfile](https://taskfile.dev/):

### Game Target Selection
```bash
task set-game-jak1   # Set active target game to Jak 1
task set-game-jak2   # Set active target game to Jak 2
task set-game-jak3   # Set active target game to Jak 3
```

### Build & Compilation
```bash
task gen-cmake-release       # Configure CMake with Ninja + Clang (auto-configures sccache if installed)
task build-release           # Build ALL ~20 binaries (first-time setup or full CI check)
task build-release-game      # Fast: builds ONLY gk and goalc (C++ runtime iteration)
task build-release-decomp    # Fast: builds ONLY the decompiler (asset pipeline iteration)
task extract                 # Extract assets and run decompiler (offline asset generation)
```

### Game Execution & Iteration
```bash
task repl                    # Open goalc interactive compiler
# Inside REPL:
(mi)                         # Incrementally compile and hot-reload active project
task boot-game               # Boot game directly without REPL attached
task run-game                # Boot game and attach REPL automatically
task format                  # Format all C++ and GOAL files
```

### Modding Tool Wrappers (scripts/modding/*.py)
```bash
task modding-new-branch -- jak2/features/my-mod   # Create mod branch from master-dev + README template
task modding-sync-branch                          # Safe git merge of master-dev into current branch
task modding-sync-docs                            # Pull docs/modding + AGENTS.md + CLAUDE.md from master-dev
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
task modding-branch-status                        # Update branch synchronization dashboard
task modding-audit                                # Regenerate docs/modding/branch_audit.md
```

---

## 4. Decompiler Asset Pipeline Workflow

When adding custom actors or modifying `decompiler/config/jak[x]/*.jsonc`:
1. Rebuild decompiler: `task build-release-decomp`
2. Re-run extraction: `task extract`
3. Notice: **A decompiler change is inert until extraction is re-run.** The game loads baked `.fr3` files and `.go` files produced offline by extraction.
