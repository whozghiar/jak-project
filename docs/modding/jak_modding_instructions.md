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

### 1. The two reference documents (consult BEFORE coding)

There is now **one curated source of truth per topic**, not a per-branch pile of
tip files. Before you write or change a single `.gc` line, read the relevant one:

* **`docs/modding/jak[N°]_lisp_instructions.md`** — the verified OpenGOAL Lisp
  reference for that game: every instruction/pattern that is **100 %-certain**
  (compiled and seen working), in plain language, with one commented example each
  and its traps. This is what stops an agent hallucinating an instruction that does
  not exist.
  - Jak 1: `docs/modding/jak1_lisp_instructions.md`
  - Jak 2: `docs/modding/jak2_lisp_instructions.md`
  - Jak 3: `docs/modding/jak3_lisp_instructions.md`
* **`docs/modding/engine_generic_concepts.md`** — the shared, non-Lisp engine primer
  (memory, heaps, DGOs & level streaming, virtual-state residency, process life
  cycle, boot diagnostics). Common to all three games.

**Recording a discovery (conflict-free rule).** These files have **one source of
truth: `master-dev`**. NEVER edit them on a mod branch — that is what caused
constant merge conflicts. When you verify a new instruction or engine fact:

1. `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push`
   — it carries your appended block onto `master-dev` as a tiny dedicated commit,
   pushes, returns you to your branch and re-syncs. (Or do the round-trip by hand:
   branch off `master-dev`, append, commit, push, then `task modding-sync-docs`.)
2. Only **append** — add a numbered block below the
   `➕ APPEND NEW VERIFIED ENTRIES` marker. Never reflow existing sections. Appends
   to end-of-file are what keep parallel mods from ever conflicting on the file.
3. Only add what is **verified**. No speculation, no "should work".

**Mod-*feature*-specific notes** (what your mod changed and why — jetboard tuning,
a faction rework, a networking stub) do **not** go in the reference docs. They go in
your mod branch's root `README.md` "Modding Changes Log", and optionally a
`docs/modding/current_mod/<slug>_readme.md` on your branch.

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

### 🥇 Golden rules (non-negotiable)

1. **Consult the reference first.** Before writing or changing any `.gc`, read the
   relevant `docs/modding/jak[x]_lisp_instructions.md` and
   `docs/modding/engine_generic_concepts.md`. Do not invent instructions.
2. **Native non-regression.** A mod MUST NOT change the game's default behaviour
   unless its written spec explicitly requires it. Ship every behaviour change
   **OFF by default**, gated behind the mod's toggle. A fresh install with the mod
   compiled but disabled must play identically to stock.
3. **Debug ▸ Mods toggle mandatory.** Every mod must be switchable on/off at runtime
   from the in-game debug menu. On Jak 2, register it with
   `(mods-menu-register "<slug>" builder)` — see
   [`tools/mods_debug_menu.md`](tools/mods_debug_menu.md). Never edit
   `default-menu.gc` / `default-menu-pc.gc` directly. (Jak 1 / Jak 3: add a
   mod-slug-prefixed submenu for now; the unified framework port is a follow-up.)
4. **Record every verified Lisp instruction** you rely on that is not yet in
   `jak[x]_lisp_instructions.md` — via `task modding-land-doc` (`master-dev` only,
   append-only). See §3.1.

### Architecture rules

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

**Modding-workflow tasks (wrappers over `scripts/modding/*.py`):**
- `task modding-new-branch -- jak2/features/my-mod` — new mod branch from `master-dev` + initial README.
- `task modding-sync-branch` — safe `git merge` of `master-dev` into the current branch.
- `task modding-sync-docs` — pull `docs/modding` + `AGENTS.md` + `CLAUDE.md` from `master-dev` (prunes deleted files).
- `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push` — land a doc addition on `master-dev` conflict-free.
- `task modding-branch-status` — refresh the branch sync dashboard.
- `task modding-audit` — regenerate `docs/modding/branch_audit.md`.

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

### 1. Les deux documents de référence (à consulter AVANT de coder)

Il existe désormais **une source de vérité curatée par sujet**, et non plus un tas
de fichiers de tips par branche. Avant d'écrire ou de modifier une seule ligne
`.gc`, lisez le document pertinent :

