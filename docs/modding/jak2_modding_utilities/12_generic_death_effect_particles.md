# Jak 2 — Generic Enemy Death Effect (Purple Skeleton-Dissolve Particles) / Effet de Mort Générique des Ennemis (Particules Violettes de Dissolution)

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/yakow_killable`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Generic Death Effect (`death-default`) — Purple Particles Tracing the Mesh/Skeleton Outline

### Context & Core Concepts
When many Jak II enemies (civilians, Crimson Guards, wasps, etc.) die, their model dissolves into purple/violet particles that appear to trace the outline of the mesh as it fades out, accompanied by a "fizz" sound. This is **not** a per-joint/bone particle emitter — it is a generic, reusable engine system built around a `death-info` data type and a handful of static presets, driven through the existing `effect-control` resource-tag dispatcher (`do-effect`).

- **Type:** `death-info` (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc:12-19`) — `vertex-skip`, `timer`, `overlap`, `effect` (a `sparticle-launcher` id), `sound` (a sound-bank name symbol).
- **Presets:** `death-default` (id `73`, purple, generic kill), `death-seed` (id `72`, orange/yellow, used for life-seed death scenes), `death-warp-in` / `death-warp-out` (id `74`, blue-purple, warp-gate teleport — not a kill).
- These are plain global `(define ...)` symbols, so `(-> 'death-default value)` **is already the `death-info` struct** — no per-actor resource tag needs to be declared to use it.

