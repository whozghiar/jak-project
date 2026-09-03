# Enhanced Spawn Rates & Nav-Mesh Limits / Taux de Spawn et Limites Nav-Mesh Renforcés

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Fconfig%2Fenhanced_spawnrates-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Increases civilian density, Crimson Guard patrol frequencies, and vehicle spawn volumes in Haven City while expanding navigation mesh quotas to prevent despawns.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/enhanced_spawnrates`

## ✨ Key Features
- **Feature:** Higher ambient traffic and pedestrian density across all Haven City zones.
- **Feature:** Elevated Crimson Guard alert spawns during combat and chases.
- **Feature:** Increased nav-mesh and pathfinding table buffers to prevent entity despawning.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** Not required. Changes are purely written in high-level GOAL engine scripts.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. The mod operates on standard Jak 2 game assets.
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
> 📁 [`docs/modding/current_mod/enhanced_spawnrates.mp4`](docs/modding/current_mod/enhanced_spawnrates.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
Adjusts spawn controllers in `goal_src/jak2/levels/city/common/` and expands navigation table constants in `traffic-h.gc`.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Augmente la densité des piétons, la fréquence des patrouilles de gardes et le volume des véhicules dans Haven City, tout en augmentant les quotas nav-mesh pour éviter les disparitions.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/enhanced_spawnrates`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Densité accrue de la circulation et des piétons dans l'ensemble des quartiers de Haven City.
- **Fonctionnalité :** Renforts de gardes plus nombreux et plus réactifs lors des phases d'alerte et de combat.
- **Fonctionnalité :** Augmentation des tampons de navigation pour préserver la persistance des entités actives.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Non requise. Les modifications sont entièrement contenues dans des scripts GOAL de haut niveau.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. Le mod fonctionne avec les assets standards de Jak 2.
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
> 📁 [`docs/modding/current_mod/enhanced_spawnrates.mp4`](docs/modding/current_mod/enhanced_spawnrates.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
Ajuste les contrôleurs de spawn dans `goal_src/jak2/levels/city/common/` et élève les constantes de table de navigation dans `traffic-h.gc`.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

</details>

---
*(AI-assisted)*
