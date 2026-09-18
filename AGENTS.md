# Agent Development & Modding Guide — OpenGOAL / Guide de Développement & de Modding des Agents — OpenGOAL

> **Bilingual Unified Agent Reference / Référence Unifiée Bilingue des Agents**
>
> - **Scope / Portée :** AI Coding Agents, Maintainers & Mod Developers
> - **Source of Truth / Source de Vérité :** `master-dev`
> - **Compliance / Conformité :** Mandatory across all mod branches (`jak[1-3]/**`)

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Project Overview & Architecture](#1-project-overview--architecture) · [2. Dynamic Skills Registry](#2-dynamic-skills-registry-lazy-loaded-knowledge) · [3. Long-Term Memory Feeder Rule](#3-long-term-memory-feeder-rule) · [4. Mandatory Documentation Formalism](#4-mandatory-documentation-formalism-bilingual-enfr--mini-toc) · [5. Essential Commands & Task Reference](#5-essential-commands--taskfile-reference) · [6. CI/CD & GitHub Actions Workflows](#6-cicd--github-actions-workflows) · [7. Development Cycle (REPL vs Cold Boot)](#7-development-cycle-repl-hot-reload-vs-cold-boot) · [8. Strict Modding Instructions & Golden Rules](#8-strict-modding-instructions--guardrails) · [9. Git Branching Strategy & Two-Tier Docs](#9-git-branching-strategy--collaboration) · [10. PR & Contribution Guidelines](#10-contributing-issue-and-pr-guidelines)
> - 🇫🇷 **Français :** [1. Présentation du Projet & Architecture](#1-présentation-du-projet--architecture) · [2. Registre Dynamique des Compétences](#2-registre-dynamique-des-compétences-chargement-à-la-demande) · [3. Règle d'Alimentation de la Mémoire](#3-règle-dalimentation-de-la-mémoire-à-long-terme) · [4. Formalisme Obligatoire de Documentation](#4-formalisme-obligatoire-de-documentation-bilingue-enfr--mini-sommaire) · [5. Commandes Essentielles & Référence Task](#5-commandes-essentielles--référence-taskfile) · [6. Workflows CI/CD & GitHub Actions](#6-workflows-cicd--github-actions) · [7. Cycle de Développement (REPL vs Boot à Froid)](#7-cycle-de-développement-rechargement-à-chaud-repl-vs-boot-à-froid) · [8. Règles d'Or & Garde-Fous de Modding](#8-instructions-strictes-de-modding--règles-dor) · [9. Stratégie de Branches Git & Docs à Deux Niveaux](#9-stratégie-de-branches-git--collaboration) · [10. Directives de Contribution & PR](#10-directives-de-contribution-tickets-et-pr)

---

# 🇬🇧 English Version

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

## 4. Mandatory Documentation Formalism (Bilingual EN/FR & Mini-TOC)

> [!IMPORTANT]
> **Strict Documentation Rule for AI Agents:**
> Every documentation file (`.md`) created or updated across the project — **with the exception of files inside `.agents/skills/`** — **MUST strictly follow this bilingual structure**:
> 1. **Bilingual Header & Metadata:** Bilingual title and description banner.
> 2. **Top Navigation & Mini-Summary (Sommaire):**
>    - Language anchor buttons: `<a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>`
>    - A compact bilingual **mini-table of contents** (Sommaire) with direct anchor links to each section in both languages.
> 3. **Separated English Block (`# 🇬🇧 English Version`):** The entire English documentation.
> 4. **Separator (`---`):** Clear horizontal divider between the two versions.
> 5. **Separated French Block (`# 🇫🇷 Version Française`):** The complete French documentation, faithfully mirroring the English content.
> 6. **Zero Interleaved Content:** Never interleave paragraphs sentence-by-sentence. Always provide two complete, self-contained language blocks.

### Standard Documentation Template:
```markdown
# [Title in English] / [Titre en Français]

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** ...
> - **Origin / Provenance :** `master-dev`

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Section](#1-section) · [2. Section](#2-section)
> - 🇫🇷 **Français :** [1. Section](#1-section-fr) · [2. Section](#2-section-fr)

---

# 🇬🇧 English Version
...

---

# 🇫🇷 Version Française
...
```

---

## 5. Essential Commands & Taskfile Reference

Task automation is driven by [Taskfile](https://taskfile.dev/). For a full pedagogical explanation of when and why to call each task, see the **[Task Commands & Modding Scripts Reference](docs/modding/tools/task_scripts_reference.md)**.

```bash
# Game selection
task set-game-jak1          # Switch active target game to Jak 1
task set-game-jak2          # Switch active target game to Jak 2
task set-game-jak3          # Switch active target game to Jak 3

# Building & Compilation (3-Layer Rule)
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
task boot-game              # Boot game directly in debug mode
task boot-game-retail       # Boot game in retail mode (-boot -fakeiso) to test Mods Menu (L3 + SELECT)
task run-game               # Run game with REPL attached
task format                 # Format C++ and GOAL code

# Modding workflow wrappers (scripts/modding/*.py — pass args after `--`)
task modding-new-branch -- jak2/features/my-mod   # Create new mod branch from master-dev + README template
task modding-sync-branch                          # YOUR branch only: safe git merge of master-dev into it (sync_branch_with_master_dev.py)
task modding-sync-docs                            # Pull docs/modding + AGENTS.md + CLAUDE.md from master-dev
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
task modding-branch-status                        # EVERY mod branch: test/refresh sync status (sync_branches_with_master.py)
task modding-audit                                # Regenerate docs/modding/branch_audit.md
task modding-sync-catalog                          # Regenerate master-dev root index.json from published releases
```

> [!IMPORTANT]
> **Task Execution Policy:** Agents must **NEVER** run long-running build or runtime `task` commands silently in the background without explicit user request. Always propose the exact command for the user to execute in their terminal.

---

## 6. CI/CD & GitHub Actions Workflows

Our repository relies on 6 specialized GitHub Actions workflows. For a comprehensive pedagogical breakdown, see **[GitHub Actions Workflows Guide](docs/modding/tools/github_workflows.md)**:

1. **`sync-upstream.yaml`** (Daily Cron at 10:00 UTC / Dispatch): Fast-forwards `master` from official OpenGOAL, updates `master-dev`, auto-merges clean mod branches (`scripts/modding/sync_branches_with_master.py`), and updates the conflict dashboard (`branch_sync_status.md`).
2. **`branch-sync-check.yaml`** (Push on `jak[1-3]/**` / Dispatch): Lightweight ancestry check against `master-dev`. Powers each mod branch's live GitHub Actions status badge in its `README.md`.
3. **`release.yml`** (Manual `workflow_dispatch` only): Builds complete static binaries (Clang + Ninja) for Windows and Linux from clean source, packages assets, publishes GitHub Releases, computes SHA256 hashes, and updates `index.json`.
4. **`mod-bug-report-sync.yml`** (Release events): Queries GitHub Releases to keep the bug report dropdown strictly aligned with released mods.
5. **`mod-bug-triage.yml`** (Issues opened/edited with `mod-bug`): Parses the issue form and auto-applies game and `mod:<slug>` labels.
6. **`sync-global-catalog.yml`** (Release events / Workflow call / Dispatch): Aggregates all published releases into the root `index.json` on `master-dev` so players can subscribe to a single catalog URL in the OpenGOAL Launcher.

---

## 7. Development Cycle: REPL Hot-Reload vs Cold Boot

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

### Default Save Slot 1 & Settings/Cheats Persistence
- **Default Auto-Load:** When the game boots (`task boot-game` / cold boot), OpenGOAL automatically reads the simulated memory card and **restores Save Slot 1 by default** if a save file exists (`%APPDATA%/OpenGOAL/jak[x]/saves/BASCUS-.../bank0.bin`). If you need to test fresh, unprogressed game behavior, start a new game or temporarily clear/rename Slot 1.
- **Persistent PC Settings & Cheats:** OpenGOAL settings and toggled cheats (e.g. `city-peace`, `turbo-board`, `music-player`) are saved to disk in `%APPDATA%/OpenGOAL/jak[x]/settings/pc-settings.gc`. Once a cheat is enabled (via the in-game Debug menu or Secrets menu), it is written to the `(cheats ...)` bitmask in `pc-settings.gc` and remains **permanently active across subsequent launches** until toggled off in-game or cleared in the file.

---

## 8. Strict Modding Instructions & Guardrails

All mod development must adhere to the conventions documented in this guide, the [Modding Documentation Hub](docs/modding/README.md), and specialized skills in [`.agents/skills/`](.agents/skills/).

### 🥇 Golden Rules
1. **Consult Reference Docs First:**
   - 📗 `docs/modding/jak[1|2|3]_lisp_instructions.md` — Verified OpenGOAL LISP reference. **Never hallucinate or invent an instruction.**
   - 📘 [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) — Shared engine concepts (memory heaps, DGOs, process lifecycle).
2. **Native Non-Regression:**
   - A mod MUST NOT alter default game behavior unless explicitly requested.
   - All behavior changes must ship **OFF by default**, gated behind the mod's runtime toggle.
3. **In-Game Mods Toggle Mandatory (Especially for `features/*`):**
   - Every newly created mod — and **strictly without exception for any `features/*` mod** — must register an in-game toggle in the unified Mods menu (`mods-menu-register "<slug>" builder`).
   - The mod must be switchable on/off at runtime from a **retail boot** (the default launcher boot mode, `-boot -fakeiso`), not only in debug mode.
   - **Jak 2 / Jak 3:** The Mods menu opens in-game with **L3 + SELECT** in both retail and debug boots. Register via `(mods-menu-register "<slug>" builder)`. See [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md) and template [`docs/modding/templates/mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc).
   - **Never Edit Shared Menus:** Never edit `default-menu*.gc` directly, and never put your menu file behind `(declare-file (debug))` — a DEBUG segment is not linked in a retail boot.
   - **Jak 1:** Prefix submenus cleanly with the mod slug, and document in the mod README that the toggle is debug-only.
   - **Audit Enforcement:** Any `features/*` branch lacking an active `mods-menu-register` call is considered non-compliant and will be flagged as an action item by `task modding-audit`.
4. **Mandatory In-Code Comments:**
   - Every function, method, state, hook, and type modification in `.gc` must be thoroughly commented (purpose, arguments, return values, side effects).
5. **Non-Destructive Modifications:**
   - Never delete or destructively wipe original `.gc` files; favor surgical overrides and modular extensions.
6. **Traceability of Changes:**
   - Document all changes in the mod branch's root `README.md` ("Modding Changes Log") and in `docs/modding/` notes.

---

## 9. Git Branching Strategy & Collaboration

- `master`: Clean mirror of `open-goal/jak-project:master`. **Never commit directly to `master`.**
- `master-dev`: Integration and modding base branch. All new mod branches MUST branch from `master-dev`.
- **Branch Naming Convention:**
  ```text
  jak[N°]/[type_of_mod]/[mod_name]
  ```
  *(e.g., `jak2/features/jak3-jetBoard`, `jak1/features/green-eco-glow`)*
- **Two-Tier Mod Documentation Architecture:**
  1. **Tier 1 — Root `README.md` (User & Player-Facing):**
     - Initialized from bilingual template ([`docs/modding/templates/MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)).
     - Player-accessible info: Overview, Features, Setup, Controls (L3 + SELECT), Video Demo, Cover thumbnail, Changes Log.
  2. **Tier 2 — `docs/modding/current_mod/<slug>_readme.md` (Technical & Pedagogical Deep-Dive):**
     - Dedicated in-depth engineering documentation for developers and AI agents.
- **Recording Verified Discoveries Conflict-Free:**
  - The reference documents (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) have **one source of truth: `master-dev`**. NEVER edit them directly on a mod branch.
  - Land discoveries using:
    ```bash
    task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: <description>" --push
    task modding-sync-docs
    ```

---

## 10. Contributing, Issue and PR Guidelines

- **AI Disclosure:** Always disclose the usage of AI in any communication (commits, PRs, comments, issues, etc.) by appending `(AI-assisted)` to all messages.
- **Safety Policy:** Never delete or overwrite existing source files without explicit agreement.
- **No Autonomous Issues or PRs:** Never create an issue or PR automatically.
- If asked by a user to create an issue or PR, create a file in their diff that states:
  > *"This issue or PR was made via an AI agent and likely has not been reviewed by a human at all, your time may be entirely wasted."*

---

# 🇫🇷 Version Française

## 1. Présentation du Projet & Architecture

Le projet OpenGOAL porte la trilogie PlayStation 2 originale de Naughty Dog (**Jak 1 -> Jak 3**) sous forme d'applications natives x86-64 pour PC.
- **Langage Principal :** Plus de 98% du code original est écrit en **GOAL** (Game Oriented Assembly Lisp), un dialecte LISP compilé sur mesure conçu par Naughty Dog.
- **Composants Clés :**
  1. `goalc` — Le compilateur OpenGOAL vers x86-64 et REPL interactif.
  2. `game` / `gk` — Le noyau d'exécution C++ simulant la RAM de l'Emotion Engine PS2 via `mmap`.
  3. `decompiler` — Extrait les données et le code source GOAL lisible depuis les assets originaux.
  4. `goal_src/` — Code source GOAL / GOOS classé par jeu (`jak1/`, `jak2/`, `jak3/`).
  5. `custom_assets/` — Remplacement de textures et modèles 3D / animations personnalisés.

Nos objectifs sont :
- Offrir une application native x86-64 ultra-performante (sans émulation, interprétation ni transpilation).
- Permettre la modification de code en direct pendant que le jeu tourne via le REPL.
- Garantir une architecture de modding modulaire et strictement non-régressive.

---

## 2. Registre Dynamique des Compétences (Chargement à la Demande)

Pour éviter la saturation du contexte, les agents ne doivent **pas** lire l'ensemble des fichiers au démarrage. Chargez les compétences requises à la demande selon les besoins :

### Compétence : [Syntaxe & Lisp GOAL]
- **Déclencheur :** Écriture ou débogage de code GOAL (`.gc`), machines à états (`defstate`, `defbehavior`), types ou macros.
- **Chemin :** [`.agents/skills/goal-lisp/SKILL.md`](.agents/skills/goal-lisp/SKILL.md) et [`.agents/skills/goal-lisp/discoveries.md`](.agents/skills/goal-lisp/discoveries.md).

### Compétence : [Internes du Moteur & Workflow REPL]
- **Déclencheur :** Architecture moteur, runtime C++ (`gk`), compilateur (`goalc`), décompilateur, cycle REPL, gestion mémoire/heaps, commandes Taskfile.
- **Chemin :** [`.agents/skills/engine-internals/SKILL.md`](.agents/skills/engine-internals/SKILL.md) et [`.agents/skills/engine-internals/repl-workflow.md`](.agents/skills/engine-internals/repl-workflow.md).

### Compétence : [Acteurs Personnalisés & Assets 3D]
- **Déclencheur :** Ajout de modèles `.glb`, armatures, canaux d'articulations, imports Blender, animations, entités custom, banques de sons (SBK) ou niveaux.
- **Chemin :** [`.agents/skills/custom-actors-levels/SKILL.md`](.agents/skills/custom-actors-levels/SKILL.md) et [`.agents/skills/custom-actors-levels/discoveries.md`](.agents/skills/custom-actors-levels/discoveries.md).

### Compétence : [Modding de Textures]
- **Déclencheur :** Remplacement de textures, pages de textures (`tpage`), extraction et fusion de textures.
- **Chemin :** [`.agents/skills/texture-modding/SKILL.md`](.agents/skills/texture-modding/SKILL.md) et [`.agents/skills/texture-modding/discoveries.md`](.agents/skills/texture-modding/discoveries.md).

---

## 3. Règle d'Alimentation de la Mémoire à Long Terme

Afin d'enrichir continuellement la base de connaissances du projet, chaque agent doit respecter cette consigne :

> **« Dès que vous identifiez un comportement non documenté, un piège de syntaxe en GOAL ou la résolution d'un crash moteur lors d'un mod, vous devez ajouter une entrée concise (moins de 10 lignes) avec extrait de code dans `.agents/skills/<relevant-skill>/discoveries.md` avant de conclure la tâche. »**

---

## 4. Formalisme Obligatoire de Documentation (Bilingue EN/FR & Mini-Sommaire)

> [!IMPORTANT]
> **Règle Formelle Obligatoire pour les Agents IA :**
> Tout fichier de documentation (`.md`) créé ou mis à jour dans le dépôt — **à l'exception des fichiers sous `.agents/skills/`** — **DOIT impérativement respecter ce formalisme bilingue** :
> 1. **En-tête Bilingue & Métadonnées :** Titre bilingue et cartouche d'information.
> 2. **Navigation Haute & Mini-Sommaire :**
>    - Boutons d'ancrage de langue : `<a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>`
>    - Un **mini-sommaire** compact avec liens cliquables directs vers chaque section dans les deux langues.
> 3. **Bloc Anglais Séparé (`# 🇬🇧 English Version`) :** L'intégralité du document en anglais.
> 4. **Séparateur Horizontal (`---`) :** Séparation visuelle nette entre les deux versions.
> 5. **Bloc Français Séparé (`# 🇫🇷 Version Française`) :** L'intégralité du document en français, reflétant fidèlement le contenu anglais.
> 6. **Aucun Entrelacement :** Ne jamais mélanger les langues paragraphe par paragraphe ou phrase par phrase. Toujours fournir deux blocs distincts et autonomes.

---

## 5. Commandes Essentielles & Référence Taskfile

L'automatisation des tâches s'effectue via [Taskfile](https://taskfile.dev/). Pour une explication pédagogique détaillée de chaque commande, consultez la **[Référence des Commandes Task & Scripts de Modding](docs/modding/tools/task_scripts_reference.md)**.

```bash
# Sélection du jeu actif
task set-game-jak1          # Cible Jak 1
task set-game-jak2          # Cible Jak 2
task set-game-jak3          # Cible Jak 3

# Compilation C++ (Règle des 3 couches)
task gen-cmake-release      # Configure CMake (Ninja + Clang) ; active sccache automatiquement
task build-release          # Compile les ~20 binaires (première installation / audit complet)
task build-release-game     # Compile UNIQUEMENT gk + goalc — itération rapide moteur C++
task build-release-decomp   # Compile UNIQUEMENT le décompilateur (decompiler/)
task build-debug            # Équivalents Debug : build-debug-game, build-debug-decomp
task extract                # Extrait les assets et lance le décompilateur

# REPL Interactif & Rechargement à Chaud (les modifications .gc ne nécessitent aucun build C++)
task repl                   # Ouvre le shell interactif goalc
# Dans le REPL :
(mi)                        # Compile incrémentalement et réinjecte dans le jeu en cours d'exécution

# Exécution du Jeu
task boot-game              # Lance le jeu directement en mode debug
task boot-game-retail       # Lance le jeu en mode retail (-boot -fakeiso) pour tester le menu Mods (L3 + SELECT)
task run-game               # Lance le runtime en attente du REPL
task format                 # Formate le code C++ et GOAL

# Scripts de Modding (scripts/modding/*.py — arguments passés après `--`)
task modding-new-branch -- jak2/features/mon-mod   # Crée une branche depuis master-dev + README template
task modding-sync-branch                           # Votre branche : fusionne proprement master-dev (sync_branch_with_master_dev.py)
task modding-sync-docs                             # Rapatrie docs/modding + AGENTS.md + CLAUDE.md depuis master-dev
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
task modding-branch-status                         # Toutes les branches : audite et synchronise (sync_branches_with_master.py)
task modding-audit                                 # Régénère docs/modding/branch_audit.md
task modding-sync-catalog                          # Régénère le catalogue global index.json racine depuis les Releases
```

> [!IMPORTANT]
> **Politique d'Exécution des Tâches :** Les agents ne doivent **JAMAIS** lancer de commandes `task` longues ou bloquantes en arrière-plan sans demande explicite de l'utilisateur. Proposez toujours la commande exacte à exécuter dans son terminal.

---

## 6. Workflows CI/CD & GitHub Actions

Notre dépôt s'appuie sur 6 workflows GitHub Actions spécialisés. Pour un guide pédagogique complet, consultez le **[Guide des Workflows GitHub Actions](docs/modding/tools/github_workflows.md)** :

1. **`sync-upstream.yaml`** (Cron quotidien à 10:00 UTC / Dispatch) : Avance rapide de `master` depuis l'OpenGOAL officiel, synchronisation de `master-dev`, auto-fusion des branches saines (`scripts/modding/sync_branches_with_master.py`) et mise à jour du tableau de bord (`branch_sync_status.md`).
2. **`branch-sync-check.yaml`** (Push sur `jak[1-3]/**` / Dispatch) : Vérification de filiation légère avec `master-dev`. Pilote le badge d'état GitHub Actions natif dans le `README.md` de chaque mod.
3. **`release.yml`** (Manuel `workflow_dispatch` uniquement) : Compile les binaires statiques complets (Clang + Ninja) sous Windows et Linux, package les assets, publie la Release GitHub, génère les empreintes SHA256 et met à jour `index.json`.
4. **`mod-bug-report-sync.yml`** (Événements de Release) : Interroge l'API GitHub Releases pour restreindre le formulaire de bug aux mods réellement publiés.
5. **`mod-bug-triage.yml`** (Issues ouvertes/modifiées avec `mod-bug`) : Analyse le formulaire et applique automatiquement les labels de jeu et de mod (`mod:<slug>`).
6. **`sync-global-catalog.yml`** (Événements de Release / Appel de workflow / Dispatch) : Agrège l'ensemble des releases publiées dans le catalogue `index.json` à la racine de `master-dev` pour permettre aux joueurs de s'abonner à une source unique dans le Launcher.

---

## 7. Cycle de Développement : Rechargement à Chaud (REPL) vs Boot à Froid

### Le Cycle de Rechargement à Chaud `(mi)`
- Lors de l'édition de fichiers `.gc`, aucune recompilation C++ n'est requise.
- Dans le REPL `goalc`, lancez `(mi)` pour recompiler incrémentalement et injecter instantanément vos fonctions et états dans la RAM du jeu.

### Le Piège de la Mémoire Fantôme & Vérification au Démarrage à Froid
- **Le Danger :** Lors du rechargement à chaud via `(mi)`, d'anciennes définitions, symboles et structures obsolètes persistent dans la mémoire simulée PS2.
- Si vous modifiez la disposition des champs d'une structure ou réordonnez des déclarations, le code peut fonctionner dans votre session REPL tout en étant irrémédiablement brisé lors d'un démarrage propre.
- **Règle Obligatoire du Boot à Froid :** Validez systématiquement vos changements avec un démarrage complet à froid avant de conclure :
  ```bash
  task boot-game
  ```

### Enregistrement des Fichiers Projet (`.gp`)
Dès l'ajout d'un nouveau fichier source `.gc`, vous **devez l'enregistrer** dans le fichier `.gp` correspondant :
- Jak 1 : `goal_src/jak1/game.gp`
- Jak 2 : `goal_src/jak2/jak2-game.gp`
- Jak 3 : `goal_src/jak3/jak3-game.gp`

---

## 8. Instructions Strictes de Modding & Règles d'Or

### 🥇 Les Règles d'Or
1. **Consulter la Documentation Avant de Coder :**
   - 📗 `docs/modding/jak[1|2|3]_lisp_instructions.md` — Référence LISP OpenGOAL vérifiée. **Ne jamais inventer une instruction.**
   - 📘 [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) — Concepts moteur partagés.
2. **Non-Régression Native :**
   - Un mod NE DOIT PAS altérer le comportement d'origine du jeu sauf demande explicite.
   - Tout changement doit être **désactivé par défaut (OFF)**, accessible via l'interrupteur du mod.
3. **Menu « Mods » en Jeu Obligatoire (En particulier pour les branches `features/*`) :**
   - Chaque nouveau mod doit enregistrer son entrée dans le menu Mods unifié via `(mods-menu-register "<slug>" builder)`.
   - Le mod doit pouvoir être activé/désactivé en **boot retail** (le boot officiel du launcher, `-boot -fakeiso`).
   - **Jak 2 / Jak 3 :** Le menu s'ouvre avec **L3 + SELECT**. Voir [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md).
   - **Ne jamais éditer les menus partagés :** Ne modifiez jamais directement `default-menu*.gc` et ne placez pas votre fichier de menu derrière un segment debug.
4. **Commentaires Obligatoires dans le Code :**
   - Chaque fonction, méthode, état et macro ajoutés en `.gc` doivent être abondamment commentés.
5. **Modifications Non-Destructives :**
   - Ne détruisez jamais les fichiers originaux ; privilégiez les surcharges chirurgicales.
6. **Traçabilité des Changements :**
   - Consignez les modifications dans le `README.md` du mod (« Modding Changes Log »).

---

## 9. Stratégie de Branches Git & Collaboration

- `master` : Miroir propre d'`open-goal/jak-project:master`. **Ne jamais commiter sur `master`.**
- `master-dev` : Branche d'intégration et base de modding. Toute branche de mod DOIT partir de `master-dev`.
- **Convention de Nommage des Branches :**
  ```text
  jak[N°]/[type_du_mod]/[nom_du_mod]
  ```
- **Architecture de Documentation à Deux Niveaux :**
  1. **Niveau 1 — `README.md` Racine (Joueur & Utilisateur) :** Initialisé depuis le template bilingue ([`docs/modding/templates/MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)).
  2. **Niveau 2 — `docs/modding/current_mod/<slug>_readme.md` (Approfondissement Technique) :** Documentation d'ingénierie détaillée pour développeurs et agents IA.
- **Intégration Sans Conflit des Découvertes :**
  - Les documents de référence ont une source unique : `master-dev`.
  - Intégrez vos ajouts via :
    ```bash
    task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: <description>" --push
    task modding-sync-docs
    ```

---

## 10. Directives de Contribution, Tickets et PR

- **Divulgation de l'IA :** Mentionnez toujours l'assistance de l'IA dans vos messages de commit et PR en ajoutant `(AI-assisted)`.
- **Politique de Sécurité :** Ne supprimez ou n'écrasez aucun fichier source sans accord préalable.
- **Aucune PR/Issue Autonome :** Ne créez jamais d'issue ou de pull request de façon autonome.
