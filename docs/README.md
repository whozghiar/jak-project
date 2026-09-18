# OpenGOAL Documentation Hub / Centre de Documentation OpenGOAL

> **Bilingual Documentation Portal / Portail de Documentation Bilingue**
>
> - **Scope / Portée :** Documentation Architecture, Engine Setup & Modding Hub
> - **Source of Truth / Source de Vérité :** `master-dev`

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Structure Overview](#1-structure-overview) · [2. Key Entry Points](#2-key-entry-points) · [3. Environment & Toolchain](#3-environment--toolchain-setup) · [4. Engine Architecture & Historical Notes](#4-engine-architecture--historical-notes)
> - 🇫🇷 **Français :** [1. Organisation des Dossiers](#1-organisation-des-dossiers) · [2. Points d'Accès Principaux](#2-points-daccès-principaux) · [3. Environnement & Outils](#3-environnement--outils-de-développement) · [4. Architecture Moteur & Notes Historiques](#4-architecture-moteur--notes-historiques)

---

# 🇬🇧 English Version

Welcome to the documentation tree for the OpenGOAL project and modding framework (`jak-project`).

## 1. Structure Overview

```text
docs/
├── modding/                # Complete modding documentation, verified references & tool guides
├── setup/                  # Environment, toolchain & IDE setup (VSCode, VS, Linux, Windows, macOS)
├── progress-notes/         # Upstream decompilation logs, assembly notes & reverse-engineering records
├── scratch/                # Upstream developer scratchpad and temporary notes
└── project-overview.md     # Architecture overview of OpenGOAL compiler, runtime & decompiler
```

---

## 2. Key Entry Points

### Modding & AI-Assisted Development
- 🛠️ **[Modding Documentation Hub (`docs/modding/`)](modding/README.md)**: Verified Lisp instructions (`jak[1|2|3]_lisp_instructions.md`), generic engine primer (`engine_generic_concepts.md`), and entity workflows.
- 🤖 **[AI Agent & Developer Guide (`AGENTS.md`)](../AGENTS.md)**: Central rules, Taskfile command reference, REPL hot-reload cycle, ghost memory verification, and git branching standards.
- 🤖 **[GitHub Actions Workflows Guide](modding/tools/github_workflows.md)**: Detailed pedagogical guide to repository CI/CD, upstream synchronization, releases, and issue triaging.
- 🛠️ **[Task Commands & Modding Scripts Reference](modding/tools/task_scripts_reference.md)**: Pedagogical reference for all Taskfile commands and `scripts/modding/*.py` automations.
- 🧠 **[Modular Skills (`.agents/skills/`)](../.agents/skills/)**: High-density engineering skills loaded on demand:
  - [`goal-lisp`](../.agents/skills/goal-lisp/SKILL.md): GOAL syntax, state machines, types & macros.
  - [`engine-internals`](../.agents/skills/engine-internals/SKILL.md): C++ runtime, heaps & REPL workflow.
  - [`custom-actors-levels`](../.agents/skills/custom-actors-levels/SKILL.md): 3D models, Blender `.glb` exports, armatures & levels.
  - [`texture-modding`](../.agents/skills/texture-modding/SKILL.md): Custom texture injection & replacement.

---

## 3. Environment & Toolchain Setup

- 💻 **[Setup Guides (`docs/setup/`)](setup/)**:
  - **Operating Systems:** [Windows](setup/system/windows.md) · [Linux](setup/system/linux.md) · [macOS](setup/system/macos.md) · [Docker](setup/system/docker.md)
  - **IDEs & Editors:** [VSCode](setup/dev/vscode.md) · [Visual Studio](setup/dev/vs.md) · [Zed](setup/dev/zed.md)

---

## 4. Engine Architecture & Historical Notes

- 📖 **[Project Overview (`docs/project-overview.md`)](project-overview.md)**: Upstream architecture and component roles.
- 🔬 **[Progress Notes (`docs/progress-notes/`)](progress-notes/)**: Decompilation notes, bone systems, joint decompression, and VU assembly documentation.

---

# 🇫🇷 Version Française

Bienvenue dans l'arborescence de documentation du projet OpenGOAL et de son environnement de modding (`jak-project`).

## 1. Organisation des Dossiers

```text
docs/
├── modding/                # Documentation complète de modding, références vérifiées & guides d'outils
├── setup/                  # Configuration environnement, compilateurs & IDE (VSCode, VS, Linux, Windows, macOS)
├── progress-notes/         # Journaux de décompilation amont, notes assembleur & ingénierie inverse
├── scratch/                # Brouillons et notes temporaires des développeurs amont
└── project-overview.md     # Vue d'ensemble architecturale du compilateur, runtime et décompilateur OpenGOAL
```

---

## 2. Points d'Accès Principaux

### Modding & Développement Assisté par IA
- 🛠️ **[Hub de Documentation du Modding (`docs/modding/`)](modding/README.md)** : Références LISP vérifiées (`jak[1|2|3]_lisp_instructions.md`), guide d'initiation au moteur (`engine_generic_concepts.md`), et workflows d'entités custom.
- 🤖 **[Guide Unifié des Agents & Développeurs (`AGENTS.md`)](../AGENTS.md)** : Règles absolues, référence des commandes Taskfile, cycle de rechargement à chaud REPL, et règles de branches Git.
- 🤖 **[Guide des Workflows GitHub Actions](modding/tools/github_workflows.md)** : Guide pédagogique complet sur la CI/CD du dépôt, synchronisation amont, packaging des releases et triage automatique des bugs.
- 🛠️ **[Référence des Commandes Task & Scripts](modding/tools/task_scripts_reference.md)** : Guide pédagogique détaillé de toutes les tâches `Taskfile.yml` et scripts `scripts/modding/*.py`.
- 🧠 **[Compétences Modulaires (`.agents/skills/`)](../.agents/skills/)** : Savoirs d'ingénierie chargés à la demande :
  - [`goal-lisp`](../.agents/skills/goal-lisp/SKILL.md) : Syntaxe GOAL, machines à états, types et macros.
  - [`engine-internals`](../.agents/skills/engine-internals/SKILL.md) : Runtime C++, heaps et workflow REPL.
  - [`custom-actors-levels`](../.agents/skills/custom-actors-levels/SKILL.md) : Modèles 3D, exports Blender `.glb`, armatures et niveaux.
  - [`texture-modding`](../.agents/skills/texture-modding/SKILL.md) : Injection et remplacement de textures.

---

## 3. Environnement & Outils de Développement

- 💻 **[Guides d'Installation (`docs/setup/`)](setup/)** :
  - **Systèmes d'exploitation :** [Windows](setup/system/windows.md) · [Linux](setup/system/linux.md) · [macOS](setup/system/macos.md) · [Docker](setup/system/docker.md)
  - **IDE & Éditeurs :** [VSCode](setup/dev/vscode.md) · [Visual Studio](setup/dev/vs.md) · [Zed](setup/dev/zed.md)

---

## 4. Architecture Moteur & Notes Historiques

- 📖 **[Aperçu du Projet (`docs/project-overview.md`)](project-overview.md)** : Rôle et architecture des composants amont.
- 🔬 **[Notes de Décompilation (`docs/progress-notes/`)](progress-notes/)** : Historique de décompilation, systèmes d'os, décompression d'articulations et assembleur VU.
