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
- 📄 [`docs/modding/current_mod/mega_dark_jak_readme.md`](docs/modding/current_mod/mega_dark_jak_readme.md)

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
- 📄 [`docs/modding/current_mod/mega_dark_jak_readme.md`](docs/modding/current_mod/mega_dark_jak_readme.md)

---
*(AI-assisted)*
