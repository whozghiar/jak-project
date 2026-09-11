# Crimson Guard Infiltration in Jak 3 / Entités Crimson Guard Hostiles dans Jak 3

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Ffeatures%2Fredguard-entity-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brings the menacing Crimson Guards from Jak II into the harsh environments of Jak 3, introducing them as fully functional hostile enemy units with custom textures and combat AI.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/features/redguard-entity`

## ✨ Key Features
- **Feature:** Fully animated Crimson Guard enemies active in Jak 3 sectors.
- **Feature:** Custom high-resolution red armor textures and weapon shielding.
- **Feature:** Complete patrol, pursuit, and gunfight AI behavior states.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist
- **Details:** Only GOAL scripts are modified. No C++ rebuild needed. For first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
> [!NOTE]
> *Demonstration videos are hosted on YouTube to avoid repository bloat.*  
> ▶️ Demonstration video coming soon on YouTube.

<<<<<<< HEAD
## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)
=======
| [`AGENTS.md`](AGENTS.md) | Unified AI agent directives and modding rules (branching, golden rules, REPL workflow, task reference). |
| [`.agents/skills/`](.agents/skills/) | Modularized developer and agent skills (GOAL Lisp, engine internals, 3D assets/actors, texture modding). |
| [`docs/modding/`](docs/modding/README.md) | Modding documentation hub (verified Lisp references, engine primer, engineering workflows, tools). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | **Verified** OpenGOAL Lisp reference per game — consult before coding. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Shared non-Lisp engine primer (memory, heaps, DGOs, level streaming, process life cycle). |
| [`docs/modding/tools/`](docs/modding/tools/) | Tool & pipeline guides (build workflow, custom assets, [Debug ▸ Mods menu](docs/modding/tools/mods_debug_menu.md)). |
| [`docs/modding/templates/`](docs/modding/templates/) | [`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_debug_menu.template.gc`](docs/modding/templates/mod_debug_menu.template.gc). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Generated per-branch compliance report (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Python automation (branch creation, branch/doc sync, doc landing, branch audit). |
| [`goal_src/`](goal_src/) | Decompiled and modified GOAL source code by game (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | OpenGOAL compiler with modding adjustments. |
| [`game/`](game/) | C++ runtime simulating the Emotion Engine memory on PC. |
| [`decompiler/`](decompiler/) | Asset extraction and decompiler tools. |
| [`custom_assets/`](custom_assets/) | Custom texture replacements and models. |
>>>>>>> origin/master-dev

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Fait revivre les redoutables Crimson Guards de Jak II dans les environnements de Jak 3, sous forme d'unités ennemies hostiles complètes avec textures rouges personnalisées et IA de combat.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/features/redguard-entity`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Ennemis Crimson Guard pleinement animés et actifs dans les secteurs de Jak 3.
- **Fonctionnalité :** Textures haute résolution de l'armure rouge et du bouclier d'énergie.
- **Fonctionnalité :** IA de combat complète avec patrouille, traque et tirs de riposte.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 3 :
```bash
task set-game-jak3
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà
- **Détails :** Seuls les scripts GOAL sont modifiés, aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
> [!NOTE]
> *Les vidéos de démonstration sont hébergées sur YouTube pour éviter d'alourdir le dépôt Git.*  
> ▶️ Démonstration vidéo prochainement disponible sur YouTube.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)

---
<<<<<<< HEAD
=======

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

## 📊 Tableau de Bord de Synchronisation des Branches / Branch Sync Dashboard

*L'historique complet des fusions et résolutions est consultable dans [`docs/modding/branch_sync_history.log`](docs/modding/branch_sync_history.log).*

<!-- BRANCH_STATUS_START -->
> **Dernière mise à jour :** `2026-09-11 13:39:20 UTC`  
> **Branche source :** `master-dev` (`e2f7032b7`)  
> **Statut global :** 0/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ⚠️ Erreur push | `2d2b11e3a - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/config/start_menu_wheel` | ⚠️ Erreur push | `50a05cef4 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/crimson-blueguard/city-insurrection` | ⚠️ Erreur push | `2d2dddaa5 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/crimson-blueguard/peaceful` | ⚠️ Erreur push | `104874cfd - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/dark_jak_enhanced` | ⚠️ Erreur push | `2001b0711 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/jak3-jetBoard` | ⚠️ Erreur push | `64a15539d - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/paddywagon/traffic` | ⚠️ Erreur push | `e04301b97 - feat(paddywagon): both traffic lanes + Jak keeps his gun while driving (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/transport-ag/alert` | ⚠️ Erreur push | `c6b130a3b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/transport-ag/traffic` | ⚠️ Erreur push | `4b3915712 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/yakow_killable` | ⚠️ Erreur push | `417e7a71b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/config/memory_increase` | ⚠️ Erreur push | `d60c2ebae - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/city-behavior` | ⚠️ Erreur push | `3842eaae6 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/jak2_skin_secret` | ⚠️ Erreur push | `be88206cf - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/mega_dark_jak` | ⚠️ Erreur push | `cd6220d59 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/redguard-entity` | ⚠️ Erreur push | `ae5334c70 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
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

>>>>>>> origin/master-dev
*(AI-assisted)*
