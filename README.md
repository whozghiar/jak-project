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

## 🌿 Git Architecture & Workflows

```text
[open-goal/jak-project] (upstream/master)
         │  (Daily automatic sync at 04:00 UTC)
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
         │      └── Routine automated testing and merges
         │
         └── Live branch status and conflict tracking below
```

### Main Workflow:
- [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml): Pulls daily updates from official OpenGOAL, fast-forwards `master`, updates `master-dev`, tests and auto-merges clean mod branches, and updates the status table.

> The old `sync-modding-docs.yaml` aggregation workflow has been **removed**. The two
> reference docs (`docs/modding/jak[x]_lisp_instructions.md`,
> `engine_generic_concepts.md`) have a single source of truth — `master-dev` — and
> are updated there directly via `task modding-land-doc` (append-only), then pulled
> into mod branches with `task modding-sync-docs`. This is what keeps parallel mod
> branches from ever conflicting on documentation.

---

## 📂 Directory Overview

| Directory / File | Description |
| :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Unified AI agent directives and modding rules (branching, golden rules, REPL workflow, task reference). |
| [`.agents/skills/`](.agents/skills/) | Modularized developer and agent skills (GOAL Lisp, engine internals, 3D assets/actors, texture modding). |
| [`docs/modding/`](docs/modding/README.md) | Modding documentation hub (verified Lisp references, engine primer, engineering workflows, tools). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | **Verified** OpenGOAL Lisp reference per game — consult before coding. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Shared non-Lisp engine primer (memory, heaps, DGOs, level streaming, process life cycle). |
| [`docs/modding/tools/`](docs/modding/tools/) | Tool & pipeline guides (build workflow, custom assets, [Mods menu](docs/modding/tools/mods_menu.md)). |
| [`docs/modding/templates/`](docs/modding/templates/) | [`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Generated per-branch compliance report (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Python automation (branch creation, branch/doc sync, doc landing, branch audit). |
| [`goal_src/`](goal_src/) | Decompiled and modified GOAL source code by game (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | OpenGOAL compiler with modding adjustments. |
| [`game/`](game/) | C++ runtime simulating the Emotion Engine memory on PC. |
| [`decompiler/`](decompiler/) | Asset extraction and decompiler tools. |
| [`custom_assets/`](custom_assets/) | Custom texture replacements and models. |

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

## 🌿 Architecture Git & Workflows

Le dépôt sépare le code amont officiel et les branches de modding :
- **`master`** : Miroir direct d'OpenGOAL amont. Aucun commit custom n'y est fait directement.
- **`master-dev`** : Branche de base pour le modding, l'outillage et la documentation consolidée.
- **Branches de mods (`jak[N]/[type]/[nom]`)** : Dérivées de `master-dev`.

### Workflow Principal :
- [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml) : Rapatrie chaque jour les nouveautés officielles sur `master`, met à jour `master-dev`, teste et fusionne les branches de mods prêtes, et actualise le tableau ci-dessous.

> L'ancien workflow d'agrégation `sync-modding-docs.yaml` a été **supprimé**. Les
> deux documents de référence (`docs/modding/jak[x]_lisp_instructions.md`,
> `engine_generic_concepts.md`) ont une seule source de vérité — `master-dev` — et
> sont mis à jour là directement via `task modding-land-doc` (en ajout seul), puis
> rapatriés dans les branches de mods avec `task modding-sync-docs`. C'est ce qui
> évite tout conflit de documentation entre branches de mods développées en
> parallèle.

---

## 📂 Vue d'ensemble des Répertoires

| Dossier / Fichier | Description |
| :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Directives unifiées pour agents IA et règles de modding (stratégie de branches, règles d'or, workflow REPL, référence des tâches). |
| [`.agents/skills/`](.agents/skills/) | Compétences modulaires développeurs et agents (GOAL Lisp, moteur interne, assets/acteurs 3D, modding de textures). |
| [`docs/modding/`](docs/modding/README.md) | Hub de documentation du modding (références Lisp vérifiées, guide d'initiation au moteur, workflows d'ingénierie, outils). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | Référence Lisp OpenGOAL **vérifiée** par jeu — à consulter impérativement avant de coder. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Guide d'initiation au moteur partagé hors-Lisp (mémoire, heaps, DGOs, streaming de niveaux, cycle de vie des processus). |
| [`docs/modding/tools/`](docs/modding/tools/) | Guides des outils et pipelines (workflow de build, assets custom, [menu Mods](docs/modding/tools/mods_menu.md)). |
| [`docs/modding/templates/`](docs/modding/templates/) | Modèles de documentation et de code ([`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_menu.template.gc`](docs/modding/templates/mod_menu.template.gc)). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Rapport de conformité généré par branche (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Automatisation Python (création de branche, synchronisation branche/doc, atterrissage de doc, audit de branche). |
| [`goal_src/`](goal_src/) | Code source GOAL décompilé et modifié par jeu (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | Compilateur OpenGOAL avec ajustements pour le modding. |
| [`game/`](game/) | Runtime C++ simulant la mémoire de l'Emotion Engine sur PC. |
| [`decompiler/`](decompiler/) | Outils d'extraction d'assets et de décompilation. |
| [`custom_assets/`](custom_assets/) | Remplacements de textures et modèles 3D personnalisés. |

---

## 📊 Tableau de Bord de Synchronisation des Branches / Branch Sync Dashboard

*L'historique complet des fusions et résolutions est consultable dans [`docs/modding/branch_sync_history.log`](docs/modding/branch_sync_history.log).*

<!-- BRANCH_STATUS_START -->
> **Dernière mise à jour :** `2026-09-17 00:54:55 UTC`  
> **Branche source :** `master-dev` (`651929c32`)  
> **Statut global :** 15/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🔄 Synchronisée | `f0902f6c2 - chore(sync): align jak2/config/enhanced_spawnrates with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `f31628e28 - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/blue-krimzon-guard` | 🔄 Synchronisée | `3b4253440 - chore(sync): align jak2/features/blue-krimzon-guard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `4f745d7e8 - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | 🔄 Synchronisée | `c240e0183 - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-rebellion` | 🔄 Synchronisée | `c336da9e1 - chore(sync): align jak2/features/haven-city-rebellion with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `d11ac1bfd - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/killable_yakow` | 🔄 Synchronisée | `a42342789 - chore(sync): align jak2/features/killable_yakow with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | 🔄 Synchronisée | `34259d183 - chore(sync): align jak2/features/paddywagon/traffic with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/peaceful-haven-city` | 🔄 Synchronisée | `fd46fc483 - chore(sync): align jak2/features/peaceful-haven-city with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/alert` | 🔄 Synchronisée | `4cae0cfd2 - chore(sync): align jak2/features/transport-ag/alert with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/traffic` | 🔄 Synchronisée | `4eb9d319d - chore(sync): align jak2/features/transport-ag/traffic with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `d720ddae6 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `0ab6b38fe - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `94815872c - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
<!-- BRANCH_STATUS_END -->

---

## 🛠️ Référence des commandes `task` / `task` Command Reference

> Builds & runtime use [Taskfile](https://taskfile.dev/). Pass script arguments after `--`.
> Les builds et l'exécution utilisent [Taskfile](https://taskfile.dev/). Passez les arguments après `--`.

### Jeu actif / Active game
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task set-game-jak1` · `-jak2` · `-jak3` | Persist the target game | Fixe le jeu ciblé |

### Build & CMake
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task gen-cmake-release` | Configure the build (Ninja + clang); auto-wires `sccache` if installed | Configure le build ; câble `sccache` s'il est installé |
| `task build-release` | Build **all** ~20 binaries (slow — first build / full check) | Build **complet** des ~20 binaires (lent) |
| `task build-release-game` | Build only `gk` + `goalc` — fast, for engine/compiler C++ iteration | Build `gk` + `goalc` uniquement — rapide, pour le C++ moteur/compilateur |
| `task build-release-decomp` | Build only the decompiler — after `decompiler/**` changes, then re-`extract` | Build le décompilateur seul — après modif `decompiler/**`, puis re-`extract` |
| `task build-debug` / `-debug-game` / `-debug-decomp` | Debug equivalents | Équivalents debug |
| `task clean-cmake` | Remove CMake artifacts | Supprime les artefacts CMake |

### Extraction & décompilation / Extraction & decompile
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task extract` | Extract assets + run the decompiler (re-run after any `decompiler/config` change) | Extrait les assets + lance le décompilateur |
| `task decomp` / `decomp-file FILE=…` | Decompile all / one object | Décompile tout / un objet |
| `task rip-textures` / `rip-levels` / `rip-collision` / `rip-audio` | Rip specific asset kinds | Extrait un type d'asset précis |

### REPL & exécution / REPL & run
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task repl` → `(mi)` | Open the compiler REPL; `(mi)` = incremental compile + hot reload (**no C++ build for `.gc` edits**) | Ouvre le REPL ; `(mi)` = compilation incrémentale + hot reload |
| `task boot-game` / `boot-game-retail` | Boot the game (debug / retail) without the REPL | Démarre le jeu (debug / retail) sans REPL |
| `task run-game` | Start the runtime, drive it from the REPL | Lance le runtime, piloté depuis le REPL |
| `task format` / `format-gsrc FILE=…` | Format C++ / one GOAL file | Formate le C++ / un fichier GOAL |

### Workflow de modding / Modding workflow
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task modding-new-branch -- jak2/features/x` | New mod branch from `master-dev` + initial README | Nouvelle branche de mod depuis `master-dev` + README initial |
| `task modding-sync-branch` | Safe `git merge` of `master-dev` into the current branch (`-- --rebase` / `-- --push`) | `git merge` sûr de `master-dev` dans la branche courante |
| `task modding-sync-docs` | Pull `docs/modding` + `AGENTS.md` + `CLAUDE.md` from `master-dev` (prunes deleted files) | Rapatrie la doc depuis `master-dev` (purge les fichiers supprimés) |
| `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "…" --push` | Land a doc addition on `master-dev` conflict-free, then re-sync your branch | Intègre un ajout de doc sur `master-dev` sans conflit, puis resync |
| `task modding-branch-status` | Test every mod branch's mergeability + refresh the dashboard (`-- --push` auto-merges) | Teste la fusionnabilité de chaque branche + actualise le tableau |
| `task modding-audit` | Regenerate `docs/modding/branch_audit.md` | Régénère `docs/modding/branch_audit.md` |

### Tests
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task offline-tests` / `offline-tests-fast` | Decompiler reference tests | Tests de référence du décompilateur |
| `task unit-tests` / `tests-filtered FILTER=…` | `goalc` unit tests | Tests unitaires `goalc` |

*(AI-assisted)*
