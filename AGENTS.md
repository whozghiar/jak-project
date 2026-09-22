# Agent Development & Modding Guide — OpenGOAL

> Unified agent reference. Scope: AI coding agents, maintainers, and mod
> developers. Source of truth: `master-dev`. Compliance is mandatory across
> all mod branches (`jak[1-3]/**`).

## Contents

1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Dynamic Skills Registry](#2-dynamic-skills-registry-lazy-loaded-knowledge)
3. [Recording Verified Discoveries](#3-recording-verified-discoveries)
4. [Documentation Standards](#4-documentation-standards)
5. [Essential Commands & Taskfile Reference](#5-essential-commands--taskfile-reference)
6. [CI/CD & GitHub Actions Workflows](#6-cicd--github-actions-workflows)
7. [Development Cycle (REPL vs Cold Boot)](#7-development-cycle-repl-hot-reload-vs-cold-boot)
8. [Strict Modding Instructions & Golden Rules](#8-strict-modding-instructions--guardrails)
9. [Git Branching Strategy & Two-Tier Docs](#9-git-branching-strategy--collaboration)
10. [Contributing, Issue and PR Guidelines](#10-contributing-issue-and-pr-guidelines)

---

## 1. Project Overview & Architecture

The OpenGOAL project ports the original Naughty Dog PlayStation 2 trilogy
(Jak 1 -> Jak 3) to native x86-64 PC applications.

- **Core language:** over 98% of the original game code is written in GOAL
  (Game Oriented Assembly Lisp), a custom compiled LISP dialect created by
  Naughty Dog.
- **Key components:**
  1. `goalc` — the OpenGOAL compiler for x86-64 and interactive REPL.
  2. `game` / `gk` — the C++ game runtime kernel simulating PS2 Emotion
     Engine RAM via `mmap`.
  3. `decompiler` — extracts assets and human-readable GOAL source code
     from retail game assets.
  4. `goal_src/` — all GOAL / GOOS source code organized by game (`jak1/`,
     `jak2/`, `jak3/`).
  5. `custom_assets/` — texture replacements
     (`custom_assets/jak[x]/texture_replacements/`) and custom 3D
     models/animations.

Objectives: deliver a native x86-64 application with high performance (no
emulation, interpretation, or transpilation); maintain near-instant live
code modification while the game is running via the REPL; provide a
modular, non-regressive modding architecture.

---

## 2. Dynamic Skills Registry (Lazy-Loaded Knowledge)

To avoid context saturation, agents should not read every reference file
at startup. Load specialized skills on demand based on the task:

### Skill: GOAL Lisp & Syntax
- **Trigger:** writing or debugging GOAL code (`.gc`), state machines
  (`defstate`, `defbehavior`), types, or macros.
- **Path:** [`.agents/skills/goal-lisp/SKILL.md`](.agents/skills/goal-lisp/SKILL.md)
  — conceptual reference; every code example lives in the Lisp wiki
  (`docs/modding/lisp_instructions.md`).

### Skill: Engine Internals & REPL Workflow
- **Trigger:** engine architecture, C++ runtime (`gk`), compiler (`goalc`),
  decompiler, REPL lifecycle, heap/memory management, Taskfile builds.
- **Path:** [`.agents/skills/engine-internals/SKILL.md`](.agents/skills/engine-internals/SKILL.md)
  and [`.agents/skills/engine-internals/repl-workflow.md`](.agents/skills/engine-internals/repl-workflow.md).

### Skill: Custom Actors, 3D Assets & Rig Adapter
- **Trigger:** adding `.glb` models, armatures, joint channels, Blender
  imports/MCP, character/enemy adaptation and backporting between Jak games
  (Jak 1, 2, 3), armature retargeting, non-destructive textures,
  animations, custom entities, sound banks (SBK), or new actors/levels.
- **Path:** [`.agents/skills/custom-actors-levels/SKILL.md`](.agents/skills/custom-actors-levels/SKILL.md).

### Skill: Texture Modding
- **Trigger:** texture replacement, texture pages (`tpage`), texture
  dumps/injection, and texture merging.
- **Path:** [`.agents/skills/texture-modding/SKILL.md`](.agents/skills/texture-modding/SKILL.md).

### Skill: Documentalist
- **Trigger:** writing, updating, or auditing any `.md` documentation file
  in the repository.
- **Path:** [`.agents/skills/documentalist/SKILL.md`](.agents/skills/documentalist/SKILL.md).

---

## 3. Recording Verified Discoveries

When you identify an undocumented GOAL syntax pattern, a language trap, or
the resolution of an engine crash during mod development, land it directly
in the Lisp wiki (`docs/modding/lisp_instructions.md`) — not in a separate
memory or scratch file:

```bash
task modding-land-doc -- --file docs/modding/lisp_instructions.md --message "jak2: <description>" --push
task modding-sync-docs
```

An engine fact with no GOAL code attached (a build quirk, a launcher
packaging requirement, a memory constant) belongs in the wiki's "Engine
model" section (Part 1.3) if it's shared by all three games, or in the
relevant skill's `SKILL.md` if
it's specific to that skill's domain. No skill folder should carry a
loose, ever-growing discoveries log — fold a verified fact into the
document that actually owns that topic.

---

## 4. Documentation Standards

> [!IMPORTANT]
> Every documentation file (`.md`) created or updated across the project
> must follow these rules. The [`documentalist`](.agents/skills/documentalist/SKILL.md)
> skill is the operational checklist for this section — load it before any
> non-trivial documentation edit.

1. **English only.** No bilingual sections, no French mirror. This
   supersedes any earlier bilingual EN/FR requirement.
2. **Concise and tutorial-toned.** Short paragraphs, one concept per
   section, tables over prose for key-to-value mappings, worked examples
   over abstract description. Avoid AI-sounding filler phrases.
3. **Clearly separated themes.** Every document states its scope in its
   first paragraph and stays inside it.
4. **No superfluous icons.** Plain markdown headings and lists. Keep
   GitHub's semantic admonitions (`[!NOTE]`, `[!IMPORTANT]`, `[!TIP]`) —
   those are functional, not decorative.
5. **GOAL/Lisp code lives only in the Lisp wiki.** Fenced GOAL/Lisp code
   examples belong exclusively in `docs/modding/lisp_instructions.md`.
   Everywhere else — skills, guides, mod READMEs — describe the
   pattern in prose and link to its entry in the wiki. The only exception
   is a `.gc` template file meant to be copied (e.g.
   `docs/modding/templates/mod_menu.template.gc`), which is a code
   artifact, not narrative documentation.
6. **Verified-true content only.** Never invent an instruction, API, path,
   or task. Check against the actual repository before writing a fact
   down.

---

## 5. Essential Commands & Taskfile Reference

Task automation is driven by [Taskfile](https://taskfile.dev/). For a full
pedagogical explanation of every task, see
[Task Commands & Modding Scripts Reference](docs/modding/guides/task_scripts_reference.md).

```bash
# Game selection
task set-game-jak1          # Switch active target game to Jak 1
task set-game-jak2          # Switch active target game to Jak 2
task set-game-jak3          # Switch active target game to Jak 3

# Building & compilation (3-layer rule)
task gen-cmake-release      # Configure CMake (Ninja + Clang); auto-wires sccache if installed
task build-release          # Build ALL ~20 binaries (first setup / full check)
task build-release-game     # Build ONLY gk + goalc -- fast iteration for engine/compiler C++
task build-release-decomp   # Build ONLY the decompiler -- use after changing decompiler/
task build-debug            # Debug equivalents: build-debug-game, build-debug-decomp
task extract                # Extract assets and run decompiler (offline asset baking)

# Interactive REPL & hot reload (GOAL .gc edits need NO C++ build)
task repl                   # Open interactive goalc compiler
# Inside REPL:
(mi)                        # Incremental compile & hot reload active project into running game

# Game execution
task boot-game               # Boot game directly in debug mode
task boot-game-retail        # Boot game in retail mode (-boot -fakeiso) to test Mods Menu (L3 + SELECT)
task run-game                # Run game with REPL attached
task format                  # Format C++ and GOAL code

# Modding workflow wrappers (scripts/modding/*.py -- pass args after `--`)
task modding-new-branch -- jak2/features/my-mod   # Create new mod branch from master-dev + README template
task modding-sync-branch                          # Your branch only: safe git merge of master-dev into it
task modding-sync-docs                            # Pull docs/modding + AGENTS.md + CLAUDE.md from master-dev
task modding-land-doc -- --file docs/modding/lisp_instructions.md --message "..." --push
task modding-branch-status                        # Every mod branch: test/refresh sync status
task modding-audit                                 # Regenerate the local branch compliance report
task modding-sync-catalog                          # Regenerate master-dev root index.json from published releases
task modding-package-texture-pack                  # Register GUI texture pack .zip into index.json
task modding-register-texture-pack                 # Alias for modding-package-texture-pack
task modding-texture-gui                           # Launch OpenGOAL Texture Pack Generator GUI desktop app
```

> [!IMPORTANT]
> **Task execution policy:** agents must never run long-running build or
> runtime `task` commands silently in the background without an explicit
> user request. Always propose the exact command for the user to run in
> their terminal.

---

## 6. CI/CD & GitHub Actions Workflows

The repository relies on 7 specialized GitHub Actions workflows. For the
full trigger and behavior detail, see
[GitHub Actions Workflows Guide](docs/modding/guides/github_workflows.md).

1. `sync-upstream.yaml` — daily sync from upstream OpenGOAL into `master`
   and `master-dev`, auto-merges clean mod branches.
2. `branch-sync-check.yaml` — lightweight ancestry check that drives each
   mod branch's status badge.
3. `release.yml` — manual trigger that builds and publishes a mod release.
4. `mod-bug-report-sync.yml` — keeps the bug report form's mod dropdown
   aligned with published releases.
5. `mod-bug-triage.yml` — auto-labels bug report issues by game and mod.
6. `sync-global-catalog.yml` — rebuilds the root `index.json` launcher
   catalog from published releases.
7. `mod-suggestion-triage.yml` — auto-labels community mod suggestions.

---

## 7. Development Cycle: REPL Hot-Reload vs Cold Boot

### The hot-reload cycle
- When editing `.gc` files, you do not rebuild C++ executables.
- In the `goalc` REPL, run `(mi)` to incrementally compile and inject
  updated functions and states directly into the running game memory.

### The "ghost memory" trap & cold boot verification
- **The danger:** when code is hot-reloaded via `(mi)`, previous
  definitions, symbols, and old structure layouts linger in the simulated
  PS2 memory.
- If you alter structure field layouts, reorder declarations, or introduce
  forward references, your code may appear to work in the active REPL
  session while actually being broken on a clean launch.
- **Mandatory cold boot rule:** always validate modifications with a clean
  cold start before concluding:
  ```bash
  task boot-game
  ```
  Cold compilation validates proper declaration order, ensures `.gp`
  project registration is complete, and guarantees no residual memory
  corruption.

### Project file registration (`.gp`)
Whenever you add a new `.gc` source file, register it in the corresponding
game project file:
- Jak 1: `goal_src/jak1/game.gp`
- Jak 2: `goal_src/jak2/jak2-game.gp`
- Jak 3: `goal_src/jak3/jak3-game.gp`

Ensure that dependent type files are listed before files that consume
them.

### Default save slot 1 & settings/cheats persistence
- **Default auto-load:** when the game boots (cold boot), OpenGOAL
  automatically restores Save Slot 1 by default if a save file exists
  (`%APPDATA%/OpenGOAL/jak[x]/saves/BASCUS-.../bank0.bin`). To test fresh,
  unprogressed behavior, start a new game or temporarily clear/rename Slot
  1.
- **Persistent PC settings & cheats:** OpenGOAL settings and toggled
  cheats (e.g. `city-peace`, `turbo-board`, `music-player`) are saved to
  `%APPDATA%/OpenGOAL/jak[x]/settings/pc-settings.gc`. Once a cheat is
  enabled, it stays active across subsequent launches until toggled off
  in-game or cleared from the file.

---

## 8. Strict Modding Instructions & Guardrails

All mod development must adhere to the conventions documented in this
guide and the specialized skills in [`.agents/skills/`](.agents/skills/).

### Golden Rules

1. **Consult reference docs first.**
   - [`docs/modding/lisp_instructions.md`](docs/modding/lisp_instructions.md) —
     the Lisp wiki, the only place GOAL/Lisp code examples live in this
     repository. Never hallucinate or invent an instruction. Part 1 covers
     memory heaps, DGOs, and process lifecycle, shared by all three games.
2. **Native non-regression.** A mod must not alter default game behavior
   unless explicitly requested. All behavior changes must ship off by
   default, gated behind the mod's runtime toggle.
3. **In-game Mods toggle mandatory (especially for `features/*`).** Every
   new mod — without exception for any `features/*` mod — must register an
   in-game toggle in the unified Mods menu. This is what lets a player
   enable or disable a mod's changes at runtime while the mod itself
   touches the minimum possible amount of vanilla code: the toggle, not a
   direct edit to shared files, is what should gate new behavior.
   - The mod must be switchable on/off at runtime from a retail boot (the
     default launcher boot mode), not only in debug mode.
   - Jak 2 / Jak 3: the Mods menu opens in-game with L3 + SELECT in both
     retail and debug boots. See
     [`docs/modding/guides/mods_menu.md`](docs/modding/guides/mods_menu.md)
     and the template
     [`docs/modding/templates/mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc);
     the exact registration call is in each game's Lisp wiki.
   - Never edit shared menu files directly, and never mark your own menu
     file as debug-only — a debug segment is not linked in a retail boot.
   - Jak 1: prefix submenus cleanly with the mod slug, and document in the
     mod README that the toggle is debug-only.
   - **Audit enforcement:** any `features/*` branch lacking an active
     Mods-menu registration is considered non-compliant and will be
     flagged by `task modding-audit`.
4. **Mandatory in-code comments.** Every function, method, state, hook,
   and type modification in `.gc` must be thoroughly commented (purpose,
   arguments, return values, side effects).
5. **Non-destructive modifications.** Never delete or destructively wipe
   original `.gc` files; favor surgical overrides and modular extensions.
6. **Traceability of changes.** Document all changes in the mod branch's
   root `README.md` ("Modding Changes Log") and, for anything with a
   deeper technical story, in a Tier-2 note under `docs/modding/current_mod/`.

---

## 9. Git Branching Strategy & Collaboration

- `master`: clean mirror of `open-goal/jak-project:master`. Never commit
  directly to `master`.
- `master-dev`: integration and modding base branch. All new mod branches
  must branch from `master-dev`.
- **Branch naming convention:**
  ```text
  jak[N]/[type_of_mod]/[mod_name]
  ```
  (e.g. `jak2/features/jak3-jetBoard`, `jak1/features/green-eco-glow`)
- **Two-tier mod documentation architecture:**
  1. **Tier 1 — root `README.md` (user & player-facing):** initialized
     from the template
     ([`docs/modding/templates/MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)).
     Player-accessible info: overview, features, setup, controls
     (L3 + SELECT), video demo, cover thumbnail, changes log.
  2. **Tier 2 — `docs/modding/current_mod/<slug>_readme.md` (technical
     deep-dive):** dedicated in-depth engineering documentation for
     developers and AI agents, referencing the Lisp wiki for any GOAL code
     rather than repeating it.
- **Recording verified discoveries conflict-free:** the Lisp wiki
  (`docs/modding/lisp_instructions.md`) has one source of truth:
  `master-dev`. Never edit it directly on a mod branch — land discoveries
  using:
  ```bash
  task modding-land-doc -- --file docs/modding/lisp_instructions.md --message "jak2: <description>" --push
  task modding-sync-docs
  ```

---

## 10. Contributing, Issue and PR Guidelines

- **AI disclosure:** always disclose the usage of AI in any communication
  (commits, PRs, comments, issues) by appending `(AI-assisted)` to all
  messages.
- **Safety policy:** never delete or overwrite existing source files
  without explicit agreement.
- **No autonomous issues or PRs:** never create an issue or PR
  automatically.
- If asked by a user to create an issue or PR, add to the diff a note
  stating that it was made via an AI agent and likely has not been
  reviewed by a human.
