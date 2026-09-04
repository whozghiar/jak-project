# Jak 3 512 MB Main Memory Heap Expansion / Extension Mémoire Vive à 512 Mo pour Jak 3

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Fconfig%2Fmemory_increase-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Expands Jak 3's engine memory heap to 512 MB, allowing expansive custom levels, high vehicle counts in the Wasteland, and complex script modifications without crashing.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/config/memory_increase`

## ✨ Key Features
- **Feature:** 512 MB total RAM heap headroom for Jak 3.
- **Feature:** Eliminates memory exhaustion when exploring massive Wasteland areas with custom mods.
- **Feature:** Future-proof foundation for high-poly 3D models and large custom level chunks.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. C++ memory layout configurations (`common/goal_constants.h`) must be recompiled.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. Operates seamlessly with existing Jak 3 game assets.
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
- 📄 [`docs/modding/jak3_modding_utilities/02_memory_architecture.md`](docs/modding/jak3_modding_utilities/02_memory_architecture.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Étend la mémoire vive du moteur pour Jak 3 à 512 Mo, permettant de concevoir de grands niveaux custom, d'augmenter le nombre de véhicules dans les Terres Dévastées et d'éviter les crashs mémoire.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/config/memory_increase`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** 512 Mo de mémoire vive allouée pour Jak 3.
- **Fonctionnalité :** Élimine les plantages par saturation mémoire lors de l'exploration des Terres Dévastées avec des mods.
- **Fonctionnalité :** Base solide pour accueillir des modèles 3D détaillés et des portions de niveaux custom.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 3 :
```bash
task set-game-jak3
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. Les constantes de configuration de la mémoire en C++ (`common/goal_constants.h`) doivent être recompilées.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. Fonctionne immédiatement avec les assets existants de Jak 3.
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
- 📄 [`docs/modding/jak3_modding_utilities/02_memory_architecture.md`](docs/modding/jak3_modding_utilities/02_memory_architecture.md)

---
*(AI-assisted)*
