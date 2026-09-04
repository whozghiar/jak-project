# Crimson Guard Infiltration in Jak 3 / Entités Crimson Guard Hostiles dans Jak 3

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Ffeatures%2Fredguard-entity-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brings the menacing Crimson Guards from Jak II into the harsh environments of Jak 3, introducing them as fully functional hostile enemy units with custom textures and combat AI.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/features/redguard-entity`

## ✨ Key Features
- **Feature:** Fully animated Crimson Guard enemies active in Jak 3 sectors.
- **Feature:** Custom high-resolution red armor textures and weapon shielding.
- **Feature:** Complete patrol, pursuit, and gunfight AI behavior states.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 3:
```bash
task set-game-jak3
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist
- **Details:** Only GOAL scripts are modified. No C++ rebuild needed. For first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
> [!NOTE]
> *Demonstration videos are hosted on YouTube to avoid repository bloat.*  
> ▶️ Demonstration video coming soon on YouTube.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Fait revivre les redoutables Crimson Guards de Jak II dans les environnements de Jak 3, sous forme d'unités ennemies hostiles complètes avec textures rouges personnalisées et IA de combat.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/features/redguard-entity`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Ennemis Crimson Guard pleinement animés et actifs dans les secteurs de Jak 3.
- **Fonctionnalité :** Textures haute résolution de l'armure rouge et du bouclier d'énergie.
- **Fonctionnalité :** IA de combat complète avec patrouille, traque et tirs de riposte.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 3 :
```bash
task set-game-jak3
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà
- **Détails :** Seuls les scripts GOAL sont modifiés, aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
> [!NOTE]
> *Les vidéos de démonstration sont hébergées sur YouTube pour éviter d'alourdir le dépôt Git.*  
> ▶️ Démonstration vidéo prochainement disponible sur YouTube.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/redguard-entity_readme.md`](docs/modding/current_mod/redguard-entity_readme.md)

---
*(AI-assisted)*
