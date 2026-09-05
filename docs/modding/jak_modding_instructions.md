# AI Agent Modding Directive & Instructions (Jak 1 / Jak 2 / Jak 3) / Directives & Instructions de Modding

> **Mandatory Universal Directive / Directive Universelle Obligatoire**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Context and Role
You are an expert developer agent assigned to modding the game **Jak [x]** (where `[x]` stands for `1`, `2`, or `3`) via the OpenGOAL project. 
Over 98% of the original trilogy was coded in GOAL, a custom LISP dialect developed by Naughty Dog. Your goal is to design, implement, document, and test scripts and assets for **Jak [x]**, strictly respecting the existing engine architecture and typing system.

---

## 2. Git Branching Strategy & Architecture

* **Repository Architecture:**
  - `master`: Pure mirror of upstream OpenGOAL (`open-goal/jak-project:master`). Never commit directly to `master`.
  - `master-dev`: Integration and modding base branch.
* **Dedicated Branch per Mod:** Every mod or experimental feature MUST be branched from `master-dev` and follow:
  ```
  jak[N°]/[type_of_mod]/[mod_name]
  ```
  *Examples:*
  - `jak1/features/green-eco-glow`
  - `jak2/features/jak3-jetBoard`
  - `jak2/config/start_menu_wheel`
  - `jak3/features/city-behavior`
  - `jak3/config/memory_increase`

* **Creating New Mod Branches Automatically:**
  Always create new mod branches using the dedicated helper:
  ```bash
  python scripts/modding/create_mod_branch.py jak[N°]/[type_of_mod]/[mod_name]
  ```
  This command fetches `master-dev`, branches out, and automatically transforms the root `README.md` into the customized mod presentation template.

* **Syncing Modding Docs On-Demand:**
  To update modding docs, tips, and guidelines on an active mod branch without rebasing or generating extraneous bot commits:
  ```bash
  python scripts/modding/sync_docs_from_master.py
  ```

* **Branch Synchronization Routine & Status Dashboard:**
  The live sync status of all mod branches against `master` is tracked in `README.md` and [`docs/modding/tools/branch_sync_status.md`](tools/branch_sync_status.md). To test or push clean merges manually:
  ```bash
  python scripts/modding/sync_branches_with_master.py --push
  ```

---

## 3. Documentation Requirements (in `docs/modding/`)

When developing a mod for any game in the trilogy, the following documentation structure is mandatory:

### 1. Modular Knowledge Bases (`docs/modding/jak[N°]_modding_utilities/`)
* Each game has its dedicated folder for knowledge base files:
  - Jak 1: `docs/modding/jak1_modding_utilities/`
  - Jak 2: `docs/modding/jak2_modding_utilities/`
  - Jak 3: `docs/modding/jak3_modding_utilities/`
* **One `.md` File per Tip / Utility:** Every engine discovery, technical mechanism, or modding utility must be documented in its own dedicated `.md` file inside the corresponding game directory (e.g. `docs/modding/jak2_modding_utilities/11_jetboard_state_handling.md`, etc.).
* **⚠️ NEVER Edit Aggregated Files Directly:** Agents must **NEVER** edit or touch the consolidated files `docs/modding/jak[x]_modding_utilities/jak[x]_modding_utilities.md` manually. Agents must exclusively create a new numbered `.md` file (or edit an existing individual tip file) according to the discovery. The aggregated document is maintained and regenerated exclusively by the automated CI aggregation script.
* **Mandatory Provenance Metadata (Branch Traceability):** Every tip file must display at the top the origin Git branch where the discovery was made or implemented, as well as subsequent branches that modified or refined it:
  ```markdown
  > - **Origin / Provenance:** `jak[x]/[type]/[name]` (or `master-dev`)
  > - **Last Updated / Dernière modification:** `jak[x]/[type]/[name]`
  ```
* **Bilingual Requirement & Strict Formalism (🇬🇧 EN & 🇫🇷 FR):** Each individual tip file must adhere strictly to the established bilingual standard:
  - Both English (`# 🇬🇧 English Version`) and French (`# 🇫🇷 Version Française`) sections within the same document.
  - Identical level of technical depth, precision, and commentary across both languages.
  - Standardized structure: Title, Provenance, Context & Core Concepts, Technical Implementation, Concrete Annotated Code Examples, Known Pitfalls / Edge Cases, and Verification Steps.
* **Factuality & Rigor:** Include only **verified, certain information** derived from source code analysis, decompiler outputs, or runtime tests. Tag unverified hypotheses with `[Hypothèse / Unverified]`.
* **Automated Aggregation via GitHub Action:** The GitHub Action workflow (`.github/workflows/sync-modding-docs.yaml`) automatically harvests all individual `.md` tip files for each game and aggregates them into `docs/modding/jak[x]_modding_utilities/jak[x]_modding_utilities.md` on `master-dev`.

