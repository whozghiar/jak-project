# Start Menu Radial Navigation Wheel / Menu Pause à Navigation Circulaire

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Fconfig%2Fstart_menu_wheel-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Implements an intuitive radial wheel navigation system inside the pause and options menu, allowing quick selection using directional inputs or analog sticks.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/start_menu_wheel`

## ✨ Key Features
- **Feature:** Modern radial selection interface for menus.
- **Feature:** Smooth analog and D-Pad responsiveness.
- **Feature:** Seamless compatibility with standard pause menu options.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. Implemented purely in GOAL UI scripts.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. Uses native interface fonts and textures.
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
- 📄 [`docs/modding/current_mod/start_menu_wheel_readme.md`](docs/modding/current_mod/start_menu_wheel_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Implémente un système de navigation circulaire intuitif dans le menu pause et options, permettant une sélection rapide à l'aide des sticks analogiques ou des touches directionnelles.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/start_menu_wheel`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Interface de sélection circulaire moderne pour les menus.
- **Fonctionnalité :** Réponse fluide au stick analogique et à la croix directionnelle.
- **Fonctionnalité :** Compatibilité totale avec toutes les options classiques du menu pause.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. Implémenté uniquement dans les scripts d'interface GOAL.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. Utilise les polices et textures d'interface natives.
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
- 📄 [`docs/modding/current_mod/start_menu_wheel_readme.md`](docs/modding/current_mod/start_menu_wheel_readme.md)

---
*(AI-assisted)*
