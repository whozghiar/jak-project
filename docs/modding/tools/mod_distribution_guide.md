# 🚀 OpenGOAL Mod Distribution & Release Guide
# Guide de Distribution & Release de Mods OpenGOAL

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 / Jak 2 / Jak 3 (OpenGOAL PC Port) — all mod branches
> - **Origin / Provenance :** `master-dev`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

This document explains the architecture and mechanics of the automated release and packaging pipeline that lets an OpenGOAL mod be installed and played directly by any player through the **official OpenGOAL Launcher**.

---

## 1. Why this pipeline handles C++ changes (`goalc`, `extractor`, `gk`)

Unlike conventional mods that only touch LISP script files (`goal_src/`), some mods in this repository alter the native C++ tools and engine:
- **Decompiler / Extractor (`decompiler/`):** Custom asset extraction, glTF/FR3 3D model injection, collision conversions.
- **Compiler (`goalc/`):** New behaviors, custom-actor compiler support, x86-64 assembly optimizations.
- **Game runtime (`gk`):** OpenGL graphics engine (shaders), EE/IOP simulation, audio hooks and extended memory.

### ⚙️ Execution mechanism in the OpenGOAL Launcher

When a player installs a mod from the Launcher:
1. The Launcher downloads the matching archive (`windows-v*.zip` or `linux-v*.zip`) and extracts it into its internal folder:
   ```text
   %APPDATA%/OpenGOAL-Launcher/features/<jak1|jak2|jak3>/mods/<source_name>/<mod_name>/
   ```
2. **Absolute priority to the mod's own executables:** The Launcher does **not** run the vanilla OpenGOAL build. It runs the binaries sitting directly at the root of the extracted mod folder:
   - `extractor` to decompress the player's clean ISO, decompile the needed assets, and run the local LISP compile with your `goalc`.
   - `gk` to launch the game natively.
3. **Fully static linking:** Thanks to the official CMake presets `Release-windows-clang-static` and `Release-linux-clang-static`, every C++ runtime and third-party library (`SDL3`, `zlib`, `lzokay`, `OpenSSL`) is merged into the binaries. The player needs no extra Visual C++ runtime or system library installed.

---

## 2. Mandatory Mod Archive Layout

For the Launcher to hit zero extraction or local-compile errors, the ZIP archive must contain exactly:

```text
├── extractor.exe (or extractor on Linux)
├── gk.exe        (or gk on Linux)
├── goalc.exe     (or goalc on Linux)
└── data/
    ├── launcher/
    │   └── error-code-metadata.json
    ├── decompiler/
    │   └── config/                       # Decompilation rules for NTSC/PAL ISOs
    ├── goal_src/                         # Full LISP source compiled by goalc
    ├── game/
    │   ├── assets/                       # Text, font and sound metadata
    │   └── graphics/
    │       └── opengl_renderer/
    │           └── shaders/              # OpenGL shaders required for gk to boot
    └── custom_assets/                    # Mod's 3D models, textures and assets (if any)
```

> [!CAUTION]
> **OpenGL Shaders Trap:** If `data/game/graphics/opengl_renderer/shaders/` is missing from the archive, the extractor and compiler will *look* like they work, but clicking "Play" will crash `gk` immediately on a GLSL compile error.

---

## 3. Triggering a Release from a Mod Branch

The `.github/workflows/release.yml` workflow lives on `master-dev` and is synced onto every mod branch.

> [!IMPORTANT]
> **`workflow_dispatch` only — no tag trigger.** This workflow does not listen for tag
> pushes (`git push origin v1.0.0` triggers **nothing**): it only ever runs manually,
> from the **Actions** tab or via `gh workflow run`. This is a deliberate choice — a
> release is an explicit action, never a side effect of a `git push`.
>
> **Always a full rebuild.** There is no more "fast packaging" mode: every release
> fully recompiles Windows and Linux from source. And the three fields `mod_name`,
> `mod_description`, `tag_name` are all **mandatory** — no more auto-detection or
> `auto` value: you decide the name, description and version number that ship to
> players.

