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
- [9. Architecture: Dark Jak Stages & Legacy Assets](#9-architecture-dark-jak-stages-legacy-assets)
- [10. Architecture: Secrets Menu System (`game-secrets`)](#10-architecture-secrets-menu-system-game-secrets)

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

### 9. Architecture: Dark Jak Stages & Legacy Assets

> **Origin / Provenance:** `master`

* **Bitmask Flags:** Dark Jak capabilities are driven by the `darkjak-stage` bitfield enum in `target-h.gc` and stored in `(-> self darkjak stage)` and `(-> self darkjak want-stage)`:
  - `active`: Base Dark Jak form.
  - `bomb0` / `bomb1`: Dark Bomb and Dark Blast abilities.
  - `invinc`: Invulnerability stage.
  - `invis`: Invisibility modifier (suppresses offensive stages).
  - `tracking`: Target tracking mode.
  - `smack`: Dark Strike attack mode.
  - `giant`: Scaling stage flag.

## 2. Transformation Checks & Mod Surfaces
* **Trigger Conditions:** `want-to-darkjak?` and `want-to-powerjak?` in `target-darkjak.gc` / `target-lightjak.gc` validate:
  - Game features flag `(game-feature darkjak)` in `*setting-control*`.
  - Focus tests (cannot transform while swimming underwater, piloting, carrying, etc.).
  - Timing delays via `(-> self fact darkjak-start-time)`.
* **Surface Modifiers:** Transformed movement is governed by `*darkjak-trans-mods*` surface parameters.

## 3. Legacy Jak 2 Giant State Assets
* **Unused Animation & Scale Hooks:** The Jak 3 engine retains full animation data for `jakb-darkjak-get-on-fast-ja` as well as scaling interpolation variables (`(-> self darkjak-giant-interp)`) originally used for the Jak 2 Dark Giant transformation.

---

---

### 10. Architecture: Secrets Menu System (`game-secrets`)

> **Origin / Provenance:** `master`

* **Bitfield Enum:** Secrets and cheats in Jak 3 are tracked through the `game-secrets` bitfield declared in `settings-h.gc`.
* **State Persistence:** Active secrets are saved in the game state within `(-> *game-info* secrets)` and can be checked using `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

## 2. Secrets Menu Structure (`secrets-menu.gc`)
* **Menu Entries:** Purchasable and toggleable items are registered inside static arrays such as `*menu-secrets-array*` using `secret-item-option` instances.
* **Key Fields:**
  - `:name`: `text-id` specifying the localization string ID.
  - `:cost`: Orb cost required to unlock (`0` allows free activation).
  - `:secret`: Corresponding bit flag from the `game-secrets` enum.
  - `:avail-after`: `game-task-node` prerequisite determining when the item appears in the menu.
  - `:flags`: Behavior attributes (e.g. `(secret-item-option-flags sf1)`).

## 3. UI Label Resolution (`progress-draw-pc.gc`)
* **Custom & Unlocalized Names:** When adding or overriding secrets that lack dedicated strings in the text database, label strings are mapped dynamically during option rendering in `progress-draw-pc.gc`.

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
- [9. Architecture: Dark Jak Stages & Legacy Assets](#9-architecture-dark-jak-stages-legacy-assets)
- [10. Architecture: Secrets Menu System (`game-secrets`)](#10-architecture-secrets-menu-system-game-secrets)

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

### 9. Architecture: Dark Jak Stages & Legacy Assets

> **Origin / Provenance :** `master`

* **Drapeaux Bitmask :** Les capacités de Dark Jak sont régies par l'énumération de bits `darkjak-stage` (`target-h.gc`) et stockées dans `(-> self darkjak stage)` et `(-> self darkjak want-stage)` :
  - `active` : Forme Dark Jak de base.
  - `bomb0` / `bomb1` : Capacités Dark Bomb et Dark Blast.
  - `invinc` : État d'invulnérabilité.
  - `invis` : Modificateur d'invisibilité (neutralise les capacités offensives).
  - `tracking` : Mode de suivi / ciblage.
  - `smack` : Attaque Dark Strike.
  - `giant` : Drapeau d'échelle / transformation géante.

## 2. Conditions de Déclenchement et Surfaces Modificatrices
* **Validation d'Entrée :** `want-to-darkjak?` et `want-to-powerjak?` (`target-darkjak.gc` / `target-lightjak.gc`) contrôlent :
  - L'activation de la feature `(game-feature darkjak)` dans `*setting-control*`.
  - Les tests de focus (interdiction sous l'eau, en véhicule, transport d'objet, etc.).
  - Les temporisations via `(-> self fact darkjak-start-time)`.
* **Modificateurs de Surface :** Les physiques de déplacement transformé utilisent `*darkjak-trans-mods*`.

## 3. Reliquats Moteur du Dark Giant de Jak 2
* **Animations et Variables d'Échelle Résiduelles :** Le moteur de Jak 3 intègre encore les données d'animation `jakb-darkjak-get-on-fast-ja` ainsi que la variable d'interpolation de taille `(-> self darkjak-giant-interp)` héritées du Dark Giant de Jak 2.

---

### 10. Architecture: Secrets Menu System (`game-secrets`)

> **Origin / Provenance :** `master`

* **Énumération Bitfield :** Les secrets et cheats de Jak 3 sont répertoriés dans le champ de bits `game-secrets` déclaré dans `settings-h.gc`.
* **Persistance d'État :** L'état actif des secrets est conservé dans `(-> *game-info* secrets)` et testé via `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

## 2. Structure du Menu des Secrets (`secrets-menu.gc`)
* **Déclaration des Éléments :** Les éléments déblocables et activables sont configurés dans des tableaux statiques comme `*menu-secrets-array*` via des structures `secret-item-option`.
* **Champs Principaux :**
  - `:name` : Identifiant `text-id` de la chaîne de texte localisée.
  - `:cost` : Coût en orbes (`0` pour activation gratuite).
  - `:secret` : Drapeau correspondant dans `game-secrets`.
  - `:avail-after` : Prérequis de progression `game-task-node` pour l'affichage dans le menu.
  - `:flags` : Attributs de comportement (ex. `(secret-item-option-flags sf1)`).

## 3. Résolution des Textes UI (`progress-draw-pc.gc`)
* **Noms Personnalisés ou Non Localisés :** Pour les options de secrets ne disposant pas d'entrée dédiée dans les fichiers de texte, le libellé est géré dynamiquement lors du rendu dans `progress-draw-pc.gc`.

---
