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
* **Documentation for developers:** Guidelines are in place so that AI agents document their findings, memory structures, and changes in modular knowledge bases (`docs/modding/`). This ensures experienced developers can review, fix, or build upon the code if needed.
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
         │      ├── Mod source code + modular tips in docs/modding/
         │      └── Routine automated testing and merges
         │
         └── Live branch status and conflict tracking below
```

### Main Workflows:
1. [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml): Pulls daily updates from official OpenGOAL, fast-forwards `master`, updates `master-dev`, tests and auto-merges clean mod branches, and updates the status table.
2. [`.github/workflows/sync-modding-docs.yaml`](.github/workflows/sync-modding-docs.yaml): Collects modular tips from mod branches and updates the documentation base on `master-dev`.

---

## 📂 Directory Overview

| Directory | Description |
| :--- | :--- |
| [`docs/modding/`](docs/modding/) | Central modding documentation, instructions, templates, and branch tracking. |
| [`docs/modding/jak1_modding_utilities/`](docs/modding/jak1_modding_utilities/) | Modular engine knowledge base and tips for **Jak 1**. |
| [`docs/modding/jak2_modding_utilities/`](docs/modding/jak2_modding_utilities/) | Modular engine knowledge base and tips for **Jak 2** (physics, guard states, etc.). |
| [`docs/modding/jak3_modding_utilities/`](docs/modding/jak3_modding_utilities/) | Modular engine knowledge base and tips for **Jak 3** (traffic, armors, secrets). |
| [`docs/modding/templates/`](docs/modding/templates/) | Templates for mod documentation ([`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)). |
| [`scripts/modding/`](scripts/modding/) | Python automation scripts (branch sync, doc aggregation, branch creation). |
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
* **Documentation pour les développeurs :** Des consignes sont en place pour que les agents documentent leurs travaux, leurs recherches et leurs découvertes dans des bases de connaissances modulaires (`docs/modding/`). Cela permet à des développeurs de vérifier, reprendre ou adapter le code si besoin.
* **README dédié par mod :** Chaque branche de mod dispose à sa racine d'un fichier `README.md` décrivant : le guide d'installation, les fonctionnalités du mod, son utilisation et une vidéo démonstrative.
* **Contributions et retours :** Toute aide ou critique constructive sur ce dépôt est accueillie avec bienveillance, à la discrétion de la justesse des propos et des remarques.

---

## 🌿 Architecture Git & Workflows

Le dépôt sépare le code amont officiel et les branches de modding :
- **`master`** : Miroir direct d'OpenGOAL amont. Aucun commit custom n'y est fait directement.
- **`master-dev`** : Branche de base pour le modding, l'outillage et la documentation consolidée.
- **Branches de mods (`jak[N]/[type]/[nom]`)** : Dérivées de `master-dev`.

### Principaux Workflows :
1. [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml) : Rapatrie chaque jour les nouveautés officielles sur `master`, met à jour `master-dev`, teste et fusionne les branches de mods prêtes, et actualise le tableau ci-dessous.
2. [`.github/workflows/sync-modding-docs.yaml`](.github/workflows/sync-modding-docs.yaml) : Récolte les tips modulaires des branches de mods et met à jour la documentation globale sur `master-dev`.

---

## 📊 Tableau de Bord de Synchronisation des Branches / Branch Sync Dashboard

*L'historique complet des fusions et résolutions est consultable dans [`docs/modding/branch_sync_history.log`](docs/modding/branch_sync_history.log).*

<!-- BRANCH_STATUS_START -->
> **Dernière mise à jour :** `2026-09-03 19:27:24 UTC`  
> **Branche source :** `master` (`65fc564c1`)  
> **Statut global :** 16/16 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/custom_animation_and_sound` | ✅ À jour | `5f73301c4 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `dbce66e35 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/config/memory_increase` | ✅ À jour | `bd0db3ec6 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | ✅ À jour | `55422fbc8 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `7e14a749c - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/enhanced_city_traffic_v2` | ✅ À jour | `2c9314035 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `a11a7dfde - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/merc-fr3-injection-poc` | ✅ À jour | `0b9bd8c20 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/paddy_wagon_v2` | ✅ À jour | `9276ce340 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport_v2` | ✅ À jour | `e58aa288e - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/yakow_killable` | ✅ À jour | `3ddee3040 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak3/config/memory_increase` | ✅ À jour | `961da8980 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak3/features/city-behavior` | ✅ À jour | `6f3e5d196 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak3/features/jak2_skin_secret` | ✅ À jour | `f94160b37 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak3/features/mega_dark_jak` | ✅ À jour | `d79fc1c80 - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
| `jak3/features/redguard-entity` | ✅ À jour | `8e9115f1b - docs: establish official bilingual mod README (AI-assisted)` | Déjà à jour | — |
<!-- BRANCH_STATUS_END -->

---

## 🛠️ Commandes Utiles / Useful Commands

```bash
# Sélectionner le jeu actif / Set active game (jak1, jak2 or jak3)
task set-game-jak2

# Compiler les binaires release du moteur et du compilateur / Build release binaries
task build-release

# Lancer le jeu directement / Boot game
task boot-game

# Mettre à jour la doc sur une branche sans rebase / Sync docs on active branch
python scripts/modding/sync_docs_from_master.py

# Créer une nouvelle branche de mod / Create a new mod branch with auto-initialized README
python scripts/modding/create_mod_branch.py jak2/features/mon-nouveau-mod
```

*(AI-assisted)*
