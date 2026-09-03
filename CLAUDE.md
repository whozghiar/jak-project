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
task build-release          # Build release binaries (C++ runtime & compiler)
task build-debug            # Build debug binaries
task extract                # Extract assets and run decompiler

# Interactive REPL & Hot Reload
task repl                   # Open interactive goalc compiler
# In REPL:
(mi)                        # Incremental compile & hot reload active project

# Game Execution
task boot-game              # Boot game directly without REPL
task run-game               # Run game with REPL attached
task format                 # Format C++ and GOAL code
```

> [!IMPORTANT]
> **Task Command Policy:** Claude must **NEVER** run long-running build or runtime `task` commands silently in the background. Always clearly propose the exact command for the user to execute in their terminal.

---

## 3. Strict Modding Instructions & Rules

Before designing or modifying any code for Jak 1, Jak 2, or Jak 3, **strictly consult and adhere to**:
* 📄 [`docs/modding/jak_modding_instructions.md`](docs/modding/jak_modding_instructions.md)

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
* **Syncing Modding Docs On-Demand:** To pull latest tips from `master-dev` without rebasing:
  ```bash
  python scripts/modding/sync_docs_from_master.py
  ```
* **Branch Sync Dashboard:** Tracked live on `master-dev`'s `README.md` and [`docs/modding/branch_sync_status.md`](docs/modding/branch_sync_status.md). Routine updates via:
  ```bash
  python scripts/modding/sync_branches_with_master.py --push
  ```

### 🛡️ Code Architecture & Guardrails
* **In-Code Comments Mandatory:** Every function, method, macro, state, hook, or type modification in `.gc` files **must be thoroughly commented** (intent, arguments, return values, side effects).
* **Non-Destructive Modifications:** Never delete or destructively empty original `.gc` files; favor surgical overrides and modular additions.
* **Project Registration (`.gp`):** Register new `.gc` files in the corresponding project file (e.g. `goal_src/jak[x]/jak[x]-game.gp`).

---

## 4. Modding Utilities & Knowledge Base Access

Engine discoveries, runtime memory structures, particle tricks, state machines, and assembly patterns are organized per game under `docs/modding/`:

### 📚 Knowledge Base Directories:
* **Jak 1:** [`docs/modding/jak1_modding_utilities/`](docs/modding/jak1_modding_utilities/)
  * Aggregated reference: [`docs/modding/jak1_modding_utilities/jak1_modding_utilities.md`](docs/modding/jak1_modding_utilities/jak1_modding_utilities.md)
* **Jak 2:** [`docs/modding/jak2_modding_utilities/`](docs/modding/jak2_modding_utilities/)
  * Aggregated reference: [`docs/modding/jak2_modding_utilities/jak2_modding_utilities.md`](docs/modding/jak2_modding_utilities/jak2_modding_utilities.md)
* **Jak 3:** [`docs/modding/jak3_modding_utilities/`](docs/modding/jak3_modding_utilities/)
  * Aggregated reference: [`docs/modding/jak3_modding_utilities/jak3_modding_utilities.md`](docs/modding/jak3_modding_utilities/jak3_modding_utilities.md)

### 📌 Writing New Tips / Utilities:
* **One File per Tip:** Create a new numbered `.md` file inside the corresponding game folder (e.g. `docs/modding/jak2_modding_utilities/12_sound_bank_allocation.md`).
* **⚠️ NEVER Edit Aggregated Files Directly:** Claude must **NEVER** manually edit or touch the consolidated `jak[x]_modding_utilities.md` files. Exclusively create a new numbered `.md` file (or edit an existing individual tip file). The aggregated files are regenerated exclusively by the automated CI pipeline.
* **Provenance Header Required:** Include Git branch origin metadata at the top:
  ```markdown
  > **Bilingual Knowledge Item / Base de Connaissances Bilingue**
  >
  > - **Origin / Provenance:** `jak[x]/[type]/[name]`
  > - **Last Updated / Dernière modification:** `jak[x]/[type]/[name]`
  > - [🇬🇧 English Version](#-english-version)
  > - [🇫🇷 Version Française](#-version-française)
  ```
* **Bilingual & Pedagogical:** Must be fully documented in both English and French with verified facts, code snippets, and common pitfalls.
* **Automated Aggregation:** The CI pipeline (`.github/workflows/sync-modding-docs.yaml` & `scripts/modding/aggregate_modding_utilities.py`) will automatically harvest tips and regenerate the aggregated knowledge base across branches.

---

## 5. Contributing, Issue & PR Guidelines

* **AI Disclosure:** Always append `(AI-assisted)` to all commit messages, PRs, comments, and documentation.
* **No Autonomous Issues or PRs:** Never create an issue or PR automatically.
* If asked by a user to create an issue or PR, include this disclaimer:
  > *"This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."*