### Triggering it — via GitHub Actions or the `gh` CLI

**Web UI:**
1. Open your repository on GitHub and go to the **Actions** tab.
2. In the left menu, select **🚀 Build & Release OpenGOAL Mod Package**.
3. Click **Run workflow**:
   - **Branch:** Pick your active mod branch (e.g. `jak2/features/my-mod`).
   - **Mod name (`mod_name`):** Mandatory. Display name (e.g. `Jak 3 JetBoard`).
   - **Short description (`mod_description`):** Mandatory. A 1-2 sentence summary embedded as-is into the `index.json` catalog.
   - **Version tag (`tag_name`):** Mandatory. An explicit tag (e.g. `v1.0.0`).
   - **Mark as pre-release:** Check if the version is experimental.
4. Click **Run workflow**.

**Command line:**
```bash
gh workflow run release.yml --ref jak2/features/my-mod \
  -f mod_name="Jak 3 JetBoard" \
  -f mod_description="Adds Jak 3's jetboard to Jak 2." \
  -f tag_name="v1.0.0"
```

---

## 4. OpenGOAL Launcher Integration (`index.json`)

The `scripts/modding/update_mod_catalog.py` script automatically generates an `index.json` file compliant with the official OpenGOAL Mod Source Schema v1:

```json
{
  "schemaVersion": "1.0.0",
  "sourceName": "Jak II - My Mod Source",
  "lastUpdated": "2026-09-13T15:00:00Z",
  "mods": {
    "my-mod": {
      "displayName": "Jak II - My Mod",
      "description": "Mod description...",
      "authors": ["MyHandle"],
      "tags": ["gameplay", "custom-engine"],
      "supportedGames": ["jak2"],
      "websiteUrl": "https://github.com/user/repo/tree/jak2/features/my-mod",
      "coverArtUrl": "https://raw.githubusercontent.com/user/repo/jak2/features/my-mod/docs/img/mod/mod_cover.png",
      "thumbnailArtUrl": "https://raw.githubusercontent.com/user/repo/jak2/features/my-mod/docs/img/mod/mod_cover.png",
      "versions": [
        {
          "version": "1.0.0",
          "publishedDate": "2026-09-13T15:00:00Z",
          "supportedGames": ["jak2"],
          "assets": {
            "windows": "https://github.com/user/repo/releases/download/v1.0.0/windows-v1.0.0.zip",
            "linux": "https://github.com/user/repo/releases/download/v1.0.0/linux-v1.0.0.zip"
          },
          "checksums": {
            "windows": "a1b2c3d4...",
            "linux": "e5f6g7h8..."
          }
        }
      ]
    }
  },
  "texturePacks": {}
}
```

### 🖼️ Mod Cover Thumbnail (`mod_cover.png`)

For each mod, you can manually drop a cover thumbnail at `docs/img/mod/mod_cover.png` on the mod's branch. It is automatically detected and injected into `index.json` (`coverArtUrl` and `thumbnailArtUrl`) for visual display in the OpenGOAL Launcher, as well as in GitHub release notes.

### 🎮 For players:
In the OpenGOAL Launcher:
1. Go to **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Enter the catalog's raw URL:
   ```text
   https://raw.githubusercontent.com/<user>/<repo>/<branch>/index.json
   ```
3. The mod immediately appears in the **Mods** tab with a 1-click install button!

> For a full screenshot-by-screenshot walkthrough (including in-game activation), see [`how_to_install_mod.md`](../how_to_install_mod.md).

---

# 🇫🇷 Version Française

Ce document détaille l'architecture et le fonctionnement du pipeline de release et d'empaquetage automatique permettant de distribuer un mod OpenGOAL pour qu'il soit directement installable et jouable par n'importe quel joueur via l'**OpenGOAL Launcher officiel**.

---

## 1. Pourquoi ce pipeline gère les modifications C++ (`goalc`, `extractor`, `gk`)