### Technical Implementation
1. **Trigger:** Call `(do-effect (-> self skel effect) 'death-default 0.0 -1)` from any `process-drawable`'s death code. `self skel effect` is an `effect-control` instance automatically created for every skeleton-having process-drawable inside `initialize-skeleton` (`goal_src/jak2/engine/process-drawable/process-drawable.gc:777`) — so this works for **any** enemy/NPC without extra setup, as long as `initialize-skeleton` was called (true for all `nav-enemy`/`enemy` subclasses).
2. **Dispatch:** `do-effect` (`effect-control.gc:272-585`) resolves `arg0`'s symbol value; when it is a `death-info`, it copies `vertex-skip`/`timer`/`overlap`/`effect` onto the process's `draw-control` (`death-vertex-skip`, `death-timer`, `death-timer-org`, `death-draw-overlap`, `death-effect` — fields declared in `goal_src/jak2/engine/data/art-h.gc:303-307`), plays the preset's `sound` via `play-effect-sound`, and sends the process a `'death-start` event (`effect-control.gc:531-576`).
3. **Per-frame mesh dissolve:** Every frame, `foreground-generic-merc-death` (`foreground.gc:728-752`) advances a randomized vertex stride (`death-vertex-skip`) through the skinned mesh and can start hiding triangles once the "overlap" threshold passes (visual erosion of the model). The actual vertex walk + world-space transform (via the current skinning matrices, so it inherently follows the animated pose) happens in the native `generic-merc-death` function — C++ port at `game/mips2c/jak2_functions/generic_merc.cpp:2470-2536`.
4. **Particle spawn:** For each sampled vertex, `merc-death-spawn` (`merc-death.gc:149-157`) looks up the launcher id (e.g. `73`) in `*part-id-table*` and calls `sp-launch-particles-death` (`sparticle-launcher.gc:486-489`) on `*sp-particle-system-2d*`. Launcher `73` chains into launcher `76` (`sparticle-motion-blur`), producing the drifting/fading trailing wisp look.
5. **Purple color values** (`merc-death.gc:116-132`, preset `death-default`): `:r 96.0-150.0 :g 32.0-64.0 :b 128.0-128.0 :a 128.0` — high/constant blue, low green, moderate red → violet/magenta.

### Concrete Annotated Code Example
The canonical minimal pattern (from `wasp.gc:1015-1033`, state `die-now`):
```lisp
:code (behavior ()
  (dying self)                                          ;; plays enemy-info's sound-die, spawns skull gems
  (let ((v1-3 (-> self root root-prim)))                 ;; clear collision so corpse stops blocking things
    (set! (-> v1-3 prim-core collide-as) (collide-spec))
    (set! (-> v1-3 prim-core collide-with) (collide-spec))
    )
  (set! (-> self hit-points) 0)
  (do-effect (-> self skel effect) 'death-default 0.0 -1) ;; spawn the purple dissolve + "enemy-fizz" sound
  (suspend-for (seconds 1))                               ;; let the ~1.25s vertex-skip timer play out
  (send-event self 'death-end)
  (cleanup-for-death self)
  )
```
Applied identically to `yakow.gc`'s `die` state (`goal_src/jak2/levels/city/farm/yakow.gc`), replacing a placeholder `group-land-poof-drt` dust-poof `part-tracker-spawn`.

### Known Pitfalls / Edge Cases
- **Don't skip the `suspend-for`:** the particle spawning is driven by `foreground-generic-merc-death`, which only runs while the process is still alive and drawing. Calling `cleanup-for-death` immediately after `do-effect` destroys the process before any particle ever spawns — the entity just vanishes silently. `death-default`'s `timer` is `0x4b` (75 game frames ≈ 1.25s @ 60 fps); `(suspend-for (seconds 1))` (as used by `wasp.gc`) is close enough in practice.
- **Requires a skeleton:** `(-> self skel effect)` is only populated for process-drawables that went through `initialize-skeleton`. A process without a skeleton (e.g. a pure collide-shape actor) has no valid target for `do-effect`.
- **Sound is baked into the preset, not chosen per-call:** `death-default` always plays `"enemy-fizz"`. If an enemy needs its own signature death cry *in addition*, play it separately (e.g. via the base `enemy` method `dying`, which already calls `(play-damage-or-death-sound this 1)` = `enemy-info :sound-die`) — both sounds will layer naturally.
- **Joint argument (`-1`) is not the spawn origin:** the last argument to `do-effect` selects an `'effect-joint` resource tag (defaults to joint 0/root when `-1` and no tag is declared) used only for the accompanying sound's 3D position — it has no effect on where the dissolve particles appear, since those are generated from mesh vertices in world space, not from a single joint.
- **`death-seed` looks similar but is a different effect:** it is orange/yellow and semantically tied to the "life seed" death sequence, not a generic kill.

### Verification Steps
1. `./goalc.exe --game jak2 -c "(mi)"` (or `task repl` → `(mi)`) — must build with `Successfully built all N targets`.
2. `task boot-game`, kill an entity using this effect, and confirm: purple dissolving particles tracing the mesh, a trailing wisp, and an audible "fizz" alongside any enemy-specific death sound.

---

# 🇫🇷 Version Française

## Effet de Mort Générique (`death-default`) — Particules Violettes Traçant le Contour du Maillage/Squelette

### Contexte & Concepts Clés
Quand de nombreux ennemis de Jak II meurent (civils, Crimson Guards, guêpes, etc.), leur modèle se dissout en particules violettes qui semblent tracer le contour du maillage pendant qu'il disparaît, accompagné d'un son de "fizz". Ce n'est **pas** un émetteur de particules par joint/os — c'est un système moteur générique et réutilisable, construit autour d'un type `death-info` et de quelques presets statiques, déclenché via le dispatcher de resource-tags existant `effect-control` (`do-effect`).

- **Type :** `death-info` (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc:12-19`) — `vertex-skip`, `timer`, `overlap`, `effect` (un id de `sparticle-launcher`), `sound` (un symbole de nom de banque sonore).
- **Presets :** `death-default` (id `73`, violet, mort générique), `death-seed` (id `72`, orange/jaune, utilisé pour les scènes de mort avec "life seed"), `death-warp-in` / `death-warp-out` (id `74`, bleu-violet, téléportation par warp-gate — pas une mort).
- Ce sont de simples symboles globaux `(define ...)`, donc `(-> 'death-default value)` **est déjà la structure `death-info`** — aucun resource-tag par acteur n'est nécessaire pour l'utiliser.

### Implémentation Technique
1. **Déclenchement :** Appeler `(do-effect (-> self skel effect) 'death-default 0.0 -1)` depuis le code de mort de n'importe quel `process-drawable`. `self skel effect` est une instance `effect-control` créée automatiquement pour tout process-drawable possédant un squelette, dans `initialize-skeleton` (`goal_src/jak2/engine/process-drawable/process-drawable.gc:777`) — cela fonctionne donc pour **n'importe quel** ennemi/PNJ sans configuration supplémentaire, tant que `initialize-skeleton` a été appelé (vrai pour toutes les sous-classes `nav-enemy`/`enemy`).
2. **Dispatch :** `do-effect` (`effect-control.gc:272-585`) résout la valeur du symbole `arg0` ; quand c'est un `death-info`, elle copie `vertex-skip`/`timer`/`overlap`/`effect` sur le `draw-control` du process (`death-vertex-skip`, `death-timer`, `death-timer-org`, `death-draw-overlap`, `death-effect` — champs déclarés dans `goal_src/jak2/engine/data/art-h.gc:303-307`), joue le son du preset via `play-effect-sound`, et envoie un événement `'death-start` au process (`effect-control.gc:531-576`).
3. **Dissolution du maillage image par image :** Chaque frame, `foreground-generic-merc-death` (`foreground.gc:728-752`) avance un pas aléatoire (`death-vertex-skip`) sur le maillage skinné et peut commencer à cacher des triangles une fois le seuil "overlap" dépassé (érosion visuelle du modèle). Le parcours réel des vertices + la transformation en espace monde (via les matrices de skinning courantes, donc suit naturellement la pose animée) se fait dans la fonction native `generic-merc-death` — portage C++ dans `game/mips2c/jak2_functions/generic_merc.cpp:2470-2536`.
4. **Spawn des particules :** Pour chaque vertex échantillonné, `merc-death-spawn` (`merc-death.gc:149-157`) recherche l'id du launcher (ex : `73`) dans `*part-id-table*` et appelle `sp-launch-particles-death` (`sparticle-launcher.gc:486-489`) sur `*sp-particle-system-2d*`. Le launcher `73` enchaîne sur le launcher `76` (`sparticle-motion-blur`), produisant l'effet de traînée qui dérive et s'estompe.
5. **Valeurs de couleur violette** (`merc-death.gc:116-132`, preset `death-default`) : `:r 96.0-150.0 :g 32.0-64.0 :b 128.0-128.0 :a 128.0` — bleu élevé/constant, vert faible, rouge modéré → violet/magenta.

### Exemple de Code Annoté
Le pattern minimal canonique (issu de `wasp.gc:1015-1033`, état `die-now`) :
```lisp
:code (behavior ()
  (dying self)                                          ;; joue sound-die de enemy-info, spawn les skull gems
  (let ((v1-3 (-> self root root-prim)))                 ;; efface la collision pour que le cadavre ne bloque plus rien
    (set! (-> v1-3 prim-core collide-as) (collide-spec))
    (set! (-> v1-3 prim-core collide-with) (collide-spec))
    )
  (set! (-> self hit-points) 0)
  (do-effect (-> self skel effect) 'death-default 0.0 -1) ;; spawn la dissolution violette + le son "enemy-fizz"
  (suspend-for (seconds 1))                               ;; laisse le timer vertex-skip (~1.25s) se dérouler
  (send-event self 'death-end)
  (cleanup-for-death self)
  )
```
Appliqué à l'identique dans l'état `die` de `yakow.gc` (`goal_src/jak2/levels/city/farm/yakow.gc`), en remplacement d'un `part-tracker-spawn` placeholder de poussière `group-land-poof-drt`.

### Pièges / Cas Particuliers
- **Ne pas sauter le `suspend-for` :** le spawn des particules est piloté par `foreground-generic-merc-death`, qui ne s'exécute que tant que le process est vivant et affiché. Appeler `cleanup-for-death` immédiatement après `do-effect` détruit le process avant qu'aucune particule n'ait pu apparaître — l'entité disparaît silencieusement. Le `timer` de `death-default` est `0x4b` (75 frames jeu ≈ 1.25s @ 60 fps) ; `(suspend-for (seconds 1))` (comme dans `wasp.gc`) est suffisant en pratique.
- **Nécessite un squelette :** `(-> self skel effect)` n'est peuplé que pour les process-drawables passés par `initialize-skeleton`. Un process sans squelette (ex : un simple acteur collide-shape) n'a pas de cible valide pour `do-effect`.
- **Le son est intégré au preset, pas choisi par appel :** `death-default` joue toujours `"enemy-fizz"`. Si un ennemi a besoin de son propre cri de mort *en plus*, le jouer séparément (ex : via la méthode de base `enemy` `dying`, qui appelle déjà `(play-damage-or-death-sound this 1)` = `enemy-info :sound-die`) — les deux sons se superposeront naturellement.
- **L'argument joint (`-1`) n'est pas l'origine du spawn :** le dernier argument de `do-effect` sélectionne un resource-tag `'effect-joint` (par défaut joint 0/racine si `-1` et aucun tag déclaré) utilisé uniquement pour la position 3D du son accompagnant — il n'a aucun effet sur l'endroit où apparaissent les particules de dissolution, car elles sont générées à partir des vertices du maillage en espace monde, pas d'un joint unique.
- **`death-seed` ressemble mais est un effet différent :** il est orange/jaune et lié sémantiquement à la séquence de mort "life seed", pas à une mort générique.

### Procédure de Validation
1. `./goalc.exe --game jak2 -c "(mi)"` (ou `task repl` → `(mi)`) — doit compiler avec `Successfully built all N targets`.
2. `task boot-game`, tuer une entité utilisant cet effet, et vérifier : particules violettes qui se dissolvent en traçant le maillage, traînée qui s'estompe, et un "fizz" audible en plus du son de mort spécifique éventuel de l'ennemi.
