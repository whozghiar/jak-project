# Jak 3 — Modding Notes & Engine Utilities / Notes de Modding & Utilitaires Moteur

> **Bilingual Knowledge Base / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Table of Contents
- [1. Core Vocabulary](#1-core-vocabulary)
- [2. Memory Architecture & Constants](#2-memory-architecture-constants)
- [3. Weapons, Vehicles & Entities](#3-weapons-vehicles-entities)
- [4. Processes, States & Behaviors](#4-processes-states-behaviors)
- [5. Skeleton, Joints & Animations](#5-skeleton-joints-animations)
- [6. Declaring Scripts in Project File (`.gp`)](#6-declaring-scripts-in-project-file-gp)
- [7. Compilation & Validation Workflow](#7-compilation-validation-workflow)
- [8. Known Pitfalls & Best Practices](#8-known-pitfalls-best-practices)

---

### 1. Core Vocabulary

> **Origin / Provenance:** `master`

| Term | Definition & Role in Jak 3 |
|---|---|
| **GOAL** | Naughty Dog's proprietary Lisp dialect compiled to native x86-64 by OpenGOAL. |
| **`gun-info`** | Structure managing Jak 3's modular arsenal (Morph-Gun and 12 weapon forms). |
| **`vehicle` / `hvehicle`** | Base object types for desert off-road vehicles and hovering city craft. |
| **`light-jak` / `dark-jak`** | State subsystems governing Jak's eco powers and special forms. |
| **`target`** | Process representing the active player (`*target*`). |

---

---

### 2. Memory Architecture & Constants

> **Origin / Provenance:** `master`

* **Kernel Entry Point:** `goal_src/jak3/kernel/gcommon.gc` and `goal_src/jak3/engine/level/level.gc`.
* **Memory Budget (PC Extension):**
  - `END_OF_MEMORY`: configured to support 512 MB (`#x20000000`).
  - `DEBUG_LEVEL_HEAP_MULT`: level heap size multiplier in `level.gc` (default value: `15.0`).
* **Shared C++ Memory:** `EE_MAIN_MEM_SIZE` is shared in `common/goal_constants.h`.

---

---

### 3. Weapons, Vehicles & Entities

> **Origin / Provenance:** `master`

### Weapon System (`gun`)
Weapon properties, ammo counts, and projectile configurations are accessed through the target process:
```lisp
(when *target*
  (let ((gun (-> *target* gun)))
    ;; Access weapon firing modes, ammo counts, morph attachments
    ))
```

### Vehicles & Physics
* Wasteland buggy and vehicle actors derive from `vehicle` (`goal_src/jak3/engine/vehicle/`).
* Dynamic suspension, tire friction, and torque resolution execute every tick via specialized behavior routines.

---

---

### 4. Processes, States & Behaviors

> **Origin / Provenance:** `master`

Standard focusable actor structure in Jak 3:
```lisp
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag  uint32)
   (energy-level      float))
  (:state-methods
    idle
    patrol
    die)
  )
```

---

---

### 5. Skeleton, Joints & Animations

> **Origin / Provenance:** `master`

* **Animation Pipeline:** Managed by `merc` / `mips2c` for skinning and skeletal evaluations.
* **Direct Joint Transform Access:** Joint transformation matrices can be read and manipulated via `(-> self node-list data [index] bone transform)`.
* **Animation Scrubbing:**
  ```lisp
  (ja :num! (seek!))
  (suspend)
  ```

---

---

### 6. Declaring Scripts in Project File (`.gp`)

> **Origin / Provenance:** `master`

To add a new `.gc` script to the Jak 3 build tree:
1. Locate the configuration `.gp` file (e.g. `goal_src/jak3/jak3-game.gp`).
2. Add the path to the new script:
   ```
   (c "custom/my-jak3-mod.gc")
   ```
3. Recompile in the REPL with `(mi)`.

---

---

### 7. Compilation & Validation Workflow

> **Origin / Provenance:** `master`

1. **Select Jak 3:**
   ```bash
   task set-game-jak3
   ```
2. **Compile Code in OpenGOAL REPL (`task repl`):**
   ```lisp
   (mi)
   ```
3. **Launch the Game:**
   ```bash
   task boot-game
   ```

---

---

### 8. Known Pitfalls & Best Practices

> **Origin / Provenance:** `master`

* **Complex Interplay Between Powers and Weapons:** Modifying `*target*` states can disrupt weapon transitions (`gun-states`) and powers (`light-jak` / `dark-jak`).
* **Git Synchronization:** Always merge verified additions from these files back to the `master` branch.

---

---

# 🇫🇷 Version Française

## Sommaire
- [1. Vocabulaire de Base](#1-vocabulaire-de-base)
- [2. Architecture Mémoire & Constantes](#2-architecture-mémoire-constantes)
- [3. Armes, Véhicules & Entités](#3-armes-véhicules-entités)
- [4. Processus, États & Comportements](#4-processus-états-comportements)
- [5. Squelette, Joints & Animations](#5-squelette-joints-animations)
- [6. Déclarer un Script (`.gp`)](#6-déclarer-un-script-gp)
- [7. Workflow de Compilation & Validation](#7-workflow-de-compilation-validation)
- [8. Pièges Connus & Bonnes Pratiques](#8-pièges-connus-bonnes-pratiques)

---

### 1. Vocabulaire de Base

> **Origin / Provenance :** `master`

| Terme | Définition & Rôle dans Jak 3 |
|---|---|
| **GOAL** | Langage Lisp propriétaire de Naughty Dog compilé en x86-64 par OpenGOAL. |
| **`gun-info`** | Structure gérant l'arsenal modulable de Jak 3 (morph-gun et 12 formes d'armes). |
| **`vehicle` / `hvehicle`** | Types de base pour les véhicules tout-terrain du désert et les véhicules urbains flottants. |
| **`light-jak` / `dark-jak`** | Sous-systèmes d'états gérant les capacités et pouvoirs de Jak. |
| **`target`** | Processus représentant le joueur (`*target*`). |

---

### 2. Architecture Mémoire & Constantes

> **Origin / Provenance :** `master`

* **Point d'Entrée Kernel :** `goal_src/jak3/kernel/gcommon.gc` et `goal_src/jak3/engine/level/level.gc`.
* **Budget Mémoire (Extension PC) :**
  - `END_OF_MEMORY` : configuré pour supporter 512 Mo (`#x20000000`).
  - `DEBUG_LEVEL_HEAP_MULT` : multiplicateur de taille du heap de niveau dans `level.gc` (valeur native : `15.0`).
* **Mémoire C++ Partagée :** `EE_MAIN_MEM_SIZE` est partagé dans `common/goal_constants.h`.

---

### 3. Armes, Véhicules & Entités

> **Origin / Provenance :** `master`

### Système d'Armes (`gun`)
L'état de l'arme, les munitions et le morphing s'interrogent via le processus joueur :
```lisp
(when *target*
  (let ((gun (-> *target* gun)))
    ;; Accès aux propriétés de tir, munitions, type d'arme
    ))
```

### Véhicules & Physique
* Les véhicules du désert dérivent de la hiérarchie `vehicle` (`goal_src/jak3/engine/vehicle/`).
* Les forces de suspension, frottement et adhérence sont résolues à chaque cycle via des behaviors dédiés.

---

### 4. Processus, États & Comportements

> **Origin / Provenance :** `master`

Structure standard d'un acteur focusable dans Jak 3 :
```lisp
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag  uint32)
   (energy-level      float))
  (:state-methods
    idle
    patrol
    die)
  )
```

---

### 5. Squelette, Joints & Animations

> **Origin / Provenance :** `master`

* **Moteur d'Animation :** Système `merc` / `mips2c` pour le calcul squelettique et le rendu.
* **Accès Direct aux Joints :** Les matrices de transformation sont accessibles via `(-> self node-list data [index] bone transform)`.
* **Avancement de l'Animation :**
  ```lisp
  (ja :num! (seek!))
  (suspend)
  ```

---

### 6. Déclarer un Script (`.gp`)

> **Origin / Provenance :** `master`

Pour ajouter un nouveau fichier `.gc` dans l'arbre de compilation de Jak 3 :
1. Localiser le fichier `.gp` de configuration (ex: `goal_src/jak3/jak3-game.gp`).
2. Ajouter le chemin vers le nouveau script :
   ```
   (c "custom/my-jak3-mod.gc")
   ```
3. Recompiler dans le REPL avec `(mi)`.

---

### 7. Workflow de Compilation & Validation

> **Origin / Provenance :** `master`

1. **Sélectionner Jak 3 :**
   ```bash
   task set-game-jak3
   ```
2. **Compiler dans le REPL OpenGOAL (`task repl`) :**
   ```lisp
   (mi)
   ```
3. **Lancer le Jeu :**
   ```bash
   task boot-game
   ```

---

### 8. Pièges Connus & Bonnes Pratiques

> **Origin / Provenance :** `master`

* **Interactions Complexes Entre Pouvoirs et Armes :** Modifier les états de `*target*` peut affecter les transitions d'armes (`gun-states`) et de pouvoirs (`light-jak` / `dark-jak`).
* **Synchronisation Git :** Penser à merger régulièrement les ajouts factuels de ce fichier vers la branche `master`.

---
