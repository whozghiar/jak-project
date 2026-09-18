# {MOD_TITLE} — {TARGET_GAME}

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-{GAME_BADGE}-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-{BRANCH_BADGE}-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">

{SYNC_BADGE}

</p>

> [!NOTE]
> 🇬🇧 The badge above is a native **GitHub Actions status badge** for
> [`branch-sync-check.yaml`](https://github.com/{REPO_PATH}/actions/workflows/branch-sync-check.yaml),
> scoped to this branch — GitHub renders it live from that workflow's own run history,
> nothing generates or rewrites this image by hand. It goes green the moment this branch
> next merges `master-dev` cleanly (usually via the daily automated sync), and can turn
> red if someone pushes commits here without syncing first. It cannot turn red purely
> because `master-dev` moved on without a new push landing here — for that live,
> all-branches view, see `master-dev`'s own
> [`docs/modding/tools/branch_sync_status.md`](https://github.com/{REPO_PATH}/blob/master-dev/docs/modding/tools/branch_sync_status.md)
> (intentionally master-dev-only, never carried onto a mod branch).
>
> 🇫🇷 Le badge ci-dessus est un **badge d'état natif GitHub Actions** pour
> [`branch-sync-check.yaml`](https://github.com/{REPO_PATH}/actions/workflows/branch-sync-check.yaml),
> propre à cette branche — GitHub le génère en direct depuis l'historique d'exécution de
> ce workflow, rien ne produit ou ne réécrit cette image à la main. Il passe au vert dès
> que cette branche fusionne `master-dev` proprement (généralement via la synchronisation
> quotidienne automatique), et peut passer au rouge si des commits sont poussés ici sans
> synchronisation préalable. Il ne peut pas passer au rouge simplement parce que
> `master-dev` a avancé sans qu'aucun push n'arrive ici — pour cette vue live toutes-
> branches, voir le fichier propre à `master-dev`
> [`docs/modding/tools/branch_sync_status.md`](https://github.com/{REPO_PATH}/blob/master-dev/docs/modding/tools/branch_sync_status.md)
> (volontairement réservé à `master-dev`, jamais présent sur une branche de mod).

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Brief, simple description of what this mod introduces or modifies in the game.

- **Target Game:** {TARGET_GAME}
- **Active Branch:** `{BRANCH_NAME}`

## ✨ Key Features
- **Feature 1:** Simple description of the first key feature.
- **Feature 2:** Simple description of the second key feature.
- **Feature 3:** Simple description of the third key feature.

## 📥 Download & Play via OpenGOAL Launcher (Players)

> [!TIP]
> **No developer environment required!** Players can install and play this mod directly using the official OpenGOAL Launcher:

### Option A — Add Custom Mod Source (Recommended)
1. In the **OpenGOAL Launcher**, navigate to **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Paste this catalog URL:
   ```text
   https://raw.githubusercontent.com/{REPO_PATH}/{BRANCH_NAME}/index.json
   ```
3. Go to the **Mods** tab, locate **{MOD_TITLE}**, and click **Install**.
4. Select your clean PS2 game ISO when prompted. The launcher will automatically extract assets and launch the game!

### Option B — Manual Installation from GitHub Releases
1. Download the pre-built package for your operating system from the [Releases](https://github.com/{REPO_PATH}/releases) tab (`windows-v*.zip` or `linux-v*.zip`).
2. Extract the archive into your OpenGOAL Launcher features directory:
   - **Windows:** `%APPDATA%\OpenGOAL-Launcher\features\{GAME_DIR}\mods\_local\{MOD_SLUG}\`
   - **Linux:** `~/.config/OpenGOAL-Launcher/features/{GAME_DIR}/mods/_local/{MOD_SLUG}/`
3. Launch the game from the OpenGOAL Launcher.

---

## 🛠️ Developer Setup & Local Compilation

If you want to modify or compile this mod locally from source:

### 1. Select the Active Game
Make sure your environment is targeting {TARGET_GAME}:
```bash
{TASK_SET_GAME}
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

[![Demonstration Video](https://img.youtube.com/vi/{YOUTUBE_ID}/maxresdefault.jpg)](https://youtu.be/{YOUTUBE_ID})

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/{YOUTUBE_ID})**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `{YOUTUBE_ID}` with your YouTube video ID (e.g. `MnqnybexhSA` from `https://youtu.be/MnqnybexhSA`).*

## ✅ Compliance Checklist
- [ ] **Native non-regression:** with the mod compiled but its toggle OFF, the game plays identically to stock.
- [ ] **In-game Mods toggle [MANDATORY FOR FEATURES]:** the mod registers at least one enable/disable entry via `(mods-menu-register "{MOD_SLUG}" ...)` (Jak 2 / Jak 3, opens with **L3 + SELECT**, works in a retail boot) or a `{MOD_SLUG}`-prefixed **debug-only** submenu (Jak 1). See [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md).
- [ ] **No direct `default-menu*.gc` edits.**
- [ ] **Symbols prefixed** with the mod slug (`*mod-{MOD_SLUG}-*`, `mod-{MOD_SLUG}-*`).
- [ ] **Verified Lisp instructions** used by this mod are present in `docs/modding/jak[x]_lisp_instructions.md` (landed on `master-dev` via `task modding-land-doc`).
- [ ] **In-code comments** on every new/overridden type, method, state, macro.
- [ ] **Mod cover thumbnail:** Optional cover image deposited at `docs/img/mod/mod_cover.png` for OpenGOAL Launcher display.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/{MOD_SLUG}_readme.md`](docs/modding/current_mod/{MOD_SLUG}_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Description simple et accessible de ce que ce mod apporte ou modifie dans le jeu.

- **Jeu Ciblé :** {TARGET_GAME}
- **Branche Active :** `{BRANCH_NAME}`

## ✨ Fonctionnalités Clés
- **Fonctionnalité 1 :** Description simple de la première fonctionnalité.
- **Fonctionnalité 2 :** Description simple de la deuxième fonctionnalité.
- **Fonctionnalité 3 :** Description simple de la troisième fonctionnalité.

## 📥 Téléchargement & Installation via OpenGOAL Launcher (Joueurs)

> [!TIP]
> **Aucun environnement de compilation requis !** Les joueurs peuvent installer et exécuter ce mod directement depuis l'OpenGOAL Launcher officiel :

### Option A — Ajouter une Source de Mod Personnalisée (Recommandé)
1. Dans l'**OpenGOAL Launcher**, rendez-vous dans **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Collez l'URL suivante pointant vers le catalogue du mod :
   ```text
   https://raw.githubusercontent.com/{REPO_PATH}/{BRANCH_NAME}/index.json
   ```
3. Allez dans l'onglet **Mods**, sélectionnez **{MOD_TITLE}** et cliquez sur **Install**.
4. Fournissez votre ISO PS2 propre lorsque demandé. Le launcher extrait les assets et installe le mod automatiquement !

### Option B — Installation Manuelle depuis les Releases GitHub
1. Téléchargez l'archive précompilée correspondant à votre OS dans l'onglet [Releases](https://github.com/{REPO_PATH}/releases) (`windows-v*.zip` ou `linux-v*.zip`).
2. Décompressez l'archive dans le répertoire des mods de votre OpenGOAL Launcher :
   - **Windows :** `%APPDATA%\OpenGOAL-Launcher\features\{GAME_DIR}\mods\_local\{MOD_SLUG}\`
   - **Linux :** `~/.config/OpenGOAL-Launcher/features/{GAME_DIR}/mods/_local/{MOD_SLUG}/`
3. Lancez le mod directement depuis l'OpenGOAL Launcher.

---

## 🛠️ Guide Développeur & Compilation Locale

Si vous souhaitez modifier le code ou compiler ce mod vous-même depuis les sources :

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible {TARGET_GAME} :
```bash
{TASK_SET_GAME}
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

[![Vidéo de Démonstration](https://img.youtube.com/vi/{YOUTUBE_ID}/maxresdefault.jpg)](https://youtu.be/{YOUTUBE_ID})

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/{YOUTUBE_ID})**

> [!NOTE]
> *Les vidéos de démonstration doivent être hébergées sur YouTube pour éviter d'alourdir le dépôt Git. Remplacez `{YOUTUBE_ID}` par l'identifiant de votre vidéo YouTube (ex : `MnqnybexhSA` pour `https://youtu.be/MnqnybexhSA`).*

## ✅ Checklist de Conformité
- [ ] **Non-régression native :** mod compilé mais bascule sur OFF → le jeu se joue à l'identique du jeu d'origine.
- [ ] **Bascule Mods en jeu [OBLIGATOIRE POUR LES FEATURES] :** le mod enregistre au moins une entrée activer/désactiver via `(mods-menu-register "{MOD_SLUG}" ...)` (Jak 2 / Jak 3, ouverture **L3 + SELECT**, fonctionne en boot retail) ou un sous-menu **debug-only** préfixé `{MOD_SLUG}` (Jak 1). Voir [`docs/modding/tools/mods_menu.md`](docs/modding/tools/mods_menu.md).
- [ ] **Aucune édition directe de `default-menu*.gc`.**
- [ ] **Symboles préfixés** par le slug du mod (`*mod-{MOD_SLUG}-*`, `mod-{MOD_SLUG}-*`).
- [ ] **Instructions Lisp vérifiées** utilisées par ce mod présentes dans `docs/modding/jak[x]_lisp_instructions.md` (intégrées sur `master-dev` via `task modding-land-doc`).
- [ ] **Commentaires dans le code** sur chaque type/méthode/état/macro ajouté ou surchargé.
- [ ] **Miniature de couverture du mod :** Image de couverture déposée dans `docs/img/mod/mod_cover.png` pour l'affichage dans l'OpenGOAL Launcher.

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/{MOD_SLUG}_readme.md`](docs/modding/current_mod/{MOD_SLUG}_readme.md)

---
*(AI-assisted)*