### 2. Dedicated Mod Readme (`README.md` at root)
* Every mod branch must replace the repository root `README.md` with its dedicated bilingual mod presentation.
* **Automatic Initialization:** Created automatically when using `python scripts/modding/create_mod_branch.py <branch_name>` via the template at:
  ```
  docs/modding/templates/MOD_README.template.md
  ```
* **GitHub Native Rendering:** Replacing root `README.md` allows GitHub to automatically display the mod's presentation directly when browsing that branch. (Original OpenGOAL port README is archived in `open-goal-original-readme.md`).
* **Mandatory Mod Readme Contents (🇬🇧 EN & 🇫🇷 FR):** Every mod readme must feature:
  1. **Installation & Build Guide:** Exact commands to set game, compile, and boot.
  2. **Detailed Features List:** Precise explanation of behaviors, models, or configurations changed.
  3. **Usage & Controls:** Keybindings, controller triggers, debug menus, or in-game activations.
  4. **Demonstrative Video / Media:** Embedded YouTube video demonstration with clickable thumbnail and link. Storing heavy video files (`.mp4`) directly inside the Git repository is strictly prohibited to keep history lightweight.
  5. **Modding Changes Log:** Tracing files touched/created, technical rationale, and objectives.
* **Mod Merging & Combinations:** Keep mod readmes modular and prefix custom symbols with the mod's identifier (e.g. `*my-mod-speed*`, `my-mod-activate!`) to prevent symbol collisions when fusing branches.

---

## 4. Strict Guardrails & Architecture Rules

* **Mandatory In-Code Comments:** Every definitive code addition or modification (types, functions, methods, states, hooks, macros, and overriding behaviors) **must be thoroughly commented** directly in the source code (`.gc`). Comments must clarify purpose, arguments, return values, and side effects.
* **Preservation of Existing Code:** Strictly avoid deleting, emptying, or destructively modifying original game source files. Favor modular extensions and surgical overrides.
* **Declaration of New Files (`.gp`):** Declare any new `.gc` files in the corresponding project file (`.gp`) for Jak [x] (e.g., in `goal_src/jak[x]/...`).
* **Texture Replacement:** Custom textures (`.png`) must be placed in `custom_assets/jak[x]/texture_replacements/`.
* **AI Attribution:** Always disclose the usage of AI by adding `(AI-assisted)` to commits, comments, and documentation. Never create issues or PRs automatically.

---

## 5. Execution Policy & Reference Commands

> [!IMPORTANT]
> **Task Execution Policy:** AI agents must **NOT** execute long-running build or runtime `task` commands silently in the background without asking the user. Propose the exact commands clearly for the user to run in their terminal.

### Reference Commands:
1. **Set Active Game:** `task set-game-jak[x]` (e.g. `task set-game-jak2`)
2. **Extract & Transfer Assets / Textures:** `task extract`
3. **Compiler REPL & Hot Reload:** `task repl` -> `(mi)` — GOAL `.gc` edits need **no** C++ build
4. **Boot Game:** `task boot-game`

**Build tasks (pick the smallest one that covers your change):**
- `task build-release-game` — rebuild only `gk` + `goalc`; use when you edit engine/compiler C++.
- `task build-release-decomp` — rebuild only the `decompiler`; use when you edit `decompiler/` code
  or `decompiler/config/**`, then **re-run `task extract`** (a decompiler change is inert until
  re-extraction).
- `task build-release` — full build of all ~20 binaries; first setup, or many layers changed at once.
- First setup / after `task clean-cmake`: `task gen-cmake-release` (installs `sccache` wiring if
  present — `scoop install sccache`).

See [`tools/build_and_iteration_workflow.md`](tools/build_and_iteration_workflow.md) for the full three-layer
model and the "what if my mod modifies the decompiler?" walkthrough.

---

# 🇫🇷 Version Française

## 1. Contexte et Rôle
Vous êtes un agent développeur expert chargé de modder le jeu **Jak [x]** (où `[x]` vaut `1`, `2` ou `3`) via le projet OpenGOAL. 
Plus de 98% de la trilogie d'origine a été programmée en GOAL, un dialecte LISP propriétaire conçu par Naughty Dog. Votre objectif est de concevoir, implémenter, documenter et tester les scripts et assets pour **Jak [x]**, en respectant rigoureusement l'architecture moteur et le système de types existant.

---

## 2. Workflow Git & Stratégie de Branches

* **Architecture du Dépôt :**
  - `master` : Miroir strict d'OpenGOAL officiel (`open-goal/jak-project:master`). Ne jamais commiter directement sur `master`.
  - `master-dev` : Branche d'intégration et base commune de modding.
