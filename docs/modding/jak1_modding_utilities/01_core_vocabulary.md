# Jak 1 — Core Vocabulary / Vocabulaire de Base

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Core Concepts & Vocabulary

| Term | Definition & Role in Jak 1 |
|---|---|
| **GOAL** | Naughty Dog's proprietary Lisp dialect compiled to native x86-64 by OpenGOAL. |
| **`process-drawable`** | Base type for any interactive world entity featuring a 3D model and transformation hierarchy (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Symbolic name representing the player process (Jak). Globally accessible via `*target*`. |
| **`state`** | State machine node containing event handlers, execution loop (`:code`), and post-processing (`:post`). |
| **`DGO`** | Data Group Object archive packaging compiled objects (`.o`) loaded together into RAM during level streaming. |

---

# 🇫🇷 Version Française

## Vocabulaire & Concepts Clés

| Terme | Définition & Rôle dans Jak 1 |
|---|---|
| **GOAL** | Langage Lisp propriétaire de Naughty Dog compilé en x86-64 par OpenGOAL. |
| **`process-drawable`** | Type de base pour toute entité du monde disposant d'un modèle 3D / affichage (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Nom symbolique du process représentant le joueur (Jak). Accessible globalement via le symbole `*target*`. |
| **`state`** | Objet représentant un état de machine d'état (ex: `target-running`, `target-jump`). Contient des handlers d'événements, code d'exécution et post-processing. |
| **`DGO`** | Fichier archive regroupant les objets compilés (`.o`) chargés en mémoire lors du chargement des niveaux. |