Contrairement aux mods conventionnels qui ne modifient que des fichiers de script LISP (`goal_src/`), certains mods de ce dépôt altèrent les outils et le moteur natifs en C++ :
- **Décompilateur / Extracteur (`decompiler/`) :** Extraction personnalisée d'assets, injection de modèles 3D glTF/FR3, conversions de collisions.
- **Compilateur (`goalc/`) :** Nouveaux comportements, compilateur d'acteurs custom, optimisations assembleur x86-64.
- **Runtime du jeu (`gk`) :** Moteur graphique OpenGL (shaders), simulation EE/IOP, hooks audio et mémoire étendue.

### ⚙️ Mécanisme d'exécution dans l'OpenGOAL Launcher

Quand un joueur installe un mod depuis le Launcher :
1. Le Launcher télécharge l'archive correspondante (`windows-v*.zip` ou `linux-v*.zip`) et l'extrait dans son dossier interne :
   ```text
   %APPDATA%/OpenGOAL-Launcher/features/<jak1|jak2|jak3>/mods/<nom_source>/<nom_mod>/
   ```
2. **Priorité absolue aux exécutables du mod :** Le Launcher n'exécute **pas** la version vanilla d'OpenGOAL. Il exécute les binaires situés directement à la racine du dossier du mod extrait :
   - `extractor` pour décompresser l'ISO propre du joueur, décompiler les assets nécessaires et lancer la compilation LISP locale avec votre `goalc`.
   - `gk` pour lancer le jeu nativement.
3. **Liaison statique totale :** Grâce aux presets CMake officiels `Release-windows-clang-static` et `Release-linux-clang-static`, tous les runtimes C++ et bibliothèques tierces (`SDL3`, `zlib`, `lzokay`, `OpenSSL`) sont fusionnés dans les binaires. Le joueur n'a besoin d'installer aucun runtime Visual C++ ou bibliothèque système supplémentaire.

---

## 2. Arborescence Obligatoire de l'Archive Mod

Pour que le Launcher ne rencontre aucune erreur d'extraction ou de compilation locale, l'archive ZIP contient très exactement :

```text
├── extractor.exe (ou extractor sur Linux)
├── gk.exe        (ou gk sur Linux)
├── goalc.exe     (ou goalc sur Linux)
└── data/
    ├── launcher/
    │   └── error-code-metadata.json
    ├── decompiler/
    │   └── config/                       # Règles de décompilation pour ISOs NTSC/PAL
    ├── goal_src/                         # Code source LISP complet compilé par goalc
    ├── game/
    │   ├── assets/                       # Métadonnées de textes, polices et sons
    │   └── graphics/
    │       └── opengl_renderer/
    │           └── shaders/              # Shaders OpenGL indispensables au démarrage de gk
    └── custom_assets/                    # Modèles 3D, textures et assets du mod (si présents)
```

> [!CAUTION]
> **Piège des Shaders OpenGL :** Si le dossier `data/game/graphics/opengl_renderer/shaders/` est absent de l'archive, l'extracteur et le compilateur sembleront fonctionner, mais lors du clic sur "Play", le moteur `gk` plantera immédiatement sur une erreur de compilation GLSL.

---

## 3. Déclencher une Release depuis une Branche de Mod

Le workflow `.github/workflows/release.yml` est disponible sur `master-dev` et synchronisé sur toutes les branches de mods.

> [!IMPORTANT]
> **`workflow_dispatch` uniquement — pas de déclenchement par tag.** Ce workflow n'écoute
> pas les pushs de tag (`git push origin v1.0.0` ne déclenche **rien**) : il se lance
> uniquement à la main, depuis l'onglet **Actions** ou via `gh workflow run`. C'est un
> choix délibéré — une release est une action explicite, jamais un effet de bord d'un
> `git push`.
>
> **Toujours un rebuild complet.** Il n'y a plus de mode « paquetage rapide » : chaque
> release recompile intégralement Windows et Linux depuis les sources. Et les trois
> champs `mod_name`, `mod_description`, `tag_name` sont **obligatoires** — il n'y a plus
> de détection ou de valeur `auto` : c'est vous qui décidez du nom, du descriptif et du
> numéro de version qui partent aux joueurs.

