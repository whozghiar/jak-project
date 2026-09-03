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
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. Uses existing OpenGOAL game runtime.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required (`task extract`) to compile the custom Blender 3D models and textures into Jak 3 level packages.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
> [!NOTE]
> **Video Demonstration:** Place or view the demonstration recording for this mod at:  
> 📁 [`docs/modding/current_mod/redguard_entity.mp4`](docs/modding/current_mod/redguard_entity.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Links custom `.glb` meshes from `custom_assets/blender/` into Jak 3 DGO manifests and registers guard entity state machines in GOAL.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)

</details>

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
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. S'exécute sur le runtime OpenGOAL standard.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise (`task extract`) pour compiler les modèles 3D Blender et les textures dans les packages de niveaux.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou via le REPL OpenGOAL avec `task repl`, puis `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
> [!NOTE]
> **Vidéo de démonstration :** L'enregistrement vidéo de démonstration de ce mod est prévu dans :  
> 📁 [`docs/modding/current_mod/redguard_entity.mp4`](docs/modding/current_mod/redguard_entity.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Lie les maillages `.glb` de `custom_assets/blender/` dans les manifests DGO de Jak 3 et enregistre les machines à états des gardes en GOAL.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)

</details>

---
*(AI-assisted)*
