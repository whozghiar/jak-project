# Custom Animation & Sound Import Tooling / Outils d'Import d'Animations et de Sons Custom

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Fconfig%2Fcustom_animation_and_sound-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Provides dedicated tooling and engine hooks to import custom skeletal 3D animations (from glTF) and custom sound banks (.sbk) directly into Jak 2.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/custom_animation_and_sound`

## ✨ Key Features
- **Feature:** Animation retargeting tool converting modern 3D formats into native OpenGOAL art-groups.
- **Feature:** Sound bank compiler utility packaging WAV samples into engine-compatible SBK banks.
- **Feature:** Seamless playback integration within existing Jak 2 character rigs.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. The mod introduces custom C++ build executables (`build_sbk` and `retarget_anim`) inside `goalc/`.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required if you are rebuilding custom sound banks or baking new animation data into levels.
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
> *Demonstration videos are hosted on YouTube to avoid repository bloat.*  
> ▶️ Demonstration video coming soon on YouTube.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/custom_animation_and_sound_readme.md`](docs/modding/current_mod/custom_animation_and_sound_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Fournit des outils dédiés et des passerelles moteur pour importer des animations 3D personnalisées (au format glTF) ainsi que des banques de sons personnalisées (.sbk) directement dans Jak 2.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/custom_animation_and_sound`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Outil de retargeting d'animations convertissant les formats 3D modernes en art-groups natifs OpenGOAL.
- **Fonctionnalité :** Utilitaire de compilation de banques sonores empaquetant les fichiers WAV en banques SBK compatibles.
- **Fonctionnalité :** Intégration transparente de la lecture d'animations sur les squelettes existants de Jak 2.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. Le mod introduit de nouveaux exécutables C++ (`build_sbk` et `retarget_anim`) dans `goalc/`.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise si vous compilez de nouvelles banques sonores ou intégrez de nouvelles animations aux niveaux.
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
> *Les vidéos de démonstration sont hébergées sur YouTube pour éviter d'alourdir le dépôt Git.*  
> ▶️ Démonstration vidéo prochainement disponible sur YouTube.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/custom_animation_and_sound_readme.md`](docs/modding/current_mod/custom_animation_and_sound_readme.md)

---
*(AI-assisted)*
