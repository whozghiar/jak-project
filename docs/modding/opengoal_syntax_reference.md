# Guide de Référence Syntaxe OpenGOAL Lisp

Ce document regroupe des motifs syntaxiques OpenGOAL validés à 100%, génériques et réutilisables dans tout projet OpenGOAL (Jak 1, Jak 2, Jak 3).

---

## 1. Définition d'États (`defstate`) et Héritage de Handlers

Les états de machine à états (`state`) d'un acteur (`process-drawable`) gèrent son cycle de vie. Un état est composé de plusieurs handlers optionnels :
- `:enter` : exécuté une seule fois à l'entrée dans l'état.
- `:exit` : exécuté à la sortie de l'état.
- `:trans` : exécuté chaque frame avant l'animation/code (idéal pour la détection et les transitions).
- `:code` : le thread principal de l'état (boucle d'animation, attentes temporelles).
- `:post` : exécuté chaque frame en fin de passe (calculs d'orientation, transformées de collision, rendu).
- `:event` : gestionnaire d'événements reçu par l'état.

### Définir un état virtuel dérivé d'un parent
Pour surcharger un état défini dans un type parent tout en réutilisant certains de ses handlers :

```lisp
(defstate mon-etat (mon-type-enfant)
  :virtual #t
  :event enemy-event-handler

  ;; Réutilisation directe des handlers de l'état du parent :
  :enter (-> (method-of-type mon-type-parent mon-etat) enter)
  :exit  (-> (method-of-type mon-type-parent mon-etat) exit)
  :code  (-> (method-of-type mon-type-parent mon-etat) code)
  :post  (-> (method-of-type mon-type-parent mon-etat) post)

  ;; Surcharge spécifique du handler trans (par exemple pour ajouter une condition) :
  :trans (behavior ()
    ;; Code exécuté chaque frame avant le code
    (when (ma-condition?)
      (go-virtual autre-etat)
      )
    )
  )
```

> [!CAUTION]
> **Piège à éviter :** Ne jamais tenter d'appeler manuellement un handler parent via `(let ((t9-0 (-> (method-of-type ...) enter))) (t9-0))`.
> Les pointeurs de handlers dans la structure `state` sont typés de façon générique (`function`). Le compilateur OpenGOAL rejettera l'appel avec l'erreur :
> `This function call has unknown argument and return types and cannot be called.`
> Il faut toujours passer directement la référence `(-> (method-of-type ...) <handler>)` dans le mot-clé correspondant du `defstate`.

---

## 2. Définition et Surcharge de Méthodes (`defmethod`)

### Définir une nouvelle méthode ou surcharger une méthode existante
```lisp
(defmethod nom-de-methode ((this mon-type) (arg0 int) (arg1 symbol))
  "Description optionnelle de la méthode."
  ;; Corps de la méthode
  0
  (none)
  )
```

### Appeler l'implémentation du type parent (équivalent de `super`)
```lisp
(defmethod nom-de-methode ((this mon-type-enfant) (arg0 int))
  ;; Appel de la méthode du parent
  ((method-of-type mon-type-parent nom-de-methode) this arg0)
  0
  (none)
  )
```

---

## 3. Gestion des Masques Binaires et Drapeaux (Bitfields)

OpenGOAL utilise massivement les champs de bits pour les masques de processus (`mask`), d'ennemis (`enemy-flags`), de collision (`collide-spec`), etc.

| Instruction | Rôle | Exemple |
|---|---|---|
| `(logior! <champ> <drapeau>)` | Active un ou plusieurs drapeaux (OU binaire in-place) | `(logior! (-> this flags) (citizen-flag sticky-weapon))` |
| `(logclear! <champ> <drapeau>)` | Désactive un ou plusieurs drapeaux (mise à zéro in-place) | `(logclear! (-> this flags) (citizen-flag hostile))` |
| `(logtest? <valeur> <drapeau>)` | Teste si au moins un bit commun est actif (renvoie `#t` ou `#f`) | `(if (logtest? (-> this flags) (citizen-flag target-in-sight)) ...)` |
| `(logand <val1> <val2>)` | ET binaire (renvoie la valeur résultante) | `(logand (-> this traffic-id) 15)` |
| `(logxor <val1> <val2>)` | OU exclusif binaire | `(logxor a b)` |

---

## 4. Allocations Mémoire (`new`)

OpenGOAL distingue clairement où la mémoire d'un objet est allouée :

### Pile temporaire : `'stack-no-clear`
Idéal pour les vecteurs, matrices ou blocs de paramètres créés à l'intérieur d'une fonction et détruits immédiatement après. Ne consomme aucune mémoire sur le heap et n'initialise pas à zéro (performances maximales) :
```lisp
(let ((pos (new 'stack-no-clear 'vector))
      (params (new 'stack-no-clear 'traffic-object-spawn-params)))
  (vector-copy! pos (-> self root trans))
  ;; utilisation...
  )
```

### Mémoire Statique : `'static`
Alloué à la compilation dans le segment de données. Immuable ou constant :
```lisp
(define *mon-vecteur-fixe* (new 'static 'vector :x 10.0 :y 20.0 :z 0.0 :w 1.0))
```

### Heap du Processus : `'process`
Alloué sur le tas du processus courant. Libéré automatiquement lorsque le processus meurt :
```lisp
(set! (-> this joint) (new 'process 'joint-mod (joint-mod-mode joint-set*-world) this 4))
```

---

## 5. Nombres Aléatoires

OpenGOAL intègre deux générateurs : celui basé sur la Vector Unit (VU, très rapide) et celui basé sur le CPU/Process.

| Fonction | Description | Exemple |
|---|---|---|
| `(rand-vu)` | Float pseudo-aléatoire entre `0.0` et `1.0` | `(< (rand-vu) 0.5)` (50% de chance) |
| `(rand-vu-int-count <N>)` | Entier pseudo-aléatoire compris entre `0` et `N - 1` | `(rand-vu-int-count 3)` (renvoie 0, 1 ou 2) |
| `(rand-vu-float-range <min> <max>)` | Float pseudo-aléatoire entre `min` et `max` | `(rand-vu-float-range 1.0 3.0)` |
| `(rnd-float-range <proc> <min> <max>)` | Float aléatoire associé au contexte du processus | `(rnd-float-range self 0.8 1.2)` |
| `(rnd-int-count <proc> <N>)` | Entier aléatoire entre `0` et `N - 1` avec contexte process | `(rnd-int-count self 2)` |

---

## 6. Mathématiques Vectorielles et Géométrie

### Copie et Opérations Arithmétiques
```lisp
;; Copie intégrale d'un vecteur (x, y, z, w)
(vector-copy! dest src)
;; ou via registre quad 128-bit :
(set! (-> dest quad) (-> src quad))

;; Soustraction vectorielle : dest = v1 - v2
(vector-! dest v1 v2)

;; Addition vectorielle : dest = v1 + v2
(vector+! dest v1 v2)

;; Multiplication scalaire : dest = v * scalaire
(vector-float*! dest v 2.5)

;; Addition + multiplication scalaire : dest = base + (dir * distance)
(vector+float*! dest base dir 8192.0)

;; Normalisation à une longueur donnée
(vector-normalize! v 1.0) ;; longueur 1.0 (vecteur unitaire)
```

### Distances
```lisp
;; Distance 3D euclidienne
(vector-vector-distance v1 v2)

;; Distance 2D sur le plan XZ (très utilisée en navigation pour ignorer le dénivelé Y)
(vector-vector-xz-distance v1 v2)

;; Carré de la distance plane XZ (beaucoup plus rapide car sans calcul de racine carrée)
(if (< (vector-vector-xz-distance-squared v1 v2) (square 16384.0))
    ;; à portée...
    )
```

---

## 7. Gestion du Temps et Horloges

- `(current-time)` : Renvoie le temps actuel en frames (ticks d'horloge de jeu, 300 ticks = 1 seconde).
- `(seconds <float>)` : Convertit une durée en secondes en ticks d'horloge. Exemple : `(seconds 1.5)` vaut 450.
- `(time-elapsed? <temps-initial> <duree>)` : Renvoie `#t` si au moins `<duree>` s'est écoulée depuis `<temps-initial>`.
```lisp
(when (time-elapsed? (-> self state-time) (seconds 2))
  ;; Action exécutée 2 secondes après l'entrée dans l'état
  )
```
- `(set-time! <champ>)` : Enregistre le temps actuel dans la variable :
```lisp
(set-time! (-> self state-time))
```

---

## 8. Communication Entre Processus et Événements

### Envoi d'événements synchrones
Pour transmettre une information ou un ordre à un autre processus :
```lisp
;; Envoi d'un événement sans paramètre
(send-event proc 'mon-evenement)

;; Envoi d'un événement avec paramètres (jusqu'à 4 paramètres)
(send-event proc 'attaquer cible degats)
```

### Gestion des Handles de Processus
Un handle (`handle`) est une référence sûre vers un processus qui évite les accès après libération (dangling pointers) :
```lisp
;; Convertir un process en handle
(set! (-> this mon-handle) (process->handle proc))

;; Retrouver le process depuis le handle (renvoie #f si le process est mort)
(let ((p (handle->process (-> this mon-handle))))
  (when p
    ;; Utiliser p en toute sécurité
    )
  )
```

### Tester l'État d'un Acteur (`focus-test?`)
Tous les acteurs dérivant de `process-focusable` (joueur, ennemis, véhicules, citoyens) maintiennent un champ d'état `focus-status`. L'instruction `(focus-test? <proc> <drapeau(x)>)` permet de tester leur état actuel :

```lisp
;; Vérifier si l'acteur est mort :
(if (focus-test? mon-proc dead)
    ;; L'acteur est mort
    )

;; Vérifier si l'acteur est vivant et interactible :
(when (and mon-proc (not (focus-test? mon-proc dead disable inactive)))
    ;; L'acteur est actif et vivant
    )
```

| Drapeau `focus-status` | Signification |
|---|---|
| `dead` | L'acteur est mort ou en cours de destruction |
| `disable` | L'acteur est désactivé (ignore les collisions) |
| `inactive` | L'acteur est en sommeil / inactif |
| `in-air` | L'acteur n'est pas au sol (en l'air ou en saut) |
| `grabbed` | L'acteur est saisi ou immobilisé |

---

## 9. Quaternions et Orientations Spatiales

### Rotation d'un vecteur par un quaternion
Pour orienter un vecteur relatif (par exemple un décalage de formation ou une position d'attache) selon l'orientation spatiale d'un acteur :
```lisp
;; dst = src tourné selon le quaternion quat
(vector-orient-by-quat! dst-vector src-vector (-> mon-acteur root quat))
```

### Extraction des axes directeurs depuis un quaternion
Pour obtenir les vecteurs unitaires représentant les axes locaux d'un acteur :
```lisp
;; Vecteur avant (forward, axe Z local)
(vector-z-quaternion! fwd-vector (-> mon-acteur root quat))

;; Vecteur droite (right, axe X local)
(vector-x-quaternion! right-vector (-> mon-acteur root quat))

;; Vecteur haut (up, axe Y local)
(vector-y-quaternion! up-vector (-> mon-acteur root quat))
```

---

## 10. Navigation sur Nav-Mesh (`nav-state`)

Pour diriger un acteur utilisant le système de navigation (`nav-enemy` ou `citizen`) vers une coordonnée spatiale :

### Définir une nouvelle position cible
```lisp
(let ((nav-st (-> self nav state)))
  ;; Désactive le mode directionnel pur
  (logclear! (-> nav-st flags) (nav-state-flag directional-mode))
  ;; Notifie le moteur de recalculer le polygone du nav-mesh pour cette nouvelle cible
  (logior! (-> nav-st flags) (nav-state-flag target-poly-dirty))
  ;; Assigne la coordonnée cible
  ;; Note: en Jak 2 le champ est nommé target-post, en Jak 3 il s'appelle target-pos
  (set! (-> nav-st target-post quad) (-> point-cible quad))
  )
```

### Ajuster la vitesse de consigne de navigation
```lisp
(set! (-> self nav target-speed) nouvelle-vitesse)
```

### Trouver le nav-mesh le plus proche d'un point
Indispensable avant d'activer la navigation d'un acteur généré dynamiquement dans le monde :
```lisp
(set! (-> params nav-mesh) (find-nearest-nav-mesh (-> params position) (the-as float #x7f800000)))
```

---

## 11. Déclarations Externes (`define-extern`) et Préservation des Types Globaux

La directive `define-extern` informe le compilateur OpenGOAL de l'existence et du type d'un symbole (variable ou fonction) défini dans un autre fichier.

```lisp
;; Déclaration d'une fonction externe
(define-extern ma-fonction (function int vector symbol none))

;; Déclaration d'une variable globale externe
(define-extern *ma-variable* symbol)
```

> [!CAUTION]
> **Piège critique : Écrasement du type d'un symbole global existant**
> Si un symbole global est déjà déclaré ou défini dans un fichier d'en-tête (ex: `*-h.gc`) avec un type spécialisé (par exemple `*mon-gestionnaire*` de type `mon-gestionnaire-type`), redéclarer ce symbole plus tard avec un type parent générique tel que `process` :
> ```lisp
> (define-extern *mon-gestionnaire* process) ;; DANGEREUX !
> ```
> **écrasera le type du symbole dans la table des symboles du compilateur** pour tous les fichiers compilés par la suite.
> Tout code ultérieur accédant aux champs spécifiques de cet objet via `(-> *mon-gestionnaire* mon-champ-special)` échouera immédiatement à la compilation :
> `Type Error: Type process has no field named mon-champ-special`
>
> **Règles de sécurité :**
> 1. Ne jamais ajouter de `define-extern` pour une variable globale déjà définie dans les en-têtes du projet (ex: `traffic-h.gc`, `game-info-h.gc`).
> 2. Si une redéclaration est nécessaire, utiliser impérativement le type exact le plus spécifique et non son type de base (`process`).

---

## 12. Événements Synchrones (`send-event`) et Cycle de Vie des Processus

### Synchronisme de `send-event` et Risque de Récursion Infinie
En OpenGOAL, la fonction `(send-event <proc> <event> <args>...)` est un appel **strictement synchrone et immédiat**. Le gestionnaire d'événements du destinataire est exécuté sur-le-champ dans la même frame et sur la même pile d'exécution.

> [!CAUTION]
> **Piège critique : La récursion infinie lors de l'activation en cascade**
> Si lors de la réception d'un événement d'activation (ex: `'traffic-activate`), l'acteur parent génère dynamiquement un ou plusieurs acteurs enfants et leur transmet immédiatement un événement `'traffic-activate` sans filtrage préalable strict :
> 1. Si les acteurs enfants exécutent le même handler que le parent sans distinguer leur rôle, ils tenteront à leur tour de créer des enfants.
> 2. Tout écrasement de variable d'état dans une fonction de réinitialisation synchrone (comme `citizen-init!`) écrasera les drapeaux d'escouade assignés juste avant l'envoi de l'événement.
> 
> Cette cascade entraîne un débordement instantané de la pile et l'épuisement de la mémoire (`exit status 5` / STATUS_ACCESS_VIOLATION).
> 
> **Bonne pratique :** Utiliser le champ `user-data` des paramètres de spawn (`traffic-object-spawn-params`) ou un champ de rôle dédié pour taguer explicitement les enfants (ex: `user-data = 1` pour un subordonné, `user-data = 2` pour du debug), et n'exécuter la génération que si `(zero? (-> params user-data))`.

### Désactivation Propre d'un Acteur
Pour faire disparaître un acteur géré par un système (comme la circulation ou un nav-mesh), il ne faut **jamais** appeler `(deactivate <process>)` directement :
```lisp
;; INTERDIT : contourne le nettoyage du nav-mesh, des collisions et des listes d'affichage :
(deactivate mon-process) ;; DANGEREUX ! Risque de plantage différé

;; CORRECT : transmettre un événement invitant l'acteur à exécuter son cycle de sommeil/nettoyage :
(send-event mon-process 'traffic-off-force)
```
La réception de cet événement permet au processus d'appeler `(go-inactive this)` qui effectue le détachement complet du nav-mesh (`remove-process-drawable`), la libération des collisions et le retour propre dans le pool dormant (`dead-pool`).

---

## 13. Sortie Anticipée de Fonction (`return`)

OpenGOAL supporte l'instruction `(return <valeur>)` pour interrompre immédiatement l'exécution d'une fonction et renvoyer la valeur spécifiée :

```lisp
(defun trouver-element ((tableau (pointer handle)) (taille int))
  (dotimes (i taille)
    (let ((p (handle->process (-> tableau i))))
      (when (and p (type? p mon-type-recherche))
        ;; Sortie immédiate dès que l'élément est trouvé
        (return (-> tableau i))
        )
      )
    )
  ;; Si la boucle se termine sans succès
  (the-as handle #f)
  )
```

---

## 14. Gestion des Processus : `dead-pool` vs Pools d'Objets Dormants

Dans le moteur OpenGOAL, la création et le recyclage des processus s'articulent autour de deux mécanismes distincts selon le moment d'exécution :

### Épuisement du `*default-dead-pool*` en Cours de Jeu
Le noyau dispose d'un pool global fini de processus (`*default-dead-pool*`, limité typiquement à 128 processus).
Lors du chargement des niveaux, les gestionnaires de trafic et de population pré-allouent la quasi-totalité de ces slots pour peupler leurs réserves d'objets dormants.
En conséquence, pendant le déroulement normal du jeu :
- Le pool de processus global `*default-dead-pool*` est **entièrement saturé** (0 slot libre).
- Tout appel direct à `(get-process *default-dead-pool* ...)` (comme via `citizen-spawn`) tente alors d'allouer depuis `*debug-dead-pool*` et déclenche une instruction matérielle explicite `(break)` dans le noyau (`gkernel.gc`).
- Cette rupture interrompt immédiatement l'application (`exit status 5` sous Windows, breakpoint/accès non valide).

### Règle d'Or : Utiliser l'Activation d'Objets Dormants
Pour générer ou réveiller un acteur dynamique (citoyen, véhicule, ennemi géré en flotte) en cours de partie sans allouer de nouveau processus :
1. Les processus dormants sont stockés dans les tableaux inactifs d'un tracker (`traffic-tracker` / `traffic-engine`).
2. Pour réactiver un processus disponible, utiliser les méthodes dédiées d'activation :
   - `(activate-object <engine> <spawn-params>)` : Sélectionne et réveille un processus disponible de ce type depuis la réserve dormante.
   - `(activate-by-handle <engine> <spawn-params>)` : Réveille un processus spécifique déjà ciblé via son handle.
3. Ces fonctions envoient l'événement d'activation (ex: `'traffic-activate`), déplacent le processus vers le tableau actif, et assignent le champ `(-> params proc)` sans allouer aucune mémoire noyau.

---

## 15. Déréférencement Chaîné et Sécurité des Pointeurs (`(-> a b c)`)

En OpenGOAL Lisp, l'expression `(-> objet champ1 champ2 champ3)` permet d'accéder à des sous-champs imbriqués.

### Absence de Court-Circuit Automatique
Contrairement aux langages modernes de haut niveau qui disposent d'opérateurs de navigation sécurisée (comme `?.`), le compilateur GOAL résout les accès chaînés en cumulant directement les décalages mémoire (offsets) :
```lisp
;; Traduction machine d'un accès chaîné :
;; [objet + offset_champ1 + offset_champ2 + offset_champ3]
(-> mon-objet champ1 champ2 champ3)
```

Si l'un des pointeurs intermédiaires vaut `#f` (représenté par le pointeur nul `0` ou l'adresse du symbole `#f`), l'exécution tente d'accéder à une adresse mémoire invalide et provoque immédiatement une violation d'accès matérielle (`STATUS_ACCESS_VIOLATION`, code de crash `exit status 5` sous Windows).

### Règle de Sécurité : Garde Explicite des Pointeurs Intermédiaires
Avant d'accéder à un sous-champ profondément imbriqué, chaque niveau de pointeur potentiellement nul doit être expressément vérifié :

```lisp
;; RISQUÉ (crash immédiat si nav ou state est #f) :
(set! mesh (-> mon-acteur nav state mesh))

;; SÉCURISÉ (chaque maillon est testé avant d'atteindre la feuille) :
(when (and (-> mon-acteur nav)
           (-> mon-acteur nav state)
           (-> mon-acteur nav state mesh)
           )
  (set! mesh (-> mon-acteur nav state mesh))
  )
```

---

## 16. Traçabilité des Projectiles et Filtrage des Dégâts Alliés dans les Événements

Lorsqu'un acteur reçoit un événement de collision ou d'attaque (`'attack`, `'touch'`, `'touched'`), le premier paramètre (`arg0`) représente le processus à l'origine de l'événement.

### Identifier l'Émetteur Réel d'un Projectile
Si l'attaquant direct est un projectile (`projectile`), le véritable instigateur (l'acteur qui a tiré ou lancé le projectile) se récupère via le handle `notify-handle` ou via le pointeur de processus parent :

```lisp
(defun obtenir-attaquant-reel ((attaquant process))
  "Renvoie le processus à l'origine de l'attaque, même si l'attaquant direct est un projectile."
  (when attaquant
    (let ((reel attaquant))
      (if (type? reel projectile)
          (let ((proprio (handle->process (-> (the-as projectile reel) notify-handle))))
            (if proprio
                (set! reel proprio)
                ;; (-> reel parent) est de type (pointer process-tree) ; un transtypage explicite (the-as process ...) est requis
                (if (-> reel parent)
                    (set! reel (the-as process (ppointer->process (-> reel parent))))
                    )
                )
            )
          )
      reel
      )
    )
  )
```

### Annulation d'un Événement d'Attaque (Tir Ami)
Dans la méthode `general-event-handler` d'un acteur, intercepter un message d'attaque et renvoyer `#f` immédiatement empêche le gestionnaire de base (`nav-enemy` ou `enemy`) de décompter des points de vie, de déclencher le recul (`knockback`) ou de générer des nombres de dégâts :

```lisp
(defmethod general-event-handler ((this mon-acteur) (arg0 process) (arg1 int) (arg2 symbol) (arg3 event-message-block))
  (case arg2
    (('attack 'touch 'touched)
     ;; Si l'attaquant appartient à la même faction, ignorer l'attaque
     (when (meme-faction? this arg0)
       (return #f)
       )
     ((method-of-type classe-parente general-event-handler) this arg0 arg1 arg2 arg3)
     )
    ;; ...
    )
  )
```

---
*(AI-assisted)*


