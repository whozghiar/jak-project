# Start Menu Wheel Fast Navigation / Navigation Rapide du Menu Circulaire — Jak 2

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
This quality-of-life (QoL) mod modernizes the in-game Start / Pause menu wheel navigation in Jak 2 to match the fluidity and responsiveness of Jak 3.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/start_menu_wheel`

## ✨ Key Features
- **Doubled Ring Rotation Speed:** In original Jak 2, menu ring rotation was capped at half the speed of Jak 3, locking new inputs until the animation finished. The seek speed is now doubled for instant response.
- **Hold-to-Repeat Navigation:** Holding down directional inputs (D-Pad / analog sticks) smoothly cycles through options with a 0.175s throttle window, removing the need to mash buttons.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist.
- **Details:** Only GOAL scripts are modified. No C++ rebuild needed. For a first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup).
- **Details:** Uses native in-game models, animations, and sound effects.
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
[![Demonstration Video](https://img.youtube.com/vi/RwAhDn31hU4/maxresdefault.jpg)](https://youtu.be/RwAhDn31hU4)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/RwAhDn31hU4)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/start_menu_wheel_readme.md`](docs/modding/current_mod/start_menu_wheel_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Ce mod de confort (QoL) modernise la navigation dans le menu circulaire Start / Pause de Jak 2 pour lui apporter la réactivité et la fluidité de Jak 3.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/start_menu_wheel`

## ✨ Fonctionnalités Clés
- **Vitesse de Rotation du Cercle Doublée :** Dans Jak 2 d'origine, la rotation du menu était deux fois plus lente que dans Jak 3 et bloquait les nouvelles entrées pendant l'animation. La vitesse est doublée pour un retour instantané.
- **Navigation « Maintenir pour Répéter » :** Maintenir une direction (croix directionnelle / stick analogique) fait défiler les options en continu avec un throttle de 0,175s, évitant d'avoir à marteler les boutons.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà.
- **Détails :** Seuls les scripts GOAL sont modifiés, aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation).
- **Détails :** Utilise les modèles, animations et bruitages natifs du jeu.
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
[![Vidéo de Démonstration](https://img.youtube.com/vi/RwAhDn31hU4/maxresdefault.jpg)](https://youtu.be/RwAhDn31hU4)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/RwAhDn31hU4)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/start_menu_wheel_readme.md`](docs/modding/current_mod/start_menu_wheel_readme.md)

---
*(AI-assisted)*
