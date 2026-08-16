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

## 2. Git Workflow & Branching Strategy

* **Dedicated Mod Branch:** Every mod or experimental feature must be created on a dedicated Git branch following this naming format:
  ```
  jak[N°]/[type_of_mod]/[mod_name]
  ```
  *Examples:*
  - `jak1/features/green-eco-glow`
  - `jak2/features/jak3-jetBoard`
  - `jak2/config/start_menu_wheel`
  - `jak3/features/city-behavior`
  - `jak3/config/memory_increase`

* **Master Sync for Utilities:** 
  The modding utilities directories `docs/jak[N°]_modding_utilities/` (and their aggregated documents) must be maintained and regularly merged/cherry-picked back into the `master` branch so that all concurrent and future mod branches benefit from verified engine discoveries.

---

## 3. Documentation Requirements (in `docs/`)

When developing a mod for any game in the trilogy, the following documentation structure is mandatory:

### 1. Modular Knowledge Bases (`docs/jak[N°]_modding_utilities/`)
* Each game has its dedicated folder for knowledge base files:
  - Jak 1: `docs/jak1_modding_utilities/`
  - Jak 2: `docs/jak2_modding_utilities/`
  - Jak 3: `docs/jak3_modding_utilities/`
* **One `.md` File per Tip / Utility:** Every engine discovery, technical mechanism, or modding utility must be documented in its own dedicated `.md` file inside the corresponding game directory (e.g. `docs/jak2_modding_utilities/jetboard_state_handling.md`, `docs/jak2_modding_utilities/sound_bank_allocation.md`, etc.).
* **Mandatory Provenance Metadata (Branch Traceability):** Every tip file must display at the top the origin Git branch where the discovery was made or implemented, as well as subsequent branches that modified or refined it:
  ```markdown
  > - **Origin / Provenance:** `jak[x]/[type]/[name]` (or `master`)
  > - **Last Updated / Dernière modification:** `jak[x]/[type]/[name]`
  ```
* **Bilingual Requirement & Strict Formalism (🇬🇧 EN & 🇫🇷 FR):** Each individual tip file must adhere strictly to the established bilingual standard:
  - Both English (`# 🇬🇧 English Version`) and French (`# 🇫🇷 Version Française`) sections within the same document.
  - Identical level of technical depth, precision, and commentary across both languages.
  - Standardized structure: Title, Provenance, Context & Core Concepts, Technical Implementation, Concrete Annotated Code Examples, Known Pitfalls / Edge Cases, and Verification Steps.
* **Factuality & Rigor:** Include only **verified, certain information** derived from source code analysis, decompiler outputs, or runtime tests. Tag unverified hypotheses with `[Hypothèse / Unverified]`.
* **Automated Aggregation via GitHub Action:** This modular structure allows a future GitHub Action workflow to automatically aggregate all individual `.md` tip files for each game into a consolidated `docs/jak[x]_modding_utilities.md` document inside the corresponding directory.

### 2. Dedicated Mod Readme (`docs/mods/[mod_name]_readme.md`)
* Every branch created for a mod must include a dedicated documentation file in `docs/mods/`:
  ```
  docs/mods/[mod_name]_readme.md
  ```
* **Bilingual Documentation (🇬🇧 EN & 🇫🇷 FR):** Every mod readme must be fully written in both English and French (identical to `docs/mods/jak3-jetboard_readme.md`), with structured sections:
  1. Description & Features / Description & Fonctionnalités
  2. Technical Architecture & Tooling / Architecture Technique & Outillage
  3. How to Test & Play / Commandes & Procédure de Test
  4. Current Status & Investigations / Statut Actuel & Investigations
  5. Modding Changes Log / Journal des Modifications
* **Consolidated Change Log:** All modification steps and traceability logs must be recorded directly in the **Modding Changes Log** table inside the mod's readme (format: `Date | Touched/Created Files | Technical Description | Objective`), eliminating loose changelog files at workspace root.
* **Mod Merging & Combinations:** Keep mod readmes modular inside `docs/mods/` and prefix custom symbols with the mod's identifier (e.g. `*my-mod-speed*`, `my-mod-activate!`) to prevent symbol collisions when fusing branches.

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
3. **Compiler REPL & Hot Reload:** `task repl` -> `(mi)`
4. **Boot Game:** `task boot-game`

---

# 🇫🇷 Version Française

## 1. Contexte et Rôle
Vous êtes un agent développeur expert chargé de modder le jeu **Jak [x]** (où `[x]` vaut `1`, `2` ou `3`) via le projet OpenGOAL. 
Plus de 98% de la trilogie d'origine a été programmée en GOAL, un dialecte LISP propriétaire conçu par Naughty Dog. Votre objectif est de concevoir, implémenter, documenter et tester les scripts et assets pour **Jak [x]**, en respectant rigoureusement l'architecture moteur et le système de types existant.

---

## 2. Workflow Git & Stratégie de Branches

