<p align="center">
  <img width="500" height="100%" src="./docs/img/logo-text-colored-new.png" alt="OpenGOAL Modding Hub">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Modding-blue.svg" alt="OpenGOAL Modding">
  <img src="https://img.shields.io/badge/Branch-master--dev-orange.svg" alt="Branch">
  <img src="https://img.shields.io/badge/Games-Jak%201%20%7C%20Jak%202%20%7C%20Jak%203-green.svg" alt="Jak Trilogy">
  <img src="https://img.shields.io/badge/AI--assisted-Research%20%26%20Dev-purple.svg" alt="AI Assisted">
</p>

## Contents

- [Purpose and Approach](#purpose-and-approach)
- [Installing a Mod (Players)](#installing-a-mod-players)
- [Git Architecture & CI/CD Workflows](#git-architecture--cicd-workflows)
- [Mod Branch Synchronization](#mod-branch-synchronization)
- [Directory Overview](#directory-overview)
- [Task Command Reference](#task-command-reference)

---

## Purpose and Approach

This project is an unofficial fork of [OpenGOAL](https://github.com/open-goal/jak-project), with no direct affiliation with the original OpenGOAL team or Naughty Dog. For the original technical documentation and build instructions of the native port, see the [original OpenGOAL README](open-goal-original-readme.md).

### Objectives

The goal of this repository is to explore the use of AI to create mods for the Jak trilogy (*Jak and Daxter: The Precursor Legacy*, *Jak II*, *Jak 3*).

### Code reliability and approach

- **Modifications to compiler & decompiler:** some liberties were taken with the GOAL compiler (`goalc`), the C++ runtime (`game`), and the extraction tools (`decompiler`) to change default behaviors and facilitate AI-assisted modding.
- **Code reliability:** the code is not guaranteed to be 100% reliable. The focus is reaching the intended objective for each mod. Most commits created with agent assistance carry the `(AI-assisted)` tag.
- **Documentation for developers:** the verified OpenGOAL Lisp wiki lives at `docs/modding/lisp_instructions.md` — common language patterns and engine architecture in Part 1, per-game specifics in Parts 2-4. It's the only place GOAL code examples live in this repository. Agents consult it before coding and never hallucinate an instruction. Mod-specific notes live in each mod branch's root `README.md`.
- **Two golden rules:** (1) **native non-regression** — a mod never changes default behavior unless its spec requires it; changes ship off by default; (2) **in-game Mods toggle** — every mod is switchable at runtime from the in-game Mods menu (L3 + SELECT), which works in a normal launcher boot.
- **Dedicated mod README:** each mod branch has its own `README.md` at the repository root, including an installation guide, feature list, usage instructions, and a demo video.
- **Contributions & feedback:** constructive feedback and contributions are welcome.

---

## Installing a Mod (Players)

This is the generic install flow for any mod published from this repository, using the official OpenGOAL Launcher.

1. **Add the mod source.** Open the OpenGOAL Launcher, go to Settings (gear icon, bottom-left), click the "Mods" tab, and paste a catalog URL into the input field. The master catalog gives access to every published mod in one source:
   ```text
   https://raw.githubusercontent.com/whozghiar/jak-project/master-dev/index.json
   ```
   Or add an individual mod branch's own catalog URL instead. Click Add.

   ![Adding a mod source in the OpenGOAL Launcher settings](docs/img/add_mod_1.png)

2. **Open the mod page.** Go to the Mods tab in the left-hand panel and click the mod you just added.

   ![Selecting the newly added mod from the Mods tab](docs/img/add_mod_2.png)

3. **Choose a version and install.** Select a version (the latest is recommended) and click Install.

   ![Choosing a version and installing the mod](docs/img/add_mod_3.png)

4. **Wait for installation.** The Launcher downloads the release archive, extracts it, then runs the mod's own `extractor` and `goalc` to decompile and compile the assets. This can take a few minutes depending on the mod.

   ![Installation progress: download, extraction, decompilation, compilation](docs/img/add_mod_4.png)

5. **Launch the game.** Click Play.

   ![Launching the mod from the OpenGOAL Launcher](docs/img/add_mod_5.png)

6. **Activate the mod in-game.** Press L3 + SELECT to open the Mods menu, and toggle the mod on (and adjust its configuration, if it exposes one).

   ![In-game Mods menu opened with L3 + SELECT](docs/img/add_mod_6.png)

> [!NOTE]
> Every mod in this repository ships disabled by default and is toggled on manually from this menu — see [`docs/modding/guides/mods_menu.md`](docs/modding/guides/mods_menu.md) for the underlying mechanism.

---

## Git Architecture & CI/CD Workflows

```text
[open-goal/jak-project] (upstream/master)
         |  (Daily automatic sync at 10:00 UTC: sync-upstream.yaml)
         v
  [whozghiar/jak-project] (origin/master)      <-- Clean upstream mirror (no custom commits)
         |
         |  (Fast-forward / automatic merge)
         v
  [whozghiar/jak-project] (origin/master-dev)  <-- Modding base branch (tools, docs, stable base)
         |
         +-- New mod branch: jak[N]/[type]/[name]
                |
                +-- Root README.md automatically initialized for the mod
                +-- Mod source code (goal_src/) + Modding Changes Log in the root README
                +-- Automated branch mergeability and conflict detection in CI / CLI
```

7 specialized GitHub Actions workflows automate this pipeline — see the [GitHub Actions Workflows Guide](docs/modding/guides/github_workflows.md) for every trigger, exact behavior, and a worked example.

---

## Mod Branch Synchronization

[![Sync Upstream](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml/badge.svg)](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml)

This badge indicates the state of the automated daily synchronization workflow (`sync-upstream.yaml`) running at 10:00 UTC:

- **Green:** the latest sync (upstream -> `master` -> `master-dev` -> mod branches) completed successfully with all clean branches merged.
- **Red:** a conflict or failure occurred during the synchronization pipeline.

Per-branch mergeability details and ready-to-run resolution commands can be audited locally at any time with `task modding-branch-status`. Each individual mod branch also carries its own live status badge in its root `README.md`, driven by `branch-sync-check.yaml`.

---

## Directory Overview

| Directory / File | Description |
| :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Unified AI agent directives and modding rules (branching, golden rules, REPL workflow, task reference). |
| [`.agents/skills/`](.agents/skills/) | Modularized agent skills (GOAL Lisp, engine internals, 3D assets/actors, texture modding, documentation standards). |
| [`index.json`](index.json) | Consolidated OpenGOAL Launcher mod catalog (all published mods and releases across Jak 1-3). |
| [`docs/modding/lisp_instructions.md`](docs/modding/lisp_instructions.md) | Verified OpenGOAL Lisp wiki — common patterns and engine model, plus each game's specifics — consult before coding. |
| [`docs/modding/guides/github_workflows.md`](docs/modding/guides/github_workflows.md) | Guide to all 7 GitHub Actions CI/CD workflows, triggers, and branch synchronization. |
| [`docs/modding/guides/task_scripts_reference.md`](docs/modding/guides/task_scripts_reference.md) | Reference for every `task` command and modding automation script. |
| [`docs/modding/guides/mod_distribution_guide.md`](docs/modding/guides/mod_distribution_guide.md) | Multi-platform binary release pipeline and launcher catalog architecture (`index.json`). |
| [`docs/modding/guides/mod_bug_tracking.md`](docs/modding/guides/mod_bug_tracking.md) | Bug reporting automation, release synchronization, and issue triage. |
| [`docs/modding/guides/mods_menu.md`](docs/modding/guides/mods_menu.md) | Unified in-game Mods menu architecture. |
| [`docs/saves/`](docs/saves/README.md) | 100%-completion save files for Jak 1, Jak 2, and Jak 3 (vanilla game and mods). |
| [`docs/modding/templates/`](docs/modding/templates/) | [`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc). |
| [`scripts/modding/`](scripts/modding/) | Python automation (branch creation, branch/doc sync, doc landing, branch audit, global catalog sync). |
| [`goal_src/`](goal_src/) | Decompiled and modified GOAL source code by game (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | OpenGOAL compiler with modding adjustments. |
| [`game/`](game/) | C++ runtime simulating the Emotion Engine memory on PC. |
| [`decompiler/`](decompiler/) | Asset extraction and decompiler tools. |
| [`custom_assets/`](custom_assets/) | Custom texture replacements and models. |

---

## Task Command Reference

Automation and builds are driven by [Taskfile](https://taskfile.dev/). Pass script arguments after `--`. For every task, including Decompiling, Asset Ripping, Tools, and Tests categories, see the [full Task Reference](docs/modding/guides/task_scripts_reference.md).

### Active target game selection

| Command | Purpose |
| :--- | :--- |
| `task set-game-jak1` · `-jak2` · `-jak3` | Persist active target game configuration (`jak1`, `jak2`, or `jak3`) |

### Build & CMake (3-layer rule)

| Command | Purpose |
| :--- | :--- |
| `task gen-cmake-release` | Configure CMake build system (Ninja + Clang); auto-wires `sccache` if installed |
| `task build-release` | Build all ~20 binaries (first setup / full regression check) |
| `task build-release-game` | Build only `gk` + `goalc` — fast iteration for engine runtime & compiler C++ |
| `task build-release-decomp` | Build only the decompiler — use after changing `decompiler/`, then re-extract |
| `task build-debug` / `-debug-game` / `-debug-decomp` | Debug build equivalents with full symbols |
| `task clean-cmake` | Remove build artifacts and CMake cache |

### Asset extraction & decompilation

| Command | Purpose |
| :--- | :--- |
| `task extract` | Extract retail assets and run the decompiler (run after decompiler config edits) |
| `task decomp` / `decomp-file FILE=...` | Decompile all objects or a single specific GOAL object |
| `task rip-textures` / `rip-levels` / `rip-collision` / `rip-audio` | Rip specific asset categories |

### Interactive REPL & game execution

| Command | Purpose |
| :--- | :--- |
| `task repl` -> `(mi)` | Start compiler REPL; `(mi)` hot-reloads GOAL code directly into running RAM (no C++ build needed) |
| `task boot-game` | Boot game executable in debug mode without attaching REPL |
| `task boot-game-retail` | Boot game in retail mode (`-boot -fakeiso`) to test the Mods menu (L3 + SELECT) |
| `task run-game` | Launch runtime process driven and monitored via REPL connection |
| `task format` / `format-gsrc FILE=...` | Format all C++ and GOAL source code or a single `.gc` file |

---

*(AI-assisted)*
