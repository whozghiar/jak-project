# Jak II Outfit Secret Unlock in Jak 3 / Déblocage de la Tenue Jak II dans les Secrets de Jak 3

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%203-red.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak3%2Ffeatures%2Fjak2_skin_secret-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Adds Jak's iconic Jak II outfit to the in-game Secrets Menu in Jak 3, allowing players to purchase and toggle his classic Haven City rebel appearance at any time.

- **Target Game:** Jak 3
- **Active Branch:** `jak3/features/jak2_skin_secret`

## ✨ Key Features
- **Feature:** Official integration into Jak 3's pause screen Secrets store.
- **Feature:** Equips Jak's full classic Jak II 3D mesh throughout gameplay and cutscenes.
- **Feature:** Preserves save-file compatibility and secret completion status.

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
- 📄 [`docs/modding/current_mod/jak2_skin_secret_readme.md`](docs/modding/current_mod/jak2_skin_secret_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Ajoute la tenue emblématique de Jak II dans le Menu des Secrets de Jak 3, permettant aux joueurs de débloquer et d'équiper son apparence classique de rebelle de Haven City à tout moment.

- **Jeu Ciblé :** Jak 3
- **Branche Active :** `jak3/features/jak2_skin_secret`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Intégration propre dans la boutique de Secrets du menu pause de Jak 3.
- **Fonctionnalité :** Permet d'arborer le modèle 3D classique de Jak II en jeu et dans les cinématiques.
- **Fonctionnalité :** Préserve la compatibilité des sauvegardes et le suivi des secrets débloqués.

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
- 📄 [`docs/modding/current_mod/jak2_skin_secret_readme.md`](docs/modding/current_mod/jak2_skin_secret_readme.md)

---
*(AI-assisted)*
