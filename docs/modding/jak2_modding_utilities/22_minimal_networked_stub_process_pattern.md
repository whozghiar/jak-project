# Jak 2 — A Minimal Non-Interactive Stub Process / Un Processus-Relais Minimal et Non-Interactif

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/multiplayer`
> - **Last Updated / Dernière modification:** `jak2/features/multiplayer`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. When you want this

Sometimes you need a process that is *visible* — has a position, plays an animation, gets drawn —
but is not *interactive*: no collision, no AI, no combat, driven entirely by state that comes from
somewhere else (network data, a script, a recording). Building this on top of `process-drawable`
directly, skipping everything `target`/`nav-enemy`/etc. carry, keeps it cheap and simple to reason
about.

## 2. The template — `minnow`

`goal_src/jak2/levels/forest/fish.gc:26-78` is close to the minimal possible `process-drawable`:

```lisp
(deftype minnow (process-drawable)
  ()
  (:state-methods idle)
  )

(defbehavior minnow-init-by-other minnow ((arg0 object) (arg1 fish-type))
  (set! (-> self root) (new 'process 'trsqv))
  (set! (-> self root trans quad) (the-as uint128 0))
  (quaternion-identity! (-> self root quat))
  (vector-identity! (-> self root scale))
  (initialize-skeleton
    self
    (the-as skeleton-group (art-group-get-by-name *level* "skel-minnow" (the-as (pointer uint32) #f)))
    (the-as pair 0)
    )
  ;; ...
  (go-virtual idle)
  (none)
  )

(defstate idle (minnow)
  :virtual #t
  :code (behavior ()
    (until #f
      (ja-no-eval :group! minnow-idle-ja :num! (seek! max 5.0) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek! max 5.0))
        )
      )
    #f
    )
  :post ja-post
  )
  )
```

The essentials, in order:

1. **A bare `trsqv` root** (`(new 'process 'trsqv)`), not a `collide-shape`/`collide-shape-moving`.
   No collision setup at all — this object cannot be touched, pushed, or hit, and cannot touch
   anything itself.
2. **One `initialize-skeleton` call** at init, binding whatever skeleton it needs.
3. **A single state** that loops an animation with `ja-no-eval`/`ja` and finishes with `:post
   ja-post` — the standard "play this animation forever" idiom used throughout the codebase.

## 3. Extending it for externally-driven state

`goal_src/jak2/pc/multiplayer/remote-player.gc` (this mod) extends this exact template for a
process whose transform/animation/skin come from network packets rather than being self-contained:

- Extra fields hold the latest externally-supplied sample (`net-target-pos`, `net-target-quat`,
  `net-anim-state`, `net-skin-id`).
- A `set-net-sample!` method is the only way anything external touches the object - the owning
  manager process calls it once per frame with fresh data; the object itself never reaches out to
  fetch it. This keeps the stub process fully decoupled from *how* the state is produced (network,
  replay file, script - it would not care).
- The `idle` state, each frame, blends the current transform toward the latest sample
  (`vector-lerp!`/`quaternion-slerp!`) rather than snapping, and re-picks its `ja-no-eval` group
  only when the desired one actually changes (comparing against a stored `current-anim-group`
  field), instead of restarting animation every single frame.
- Re-skinning (see
  [21_live_reskinning_a_process_with_initialize-skeleton.md](21_live_reskinning_a_process_with_initialize-skeleton.md))
  only happens on the frame the skin id actually changes, guarded the same way.

## 4. Known pitfalls

- **No collide-shape means no `control` field access.** Code copy-pasted from a `target`/enemy
  example that reads `(-> self control trans)` will not compile on a bare-`trsqv` stub - use `(->
  self root trans)` instead (`root` is a `trsqv` on every `process-drawable`; `control` only
  exists on types that overlay a `collide-shape`-derived type there, like `target`).
- **`ja-no-eval :group!` takes an expression, not just a literal symbol** - it is fine to compute
  the desired group in a variable and pass that, as long as the variable actually holds a
  compiled `art-joint-anim` for a skeleton the object is currently bound to. Passing a group that
  belongs to a *different* skeleton than the one currently bound will misbehave.
- **Do not invent animation group names.** Every `-ja` symbol used must be a real, already-compiled
  animation group for the exact skeleton in use - grep the skeleton's owning file for `ja-no-eval`
  calls to find real ones rather than guessing a plausible-sounding name (which will fail to
  compile).

## 5. Verification steps

1. Spawn the process and confirm it appears in the correct starting position with the right
   skeleton bound (not T-posed).
2. Feed it a changing sample each frame (or, for a hand test, hardcode a moving target) and confirm
   the lerp/slerp tracks smoothly rather than snapping or jittering.
3. Confirm nothing about the object registers as collidable in-game - walking through it should do
   nothing.

---

# 🇫🇷 Version Française

## 1. Quand utiliser ce patron

Il arrive qu'on ait besoin d'un processus *visible* — avec une position, jouant une animation,
affiché à l'écran — mais non *interactif* : pas de collision, pas d'IA, pas de combat, entièrement
piloté par un état venant d'ailleurs (données réseau, script, enregistrement). Le construire
directement sur `process-drawable`, en évitant tout ce que `target`/`nav-enemy`/etc. embarquent,
le garde léger et simple à raisonner.

## 2. Le patron — `minnow`

`goal_src/jak2/levels/forest/fish.gc:26-78` est proche du `process-drawable` minimal possible :

```lisp
(deftype minnow (process-drawable)
  ()
  (:state-methods idle)
  )