* **Branche Dédiée par Mod :** Chaque mod ou fonctionnalité expérimentale doit être obligatoirement dérivé de `master-dev` et respecter la nomenclature :
  ```
  jak[N°]/[type_de_mod]/[nom_du_mod]
  ```
  *Exemples :*
  - `jak1/features/green-eco-glow`
  - `jak2/features/jak3-jetBoard`
  - `jak2/config/start_menu_wheel`
  - `jak3/features/city-behavior`
  - `jak3/config/memory_increase`

* **Création Automatisée d'une Nouvelle Branche de Mod :**
  Toujours initialiser une nouvelle branche via le script dédié :
  ```bash
  python scripts/modding/create_mod_branch.py jak[N°]/[type_de_mod]/[nom_du_mod]
  ```
  Ce script checkout `master-dev`, crée la branche et transforme automatiquement le `README.md` racine en template personnalisé du mod.

* **Mise à Jour de la Documentation à la Demande :** 
  Pour synchroniser la documentation, les tips et les consignes de modding sur une branche de mod active sans rebase invasif ni commits polluants de bot :
  ```bash
  python scripts/modding/sync_docs_from_master.py
  ```

* **Routine de Synchronisation & Tableau de Bord des Conflits :**
  L'état de synchronisation en direct des branches par rapport à `master` est suivi dans `README.md` et [`docs/modding/tools/branch_sync_status.md`](tools/branch_sync_status.md). Pour tester ou fusionner manuellement les branches propres :
  ```bash
  python scripts/modding/sync_branches_with_master.py --push
  ```

---

## 3. Exigences Documentaires (dans `docs/modding/`)

Lors du développement d'un mod pour n'importe quel jeu de la trilogie, la structure documentaire suivante est obligatoire :

### 1. Bases de Connaissances Modulaires (`docs/modding/jak[N°]_modding_utilities/`)
* Chaque jeu dispose de son répertoire dédié pour les fichiers de base de connaissances :
  - Jak 1 : `docs/modding/jak1_modding_utilities/`
  - Jak 2 : `docs/modding/jak2_modding_utilities/`
  - Jak 3 : `docs/modding/jak3_modding_utilities/`
* **Un Fichier `.md` par Tip / Utilitaire :** Chaque découverte moteur, mécanisme technique ou pattern d'utilitaire doit être consigné dans son propre fichier `.md` dédié au sein du répertoire du jeu correspondant (ex : `docs/modding/jak2_modding_utilities/11_jetboard_state_handling.md`, etc.).
* **⚠️ Interdiction de Modifier les Fichiers Agrégés Directement :** Les agents ne doivent **JAMAIS** modifier manuellement les fichiers consolidés `docs/modding/jak[x]_modding_utilities/jak[x]_modding_utilities.md`. Les agents doivent exclusivement créer un nouveau fichier `.md` numéroté (ou modifier le fichier individuel existant) selon le tip découvert. Le fichier agrégé est maintenu et régénéré exclusivement par le script d'agrégation automatique CI.
* **Métadonnées de Traçabilité Obligatoires (Origine des Branches) :** Chaque fichier de tip doit obligatoirement afficher en en-tête la branche Git d'origine où la découverte/le code a été créé, ainsi que les branches ultérieures l'ayant modifié :
  ```markdown
  > - **Origin / Provenance :** `jak[x]/[type]/[nom]` (ou `master-dev`)
  > - **Last Updated / Dernière modification :** `jak[x]/[type]/[nom]`
  ```
* **Exigence Bilingue & Formalisme Strict (🇬🇧 EN & 🇫🇷 FR) :** Chaque fichier de tip individuel doit respecter rigoureusement le formalisme bilingue établi :
  - Les deux sections Anglais (`# 🇬🇧 English Version`) et Français (`# 🇫🇷 Version Française`) au sein du même document.
  - Même niveau de profondeur technique, de précision et de commentaires dans les deux langues.
  - Structure standardisée : Titre, Provenance, Contexte & Concepts Clés, Implémentation Technique, Exemples de Code annotés concrets, Pièges / Cas Particuliers et Procédure de Validation.
* **Factualité & Rigueur :** N'inclure que des informations vérifiées et certaines issues de l'analyse du code source, de la décompilation ou des tests runtime. Taguer les hypothèses avec `[Hypothèse / Unverified]`.
* **Agrégation Automatisée via GitHub Action :** La GitHub Action (`.github/workflows/sync-modding-docs.yaml`) récolte automatiquement les tips individuels des branches de mods et les agrège dans `docs/modding/jak[x]_modding_utilities/jak[x]_modding_utilities.md` sur `master-dev`.

