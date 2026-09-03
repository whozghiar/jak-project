# Interactive & Vulnerable Yakows / Yakows Interactifs et Vulnérables

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fyakow_killable-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Makes the peaceful Yakow farm animals responsive to player actions and vulnerable to attacks, featuring custom hit reactions, death states, sound cues, and drops.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/yakow_killable`

## ✨ Key Features
- **Feature:** Yakows now react dynamically to kicks, punches, and weapon gunfire.
- **Feature:** Custom death animations and comical sound effects upon defeat.
- **Feature:** Health and Eco item drops upon defeat.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. GOAL scripts handle the health and combat state transitions.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required (`task extract`) to process the custom Yakow 3D GLB model and collision data.
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
> 📁 [`docs/modding/current_mod/yakow_killable.mp4`](docs/modding/current_mod/yakow_killable.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Implements `:event` handlers and `yakow-die` states in `goal_src/jak2/levels/city/farm/yakow.gc` using `custom_assets/` GLB meshes.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Rend les paisibles Yakows de la ferme réactifs aux actions de Jak et vulnérables aux coups, avec des réactions d'impact, un état de mort, des bruitages et du butin.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/yakow_killable`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Les Yakows réagissent désormais dynamiquement aux coups de pied, poings et tirs d'armes.
- **Fonctionnalité :** Animations de chute personnalisées et bruitages comiques lors de la défaite.
- **Fonctionnalité :** Apparition de packs de vie ou d'éco après élimination.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. Les scripts GOAL gèrent la vie et les transitions d'états de combat.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise (`task extract`) pour compiler le modèle 3D GLB et les collisions custom du Yakow.
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
> 📁 [`docs/modding/current_mod/yakow_killable.mp4`](docs/modding/current_mod/yakow_killable.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Implémente les gestionnaires d'événements et l'état `yakow-die` dans `goal_src/jak2/levels/city/farm/yakow.gc` en s'appuyant sur les maillages GLB de `custom_assets/`.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)

</details>

---
*(AI-assisted)*
