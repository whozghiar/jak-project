# Merc-Geometry .fr3 Injection Proof of Concept / Preuve de Concept d'Injection .fr3 Merc-Geometry

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fmerc-fr3-injection-poc-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Technical breakthrough enabling skeletal 3D models to be permanently resident across any level by baking their merc-geometry directly into `.fr3` level files offline, completely eliminating level borrowing.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/merc-fr3-injection-poc`

## ✨ Key Features
- **Feature:** Demonstrates universal actor visibility in all Haven City sectors.
- **Feature:** Bypasses PS2 level-borrowing memory limits.
- **Feature:** Validates resident drop-ship (`transport-ag`) geometry rendering anywhere.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (`task build-release`)
- **Details:** Required. Modifies offline decompiler asset baking tools.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required (`task extract`) to bake the injected merc models into the target level `.fr3` files.
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
- 📄 [`docs/modding/current_mod/merc_fr3_injection_poc_readme.md`](docs/modding/current_mod/merc_fr3_injection_poc_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Avancée technique permettant d'injecter des modèles 3D squelettiques dans n'importe quel niveau en intégrant leur géométrie merc directement dans les fichiers de niveau `.fr3` hors-ligne, sans emprunt de niveau.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/merc-fr3-injection-poc`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Prouve la possibilité d'afficher des acteurs universels dans tous les quartiers de Haven City.
- **Fonctionnalité :** Contourne les restrictions historiques d'emprunt de mémoire de la PS2.
- **Fonctionnalité :** Valide l'affichage permanent du vaisseau de transport (`transport-ag`) dans toute la ville.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (`task build-release`)
- **Détails :** Requise. Modifie les outils d'assemblage d'assets du décompilateur hors-ligne.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise (`task extract`) pour compiler et cuire les modèles injectés dans les fichiers `.fr3` des niveaux.
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
- 📄 [`docs/modding/current_mod/merc_fr3_injection_poc_readme.md`](docs/modding/current_mod/merc_fr3_injection_poc_readme.md)

---
*(AI-assisted)*
