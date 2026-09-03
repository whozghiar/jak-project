# City & Wasteland Ambient Pedestrian Behaviors / Comportements Ambiants des Citadins et Gardes

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Ffeatures%2Fcity-behavior-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Enriches non-player character AI in Spargus and Haven City, introducing diverse ambient animations, improved reaction to nearby combat, and varied pathfinding routes.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/features/city-behavior`

## ✨ Key Features
- **Feature:** Civilians react dynamically to gunfights and Wasteland beast intrusions.
- **Feature:** Expanded ambient dialogue and idle animation variations.
- **Feature:** Smoother crowd pathfinding preventing NPC logjams in narrow alleys.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. Changes reside within GOAL AI scripts.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. Uses standard Jak 3 character and audio assets.
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
> 📁 [`docs/modding/current_mod/city_behavior.mp4`](docs/modding/current_mod/city_behavior.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Adjusts civilian state machines in `goal_src/jak3/levels/city/common/ctywide-init.gc` and nav-mesh behavior controllers.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/city-behavior_readme.md`](docs/modding/current_mod/city-behavior_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Enrichit l'intelligence artificielle des personnages non-joueurs à Spargus et Haven City, en introduisant de nouvelles animations d'ambiance, des réactions au combat et des trajets variés.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/features/city-behavior`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Les civils réagissent de manière plus vivante aux tirs et à l'intrusion de créatures.
- **Fonctionnalité :** Variété accrue des lignes de dialogue et des postures d'attente des PNJs.
- **Fonctionnalité :** Navigation de foule plus fluide évitant les blocages dans les ruelles étroites.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 3 :
```bash
task set-game-jak3
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. Les modifications se situent dans les scripts d'IA en GOAL.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. Utilise les assets et sons standards de Jak 3.
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
> 📁 [`docs/modding/current_mod/city_behavior.mp4`](docs/modding/current_mod/city_behavior.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Ajuste les machines à états des civils dans `goal_src/jak3/levels/city/common/ctywide-init.gc` et les contrôleurs nav-mesh.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/city-behavior_readme.md`](docs/modding/current_mod/city-behavior_readme.md)

</details>

---
*(AI-assisted)*
