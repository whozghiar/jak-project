# CLAUDE.md — OpenGOAL Modding & Development Guide

This guide defines the mandatory rules, development workflow, commands, and knowledge bases for Claude when assisting on the OpenGOAL project (Jak 1, Jak 2, Jak 3).

---

## 1. Project Overview & Architecture

The project's objective is to port the original Naughty Dog trilogy (**Jak 1 -> Jak 3**) to native x86-64 PC applications.
* **Core Language:** Over 98% of original game logic is written in **GOAL** (a proprietary LISP dialect designed by Naughty Dog).
* **Key Components:**
  1. `goalc` — The OpenGOAL compiler for x86-64.
  2. `game` / `gk` — The C++ game runtime kernel simulating PS2 Emotion Engine RAM via `mmap`.
  3. `decompiler` — Extracts human-readable GOAL source code from retail game assets.
  4. `goal_src/` — All GOAL / GOOS code organized by game (`jak1/`, `jak2/`, `jak3/`).
  5. `custom_assets/` — Texture replacements (`custom_assets/jak[x]/texture_replacements/`) and custom models/animations.

---

## 2. Essential Commands & Taskfile Reference

Builds and runtime tasks use [Taskfile](https://taskfile.dev/).

```bash
# Game selection
task set-game-jak1          # Switch active target game to Jak 1
task set-game-jak2          # Switch active target game to Jak 2
task set-game-jak3          # Switch active target game to Jak 3

# Building & Compilation
task gen-cmake-release      # Configure the build (Ninja + clang); auto-wires sccache if installed
task build-release          # Build ALL ~20 binaries (runtime, compiler, decompiler, tools, tests) — slow, first build / full check only
task build-release-game     # Build ONLY gk + goalc — fast, use for engine/compiler C++ iteration
task build-release-decomp   # Build ONLY the decompiler — use after changing decompiler/ code or decompiler/config/**
task build-debug            # Debug equivalents: also build-debug-game / build-debug-decomp
task extract                # Extract assets and run decompiler (re-run after any decompiler/config change)

# Interactive REPL & Hot Reload  — GOAL .gc edits need NO C++ build, use this
task repl                   # Open interactive goalc compiler
# In REPL:
(mi)                        # Incremental compile & hot reload active project

# Game Execution
task boot-game              # Boot game directly without REPL
task run-game               # Run game with REPL attached
task format                 # Format C++ and GOAL code

# Modding workflow (wrappers over scripts/modding/*.py — pass args after `--`)
task modding-new-branch -- jak2/features/my-mod   # new mod branch from master-dev + initial README
task modding-sync-branch                          # safe git merge of master-dev into current branch
task modding-sync-docs                            # pull docs/modding + AGENTS.md + CLAUDE.md from master-dev (prunes deletes)
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push  # land a doc addition on master-dev, conflict-free
task modding-branch-status                        # refresh the branch sync dashboard
task modding-audit                                # regenerate docs/modding/branch_audit.md
```

> [!IMPORTANT]
> **Task Command Policy:** Claude must **NEVER** run long-running build or runtime `task` commands silently in the background. Always clearly propose the exact command for the user to execute in their terminal.

> [!NOTE]
> **Build speed & when to rebuild what:** see [`docs/modding/tools/build_and_iteration_workflow.md`](docs/modding/tools/build_and_iteration_workflow.md) — the three-layer model (C++ runtime / decompiler / GOAL code), the `sccache` compiler cache, and the targeted build tasks. Most mods only edit GOAL code and never need a C++ build after setup.

---

## 3. Strict Modding Instructions & Rules

Before designing or modifying any code for Jak 1, Jak 2, or Jak 3, **strictly consult and adhere to**:
* 📄 [`docs/modding/jak_modding_instructions.md`](docs/modding/jak_modding_instructions.md)

> [!IMPORTANT]
> **Consult the reference BEFORE writing or changing any `.gc`:**
> * 📗 [`docs/modding/jak[1|2|3]_lisp_instructions.md`](docs/modding/) — the verified,
>   100 %-certain OpenGOAL Lisp reference for that game (one commented example + traps
>   per instruction). **Never invent an instruction.** If you rely on a verified
>   instruction that is missing, record it — see §4.
> * 📘 [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md)
>   — the shared, non-Lisp engine primer (memory, heaps, DGOs, level streaming,
>   virtual-state residency, process life cycle, boot diagnostics).

### 🌿 Git Branching Convention
* `master`: Clean mirror of `open-goal/jak-project:master`. Never commit directly to `master`.
* `master-dev`: Integration and modding base branch. All new mod branches MUST branch from `master-dev`.
* Mod branches: Dedicated branch per mod following:
```
jak[N°]/[type_of_mod]/[mod_name]
```
* **Branch Creation Automation:** Always create mod branches using:
  ```bash
  python scripts/modding/create_mod_branch.py jak[N]/[type]/[name]
  ```
  This automatically branches from `master-dev` and replaces root `README.md` with the pre-filled template.

### 📝 Mandatory Mod Documentation (Root `README.md`)
Every mod branch maintains a dedicated root `README.md` presenting:
1. Installation Guide / Guide d'installation
2. Mod Features / Fonctionnalités du mod
3. Usage & Controls / Utilisation & Commandes
4. Video Demo / Vidéo démonstrative (or gameplay screenshots)
* **Template:** [`docs/modding/templates/MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)
* **GitHub Visibility:** GitHub automatically renders this root `README.md` when browsing the mod's branch.
* **Syncing Modding Docs On-Demand:** To pull `docs/modding` + `AGENTS.md` + `CLAUDE.md` from `master-dev` (prunes files deleted upstream) without rebasing:
  ```bash
  task modding-sync-docs      # = python scripts/modding/sync_docs_from_master.py
  ```
* **Branch Sync Dashboard:** Tracked live on `master-dev`'s `README.md` and [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md). Routine updates via:
  ```bash
  python scripts/modding/sync_branches_with_master.py --push
  ```

### 🛡️ Code Architecture & Guardrails — 🥇 Golden Rules
* **Consult the reference first** (see §3): read `jak[x]_lisp_instructions.md` + `engine_generic_concepts.md` before touching any `.gc`. Never hallucinate an instruction.
* **Native non-regression:** a mod MUST NOT change default game behaviour unless its written spec explicitly requires it. Every behaviour change ships **OFF by default**, gated behind the mod's Debug ▸ Mods toggle. A fresh install with the mod compiled-but-disabled must play identically to stock.
* **Debug ▸ Mods toggle mandatory:** every mod is switchable on/off at runtime from the in-game debug menu. Jak 2: `(mods-menu-register "<slug>" builder)` — [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md). Never edit `default-menu*.gc` directly. (Jak 1 / Jak 3: mod-slug-prefixed submenu for now; unified-framework port is a follow-up.)
* **In-Code Comments Mandatory:** Every function, method, macro, state, hook, or type modification in `.gc` files **must be thoroughly commented** (intent, arguments, return values, side effects).
* **Non-Destructive Modifications:** Never delete or destructively empty original `.gc` files; favor surgical overrides and modular additions.
* **Project Registration (`.gp`):** Register new `.gc` files in the corresponding project file (e.g. `goal_src/jak[x]/jak[x]-game.gp`).

---

## 4. Modding Knowledge Base — Two Reference Docs

Verified engine knowledge lives in **two curated files per topic** (not a per-branch pile of tips). CI aggregation and its workflow have been removed.

### 📚 The reference:
* 📗 **`docs/modding/jak[1|2|3]_lisp_instructions.md`** — the per-game source of truth for OpenGOAL Lisp. Every entry is **100 %-verified** (compiled + seen working), in plain language, with one commented example and its traps. Consult before coding.
* 📘 **`docs/modding/engine_generic_concepts.md`** — shared, non-Lisp engine primer (memory, heaps, DGOs, level streaming, virtual-state residency, process life cycle, boot diagnostics).

### 📌 Recording a verified discovery (conflict-free rule):
* These files have **one source of truth: `master-dev`**. **NEVER edit them on a mod branch.**
* Land a discovery on `master-dev` as a tiny dedicated commit, then pull it back:
  ```bash
  task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: <what>" --push
  # then, back on your branch:
  task modding-sync-docs
  ```
* **Append only** — add a numbered block below the `➕ APPEND NEW VERIFIED ENTRIES` marker; never reflow existing sections (this is what keeps parallel mods conflict-free).
* Only **verified** facts. No speculation.
* **Mod-*feature*-specific notes** (what your mod changed and why) go in the mod branch's root `README.md` "Modding Changes Log", NOT in the reference docs.

---

## 5. Contributing, Issue & PR Guidelines

* **AI Disclosure:** Always append `(AI-assisted)` to all commit messages, PRs, comments, and documentation.
* **No Autonomous Issues or PRs:** Never create an issue or PR automatically.
* If asked by a user to create an issue or PR, include this disclaimer:
  > *"This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."*
