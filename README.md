# Haven City Chaos — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fhaven-city-chaos-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brief, simple description of what this mod introduces or modifies in the game.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/haven-city-chaos`

## ✨ Key Features
- **Feature 1:** Simple description of the first key feature.
- **Feature 2:** Simple description of the second key feature.
- **Feature 3:** Simple description of the third key feature.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** [Not required (GOAL-only mod, standard binaries sufficient) / `task build-release-game` (engine or compiler C++ changed) / `task build-release` + `task extract` (decompiler or decompiler/config changed)]
- **Details:** [Specify which C++ layer was modified — see `docs/modding/tools/build_and_iteration_workflow.md`]
```bash
# GOAL-only mod: nothing to build — go straight to the REPL below.
# Engine / compiler C++ changed:
task build-release-game
# Decompiler or decompiler/config changed (then step 3 is mandatory):
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** [Required (`task extract`) / Standard extraction sufficient]
- **Details:** [Specify if custom 3D models, textures, or sound banks require extraction]
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

[![Demonstration Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUR_VIDEO_ID)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/YOUR_VIDEO_ID)**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `YOUR_VIDEO_ID` with your YouTube video ID (e.g. `MnqnybexhSA` from `https://youtu.be/MnqnybexhSA`).*

## ✅ Compliance Checklist
- [ ] **Native non-regression:** with the mod compiled but its toggle OFF, the game plays identically to stock.
- [ ] **Debug ▸ Mods toggle:** the mod registers at least one enable/disable entry via `(mods-menu-register "haven_city_chaos" ...)` (Jak 2) or a `haven_city_chaos`-prefixed debug submenu (Jak 1/3). See [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **No direct `default-menu*.gc` edits.**
- [ ] **Symbols prefixed** with the mod slug (`*mod-haven_city_chaos-*`, `mod-haven_city_chaos-*`).
- [ ] **Verified Lisp instructions** used by this mod are present in `docs/modding/jak[x]_lisp_instructions.md` (landed on `master-dev` via `task modding-land-doc`).
- [ ] **In-code comments** on every new/overridden type, method, state, macro.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/haven_city_chaos_readme.md`](docs/modding/current_mod/haven_city_chaos_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Description simple et accessible de ce que ce mod apporte ou modifie dans le jeu.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/haven-city-chaos`

## ✨ Fonctionnalités Clés
- **Fonctionnalité 1 :** Description simple de la première fonctionnalité.
- **Fonctionnalité 2 :** Description simple de la deuxième fonctionnalité.
- **Fonctionnalité 3 :** Description simple de la troisième fonctionnalité.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** [Non requise (mod GOAL uniquement, binaires standards suffisants) / `task build-release-game` (C++ moteur ou compilateur modifié) / `task build-release` + `task extract` (décompilateur ou decompiler/config modifié)]
- **Détails :** [Précisez quelle couche C++ a été modifiée — voir `docs/modding/tools/build_and_iteration_workflow.md`]
```bash
# Mod GOAL uniquement : rien à compiler — passez directement au REPL ci-dessous.
# C++ moteur / compilateur modifié :
task build-release-game
# Décompilateur ou decompiler/config modifié (l'étape 3 devient obligatoire) :
task build-release-decomp
```

### 3. Extraction des Données (Assets)
- **Statut :** [Requise (`task extract`) / Extraction standard suffisante]
- **Détails :** [Précisez si des modèles 3D, textures ou sons personnalisés nécessitent une extraction]
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

[![Vidéo de Démonstration](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUR_VIDEO_ID)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/YOUR_VIDEO_ID)**

> [!NOTE]
> *Les vidéos de démonstration doivent être hébergées sur YouTube pour éviter d'alourdir le dépôt Git. Remplacez `YOUR_VIDEO_ID` par l'identifiant de votre vidéo YouTube (ex : `MnqnybexhSA` pour `https://youtu.be/MnqnybexhSA`).*

## ✅ Checklist de Conformité
- [ ] **Non-régression native :** mod compilé mais bascule sur OFF → le jeu se joue à l'identique du jeu d'origine.
- [ ] **Bascule Debug ▸ Mods :** le mod enregistre au moins une entrée activer/désactiver via `(mods-menu-register "haven_city_chaos" ...)` (Jak 2) ou un sous-menu debug préfixé `haven_city_chaos` (Jak 1/3). Voir [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **Aucune édition directe de `default-menu*.gc`.**
- [ ] **Symboles préfixés** par le slug du mod (`*mod-haven_city_chaos-*`, `mod-haven_city_chaos-*`).
- [ ] **Instructions Lisp vérifiées** utilisées par ce mod présentes dans `docs/modding/jak[x]_lisp_instructions.md` (intégrées sur `master-dev` via `task modding-land-doc`).
- [ ] **Commentaires dans le code** sur chaque type/méthode/état/macro ajouté ou surchargé.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/haven_city_chaos_readme.md`](docs/modding/current_mod/haven_city_chaos_readme.md)

---
*(AI-assisted)*
