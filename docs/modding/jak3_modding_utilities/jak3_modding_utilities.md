# Jak 3 — Notes de modding & fonctionnement moteur

> Document de travail pensé pour être complété et enrichi au fil des sessions de modding.
> **Objectif :** Garder une trace pédagogique du fonctionnement interne d'OpenGOAL pour **Jak 3**, avec des explications concrètes et vérifiées issues de l'analyse du code source (`goal_src/jak3/`).
> 
> *Règle : N'inclure que des informations sûres et vérifiées. Toute hypothèse non encore confirmée par le code ou les tests doit être explicitement préfixée par `[Hypothèse]`.*

---

## Sommaire

- [1. Vocabulaire et concepts de base](#1-vocabulaire-et-concepts-de-base)
- [2. Architecture mémoire et constantes](#2-architecture-mémoire-et-constantes)
- [3. Système d'armes, véhicules et entités](#3-système-darmes-véhicules-et-entités)
- [4. Processus, états et comportements](#4-processus-états-et-comportements)
- [5. Squelette, joints et animations](#5-squelette-joints-et-animations)
- [6. Déclarer un nouveau script dans le projet (`.gp`)](#6-déclarer-un-nouveau-script-dans-le-projet-gp)
- [7. Workflow de compilation et validation](#7-workflow-de-compilation-et-validation)
- [8. Pièges connus et points de vigilance](#8-pièges-connus-et-points-de-vigilance)

---

## 1. Vocabulaire et concepts de base

| Terme | Définition & Rôle dans Jak 3 |
|---|---|
| **GOAL** | Langage Lisp propriétaire de Naughty Dog compilé en x86-64 par OpenGOAL. |
| **`gun-info`** | Structure gérant l'arsenal modulable de Jak 3 (morph-gun et 12 formes d'armes). |
| **`vehicle` / `hvehicle`** | Types de base pour les véhicules tout-terrain du désert et les véhicules urbains flottants. |
| **`light-jak` / `dark-jak`** | Sous-systèmes d'états gérant les capacités et pouvoirs de Jak. |
| **`target`** | Processus représentant le joueur (`*target*`). |

---

## 2. Architecture mémoire et constantes

* **Point d'entrée Kernel :** `goal_src/jak3/kernel/gcommon.gc` et `goal_src/jak3/engine/level/level.gc`.
* **Budget Mémoire (Extension PC) :**
  - `END_OF_MEMORY` : configuré pour supporter 512 Mo (`#x20000000`).
  - `DEBUG_LEVEL_HEAP_MULT` : multiplicateur de taille du heap de niveau dans `level.gc` (valeur historique : `15.0`).
* **Mémoire C++ partagée :** `EE_MAIN_MEM_SIZE` est partagé dans `common/goal_constants.h`.

---

## 3. Système d'armes, véhicules et entités

### Système d'armes (`gun`)
* L'accès à l'état de l'arme se fait généralement à travers le process joueur :
```lisp
(when *target*
  (let ((gun (-> *target* gun)))
    ;; Accès aux propriétés de tir, munitions, type d'arme
    ))
```

### Véhicules et physique
* Les véhicules du désert dérivent de la hiérarchie `vehicle` (`goal_src/jak3/engine/vehicle/`).
* Le comportement physique utilise des forces de suspension, frottement et inertie résolues à chaque cycle via des behaviors dédiés.

---

## 4. Processus, états et comportements

Structure standard d'un acteur dans Jak 3 :
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

## 5. Squelette, joints et animations

* **Moteur d'animation :** Système `merc` / `mips2c` pour le rendu et calculs squelettiques.
* **Manipulation de joints :** Accès direct aux transformations via le tableau `(-> self node-list data [index] bone transform)`.
* **Avancement d'animation :**
  ```lisp
  (ja :num! (seek!))
  (suspend)
  ```

---

## 6. Déclarer un nouveau script dans le projet (`.gp`)

Pour ajouter un nouveau fichier `.gc` dans l'arbre de compilation :
1. Localiser le fichier `.gp` de configuration (ex: `goal_src/jak3/jak3-game.gp`).
2. Ajouter le chemin vers le nouveau script :
   ```
   (c "custom/my-jak3-mod.gc")
   ```
3. Recompiler dans le REPL avec `(mi)`.

---

## 7. Workflow de compilation et validation

1. **Sélectionner Jak 3 :**
   ```bash
   task set-game-jak3
   ```
2. **Compilation du code :**
   Dans le REPL OpenGOAL (`task repl`) :
   ```lisp
   (mi)
   ```
3. **Lancement du jeu :**
   ```bash
   task boot-game
   ```

---

## 8. Pièges connus et points de vigilance

* **Interactions complexes entre pouvoirs et armes :** Modifier les états de `*target*` peut affecter les transitions d'armes (`gun-states`) et de pouvoirs (`light-jak` / `dark-jak`).
* **Synchronisation Git :** Penser à merger régulièrement les ajouts factuels de ce fichier vers la branche `master`.
