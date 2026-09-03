<p align="center">
  <img width="500" height="100%" src="./docs/img/logo-text-colored-new.png" alt="OpenGOAL AI Modding Hub">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-AI--Assisted%20Modding-blue.svg" alt="OpenGOAL Modding">
  <img src="https://img.shields.io/badge/Branch-master--dev-orange.svg" alt="Branch">
  <img src="https://img.shields.io/badge/Trilogy-Jak%201%20%7C%20Jak%202%20%7C%20Jak%203-green.svg" alt="Jak Trilogy">
  <img src="https://img.shields.io/badge/Status-Active%20Research-purple.svg" alt="Status">
</p>

---

## 🎯 Démarche & Objectif du Projet

Ce dépôt est un **fork non officiel** du projet [OpenGOAL](https://github.com/open-goal/jak-project), sans affiliation directe avec l'équipe originelle d'OpenGOAL ou Naughty Dog. Pour la documentation technique et les instructions de compilation du projet OpenGOAL de base, consultez le [README originel d'OpenGOAL](open-goal-original-readme.md).

### Pourquoi ce fork ?
L'ambition de ce projet est de **mettre à profit les bénéfices et la puissance de l'Intelligence Artificielle** (agents de code, LLMs spécialisés) pour concevoir, implémenter et itérer rapidement sur des **mods avancés** pour la trilogie Jak (*Jak and Daxter: The Precursor Legacy*, *Jak II*, *Jak 3*).

### Libertés architecturales & Avertissement sur la fiabilité du code
* **Libertés sur le compilateur / décompilateur :** Certaines modifications chirurgicales ont été apportées directement au compilateur GOAL (`goalc`), au runtime C++ (`game`) et aux outils d'extraction d'assets (`decompiler`) pour contourner des restrictions natives ou étendre les capacités d'injection (ex: injection de géométrie `.fr3` offline, extension de heap RAM à 512 Mo, hook d'art-groups dynamiques).
* **Fiabilité du code généré par IA :** Le code produit par les agents d'assistance n'a pas la prétention d'être exempt de bugs ou certifié conforme aux standards industriels stricts. L'accent est mis sur l'atteinte concrète de l'objectif fonctionnel visé par le mod. Les commits correspondants portent systématiquement la mention `(AI-assisted)`.
* **Traçabilité & Reprise pour développeurs :** Un protocole rigoureux et un ensemble d'instructions (`AGENTS.md`, `CLAUDE.md`, `docs/modding/`) contraignent les agents à documenter minutieusement chacune de leurs découvertes, structures mémoire et expérimentations dans des bases de connaissances modulaires. Ainsi, tout développeur chevronné peut facilement auditer, fiabiliser ou prolonger le travail entamé.
* **Un README complet par mod :** Chaque branche de mod possède à sa racine son propre `README.md` détaillant le guide d'installation, les fonctionnalités précises, le guide d'utilisation et une vidéo démonstrative.
* **Bienveillance & Entraide :** Toute aide, contribution ou critique constructive sur ce dépôt est accueillie avec bienveillance, à la discrétion de la justesse technique des propos et des remarques.

---

## 🌿 Architecture Git & Workflows

Le dépôt s'articule autour d'une séparation stricte entre le code amont officiel et nos développements de modding :

```text
[open-goal/jak-project] (upstream/master)
         │  (Sync automatique quotidienne à 04:00 UTC)
         ▼
  [whozghiar/jak-project] (origin/master)      <── Miroir 100% propre d'OpenGOAL (aucun commit custom)
         │
         │  (Fast-forward / merge automatique)
         ▼
  [whozghiar/jak-project] (origin/master-dev)  <── Tronc commun de modding (Docs, outillage, base stable)
         │
         ├── Création d'une branche de mod : jak[N°]/[type]/[mod_name]
         │      │
         │      ├── Remplacement automatique de README.md par la fiche du mod
         │      ├── Code source du mod + tips modulaires dans docs/modding/
         │      └── Tests et fusions automatiques par routine
         │
         └── Surveillance & Détection de conflits en direct dans ce README ci-dessous
```

### Principaux Workflows GitHub Actions :
1. [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml) : 
   - Rapatrie chaque jour les évolutions officielles d'OpenGOAL sur `master`.
   - Propage les nouveautés dans `master-dev`.
   - Teste en mémoire (`git merge-tree`) et fusionne automatiquement les branches de mods sans conflits, tout en actualisant le tableau de bord ci-dessous.
