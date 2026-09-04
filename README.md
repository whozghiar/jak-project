# 512 MB Main Memory Heap Expansion / Extension de la Mémoire Vive à 512 Mo

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Fconfig%2Fmemory_increase-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Expands the OpenGOAL global RAM heap from the original 128 MB to a massive 512 MB, enabling heavy custom geometry, dense traffic, and large asset packs without memory overflows.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/memory_increase`

## ✨ Key Features
- **Feature:** Quadrupled engine memory headroom (512 MB total).
- **Feature:** Eliminates out-of-memory crashes when spawning numerous vehicles or custom actors.
- **Feature:** Provides safe memory space for complex future mod additions.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. Memory layout constants are defined in C++ headers (`goal_constants.h` and `memory_layout.h`).
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** Not required. The memory expansion works out of the box with standard assets.
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
- 📄 [`docs/modding/jak2_modding_utilities/02_memory_architecture.md`](docs/modding/jak2_modding_utilities/02_memory_architecture.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Étend la mémoire vive allouée au moteur OpenGOAL de 128 Mo à 512 Mo, permettant d'accueillir des géométries lourdes, un trafic dense et des packs d'assets conséquents sans saturation mémoire.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/memory_increase`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Capacité mémoire quadruplée pour le moteur (512 Mo au total).
- **Fonctionnalité :** Élimine les plantages par manque de mémoire lors de l'apparition de nombreux véhicules ou acteurs custom.
- **Fonctionnalité :** Offre une marge de sécurité idéale pour les futurs ajouts de mods complexes.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. Les constantes d'allocation mémoire sont définies dans les en-têtes C++ (`goal_constants.h` et `memory_layout.h`).
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Non requise. L'extension mémoire s'applique directement avec les assets standards.
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
- 📄 [`docs/modding/jak2_modding_utilities/02_memory_architecture.md`](docs/modding/jak2_modding_utilities/02_memory_architecture.md)

---
*(AI-assisted)*