* **`docs/modding/jak[N°]_lisp_instructions.md`** — la référence Lisp OpenGOAL
  vérifiée pour ce jeu : chaque instruction/pattern **certain à 100 %** (compilé et
  vu fonctionner), en langage simple, avec un exemple commenté et ses pièges. C'est
  ce qui empêche un agent d'halluciner une instruction qui n'existe pas.
  - Jak 1 : `docs/modding/jak1_lisp_instructions.md`
  - Jak 2 : `docs/modding/jak2_lisp_instructions.md`
  - Jak 3 : `docs/modding/jak3_lisp_instructions.md`
* **`docs/modding/engine_generic_concepts.md`** — l'introduction moteur partagée,
  non-Lisp (mémoire, heaps, DGO & streaming de niveaux, résidence des états
  virtuels, cycle de vie des processus, diagnostic au démarrage). Commune aux trois
  jeux.

**Consigner une découverte (règle anti-conflit).** Ces fichiers ont **une seule
source de vérité : `master-dev`**. Ne JAMAIS les éditer sur une branche de mod —
c'est ce qui a causé les conflits de fusion permanents. Quand vous vérifiez une
nouvelle instruction ou un fait moteur :

1. `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push`
   — le script porte votre bloc ajouté sur `master-dev` comme un petit commit dédié,
   pousse, vous ramène sur votre branche et resynchronise. (Ou faites l'aller-retour
   à la main : partir de `master-dev`, ajouter, commit, push, puis
   `task modding-sync-docs`.)
2. Uniquement en **ajout** — un bloc numéroté sous le marqueur
   `➕ APPEND NEW VERIFIED ENTRIES`. Ne jamais reformater les sections existantes.
   Les ajouts en fin de fichier sont ce qui évite tout conflit entre mods
   parallèles.
3. N'ajouter que ce qui est **vérifié**. Pas de spéculation, pas de « devrait
   marcher ».

**Les notes propres à une *fonctionnalité* de mod** (ce que votre mod change et
pourquoi — réglage du jetboard, refonte d'une faction, stub réseau) ne vont **pas**
dans les documents de référence. Elles vont dans le « Modding Changes Log » du
`README.md` racine de votre branche, et éventuellement un
`docs/modding/current_mod/<slug>_readme.md` sur votre branche.

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

### 🥇 Règles d'or (non négociables)

1. **Consulter la référence d'abord.** Avant d'écrire ou de modifier un `.gc`, lire
   le `docs/modding/jak[x]_lisp_instructions.md` concerné et
   `docs/modding/engine_generic_concepts.md`. Ne pas inventer d'instructions.
2. **Non-régression native.** Un mod NE DOIT PAS changer le comportement par défaut
   du jeu sauf si son cahier des charges écrit l'exige explicitement. Livrer chaque
   changement de comportement **DÉSACTIVÉ par défaut**, derrière la bascule du mod.
   Une installation neuve, mod compilé mais désactivé, doit se jouer à l'identique
   du jeu d'origine.
3. **Bascule Debug ▸ Mods obligatoire.** Tout mod doit être activable/désactivable à
   la volée depuis le menu debug en jeu. Sur Jak 2, l'enregistrer avec
   `(mods-menu-register "<slug>" builder)` — voir
   [`tools/mods_debug_menu.md`](tools/mods_debug_menu.md). Ne jamais éditer
   directement `default-menu.gc` / `default-menu-pc.gc`. (Jak 1 / Jak 3 : ajouter un
   sous-menu préfixé par le slug pour l'instant ; le portage du framework unifié est
   un suivi.)
4. **Consigner toute instruction Lisp vérifiée** dont vous dépendez et qui n'est pas
   encore dans `jak[x]_lisp_instructions.md` — via `task modding-land-doc`
   (`master-dev` uniquement, en ajout seul). Voir §3.1.

### Règles d'architecture

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

**Tâches du workflow de modding (wrappers de `scripts/modding/*.py`) :**
- `task modding-new-branch -- jak2/features/mon-mod` — nouvelle branche de mod depuis `master-dev` + README initial.
- `task modding-sync-branch` — `git merge` sûr de `master-dev` dans la branche courante.
- `task modding-sync-docs` — rapatrie `docs/modding` + `AGENTS.md` + `CLAUDE.md` depuis `master-dev` (purge les fichiers supprimés).
- `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push` — intègre un ajout de doc sur `master-dev` sans conflit.
- `task modding-branch-status` — actualise le tableau de bord de synchronisation des branches.
- `task modding-audit` — régénère `docs/modding/branch_audit.md`.
