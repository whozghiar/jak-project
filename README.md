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
Makes the peaceful Yakow farm animals killable and protected by Krimzon law. Striking a Yakow immediately triggers a Krimzon Guard alert ("Hands off the cow!"), while defeating it drops dark eco pills with authentic death VFX.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/yakow_killable`

## ✨ Key Features
- **Feature:** Yakows are now vulnerable and killable, taking damage from player attacks.
- **Feature:** Striking a Yakow instantly triggers Krimzon Guard Alert Level 1 ("Hands off the cow!").
- **Feature:** Purple dissolution death VFX and drops 6 Dark Eco pills upon defeat.

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
- **Status:** Standard extraction sufficient
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
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
[![Demonstration Video](https://img.youtube.com/vi/njKxjCuEpcU/maxresdefault.jpg)](https://youtu.be/njKxjCuEpcU)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/njKxjCuEpcU)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Rend les paisibles Yakows de la ferme vulnérables et éliminables sous la protection des Grenadiers. Frapper un Yakow déclenche immédiatement l'alerte des Grenadiers Krimzon (« Pas touche à la vache ! »), tandis que son élimination octroie des pilules d'éco sombre avec un effet visuel de mort authentique.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/yakow_killable`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Les Yakows sont désormais vulnérables et éliminables (gestion des points de vie et des impacts).
- **Fonctionnalité :** Frapper un Yakow déclenche instantanément l'alerte de niveau 1 des Grenadiers Krimzon (« Pas touche à la vache ! »).
- **Fonctionnalité :** Effet de mort par dissolution violette et apparition de 6 pilules d'éco sombre lors de l'élimination.

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
- **Statut :** Extraction standard suffisante
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
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
[![Vidéo de Démonstration](https://img.youtube.com/vi/njKxjCuEpcU/maxresdefault.jpg)](https://youtu.be/njKxjCuEpcU)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/njKxjCuEpcU)**


## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)

---
*(AI-assisted)*
