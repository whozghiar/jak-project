# OpenGOAL — Project Overview / Vue d'ensemble du Projet

> **Language / Langue :** [🇬🇧 English Version](#-english-version) &nbsp;•&nbsp; [🇫🇷 Version Française](#-version-française)

---

## 📑 Summary / Sommaire
- [🇬🇧 English Version](#-english-version)
  - [1. `goalc` (Compiler & REPL)](#1-goalc-compiler--repl)
  - [2. `decompiler` (Asset & Code Extraction)](#2-decompiler-asset--code-extraction)
  - [3. `goal_src/` (Game Source Code)](#3-goal_src-game-source-code)
  - [4. `game` runtime (C++ Engine & Kernel)](#4-game-runtime-c-engine--kernel)
- [🇫🇷 Version Française](#-version-française)
  - [1. `goalc` (Compilateur et REPL)](#1-goalc-compilateur-et-repl)
  - [2. `decompiler` (Extraction des Assets et du Code)](#2-decompiler-extraction-des-assets-et-du-code)
  - [3. `goal_src/` (Code Source du Jeu)](#3-goal_src-code-source-du-jeu)
  - [4. `game` runtime (Moteur C++ et Kernel)](#4-game-runtime-moteur-c-et-kernel)

---

# 🇬🇧 English Version

There are four main components to the project:

1. `goalc` — the GOAL compiler for x86-64 and interactive REPL.
2. `decompiler` — our decompiler for extracting retail game assets and code.
3. `goal_src/` — the directory containing all OpenGOAL / GOOS source code.
4. `game` — the C++ game runtime kernel simulating PS2 Emotion Engine RAM.

Let's break down each component.

---

## 1. `goalc` (Compiler & REPL)

Our implementation of GOAL is called **OpenGOAL**.

All of the compiler source code is located in `goalc/`. The compiler is controlled through an interactive prompt which can be used to:
- Enter commands to compile `.gc` source files.
- Connect to a running GOAL program for live interaction.
- Run the OpenGOAL debugger.
- Act as an interactive REPL (`(mi)`, etc.) to evaluate code on the fly in the running game memory.
- Pack and build binary data files.

### Running the Compiler

- **Environment Agnostic (Recommended):**
  If you have installed `task`, run:
  ```bash
  task repl
  ```
- **Linux:**
  Run the script: `scripts/shell/gc.sh`
- **Windows:**
  Run `scripts/batch/gc.bat` or `scripts/batch/gc-no-lt.bat` (the latter does not attempt to automatically attach to a running target).

---

## 2. `decompiler` (Asset & Code Extraction)

The second component of the project is the decompiler.

The decompiler outputs disassemblies, types, and human-readable GOAL source code in the `decompiler_out/` directory. Files in this folder are intended for inspection and are not directly consumed by the compiler.

### Running the Decompiler

You must possess a legitimate retail copy of the PS2 game and place all files from the DVD inside the corresponding folder within `iso_data/` (`jak1` for Jak 1 Black Label, `jak2`, `jak3`), as shown below:

![](./img/iso_data-help.png)

The decompiler extracts assets to the `assets/` folder. These assets will be used by the compiler when building the native port:
- **Environment Agnostic (Recommended):**
  ```bash
  task extract
  ```
  *(or `task decomp` for decompilation only)*
- **Linux:**
  `scripts/shell/decomp.sh`
- **Windows:**
  `scripts/batch/decomp-jak1.bat`

---

## 3. `goal_src/` (Game Source Code)

The game source code, written in OpenGOAL LISP, is located in `goal_src/`. All GOAL and GOOS code is organized by game:
- `goal_src/jak1/`
- `goal_src/jak2/`
- `goal_src/jak3/`

---

## 4. `game` runtime (C++ Engine & Kernel)

The final component is the **runtime**, located in `game/`. This is the native x86-64 executable written in C++ that emulates PS2 hardware structures and provides the environment for GOAL code to execute.

In the port, this includes:
- **The C Kernel (`game/kernel/`):** Contains the GOAL linker, memory heap allocators (`global`, `debug`), symbol table, type system, and low-level kernel dispatcher. It also handles TCP communication with the `goalc` compiler.
- **Sony Standard Library (`game/sce/`, `game/system/`):** Implements or stubs Sony PS2 SDK functions for file access, memory cards, controllers, and threading.
- **OVERLORD IOP Driver (`game/overlord/`):** The PS2 had a dedicated I/O Processor (IOP). Naughty Dog authored an IOP driver called OVERLORD for asynchronous DVD streaming and sound loading.
- **Sound Engine (`game/sound/`):** Implementation of Sony's `989SND` library and PC audio output backends (Cubeb).
- **PC Graphics Renderer (`game/graphics/`):** An OpenGL 4.3 pipeline that translates PS2 GS (Graphics Synthesizer) draw calls into modern PC shaders and render passes (TFRAG, TIE, MERC, SHRUB, etc.).
- **Extra Assets (`game/assets/`):** Supplemental PC port assets, icons, fonts, and configuration files.

---
---

# 🇫🇷 Version Française

Le projet s'articule autour de quatre composants fondamentaux :

1. `goalc` — le compilateur GOAL pour x86-64 et REPL interactif.
2. `decompiler` — notre décompilateur pour extraire les assets et le code des disques PS2 originaux.
3. `goal_src/` — le dossier contenant l'ensemble du code source GOAL et GOOS.
4. `game` — le moteur d'exécution (runtime) natif écrit en C++ simulant la RAM de la PS2.

Voici une description détaillée de chaque composant.

---

## 1. `goalc` (Compilateur et REPL)

Notre implémentation du langage GOAL s'appelle **OpenGOAL**.

L'intégralité du code source du compilateur se trouve dans `goalc/`. Le compilateur est piloté via une invite de commande interactive permettant de :
- Compiler des fichiers source `.gc`.
- Se connecter à une instance de jeu en cours d'exécution pour interagir en direct.
- Lancer le débogueur OpenGOAL.
- Utiliser un REPL interactif (`(mi)`, etc.) afin d'évaluer du code à la volée dans la mémoire vive du jeu.
- Empaqueter et compiler les fichiers de données binaires (DGO, tpages, etc.).

### Lancer le Compilateur

- **Multiplateforme (Recommandé) :**
  Si `task` est installé, exécutez :
  ```bash
  task repl
  ```
- **Linux :**
  Exécutez le script : `scripts/shell/gc.sh`
- **Windows :**
  Exécutez `scripts/batch/gc.bat` ou `scripts/batch/gc-no-lt.bat` (ce dernier ne tente pas de se connecter automatiquement à une cible active).

---

## 2. `decompiler` (Extraction des Assets et du Code)

Le second composant du projet est le décompilateur.

Le décompilateur génère du désassemblage, des définitions de types et du code source GOAL lisible dans le dossier `decompiler_out/`. Les fichiers de ce dossier sont destinés à l'inspection humaine et ne sont pas directement utilisés par le compilateur.

### Lancer le Décompilateur

Vous devez posséder une copie légale du jeu PS2 et placer l'ensemble des fichiers du DVD dans le sous-dossier correspondant sous `iso_data/` (`jak1` pour Jak 1 Black Label, `jak2`, `jak3`), comme illustré ici :

![](./img/iso_data-help.png)

Le décompilateur extrait les assets dans le dossier `assets/`. Ces assets sont indispensables au compilateur pour générer le portage PC :
- **Multiplateforme (Recommandé) :**
  ```bash
  task extract
  ```
  *(ou `task decomp` pour décompiler sans réextraire)*
- **Linux :**
  `scripts/shell/decomp.sh`
- **Windows :**
  `scripts/batch/decomp-jak1.bat`

---

## 3. `goal_src/` (Code Source du Jeu)

Le code source du jeu, écrit en OpenGOAL LISP, est situé dans `goal_src/`. Tout le code GOAL et GOOS est organisé par jeu :
- `goal_src/jak1/`
- `goal_src/jak2/`
- `goal_src/jak3/`

---

## 4. `game` runtime (Moteur C++ et Kernel)

Le dernier composant est le **runtime**, situé dans le répertoire `game/`. Il s'agit de l'exécutable natif x86-64 écrit en C++ qui simule les structures matérielles de la PS2 et fournit l'environnement d'exécution pour le code GOAL.

Dans le cadre du portage, cela comprend :
- **Le Kernel C (`game/kernel/`) :** Contient l'éditeur de liens (linker) GOAL, les gestionnaires de mémoire tas (`global`, `debug`), la table des symboles, le système de types et le répartiteur du noyau. Il gère également la communication TCP avec le compilateur `goalc`.
- **Bibliothèque standard Sony (`game/sce/`, `game/system/`) :** Implémente ou émule les fonctions du SDK Sony PS2 pour la lecture de fichiers, les cartes mémoire, les manettes et le multithreading.
- **Pilote OVERLORD pour IOP (`game/overlord/`) :** La PS2 disposait d'un processeur dédié aux E/S (IOP). Naughty Dog a développé le pilote OVERLORD pour assurer le streaming asynchrone des données du DVD et le chargement audio.
- **Moteur Sonore (`game/sound/`) :** Implémentation de la bibliothèque Sony `989SND` et backends audio PC (Cubeb).
- **Moteur Graphique PC (`game/graphics/`) :** Un pipeline moderne OpenGL 4.3 convertissant les commandes d'affichage du GS (Graphics Synthesizer) de la PS2 en shaders et passes de rendu modernes (TFRAG, TIE, MERC, SHRUB, etc.).
- **Ressources Additionnelles (`game/assets/`) :** Fichiers de configuration, icônes, polices et assets spécifiques au portage PC.
