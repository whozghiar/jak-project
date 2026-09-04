# Multiplayer — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fmultiplayer-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brief, simple description of what this mod introduces or modifies in the game.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/multiplayer`

## ✨ Key Features
- **Feature 1:** Simple description of the first key feature.
- **Feature 2:** Simple description of the second key feature.
- **Feature 3:** Simple description of the third key feature.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
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

[![Demonstration Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Watch the demonstration video on YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `YOUR_VIDEO_ID` with the YouTube video ID (e.g. `MnqnybexhSA`) and `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` with the video URL (e.g. `https://youtu.be/MnqnybexhSA`).*

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Description simple et accessible de ce que ce mod apporte ou modifie dans le jeu.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/multiplayer`

## ✨ Fonctionnalités Clés
- **Fonctionnalité 1 :** Description simple de la première fonctionnalité.
- **Fonctionnalité 2 :** Description simple de la deuxième fonctionnalité.
- **Fonctionnalité 3 :** Description simple de la troisième fonctionnalité.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
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

[![Vidéo de Démonstration](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Les vidéos de démonstration doivent être hébergées sur YouTube pour éviter d'alourdir le dépôt Git. Remplacez `YOUR_VIDEO_ID` par l'identifiant de la vidéo YouTube (ex : `MnqnybexhSA`) et `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` par l'URL de la vidéo (ex : `https://youtu.be/MnqnybexhSA`).*

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)

---
*(AI-assisted)*
