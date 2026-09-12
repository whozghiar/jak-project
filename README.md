# Jetpack Crimsonguard — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fjetpack-crimsonguard-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Haven City gets an air force. This mod puts the game's existing jet-propelled Krimzon Guard —
the one you normally only meet at the Fortress, the Drill Platform and Haven Forest — into the
skies over the city, where it hunts Metal Heads instead of Jak.

It is built as the companion branch to **Haven City : Chaos**, but it works on its own: switch it
on, walk into the city, and guards start flying in.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/jetpack-crimsonguard`

## ✨ Key Features
- **Flying Krimzon Guards over Haven City:** up to three at a time, dispatched around the player,
  using the retail hover-guard model, animations and weapon.
- **They fight Metal Heads, not you:** they register as guards, they only ever target Metal Heads,
  and Metal Heads fight back.
- **Self-managing:** guards fly in on a timer, and are recycled once they drift too far from the
  player, so the population never runs away with your frame budget.
- **Off by default:** one toggle in `Debug ▸ Mods ▸ jetpack-crimsonguard`. With it off the city is
  bit-for-bit stock.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required — no C++ was modified. Standard binaries are enough.
- **Details:** The mod is GOAL source plus one `decompiler/config` entry, which is consumed by
  `task extract` (step 3), not by a C++ rebuild.
```bash
# GOAL-only mod: nothing to build — go straight to the REPL below.
# Engine / compiler C++ changed:
task build-release-game
# Decompiler or decompiler/config changed (then step 3 is mandatory):
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** **Required.** Run `task extract` once after checking out this branch.
- **Details:** `decompiler/config/jak2/jak2_config.jsonc` gains an `extra_art_groups_by_dgo` entry
  that bakes the hover guard's mesh and textures into `lwidea.fr3` / `lwideb.fr3` / `lwidec.fr3`.
  Skip this and the guards will run, make noise and shoot — but stay completely invisible.
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
- [ ] **Debug ▸ Mods toggle:** the mod registers at least one enable/disable entry via `(mods-menu-register "jetpack-crimsonguard" ...)` (Jak 2) or a `jetpack-crimsonguard`-prefixed debug submenu (Jak 1/3). See [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **No direct `default-menu*.gc` edits.**
- [ ] **Symbols prefixed** with the mod slug (`*mod-jetpack-*`, `mod-jetpack-*`).
- [ ] **Verified Lisp instructions** used by this mod are present in `docs/modding/jak[x]_lisp_instructions.md` (landed on `master-dev` via `task modding-land-doc`).
- [ ] **In-code comments** on every new/overridden type, method, state, macro.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/jetpack-crimsonguard_readme.md`](docs/modding/current_mod/jetpack-crimsonguard_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Haven City se dote d'une force aérienne. Ce mod fait voler au-dessus de la ville le garde cramoisi
à réacteur déjà présent dans le jeu — celui qu'on ne croise normalement qu'à la Forteresse, à la
plateforme de forage et dans la forêt de Haven — et le lance à la poursuite des têtes de métal
plutôt que de Jak.

C'est la branche compagnon de **Haven City : Chaos**, mais elle fonctionne seule : activez-la,
entrez en ville, et les gardes arrivent.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/jetpack-crimsonguard`

## ✨ Fonctionnalités Clés
- **Des gardes volants au-dessus de Haven City :** jusqu'à trois simultanément, déployés autour du
  joueur, avec le modèle, les animations et l'arme d'origine du garde à réacteur.
- **Ils combattent les têtes de métal, pas vous :** ils comptent comme des gardes, ne ciblent que
  les têtes de métal, et celles-ci ripostent.
- **Autogéré :** les gardes arrivent au fil du temps et sont recyclés dès qu'ils s'éloignent trop
  du joueur, pour que la population ne dérape jamais.
- **Désactivé par défaut :** une seule bascule dans `Debug ▸ Mods ▸ jetpack-crimsonguard`. Bascule
  sur OFF, la ville est strictement identique à l'originale.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise — aucun C++ modifié, les binaires standards suffisent.
- **Détails :** Le mod se compose de sources GOAL et d'une entrée `decompiler/config`, consommée
  par `task extract` (étape 3) et non par une recompilation C++.
```bash
# Mod GOAL uniquement : rien à compiler — passez directement au REPL ci-dessous.
# C++ moteur / compilateur modifié :
task build-release-game
# Décompilateur ou decompiler/config modifié (l'étape 3 devient obligatoire) :
task build-release-decomp
```

### 3. Extraction des Données (Assets)
- **Statut :** **Requise.** Lancez `task extract` une fois après avoir récupéré la branche.
- **Détails :** `decompiler/config/jak2/jak2_config.jsonc` reçoit une entrée
  `extra_art_groups_by_dgo` qui cuit le maillage et les textures du garde à réacteur dans
  `lwidea.fr3` / `lwideb.fr3` / `lwidec.fr3`. Sans cette étape les gardes existent, tirent et font
  du bruit — mais restent totalement invisibles.
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
- [ ] **Bascule Debug ▸ Mods :** le mod enregistre au moins une entrée activer/désactiver via `(mods-menu-register "jetpack-crimsonguard" ...)` (Jak 2) ou un sous-menu debug préfixé `jetpack-crimsonguard` (Jak 1/3). Voir [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **Aucune édition directe de `default-menu*.gc`.**
- [ ] **Symboles préfixés** par le slug du mod (`*mod-jetpack-*`, `mod-jetpack-*`).
- [ ] **Instructions Lisp vérifiées** utilisées par ce mod présentes dans `docs/modding/jak[x]_lisp_instructions.md` (intégrées sur `master-dev` via `task modding-land-doc`).
- [ ] **Commentaires dans le code** sur chaque type/méthode/état/macro ajouté ou surchargé.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/jetpack-crimsonguard_readme.md`](docs/modding/current_mod/jetpack-crimsonguard_readme.md)

---
*(AI-assisted)*