2. [`.github/workflows/sync-modding-docs.yaml`](.github/workflows/sync-modding-docs.yaml) : 
   - Récolte tous les tips numérotés des branches `jak*/**` et régénère les fiches de connaissances modulaires sur `master-dev`.

---

## 📂 Organisation des Répertoires

| Répertoire | Description & Utilité |
| :--- | :--- |
| [`docs/modding/`](docs/modding/) | **Hub central de modding** : instructions, guides généraux, templates et suivi des branches. |
| [`docs/modding/jak1_modding_utilities/`](docs/modding/jak1_modding_utilities/) | Base de connaissances modulaire & tips techniques pour **Jak 1**. |
| [`docs/modding/jak2_modding_utilities/`](docs/modding/jak2_modding_utilities/) | Base de connaissances modulaire & tips techniques pour **Jak 2** (physique, jetboard, guard states, etc.). |
| [`docs/modding/jak3_modding_utilities/`](docs/modding/jak3_modding_utilities/) | Base de connaissances modulaire & tips techniques pour **Jak 3** (traffic, armures, light/dark Jak). |
| [`docs/modding/templates/`](docs/modding/templates/) | Modèles types de fiches de mod ([`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md)). |
| [`scripts/modding/`](scripts/modding/) | Scripts Python d'automatisation (synchronisation, récolte de doc, initialisation de branches). |
| [`goal_src/`](goal_src/) | Code source GOAL décompilé et fichiers spécifiques de modding par jeu (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | Compilateur GOAL x86-64 avec nos adaptations pour le modding. |
| [`game/`](game/) | Runtime / Kernel C++ émulant la mémoire de l'Emotion Engine sur PC. |
| [`decompiler/`](decompiler/) | Décompilateur et extracteur d'assets du jeu original. |
| [`custom_assets/`](custom_assets/) | Remplacement de textures PNG et modèles custom. |

---

## 📊 Tableau de Bord de Synchronisation des Branches

<!-- BRANCH_STATUS_START -->
> **Dernière mise à jour :** `2026-09-03 18:15:04 UTC`  
> **Branche source :** `master` (`65fc564c1`)  
> **Statut global :** 16/16 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/custom_animation_and_sound` | ✅ À jour | `200ef0e4c - fix(merge): resolve CMake conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `d8ad86f1e - chore: sync jak2/config/enhanced_spawnrates with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/memory_increase` | ✅ À jour | `1e7ce1531 - chore: sync jak2/config/memory_increase with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | ✅ À jour | `ba3ae4348 - chore: sync jak2/config/start_menu_wheel with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `6c4fbbef5 - chore: sync jak2/features/dark_jak_enhanced with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/enhanced_city_traffic_v2` | ✅ À jour | `1dcf66491 - chore: sync jak2/features/enhanced_city_traffic_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `5d71ff198 - fix(merge): resolve CMake conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/merc-fr3-injection-poc` | ✅ À jour | `5427bdebd - chore: sync jak2/features/merc-fr3-injection-poc with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/paddy_wagon_v2` | ✅ À jour | `fdeb0ecf4 - chore: sync jak2/features/paddy_wagon_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport_v2` | ✅ À jour | `a7ab8c19f - chore: sync jak2/features/transport_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/yakow_killable` | ✅ À jour | `07ed1641b - chore: sync jak2/features/yakow_killable with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/config/memory_increase` | ✅ À jour | `93c8570b5 - chore: sync jak3/config/memory_increase with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/city-behavior` | ✅ À jour | `d03da075b - chore: sync jak3/features/city-behavior with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/jak2_skin_secret` | ✅ À jour | `77323bced - fix(merge): resolve progress-draw-pc.gc conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/mega_dark_jak` | ✅ À jour | `c92710916 - chore: sync jak3/features/mega_dark_jak with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/redguard-entity` | ✅ À jour | `adb1e2741 - chore: sync jak3/features/redguard-entity with latest origin/master (AI-assisted)` | Déjà à jour | — |
<!-- BRANCH_STATUS_END -->

---

## 🛠️ Commandes Utiles de Modding

```bash
# Sélectionner le jeu actif (jak1, jak2 ou jak3)
task set-game-jak2

# Compiler les binaires release du moteur et du compilateur
task build-release

# Lancer le jeu directement
task boot-game

# Mettre à jour la documentation sur votre branche de mod active sans rebase
python scripts/modding/sync_docs_from_master.py

# Créer une nouvelle branche de mod avec initialisation automatique du README de mod
python scripts/modding/create_mod_branch.py jak2/features/mon-nouveau-mod
```

*(AI-assisted)*
