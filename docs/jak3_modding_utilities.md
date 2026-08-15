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

### Trouver l'index d'un joint : ne jamais compter à la main

`(-> self node-list data N)` a besoin d'un index numérique, mais cet index est celui du **joint-group compilé** (`*jg-info*`), pas la position brute dans le tableau de joints d'un GLB. Compter les entrées d'un GLB à la main pour deviner cet index est **non fiable** - vérifié en pratique : ça a donné 2 réponses différentes et fausses de suite sur le même joint dans une session de modding (index 25 puis 24, la vraie réponse était ailleurs), simplement parce que l'ordre du GLB ne correspond pas forcément à l'ordre d'assignation du compilateur.

La bonne méthode - une résolution par nom, à la compilation, contre les vraies données `*jg-info*` :
```lisp
(joint-node-index jakb-lod0-jg board)          ; -> l'index entier
(-> self node-list data (joint-node-index jakb-lod0-jg board))  ; -> le node directement
;; ou, équivalent et plus court :
(joint-node jakb-lod0-jg board)
```
Ces deux macros existent aussi bien côté Jak 2 que Jak 3 (`engine/data/art-h.gc`). Si un index de joint doit être écrit en dur dans du code de gameplay, préférer une de ces macros à un littéral numérique - le littéral casse silencieusement si la géométrie/le squelette change, la macro non.

### Reciblage d'animations entre squelettes (ex: importer une animation Jak 3 dans Jak 2)

Un outil dédié existe pour ça : `goalc/retarget_anim/` (build via CMake, cible `retarget_anim`, lié à `tiny_gltf`). Il prend un GLB de base (le squelette natif du jeu cible, ex. `decompiler_out/jak2/levels/common/jakb-lod0.glb`) et un GLB source (le squelette natif du jeu d'origine avec l'animation voulue déjà dedans, ex. `decompiler_out/jak3/levels/common/jakb-lod0.glb` - ces fichiers contiennent déjà toutes les animations natives du jeu, décompressées, pas besoin de retoucher le pipeline de décompilation), et retargete par **nom de joint**, pas par index.

Règle de reciblage vérifiée contre de vraies données natives avant d'être appliquée (ne pas supposer, vérifier) :
- **Translation :** seuls les joints racine (`align`, `main` par défaut, `--root-joints`) reçoivent la translation réelle de la source - c'est ce qui porte le vrai mouvement de la racine. Tout autre joint garde sa propre translation bind-pose (celle du squelette de base) : la translation encode la longueur d'os, et les deux squelettes n'ont pas forcément les mêmes proportions - copier la translation de la source sur un joint non-racine étire le membre.
- **Rotation :** copiée depuis la source pour tout joint qui l'anime, indépendamment d'être racine ou non (la rotation n'encode pas de longueur d'os, donc a priori sûre à recibler partout) - **mais seulement si les deux squelettes partagent la même orientation de bind-pose pour ce joint**. Si un doute existe là-dessus, vérifier d'abord (`node.rotation` sur le joint concerné dans les deux GLB natifs) plutôt que de supposer un décalage à corriger : sur cette branche, l'hypothèse d'un décalage de bind-pose expliquant une dérive visuelle a été testée puis **infirmée** par comparaison directe - les deux squelettes avaient une bind-pose identique `(0,0,0,1)`, donc rien à corriger de ce côté-là pour ce cas précis.
- **Échelle :** bind-pose du squelette de base par défaut ; ne jamais forcer `(1,1,1)` sur un joint dont la bind-pose native n'est pas neutre (un joint d'attache comme un porte-arme peut avoir une échelle non-neutre qui annule volontairement celle de son parent - le vérifier dans le GLB natif avant de forcer une valeur).

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
* **Un son qui existe dans une `.SBK` n'est pas forcément chargé.** Le simple fait qu'une banque de sons soit présente sur le disque (ou déclarée en jeu comme `mode-sound-bank` côté GOAL) ne veut pas dire qu'elle est réellement chargée en mémoire - quelque chose doit explicitement le demander (`sound-bank-load` côté GOAL, qui part en RPC vers le code overlord IOP). Si des sons d'une banque nommée échouent tous en `play_sound_by_name: failed to find bank`, vérifier dans cet ordre : (1) quelque chose appelle bien `sound-bank-load` pour ce nom précis (les tables de rotation par niveau, `:want-sound` dans `level-info.gc`, ne couvrent que les banques tournantes, pas les banques à emplacement dédié) ; (2) côté C++ overlord, si la banque a un emplacement dédié réservé au boot (comme "common"), la fonction d'allocation par nom (`AllocateBankName`/équivalent) la traite bien comme cas spécial à retour direct - sinon elle peut tomber dans une boucle qui ne cherche que les emplacements de rotation (toujours pleins en jeu normal), et échouer avec "plus de place" alors que son propre emplacement dédié est inutilisé. **[Vérifié sur Jak 2]** (`game/overlord/common/sbank.cpp`, exploité par `jak2`) : les emplacements dédiés `gun`/`board` existaient depuis toujours mais n'étaient jamais retournés par `AllocateBankName`, qui ne traitait ce cas spécial que pour `common`. Jak 3 a sa propre implémentation séparée (`game/overlord/jak3/sbank.cpp`, structure différente - pas de slot `board` dédié, un slot `mode` à la place) - la démarche de vérification ci-dessus s'applique, mais ce bug précis n'a pas été vérifié côté Jak 3.
* **Synchronisation Git :** Penser à merger régulièrement les ajouts factuels de ce fichier vers la branche `master`.
