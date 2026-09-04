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
> *Demonstration videos are hosted on YouTube to avoid repository bloat.*  
> ▶️ Demonstration video coming soon on YouTube.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

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
> *Les vidéos de démonstration sont hébergées sur YouTube pour éviter d'alourdir le dépôt Git.*  
> ▶️ Démonstration vidéo prochainement disponible sur YouTube.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

---
*(AI-assisted)*
