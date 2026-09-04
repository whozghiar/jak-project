# Dark Jak Enhanced Combat & Abilities / Dark Jak Amélioré & Nouveaux Combats

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fdark_jak_enhanced-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Reworks Dark Jak's moveset, introducing extended combo mechanics, increased attack reach, adjusted eco consumption, and responsive combat transitions.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/dark_jak_enhanced`

## ✨ Key Features
- **Feature:** Extended combo strings and punch-spin variations for Dark Jak.
- **Feature:** Rebalanced Dark Eco drain for longer, more satisfying combat phases.
- **Feature:** Dynamic damage scaling and enhanced impact particle effects.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
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
- 📄 [`docs/modding/current_mod/dark_jak_enhanced_readme.md`](docs/modding/current_mod/dark_jak_enhanced_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Revisite la palette de mouvements de Dark Jak en introduisant des enchaînements de combos prolongés, une allonge d'attaque accrue, un équilibrage de la consommation d'éco et des transitions fluides en combat.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/dark_jak_enhanced`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Combos prolongés et variations d'attaques tourniquet pour Dark Jak.
- **Fonctionnalité :** Consommation d'Éco Noire rééquilibrée pour des phases de combat plus intenses et gratifiantes.
- **Fonctionnalité :** Dégâts réajustés et renforcement visuel des impacts.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
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
- 📄 [`docs/modding/current_mod/dark_jak_enhanced_readme.md`](docs/modding/current_mod/dark_jak_enhanced_readme.md)

---
*(AI-assisted)*
