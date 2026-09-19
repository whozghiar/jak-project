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

These tasks wrap specialized Python automation scripts located in `scripts/modding/`. You can pass arguments after `--`.

### 1. `task modding-new-branch -- jak[x]/[type]/[slug]`
- **Script:** [`create_mod_branch.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/create_mod_branch.py)
- **When?** Creating a new mod branch.
- **Why?** Branches cleanly from `master-dev`, auto-initializes the root `README.md` from the bilingual template, sets up the GitHub Actions sync badge, and verifies naming rules (`jak[1-3]/[features|config|chore]/[slug]`).

### 2. `task modding-sync-branch`
- **Script:** [`sync_branch_with_master_dev.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_branch_with_master_dev.py)
- **When?** Regularly during mod development on your mod branch.
- **Why?** Safely merges latest `origin/master-dev` into your current branch while strictly preserving your mod's root `README.md` and excluding `master-dev`-only files (`branch_sync_status.md`).

### 3. `task modding-sync-docs`
- **Script:** [`sync_docs_from_master.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_docs_from_master.py)
- **When?** When you want latest modding documentation, verified Lisp instructions, or agent skills on your branch without merging code.
- **Why?** Pulls `.agents`, `docs/modding`, `AGENTS.md`, and `CLAUDE.md` from `master-dev` without touching game code.

### 4. `task modding-land-doc -- --file <path> --message "<msg>" --push`
- **Script:** [`land_doc_on_master_dev.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/land_doc_on_master_dev.py)
- **When?** When you discover and verify an undocumented Lisp instruction or engine fact while working on a mod.
- **Why?** Reference documents (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) have a single source of truth: `master-dev`. This script commits the update to `master-dev` and immediately syncs it back to your branch, preventing parallel branches from conflicting.

### 5. `task modding-branch-status`
- **Script:** [`sync_branches_with_master.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_branches_with_master.py)
- **When?** On `master-dev` to audit mergeability across all 15+ mod branches.
- **Why?** Tests `git merge` in memory for every mod branch. When called with `--push`, auto-merges all clean branches and regenerates the sync dashboard.

### 6. `task modding-audit`
- **Script:** [`branch_audit.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/branch_audit.py)
- **When?** Before merging or releasing a mod.
- **Why?** Verifies project compliance: non-regression checks, absence of direct `default-menu*.gc` edits, presence of `mods-menu-register`, and valid bilingual README structure.

### 7. `task modding-sync-bug-report-options`
- **Script:** [`sync_bug_report_options.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_bug_report_options.py)
- **When?** Automatically on release events, or manually with `--dry-run`.
- **Why?** Keeps the bug report form dropdown restricted to mods with real published releases.

### 8. `task modding-sync-catalog`
- **Script:** [`sync_global_catalog.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_global_catalog.py)
- **When?** On `master-dev` to refresh and rebuild the unified root `index.json` catalog containing all published mods and versions.
- **Why?** Queries GitHub Releases across the repository, parses attached mod assets and metadata, dedupes versions, normalizes branch slugs, and updates the consolidated Launcher v1 schema file.

### 9. Per-Branch Catalog Tools: `update_mod_catalog.py` & `apply_catalog_to_all_branches.py`
- **When?** During release creation or per-branch catalog restructuring.
- **Why?** Generates and maintains individual mod `index.json` catalogs.

### 10. `task modding-package-texture-pack`
- **Script:** [`package_texture_pack.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/package_texture_pack.py)
- **When?** When creating or updating a standalone texture pack from `custom_assets/<game>/texture_replacements/` via the command-line interface.
- **Why?** Packages modified textures into an OpenGOAL Launcher-compliant `.zip` archive with `metadata.json` and `cover.png`, computes the SHA256 checksum, targets `docs/modding/current_mod/texture_packs/` by default so it is automatically packaged during GitHub Releases, and optionally registers/updates the texture pack in `index.json` (`--update-index`).

### 11. `task modding-texture-gui`
- **Script:** [`launch_texture_gui.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/launch_texture_gui.py)
- **When?** When creating, previewing, and packaging custom texture replacements via a modern graphical desktop application.
- **Why?** Launches the dedicated high-performance desktop application ([`open-goal-texture-pack-generator`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/docs/modding/tools/open-goal-texture-pack-generator), powered by Tauri v2, Rust, and Svelte 5). It allows you to select texture files, customize author/version metadata, automatically apply descriptions to all textures in one click, preview image dimensions, and export `.zip` archives directly into `docs/modding/current_mod/texture_packs/`.

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
2. Launch the desktop GUI via `task modding-texture-gui` (or CLI via `task modding-package-texture-pack -- --update-index`).
3. Fill in name, version, author, and description.
4. Export the archive to `docs/modding/current_mod/texture_packs/<slug>-v<version>.zip`.
5. Commit the `.zip` file on your mod branch.
6. Trigger the `release.yml` workflow: the archive is automatically packaged as a GitHub Release asset, hashed, and registered under `"texturePacks"` in `index.json`!

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

Ces tâches enveloppent les scripts Python du dossier `scripts/modding/`. Vous pouvez passer des arguments après `--`.

### 1. `task modding-new-branch -- jak[x]/[type]/[slug]`
- **Script :** [`create_mod_branch.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/create_mod_branch.py)
- **Quand ?** Pour créer une nouvelle branche de mod.
- **Pourquoi ?** Branche proprement depuis `master-dev`, génère le `README.md` bilingue avec le badge GitHub et la checklist, et valide le nommage (`jak[1-3]/[features|config|chore]/[slug]`).

### 2. `task modding-sync-branch`
- **Script :** [`sync_branch_with_master_dev.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_branch_with_master_dev.py)
- **Quand ?** Régulièrement durant le développement d'un mod sur sa branche.
- **Pourquoi ?** Fusionne `origin/master-dev` en préservant le `README.md` spécifique au mod et en excluant les fichiers réservés à `master-dev` (`branch_sync_status.md`).

