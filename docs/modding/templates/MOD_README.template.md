# {MOD_TITLE} — {TARGET_GAME}

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-{GAME_BADGE}-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-{BRANCH_BADGE}-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brief, simple description of what this mod introduces or modifies in the game.

- **Target Game:** {TARGET_GAME}
- **Active Branch:** `{BRANCH_NAME}`

## ✨ Key Features
- **Feature 1:** Simple description of the first key feature.
- **Feature 2:** Simple description of the second key feature.
- **Feature 3:** Simple description of the third key feature.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting {TARGET_GAME}:
```bash
{TASK_SET_GAME}
```

### 2. Binary Compilation
- **Status:** [Required (`task build-release`) / Not required (standard binaries sufficient)]
- **Details:** [Specify if C++ engine or compiler files were modified]
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** [Required (`task extract`) / Standard extraction sufficient]
- **Details:** [Specify if custom 3D models, textures, or sound banks require extraction]
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
> 📁 `docs/modding/current_mod/{MOD_SLUG}.mp4`  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Technical summary of modified GOAL functions, state handlers, or C++ subsystems.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 `docs/modding/current_mod/{MOD_SLUG}_readme.md`

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Description simple et accessible de ce que ce mod apporte ou modifie dans le jeu.

- **Jeu Ciblé :** {TARGET_GAME}
- **Branche Active :** `{BRANCH_NAME}`

## ✨ Fonctionnalités Clés
- **Fonctionnalité 1 :** Description simple de la première fonctionnalité.
- **Fonctionnalité 2 :** Description simple de la deuxième fonctionnalité.
- **Fonctionnalité 3 :** Description simple de la troisième fonctionnalité.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible {TARGET_GAME} :
```bash
{TASK_SET_GAME}
```

### 2. Compilation des Binaires
- **Statut :** [Requise (`task build-release`) / Non requise (binaires standards suffisants)]
- **Détails :** [Précisez si le moteur ou le compilateur C++ a été modifié]
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** [Requise (`task extract`) / Extraction standard suffisante]
- **Détails :** [Précisez si des modèles 3D, textures ou sons personnalisés nécessitent une extraction]
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
> 📁 `docs/modding/current_mod/{MOD_SLUG}.mp4`  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Résumé technique des fonctions GOAL, machines à états ou sous-systèmes modifiés.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 `docs/modding/current_mod/{MOD_SLUG}_readme.md`

</details>

---
*(AI-assisted)*