### Déclenchement — Via GitHub Actions ou la CLI `gh`

**Interface web :**
1. Ouvrez votre dépôt sur GitHub et rendez-vous dans l'onglet **Actions**.
2. Dans le menu de gauche, sélectionnez **🚀 Build & Release OpenGOAL Mod Package**.
3. Cliquez sur **Run workflow** :
   - **Branche :** Choisissez votre branche de mod active (ex: `jak2/features/my-mod`).
   - **Nom du mod (`mod_name`) :** Obligatoire. Nom d'affichage (ex: `Jak 3 JetBoard`).
   - **Descriptif court (`mod_description`) :** Obligatoire. Résumé (1 à 2 phrases) intégré tel quel dans le catalogue `index.json`.
   - **Tag de version (`tag_name`) :** Obligatoire. Un tag explicite (ex: `v1.0.0`).
   - **Marquer comme pré-release :** Cochez si la version est expérimentale.
4. Cliquez sur **Run workflow**.

**Ligne de commande :**
```bash
gh workflow run release.yml --ref jak2/features/my-mod \
  -f mod_name="Jak 3 JetBoard" \
  -f mod_description="Ajoute le jetboard de Jak 3 dans Jak 2." \
  -f tag_name="v1.0.0"
```

---

## 4. Intégration dans l'OpenGOAL Launcher (`index.json`)

Le script `scripts/modding/update_mod_catalog.py` génère automatiquement un fichier `index.json` conforme au schéma officiel OpenGOAL Mod Source Schema v1 :

```json
{
  "schemaVersion": "1.0.0",
  "sourceName": "Jak II - Mon Mod Source",
  "lastUpdated": "2026-09-13T15:00:00Z",
  "mods": {
    "my-mod": {
      "displayName": "Jak II - Mon Mod",
      "description": "Description du mod...",
      "authors": ["MonPseudo"],
      "tags": ["gameplay", "custom-engine"],
      "supportedGames": ["jak2"],
      "websiteUrl": "https://github.com/user/repo/tree/jak2/features/my-mod",
      "coverArtUrl": "https://raw.githubusercontent.com/user/repo/jak2/features/my-mod/docs/img/mod/mod_cover.png",
      "thumbnailArtUrl": "https://raw.githubusercontent.com/user/repo/jak2/features/my-mod/docs/img/mod/mod_cover.png",
      "versions": [
        {
          "version": "1.0.0",
          "publishedDate": "2026-09-13T15:00:00Z",
          "supportedGames": ["jak2"],
          "assets": {
            "windows": "https://github.com/user/repo/releases/download/v1.0.0/windows-v1.0.0.zip",
            "linux": "https://github.com/user/repo/releases/download/v1.0.0/linux-v1.0.0.zip"
          },
          "checksums": {
            "windows": "a1b2c3d4...",
            "linux": "e5f6g7h8..."
          }
        }
      ]
    }
  },
  "texturePacks": {}
}
```

### 🖼️ Miniature / Image de Couverture du Mod (`mod_cover.png`)

Pour chaque mod, vous pouvez déposer manuellement une miniature de couverture dans `docs/img/mod/mod_cover.png` sur la branche du mod. Elle est automatiquement détectée et injectée dans `index.json` (`coverArtUrl` et `thumbnailArtUrl`) pour l'affichage visuel dans le Launcher OpenGOAL, ainsi que dans les notes de release GitHub.

### 🎮 Pour les joueurs :
Dans l'OpenGOAL Launcher :
1. Allez dans **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Entrez l'URL brute du catalogue :
   ```text
   https://raw.githubusercontent.com/<utilisateur>/<dépôt>/<branche>/index.json
   ```
3. Le mod apparaît immédiatement dans l'onglet **Mods** avec bouton d'installation 1-clic !

> Pour un tutoriel complet illustré par captures d'écran (incluant l'activation en jeu), voir [`how_to_install_mod.md`](../how_to_install_mod.md).
