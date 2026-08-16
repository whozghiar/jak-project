# Jak 2 — Core Vocabulary / Vocabulaire de Base

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/config/memory_increase`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Core Concepts & Vocabulary

| Term | Meaning |
|---|---|
| **EE** | "Emotion Engine", the main PS2 CPU. The PC port emulates its main memory by reserving a contiguous block via `mmap` (see `game/runtime.cpp`). |
| **GOAL** | The custom Lisp/Scheme dialect in which all original Naughty Dog game code is written (`goal_src/**/*.gc`). Compiled by **OpenGOAL**. |
| **`goalc`** | The OpenGOAL compiler executable. Runs in interactive REPL mode (`task repl`) or batch mode (`-c "(command)"`). |
| **`gk`** | The C++ runtime executable ("game kernel") that loads and executes compiled GOAL code. |
| **DGO** | "Data Group Object" — a package bundling compiled GOAL objects (code + data) loaded together from disk. |
| **Heap** | A memory arena allocated in bulk, within which GOAL dynamically allocates its own objects. |
| **`valid?`** | GOAL function in `gcommon.gc` checking pointer alignment and address boundaries before dereferencing. |

---

# 🇫🇷 Version Française

## Vocabulaire & Concepts Fondamentaux

| Terme | Signification & Rôle |
|---|---|
| **EE** | "Emotion Engine", le processeur principal de la PS2. Le port PC émule sa mémoire en réservant un bloc contigu via `mmap` (voir `game/runtime.cpp`). |
| **GOAL** | Le dialecte Lisp/Scheme propriétaire dans lequel tout le code de Naughty Dog est écrit (`goal_src/**/*.gc`). Compilé par **OpenGOAL**. |
| **`goalc`** | Le compilateur OpenGOAL. S'utilise en REPL interactif (`task repl`) ou en mode batch (`-c "(command)"`). |
| **`gk`** | L'exécutable C++ ("game kernel") qui charge et exécute le code GOAL compilé. |
| **DGO** | "Data Group Object" — archive regroupant du code et des assets GOAL compilés, chargés d'un bloc depuis le disque. |
| **Heap** | Un espace mémoire alloué en bloc, dans lequel GOAL alloue dynamiquement ses propres objets. |
| **`valid?`** | Fonction GOAL dans `gcommon.gc` vérifiant l'alignement et les bornes d'un pointeur avant déréférencement. |
