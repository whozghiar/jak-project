# Agent Development & Modding Guide — OpenGOAL

A unified instruction guide and engineering reference for AI coding agents ([agents.md](https://agents.md/)) working on the OpenGOAL project (`jak-project`).

---

## 1. Project Overview & Architecture

The OpenGOAL project ports the original Naughty Dog PlayStation 2 trilogy (**Jak 1 -> Jak 3**) to native x86-64 PC applications.
- **Core Language:** Over 98% of the original game code is written in **GOAL** (Game Oriented Assembly Lisp), a custom compiled LISP dialect created by Naughty Dog.
- **Key Components:**
  1. `goalc` — The OpenGOAL compiler for x86-64 and interactive REPL.
  2. `game` / `gk` — The C++ game runtime kernel simulating PS2 Emotion Engine RAM via `mmap`.
  3. `decompiler` — Extracts assets and human-readable GOAL source code from retail game assets.
  4. `goal_src/` — All GOAL / GOOS source code organized by game (`jak1/`, `jak2/`, `jak3/`).
  5. `custom_assets/` — Texture replacements (`custom_assets/jak[x]/texture_replacements/`) and custom 3D models/animations.

Our objectives are:
- Deliver a native x86-64 application with high performance (no emulation, interpretation, or transpilation).
- Maintain near-instant live code modification while the game is running via the REPL.
- Provide a modular, non-regressive modding architecture.

---

## 2. Dynamic Skills Registry (Lazy-Loaded Knowledge)

To avoid context saturation, agents should **not** read every reference file at startup. Instead, load specialized skills on-demand based on the user's prompt:

### Skill: [GOAL Lisp & Syntax]
- **Trigger:** Writing or debugging GOAL code (`.gc`), state machines (`defstate`, `defbehavior`), types, or macros.
- **Path:** [`.agents/skills/goal-lisp/SKILL.md`](.agents/skills/goal-lisp/SKILL.md) and [`.agents/skills/goal-lisp/discoveries.md`](.agents/skills/goal-lisp/discoveries.md).

### Skill: [Engine Internals & REPL Workflow]
- **Trigger:** Engine architecture, C++ runtime (`gk`), compiler (`goalc`), decompiler, REPL lifecycle, heap/memory management, Taskfile builds.
- **Path:** [`.agents/skills/engine-internals/SKILL.md`](.agents/skills/engine-internals/SKILL.md) and [`.agents/skills/engine-internals/repl-workflow.md`](.agents/skills/engine-internals/repl-workflow.md).

### Skill: [Custom Actors & 3D Assets]
- **Trigger:** Adding `.glb` models, armatures, joint channels, Blender imports, animations, custom entities, sound banks (SBK), or new actors/levels.
- **Path:** [`.agents/skills/custom-actors-levels/SKILL.md`](.agents/skills/custom-actors-levels/SKILL.md) and [`.agents/skills/custom-actors-levels/discoveries.md`](.agents/skills/custom-actors-levels/discoveries.md).

### Skill: [Texture Modding]
- **Trigger:** Texture replacement, texture pages (`tpage`), texture dumps/injection, and texture merging.
- **Path:** [`.agents/skills/texture-modding/SKILL.md`](.agents/skills/texture-modding/SKILL.md) and [`.agents/skills/texture-modding/discoveries.md`](.agents/skills/texture-modding/discoveries.md).

---

## 3. Long-Term Memory Feeder Rule

To continually enrich the project knowledge base across modding sessions, all agents must adhere to the following rule:

> **"Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, you must append a concise entry (under 10 lines) with code snippet into `.agents/skills/<relevant-skill>/discoveries.md` before concluding the task."**

---

## 4. Essential Commands & Taskfile Reference

Builds and runtime tasks use [Taskfile](https://taskfile.dev/).

```bash
# Game selection
task set-game-jak1          # Switch active target game to Jak 1
task set-game-jak2          # Switch active target game to Jak 2
task set-game-jak3          # Switch active target game to Jak 3

# Building & Compilation
task gen-cmake-release      # Configure CMake (Ninja + Clang); auto-wires sccache if installed
task build-release          # Build ALL ~20 binaries (first setup / full check)
task build-release-game     # Build ONLY gk + goalc — fast iteration for engine/compiler C++
task build-release-decomp   # Build ONLY the decompiler — use after changing decompiler/
task build-debug            # Debug equivalents: build-debug-game, build-debug-decomp
task extract                # Extract assets and run decompiler (offline asset baking)

# Interactive REPL & Hot Reload (GOAL .gc edits need NO C++ build)
task repl                   # Open interactive goalc compiler
# Inside REPL:
(mi)                        # Incremental compile & hot reload active project into running game

# Game Execution
task boot-game              # Boot game directly without REPL
task run-game               # Run game with REPL attached
task format                 # Format C++ and GOAL code
task fix-translations       # Validate translation files

# Modding workflow wrappers (scripts/modding/*.py — pass args after `--`)
task modding-new-branch -- jak2/features/my-mod   # Create new mod branch from master-dev + README template
task modding-sync-branch                          # Safe git merge of master-dev into current branch
task modding-sync-docs                            # Pull docs/modding + AGENTS.md + CLAUDE.md from master-dev
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
task modding-branch-status                        # Refresh branch sync dashboard
task modding-audit                                # Regenerate docs/modding/branch_audit.md
```

> [!IMPORTANT]
> **Task Execution Policy:** Agents must **NEVER** run long-running build or runtime `task` commands silently in the background without explicit user request. Always propose the exact command for the user to execute in their terminal.

---

## 5. Development Cycle: REPL Hot-Reload vs Cold Boot

Understanding the difference between hot-reloading in the REPL and clean cold boot execution is critical:

### The Hot-Reload Cycle `(mi)`
- When editing `.gc` files, you do not rebuild C++ executables.
- In `goalc` REPL, run `(mi)` to incrementally compile and inject updated functions and states directly into the running game memory.

### The "Ghost Memory" Trap (Mémoire Fantôme) & Cold Boot Verification
- **The Danger:** When code is hot-reloaded via `(mi)`, previous definitions, symbols, and old structure layouts linger in the simulated PS2 memory. 
- If you alter structure field layouts, reorder declarations, or introduce forward references, your code may appear to work in the active REPL session while actually being broken on a clean launch.
- **Mandatory Cold Boot Rule:** Always validate modifications with a clean cold start before concluding:
  ```bash
  task boot-game
  ```
  Cold compilation validates proper declaration order, ensures `.gp` project registration is complete, and guarantees no residual memory corruption.

### Project File Registration (`.gp`)
Whenever you add a new `.gc` source file, you **must register it** in the corresponding game project file:
- Jak 1: `goal_src/jak1/game.gp`
- Jak 2: `goal_src/jak2/jak2-game.gp`
- Jak 3: `goal_src/jak3/jak3-game.gp`
Ensure that dependent type files are listed **before** files that consume them.

---

## 6. Strict Modding Instructions & Guardrails

All mod development must adhere to the conventions documented in this guide, the [Modding Documentation Hub](docs/modding/README.md), and specialized skills in [`.agents/skills/`](.agents/skills/).

### 🥇 Golden Rules
1. **Consult Reference Docs First:**
   - 📗 `docs/modding/jak[1|2|3]_lisp_instructions.md` — Verified OpenGOAL LISP reference. **Never hallucinate or invent an instruction.**
   - 📘 [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) — Shared engine concepts (memory heaps, DGOs, process lifecycle).
2. **Native Non-Regression:**
   - A mod MUST NOT alter default game behavior unless explicitly required.
   - All behavior changes must ship **OFF by default**, gated behind the mod's toggle.
3. **Debug ▸ Mods Toggle Mandatory:**
   - Every mod must be switchable on/off at runtime via the in-game debug menu.
   - Jak 2: Register via `(mods-menu-register "<slug>" builder)` — see [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md). Never edit `default-menu*.gc` directly.
   - Jak 1 / Jak 3: Prefix submenus cleanly with the mod slug.
4. **Mandatory In-Code Comments:**
   - Every function, method, state, hook, and type modification in `.gc` must be thoroughly commented (purpose, arguments, return values, side effects).
5. **Non-Destructive Modifications:**
   - Never delete or destructively wipe original `.gc` files; favor surgical overrides and modular extensions.
6. **Traceability of Changes:**
   - Document all changes in the mod branch's root `README.md` ("Modding Changes Log") and in `docs/modding/` notes.

---

## 7. Git Branching Strategy & Collaboration

- `master`: Clean mirror of `open-goal/jak-project:master`. **Never commit directly to `master`.**
- `master-dev`: Integration and modding base branch. All new mod branches MUST branch from `master-dev`.
- **Branch Naming Convention:**
  ```text
  jak[N°]/[type_of_mod]/[mod_name]
  ```
  *(e.g., `jak2/features/jak3-jetBoard`, `jak1/features/green-eco-glow`)*
- **Two-Tier Mod Documentation Architecture:**
  1. **Tier 1 — Root `README.md` (User & Player-Facing):**
     - Must be initialized from the bilingual template ([`docs/modding/templates/MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)).
     - Filled with clear, generic, and player-accessible information conforming to the template: Mod Overview, Key Features, Step-by-Step guide to run the mod, Controls & gameplay usage, Demonstrative video/media (embedded YouTube thumbnail, never commit `.mp4` files to Git), and high-level Modding Changes Log.
  2. **Tier 2 — `docs/modding/current_mod/<slug>_readme.md` (Technical & Pedagogical Deep-Dive):**
     - Dedicated in-depth engineering documentation for developers, agents, and future maintainers.
     - Uses a pedagogical approach with concrete GOAL Lisp code examples, type layouts (`deftype`), state machine transitions (`defstate`), engine hooks, audio bank/asset injection pipelines, and architectural explanations.
- **Recording Verified Discoveries Conflict-Free:**
  - The reference documents (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) have **one source of truth: `master-dev`**. NEVER edit them directly on a mod branch.
  - Land discoveries using:
    ```bash
    task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: <description>" --push
    task modding-sync-docs
    ```

---

## 8. Contributing, Issue and PR Guidelines

- **AI Disclosure:** Always disclose the usage of AI in any communication (commits, PRs, comments, issues, etc.) by appending `(AI-assisted)` to all messages.
- **Safety Policy:** Never delete or overwrite existing source files without explicit agreement.
- **No Autonomous Issues or PRs:** Never create an issue or PR automatically.
- If asked by a user to create an issue or PR, create a file in their diff that states:
  > *"This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."*
