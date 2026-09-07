# Agent Development Guide

A file for [guiding AI coding agents](https://agents.md/).

## Project Overview

The project's goal is to port the original trilogy (Jak 1 -> Jak 3) to PC. Over 98% of the games were written in GOAL, a custom LISP language developed by Naughty Dog. Our strategy is:
- decompile the original game code into human-readable GOAL code
- develop our own compiler for GOAL and recompile the game code for x86-64
- create a tool to extract game assets into formats that can be easily viewed or modified
- create tools to repack game assets into a format that our port uses.

Our objectives are:
- make the port a "native application" on x86-64, with high performance. It shouldn't be emulated, interpreted, or transpiled.
- Our GOAL compiler's performance should be around the same as unoptimized C.
- try to match things from the original game and development as possible. For example, the original GOAL compiler supported live modification of code while the game is running, so we do the same, even though it's not required for just porting the game.
- support modifications. It should be possible to make edits to the code without everything else breaking.

At the moment we support **x86_64** on Windows, Linux and macOS (via Rosetta translation).  There are no plans to ever make a mobile release.

### Project Structure

There are four main components to the project.

1. `goalc` - the GOAL compiler for x86-64
2. `decompiler` - our decompiler
3. `goal_src/` - the folder containing all OpenGOAL / GOOS code
4. `game` - aka the runtime written in C++

## Commands

Common commands that are useful.  We use https://taskfile.dev/ to make cross-platform build commands possible.

- `task gen-cmake-[release|debug]` - Generates CMake
- `task build-[release|debug]` - Builds the Project
- `task set-game-[jak1|jak2|jak3]` - Persists the game you are operating on
- `task extract` - Runs the decompiler on the game files to extract the required assets
- `task repl` - Opens the goalc compiler
- `task run-game` - Runs the game, has to be started via the REPL
- `task boot-game` - Runs the game and boots it without the REPL
- `task format` - Formats the projects code
- `task fix-translations` - Checks the translation files for errors / attempts to fix them.
- `task modding-new-branch -- jak2/features/x` / `modding-sync-branch` / `modding-sync-docs` / `modding-land-doc` / `modding-branch-status` / `modding-audit` - modding workflow wrappers over `scripts/modding/*.py`

## Modding Guidelines & Instructions

When working on or creating mods for Jak 1, Jak 2, or Jak 3, all agents MUST strictly consult and follow:
- **Modding Instructions & Rules:** [`docs/modding/jak_modding_instructions.md`](docs/modding/jak_modding_instructions.md)
- **Consult BEFORE writing or changing any `.gc`:**
  - 📗 `docs/modding/jak[1|2|3]_lisp_instructions.md` — the per-game **verified** OpenGOAL Lisp reference (one commented example + traps per instruction). **Never invent an instruction.**
  - 📘 [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) — shared, non-Lisp engine primer (memory, heaps, DGOs, level streaming, virtual-state residency, process life cycle, boot diagnostics).
- **🥇 Golden rules:**
  - **Native non-regression:** a mod MUST NOT change default game behaviour unless its written spec explicitly requires it. Ship every behaviour change **OFF by default**, behind the mod's Debug ▸ Mods toggle.
  - **Debug ▸ Mods toggle mandatory:** every mod is switchable on/off at runtime from the in-game debug menu. Jak 2: `(mods-menu-register "<slug>" builder)` — [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md). Never edit `default-menu*.gc` directly. (Jak 1/3: mod-slug-prefixed submenu for now.)
  - **Record verified Lisp instructions** you rely on that are missing from `jak[x]_lisp_instructions.md`.
- **Branch Architecture:**
  - `master`: Clean mirror of `open-goal/jak-project:master`. Never commit directly to `master`.
  - `master-dev`: Integration and modding base branch. All new mod branches MUST branch from `master-dev`.
  - Mod branches: Dedicated branch per mod: `jak[N°]/[type_of_mod]/[mod_name]` (e.g. `jak2/features/blueguard`).
- **Creating a New Mod Branch:** `task modding-new-branch -- jak[N]/[type]/[name]` (= `scripts/modding/create_mod_branch.py`). Branches from `master-dev` and replaces the root `README.md` with the customized mod README template.
- **Mod-Specific README:** On each mod branch, the root `README.md` presents the mod (installation, features, usage, embedded YouTube demo video, Modding Changes Log). Heavy video files (`.mp4`) must NEVER be committed; demonstrations are hosted on YouTube with clickable thumbnails.
- **Branch Synchronization & Status Dashboard:** The live sync state of all branches is tracked on `master-dev`'s `README.md` and [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md). Routine testing/auto-merges: `task modding-branch-status -- --push`.
- **Syncing a Mod Branch with master-dev:** `task modding-sync-branch` (safe `git merge`; `-- --rebase` for linear history).
- **Syncing Documentation:** `task modding-sync-docs` — pulls `docs/modding` + `AGENTS.md` + `CLAUDE.md` from `master-dev` and prunes files deleted upstream. Never rebases.
- **Recording a discovery (conflict-free):** the reference docs have **one source of truth: `master-dev`**. NEVER edit them on a mod branch. Use `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push` (append-only, below the `➕ APPEND` marker), then `task modding-sync-docs`. Mod-*feature* notes go in the mod branch README, not the reference.
- **Branch compliance audit:** `task modding-audit` regenerates [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md).
- **Task Commands Policy:** Do NOT run `task` build, run, or extraction commands automatically in the background without explicit user request. Propose them for the user to execute.

## Contributing, Issue and PR Guidelines

- Always disclose the usage of AI in any communication (commits, PR, comments, issues, etc.) by adding an `(AI-assisted)` text to all messages.
- Never create an issue.
- Never create a PR.
- If the user asks you to create an issue or PR, create a file in their diff that says "This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."