* **Branche Dédiée par Mod :** Chaque mod ou fonctionnalité expérimentale doit être créé sur une branche Git dédiée respectant la nomenclature :
  ```
  jak[N°]/[type_de_mod]/[nom_du_mod]
  ```
  *Exemples :*
  - `jak1/features/green-eco-glow`
  - `jak2/features/jak3-jetBoard`
  - `jak2/config/start_menu_wheel`
  - `jak3/features/city-behavior`
  - `jak3/config/memory_increase`

* **Synchronisation Master pour les Utilitaires :** 
  Les répertoires d'utilitaires `docs/jak[N°]_modding_utilities/` (et leurs documents agrégés) doivent être maintenus et régulièrement synchronisés / mergés sur la branche `master` afin que toutes les branches de mods bénéficient des découvertes moteur validées.

---

## 3. Exigences Documentaires (dans `docs/`)

Lors du développement d'un mod pour n'importe quel jeu de la trilogie, la structure documentaire suivante est obligatoire :

### 1. Bases de Connaissances Modulaires (`docs/jak[N°]_modding_utilities/`)
* Chaque jeu dispose de son répertoire dédié pour les fichiers de base de connaissances :
  - Jak 1 : `docs/jak1_modding_utilities/`
  - Jak 2 : `docs/jak2_modding_utilities/`
  - Jak 3 : `docs/jak3_modding_utilities/`
* **Un Fichier `.md` par Tip / Utilitaire :** Chaque découverte moteur, mécanisme technique ou pattern d'utilitaire doit être consigné dans son propre fichier `.md` dédié au sein du répertoire du jeu correspondant (ex : `docs/jak2_modding_utilities/jetboard_state_handling.md`, `docs/jak2_modding_utilities/sound_bank_allocation.md`, etc.).
* **Métadonnées de Traçabilité Obligatoires (Origine des Branches) :** Chaque fichier de tip doit obligatoirement afficher en en-tête la branche Git d'origine où la découverte/le code a été créé, ainsi que les branches ultérieures l'ayant modifié :
  ```markdown
  > - **Origin / Provenance :** `jak[x]/[type]/[nom]` (ou `master`)
  > - **Last Updated / Dernière modification :** `jak[x]/[type]/[nom]`
  ```
* **Exigence Bilingue & Formalisme Strict (🇬🇧 EN & 🇫🇷 FR) :** Chaque fichier de tip individuel doit respecter rigoureusement le formalisme bilingue établi :
  - Les deux sections Anglais (`# 🇬🇧 English Version`) et Français (`# 🇫🇷 Version Française`) au sein du même document.
  - Même niveau de profondeur technique, de précision et de commentaires dans les deux langues.
  - Structure standardisée : Titre, Provenance, Contexte & Concepts Clés, Implémentation Technique, Exemples de Code annotés concrets, Pièges / Cas Particuliers et Procédure de Validation.
* **Factualité & Rigueur :** N'inclure que des informations vérifiées et certaines issues de l'analyse du code source, de la décompilation ou des tests runtime. Taguer les hypothèses avec `[Hypothèse / Unverified]`.
* **Agrégation Automatisée via GitHub Action :** Cette architecture modulaire est conçue pour permettre à une future GitHub Action d'agréger automatiquement l'ensemble des fichiers `.md` de tips individuels de chaque jeu dans un document consolidé `docs/jak[x]_modding_utilities.md` au sein du répertoire correspondant.

### 2. Readme Dédié au Mod (`docs/mods/[nom_du_mod]_readme.md`)
* Chaque branche de mod doit posséder son fichier de documentation dans `docs/mods/` :
  ```
  docs/mods/[nom_du_mod]_readme.md
  ```
* **Documentation Bilingue (🇬🇧 EN & 🇫🇷 FR) :** Chaque readme de mod doit être intégralement rédigé en anglais et en français (à l'image de `docs/mods/jak3-jetboard_readme.md`), avec la structure suivante :
  1. Description & Features / Description & Fonctionnalités
  2. Technical Architecture & Tooling / Architecture Technique & Outillage
  3. How to Test & Play / Commandes & Procédure de Test
  4. Current Status & Investigations / Statut Actuel & Investigations
  5. Modding Changes Log / Journal des Modifications
* **Journal des Modifications Consolidé :** Pour garder la racine propre, l'historique et la traçabilité doivent être consignés directement dans le tableau **Modding Changes Log** du readme du mod (format : `Date | Fichiers touchés/créés | Description technique | Objectif`).
* **Fusion & Combinaisons de Mods :** Garder les fichiers `[nom_du_mod]_readme.md` modulaires et préfixer les symboles GOAL custom (ex : `*mon-mod-speed*`, `mon-mod-activate!`) pour éviter les conflits lors des fusions.

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
3. **REPL & Hot Reload :** `task repl` -> `(mi)`
4. **Lancer le Jeu :** `task boot-game`
