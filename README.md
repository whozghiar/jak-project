# Jak 3 Jetboard Mechanics Port to Jak 2 / Portage du Jetboard de Jak 3 dans Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fjak3-jetBoard-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brings the refined, acrobatic Jetboard mechanics from Jak 3 into Jak 2, including enhanced tricks, improved grind physics, responsive jump curves, and custom audio cues.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/jak3-jetBoard`

## ✨ Key Features
- **Feature:** Jak 3 jump physics and air-trick combo system.
- **Feature:** Refined rail and edge grinding responsiveness.
- **Feature:** Custom sound effects and animation blending.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. The branch includes custom animation compilation and retargeting tools in `goalc/`.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required to process and package the ported board animations and sound banks into Jak 2 levels.
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
> 📁 [`docs/modding/current_mod/jak3_jetboard.mp4`](docs/modding/current_mod/jak3_jetboard.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Backports physics state handlers from `goal_src/jak3/engine/target/board/` into Jak 2's target board subsystem, linking custom art-groups.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Intègre la physique de Jetboard plus acrobatique et souple de Jak 3 dans Jak 2, avec de nouvelles figures, une physique de grind améliorée et une réactivité accrue.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/jak3-jetBoard`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Physique de saut et système de figures aériennes issus de Jak 3.
- **Fonctionnalité :** Accroche et glisse sur les rails optimisées.
- **Fonctionnalité :** Transitions d'animations et effets sonores adaptés.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. La branche intègre les outils de compilation et retargeting d'animations dans `goalc/`.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise pour traiter et empaqueter les animations du board et les banques sonores dans les niveaux.
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
> 📁 [`docs/modding/current_mod/jak3_jetboard.mp4`](docs/modding/current_mod/jak3_jetboard.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Rétro-porte les gestionnaires physiques de `goal_src/jak3/engine/target/board/` vers le sous-système board de Jak 2 en liant des art-groups custom.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

</details>

---
*(AI-assisted)*
