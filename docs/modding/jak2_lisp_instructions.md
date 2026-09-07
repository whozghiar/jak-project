# Jak 2 — OpenGOAL Lisp Instructions / Instructions Lisp OpenGOAL

> **Bilingual reference / Référence bilingue** — [🇬🇧 English](#-english) · [🇫🇷 Français](#-français)
>
> **What this file is / Rôle de ce fichier**
>
> 🇬🇧 The **source of truth** for how to write OpenGOAL (GOAL) Lisp for Jak 2. Every
> instruction here is **verified** — it has been compiled and seen working in game.
> Consult it *before* writing or changing any `.gc` file so you never invent an
> instruction that does not exist. Each entry says, in plain words, what a block
> does, gives one commented example, and lists the traps.
>
> 🇫🇷 La **source de vérité** pour écrire du Lisp OpenGOAL (GOAL) pour Jak 2. Chaque
> instruction ici est **vérifiée** — elle a été compilée et vue fonctionner en jeu.
> À consulter *avant* d'écrire ou de modifier un fichier `.gc`, pour ne jamais
> inventer une instruction qui n'existe pas. Chaque entrée explique, en mots simples,
> ce que fait un bloc, donne un exemple commenté, et liste les pièges.
>
> **Also read / À lire aussi:** [`engine_generic_concepts.md`](engine_generic_concepts.md)
> (memory, heaps, DGOs, process life cycle / mémoire, heaps, DGO, cycle de vie).
>
> **Zero-hallucination contract / Contrat zéro hallucination**
>
> 🇬🇧 Only 100%-verified instructions belong here. No speculation, no "should work".
> If you are unsure, test it in the REPL first, then add it. New entries are landed
> **on `master-dev` only** — see [How to contribute](#how-to-contribute--comment-contribuer).
>
> 🇫🇷 Seules les instructions vérifiées à 100 % figurent ici. Pas de spéculation, pas
> de « devrait marcher ». En cas de doute, testez d'abord au REPL, puis ajoutez.
> Les nouvelles entrées sont intégrées **sur `master-dev` uniquement** — voir
> [Comment contribuer](#how-to-contribute--comment-contribuer).

---

<a name="-english"></a>
<a name="-français"></a>

## A — Vocabulary / Vocabulaire

| Term | 🇬🇧 Meaning | 🇫🇷 Signification |
|---|---|---|
| **GOAL** | Naughty Dog's Lisp dialect, compiled to native x86-64 by OpenGOAL. All game logic (`goal_src/**/*.gc`). | Le dialecte Lisp de Naughty Dog, compilé en x86-64 natif par OpenGOAL. Toute la logique du jeu (`goal_src/**/*.gc`). |
| **`goalc`** | The OpenGOAL compiler. REPL (`task repl`) or batch (`-c "(...)"`). | Le compilateur OpenGOAL. REPL (`task repl`) ou batch (`-c "(...)"`). |
| **`gk`** | The C++ runtime ("game kernel") that runs the compiled code. | Le runtime C++ (« game kernel ») qui exécute le code compilé. |
| **`(mi)`** | REPL command: incremental compile + hot-reload the running game. | Commande REPL : compilation incrémentale + rechargement à chaud du jeu. |
| **process** | Lightweight cooperative task with its own stack/heap. | Tâche coopérative légère avec sa propre pile/son propre heap. |
| **`process-drawable`** | A process that also has a 3D model + transform (`engine/process-drawable/process-drawable.gc`). | Un processus qui a aussi un modèle 3D + une transformation. |
| **`*target*`** | The global symbol pointing at the player process (Jak). | Le symbole global qui pointe sur le processus joueur (Jak). |
| **`self` / `pp`** | Inside a `behavior`: `self` = the process; `(with-pp ...)` binds `pp` = the process pointer. | Dans un `behavior` : `self` = le processus ; `(with-pp ...)` lie `pp` = le pointeur de processus. |
| **state** | A named node of a process's state machine: `:event`, `:code`, `:post`. | Un nœud nommé de la machine à états d'un processus : `:event`, `:code`, `:post`. |
| **`ja`** | Family of macros that drive skeletal animation ("joint animation"). | Famille de macros qui pilotent l'animation squelettique (« joint animation »). |
| **art-group** | A named bundle of a model's skeleton + geometry + animations. | Un paquet nommé : squelette + géométrie + animations d'un modèle. |
| **DGO** | On-disk package of compiled objects loaded as one unit. | Paquet disque d'objets compilés chargé d'un bloc. |

---

## B — Verified instruction blocks / Blocs d'instructions vérifiés

### B1 — Define a custom actor type / Définir un type d'acteur custom

> 🇬🇧 `deftype` declares a new type. For something that moves and is drawn, derive
> from `process-drawable` (or `process-focusable` for something the camera/AI can
> target). Extra fields go in the first list; `:state-methods` pre-declares the
> states this type can be in.
>
> 🇫🇷 `deftype` déclare un nouveau type. Pour quelque chose qui bouge et s'affiche,
> dérivez de `process-drawable` (ou `process-focusable` pour une cible caméra/IA).
> Les champs supplémentaires vont dans la première liste ; `:state-methods`
> pré-déclare les états possibles de ce type.

```lisp
;; EN: a minimal custom actor with two fields and two states
;; FR: un acteur custom minimal avec deux champs et deux états
(deftype my-actor (process-drawable)
  ((hp        int32)          ;; EN: custom field / FR: champ custom
   (wake-time time-frame))    ;; EN: a timestamp field / FR: un champ horodatage
  (:state-methods
    idle
    active))
```

- 🇬🇧 **Trap:** the parent type must already be known — its file must be earlier in
  the `.gp` include list. See [D1](#d1--symbol-and-load-order--ordre-des-symboles-et-du-chargement).
- 🇫🇷 **Piège :** le type parent doit déjà être connu — son fichier doit être plus
  haut dans la liste d'inclusion du `.gp`. Voir [D1](#d1--symbol-and-load-order--ordre-des-symboles-et-du-chargement).

### B2 — Define a state / Définir un état

> 🇬🇧 `defstate` fills one state of a type. The three parts:
> `:event` handles messages sent to the process; `:code` is the behaviour loop;
> `:post` runs every frame after `:code` (usually `ja-post` to flush animation).
> Add `:virtual #t` when the state overrides a parent's state and must dispatch
> through the vtable.
>
> 🇫🇷 `defstate` remplit un état d'un type. Les trois parties :
> `:event` traite les messages envoyés au processus ; `:code` est la boucle de
> comportement ; `:post` s'exécute chaque frame après le `:code` (en général
> `ja-post` pour appliquer l'animation). Ajoutez `:virtual #t` quand l'état surcharge
> celui d'un parent et doit passer par la vtable.

```lisp
(defstate idle (my-actor)
  :virtual #t
  ;; EN: react to messages / FR: réagir aux messages
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack)
       (go-virtual active))))       ;; EN: switch state on hit / FR: changer d'état si touché
  ;; EN: the loop: play the idle anim forever, yielding each frame
  ;; FR: la boucle : jouer l'anim idle en boucle, en rendant la main chaque frame
  :code (behavior ()
    (loop
      ;; my-actor-idle-ja = the animation symbol from this actor's art-group
      ;; my-actor-idle-ja = le symbole d'animation de l'art-group de cet acteur
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))))
  :post ja-post)
```

- 🇬🇧 `(go active)` vs `(go-virtual active)`: `go` jumps to the state named in *this*
  type; `go-virtual` dispatches through the vtable so a subclass's override wins.
  Use `go-virtual` for states declared in `:state-methods`.
- 🇫🇷 `(go active)` vs `(go-virtual active)` : `go` saute vers l'état nommé dans *ce*
  type ; `go-virtual` passe par la vtable pour que la surcharge d'une sous-classe
  l'emporte. Utilisez `go-virtual` pour les états déclarés dans `:state-methods`.
- 🇬🇧 **Residency trap:** if this actor is spawned by an always-resident system,
  every `:virtual #t` state must live in a resident file — see
  [`engine_generic_concepts.md` §6](engine_generic_concepts.md).
- 🇫🇷 **Piège de résidence :** si cet acteur est instancié par un système toujours
  résident, chaque état `:virtual #t` doit vivre dans un fichier résident — voir
  [`engine_generic_concepts.md` §6](engine_generic_concepts.md).

### B3 — Drive animation: the `ja` macros / Piloter l'animation : les macros `ja`

> 🇬🇧 A skeleton is a tree of joints; an animation is a stream of joint poses per
> frame. You do not move joints by hand — you tell a **channel** (usually channel 0)
> which animation to play and how fast to advance it, once per frame, then let
> `ja-post` push the result to the renderer.
>
> | Macro | 🇬🇧 What it does | 🇫🇷 Ce qu'elle fait |
> |---|---|---|
> | `(ja-no-eval :group! G :num! (seek! MAX) :frame-num F)` | Start channel 0 on animation `G` at frame `F`; set its target advance. | Démarre le canal 0 sur l'animation `G` à la frame `F` ; fixe sa cible d'avancement. |
> | `(ja :num! (seek!))` | Advance the current animation one frame toward the target. | Fait avancer l'animation courante d'une frame vers la cible. |
> | `(ja-done? 0)` | `#t` when channel 0 reached the end of its clip. | `#t` quand le canal 0 a atteint la fin de son clip. |
> | `(ja-aframe N 0)` | Read/seek to a specific frame number on channel 0. | Lire/aller à une frame précise sur le canal 0. |
> | `(suspend)` | Yield to the engine for this frame (like `yield`). | Rendre la main au moteur pour cette frame (comme `yield`). |
> | `ja-post` | State `:post` helper: flush the pose + collision. | Aide de `:post` : appliquer la pose + la collision. |
>
> 🇫🇷 Un squelette est un arbre de joints ; une animation est un flux de poses de
> joints par frame. On ne bouge pas les joints à la main — on indique à un **canal**
> (en général le canal 0) quelle animation jouer et à quelle vitesse l'avancer, une
> fois par frame, puis `ja-post` envoie le résultat au moteur de rendu.

```lisp
;; EN: play an animation once, from start to end, then continue
;; FR: jouer une animation une fois, du début à la fin, puis continuer
(ja-no-eval :group! my-anim-ja :num! (seek!) :frame-num 0.0)
(until (ja-done? 0)
  (suspend)                ;; EN: give the frame back to the engine / FR: rendre la frame au moteur
  (ja :num! (seek!)))      ;; EN: step the animation forward / FR: avancer l'animation
```

- 🇬🇧 **Trap:** forgetting `(suspend)` inside an animation loop freezes the game — the
  process never yields.
- 🇫🇷 **Piège :** oublier `(suspend)` dans une boucle d'animation gèle le jeu — le
  processus ne rend jamais la main.

### B4 — Skeletons & joints / Squelettes & joints

> 🇬🇧 The joint subsystem is `cspace` / `joint-control` (`engine/anim/joint.gc`). A
> process's live joint transforms are reachable through its `node-list`. You rarely
> need direct joint access — prefer animations (B3) and `joint-mod` helpers — but it
> exists.
>
> 🇫🇷 Le sous-système de joints est `cspace` / `joint-control` (`engine/anim/joint.gc`).
> Les transformations de joints en direct d'un processus sont accessibles via son
> `node-list`. Vous avez rarement besoin d'un accès direct — préférez les animations
> (B3) et les aides `joint-mod` — mais c'est possible.

```lisp
;; EN: number of joints on a live process (useful to compare two skeletons)
;; FR: nombre de joints d'un processus vivant (utile pour comparer deux squelettes)
(-> self node-list length)

;; EN: a joint's world transform matrix, by index
;; FR: la matrice de transformation monde d'un joint, par index
(-> self node-list data 5 bone transform)
```

- 🇬🇧 **Trap:** joint **indices** are skeleton-specific. Code that pokes joint `5` of
  `skel-jchar` will poke a *different* body part on another skeleton. See [C4](#c4--live-re-skinning-a-process--reskin-à-chaud-dun-processus).
- 🇫🇷 **Piège :** les **indices** de joints sont propres à un squelette. Du code qui
  touche le joint `5` de `skel-jchar` touchera une *autre* partie du corps sur un
  autre squelette. Voir [C4](#c4--live-re-skinning-a-process--reskin-à-chaud-dun-processus).

### B5 — Bind a model to a process: `initialize-skeleton` / Lier un modèle à un processus

> 🇬🇧 `initialize-skeleton` is what a `process-drawable` calls once at init to bind
> its mesh + skeleton + animation set. It takes a resolved `skeleton-group`.
> `initialize-skeleton-by-name` takes a plain string and does the lookup for you.
> It is *not* restricted to first-time init: calling it again on a live process
> rebinds its look in place (a "live re-skin") — the process keeps its identity,
> position and handlers.
>
> 🇫🇷 `initialize-skeleton` est ce qu'un `process-drawable` appelle une fois à
> l'init pour lier son maillage + squelette + jeu d'animations. Elle prend un
> `skeleton-group` déjà résolu. `initialize-skeleton-by-name` prend une simple chaîne
> et fait la résolution pour vous. Elle n'est *pas* limitée à la première init :
> l'appeler à nouveau sur un processus vivant relie son apparence sur place (un
> « reskin à chaud ») — le processus garde son identité, sa position et ses handlers.

```lisp
;; EN: standard init — resolve the art-group from the current level, then bind
;; FR: init standard — résoudre l'art-group depuis le niveau courant, puis lier
(initialize-skeleton
  this
  (the-as skeleton-group (art-group-get-by-name *level* "skel-my-actor" (the-as (pointer uint32) #f)))
  (the-as pair 0))

;; EN: shorthand when you only have the name / FR: raccourci quand on n'a que le nom
(initialize-skeleton-by-name this "skel-my-actor")
```

- 🇬🇧 **Multi-DGO trap:** the lookup uses `(-> this level)`. If a parent in level A
  spawns a child whose art lives in level B, set `(-> this level)` **and**
  `(-> pp level)` to level B *before* calling `initialize-skeleton`, or the child
  crashes into `:state process-drawable-art-error "art-group"`.
- 🇫🇷 **Piège multi-DGO :** la résolution utilise `(-> this level)`. Si un parent du
  niveau A instancie un enfant dont l'art est dans le niveau B, réglez
  `(-> this level)` **et** `(-> pp level)` sur le niveau B *avant* d'appeler
  `initialize-skeleton`, sinon l'enfant crashe dans
  `:state process-drawable-art-error "art-group"`.

```lisp
;; EN: fix for a child whose art-group is in another level DGO
;; FR: correctif pour un enfant dont l'art-group est dans un autre DGO de niveau
(when (= (level-status *level* 'lwidea) 'active)
  (set! (-> this level) (level-get *level* 'lwidea))
  (set! (-> pp   level) (level-get *level* 'lwidea)))
(initialize-skeleton this <skeleton-group> (the-as pair 0))
```

### B6 — Play a sound / Jouer un son

> 🇬🇧 `sound-play` is the simple form. `sound-play-by-name` gives control over
> volume, pitch, position and group.
>
> 🇫🇷 `sound-play` est la forme simple. `sound-play-by-name` donne le contrôle du
> volume, du pitch, de la position et du groupe.

```lisp
;; EN: fire-and-forget SFX by name / FR: SFX simple par nom
(sound-play "menu-select")

;; EN: full control (volume 1024 = nominal, group sfx, positional flag #t)
;; FR: contrôle complet (volume 1024 = nominal, groupe sfx, drapeau positionnel #t)
(sound-play-by-name
  (static-sound-name "my-sound")
  (new-sound-id)
  1024 0 0
  (sound-group sfx)
  #t)
```

- 🇬🇧 **Trap:** the sound name must exist in a loaded sound bank. Custom sounds need
  their bank extracted/loaded — see the custom-audio pipeline in `docs/modding/tools/`.
- 🇫🇷 **Piège :** le nom du son doit exister dans une banque sonore chargée. Les sons
  custom nécessitent l'extraction/le chargement de leur banque — voir la pipeline
  audio custom dans `docs/modding/tools/`.

### B7 — Collision basics / Bases de la collision

> 🇬🇧 A `process-drawable`'s collision lives in its `root` field (a `collide-shape`
> or `trsqv`). Surface behaviour (slippery, deadly, etc.) comes from `pat-surface`
> data (`engine/collide/pat-h.gc`). To make a corpse stop blocking movement, clear
> its collide specs.
>
> 🇫🇷 La collision d'un `process-drawable` vit dans son champ `root` (un
> `collide-shape` ou un `trsqv`). Le comportement de surface (glissant, mortel, etc.)
> vient des données `pat-surface` (`engine/collide/pat-h.gc`). Pour qu'un cadavre
> arrête de bloquer les déplacements, effacez ses specs de collision.

```lisp
;; EN: disable an actor's collision (e.g. on death)
;; FR: désactiver la collision d'un acteur (ex. à la mort)
(let ((prim (-> self root root-prim)))
  (set! (-> prim prim-core collide-as)   (collide-spec))
  (set! (-> prim prim-core collide-with) (collide-spec)))
```

### B8 — Custom art-groups & dynamic animation linking (`link-art!`) / Art-groups custom & liaison dynamique

> 🇬🇧 To add animations imported from a `.glb` into a resident character art-group
> (`jakb-ag`, `daxter-ag`) *without* recompiling the hundreds of native animations:
> `build-actor` (in `game.gp`) bakes target slot indices with `:master-art-group` /
> `:master-ag-map`; `link-art!` (`loader.gc`) attaches the custom group's entries
> into those slots.
>
> 🇫🇷 Pour ajouter des animations importées d'un `.glb` dans un art-group de
> personnage résident (`jakb-ag`, `daxter-ag`) *sans* recompiler les centaines
> d'animations natives : `build-actor` (dans `game.gp`) inscrit les index de slots
> cibles via `:master-art-group` / `:master-ag-map` ; `link-art!` (`loader.gc`)
> attache les entrées du groupe custom dans ces slots.

```lisp
;; EN: hook link-art! in art-group::relocate (engine/anim/joint.gc) — NOT in gameplay
;; FR: accrocher link-art! dans art-group::relocate (engine/anim/joint.gc) — PAS en gameplay
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "jakb-my-import"))
      (link-art! this)))
```

- 🇬🇧 **Trap:** never call `link-art!` during gameplay (e.g. from a state `init`):
  the level art-group arrays are not in a stable state and you risk a memory crash.
  The safe hook is `art-group::relocate`.
- 🇫🇷 **Piège :** ne jamais appeler `link-art!` pendant le gameplay (ex. depuis
  l'`init` d'un état) : les tableaux d'art-groups du niveau ne sont pas dans un état
  stable, risque de crash mémoire. Le point d'accroche sûr est `art-group::relocate`.

### B9 — Send an event / Envoyer un événement

> 🇬🇧 `send-event` delivers a message to another process's current `:event` handler.
> It uses a **stack** message block — no heap allocation — so it is safe to call at
> any time, including while the player crosses a level/district boundary.
>
> 🇫🇷 `send-event` délivre un message au handler `:event` courant d'un autre
> processus. Il utilise un bloc message sur la **pile** — aucune allocation heap —
> donc son appel est sûr à tout moment, y compris quand le joueur franchit une
> frontière de niveau/quartier.

```lisp
;; EN: ask the traffic manager to recycle a vehicle type (no alloc, no respawn storm)
;; FR: demander au traffic manager de recycler un type de véhicule (sans alloc, sans pluie de spawns)
(when *traffic-manager*
  (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-0)))
```

- 🇬🇧 **Trap:** guard managers that may not exist. `*traffic-manager*` is `#f`
  outside the city — always `(when *traffic-manager* ...)`.
- 🇫🇷 **Piège :** les gestionnaires qui peuvent ne pas exister. `*traffic-manager*`
  vaut `#f` hors de la ville — toujours `(when *traffic-manager* ...)`.

### B10 — Generic enemy death effect (`do-effect` / `death-default`) / Effet de mort générique

> 🇬🇧 Many Jak 2 enemies dissolve into purple particles tracing the mesh, with a
> "fizz" sound. This is a reusable engine system, not a per-bone emitter. Trigger it
> from any skeleton-having `process-drawable`'s death code with one call. The
> `effect-control` at `(-> self skel effect)` is created for you inside
> `initialize-skeleton`.
>
> 🇫🇷 Beaucoup d'ennemis de Jak 2 se dissolvent en particules violettes qui tracent
> le maillage, avec un son de « fizz ». C'est un système moteur réutilisable, pas un
> émetteur par os. On le déclenche depuis le code de mort de n'importe quel
> `process-drawable` doté d'un squelette, en un appel. L'`effect-control` en
> `(-> self skel effect)` est créé pour vous dans `initialize-skeleton`.

```lisp
;; EN: canonical death code (pattern from wasp.gc die-now state)
;; FR: code de mort canonique (pattern de l'état die-now de wasp.gc)
:code (behavior ()
  (dying self)                                            ;; EN: plays enemy sound-die + drops gems / FR: joue sound-die + drop des gemmes
  (let ((prim (-> self root root-prim)))                  ;; EN: stop the corpse blocking things / FR: le cadavre ne bloque plus rien
    (set! (-> prim prim-core collide-as)   (collide-spec))
    (set! (-> prim prim-core collide-with) (collide-spec)))
  (set! (-> self hit-points) 0)
  (do-effect (-> self skel effect) 'death-default 0.0 -1) ;; EN: spawn the purple dissolve + "enemy-fizz" / FR: spawn la dissolution violette + "enemy-fizz"
  (suspend-for (seconds 1))                               ;; EN: MUST wait — particles spawn while alive / FR: DOIT attendre — les particules spawn tant qu'il est vivant
  (send-event self 'death-end)
  (cleanup-for-death self))
```

- 🇬🇧 **Trap:** do **not** call `cleanup-for-death` right after `do-effect` — the
  particle spawn is driven per-frame while the process is still drawing; killing it
  immediately makes the entity vanish silently. Also: needs a skeleton.
- 🇫🇷 **Piège :** ne **pas** appeler `cleanup-for-death` juste après `do-effect` —
  le spawn des particules est piloté frame par frame tant que le processus s'affiche ;
  le tuer immédiatement fait disparaître l'entité en silence. Aussi : nécessite un
  squelette.
- 🇬🇧 Presets: `death-default` (purple, generic kill), `death-seed` (orange, life-seed
  scene), `death-warp-in`/`out` (blue-purple, warp gate — not a kill).
- 🇫🇷 Presets : `death-default` (violet, mort générique), `death-seed` (orange, scène
  life-seed), `death-warp-in`/`out` (bleu-violet, warp gate — pas une mort).

### B11 — Register a Debug ▸ Mods toggle / Enregistrer une bascule Debug ▸ Mods

> 🇬🇧 Every mod must expose an on/off switch under **Debug ▸ Mods**. You never edit
> `default-menu*.gc` — you call `mods-menu-register` from one of your mod's own
> compiled `.gc` files. See the full guide and copy-paste template:
> [`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md) and
> [`docs/modding/templates/mod_debug_menu.template.gc`](templates/mod_debug_menu.template.gc).
>
> 🇫🇷 Chaque mod doit exposer un interrupteur on/off sous **Debug ▸ Mods**. On
> n'édite jamais `default-menu*.gc` — on appelle `mods-menu-register` depuis un des
> fichiers `.gc` compilés du mod. Voir le guide complet et le template à copier :
> [`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md) et
> [`docs/modding/templates/mod_debug_menu.template.gc`](templates/mod_debug_menu.template.gc).

```lisp
(declare-file (debug))

;; EN: one prefixed symbol per option; its `value` slot holds the boolean
;; FR: un symbole préfixé par option ; son slot `value` porte le booléen
(define *mod-my-slug-enable* #f)

;; EN: builder — pure, returns this mod's submenu node
;; FR: builder — pur, renvoie le nœud sous-menu du mod
(defun mod-my-slug-build-menu ((ctx debug-menu-context))
  (debug-menu-make-from-template ctx
    '(menu "my-slug"
       (flag "Enable" *mod-my-slug-enable* dm-boolean-toggle-pick-func))))

;; EN: register at file load (top-level) / FR: enregistrer au chargement du fichier (top-level)
(mods-menu-register "my-slug" mod-my-slug-build-menu)
```

- 🇬🇧 Prefix every symbol with your mod slug (`*mod-<slug>-*`, `mod-<slug>-*`) to
  avoid collisions between mod branches. Add `"my-slug-menu.o"` to your `.gd`
  **after** `"mods-menu.o"`.
- 🇫🇷 Préfixez chaque symbole avec le slug du mod (`*mod-<slug>-*`, `mod-<slug>-*`)
  pour éviter les collisions entre branches. Ajoutez `"my-slug-menu.o"` à votre `.gd`
  **après** `"mods-menu.o"`.

---

## C — Game-specific verified subsystems / Sous-systèmes vérifiés propres à Jak 2

### C1 — Vehicles: flags, grab rails, driver methods / Véhicules : drapeaux, barres d'accroche, méthodes de conduite

> 🇬🇧 All ambient and player vehicles derive from `vehicle`
> (`goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc`). The
> `rigid-body-vehicle-constants` `:flags` bitfield configures gameplay:
>
> | Bit | Hex | Effect |
> |---|---|---|
> | 2 | `#x04` | `guard-vehicle` — Crimson Guard asset (Hellcat, Guard Bike). |
> | 3 | `#x08` | `vehicle` — standard vehicle physics. |
> | 5 | `#x20` | `allow-gun` — Jak can draw & fire guns while driving. |
> | 6 | `#x40` | `allow-flight-zones` — R2 switches low/high altitude corridors. |
>
> `#x6c` = flight + guns on a guard vehicle.
>
> 🇫🇷 Tous les véhicules ambiants et pilotables dérivent de `vehicle`. Le champ de
> bits `:flags` de `rigid-body-vehicle-constants` configure le gameplay (voir table).
> `#x6c` = vol + armes sur un véhicule de garde.

```lisp
;; EN: unarmed guard-derived vehicle — override method-94 or it SIGSEGVs on the
;;     missing turret when the player takes control
;; FR: véhicule dérivé de garde non armé — surcharger method-94 sinon SIGSEGV sur la
;;     tourelle absente quand le joueur prend le contrôle
(defmethod vehicle-method-94 ((this paddywagon))
  ((method-of-type vehicle vehicle-method-94) this)
  0
  (none))
```

- 🇬🇧 Grab rails: define `:grab-rail-count` + `:grab-rail-array` for long-range
  edge-grab boarding (Triangle → hang → Cross → cockpit). Small bikes use
  `:grab-rail-array #f` and seat Jak instantly.
- 🇫🇷 Barres d'accroche : définir `:grab-rail-count` + `:grab-rail-array` pour
  l'embarquement par accroche longue portée (Triangle → suspension → Croix →
  cockpit). Les petites motos utilisent `:grab-rail-array #f` et installent Jak
  instantanément.
- 🇬🇧 Also see the flight control-point / `cm-offset-joint` "turtle-flip" gotcha in
  git history for `jak2/features/transport_traffic`.
- 🇫🇷 Voir aussi le piège du control-point de vol / `cm-offset-joint` (« turtle-flip »)
  dans l'historique git de `jak2/features/transport_traffic`.

### C2 — Traffic manager / Gestionnaire de trafic

> 🇬🇧 `*traffic-manager*` owns ambient city actors. Change large dynamic state by
> **event**, not by hand-spawning: `(send-event *traffic-manager* 'deactivate-by-type
> (traffic-type ...))` recycles existing actor slots. When spawning ejected riders,
> always check `(when (-> spawn-params nav-mesh) ...)` first — a missing nav-mesh
> causes an infinite spawn-retry loop and memory exhaustion.
>
> 🇫🇷 `*traffic-manager*` possède les acteurs urbains ambiants. Changez un gros état
> dynamique par **événement**, pas par spawn manuel :
> `(send-event *traffic-manager* 'deactivate-by-type (traffic-type ...))` recycle les
> slots d'acteurs existants. Pour spawn des passagers éjectés, vérifiez toujours
> `(when (-> spawn-params nav-mesh) ...)` d'abord — un nav-mesh absent provoque une
> boucle infinie de re-spawn et l'épuisement mémoire.

### C3 — Virtual state / method residency / Résidence des états et méthodes virtuels

> 🇬🇧 See [`engine_generic_concepts.md` §6](engine_generic_concepts.md).
> Jak 2 hits this most with traffic/vehicle actors: define **all** their `:virtual #t`
> states and methods in a resident file (`vehicle.gc`, `car.gc`), never in a mission
> DGO. Symptom in the log: `sending traffic-on to #<... :state process-drawable-art-error>`
> or an actor stuck `inactive`/invisible in free-roam.
>
> 🇫🇷 Voir [`engine_generic_concepts.md` §6](engine_generic_concepts.md).
> Jak 2 y est confronté surtout avec les acteurs de trafic/véhicules : définir
> **tous** leurs états et méthodes `:virtual #t` dans un fichier résident
> (`vehicle.gc`, `car.gc`), jamais dans un DGO de mission. Symptôme dans le log :
> `sending traffic-on to #<... :state process-drawable-art-error>` ou un acteur bloqué
> `inactive`/invisible en jeu libre.

### C4 — Live re-skinning a process / Reskin à chaud d'un processus

> 🇬🇧 Calling `initialize-skeleton(-by-name)` again on a live process swaps its mesh
> and animation set while keeping its identity. Proven safe in the base game on
> reconfigurable objects (`widow-extras.gc`, `metalkor-setup.gc`). **The risk is
> `target` only:** `target` sets up `joint-mod`s (neck look-at, gun aim, IK) against
> *fixed joint indices* of `skel-jchar`. Re-skinning `target` to a skeleton with a
> different joint layout makes those `joint-mod`s index the wrong joint or go out of
> bounds. A stub process with no `joint-mod`s has nothing to desync.
>
> 🇫🇷 Rappeler `initialize-skeleton(-by-name)` sur un processus vivant échange son
> maillage et son jeu d'animations en gardant son identité. Prouvé sûr dans le jeu de
> base sur des objets reconfigurables (`widow-extras.gc`, `metalkor-setup.gc`). **Le
> risque ne concerne que `target` :** `target` configure des `joint-mod` (look-at du
> cou, visée, IK) sur des *indices de joints fixes* de `skel-jchar`. Reskinner
> `target` vers un squelette à disposition de joints différente fait indexer le
> mauvais joint ou sortir des limites. Un processus-relais sans `joint-mod` n'a rien
> à désynchroniser.

```lisp
;; EN: from the REPL — check whether the joint count actually changed before/after
;; FR: depuis le REPL — vérifier si le nombre de joints a changé avant/après
(-> *target* node-list length)
(initialize-skeleton-by-name *target* "skel-crimson-guard-level")
(-> *target* node-list length)
```

### C5 — Merc geometry / FR3 residency / Géométrie merc & résidence FR3

> 🇬🇧 Imported models built with `build-actor` produce a merc art-group whose
> geometry (`.fr3`) must be resident wherever the actor is drawn. If an actor is
> spawned globally but its `.fr3` is level-scoped, it renders as nothing or crashes
> on relocate. Keep custom-model geometry in a resident art-group, or bind the
> process's level to the level that owns the geometry (see [B5](#b5--bind-a-model-to-a-process-initialize-skeleton--lier-un-modèle-à-un-processus)).
>
> 🇫🇷 Les modèles importés construits avec `build-actor` produisent un art-group merc
> dont la géométrie (`.fr3`) doit être résidente partout où l'acteur est affiché. Si
> un acteur est instancié globalement mais son `.fr3` est propre à un niveau, il
> s'affiche vide ou crashe au relocate. Gardez la géométrie des modèles custom dans
> un art-group résident, ou liez le niveau du processus au niveau qui possède la
> géométrie (voir [B5](#b5--bind-a-model-to-a-process-initialize-skeleton--lier-un-modèle-à-un-processus)).

---

## D — Lisp-level known pitfalls / Pièges connus au niveau Lisp

### D1 — Symbol and load order / Ordre des symboles et du chargement

- 🇬🇧 Parent types **must** be declared before child types — order files correctly in
  the `.gp` include list. A forward reference to an undeclared type is a compile
  error; a forward reference to an unloaded *virtual* slot is a silent runtime
  no-op (see [B2](#b2--define-a-state--définir-un-état)).
- 🇫🇷 Les types parents **doivent** être déclarés avant les types enfants — ordonnez
  les fichiers correctement dans la liste d'inclusion du `.gp`. Une référence avant à
  un type non déclaré est une erreur de compilation ; une référence avant à un slot
  *virtuel* non chargé est un no-op runtime silencieux (voir [B2](#b2--define-a-state--définir-un-état)).

### D2 — REPL ghost memory / Mémoire fantôme du REPL

- 🇬🇧 After large changes, do a **cold restart** of the REPL and a fresh boot. Hot
  reload (`(mi)`) keeps stale state; a change can appear to work only because the old
  code is still resident.
- 🇫🇷 Après de gros changements, faites un **redémarrage à froid** du REPL et un boot
  neuf. Le hot reload (`(mi)`) conserve l'état résiduel ; un changement peut sembler
  marcher seulement parce que l'ancien code est encore résident.

### D3 — A clean compile is not a validation / Une compilation propre n'est pas une validation

- 🇬🇧 Always `(mi)` → `task boot-game` → check `log/jak2.*.log` for
  `bad address` / `not a valid object` / `unable to malloc` before declaring done.
- 🇫🇷 Toujours `(mi)` → `task boot-game` → vérifier `log/jak2.*.log` pour
  `bad address` / `not a valid object` / `unable to malloc` avant de déclarer terminé.

### D4 — Native non-regression / Non-régression native

- 🇬🇧 A mod must not change default game behaviour unless its spec explicitly
  requires it. Ship changes **off by default**, gated behind the mod's Debug ▸ Mods
  toggle ([B11](#b11--register-a-debug--mods-toggle--enregistrer-une-bascule-debug--mods)).
- 🇫🇷 Un mod ne doit pas changer le comportement par défaut du jeu sauf si son
  cahier des charges l'exige explicitement. Livrez les changements **désactivés par
  défaut**, derrière la bascule Debug ▸ Mods du mod ([B11](#b11--register-a-debug--mods-toggle--enregistrer-une-bascule-debug--mods)).

---

## E — ➕ Append new verified entries below / Ajouter les nouvelles entrées vérifiées ci-dessous

> 🇬🇧 One numbered block at a time, same shape as section B/C. **`master-dev` only.**
> Never reflow the entries above — append.
>
> 🇫🇷 Un bloc numéroté à la fois, même forme que la section B/C. **`master-dev`
> uniquement.** Ne jamais reformater les entrées ci-dessus — ajouter à la fin.

<!-- ➕ APPEND NEW VERIFIED ENTRIES BELOW THIS LINE — master-dev only, one block at a time -->

---

## How to contribute / Comment contribuer

> 🇬🇧 This file has **one source of truth: `master-dev`**. That is what keeps
> parallel mod branches from ever conflicting on it. When you verify a new
> instruction on a mod branch:
>
> 1. `task modding-land-doc` — stashes your work, checks out `master-dev`, pulls,
>    lets you append the entry, commits `docs(lisp): <slug> (AI-assisted)`, pushes,
>    returns you to your branch, re-syncs. (Or do it by hand.)
> 2. Back on your branch: `task modding-sync-docs`.
>
> Mod-*feature*-specific notes (what your mod changed, why) do **not** go here — they
> go in your mod branch's root `README.md` "Modding Changes Log".
>
> 🇫🇷 Ce fichier a **une seule source de vérité : `master-dev`**. C'est ce qui évite
> tout conflit entre branches de mods développées en parallèle. Quand vous vérifiez
> une nouvelle instruction sur une branche de mod :
>
> 1. `task modding-land-doc` — met votre travail de côté (stash), bascule sur
>    `master-dev`, tire, vous laisse ajouter l'entrée, commit
>    `docs(lisp): <slug> (AI-assisted)`, pousse, vous ramène sur votre branche,
>    resynchronise. (Ou à la main.)
> 2. De retour sur votre branche : `task modding-sync-docs`.
>
> Les notes propres à une *fonctionnalité* de mod (ce que votre mod change, pourquoi)
> ne vont **pas** ici — elles vont dans le `README.md` racine de votre branche, dans
> le « Modding Changes Log ».
