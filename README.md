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
Haven City, at war, on demand.

Late in Jak 2 the city is overrun by Metal Heads and the Krimzon Guard stop caring about Jak
entirely — they have bigger problems. This mod lets you switch that state on whenever you like,
then pushes it much further: four Metal Head species that never set foot in the city join the
invasion, the guards get tougher, their gunships start shooting Metal Heads, and blast bots roll
out to hunt them.

Jak is a bystander. Nothing you do raises the alarm, and no guard will come after you.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/haven-city-chaos`

## ✨ Key Features
- **Metal Head invasion on demand:** the late-game war zone, available from any point in the story.
- **Seven Metal Head species instead of three.** The three the city already knows, rebalanced, plus
  four pulled in from elsewhere in the game:

  | Species | Share | Where it normally lives |
  |---|---:|---|
  | Grunt | 30% | Haven City invasion |
  | Stinger | 30% | Haven City invasion |
  | Cloaker | 10% | Haven City invasion |
  | Juice goon | 10% | Pumping Station |
  | Spyder gunner | 5% | Haven Forest / Pumping Station |
  | Centurion | 5% | Drill Platform / Mountain Temple |
  | Hopper | 5% | Mountain Temple |

- **The Krimzon Guard fight back harder:** red and yellow guards get 1.5× health, their gunships
  break off and engage Metal Heads, and a blast bot is occasionally dispatched that targets
  *only* Metal Heads.
- **A truce with Jak:** guards cannot see Jak at all. Nothing alerts them, nothing pursues him.
- **Off by default:** everything lives behind `Debug ▸ Mods ▸ haven-city-chaos`, with sub-toggles
  so you can dial any piece back on its own.

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
  that bakes the four new species' meshes and textures into `lwideb.fr3`. Skip this and they will
  walk around, fight and die — completely invisible.
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
- [ ] **Debug ▸ Mods toggle:** the mod registers at least one enable/disable entry via `(mods-menu-register "haven-city-chaos" ...)` (Jak 2) or a `haven-city-chaos`-prefixed debug submenu (Jak 1/3). See [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **No direct `default-menu*.gc` edits.**
- [ ] **Symbols prefixed** with the mod slug (`*mod-chaos-*`, `mod-chaos-*`).
- [ ] **Verified Lisp instructions** used by this mod are present in `docs/modding/jak[x]_lisp_instructions.md` (landed on `master-dev` via `task modding-land-doc`).
- [ ] **In-code comments** on every new/overridden type, method, state, macro.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/haven-city-chaos_readme.md`](docs/modding/current_mod/haven-city-chaos_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Haven City en guerre, à la demande.

En fin de Jak 2, la ville est envahie par les têtes de métal et les gardes cramoisis se
désintéressent complètement de Jak — ils ont d'autres soucis. Ce mod permet d'activer cet état
quand on veut, puis va beaucoup plus loin : quatre espèces de têtes de métal absentes de la ville
rejoignent l'invasion, les gardes deviennent plus coriaces, leurs véhicules ouvrent le feu sur les
têtes de métal, et des blast bots partent à la chasse.

Jak n'est qu'un spectateur. Rien de ce qu'il fait ne déclenche l'alerte, et aucun garde ne le
poursuit.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/haven-city-chaos`

## ✨ Fonctionnalités Clés
- **L'invasion à la demande :** la zone de guerre de fin de jeu, disponible à n'importe quel moment
  de l'histoire.
- **Sept espèces de têtes de métal au lieu de trois.** Les trois que la ville connaît déjà,
  rééquilibrées, plus quatre importées d'ailleurs dans le jeu :

  | Espèce | Part | Lieu d'origine |
  |---|---:|---|
  | Grunt | 30% | Invasion de Haven City |
  | Stinger | 30% | Invasion de Haven City |
  | Cloaker | 10% | Invasion de Haven City |
  | Juice goon | 10% | Station de pompage |
  | Spyder gunner | 5% | Forêt de Haven / Station de pompage |
  | Centurion | 5% | Plateforme de forage / Temple de la montagne |
  | Hopper | 5% | Temple de la montagne |

- **Des gardes cramoisis plus dangereux :** gardes rouges et jaunes à 1,5× de vie, véhicules de
  garde qui rompent leur patrouille pour engager les têtes de métal, et un blast bot déployé de
  temps à autre qui ne cible **que** les têtes de métal.
- **Une trêve avec Jak :** les gardes ne peuvent tout simplement plus le voir. Rien ne les alerte,
  rien ne le poursuit.
- **Désactivé par défaut :** tout se trouve dans `Debug ▸ Mods ▸ haven-city-chaos`, avec des
  sous-bascules pour ajuster chaque élément séparément.

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
  `extra_art_groups_by_dgo` qui cuit les maillages et textures des quatre nouvelles espèces dans
  `lwideb.fr3`. Sans cette étape, elles se déplacent, combattent et meurent — mais restent
  totalement invisibles.
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
- [ ] **Bascule Debug ▸ Mods :** le mod enregistre au moins une entrée activer/désactiver via `(mods-menu-register "haven-city-chaos" ...)` (Jak 2) ou un sous-menu debug préfixé `haven-city-chaos` (Jak 1/3). Voir [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [ ] **Aucune édition directe de `default-menu*.gc`.**
- [ ] **Symboles préfixés** par le slug du mod (`*mod-chaos-*`, `mod-chaos-*`).
- [ ] **Instructions Lisp vérifiées** utilisées par ce mod présentes dans `docs/modding/jak[x]_lisp_instructions.md` (intégrées sur `master-dev` via `task modding-land-doc`).
- [ ] **Commentaires dans le code** sur chaque type/méthode/état/macro ajouté ou surchargé.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/haven-city-chaos_readme.md`](docs/modding/current_mod/haven-city-chaos_readme.md)

---
*(AI-assisted)*
