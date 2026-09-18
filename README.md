<p align="center">
  <img width="500" height="100%" src="./docs/img/logo-text-colored-new.png" alt="OpenGOAL Modding Hub">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Modding-blue.svg" alt="OpenGOAL Modding">
  <img src="https://img.shields.io/badge/Branch-master--dev-orange.svg" alt="Branch">
  <img src="https://img.shields.io/badge/Games-Jak%201%20%7C%20Jak%202%20%7C%20Jak%203-green.svg" alt="Jak Trilogy">
  <img src="https://img.shields.io/badge/AI--assisted-Research%20%26%20Dev-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [Purpose & Approach](#-purpose-and-approach) · [Git Architecture & CI/CD](#-git-architecture--cicd-workflows) · [Mod Branch Synchronization](#-mod-branch-synchronization) · [Directory Overview](#-directory-overview) · [Task Command Reference](#-task-command-reference)
> - 🇫🇷 **Français :** [Démarche & Objectif](#-démarche--objectif-du-projet) · [Architecture Git & CI/CD](#-architecture-git--workflows-cicd) · [Synchronisation des Branches de Mods](#-synchronisation-des-branches-de-mods) · [Vue d'ensemble des Répertoires](#-vue-densemble-des-répertoires) · [Référence des Commandes Task](#-référence-des-commandes-task)

---

# 🇬🇧 English Version

## 🎯 Purpose and Approach

This project is an unofficial fork of [OpenGOAL](https://github.com/open-goal/jak-project), with no direct affiliation with the original OpenGOAL team or Naughty Dog. For the original technical documentation and build instructions of the native port, please refer to the [original OpenGOAL README](open-goal-original-readme.md).

### Objectives
The goal of this repository is to explore the use of AI to create mods for the Jak trilogy (*Jak and Daxter: The Precursor Legacy*, *Jak II*, *Jak 3*).

### Code Reliability and Approach
* **Modifications to compiler & decompiler:** Some liberties were taken with the GOAL compiler (`goalc`), the C++ runtime (`game`), and the extraction tools (`decompiler`) to change default behaviors and facilitate AI-assisted modding.
* **Code reliability:** The code is not guaranteed to be 100% reliable. The focus is to reach the intended objective for each mod. Most commits created with agent assistance include the `(AI-assisted)` tag.
* **Documentation for developers:** Two curated bilingual references live under `docs/modding/` — `jak[x]_lisp_instructions.md` (verified OpenGOAL Lisp per game) and `engine_generic_concepts.md` (shared engine architecture). Agents consult them before coding and never hallucinate an instruction. Mod-specific notes live in each mod branch's root `README.md`.
* **Two golden rules:** (1) **native non-regression** — a mod never changes default behaviour unless its spec requires it; changes ship OFF by default; (2) **In-game Mods toggle** — every mod is switchable at runtime from the in-game Mods menu (L3 + SELECT), which works in a normal launcher boot.
* **Dedicated mod README:** Each mod branch features its own `README.md` at the root of the repository, including an installation guide, feature list, usage instructions, and a demo video.
* **Contributions & feedback:** Constructive feedback and contributions are welcome.

---

## 🌿 Git Architecture & CI/CD Workflows

```text
[open-goal/jak-project] (upstream/master)
         │  (Daily automatic sync at 10:00 UTC: sync-upstream.yaml)
         ▼
  [whozghiar/jak-project] (origin/master)      <── Clean upstream mirror (no custom commits)
         │
         │  (Fast-forward / automatic merge)
         ▼
  [whozghiar/jak-project] (origin/master-dev)  <── Modding base branch (tools, docs, stable base)
         │
         ├── New mod branch: jak[N]/[type]/[name]
         │      │
         │      ├── Root README.md automatically initialized for the mod
         │      ├── Mod source code (goal_src/) + Modding Changes Log in the root README
         │      └── Automated health checks on push (branch-sync-check.yaml)
         │
         └── Live branch status and conflict tracking dashboard (branch_sync_status.md)
```

### GitHub Actions Workflows Pipeline
Our repository relies on 5 specialized CI/CD workflows. For complete architectural documentation and detailed triggers, see the **[GitHub Actions Workflows Guide](docs/modding/tools/github_workflows.md)**:

1. **[`sync-upstream.yaml`](.github/workflows/sync-upstream.yaml)** *(Daily Cron at 10:00 UTC / Dispatch)*: Fast-forwards `master` from official OpenGOAL, updates `master-dev`, auto-merges clean mod branches via [`scripts/modding/sync_branches_with_master.py`](scripts/modding/sync_branches_with_master.py), and generates the live conflict dashboard ([`branch_sync_status.md`](docs/modding/tools/branch_sync_status.md)).
2. **[`branch-sync-check.yaml`](.github/workflows/branch-sync-check.yaml)** *(On push to `jak[1-3]/**` / Dispatch)*: Lightweight ancestry check verifying that a mod branch is strictly up-to-date with `master-dev`. Powers each mod branch's live status badge in its `README.md`.
3. **[`release.yml`](.github/workflows/release.yml)** *(Manual `workflow_dispatch`)*: Builds fully static Windows and Linux binaries from clean source, packages assets, publishes GitHub Releases, computes SHA256 hashes, and updates the `index.json` catalog for the OpenGOAL Launcher (see **[Mod Distribution Guide](docs/modding/tools/mod_distribution_guide.md)**).
4. **[`mod-bug-report-sync.yml`](.github/workflows/mod-bug-report-sync.yml)** *(On Release)*: Syncs released mods to the GitHub issue bug report dropdown form.
5. **[`mod-bug-triage.yml`](.github/workflows/mod-bug-triage.yml)** *(On Issue open/edit)*: Parses player bug reports and auto-applies game and mod labels (see **[Mod Bug Tracking Guide](docs/modding/tools/mod_bug_tracking.md)**).

> [!NOTE]
> **Conflict-Free Documentation Strategy:**
> The reference docs (`docs/modding/jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) have a single source of truth: `master-dev`. They are updated directly via `task modding-land-doc` (append-only), then pulled into mod branches with `task modding-sync-docs`. This design guarantees that parallel mod branches never conflict on shared documentation.

---

## 📊 Mod Branch Synchronization

[![Sync Upstream](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml/badge.svg)](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml)

This badge indicates the state of the automated daily synchronization workflow (`sync-upstream.yaml`) running at 10:00 UTC:
- **Green:** The latest sync (upstream → `master` → `master-dev` → mod branches) completed successfully with all clean branches merged.
- **Red:** A conflict or failure occurred during the synchronization pipeline.

Per-branch mergeability details and ready-to-run resolution commands are tracked on `master-dev`:
- 📋 **Live Status Dashboard:** [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md) *(master-dev only, updated on every sync)*
- 📜 **Full Merge History:** [`docs/modding/tools/branch_sync_history.md`](docs/modding/tools/branch_sync_history.md)

Each individual mod branch also carries its own live status badge in its root `README.md` driven by [`branch-sync-check.yaml`](.github/workflows/branch-sync-check.yaml). For full operational details, refer to the **[GitHub Actions Workflows Guide](docs/modding/tools/github_workflows.md)**.

---

## 📂 Directory Overview

| Directory / File | Description |
| :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Unified AI agent directives and modding rules (branching, golden rules, REPL workflow, task reference). |
| [`.agents/skills/`](.agents/skills/) | Modularized developer and agent skills (GOAL Lisp, engine internals, 3D assets/actors, texture modding). |
| [`docs/modding/`](docs/modding/README.md) | Modding documentation hub (verified Lisp references, engine primer, engineering workflows, tools). |
| [`docs/modding/tools/github_workflows.md`](docs/modding/tools/github_workflows.md) | **Comprehensive guide to all 5 GitHub Actions CI/CD workflows**, triggers, and branch synchronization. |
| [`docs/modding/tools/task_scripts_reference.md`](docs/modding/tools/task_scripts_reference.md) | **Pedagogical reference for all `task` commands** and modding automation scripts. |
| [`docs/modding/tools/mod_bug_tracking.md`](docs/modding/tools/mod_bug_tracking.md) | Bug reporting automation, release synchronization, and issue triage. |
| [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md) | Live mergeability dashboard across all mod branches (`task modding-branch-status`). |
| [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md) | Unified in-game Mods menu architecture (`mods-menu-register`, L3 + SELECT). |
| [`docs/modding/how_to_install_mod.md`](docs/modding/how_to_install_mod.md) | Step-by-step player guide to installing mods via the official OpenGOAL Launcher. |
| [`docs/saves/`](docs/saves/README.md) | **100% completion save files** for Jak 1, Jak 2, and Jak 3 (Vanilla game and Mods). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | **Verified** OpenGOAL Lisp reference per game — consult before coding. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Shared non-Lisp engine primer (memory, heaps, DGOs, level streaming, process life cycle). |
| [`docs/modding/templates/`](docs/modding/templates/) | [`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Generated per-branch compliance report (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Python automation (branch creation, branch/doc sync, doc landing, branch audit). |
| [`goal_src/`](goal_src/) | Decompiled and modified GOAL source code by game (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | OpenGOAL compiler with modding adjustments. |
| [`game/`](game/) | C++ runtime simulating the Emotion Engine memory on PC. |
| [`decompiler/`](decompiler/) | Asset extraction and decompiler tools. |
| [`custom_assets/`](custom_assets/) | Custom texture replacements and models. |

---

## 🛠️ Task Command Reference

> Automation and builds are driven by [Taskfile](https://taskfile.dev/). Pass script arguments after `--`.
> For an in-depth pedagogical explanation of when and why to use each task, see the **[Task Commands & Modding Scripts Reference](docs/modding/tools/task_scripts_reference.md)**.

### Active Target Game Selection
| Command | Purpose |
| :--- | :--- |
| `task set-game-jak1` · `-jak2` · `-jak3` | Persist active target game configuration (`jak1`, `jak2`, or `jak3`) |

### Build & CMake (3-Layer Rule)
| Command | Purpose |
| :--- | :--- |
| `task gen-cmake-release` | Configure CMake build system (Ninja + Clang); auto-wires `sccache` if installed |
| `task build-release` | Build **all** ~20 binaries (first setup / full regression check) |
| `task build-release-game` | Build **only** `gk` + `goalc` — fast iteration for engine runtime & compiler C++ |
| `task build-release-decomp` | Build **only** the decompiler — use after changing `decompiler/`, then re-extract |
| `task build-debug` / `-debug-game` / `-debug-decomp` | Debug build equivalents with full symbols |
| `task clean-cmake` | Remove build artifacts and CMake cache |

### Asset Extraction & Decompilation
| Command | Purpose |
| :--- | :--- |
| `task extract` | Extract retail assets and run the decompiler (run after decompiler config edits) |
| `task decomp` / `decomp-file FILE=…` | Decompile all objects or a single specific GOAL object |
| `task rip-textures` / `rip-levels` / `rip-collision` / `rip-audio` | Rip specific asset categories |

### Interactive REPL & Game Execution
| Command | Purpose |
| :--- | :--- |
| `task repl` → `(mi)` | Start compiler REPL; `(mi)` hot-reloads GOAL code directly into running RAM (**no C++ build needed**) |
| `task boot-game` | Boot game executable in debug mode without attaching REPL |
| `task boot-game-retail` | Boot game in retail mode (`-boot -fakeiso`) to test Mods menu (L3 + SELECT) |
| `task run-game` | Launch runtime process driven and monitored via REPL connection |
| `task format` / `format-gsrc FILE=…` | Format all C++ and GOAL source code or a single `.gc` file |

### Modding Workflow Scripts
| Command | Purpose |
| :--- | :--- |
| `task modding-new-branch -- jak2/features/x` | Create a new mod branch from `master-dev` with template `README.md` |
| `task modding-sync-branch` | Safely merge `master-dev` into your current mod branch (`-- --rebase` / `-- --push`) |
| `task modding-sync-docs` | Pull latest `docs/modding`, `AGENTS.md`, and `CLAUDE.md` from `master-dev` |
| `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "…" --push` | Land verified Lisp discoveries on `master-dev` conflict-free, then re-sync |
| `task modding-branch-status` | Refresh mergeability of all mod branches against `master-dev` (`branch_sync_status.md`) |
| `task modding-audit` | Regenerate repo-wide compliance audit report (`docs/modding/branch_audit.md`) |

### Automated Tests
| Command | Purpose |
| :--- | :--- |
| `task offline-tests` / `offline-tests-fast` | Run decompiler regression tests against retail binaries |
| `task unit-tests` / `tests-filtered FILTER=…` | Run `goalc` compiler unit test suite |

---

# 🇫🇷 Version Française

## 🎯 Démarche & Objectif du Projet

Ce dépôt est un **fork non officiel** du projet [OpenGOAL](https://github.com/open-goal/jak-project), sans affiliation directe avec l'équipe originelle d'OpenGOAL ou Naughty Dog. Pour la documentation technique et les instructions de compilation du port de base, consultez le [README originel d'OpenGOAL](open-goal-original-readme.md).

### Objectifs
L'objectif de ce projet est d'utiliser l'IA pour créer des mods pour la trilogie Jak (*Jak and Daxter: The Precursor Legacy*, *Jak II*, *Jak 3*).

### Fiabilité du code et démarche
* **Modifications du compilateur et décompilateur :** Certaines libertés ont été prises au niveau du compilateur GOAL (`goalc`), du runtime C++ (`game`) et des outils d'extraction (`decompiler`) pour modifier des comportements natifs du projet original et faciliter le modding avec l'IA.
* **Fiabilité du code :** Le code produit avec l'assistance d'agents IA n'est pas garanti fiable à 100%. L'accent est mis sur l'atteinte de l'objectif fixé pour chaque mod. La plupart des commits correspondants portent la mention `(AI-assisted)`.
* **Documentation pour les développeurs :** Deux références bilingues curatées sous `docs/modding/` — `jak[x]_lisp_instructions.md` (Lisp OpenGOAL vérifié par jeu) et `engine_generic_concepts.md` (architecture moteur partagée). Les agents les consultent avant de coder et n'hallucinent jamais d'instruction. Les notes propres à un mod vivent dans le `README.md` racine de sa branche.
* **Deux règles d'or :** (1) **non-régression native** — un mod ne change jamais le comportement par défaut sauf si son cahier des charges l'exige ; les changements sont livrés DÉSACTIVÉS par défaut ; (2) **bascule Mods en jeu** — tout mod est activable/désactivable à la volée depuis le menu Mods en jeu (L3 + SELECT), qui fonctionne dans un boot normal du launcher.
* **README dédié par mod :** Chaque branche de mod dispose à sa racine d'un fichier `README.md` décrivant : le guide d'installation, les fonctionnalités du mod, son utilisation et une vidéo démonstrative.
* **Contributions et retours :** Toute contribution ou suggestion est accueillie avec grand plaisir, tant qu'elle reste constructive et bienveillante.

---

## 🌿 Architecture Git & Workflows CI/CD

```text
[open-goal/jak-project] (upstream/master)
         │  (Synchronisation quotidienne automatique à 10:00 UTC : sync-upstream.yaml)
         ▼
  [whozghiar/jak-project] (origin/master)      <── Miroir amont propre (aucun commit custom)
         │
         │  (Fast-forward / fusion automatique)
         ▼
  [whozghiar/jak-project] (origin/master-dev)  <── Branche de base modding (outils, docs, base stable)
         │
         ├── Nouvelle branche de mod : jak[N]/[type]/[nom]
         │      │
         │      ├── README.md racine initialisé automatiquement pour le mod
         │      ├── Code source du mod (goal_src/) + Journal des modifications dans le README
         │      └── Vérifications de santé automatiques au push (branch-sync-check.yaml)
         │
         └── Tableau de bord en direct de l'état des branches (branch_sync_status.md)
```

### Pipeline des Workflows GitHub Actions
Notre dépôt repose sur 5 workflows CI/CD spécialisés. Pour une documentation architecturale complète et le détail des déclencheurs, consultez le **[Guide des Workflows GitHub Actions](docs/modding/tools/github_workflows.md)** :

1. **[`sync-upstream.yaml`](.github/workflows/sync-upstream.yaml)** *(Cron quotidien à 10:00 UTC / Dispatch)* : Rapatrie les nouveautés d'OpenGOAL amont sur `master`, met à jour `master-dev`, fusionne automatiquement les branches de mods prêtes via [`scripts/modding/sync_branches_with_master.py`](scripts/modding/sync_branches_with_master.py), et actualise le tableau de bord des conflits ([`branch_sync_status.md`](docs/modding/tools/branch_sync_status.md)).
2. **[`branch-sync-check.yaml`](.github/workflows/branch-sync-check.yaml)** *(Au push sur `jak[1-3]/**` / Dispatch)* : Vérification ultra-rapide d'ascendance garantissant qu'une branche de mod est à jour avec `master-dev`. Alimente le badge d'état GitHub Actions dans le `README.md` de chaque mod.
3. **[`release.yml`](.github/workflows/release.yml)** *(Déclenchement manuel `workflow_dispatch`)* : Compile des binaires Windows et Linux entièrement statiques depuis les sources propres, empaquette les assets, publie les releases GitHub, calcule les empreintes SHA256 et met à jour le catalogue `index.json` du Launcher OpenGOAL (voir le **[Guide de Distribution des Mods](docs/modding/tools/mod_distribution_guide.md)**).
4. **[`mod-bug-report-sync.yml`](.github/workflows/mod-bug-report-sync.yml)** *(À chaque Release)* : Synchronise la liste des mods publiés dans le formulaire de rapport de bug GitHub.
5. **[`mod-bug-triage.yml`](.github/workflows/mod-bug-triage.yml)** *(À l'ouverture/édition d'un ticket)* : Analyse les rapports de bugs des joueurs et applique automatiquement les labels de jeu et de mod (voir le **[Guide de Suivi des Bugs de Mods](docs/modding/tools/mod_bug_tracking.md)**).

> [!NOTE]
> **Stratégie de Documentation Sans Conflit :**
> Les documents de référence (`docs/modding/jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) possèdent une source de vérité unique : `master-dev`. Ils sont mis à jour directement via `task modding-land-doc` (en ajout seul), puis rapatriés dans les branches de mods avec `task modding-sync-docs`. Cette conception évite tout conflit de documentation entre branches développées en parallèle.

---

## 📊 Synchronisation des Branches de Mods

[![Sync Upstream](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml/badge.svg)](https://github.com/whozghiar/jak-project/actions/workflows/sync-upstream.yaml)

Ce badge indique l'état d'exécution du workflow de synchronisation quotidienne automatique (`sync-upstream.yaml`) exécuté chaque jour à 10:00 UTC :
- **Vert :** La dernière synchronisation (amont → `master` → `master-dev` → branches de mods) s'est déroulée avec succès et toutes les branches sans conflit ont été fusionnées automatiquement.
- **Rouge :** Un conflit ou un incident est survenu pendant le pipeline de synchronisation.

Le détail branche par branche avec les commandes prêtes à l'emploi pour résoudre les conflits est consigné sur `master-dev` dans :
- 📋 **Tableau de bord en direct :** [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md) *(réservé à master-dev, mis à jour à chaque synchro)*
- 📜 **Historique complet des fusions :** [`docs/modding/tools/branch_sync_history.md`](docs/modding/tools/branch_sync_history.md)

Chaque branche de mod dispose également de son propre badge d'état en direct dans son `README.md` racine, alimenté par [`branch-sync-check.yaml`](.github/workflows/branch-sync-check.yaml). Pour tous les détails d'architecture, consultez le **[Guide des Workflows GitHub Actions](docs/modding/tools/github_workflows.md)**.

---

## 📂 Vue d'ensemble des Répertoires

| Dossier / Fichier | Description |
| :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Directives unifiées pour agents IA et règles de modding (stratégie de branches, règles d'or, workflow REPL, référence des tâches). |
| [`.agents/skills/`](.agents/skills/) | Compétences modulaires développeurs et agents (GOAL Lisp, moteur interne, assets/acteurs 3D, modding de textures). |
| [`docs/modding/`](docs/modding/README.md) | Hub de documentation du modding (références Lisp vérifiées, guide d'initiation au moteur, workflows d'ingénierie, outils). |
| [`docs/modding/tools/github_workflows.md`](docs/modding/tools/github_workflows.md) | **Guide exhaustif des 5 workflows CI/CD GitHub Actions**, déclencheurs et synchronisation des branches. |
| [`docs/modding/tools/task_scripts_reference.md`](docs/modding/tools/task_scripts_reference.md) | **Référence pédagogique de toutes les commandes `task`** et des scripts Python d'automatisation. |
| [`docs/modding/tools/mod_bug_tracking.md`](docs/modding/tools/mod_bug_tracking.md) | Automatisation des rapports de bugs, synchronisation des releases et triage automatique des tickets. |
| [`docs/modding/tools/branch_sync_status.md`](docs/modding/tools/branch_sync_status.md) | Tableau de bord de fusionnabilité en direct de toutes les branches de mods (`task modding-branch-status`). |
| [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md) | Architecture unifiée du menu Mods en jeu (`mods-menu-register`, L3 + SELECT). |
| [`docs/modding/how_to_install_mod.md`](docs/modding/how_to_install_mod.md) | Guide pas à pas pour les joueurs expliquant comment installer un mod via le Launcher OpenGOAL. |
| [`docs/saves/`](docs/saves/README.md) | **Sauvegardes terminées à 100%** pour Jak 1, Jak 2 et Jak 3 (Jeu original et Mods). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | Référence Lisp OpenGOAL **vérifiée** par jeu — à consulter impérativement avant de coder. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Guide d'initiation au moteur partagé hors-Lisp (mémoire, heaps, DGOs, streaming de niveaux, cycle de vie des processus). |
| [`docs/modding/templates/`](docs/modding/templates/) | Modèles de documentation et de code ([`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc)). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Rapport de conformité généré par branche (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Automatisation Python (création de branche, synchronisation branche/doc, atterrissage de doc, audit de branche). |
| [`goal_src/`](goal_src/) | Code source GOAL décompilé et modifié par jeu (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | Compilateur OpenGOAL avec ajustements pour le modding. |
| [`game/`](game/) | Runtime C++ simulant la mémoire de l'Emotion Engine sur PC. |
| [`decompiler/`](decompiler/) | Outils d'extraction d'assets et de décompilation. |
| [`custom_assets/`](custom_assets/) | Remplacements de textures et modèles 3D personnalisés. |

---

## 🛠️ Référence des Commandes Task

> L'automatisation et les compilations s'appuient sur [Taskfile](https://taskfile.dev/). Passez les arguments de scripts après `--`.
> Pour un guide pédagogique complet détaillant quand et pourquoi employer chaque commande, consultez la **[Référence des Commandes Task & Scripts de Modding](docs/modding/tools/task_scripts_reference.md)**.

### Sélection du Jeu Actif
| Commande | Rôle |
| :--- | :--- |
| `task set-game-jak1` · `-jak2` · `-jak3` | Définit et mémorise le jeu actif ciblé (`jak1`, `jak2` ou `jak3`) |

### Compilation & CMake (Règle des 3 couches)
| Commande | Rôle |
| :--- | :--- |
| `task gen-cmake-release` | Configure CMake (Ninja + Clang) ; active automatiquement `sccache` s'il est présent |
| `task build-release` | Compile l'ensemble des ~20 binaires (première installation / audit complet) |
| `task build-release-game` | Compile **uniquement** `gk` + `goalc` — boucle rapide pour le C++ moteur/compilateur |
| `task build-release-decomp` | Compile **uniquement** le décompilateur — après modifs dans `decompiler/` |
| `task build-debug` / `-debug-game` / `-debug-decomp` | Équivalents en mode debug avec symboles complets |
| `task clean-cmake` | Nettoie les artefacts de build et le cache CMake |

### Extraction d'Assets & Décompilation
| Commande | Rôle |
| :--- | :--- |
| `task extract` | Extrait les assets originaux et exécute le décompilateur |
| `task decomp` / `decomp-file FILE=…` | Décompile tous les fichiers ou un fichier GOAL précis |
| `task rip-textures` / `rip-levels` / `rip-collision` / `rip-audio` | Extrait une catégorie d'assets spécifique |

### REPL Interactif & Exécution du Jeu
| Commande | Rôle |
| :--- | :--- |
| `task repl` → `(mi)` | Ouvre le REPL `goalc` ; `(mi)` injecte le code GOAL en direct en mémoire (**aucun build C++ requis**) |
| `task boot-game` | Démarre le jeu en mode debug sans REPL |
| `task boot-game-retail` | Démarre le jeu en mode retail (`-boot -fakeiso`) pour tester le menu Mods (L3 + SELECT) |
| `task run-game` | Lance le runtime, piloté et connecté au REPL |
| `task format` / `format-gsrc FILE=…` | Formate le code C++ et GOAL ou un fichier `.gc` spécifique |

### Scripts du Workflow de Modding
| Commande | Rôle |
| :--- | :--- |
| `task modding-new-branch -- jak2/features/x` | Crée une nouvelle branche de mod depuis `master-dev` avec le template `README.md` |
| `task modding-sync-branch` | Fusionne de manière sécurisée `master-dev` dans votre branche courante |
| `task modding-sync-docs` | Rapatrie `docs/modding`, `AGENTS.md` et `CLAUDE.md` depuis `master-dev` |
| `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "…" --push` | Intègre des découvertes Lisp sur `master-dev` sans conflit, puis resynchronise |
| `task modding-branch-status` | Actualise l'état de fusion de chaque branche de mod (`branch_sync_status.md`) |
| `task modding-audit` | Régénère le rapport d'audit de conformité (`docs/modding/branch_audit.md`) |

### Tests Automatisés
| Commande | Rôle |
| :--- | :--- |
| `task offline-tests` / `offline-tests-fast` | Exécute les tests de non-régression du décompilateur |
| `task unit-tests` / `tests-filtered FILTER=…` | Exécute la suite de tests unitaires du compilateur `goalc` |

---

*(AI-assisted)*
