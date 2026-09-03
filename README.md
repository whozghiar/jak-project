# Mega Dark Jak Overhaul / Transformation Mega Dark Jak Améliorée

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Ffeatures%2Fmega_dark_jak-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Overhauls Jak 3's Dark Jak into a devastating powerhouse, featuring increased melee reach, permanent empowered dark strikes, boosted mobility, and enhanced aura effects.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/features/mega_dark_jak`

## ✨ Key Features
- **Feature:** Enhanced damage multiplier and expanded hitboxes on all Dark Jak attacks.
- **Feature:** Dynamic dark energy shockwaves emitted during heavy ground slams.
- **Feature:** Extended transformation duration with optimized Dark Eco consumption.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. All gameplay changes are implemented in GOAL combat states.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. Uses standard Jak 3 Dark Jak animations and particle fx.
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
> 📁 [`docs/modding/current_mod/mega_dark_jak.mp4`](docs/modding/current_mod/mega_dark_jak.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Modifies Dark Jak behavior states in `goal_src/jak3/engine/target/target-darkjak.gc` including attack damage and collision sphere dimensions.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/mega_dark_jak_readme.md`](docs/modding/current_mod/mega_dark_jak_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Transforme le Dark Jak de Jak 3 en une véritable force destructrice, avec une allonge de frappe accrue, des attaques renforcées permanentes, une meilleure mobilité et une aura ténébreuse intensifiée.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/features/mega_dark_jak`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Multiplicateur de dégâts accru et zones d'impact élargies sur toutes les attaques.
- **Fonctionnalité :** Ondes de choc d'énergie noire lors des écrasements au sol.
- **Fonctionnalité :** Durée de transformation prolongée avec gestion optimisée de l'Éco Noire.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 3 :
```bash
task set-game-jak3
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. Les changements sont codés dans les états de combat en GOAL.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. Utilise les animations et particules natives de Dark Jak.
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
> 📁 [`docs/modding/current_mod/mega_dark_jak.mp4`](docs/modding/current_mod/mega_dark_jak.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Modifie les états de comportement dans `goal_src/jak3/engine/target/target-darkjak.gc`, notamment les tables de dégâts et les sphères de collision.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/mega_dark_jak_readme.md`](docs/modding/current_mod/mega_dark_jak_readme.md)

</details>

---
*(AI-assisted)*
