# 🛠️ Task Commands & Modding Scripts Reference / Référence des Commandes Task & Scripts de Modding

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 / Jak 2 / Jak 3 (OpenGOAL PC Port) — all mod branches
> - **Origin / Provenance :** `master-dev`
> - **Scope / Portée :** Taskfile Automation (`Taskfile.yml`), Build Targets & Modding Python Scripts (`scripts/modding/*.py`)

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Philosophy & Mental Model](#1-philosophy--mental-model) · [2. Game & Environment Configuration](#2-game--environment-configuration) · [3. C++ Build & Compilation Tasks](#3-c-build--compilation-tasks) · [4. Asset Baking & Game Execution](#4-asset-baking--game-execution) · [5. REPL & Live Code Iteration](#5-repl--live-code-iteration) · [6. Modding Automation Scripts (`scripts/modding/`)](#6-modding-automation-scripts-scriptsmodding) · [7. Common Developer Workflows](#7-common-developer-workflows)
> - 🇫🇷 **Français :** [1. Philosophie & Modèle Mental](#1-philosophie--modèle-mental) · [2. Configuration du Jeu & de l'Environnement](#2-configuration-du-jeu--de-lenvironnement) · [3. Tâches de Compilation C++](#3-tâches-de-compilation-c) · [4. Extraction des Données & Exécution du Jeu](#4-extraction-des-données--exécution-du-jeu) · [5. REPL & Itération de Code en Direct](#5-repl--itération-de-code-en-direct) · [6. Scripts d'Automatisation du Modding (`scripts/modding/`)](#6-scripts-dautomatisation-du-modding-scriptsmodding) · [7. Workflows Développeur Typiques](#7-workflows-développeur-typiques)

---

# 🇬🇧 English Version

## 1. Philosophy & Mental Model

In OpenGOAL, developer commands are unified under [Taskfile](https://taskfile.dev/) (`Taskfile.yml`). Instead of remembering long CMake flags, compiler paths, or Python scripts with complex arguments, `task <command>` provides cross-platform, deterministic shortcuts.

### Why use Task?
1. **Targeted Speed:** Never compile 20 binaries when you only need two (`gk` and `goalc`).
2. **Deterministic Environment:** Task manages environment variables (`.env`, active game selection) automatically.
3. **Reproducible CI/CD:** Modding Python scripts run identically locally and in automated GitHub Actions.

---

## 2. Game & Environment Configuration

| Command | When to use? | Why? | What it does under the hood |
| :--- | :--- | :--- | :--- |
| `task set-game-jak1` | When starting work on a Jak 1 mod. | Switches compiler target and asset search paths to Jak 1. | Runs `python ./scripts/tasks/update-env.py --game jak1`, updating `./scripts/tasks/.env`. |
| `task set-game-jak2` | When starting work on a Jak 2 mod. | Switches compiler target and asset search paths to Jak 2. | Updates `.env` to `GAME=jak2`. |
| `task set-game-jak3` | When starting work on a Jak 3 mod. | Switches compiler target and asset search paths to Jak 3. | Updates `.env` to `GAME=jak3`. |
| `task settings` | Whenever diagnosing configuration issues. | Displays the currently selected game, build dirs, and tool paths. | Runs `update-env.py --info`. |
| `task set-decomp-ntscv1` | When extracting assets from a Black Label NTSC ISO. | Sets the appropriate decompiler config for asset matching. | Updates `DECOMP_CONFIG` in `.env`. |
| `task set-decomp-pal` | When extracting from a European PAL ISO. | Sets PAL translation and asset mappings. | Updates `DECOMP_CONFIG` to PAL. |

---

## 3. C++ Build & Compilation Tasks

### Generator Configuration
- `task gen-cmake-release`:
  - **When?** Once after cloning the repo, after deleting `build/`, or after CMakeLists changes.
  - **Why?** Configures CMake with Clang and Ninja. Automatically detects and enables `sccache` compiler cache if installed on PATH, accelerating rebuilds by 10×.
- `task clean-cmake`:
  - **When?** When CMake cache corruption occurs or after major upstream refactors.
  - **Why?** Deletes `build/` and `out/build/` cleanly.

### Compilation Targets (The 3-Layer Rule)
- `task build-release-game`:
  - **When?** Fast iteration when modifying engine C++ (`game/`), OpenGL shaders, or the compiler (`goalc/`).
  - **Why?** Compiles ONLY `gk` and `goalc`. Skips ~18 unneeded binaries (decompiler, LSP, unit tests). Takes seconds instead of 10+ minutes.
- `task build-release-decomp`:
  - **When?** When changing asset extraction logic, glTF model injection (`extra_art_groups_by_dgo`), or collision parsers in `decompiler/`.
  - **Why?** Compiles ONLY the decompiler binary.
- `task build-release`:
  - **When?** First setup or when cutting a full release.
  - **Why?** Builds all ~20 executables across the repository.

---

## 4. Asset Baking & Game Execution

| Command | When to use? | Why? | What it does under the hood |
| :--- | :--- | :--- | :--- |
| `task extract` | After installing an ISO or changing decompiler config / injected assets. | Extracts 3D models, textures, animations, and level collision from `./iso_data` into `./decompiler_out`. | Runs `decompiler.exe` with `levels_extract: true`. |
| `task boot-game` | Cold launch testing of your mod. | Launches the game natively in debug mode (`-debug`), loading save slot 1. | Runs `gk.exe -v --game jak[x] -- -boot -fakeiso -debug`. |
| `task boot-game-retail` | Mandatory testing of in-game Mods menu (`mods-menu.gc`). | Reproduces retail boot (`-boot -fakeiso` without debug segment), proving the mod works for players. | Runs `gk.exe` without `-debug`. |
| `task run-game` | Launching runtime in listening mode for the REPL. | Keeps the game window waiting for REPL connection. | Runs `gk.exe -- -fakeiso -debug`. |

---

## 5. REPL & Live Code Iteration

- `task repl`:
  - **When?** During GOAL Lisp coding (`goal_src/**/*.gc`).
  - **Why?** Opens the interactive `goalc` compiler shell connected to the running game.
  - **Inside the REPL:**
    - `(mi)`: Incremental compile — re-reads modified `.gc` files and injects updated functions/states directly into game memory in milliseconds.
    - `(r)`: Restarts the active process or resets the level state.

---

## 6. Modding Automation Scripts (`scripts/modding/`)

These tasks wrap specialized Python automation scripts located in `scripts/modding/`. You can pass parameters to any script after `--` (e.g. `task modding-new-branch -- jak2/features/my-mod --youtube https://youtu.be/...`).

---

### 1. `task modding-new-branch -- jak[x]/[type]/[slug] [options]`
- **Script:** [`create_mod_branch.py`](../../../scripts/modding/create_mod_branch.py)
- **When?** Creating a new mod branch.
- **Why?** Branches cleanly from `master-dev`, auto-initializes the root `README.md` from the bilingual template, sets up the GitHub Actions sync badge, and verifies naming rules (`jak[1-3]/[features|config|chore]/[slug]`).
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `<branch_name>` | Positional *(required)* | Branch name conforming to `jak[1-3]/[type]/[slug]` (e.g. `jak2/features/my-mod`). |
  | `--youtube <url>` | String *(optional)* | YouTube demonstration video URL (e.g. `https://youtu.be/MnqnybexhSA`). Automatically extracts the video ID and embeds responsive video player markdown in `README.md`. |
  | `--no-commit` | Flag *(optional)* | Creates the branch and initializes the customized `README.md` without creating the initial git commit. |
  | `--push` | Flag *(optional)* | Pushes the newly created branch to `origin` immediately. |

*Example:*
```bash
task modding-new-branch -- jak2/features/traffic-overhaul --youtube https://youtu.be/MnqnybexhSA --push
```

---

### 2. `task modding-sync-branch -- [options]`
- **Script:** [`sync_branch_with_master_dev.py`](../../../scripts/modding/sync_branch_with_master_dev.py)
- **When?** Regularly during mod development on your mod branch.
- **Why?** Safely merges latest `origin/master-dev` into your current branch while strictly preserving your mod's root `README.md` and excluding `master-dev`-only files.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--branch <name>` | String (`current branch`) | Target branch to synchronize (defaults to currently checked-out branch). |
  | `--rebase` | Flag *(optional)* | Uses `git rebase` instead of `git merge` (rewrites local commit history; use only on unpushed local commits). |
  | `--push` | Flag *(optional)* | Automatically pushes the synchronized branch to `origin` if merge succeeds cleanly. |
  | `--source <branch>` | String (`master-dev`) | Source base branch to merge changes from. |

*Example:*
```bash
task modding-sync-branch -- --push
```

---

### 3. `task modding-sync-docs -- [options]`
- **Script:** [`sync_docs_from_master.py`](../../../scripts/modding/sync_docs_from_master.py)
- **When?** When you want latest modding documentation, verified Lisp instructions, or agent skills on your branch without merging game code.
- **Why?** Pulls `.agents`, `docs/modding`, `AGENTS.md`, and `CLAUDE.md` from `master-dev` without touching game source code.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--commit` | Flag *(optional)* | Automatically creates a git commit (`docs: sync modding docs and agent skills from master-dev`) with the pulled documentation. |
  | `--source <ref>` | String (`origin/master-dev`) | Source git ref or branch to pull documentation from. |
  | `--no-fetch` | Flag *(optional)* | Skips running `git fetch` before checking out docs. |
  | `--rebase` | Flag *(optional)* | Rebases the whole mod branch onto `origin/master-dev` instead of selective doc checkout. |

*Example:*
```bash
task modding-sync-docs -- --commit
```

---

### 4. `task modding-land-doc -- --file <path> --message "<msg>" [options]`
- **Script:** [`land_doc_on_master_dev.py`](../../../scripts/modding/land_doc_on_master_dev.py)
- **When?** When you discover and verify an undocumented Lisp instruction or engine fact while working on a mod.
- **Why?** Reference documents (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) have a single source of truth: `master-dev`. This script commits the update to `master-dev` and immediately syncs it back to your branch, preventing parallel branches from conflicting.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--file <path>` | String *(required, repeatable)* | Path to modified file under `docs/modding/` or `.agents/`. Can be repeated for multiple files. |
  | `--message "<msg>"` | String *(required)* | Commit message summary describing the verified discovery. |
  | `--push` | Flag *(optional)* | Pushes `master-dev` to `origin` and re-syncs back into your current branch automatically. |
  | `--source <branch>` | String (`master-dev`) | Canonical destination branch. |

*Example:*
```bash
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: add send-event syntax and stack trap" --push
```

---

### 5. `task modding-branch-status -- [options]`
- **Script:** [`sync_branches_with_master.py`](../../../scripts/modding/sync_branches_with_master.py)
- **When?** On `master-dev` to audit mergeability across all 15+ mod branches.
- **Why?** Tests `git merge` in memory for every mod branch. When called with `--push`, auto-merges all clean branches and regenerates the sync dashboard.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--push` | Flag *(optional)* | Automatically merges `master-dev` into all clean branches (zero conflicts) and pushes them to `origin`. |
  | `--output-only` | Flag *(optional)* | Evaluates branches and generates the status dashboard without performing any git merges. |
  | `--source <branch>` | String (`master-dev`) | Source base branch to test mergeability against. |

*Example:*
```bash
task modding-branch-status -- --push
```

---

### 6. `task modding-audit -- [options]`
- **Script:** [`branch_audit.py`](../../../scripts/modding/branch_audit.py)
- **When?** Before merging or releasing a mod.
- **Why?** Verifies project compliance: non-regression checks, absence of direct `default-menu*.gc` edits, presence of `mods-menu-register`, and valid bilingual README structure.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--local` | Flag *(optional)* | Audits local branch heads against local `master-dev` instead of remote `origin/` refs (useful before pushing synchronization commits). |
  | `--no-fetch` | Flag *(optional)* | Skips running `git fetch origin --prune`. |

*Example:*
```bash
task modding-audit -- --local
```

---

### 7. `task modding-sync-bug-report-options -- [options]`
- **Script:** [`sync_bug_report_options.py`](../../../scripts/modding/sync_bug_report_options.py)
- **When?** Automatically on release events, or manually with `--dry-run`.
- **Why?** Keeps the bug report form dropdown restricted to mods with real published releases.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--repo <owner/repo>` | String (`whozghiar/jak-project`) | Target GitHub repository to query for published releases. |
  | `--file <path>` | String (`.github/ISSUE_TEMPLATE/mod-bug-report.yml`) | Path to the bug report form template to regenerate. |
  | `--dry-run` | Flag *(optional)* | Preview the generated dropdown options in the terminal without modifying the file. |

*Example:*
```bash
task modding-sync-bug-report-options -- --dry-run
```

---

### 8. `task modding-sync-catalog -- [options]`
- **Script:** [`sync_global_catalog.py`](../../../scripts/modding/sync_global_catalog.py)
- **When?** On `master-dev` to refresh and rebuild the unified root `index.json` catalog containing all published mods and versions.
- **Why?** Queries GitHub Releases across the repository, parses attached mod assets and metadata, dedupes versions, normalizes branch slugs, and updates the consolidated Launcher v1 schema file.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--repo <owner/repo>` | String (`auto-detect`) | Target GitHub repository in `owner/repo` format. |
  | `--output <path>` | Path (`<repo_root>/index.json`) | Output path for the consolidated catalog file. |
  | `--offline` | Flag *(optional)* | Gathers releases strictly from local git release tags (`*-v*.*.*`) without calling GitHub REST API. |
  | `--source-name "<name>"` | String (`OpenGOAL Community Mods & Texture Packs`) | Catalog display title shown in the OpenGOAL Launcher UI. |
  | `--dry-run` | Flag *(optional)* | Analyzes releases and prints summary statistics to terminal without modifying `index.json`. |

*Example:*
```bash
task modding-sync-catalog -- --offline
```

---

### 9. Per-Branch Catalog Tools: `update_mod_catalog.py` & `apply_catalog_to_all_branches.py`
- **When?** During release creation or per-branch catalog restructuring.
- **Why?** Generates and maintains individual mod `index.json` catalogs.

---

### 10. `task modding-package-texture-pack` (Alias: `task modding-register-texture-pack`) `-- [options]`
- **Script:** [`package_texture_pack.py`](../../../scripts/modding/package_texture_pack.py)
- **When?** When registering a standalone texture pack into `index.json` after exporting it via the OpenGOAL Texture Pack Generator GUI (or when creating one via CLI with `--from-source`).
- **Why?** Recovers launcher-compliant `.zip` archives from `docs/modding/current_mod/texture_packs/` (generated by the GUI tool), inspects their internal `metadata.json`, computes SHA256 checksums, and automatically registers or updates the texture pack in `index.json` under `"texturePacks"`. Also supports building directly from raw PNG textures in `custom_assets/<game>/texture_replacements/` when run with `--from-source`.
- **CLI Parameters (`-- <args>`):**
  | Parameter | Type / Default | Description |
  | :--- | :--- | :--- |
  | `--dir <path>` | Path (`docs/modding/current_mod/texture_packs/`) | Directory to scan for `.zip` texture archives. |
  | `--zip <path>` | Path *(optional)* | Specific texture pack `.zip` file to register directly. |
  | `--no-index` | Flag *(optional)* | Inspects archive and computes SHA256 checksums without writing into `index.json`. |
  | `--release-url <url>` | String *(optional)* | Custom base URL where the texture pack `.zip` is hosted for downloads. |
  | `--game <id>` | Choice (`jak1|jak2|jak3|jakx`) | Target game identifier. |
  | `--from-source` | Flag *(optional)* | Compiles a new `.zip` archive directly from raw PNG files in `custom_assets/<game>/texture_replacements/`. |
  | `--slug <slug>` | String *(with `--from-source`)* | Unique identifier slug for the pack. |
  | `--display-name "<name>"` | String *(with `--from-source`)* | Human-readable display title in Launcher. |
  | `--description "<text>"` | String *(with `--from-source`)* | Detailed texture pack description. |
  | `--author "<name>"` | String *(with `--from-source`)* | Author or creator name. |
  | `--version <semver>` | String (`1.0.0`) | Semantic version string. |
  | `--tags <tag...>` | List *(with `--from-source`)* | Keywords/tags for filtering in Launcher. |
  | `--cover <path>` | Path *(with `--from-source`)* | Cover thumbnail image (`cover.png`). |
  | `--output <path>` | Path *(with `--from-source`)* | Destination `.zip` archive file path. |

*Example:*
```bash
# Register GUI-exported zip into index.json:
task modding-package-texture-pack

# Package directly from raw PNG assets:
task modding-package-texture-pack -- --from-source --game jak2 --slug blue-kg-textures --display-name "Blue KG Textures"
```

---

### 11. `task modding-texture-gui`
- **Script:** [`launch_texture_gui.py`](../../../scripts/modding/launch_texture_gui.py)
- **Tool Directory:** [`open-goal-texture-pack-generator`](open-goal-texture-pack-generator)
- **When?** When creating, previewing, and packaging custom texture replacements via a modern graphical desktop application.
- **Why?** Launches the dedicated high-performance desktop application ([`open-goal-texture-pack-generator`](open-goal-texture-pack-generator), powered by Tauri v2, Rust, and Svelte 5). It allows you to select texture files, customize author/version metadata, automatically apply descriptions to all textures in one click, preview image dimensions, and export `.zip` archives directly into `docs/modding/current_mod/texture_packs/`.
- **CLI Parameters (`-- <args>`):**
  - Requires no arguments. Runs the precompiled binary if found (`texture_pack_generator.exe`), automatically downloads the latest release from GitHub if missing on Windows, or falls back to `npm run tauri dev`.

*Example:*
```bash
task modding-texture-gui
```

---

## 7. Common Developer Workflows

### Scenario A: Fast LISP Gameplay Modding
1. `task set-game-jak2`
2. `task run-game` (in terminal 1)
3. `task repl` (in terminal 2)
4. Edit `.gc` files in `goal_src/jak2/`
5. In REPL: `(mi)` to hot reload instantly.

### Scenario B: Testing In-Game Mods Menu (Retail Boot)
1. Close REPL and game.
2. `task boot-game-retail`
3. Press **L3 + SELECT** on gamepad to ensure menu opens and toggle functions properly.

### Scenario C: Packaging & Distributing a Custom Texture Pack
1. Place or extract textures in `custom_assets/<game>/texture_replacements/`.
2. Launch the desktop GUI via `task modding-texture-gui`.
3. Select textures, set name, version, author, and description, then export the `.zip` archive into `docs/modding/current_mod/texture_packs/`.
4. Register the pack into `index.json`: `task modding-package-texture-pack`.
5. When publishing, upload the `.zip` archive as a GitHub Release asset (or trigger `release.yml` which automatically packages it).

### Scenario D: Synchronizing Your Mod Branch with Master-Dev
1. On your mod branch: `task modding-sync-branch`
2. If conflicts occur, inspect the reported files or run the recommended resolution command.
3. Test with cold boot: `task boot-game-retail`.

---

# 🇫🇷 Version Française

## 1. Philosophie & Modèle Mental

Dans OpenGOAL, les commandes de développement sont unifiées via [Taskfile](https://taskfile.dev/) (`Taskfile.yml`). Au lieu de mémoriser de longues options CMake, des chemins de compilateurs ou des scripts Python complexes, `task <commande>` offre des raccourcis multiplateformes et fiables.

### Pourquoi utiliser Task ?
1. **Vitesse Ciblée :** Ne recompilez jamais 20 exécutables lorsque vous n'en avez besoin que de deux (`gk` et `goalc`).
2. **Environnement Déterministe :** Task gère automatiquement les variables d'environnement (`.env`, jeu actif sélectionné).
3. **Reproductibilité CI/CD :** Les scripts de modding s'exécutent de façon strictement identique en local et dans GitHub Actions.

---

## 2. Configuration du Jeu & de l'Environnement

| Commande | Quand l'utiliser ? | Pourquoi ? | Ce qu'elle fait sous le capot |
| :--- | :--- | :--- | :--- |
| `task set-game-jak1` | Au démarrage d'un travail sur un mod Jak 1. | Bascule la cible du compilateur et les chemins d'assets sur Jak 1. | Exécute `python ./scripts/tasks/update-env.py --game jak1`, modifiant `./scripts/tasks/.env`. |
| `task set-game-jak2` | Au démarrage d'un travail sur un mod Jak 2. | Bascule la cible du compilateur et les chemins d'assets sur Jak 2. | Modifie `.env` vers `GAME=jak2`. |
| `task set-game-jak3` | Au démarrage d'un travail sur un mod Jak 3. | Bascule la cible du compilateur et les chemins d'assets sur Jak 3. | Modifie `.env` vers `GAME=jak3`. |
| `task settings` | Lors du diagnostic de l'environnement. | Affiche le jeu actif, les dossiers de build et les chemins d'outils. | Exécute `update-env.py --info`. |
| `task set-decomp-ntscv1` | Pour extraire les données d'une ISO NTSC Black Label. | Configure les règles de décompilation adaptées. | Met à jour `DECOMP_CONFIG` dans `.env`. |
| `task set-decomp-pal` | Pour extraire les données d'une ISO PAL européenne. | Configure les correspondances d'assets et langues PAL. | Met à jour `DECOMP_CONFIG` vers PAL. |

---

## 3. Tâches de Compilation C++

### Configuration du Générateur
- `task gen-cmake-release` :
  - **Quand ?** Après le premier clonage du dépôt, après suppression de `build/`, ou lors de changements dans `CMakeLists.txt`.
  - **Pourquoi ?** Configure CMake avec Clang et Ninja. Active automatiquement le cache de compilation `sccache` s'il est présent sur votre machine, accélérant les recompilations par 10.
- `task clean-cmake` :
  - **Quand ?** En cas de corruption du cache CMake ou après un gros rebase.
  - **Pourquoi ?** Supprime proprement `build/` et `out/build/`.

### Cibles de Compilation (La règle des 3 couches)
- `task build-release-game` :
  - **Quand ?** Itération rapide si vous modifiez le moteur C++ (`game/`), les shaders OpenGL ou le compilateur (`goalc/`).
  - **Pourquoi ?** Compile UNIQUEMENT `gk` et `goalc`. Ignore ~18 binaires superflus (décompilateur, LSP, tests unitaires). Prend quelques secondes au lieu de 10 à 20 minutes.
- `task build-release-decomp` :
  - **Quand ?** En cas de modification de l'extraction d'assets, de l'injection 3D glTF (`extra_art_groups_by_dgo`) ou de la collision dans `decompiler/`.
  - **Pourquoi ?** Compile UNIQUEMENT le décompilateur.
- `task build-release` :
  - **Quand ?** Configuration initiale ou préparation d'une release complète.
  - **Pourquoi ?** Construit la totalité des ~20 exécutables du projet.

---

## 4. Extraction des Données & Exécution du Jeu

| Commande | Quand l'utiliser ? | Pourquoi ? | Ce qu'elle fait sous le capot |
| :--- | :--- | :--- | :--- |
| `task extract` | Après avoir placé une ISO ou modifié des configurations d'assets injectés. | Extrait les modèles 3D, textures, animations et collisions de `./iso_data` vers `./decompiler_out`. | Lance `decompiler.exe` avec `levels_extract: true`. |
| `task boot-game` | Test de lancement à froid de votre mod. | Lance le jeu nativement en mode debug (`-debug`) en restaurant la sauvegarde 1. | Exécute `gk.exe -v --game jak[x] -- -boot -fakeiso -debug`. |
| `task boot-game-retail` | Test obligatoire du menu Mods en jeu (`mods-menu.gc`). | Reproduit fidèlement le boot du launcher officiel (`-boot -fakeiso` sans debug), prouvant la compatibilité joueur. | Exécute `gk.exe` sans l'argument `-debug`. |
| `task run-game` | Lancement du moteur en attente du REPL. | Maintient la fenêtre de jeu prête pour la connexion du REPL. | Exécute `gk.exe -- -fakeiso -debug`. |

---

## 5. REPL & Itération de Code en Direct

- `task repl` :
  - **Quand ?** Pendant le développement en GOAL Lisp (`goal_src/**/*.gc`).
  - **Pourquoi ?** Ouvre le shell interactif du compilateur `goalc` connecté au jeu en cours d'exécution.
  - **Dans le REPL :**
    - `(mi)` : Compilation incrémentale — analyse les fichiers `.gc` modifiés et réinjecte instantanément les fonctions/états dans la mémoire du jeu.
    - `(r)` : Réinitialise le processus actif ou relance le niveau.

---

## 6. Scripts d'Automatisation du Modding (`scripts/modding/`)

Ces tâches enveloppent les scripts Python du dossier `scripts/modding/`. Vous pouvez transmettre des arguments et options à n'importe quel script après `--` (ex. : `task modding-new-branch -- jak2/features/mon-mod --youtube https://youtu.be/...`).

---

### 1. `task modding-new-branch -- jak[x]/[type]/[slug] [options]`
- **Script :** [`create_mod_branch.py`](../../../scripts/modding/create_mod_branch.py)
- **Quand ?** Pour créer une nouvelle branche de mod.
- **Pourquoi ?** Branche proprement depuis `master-dev`, génère le `README.md` bilingue avec le badge GitHub et la checklist, et valide le nommage (`jak[1-3]/[features|config|chore]/[slug]`).
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `<nom_branche>` | Positionnel *(requis)* | Nom de branche respectant le format `jak[1-3]/[type]/[slug]` (ex. : `jak2/features/mon-mod`). |
  | `--youtube <url>` | Chaîne *(optionnel)* | URL de démonstration YouTube (ex. : `https://youtu.be/MnqnybexhSA`). Extrait automatiquement l'ID de la vidéo et insère le lecteur responsive dans le `README.md`. |
  | `--no-commit` | Booléen *(optionnel)* | Crée la branche et initialise le `README.md` sans créer le commit Git initial automatiquement. |
  | `--push` | Booléen *(optionnel)* | Pousse immédiatement la nouvelle branche vers le dépôt distant `origin`. |

*Exemple :*
```bash
task modding-new-branch -- jak2/features/traffic-overhaul --youtube https://youtu.be/MnqnybexhSA --push
```

---

### 2. `task modding-sync-branch -- [options]`
- **Script :** [`sync_branch_with_master_dev.py`](../../../scripts/modding/sync_branch_with_master_dev.py)
- **Quand ?** Régulièrement durant le développement d'un mod sur sa branche.
- **Pourquoi ?** Fusionne `origin/master-dev` en préservant le `README.md` spécifique au mod et en excluant les fichiers réservés à `master-dev`.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--branch <nom>` | Chaîne (`branche active`) | Branche cible à synchroniser (par défaut la branche Git couramment extraite). |
  | `--rebase` | Booléen *(optionnel)* | Utilise `git rebase` au lieu de `git merge` (réécrit l'historique local ; à réserver aux commits non encore publiés). |
  | `--push` | Booléen *(optionnel)* | Pousse automatiquement la branche vers `origin` si la fusion s'est terminée sans conflit. |
  | `--source <branche>` | Chaîne (`master-dev`) | Branche source de référence depuis laquelle fusionner les nouveautés. |

*Exemple :*
```bash
task modding-sync-branch -- --push
```

---

### 3. `task modding-sync-docs -- [options]`
- **Script :** [`sync_docs_from_master.py`](../../../scripts/modding/sync_docs_from_master.py)
- **Quand ?** Pour récupérer les dernières documentations, instructions Lisp ou compétences d'agents sans toucher au code source du jeu.
- **Pourquoi ?** Met à jour `.agents`, `docs/modding`, `AGENTS.md` et `CLAUDE.md` depuis `master-dev`.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--commit` | Booléen *(optionnel)* | Crée automatiquement un commit Git (`docs: sync modding docs and agent skills from master-dev`) avec les fichiers mis à jour. |
  | `--source <ref>` | Chaîne (`origin/master-dev`) | Référence ou branche Git source d'où extraire la documentation. |
  | `--no-fetch` | Booléen *(optionnel)* | Ignore l'étape `git fetch` préalable. |
  | `--rebase` | Booléen *(optionnel)* | Rebase l'ensemble de la branche sur `origin/master-dev` au lieu d'une extraction sélective de docs. |

*Exemple :*
```bash
task modding-sync-docs -- --commit
```

---

### 4. `task modding-land-doc -- --file <chemin> --message "<msg>" [options]`
- **Script :** [`land_doc_on_master_dev.py`](../../../scripts/modding/land_doc_on_master_dev.py)
- **Quand ?** Lorsque vous découvrez et vérifiez une nouvelle instruction Lisp ou un comportement moteur durant le modding.
- **Pourquoi ?** Les documents de référence (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) ont une source unique : `master-dev`. Ce script commite la découverte sur `master-dev` puis synchronise votre branche, évitant les conflits entre branches parallèles.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--file <chemin>` | Chaîne *(requis, répétable)* | Chemin du fichier modifié sous `docs/modding/` ou `.agents/`. Répétable pour plusieurs fichiers. |
  | `--message "<msg>"` | Chaîne *(requis)* | Message de commit Git résumant la découverte vérifiée. |
  | `--push` | Booléen *(optionnel)* | Pousse `master-dev` vers `origin` et re-synchronise automatiquement la branche courante. |
  | `--source <branche>` | Chaîne (`master-dev`) | Branche canonique cible. |

*Exemple :*
```bash
task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "jak2: syntaxe send-event et piège de pile" --push
```

---

### 5. `task modding-branch-status -- [options]`
- **Script :** [`sync_branches_with_master.py`](../../../scripts/modding/sync_branches_with_master.py)
- **Quand ?** Sur `master-dev` pour auditer l'état de fusion de toutes les branches du dépôt.
- **Pourquoi ?** Teste la fusion Git en mémoire pour chaque branche. Avec `--push`, fusionne automatiquement les branches saines et met à jour le tableau de bord.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--push` | Booléen *(optionnel)* | Fusionne automatiquement `master-dev` dans toutes les branches saines (zéro conflit) et les pousse vers `origin`. |
  | `--output-only` | Booléen *(optionnel)* | Évalue les branches et génère le tableau de bord sans exécuter de fusion Git. |
  | `--source <branche>` | Chaîne (`master-dev`) | Branche source de base avec laquelle tester l'intégrabilité. |

*Exemple :*
```bash
task modding-branch-status -- --push
```

---

### 6. `task modding-audit -- [options]`
- **Script :** [`branch_audit.py`](../../../scripts/modding/branch_audit.py)
- **Quand ?** Avant de fusionner ou publier un mod.
- **Pourquoi ?** Vérifie la conformité du projet : non-régression, absence d'édition directe de `default-menu*.gc`, présence de `mods-menu-register` et format bilingue du README.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--local` | Booléen *(optionnel)* | Audite les têtes locales des branches par rapport au `master-dev` local (utile avant de pousser les commits d'harmonisation). |
  | `--no-fetch` | Booléen *(optionnel)* | Ignore l'exécution de `git fetch origin --prune`. |

*Exemple :*
```bash
task modding-audit -- --local
```

---

### 7. `task modding-sync-bug-report-options -- [options]`
- **Script :** [`sync_bug_report_options.py`](../../../scripts/modding/sync_bug_report_options.py)
- **Quand ?** Automatiquement lors des releases, ou manuellement avec `--dry-run`.
- **Pourquoi ?** Restreint la liste des mods du formulaire de signalement de bugs aux seuls mods ayant une release officielle.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--repo <owner/repo>` | Chaîne (`whozghiar/jak-project`) | Dépôt GitHub cible pour répertorier les releases publiées. |
  | `--file <chemin>` | Chaîne (`.github/ISSUE_TEMPLATE/mod-bug-report.yml`) | Chemin du modèle de formulaire d'issue à régénérer. |
  | `--dry-run` | Booléen *(optionnel)* | Prévisualise dans la console les options générées sans modifier le fichier. |

*Exemple :*
```bash
task modding-sync-bug-report-options -- --dry-run
```

---

### 8. `task modding-sync-catalog -- [options]`
- **Script :** [`sync_global_catalog.py`](../../../scripts/modding/sync_global_catalog.py)
- **Quand ?** Sur `master-dev` pour actualiser et reconstruire le catalogue unifié `index.json` racine avec l'ensemble des mods et versions publiés.
- **Pourquoi ?** Interroge les releases GitHub du dépôt, analyse les archives et métadonnées associées, déduplique les versions, normalise les slugs et met à jour le fichier au schéma Launcher v1.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--repo <owner/repo>` | Chaîne (`auto-détecté`) | Dépôt GitHub cible au format `propriétaire/dépôt`. |
  | `--output <chemin>` | Chemin (`<racine>/index.json`) | Chemin de destination du catalogue consolidé. |
  | `--offline` | Booléen *(optionnel)* | Répertorie les versions strictement depuis les tags Git locaux (`*-v*.*.*`) sans appel à l'API GitHub. |
  | `--source-name "<nom>"` | Chaîne (`OpenGOAL Community Mods & Texture Packs`) | Titre affiché pour ce dépôt dans l'interface de l'OpenGOAL Launcher. |
  | `--dry-run` | Booléen *(optionnel)* | Analyse les releases et affiche les statistiques en console sans toucher à `index.json`. |

*Exemple :*
```bash
task modding-sync-catalog -- --offline
```

---

### 9. Outils de Catalogue par Branche : `update_mod_catalog.py` & `apply_catalog_to_all_branches.py`
- **Quand ?** Lors de la création d'une release ou réorganisation du catalogue propre à une branche.
- **Pourquoi ?** Génère et maintient le fichier `index.json` individuel consommé par l'OpenGOAL Launcher.

---

### 10. `task modding-package-texture-pack` (Alias : `task modding-register-texture-pack`) `-- [options]`
- **Script :** [`package_texture_pack.py`](../../../scripts/modding/package_texture_pack.py)
- **Quand ?** Lors de l'enregistrement d'un pack de textures dans `index.json` après l'avoir exporté avec l'OpenGOAL Texture Pack Generator GUI (ou lors de la création directe en CLI via `--from-source`).
- **Pourquoi ?** Récupère les archives `.zip` conformes au Launcher présentes dans `docs/modding/current_mod/texture_packs/` (générées par l'utilitaire GUI), analyse leur fichier `metadata.json` interne, calcule les empreintes SHA256 et inscrit automatiquement le pack dans le catalogue `index.json` sous `"texturePacks"`. Supporte également la compilation directe depuis les PNG bruts de `custom_assets/<game>/texture_replacements/` avec l'option `--from-source`.
- **Paramètres CLI (`-- <args>`) :**
  | Paramètre | Type / Défaut | Description |
  | :--- | :--- | :--- |
  | `--dir <chemin>` | Chemin (`docs/modding/current_mod/texture_packs/`) | Dossier à analyser pour trouver les archives `.zip`. |
  | `--zip <chemin>` | Chemin *(optionnel)* | Archive `.zip` spécifique à enregistrer directement. |
  | `--no-index` | Booléen *(optionnel)* | Analyse l'archive et calcule les empreintes SHA256 sans modifier `index.json`. |
  | `--release-url <url>` | Chaîne *(optionnel)* | URL de base personnalisée où l'archive `.zip` est hébergée pour le téléchargement. |
  | `--game <id>` | Choix (`jak1|jak2|jak3|jakx`) | Identifiant du jeu ciblé. |
  | `--from-source` | Booléen *(optionnel)* | Compile une nouvelle archive `.zip` directement depuis les textures PNG de `custom_assets/<game>/texture_replacements/`. |
  | `--slug <slug>` | Chaîne *(avec `--from-source`)* | Identifiant unique du pack. |
  | `--display-name "<nom>"` | Chaîne *(avec `--from-source`)* | Titre affiché dans le Launcher. |
  | `--description "<texte>"` | Chaîne *(avec `--from-source`)* | Description détaillée du pack de textures. |
  | `--author "<nom>"` | Chaîne *(avec `--from-source`)* | Nom de l'auteur ou du créateur. |
  | `--version <semver>` | Chaîne (`1.0.0`) | Chaîne de version sémantique. |
  | `--tags <tag...>` | Liste *(avec `--from-source`)* | Mots-clés pour le filtrage dans le Launcher. |
  | `--cover <chemin>` | Chemin *(avec `--from-source`)* | Image de couverture (`cover.png`). |
  | `--output <chemin>` | Chemin *(avec `--from-source`)* | Chemin du fichier archive `.zip` généré. |

*Exemple :*
```bash
# Enregistrer le zip exporté par le GUI dans index.json :
task modding-package-texture-pack

# Compiler directement depuis les assets PNG :
task modding-package-texture-pack -- --from-source --game jak2 --slug blue-kg-textures --display-name "Blue KG Textures"
```

---

### 11. `task modding-texture-gui`
- **Script :** [`launch_texture_gui.py`](../../../scripts/modding/launch_texture_gui.py)
- **Dossier de l'Outil :** [`open-goal-texture-pack-generator`](open-goal-texture-pack-generator)
- **Quand ?** Lors de la création, prévisualisation et empaquetage de textures modifiées via une interface graphique moderne pour PC.
- **Pourquoi ?** Lance l'application de bureau dédiée ([`open-goal-texture-pack-generator`](open-goal-texture-pack-generator), conçue en Tauri v2, Rust et Svelte 5). Elle permet de sélectionner les textures, personnaliser les métadonnées (auteur, version), appliquer automatiquement des descriptions à toutes les textures en un clic, prévisualiser les dimensions d'images et exporter les archives `.zip` directement vers `docs/modding/current_mod/texture_packs/`.
- **Paramètres CLI (`-- <args>`) :**
  - Ne nécessite aucun argument. Exécute le binaire précompilé s'il est présent (`texture_pack_generator.exe`), télécharge automatiquement la release GitHub sur Windows en cas d'absence, ou lance `npm run tauri dev` en solution de repli.

*Exemple :*
```bash
task modding-texture-gui
```

---

## 7. Workflows Développeur Typiques

### Scénario A : Développement Rapide en GOAL Lisp
1. `task set-game-jak2`
2. `task run-game` (dans un premier terminal)
3. `task repl` (dans un second terminal)
4. Modifiez vos fichiers `.gc` dans `goal_src/jak2/`
5. Dans le REPL : tapez `(mi)` pour recharger à chaud instantanément.

### Scénario B : Test du Menu « Mods » en Jeu (Boot Retail)
1. Fermez le REPL et le jeu.
2. Lancez `task boot-game-retail`.
3. Appuyez sur **L3 + SELECT** à la manette pour vérifier que le menu s'ouvre bien en conditions réelles joueur.

### Scénario C : Création & Distribution d'un Pack de Textures
1. Placez ou extrayez vos textures dans `custom_assets/<game>/texture_replacements/`.
2. Lancez l'application graphique via `task modding-texture-gui`.
3. Sélectionnez vos textures, ajustez le nom, la version, l'auteur et la description, puis exportez l'archive `.zip` vers `docs/modding/current_mod/texture_packs/`.
4. Enregistrez le pack dans le catalogue du mod : `task modding-package-texture-pack` (lit le `.zip` exporté, extrait les métadonnées et met à jour `index.json`).
5. Publiez votre Release GitHub : attachez l'archive `.zip` aux assets de release (ou laissez le workflow `release.yml` la détecter automatiquement).

### Scénario D : Synchronisation de Votre Branche avec Master-Dev
1. Sur votre branche de mod : `task modding-sync-branch`
2. En cas de conflits, vérifiez les fichiers signalés ou appliquez la commande de résolution suggérée.
3. Validez avec un boot complet : `task boot-game-retail`.