(defbehavior minnow-init-by-other minnow ((arg0 object) (arg1 fish-type))
  (set! (-> self root) (new 'process 'trsqv))
  ;; ...
  (initialize-skeleton
    self
    (the-as skeleton-group (art-group-get-by-name *level* "skel-minnow" (the-as (pointer uint32) #f)))
    (the-as pair 0)
    )
  (go-virtual idle)
  (none)
  )
```

Les éléments essentiels, dans l'ordre :

1. **Une racine `trsqv` nue** (`(new 'process 'trsqv)`), pas un `collide-shape`/
   `collide-shape-moving`. Aucune configuration de collision — cet objet ne peut être touché,
   poussé, ni frappé, et ne peut lui-même toucher quoi que ce soit.
2. **Un seul appel `initialize-skeleton`** à l'initialisation, liant le squelette nécessaire.
3. **Un unique état** qui boucle une animation via `ja-no-eval`/`ja` et se termine par `:post
   ja-post` — l'idiome standard « jouer cette animation indéfiniment » utilisé dans tout le code
   source.

## 3. L'étendre pour un état piloté de l'extérieur

`goal_src/jak2/pc/multiplayer/remote-player.gc` (ce mod) étend exactement ce patron pour un
processus dont la transformation/animation/skin proviennent de paquets réseau plutôt que d'être
autonomes :

- Des champs supplémentaires stockent le dernier échantillon fourni de l'extérieur
  (`net-target-pos`, `net-target-quat`, `net-anim-state`, `net-skin-id`).
- Une méthode `set-net-sample!` est le seul moyen par lequel l'extérieur touche l'objet - le
  processus gestionnaire l'appelle une fois par frame avec des données fraîches ; l'objet
  lui-même ne va jamais les chercher. Cela garde le processus-relais totalement découplé de la
  *façon* dont l'état est produit (réseau, fichier de replay, script - peu importe).
- L'état `idle`, à chaque frame, interpole la transformation actuelle vers le dernier échantillon
  (`vector-lerp!`/`quaternion-slerp!`) plutôt que de la faire sauter, et ne recalcule son groupe
  `ja-no-eval` que lorsque celui désiré change réellement (comparaison avec un champ
  `current-anim-group` stocké), plutôt que de relancer l'animation à chaque frame.
- Le reskin (voir
  [21_live_reskinning_a_process_with_initialize-skeleton.md](21_live_reskinning_a_process_with_initialize-skeleton.md))
  ne se produit que sur la frame où l'id de skin change réellement, protégé de la même façon.

## 4. Pièges connus

- **Pas de `collide-shape` signifie pas d'accès au champ `control`.** Du code copié-collé depuis
  un exemple `target`/ennemi qui lit `(-> self control trans)` ne compilera pas sur un relais à
  `trsqv` nu - utiliser `(-> self root trans)` à la place (`root` est un `trsqv` sur tout
  `process-drawable` ; `control` n'existe que sur les types qui y superposent un type dérivé de
  `collide-shape`, comme `target`).
- **`ja-no-eval :group!` accepte une expression, pas seulement un symbole littéral** - il est tout
  à fait valide de calculer le groupe désiré dans une variable et de la passer, tant que cette
  variable contient bien un `art-joint-anim` compilé pour un squelette actuellement lié à l'objet.
  Passer un groupe appartenant à un squelette *différent* de celui actuellement lié se comportera
  mal.
- **Ne pas inventer de noms de groupe d'animation.** Chaque symbole `-ja` utilisé doit être un
  groupe d'animation réel, déjà compilé, pour le squelette exact utilisé - grepper le fichier
  propriétaire du squelette pour ses appels `ja-no-eval` afin d'en trouver de réels plutôt que de
  deviner un nom plausible (qui échouera à la compilation).

## 5. Étapes de vérification

1. Instancier le processus et vérifier qu'il apparaît à la bonne position de départ avec le bon
   squelette lié (pas en T-pose).
2. Lui fournir un échantillon changeant à chaque frame (ou, pour un test manuel, coder en dur une
   cible mobile) et vérifier que l'interpolation suit sans saut ni tremblement.
3. Vérifier que rien chez cet objet ne s'enregistre comme collidable en jeu - marcher au travers
   ne doit rien produire.
