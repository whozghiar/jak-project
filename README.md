# Jak 3 Jetboard Mechanics Port to Jak 2 / Portage du Jetboard de Jak 3 dans Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fjak3-jetBoard-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Ports three signature Jetboard mechanics from Jak 3 directly into Jak 2: the Charge / Loaded Jump (`L1` + release `X`), the Circular Zap Attack (`Circle`), and the 180° Quick Turn-Around (`Triangle`) with an exit speed boost, complete with ported animations, particle VFX, and dedicated audio cues.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/jak3-jetBoard`

## ✨ Key Features
- **Feature:** **Loaded High Jump:** Hold `L1` (crouch on board) and release `X` to charge kinetic energy and launch Jak into high jumps with charge particles and audio.
- **Feature:** **Circular Zap Attack:** Press `Circle` to unleash a radial electrical sweep with invincibility frames and custom sound effects.
- **Feature:** **180° Quick Turn-Around:** Press `Triangle` to instantly snap 180 degrees and gain a forward speed boost upon exit.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. The branch includes custom animation compilation and retargeting tools in `goalc/`.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required to process and package the ported board animations and sound banks into Jak 2 levels.
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
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Porte trois mécaniques majeures du Jetboard de Jak 3 directement dans Jak 2 : le saut chargé (*Loaded Jump* avec `L1` + relâchement de `Croix`), le tacle circulaire électrique (*Board Zap* avec `Rond`) et le demi-tour instantané à 180° (*Quick Turn-Around* avec `Triangle`) suivi d'un boost d'accélération, avec animations réassignées, effets de particules et bruitages dédiés.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/jak3-jetBoard`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** **Saut Chargé (Loaded Jump) :** Maintenez `L1` pour vous accroupir sur le Jetboard et relâchez `Croix` pour charger l'énergie cinétique et sauter bien plus haut.
- **Fonctionnalité :** **Tacle Circulaire (Zap Attack) :** Appuyez sur `Rond` pour déclencher une décharge électrique radiale à 360° avec frames d'invincibilité et bruitages dédiés.
- **Fonctionnalité :** **Changement de Direction Rapide (180° Turn) :** Appuyez sur `Triangle` pour pivoter instantanément à 180° et repartir immédiatement avec un boost de vitesse.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. La branche intègre les outils de compilation et retargeting d'animations dans `goalc/`.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise pour traiter et empaqueter les animations du board et les banques sonores dans les niveaux.
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
[![Demonstration Video](https://img.youtube.com/vi/y-s5oj6Bimo/maxresdefault.jpg)](https://youtu.be/y-s5oj6Bimo)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/y-s5oj6Bimo)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/jak3-jetboard_readme.md`](docs/modding/current_mod/jak3-jetboard_readme.md)

---
*(AI-assisted)*
