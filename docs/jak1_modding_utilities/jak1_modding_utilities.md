# Jak 1 — Notes de modding & fonctionnement moteur

> Document de travail pensé pour être complété et enrichi au fil des sessions de modding.
> **Objectif :** Garder une trace pédagogique du fonctionnement interne d'OpenGOAL pour **Jak 1 (The Precursor Legacy)**, avec des explications concrètes et vérifiées issues de l'analyse du code source (`goal_src/jak1/`).
> 
> *Règle : N'inclure que des informations sûres et vérifiées. Toute hypothèse non encore confirmée par le code ou les tests doit être explicitement préfixée par `[Hypothèse]`.*

---

## Sommaire

- [1. Vocabulaire et concepts de base](#1-vocabulaire-et-concepts-de-base)
- [2. Architecture mémoire et constantes](#2-architecture-mémoire-et-constantes)
- [3. Système d'entités, process et états (State Machine)](#3-système-dentités-process-et-états-state-machine)
- [4. Squelette, joints et animations](#4-squelette-joints-et-animations)
- [5. Collisions et requêtes spatiales](#5-collisions-et-requêtes-spatiales)
- [6. Audio et lecture de sons](#6-audio-et-lecture-de-sons)
- [7. Déclarer un nouveau script dans le projet (`.gp`)](#7-déclarer-un-nouveau-script-dans-le-projet-gp)
- [8. Workflow de compilation et validation](#8-workflow-de-compilation-et-validation)
- [9. Pièges connus et points de vigilance](#9-pièges-connus-et-points-de-vigilance)

---

## 1. Vocabulaire et concepts de base

| Terme | Définition & Rôle dans Jak 1 |
|---|---|
| **GOAL** | Langage Lisp propriétaire de Naughty Dog compilé en x86-64 par OpenGOAL. |
| **`process-drawable`** | Type de base pour toute entité du monde disposant d'un modèle 3D / affichage (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Nom symbolique du process représentant le joueur (Jak). Accessible globalement via le symbole `*target*`. |
| **`state`** | Objet représentant un état de machine d'état (ex: `target-running`, `target-jump`). Contient des handlers d'événements, code d'exécution et post-processing. |
| **`DGO`** | Fichier archive regroupant les objets compilés (`.o`) chargés en mémoire lors du chargement des niveaux. |

---

## 2. Architecture mémoire et constantes

* **Point d'entrée Kernel :** `goal_src/jak1/kernel/gcommon.gc` et `goal_src/jak1/engine/level/level.gc`.
* **Vérification d'adresses (`valid?`) :** `END_OF_MEMORY` dans `goal_src/jak1/kernel/gcommon.gc`.
* **Mémoire C++ partagée :** `EE_MAIN_MEM_SIZE` est défini dans `common/goal_constants.h` et alloué via le runtime C++.

---

## 3. Système d'entités, process et états (State Machine)

### Structure type d'un nouveau process
En GOAL, un nouvel acteur dérive généralement de `process-drawable` :

```lisp
(deftype my-custom-actor (process-drawable)
  ((custom-counter  int32)
   (custom-timer    time-frame))
  (:state-methods
    idle
    active)
  )
```

### Définition d'un état simple
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

## 4. Squelette, joints et animations

* **Joints & Bones :** Gérés par le sous-système `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
* **Macros d'animation courantes :**
  - `(ja-no-eval :group! ... :num! (seek!) :frame-num 0.0)` : Lance une animation.
  - `(ja :num! (seek!))` : Fait avancer la frame courante d'animation.
  - `(ja-done? 0)` : Vérifie si le canal d'animation 0 a terminé son cycle.
  - `(suspend)` : Rend la main au moteur pour la frame courante (équivalent d'un `yield`).

---

## 5. Collisions et requêtes spatiales

* **Gestionnaire de collision :** Stocké dans le champ `(root ...)` du process (type `collide-shape` ou `trsqv`).
* **Surfaces & Matières :** Définies dans `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

---

## 6. Audio et lecture de sons

* Pour déclencher un effet sonore depuis le code :
```lisp
(sound-play "sound-name")
```
* Déclenchement spatialisé ou lié à une entité :
```lisp
(sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
```

---

## 7. Déclarer un nouveau script dans le projet (`.gp`)

Pour que le compilateur prenne en compte un nouveau fichier `.gc` créé sous `goal_src/jak1/custom/` :
1. Ouvrir le fichier de description de projet approprié (ex: `goal_src/jak1/jak1-game.gp`).
2. Ajouter l'entrée correspondant au fichier :
   ```
   (c "custom/my-script.gc")
   ```
3. Lancer la compilation via `(mi)`.

---

## 8. Workflow de compilation et validation

1. **Vérification du jeu actif :**
   ```bash
   task set-game-jak1
   ```
2. **Compilation du code :**
   Dans le REPL OpenGOAL (`task repl`) :
   ```lisp
   (mi)
   ```
3. **Lancement de test :**
   ```bash
   task boot-game
   ```

---

## 9. Pièges connus et points de vigilance

* **Ordre de chargement des symboles :** Les types parents doivent impérativement être déclarés avant les types enfants.
* **REPL Ghost Memory :** Toujours valider les modifications avec un redémarrage à froid du REPL pour s'assurer que le jeu compile de zéro.
* **Sauvegarde dans Git :** Synchroniser régulièrement les ajouts de ce fichier avec la branche `master`.
