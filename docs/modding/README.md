# OpenGOAL Modding Documentation Hub / Centre de Documentation du Modding OpenGOAL

> **Bilingual Modding Hub Portal / Portail Bilingue du Modding**
>
> - **Scope / Portée :** Official Reference Guides, Workflows, Tools & Synchronization Dashboards
> - **Source of Truth / Source de Vérité :** `master-dev`

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Core References](#1-core-references-consult-before-coding) · [2. Agent Directives & Skills](#2-agent-guidelines--modular-skills) · [3. Engineering & Workflow Guides](#3-engineering--workflow-guides) · [4. Mandatory Mods Menu Policy](#4-mandatory-rule-registration-in-the-mods-menu-mods-menu-register) · [5. Branch Dashboards & Compliance](#5-branch-dashboards--compliance) · [6. Templates & Standalone Tools](#6-templates--standalone-modding-tools)
> - 🇫🇷 **Français :** [1. Références Fondamentales](#1-références-fondamentales-à-consulter-avant-de-coder) · [2. Directives des Agents & Compétences](#2-directives-des-agents--compétences-modulaires) · [3. Guides d'Ingénierie & Workflows](#3-guides-dingénierie--de-workflows) · [4. Règle Obligatoire du Menu Mods](#4-règle-obligatoire--enregistrement-dans-le-menu-mods-mods-menu-register) · [5. Tableaux de Bord & Conformité](#5-tableaux-de-bord--conformité-des-branches) · [6. Modèles & Outils Autonomes](#6-modèles--outils-de-modding-autonomes)

---

# 🇬🇧 English Version

This directory centralizes all official reference guides, engineering workflows, tool manuals, and synchronization dashboards for modding Jak 1, Jak 2, and Jak 3 with OpenGOAL.

---

## 1. Core References (Consult Before Coding)

These curated, verified documents are the **single source of truth** hosted on `master-dev`. They prevent hallucinations by providing concrete, tested examples and known traps.

| Reference Document | Scope | Contents |
| :--- | :--- | :--- |
| 📗 [`jak1_lisp_instructions.md`](jak1_lisp_instructions.md) | Jak 1 | Verified OpenGOAL LISP syntax, states, and entity functions for Jak 1. |
| 📗 [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) | Jak 2 | Verified OpenGOAL LISP instructions, combat hooks, and entity methods for Jak 2. |
| 📗 [`jak3_lisp_instructions.md`](jak3_lisp_instructions.md) | Jak 3 | Verified OpenGOAL LISP instructions, vehicle hooks, and weapon types for Jak 3. |
| 📘 [`engine_generic_concepts.md`](engine_generic_concepts.md) | All Games | Memory heaps (`global`, `level`, `debug`, `process`), `mmap` PS2 RAM simulation, DGOs, and process lifecycle. |

> **Anti-Conflict Landing Rule:**
> Never edit reference docs directly on a mod branch. Use:
> ```bash
> task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
> task modding-sync-docs
> ```

---

## 2. Agent Guidelines & Modular Skills

- **[Unified Agent Guide (`AGENTS.md`)](../../AGENTS.md)**: Rules, Taskfile command reference, REPL hot-reload cycle, ghost memory verification, and git branching standards.
- **[Dynamic Skills Library (`.agents/skills/`)](../../.agents/skills/)**:
  - [`goal-lisp`](../../.agents/skills/goal-lisp/SKILL.md) & [`discoveries.md`](../../.agents/skills/goal-lisp/discoveries.md)
  - [`engine-internals`](../../.agents/skills/engine-internals/SKILL.md) & [`repl-workflow.md`](../../.agents/skills/engine-internals/repl-workflow.md)
  - [`custom-actors-levels`](../../.agents/skills/custom-actors-levels/SKILL.md) & [`discoveries.md`](../../.agents/skills/custom-actors-levels/discoveries.md)
  - [`texture-modding`](../../.agents/skills/texture-modding/SKILL.md) & [`discoveries.md`](../../.agents/skills/texture-modding/discoveries.md)

---

## 3. Engineering & Workflow Guides

| Guide | Description |
| :--- | :--- |
| 🤖 [`tools/github_workflows.md`](tools/github_workflows.md) | Comprehensive pedagogical guide for all 5 repository GitHub Actions workflows (upstream sync, branch checks, releases, bug triaging). |
| 🛠️ [`tools/task_scripts_reference.md`](tools/task_scripts_reference.md) | Detailed pedagogical guide for all Taskfile tasks and modding Python scripts (`scripts/modding/*.py`). |
| 🚀 [`custom_entity_workflow.md`](custom_entity_workflow.md) | Comprehensive engineering guide on importing custom 3D models, custom animations, and new sound banks (`.SBK`) with `og-j1-board` case study. |
| ⚡ [`tools/build_and_iteration_workflow.md`](tools/build_and_iteration_workflow.md) | Three-layer build model, `sccache` acceleration, and targeted build tasks (`build-release-game`, `build-release-decomp`). |
| 🎨 [`tools/model_and_entity_level_injection_guide.md`](tools/model_and_entity_level_injection_guide.md) | No-borrow Merc `.fr3` injection pipeline (`extra_art_groups_by_dgo`) to inject models into any level. |
| 🎛️ [`tools/mods_menu.md`](tools/mods_menu.md) | How to register mods into the in-game Mods menu (L3 + SELECT, works in a retail boot) via `(mods-menu-register "<slug>" builder)`. |
| 📦 [`tools/mod_distribution_guide.md`](tools/mod_distribution_guide.md) | Full guide on packaging, CI/CD automated releases, launcher catalog (`index.json`), and custom cover thumbnails (`docs/img/mod/mod_cover.png`). |
| 🎮 [`how_to_install_mod.md`](how_to_install_mod.md) | Player-facing tutorial: add a mod's `index.json` catalog URL in the Launcher, install it, and activate it in-game (L3 + SELECT). |
| 🐛 [`tools/mod_bug_tracking.md`](tools/mod_bug_tracking.md) | Player-facing "Mod Bug Report" issue form, automatic `jak[x]`/`mod:<slug>` labeling, and the fix-commit → release loop (`Fixes #123`). |

---

## 4. Mandatory Rule: Registration in the "Mods" Menu (`mods-menu-register`)

> [!IMPORTANT]
> Every new mod created in this repository — **especially `features/*`-type branches (`jak[x]/features/*`)** — **must be toggleable in-game** via the unified registry:
> ```lisp
> (mods-menu-register "<mod-slug>" <builder-function>)
> ```
> - **Retail Boot Compatibility:** The OpenGOAL Launcher boots the game in retail mode (`-boot -fakeiso`), disabling the debug menu and debug heap. The Mods menu opens with **L3 + SELECT** in both retail and debug boots (Jak 2 and Jak 3).
> - **Native Non-Regression:** Every feature must start **disabled by default (`#f`)** and be toggleable on player demand from this menu.
> - **Resources:** See the full guide [`tools/mods_menu.md`](tools/mods_menu.md) and the template file [`templates/mod_menu.template.gc`](templates/mod_menu.template.gc).

---

## 5. Branch Dashboards & Compliance

- 📊 [`tools/branch_sync_status.md`](tools/branch_sync_status.md): Live mergeability dashboard across all mod branches (`task modding-branch-status`). **`master-dev`-only**.
- 📜 [`tools/branch_sync_history.md`](tools/branch_sync_history.md): Historical log of automated branch merges and conflict resolutions.
- 📋 [`branch_audit.md`](branch_audit.md): Compliance report tracking active mod branches against project standards (`task modding-audit`).

---

## 6. Templates & Standalone Modding Tools

- 📝 [`templates/MOD_README.template.md`](templates/MOD_README.template.md): Bilingual presentation template for root `README.md` on mod branches.
- ⚙️ [`templates/mod_menu.template.gc`](templates/mod_menu.template.gc): Ready-to-use GOAL template for in-game Mods menu registration.
- 📂 [`current_mod/`](current_mod/): Folder storing mod-specific feature readmes (e.g. [`current_mod/README.md`](current_mod/README.md)).
- 🎭 [`tools/open-goal-glb-reskin-tool/`](tools/open-goal-glb-reskin-tool/): GUI application for retargeting and reskinning GLB characters.
- 🗺️ [`tools/open-goal-level-builder/`](tools/open-goal-level-builder/): GUI application for building custom OpenGOAL levels.

---

# 🇫🇷 Version Française

Ce répertoire centralise l'ensemble des guides de référence officiels, workflows d'ingénierie, manuels d'outils et tableaux de bord de synchronisation pour le modding de Jak 1, Jak 2 et Jak 3 avec OpenGOAL.

---

## 1. Références Fondamentales (À Consulter Avant de Coder)

Ces documents validés constituent la **source unique de vérité** hébergée sur `master-dev`. Ils évitent toute hallucination en fournissant des exemples testés et des pièges répertoriés.

| Document de Référence | Portée | Contenu |
| :--- | :--- | :--- |
| 📗 [`jak1_lisp_instructions.md`](jak1_lisp_instructions.md) | Jak 1 | Syntaxe LISP OpenGOAL vérifiée, états et fonctions d'entités pour Jak 1. |
| 📗 [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) | Jak 2 | Instructions LISP vérifiées, hooks de combat et méthodes d'entités pour Jak 2. |
| 📗 [`jak3_lisp_instructions.md`](jak3_lisp_instructions.md) | Jak 3 | Instructions LISP vérifiées, hooks de véhicules et types d'armes pour Jak 3. |
| 📘 [`engine_generic_concepts.md`](engine_generic_concepts.md) | Tous jeux | Heaps mémoire (`global`, `level`, `debug`, `process`), simulation RAM PS2 `mmap`, DGOs et cycle de vie. |

> **Règle d'Intégration Sans Conflit :**
> Ne modifiez jamais les documents de référence directement sur une branche de mod. Utilisez :
> ```bash
> task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
> task modding-sync-docs
> ```

---

## 2. Directives des Agents & Compétences Modulaires

- **[Guide Unifié des Agents (`AGENTS.md`)](../../AGENTS.md)** : Règles, référence des commandes Taskfile, cycle de rechargement à chaud REPL, et règles de branches Git.
- **[Bibliothèque Dynamique des Compétences (`.agents/skills/`)](../../.agents/skills/)** :
  - [`goal-lisp`](../../.agents/skills/goal-lisp/SKILL.md) & [`discoveries.md`](../../.agents/skills/goal-lisp/discoveries.md)
  - [`engine-internals`](../../.agents/skills/engine-internals/SKILL.md) & [`repl-workflow.md`](../../.agents/skills/engine-internals/repl-workflow.md)
  - [`custom-actors-levels`](../../.agents/skills/custom-actors-levels/SKILL.md) & [`discoveries.md`](../../.agents/skills/custom-actors-levels/discoveries.md)
  - [`texture-modding`](../../.agents/skills/texture-modding/SKILL.md) & [`discoveries.md`](../../.agents/skills/texture-modding/discoveries.md)

---

## 3. Guides d'Ingénierie & de Workflows

| Guide | Description |
| :--- | :--- |
| 🤖 [`tools/github_workflows.md`](tools/github_workflows.md) | Guide pédagogique complet des 5 workflows GitHub Actions (synchronisation amont, santé des branches, releases, triage automatique). |
| 🛠️ [`tools/task_scripts_reference.md`](tools/task_scripts_reference.md) | Référence pédagogique de l'ensemble des commandes Taskfile et scripts Python de modding (`scripts/modding/*.py`). |
| 🚀 [`custom_entity_workflow.md`](custom_entity_workflow.md) | Guide d'ingénierie sur l'importation de modèles 3D, animations personnalisées et banques de sons (`.SBK`) avec étude de cas `og-j1-board`. |
| ⚡ [`tools/build_and_iteration_workflow.md`](tools/build_and_iteration_workflow.md) | Modèle de compilation en 3 couches, accélération `sccache` et tâches ciblées (`build-release-game`, `build-release-decomp`). |
| 🎨 [`tools/model_and_entity_level_injection_guide.md`](tools/model_and_entity_level_injection_guide.md) | Pipeline d'injection Merc `.fr3` sans borrow (`extra_art_groups_by_dgo`) pour injecter des modèles dans n'importe quel niveau. |
| 🎛️ [`tools/mods_menu.md`](tools/mods_menu.md) | Enregistrement des fonctionnalités dans le menu Mods en jeu (L3 + SELECT en boot retail) via `(mods-menu-register "<slug>" builder)`. |
| 📦 [`tools/mod_distribution_guide.md`](tools/mod_distribution_guide.md) | Guide complet de packaging, releases automatisées, catalogue launcher (`index.json`) et miniatures de couverture. |
| 🎮 [`how_to_install_mod.md`](how_to_install_mod.md) | Tutoriel joueur : ajouter l'URL catalogue `index.json` dans le Launcher, installer le mod et l'activer en jeu (L3 + SELECT). |
| 🐛 [`tools/mod_bug_tracking.md`](tools/mod_bug_tracking.md) | Formulaire de signalement de bugs, labellisation automatique et boucle de résolution (`Fixes #123`). |

---

## 4. Règle Obligatoire : Enregistrement dans le Menu « Mods » (`mods-menu-register`)

> [!IMPORTANT]
> Tout nouveau mod créé sur ce dépôt — **en particulier pour les branches de type `features/*` (`jak[x]/features/*`)** — **DOIT être activable en jeu** via le registre unifié :
> ```lisp
> (mods-menu-register "<mod-slug>" <builder-function>)
> ```
> - **Compatibilité Boot Retail :** L'OpenGOAL Launcher démarre le jeu en mode retail (`-boot -fakeiso`), ce qui désactive le menu debug. Le menu Mods s'ouvre avec **L3 + SELECT** dans les deux modes (Jak 2 et Jak 3).
> - **Non-Régression Native :** Chaque fonctionnalité doit être **désactivée par défaut (`#f`)** et activable à la demande du joueur depuis ce menu.
> - **Ressources :** Consultez le guide [`tools/mods_menu.md`](tools/mods_menu.md) et le template [`templates/mod_menu.template.gc`](templates/mod_menu.template.gc).

---

## 5. Tableaux de Bord & Conformité des Branches

- 📊 [`tools/branch_sync_status.md`](tools/branch_sync_status.md) : Tableau de bord de fusion en direct pour toutes les branches de mods (`task modding-branch-status`). **Réservé à `master-dev`**.
- 📜 [`tools/branch_sync_history.md`](tools/branch_sync_history.md) : Journal historique des fusions automatiques et résolutions de conflits.
- 📋 [`branch_audit.md`](branch_audit.md) : Rapport d'audit de conformité par rapport aux standards du projet (`task modding-audit`).

---

## 6. Modèles & Outils de Modding Autonomes

- 📝 [`templates/MOD_README.template.md`](templates/MOD_README.template.md) : Modèle de présentation bilingue pour le `README.md` racine des branches de mods.
- ⚙️ [`templates/mod_menu.template.gc`](templates/mod_menu.template.gc) : Modèle GOAL prêt à l'emploi pour l'enregistrement au menu Mods en jeu.
- 📂 [`current_mod/`](current_mod/) : Dossier hébergeant les documentations techniques propres à un mod ([`current_mod/README.md`](current_mod/README.md)).
- 🎭 [`tools/open-goal-glb-reskin-tool/`](tools/open-goal-glb-reskin-tool/) : Application graphique pour retargeting et reskin de personnages GLB.
- 🗺️ [`tools/open-goal-level-builder/`](tools/open-goal-level-builder/) : Outil graphique pour concevoir des niveaux OpenGOAL sur mesure.