### 2. Readme Dédié au Mod (`README.md` à la racine)
* Chaque branche de mod doit remplacer le fichier `README.md` à la racine du dépôt par la présentation de son mod.
* **Initialisation Automatisée :** Généré automatiquement via `python scripts/modding/create_mod_branch.py <nom_branche>` à partir du modèle :
  ```
  docs/modding/templates/MOD_README.template.md
  ```
* **Affichage Natif sur GitHub :** Remplacer le `README.md` racine permet à GitHub d'afficher immédiatement la page de présentation du mod lorsque l'utilisateur navigue sur cette branche. (Le README originel du port OpenGOAL est archivé dans `open-goal-original-readme.md`).
* **Contenu Obligatoire du Readme de Mod (🇬🇧 EN & 🇫🇷 FR) :** Chaque readme de mod doit obligatoirement comprendre :
  1. **Guide d'installation & de compilation :** Commandes exactes pour configurer le jeu cible, compiler et lancer.
  2. **Fonctionnalités détaillées :** Description claire des comportements, modèles ou réglages modifiés.
  3. **Utilisation & Commandes :** Touches manette, raccourcis clavier, menus de debug ou déclencheurs ingame.
  4. **Vidéo Démonstrative / Médias :** Vidéo de démonstration intégrée via YouTube avec miniature cliquable et lien direct. L'hébergement direct de fichiers vidéo lourds (`.mp4`) dans le dépôt Git est strictement proscrit afin de préserver la légèreté de l'historique.
  5. **Journal des Modifications (Modding Changes Log) :** Tableau de traçabilité des fichiers modifiés, justifications techniques et objectifs.
* **Fusion & Combinaisons de Mods :** Garder les composants modulaires et préfixer les symboles GOAL custom (ex : `*mon-mod-speed*`, `mon-mod-activate!`) pour éviter les collisions de symboles lors des fusions de branches.

---

## 4. Règles d'Architecture & Garde-Fous

* **Commentaires Obligatoires dans le Code :** Tout ajout ou modification définitive de code (types, fonctions, méthodes, états, hooks, macros) **doit être rigoureusement commenté** directement dans les fichiers source `.gc` (rôle, arguments, types, valeurs de retour, effets de bord).
* **Préservation du Code Existant :** Interdiction absolue de supprimer ou écraser destructivement les fichiers sources d'origine. Privilégier les extensions modulaires et les surcharges chirurgicales.
* **Déclaration des Nouveaux Fichiers (`.gp`) :** Déclarer tout nouveau fichier `.gc` dans le fichier projet (`.gp`) correspondant pour Jak [x].
* **Remplacement de Textures :** Placer les textures custom (`.png`) dans `custom_assets/jak[x]/texture_replacements/`.
* **Attribution IA :** Toujours mentionner l'utilisation d'IA en ajoutant `(AI-assisted)` aux commits, commentaires et documents. Ne jamais créer d'issues ou de PRs automatiquement.

---

## 5. Politique d'Exécution & Commandes de Référence

> [!IMPORTANT]
> **Politique d'Exécution des Tâches :** Les agents IA ne doivent **PAS** exécuter de commandes longues de build ou d'exécution `task` en arrière-plan sans autorisation explicite. Proposez les commandes exactes à l'utilisateur pour qu'il les lance dans son terminal.

### Commandes de Référence :
1. **Sélectionner le Jeu Actif :** `task set-game-jak[x]` (ex : `task set-game-jak2`)
2. **Extraire & Transférer les Assets :** `task extract`
3. **REPL & Hot Reload :** `task repl` -> `(mi)` — les modifs GOAL `.gc` ne nécessitent **aucun** build C++
4. **Lancer le Jeu :** `task boot-game`

**Tâches de build (choisir la plus petite qui couvre votre changement) :**
- `task build-release-game` — reconstruit uniquement `gk` + `goalc` ; à utiliser si vous modifiez
  du C++ moteur/compilateur.
- `task build-release-decomp` — reconstruit uniquement le `decompiler` ; à utiliser si vous
  modifiez le code `decompiler/` ou `decompiler/config/**`, puis **relancer `task extract`** (une
  modif du décompilateur est inerte tant que l'extraction n'est pas refaite).
- `task build-release` — build complet des ~20 binaires ; première install, ou plusieurs couches
  modifiées à la fois.
- Première install / après `task clean-cmake` : `task gen-cmake-release` (câble `sccache` s'il est
  présent — `scoop install sccache`).

Voir [`tools/build_and_iteration_workflow.md`](tools/build_and_iteration_workflow.md) pour le modèle complet à
trois couches et le déroulé « et si mon mod modifie le décompilateur ? ».
