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

## Modding Guidelines & Instructions

When working on or creating mods for Jak 1, Jak 2, or Jak 3, all agents MUST strictly consult and follow:
- **Modding Instructions & Rules:** [`docs/modding/jak_modding_instructions.md`](docs/modding/jak_modding_instructions.md)
- **Branch Architecture:**
  - `master`: Clean mirror of `open-goal/jak-project:master`. Never commit directly to `master`.
  - `master-dev`: Integration and modding base branch. All new mod branches MUST branch from `master-dev`.
  - Mod branches: Dedicated branch per mod: `jak[N°]/[type_of_mod]/[mod_name]` (e.g. `jak2/features/blueguard`).
- **Creating a New Mod Branch:** Always use the automation script:
  `python scripts/modding/create_mod_branch.py jak[N]/[type]/[name]`
  This automatically branches from `master-dev` and replaces the root `README.md` with the customized mod README template.
- **Mod-Specific README:** On each mod branch, the root `README.md` presents the mod (installation, features, usage, embedded YouTube demo video). Heavy video files (`.mp4`) must NEVER be committed to the repository; demonstrations must be hosted on YouTube with clickable thumbnails in the README.
- **Branch Synchronization & Status Dashboard:** The live sync state of all branches is tracked on `master-dev`'s `README.md` and [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md). Routine testing and auto-merges are handled by:
  `python scripts/modding/sync_branches_with_master.py --push`
- **Syncing a Mod Branch with master-dev:** To synchronize the active mod branch with `master-dev`:
  `python scripts/modding/sync_branch_with_master_dev.py` (safe `git merge` by default, or `--rebase` if linear history is explicitly desired)
- **Syncing Documentation:** To update modding docs only on any active mod branch without rebasing or polluting history, run:
  `python scripts/modding/sync_docs_from_master.py`
- **Game-Specific Knowledge Bases & Modular Utilities:**
  - Jak 1: [`docs/modding/jak1_modding_utilities/`](docs/modding/jak1_modding_utilities/) ([`docs/modding/jak1_modding_utilities/jak1_modding_utilities.md`](docs/modding/jak1_modding_utilities/jak1_modding_utilities.md))
  - Jak 2: [`docs/modding/jak2_modding_utilities/`](docs/modding/jak2_modding_utilities/) ([`docs/modding/jak2_modding_utilities/jak2_modding_utilities.md`](docs/modding/jak2_modding_utilities/jak2_modding_utilities.md))
  - Jak 3: [`docs/modding/jak3_modding_utilities/`](docs/modding/jak3_modding_utilities/) ([`docs/modding/jak3_modding_utilities/jak3_modding_utilities.md`](docs/modding/jak3_modding_utilities/jak3_modding_utilities.md))
- **Modular Tips Policy:** Agents must **NEVER** edit aggregated `jak[x]_modding_utilities.md` files directly. Only create or edit individual numbered `.md` files in the directories; the CI pipeline aggregates them automatically.
- **Task Commands Policy:** Do NOT run `task` build, run, or extraction commands automatically in the background without explicit user request. Propose them for the user to execute.

## Contributing, Issue and PR Guidelines

- Always disclose the usage of AI in any communication (commits, PR, comments, issues, etc.) by adding an `(AI-assisted)` text to all messages.
- Never create an issue.
- Never create a PR.
- If the user asks you to create an issue or PR, create a file in their diff that says "This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."