### 3. `task modding-sync-docs`
- **Script :** [`sync_docs_from_master.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_docs_from_master.py)
- **Quand ?** Pour récupérer les dernières documentations, instructions Lisp ou skills sans toucher au code du jeu.
- **Pourquoi ?** Met à jour `.agents`, `docs/modding`, `AGENTS.md` et `CLAUDE.md` depuis `master-dev`.

### 4. `task modding-land-doc -- --file <chemin> --message "<msg>" --push`
- **Script :** [`land_doc_on_master_dev.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/land_doc_on_master_dev.py)
- **Quand ?** Lorsque vous découvrez et vérifiez une nouvelle instruction Lisp ou un comportement moteur.
- **Pourquoi ?** Les documents de référence (`jak[x]_lisp_instructions.md`, `engine_generic_concepts.md`) ont une source unique : `master-dev`. Ce script commite la découverte sur `master-dev` puis synchronise votre branche, évitant les conflits entre branches parallèles.

### 5. `task modding-branch-status`
- **Script :** [`sync_branches_with_master.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_branches_with_master.py)
- **Quand ?** Sur `master-dev` pour auditer l'état de fusion de toutes les branches.
- **Pourquoi ?** Teste la fusion Git en mémoire pour chaque branche. Avec `--push`, fusionne automatiquement les branches saines et met à jour le tableau de bord.

### 6. `task modding-audit`
- **Script :** [`branch_audit.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/branch_audit.py)
- **Quand ?** Avant de fusionner ou publier un mod.
- **Pourquoi ?** Vérifie la conformité du projet : non-régression, absence d'édition directe de `default-menu*.gc`, présence de `mods-menu-register` et format bilingue du README.

### 7. `task modding-sync-bug-report-options`
- **Script :** [`sync_bug_report_options.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_bug_report_options.py)
- **Quand ?** Automatiquement lors des releases, ou manuellement avec `--dry-run`.
- **Pourquoi ?** Restreint la liste des mods du formulaire de bugs aux seuls mods ayant une release officielle.

### 8. `task modding-sync-catalog`
- **Script :** [`sync_global_catalog.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/sync_global_catalog.py)
- **Quand ?** Sur `master-dev` pour actualiser et reconstruire le catalogue unifié `index.json` racine avec l'ensemble des mods et versions publiés.
- **Pourquoi ?** Interroge les releases GitHub du dépôt, analyse les archives et métadonnées associées, déduplique les versions, normalise les slugs et met à jour le fichier au schéma Launcher v1.

### 9. Outils de Catalogue par Branche : `update_mod_catalog.py` & `apply_catalog_to_all_branches.py`
- **Quand ?** Lors de la création d'une release ou réorganisation du catalogue propre à une branche.
- **Pourquoi ?** Génère et maintient le fichier `index.json` individuel consommé par l'OpenGOAL Launcher.

### 10. `task modding-package-texture-pack`
- **Script :** [`package_texture_pack.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/package_texture_pack.py)
- **Quand ?** Lors de la création ou mise à jour d'un pack de textures autonome depuis `custom_assets/<game>/texture_replacements/` via l'interface en ligne de commande.
- **Pourquoi ?** Empaquette les textures modifiées dans une archive `.zip` strictement conforme au Launcher OpenGOAL (avec `metadata.json` et `cover.png`), calcule l'empreinte SHA256, cible par défaut `docs/modding/current_mod/texture_packs/` pour une publication automatique lors des releases GitHub, et enregistre ou met à jour le pack dans le catalogue `index.json` (`--update-index`).

### 11. `task modding-texture-gui`
- **Script :** [`launch_texture_gui.py`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/scripts/modding/launch_texture_gui.py)
- **Quand ?** Lors de la création, prévisualisation et empaquetage de textures modifiées via une interface graphique moderne pour PC.
- **Pourquoi ?** Lance l'application de bureau dédiée ([`open-goal-texture-pack-generator`](file:///d:/Developpement/OpenGoal%20Dev/jak-project/docs/modding/tools/open-goal-texture-pack-generator), conçue en Tauri v2, Rust et Svelte 5). Elle permet de sélectionner les textures, personnaliser les métadonnées (auteur, version), appliquer automatiquement des descriptions à toutes les textures en un clic, prévisualiser les dimensions d'images et exporter les archives `.zip` directement vers `docs/modding/current_mod/texture_packs/`.

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
2. Lancez l'interface graphique via `task modding-texture-gui` (ou en CLI via `task modding-package-texture-pack -- --update-index`).
3. Renseignez le nom, la version, l'auteur et la description.
4. Exportez l'archive dans `docs/modding/current_mod/texture_packs/<slug>-v<version>.zip`.
5. Commitez l'archive `.zip` sur votre branche de mod.
6. Déclenchez le workflow `release.yml` : l'archive est automatiquement publiée en asset de Release GitHub, hachée et inscrite sous `"texturePacks"` dans `index.json` !

### Scénario D : Synchronisation de Votre Branche avec Master-Dev
1. Sur votre branche de mod : `task modding-sync-branch`
2. En cas de conflits, vérifiez les fichiers signalés ou appliquez la commande de résolution suggérée.
3. Validez avec un boot complet : `task boot-game-retail`.
