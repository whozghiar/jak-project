# Crimson Guard Alert Drop-Ship / Transport de Troupes d'Alerte

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Ftransport__alert-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
While Haven City is on **alert (level ≥ 1)**, a **Crimson Guard Troop Transport** (`transport-ag`, the retail drop-ship) descends near the player roughly **once per minute**, deploys a squad of Crimson Guards, and departs. It is a scripted reinforcement actor tied to the city alert system.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/transport_alert`

## ✨ Key Features
- **Feature:** Scripted troop drop-ship spawns 10–18 m from the player during city alerts (level ≥ 1).
- **Feature:** Realistic opening hatch sequence with sound effects and squad deployment of Crimson Guards.
- **Feature:** Strict 60-second cooldown ensuring at most one transport per minute.
- **Feature:** `.fr3` merc geometry injection into `lwidea/b/c.fr3` for seamless Haven City free-roam rendering.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (Layer 1 & Layer 2 — Decompiler & Runtime)
- **Details:** Compiles the runtime, compiler, and decompiler required for asset extraction:
```bash
task build-release-game
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** Custom extraction required (Layer 2)
- **Details:** Re-run extraction to process custom assets and modified decompiler configuration (`transport-ag` injected into `lwide*.fr3`):
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/transport_alert_readme.md`](docs/modding/current_mod/transport_alert_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Tant qu'Abriville est en **alerte (niveau ≥ 1)**, un **Transport de Troupes des Gardes Grenat** (`transport-ag`, le drop-ship du jeu d'origine) descend près du joueur environ **une fois par minute**, déploie une escouade de Gardes Grenat, puis repart. Il s'agit d'un renfort scripté directement relié à l'état d'alerte de la ville.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/transport_alert`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Apparition d'un drop-ship de troupes à 10–18 m du joueur en situation d'alerte (niveau ≥ 1).
- **Fonctionnalité :** Séquence animée d'ouverture de la porte arrière avec bruitages et largage au sol d'une escouade de gardes.
- **Fonctionnalité :** Cooldown strict de 60 secondes garantissant un maximum d'un drop-ship par minute.
- **Fonctionnalité :** Injection de géométrie merc `.fr3` dans `lwidea/b/c.fr3` pour un rendu natif en exploration libre d'Abriville.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (Couche 1 & Couche 2 — Décompilateur & Runtime)
- **Détails :** Compile le runtime, le compilateur et le décompilateur nécessaires à l'extraction des assets :
```bash
task build-release-game
task build-release-decomp
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction personnalisée requise (Couche 2)
- **Détails :** Relancez l'extraction pour intégrer les assets modifiés et la configuration du décompilateur (`transport-ag` injecté dans `lwide*.fr3`) :
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/transport_alert_readme.md`](docs/modding/current_mod/transport_alert_readme.md)

---
*(AI-assisted)*
