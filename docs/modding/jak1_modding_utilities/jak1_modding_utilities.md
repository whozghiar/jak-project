# Jak 1 (The Precursor Legacy) — Modding Notes & Engine Utilities / Notes de Modding & Utilitaires Moteur

> **Bilingual Knowledge Base / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Table of Contents
- [1. Core Vocabulary](#1-core-vocabulary)
- [2. Memory Architecture & Constants](#2-memory-architecture-constants)
- [3. Entity System, Processes & State Machine](#3-entity-system-processes-state-machine)
- [4. Skeleton, Joints & Animations](#4-skeleton-joints-animations)
- [5. Collisions & Spatial Queries](#5-collisions-spatial-queries)
- [6. Audio & Sound Playback](#6-audio-sound-playback)
- [7. Declaring Scripts in Project File (`.gp`)](#7-declaring-scripts-in-project-file-gp)
- [8. Compilation & Validation Workflow](#8-compilation-validation-workflow)
- [9. Known Pitfalls & Best Practices](#9-known-pitfalls-best-practices)

---

### 1. Core Vocabulary

> **Origin / Provenance:** `master` | **Last Updated:** `master`

| Term | Definition & Role in Jak 1 |
|---|---|
| **GOAL** | Naughty Dog's proprietary Lisp dialect compiled to native x86-64 by OpenGOAL. |
| **`process-drawable`** | Base type for any interactive world entity featuring a 3D model and transformation hierarchy (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Symbolic name representing the player process (Jak). Globally accessible via `*target*`. |
| **`state`** | State machine node containing event handlers, execution loop (`:code`), and post-processing (`:post`). |
| **`DGO`** | Data Group Object archive packaging compiled objects (`.o`) loaded together into RAM during level streaming. |

---

---

### 2. Memory Architecture & Constants

> **Origin / Provenance:** `master` | **Last Updated:** `master`

* **Kernel Entry Point:** `goal_src/jak1/kernel/gcommon.gc` and `goal_src/jak1/engine/level/level.gc`.
* **Address Validation (`valid?`):** `END_OF_MEMORY` in `goal_src/jak1/kernel/gcommon.gc` protects pointer dereferencing across memory bounds.
* **Shared C++ Memory:** `EE_MAIN_MEM_SIZE` is defined in `common/goal_constants.h` and allocated by the C++ runtime via `mmap`.

---

---

### 3. Entity System, Processes & State Machine

> **Origin / Provenance:** `master` | **Last Updated:** `master`

In GOAL, custom interactive actors derive from `process-drawable`:

```lisp
(deftype my-custom-actor (process-drawable)
  ((custom-counter  int32)
   (custom-timer    time-frame))
  (:state-methods
    idle
    active)
  )
```

## 2. State Machine Implementation
A state is declared with `:virtual #t`, event handlers, code loop, and post function:

```lisp
(defstate idle (my-custom-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack)
       (go-virtual active))))
  :code (behavior ()
    (loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))
      ))
  :post ja-post)
```

---

---

### 4. Skeleton, Joints & Animations

> **Origin / Provenance:** `master` | **Last Updated:** `master`

* **Joint Subsystem:** Managed by `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
* **Common Animation Macros:**
  - `(ja-no-eval :group! ... :num! (seek!) :frame-num 0.0)`: Starts animation playback from frame 0.
  - `(ja :num! (seek!))`: Advances the active animation frame.
  - `(ja-done? 0)`: Evaluates whether channel 0 reached the end of its sequence.
  - `(suspend)`: Yields execution back to the game engine for the current frame.

---

---

### 5. Collisions & Spatial Queries

> **Origin / Provenance:** `master` | **Last Updated:** `master`

* **Collision Root:** Handled in the `(root ...)` field of `process-drawable` (type `collide-shape` or `trsqv`).
* **Surface Properties & Materials:** Defined in `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

---

---

### 6. Audio & Sound Playback

> **Origin / Provenance:** `master` | **Last Updated:** `master`

* **Simple SFX Playback:**
  ```lisp
  (sound-play "sound-name")
  ```
* **Positional / Entity-Bound SFX:**
  ```lisp
  (sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
  ```

---

---

### 7. Declaring Scripts in Project File (`.gp`)

> **Origin / Provenance:** `master` | **Last Updated:** `master`

To register a new `.gc` file created under `goal_src/jak1/custom/`:
1. Open the project configuration file: `goal_src/jak1/jak1-game.gp`.
2. Add the file entry:
   ```
   (c "custom/my-script.gc")
   ```
3. Recompile via the REPL with `(mi)`.

---

---

### 8. Compilation & Validation Workflow

> **Origin / Provenance:** `master` | **Last Updated:** `master`

1. **Select Active Game:**
   ```bash
   task set-game-jak1
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

### 9. Known Pitfalls & Best Practices

> **Origin / Provenance:** `master` | **Last Updated:** `master`

* **Symbol Loading Order:** Parent types must strictly be declared before child types in `.gp` and file include lists.
* **REPL Ghost Memory:** Always perform a clean cold restart of the REPL to ensure changes compile from scratch without relying on stale runtime state.
* **Git Synchronization:** Regularly merge verified discoveries from this file back to `master`.

---

---

# 🇫🇷 Version Française

## Sommaire
- [1. Vocabulaire de Base](#1-vocabulaire-de-base)
- [2. Architecture Mémoire & Constantes](#2-architecture-mémoire-constantes)
- [3. Système d'Entités, Process & États](#3-système-dentités-process-états)
- [4. Squelette, Joints & Animations](#4-squelette-joints-animations)
- [5. Collisions & Requêtes Spatiales](#5-collisions-requêtes-spatiales)
- [6. Audio & Lecture de Sons](#6-audio-lecture-de-sons)
- [7. Déclarer un Script (`.gp`)](#7-déclarer-un-script-gp)
- [8. Workflow de Compilation & Validation](#8-workflow-de-compilation-validation)
- [9. Pièges Connus & Bonnes Pratiques](#9-pièges-connus-bonnes-pratiques)

---

### 1. Vocabulaire de Base

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

| Terme | Définition & Rôle dans Jak 1 |
|---|---|
| **GOAL** | Langage Lisp propriétaire de Naughty Dog compilé en x86-64 par OpenGOAL. |
| **`process-drawable`** | Type de base pour toute entité du monde disposant d'un modèle 3D / affichage (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Nom symbolique du process représentant le joueur (Jak). Accessible globalement via le symbole `*target*`. |
| **`state`** | Objet représentant un état de machine d'état (ex: `target-running`, `target-jump`). Contient des handlers d'événements, code d'exécution et post-processing. |
| **`DGO`** | Fichier archive regroupant les objets compilés (`.o`) chargés en mémoire lors du chargement des niveaux. |

---

### 2. Architecture Mémoire & Constantes

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

* **Point d'Entrée Kernel :** `goal_src/jak1/kernel/gcommon.gc` et `goal_src/jak1/engine/level/level.gc`.
* **Vérification d'Adresses (`valid?`) :** `END_OF_MEMORY` dans `goal_src/jak1/kernel/gcommon.gc` sécurise les déréférencements de pointeurs.
* **Mémoire C++ Partagée :** `EE_MAIN_MEM_SIZE` est défini dans `common/goal_constants.h` et alloué via le runtime C++ via `mmap`.

---

### 3. Système d'Entités, Process & États

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

En GOAL, les entités interactives dérivent généralement de `process-drawable` :

```lisp
(deftype my-custom-actor (process-drawable)
  ((custom-counter  int32)
   (custom-timer    time-frame))
  (:state-methods
    idle
    active)
  )
```

## 2. Définition d'un État
Un état associe des gestionnaires d'événements, une boucle de code et une méthode de rendu :

```lisp
(defstate idle (my-custom-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack)
       (go-virtual active))))
  :code (behavior ()
    (loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))
      ))
  :post ja-post)
```

---

### 4. Squelette, Joints & Animations

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

* **Sous-Système d'Os & Joints :** Géré par `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
* **Macros d'Animation Courantes :**
  - `(ja-no-eval :group! ... :num! (seek!) :frame-num 0.0)` : Lance une animation à la frame 0.
  - `(ja :num! (seek!))` : Fait avancer la frame courante d'animation.
  - `(ja-done? 0)` : Vérifie si le canal d'animation 0 a terminé son cycle.
  - `(suspend)` : Rend la main au moteur pour la frame courante (équivalent d'un `yield`).

---

### 5. Collisions & Requêtes Spatiales

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

* **Gestionnaire de Collision :** Stocké dans le champ `(root ...)` du process (type `collide-shape` ou `trsqv`).
* **Surfaces & Matières :** Définies dans `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

---

### 6. Audio & Lecture de Sons

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

* **Lecture d'Effet Sonore Simple :**
  ```lisp
  (sound-play "sound-name")
  ```
* **Lecture Spatialisée / Liée à une Entité :**
  ```lisp
  (sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
  ```

---

### 7. Déclarer un Script (`.gp`)

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

Pour faire reconnaître un nouveau fichier `.gc` créé sous `goal_src/jak1/custom/` :
1. Ouvrir le fichier projet : `goal_src/jak1/jak1-game.gp`.
2. Ajouter la ligne correspondant au fichier :
   ```
   (c "custom/my-script.gc")
   ```
3. Lancer la compilation dans le REPL avec `(mi)`.

---

### 8. Workflow de Compilation & Validation

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

1. **Sélectionner le Jeu Actif :**
   ```bash
   task set-game-jak1
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

### 9. Pièges Connus & Bonnes Pratiques

> **Origin / Provenance :** `master` | **Dernière modification :** `master`

* **Ordre de Chargement des Symboles :** Les types parents doivent impérativement être déclarés avant les types enfants dans les fichiers `.gp`.
* **REPL Ghost Memory :** Toujours valider les modifications avec un redémarrage à froid du REPL pour s'assurer d'une compilation complète sans état résiduel.
* **Synchronisation Git :** Synchroniser régulièrement les ajouts validés avec la branche `master`.

---
