# Haven City : Chaos — Technical Deep-Dive

> **Branch:** `jak2/features/haven-city-chaos`
> **Game:** Jak 2
> **Slug:** `haven-city-chaos`
> **Status:** implemented, **not yet validated in-game** (needs `task extract` + cold boot)

---

## 1. The single most useful discovery

Almost everything this mod asks for already exists in Jak 2, switched on by one line of level data.

Haven City's ambient population — who walks the streets, who drives, who shoots at whom — comes
entirely from whichever level is **borrowed into `ctywide` slot 1**:

| Borrow | Contents | When retail uses it |
|---|---|---|
| `lwidea` | citizens, cars, bikes, Krimzon Guards | most of the story |
| `lwideb` | **grunt / flitter / predator**, guards, a few citizens, one car, one bike | the late-game Metal Head invasion |
| `lwidec` | roboguards + traffic | after the invasion |

`lwide-activate` in [`traffic-manager.gc`](../../../goal_src/jak2/levels/city/traffic/traffic-manager.gc)
is what reacts to the swap, and its `lwideb` branch does four things:

```lisp
(('lwideb)
 (set! (-> gp-0 object-type-info-array 8 level) 'lwideb)   ;; metalhead-grunt on
 (set! (-> gp-0 object-type-info-array 9 level) 'lwideb)   ;; metalhead-flitter on
 (set! (-> gp-0 object-type-info-array 10 level) 'lwideb)  ;; metalhead-predator on
 (logclear! (-> gp-0 alert-state flags) (traffic-alert-flag target-jak))   ;; <-- the truce
 (set-alert-level gp-0 3)
 (logior! (-> gp-0 alert-state flags) (traffic-alert-flag guard-multi-focus))
 (set-alert-duration gp-0 (seconds 6048000))
 (set! *traffic-alert-level-force* #t))
```

That `target-jak` flag is read in exactly one place that matters:

```lisp
;; guard.gc -- crimson-guard::citizen-init!
(if (logtest? ... (traffic-alert-flag target-jak))
    (reset-to-collide-spec (-> this focus) (collide-spec jak enemy hit-by-others-list player-list bot-targetable jak-vehicle))
    (reset-to-collide-spec (-> this focus) (collide-spec enemy hit-by-others-list bot-targetable)))
```

A guard can only ever acquire what its focus collide-spec lets it see. With `target-jak` cleared,
`jak` is not in the spec — so **"Jak cannot alert the guards and they are not interested in him"
is not something this mod implements. It is what retail already does during the invasion.** All the
mod has to do is force the borrow.

> [!TIP]
> If you only take one thing from this document: before writing a behaviour, check whether some
> retail game state already produces it. `lwideb` removed roughly half of this mod's scope.

---

## 2. Forcing the borrow

Borrows normally come from open game-task nodes (`:borrow '((ctywide 1 lwideb special))` on a
dozen `game-task-node-info` entries). But look at the order inside `update-task-masks`
([`task-control.gc`](../../../goal_src/jak2/engine/game/task/task-control.gc)):

```lisp
(dotimes (i (-> game-nodes length))       ;; every open task node, in order
  ... (borrow-eval (-> node borrow)) ...)
(borrow-eval (-> *setting-control* user-current borrow))   ;; <-- LAST. always wins.
(add-borrow-levels *load-state*)
```

The `borrow` **setting** is evaluated after every task node, so it overrides the story
unconditionally. That is the seam.

The obvious call is `(set-setting! 'borrow ...)`, but that macro expands to
`(set-setting *setting-control* (with-pp pp) ...)` — it opens a connection owned by the *calling
process*. From a debug-menu pick function that owner is whatever process happens to be running the
debug engine, and the override would silently evaporate when it dies.

Instead the mod writes `user-default` directly:

```lisp
(defun mod-chaos-apply-borrow! ((on symbol))
  (set! (-> *setting-control* user-default borrow)
        (if on '((ctywide 1 lwideb special)) '()))
  (apply-settings *setting-control*))
```

Why this works and why it is safe:

- `apply-settings` rebuilds `user-current` from `user-default` every frame
  (`mem-copy!` of the whole struct), so the override is permanent and process-free.
- `'()` is *exactly* the retail default — `settings.gc` initialises
  `(set! (-> gp-0 borrow) '())` on `user-default`. Turning the mod off restores the stock value
  rather than an approximation of it.
- `apply-settings` compares old and new `borrow` and fires `update-task-masks 'event` on a change,
  which re-runs `borrow-eval` and `add-borrow-levels` — so the level system streams `lwideb` in (or
  drops it) with no further prodding.

Only slot 1 is written. `ctywide` has a second borrow slot (slot 0), unused for the entire game
except during "Destroy the blast bots", which borrows `lbombbot` there — worth knowing if this mod
ever needs a second borrowed level, but nothing here claims it.

---

## 3. Adding traffic types

The three retail city Metal Heads are `traffic-type` 8, 9 and 10. Adding two more meant widening
a fixed-size system.

### 3.1 The enum, and the trap at 21

```lisp
;; traffic-h.gc
(chaos-rapid-gunner 22) (chaos-spyder 23)
```

**21 is skipped deliberately.** The retail enum declares `traffic-type-21` but the arrays are only
21 entries (0..20), and `ctywide-obs.gc` uses it as an "invalid / none" sentinel:

```lisp
(if (!= a1-5 (traffic-type traffic-type-21)) ...)
```

`get-random-parking-spot-type` returns it the same way. Making 21 spawnable would corrupt both.
Two constants encode the result:

```lisp
(defconstant TRAFFIC_TYPE_COUNT 24)
(defconstant TRAFFIC_SPAWN_MASK #xdfffff)   ;; bits 0..20 and 22..23; bit 21 is the hole
```

### 3.2 Resizing `traffic-engine`

```lisp
(object-type-info-array  traffic-object-type-info  26 :inline)   ;; was 21
(tracker-array           traffic-tracker           2 :inline)
(citizen-tracker-array   traffic-tracker  :inline :overlay-at (-> tracker-array 0))
(vehicle-tracker-array   traffic-tracker  :inline :overlay-at (-> tracker-array 1))  ;; was :offset 7024
(inactive-object-array   handle           520)                   ;; was 420 (26 * 20)
```

Two things to notice:

- **The hard-coded `:offset 7024` had to go.** It was the byte offset of `(-> tracker-array 1)`
  computed for a 21-entry info array; growing the array by 100 bytes silently moves it. Expressing
  it as `:overlay-at (-> tracker-array 1)` lets the compiler do the arithmetic and makes the field
  immune to any future resize.
- **Resizing is safe here** because `traffic-engine` is created at runtime
  (`(new 'loading-level 'traffic-engine)` in `ctywide-login`) and never read back from level data.
  The growth is ~500 bytes on a level heap that the PC port already runs at a 12× multiplier.

`inactive-object-array` is 20 reserve handles per type — `reset-and-init-from-manager` hands each
type a 20-handle window with `(set! v1-4 (&-> v1-4 20))`.

### 3.3 The swapped tracker names

Worth writing down because it is genuinely confusing and it bit this implementation twice:

> **`citizen-tracker-array` holds the vehicles, and `vehicle-tracker-array` holds the pedestrians.**

The evidence is unambiguous:

```lisp
;; reset-and-init-from-manager: types 11..20 (bikes/cars) get tracker-index 0,
;;                              types 0..10  (people)     get tracker-index 1
;; activate-one-citizen  -> picks (+ (rand-vu-int-count 10) 11)  = 11..20 = vehicles
;; activate-one-vehicle  -> picks over 0..10                     = people
;; child-killed          -> (type? arg0 citizen) => vehicle-tracker-array
```

So `activate-one-vehicle` is the **pedestrian** picker, and that is the function the mod had to
extend. Both it and every scan in `chaos-city.gc` carry a comment saying so.

### 3.4 The pedestrian draw

Retail expresses its candidates as the contiguous range `[0, 11)` plus an exclusion bitmask:

```lisp
(dotimes (v1-0 11)
  (if (zero? (-> this object-type-info-array v1-0 inactive-count))
      (set! exclude-mask (logior exclude-mask (ash 1 v1-0)))))
(rand-vu-int-count-excluding 11 exclude-mask)
```

22 and 23 do not fit in a contiguous range, so the mod replaces the range with an explicit table
and makes the bitmask index *the table* rather than the traffic type:

```lisp
(define *mod-chaos-ped-types* (new 'static 'array uint8 13 0 1 2 3 4 5 6 7 8 9 10 22 23))
```

The retail branch is kept intact next to it and runs whenever the mod is off. A species that is
switched off in the menu needs no special case here: it gets want-count 0 and level `#f`,
`spawn-all` never builds its reserve pool, and an empty pool is exactly what the exclusion mask
already skips.

### 3.5 Where the weights actually live

The requested percentages are **not** implemented as a weighted random draw, and this is the one
design decision most worth understanding.

`activate-by-type` refuses a type that is already at its population cap:

```lisp
(when (and (> (-> v1-2 inactive-count) 0)
           (< (-> v1-2 active-count) (-> v1-2 target-count))   ;; <-- the cap
           ...)
```

and `set-target-level` derives that cap from `want-count`. So the **steady-state mix on screen is
governed by want-count**, and the random draw only decides who is *offered* a free slot first.
Weighting both would double-count the ratio. So the advertised percentages are stored as
*relative shares* and turned into want-counts at apply time:

```lisp
(defconstant MOD_CHAOS_SHARE_GRUNT    30)  ;; "Grunt"
(defconstant MOD_CHAOS_SHARE_FLITTER  30)  ;; "Stinger"
(defconstant MOD_CHAOS_SHARE_PREDATOR 10)  ;; "Cloaker"
(defconstant MOD_CHAOS_SHARE_RAPID    10)  ;; "Rapid gunner"
(defconstant MOD_CHAOS_SHARE_SPYDER    5)  ;; "Spyder gunner"
(defconstant MOD_CHAOS_METALHEAD_POP  60)  ;; retail lwideb runs 14 + 14 + 14 = 42

;; want = share * POP / (sum of the shares that are currently switched on)
```

Only the species that are enabled contribute to the denominator, so the whole budget is always
spent: with everything on it is 85, with only the three defaults on it is 70 and those three
absorb the rest. That is what makes a per-species menu switch meaningful — turning Rapid gunner
off makes the Grunts *more* numerous rather than making the invasion smaller.

`mod-chaos-enroll-species!` writes `want-count`, `target-count` and `reserve-count` together,
mirroring `restore-default-settings`' own `(max 1000 (min #xfde8 (* 1000 want-count)))` formula so
that a mid-session toggle behaves exactly like a fresh city load.

### 3.5b Raising the overall spawn rates

`MOD_CHAOS_METALHEAD_POP` alone is not enough: three other ceilings decide whether the extra
actors ever materialise. Modelled on `jak2/config/enhanced_spawnrates`, all gated on
`*mod-chaos-enable*`:

| Lever | Retail | Mod | Where |
|---|---|---|---|
| Krimzon Guard want-count (type 6) | 9 | 20 | `mod-chaos-boost-ambient!` |
| guard-bike / hellcat want-count (18 / 19) | 4 / 3 | 9 / 7 | `mod-chaos-boost-ambient!` |
| `inv-density-factor` | 5.0 | 3.0 | `mod-chaos-boost-ambient!` |
| per-cell activation ranges | 81920 / 819200 / 491520 | 122880 / 983040 / 655360 | `traffic-engine.gc` |
| `*default-nav-mesh*` slots | 128 | 250 | `nav-mesh.gc` (unconditional) |

Citizen want-counts are deliberately left at retail values: every extra pedestrian costs a
`nav-control` slot, and the Metal Heads are the better use of them.

### 3.5c The ceiling that actually bites: `*default-nav-mesh*`

The first playable build of the higher spawn rates crashed the moment the invasion started:

```
nav-mesh::new-nav-control:  too many users for nav-mesh #f
ERROR: nav-mesh::change-to: unable to allocate nav-mesh for #<metalhead-flitter ... initialize>
```

That `#f` is the tell. `new-nav-control` prints `(res-lump-struct (-> this entity) 'name structure)`,
and the mesh that overflowed has no entity — it is `*default-nav-mesh*`, the static 1-polygon mesh
declared at the top of `nav-mesh.gc`.

Why the whole city is on it: `citizen::init-enemy-behaviour-and-stats!` opens with

```lisp
(set! (-> arg0 nav-mesh) *default-nav-mesh*)
```

because a traffic-spawned actor has no entity, and `get-nav-control` falls back to
`nav-mesh-from-res-tag (-> arg0 entity)` when handed `#f` — which would fail. So **every** Haven
City citizen, Krimzon Guard and Metal Head takes one of that static mesh's `nav-control` slots, and
keeps it for as long as its process exists — pooled and inactive counts exactly the same as active.
The relevant number is therefore the sum of the *want-counts*, not the on-screen population.

Two attempts at a fix failed before the third worked, and the failures are the instructive part.

**Attempt 1 — raise `nav-max-users` in `nav-mesh::init-from-entity`.** Wrong lever twice over: it
sizes *entity-backed* meshes, which the ambient city population never reaches, and it is read at
level-init time, so a debug-menu toggle could not affect the level the player is standing in.

**Attempt 2 — predict the usage from the want-count table and size the mesh to match.** The
arithmetic said 134 users against a 128-slot mesh, so the mesh went to 192 and the mod budgeted
itself against `max-nav-control-count` minus the citizen and guard want-counts. It crashed again,
identically. The prediction was wrong because `*default-nav-mesh*` is a single **global** object —
everything in the game without an entity-backed mesh of its own shares it, not just the ambient
traffic table — and because vehicle riders, escort NPCs and mission actors never appear in that
table at all.

**Attempt 3 — measure instead of predicting.** `mod-chaos-nav-governor!` runs every frame, counts
the genuinely free slots, and moves the Metal Head budget to suit:

```lisp
(cond
  ((< free MOD_CHAOS_NAV_LOW)                          ;; 16
   (set! *mod-chaos-pop* (max 0 (- *mod-chaos-pop* MOD_CHAOS_POP_SHRINK))))    ;; -4
  ((and (< *mod-chaos-pop* MOD_CHAOS_METALHEAD_POP)
        (> free MOD_CHAOS_NAV_HIGH))                   ;; 32, hysteresis
   (set! *mod-chaos-pop* (+ *mod-chaos-pop* MOD_CHAOS_POP_GROW))))             ;; +1
```

Three details make it work:

- **Free slots are counted, not inferred.** `max-nav-control-count - nav-control-count` is wrong:
  `remove-nav-control` only trims the *tail*, so that high-water mark badly overstates usage in a
  city that recycles actors constantly. `new-nav-control` reuses any hole in `[0, count)`, so
  `mod-chaos-nav-free` walks the array and counts holes as capacity.
- **It starts pessimistic.** `*mod-chaos-pop*` is reset to `MOD_CHAOS_START_POP` (24, below
  retail's 42) on every borrow change, because a city load fills every pool in one `fast-spawn`
  burst of up to 120 spawns in a single frame — the one moment the governor gets no frame to react
  inside. It climbs back up over the following second.
- **The floor is 0, not a minimum invasion.** If something else on this global mesh has taken
  everything, the honest outcome is an invasion that does not appear — never a killed process.

`*default-nav-mesh*` still grew, 128 → 250 slots (`:max-nav-control-count #xfa`, the static
`inline-array` count, and the matching `nav-engine` connection pool). Both count fields are `uint8`,
so 255 is the hard ceiling. That change is **unconditional** — it is a static sized at compile time,
there is no toggle to read, and an unused slot costs nothing but its 288 bytes (250 slots ≈ 72 KB).
Retail never approaches 128, so behaviour with the mod off is unchanged; the governor is what turns
the extra room into Metal Heads.

`(mod-chaos-nav-report)` from the REPL prints the occupancy and the settled budget, and
`(set! *mod-chaos-nav-verbose* #t)` logs every cutback.



### 3.5d The *other* ceiling: 20 reserve handles per traffic type

A later build crashed with the same message as §3.5c but a different victim — a **Krimzon Guard**,
during a level transition:

```
traffic-manager : level killed cpo
GAMEPLAY: enter ctyfarmb
nav-mesh::new-nav-control:  too many users for nav-mesh #f
ERROR: nav-mesh::change-to: unable to allocate nav-mesh for #<crimson-guard ... initialize>
```

The nav-mesh governor was running and reporting plenty of headroom, which was the clue: something
was holding slots that the governor could not see, because it was holding them outside the traffic
engine's own bookkeeping.

`reset-and-init-from-manager` hands every traffic type a **fixed 20-handle window** into
`traffic-tracker::inactive-object-array`:

```lisp
(set! (-> a1-3 array) v1-4)
(set! v1-4 (&-> v1-4 20))     ;; next type starts 20 handles later
```

and `add-reserved-process` refuses — silently, with no diagnostic — to record a 21st:

```lisp
(when (< a1-2 20)
  (set! (-> v1-2 array a1-2) arg1)
  (+! (-> v1-2 inactive-count) 1)
  ...)
```

`spawn-all` spawns while `active-count + inactive-count < want-count`. Set a want-count above 20
and the counters stall at 20 while that test stays true forever: every frame a fresh process is
created, its handle is dropped on the floor, and nothing can ever find it again. It is in no
tracker list, so `kill-excess-once` cannot reclaim it and `deactivate-all` cannot kill it — it
simply holds its `nav-control` slot until the level is torn down. One leaked process per frame.

The mod had `MOD_CHAOS_WANT_CRIMSON_GUARD_1` at 22, and its metal-head split could reach 25 for a
30 %-share species at a budget of 60. Retail's largest want-count is 15, which is why nothing in
the stock engine guards against this.

The fix is `MOD_CHAOS_WANT_MAX` (20) and `mod-chaos-clamp-want`, through which **every** want-count
the mod writes now passes — both `mod-chaos-enroll-species!` and `mod-chaos-bump-want!`. It is one
`min`, and it is the only thing between a tuning-constant typo and a hard crash.

> [!NOTE]
> The consequence is that 20 is the hard per-type population ceiling, so a large share of a large
> budget comes out short: the three default species at a budget of 60 want 25 / 25 / 8 and get
> 20 / 20 / 8. Redistributing the clipped remainder would just push the other species toward the
> same wall. Going denser than that means more traffic *types*, or more guard vehicles — each of
> which carries a rider.

### 3.6 Why the table is re-asserted every second

`traffic-manager::init-params` and the `restore-default-settings` event — which a dozen mission
hooks fire — both rewrite the want-count table from retail values, and there is no ordering
guarantee between those and `lwide-activate`. Rather than try to intercept every writer, the
per-frame hook simply re-asserts:

```lisp
((zero? (mod (the int (current-time)) MOD_CHAOS_REASSERT_PERIOD))    ;; 64 frames
 (mod-chaos-apply-species! te 'lwideb))
```

Five struct writes a second. Cheap, and immune to writers nobody has found yet.

---

## 4. The two new species

### 4.1 The `citizen-enemy` recipe

The retail city Metal Heads are **not** the standalone `grunt` / `flitter` / `predator` enemies.
They are `citizen-enemy` subclasses that reuse the *same art groups* but plug into the traffic
engine. `metalhead-grunt::init-enemy!` makes this explicit:

```lisp
(initialize-skeleton this (art-group-get-by-name *level* "skel-grunt" ...) ...)  ;; the plain grunt's skeleton
(init-enemy-behaviour-and-stats! this *metalhead-grunt-nav-enemy-info*)          ;; city-tuned stats
```

`citizen-enemy` already supplies everything a city enemy needs:

| Concern | Where it is handled |
|---|---|
| walk / run animation slots, travel speeds | `citizen-enemy::citizen-init!`, derived from `enemy-info` |
| patrolling the nav graph | `citizen-enemy`'s `active` state, plays `walk-anim` |
| picking a target (guard, citizen or Jak) | `citizen-enemy-method-202` → `go-hostile` |
| vehicles swerving around them | `traffic-danger-init!` |
| pooling / recycling / district culling | the traffic engine, via `citizen-init-by-other` |

So a new species needs only: a skeleton name, a `nav-enemy-info`, and a collide-shape. Each of the
two is ~40 lines.

### 4.2 Borrowing instead of transcribing

```lisp
(defmethod get-nav-info ((this chaos-rapid-gunner)) *rapid-gunner-nav-enemy-info*)

(defmethod init-enemy-collision! ((this chaos-rapid-gunner))
  ((method-of-type rapid-gunner init-enemy-collision!) (the-as rapid-gunner this))
  (chaos-cityify-collision! this))
```

Both of these point straight at the retail enemy rather than copying it:

- **`get-nav-info` returns the retail static.** Hit points, notice distances, knock-back curves,
  the full idle-animation script and the walk/run animation indices all come across exactly right,
  for free. It is read-only — never mutate it, the Ruins gunners share the object.
- **`init-enemy-collision!` calls the retail method through a cast.** Those methods only ever touch
  `(-> this root)`, which sits at the same offset in every `nav-enemy` subclass, so the cast is
  safe — and the primitive layout stays keyed to the right joint indices instead of drifting from
  a hand-written copy.

### 4.3 `chaos-cityify-collision!` — the two bits that matter

Retail enemies live in arenas where the only thing worth colliding with is Jak. Comparing
`metalhead-grunt::init-enemy-collision!` with `rapid-gunner::init-enemy-collision!` isolates the
difference:

```lisp
;; city:  backgnd jak bot crate civilian enemy obstacle hit-by-others-list player-list
;; arena: backgnd jak bot crate                obstacle hit-by-others-list player-list
```

`civilian` is what citizens and Krimzon Guards register as; `enemy` is how two Metal Heads avoid
walking through each other. Without those two bits the new species would drift straight through the
faction war they are here for.

`backup-collide-as` / `backup-collide-with` must be refreshed afterwards, because `citizen-init!`
restores the root primitive from them every time the traffic engine recycles the process.

### 4.4 The generic `hostile` fallback

`nav-enemy`'s `hostile` has a `:trans` and a `:post` but **no `:code`** — each retail enemy
supplies its own chase animation loop. Inherited as-is, a species would keep playing the `active`
walk cycle while moving at run speed. Both shipped species now override `hostile` with their retail
one (§4.6), so nothing reaches the base version any more; it is kept because an *unported* third
species inheriting the empty `:code` would look broken in a way that is hard to trace back to a
missing override. It picks a chase animation with a fallback for species shipping `run-anim -1`:

```lisp
(defmethod chaos-chase-anim ((this chaos-metalhead))
  (let ((run (-> this enemy-info run-anim)))
    (if (>= run 0) run (-> this enemy-info walk-anim))))
```

Doing it this way rather than patching `run-anim` on the shared static is the point: patching would
leak into the retail enemies that share the object.

### 4.5 The intangibility bug, and the filter that caused it

The first playable build had the extra species and the Krimzon Guards walk into each other, shove,
and then stand there: the guard swung its rifle butt with no effect, the metal head did nothing.

Damage between two `enemy`s is **touch-driven**. `common-post` calls `find-overlapping-shapes`,
which fills `*touching-list*` and makes both sides receive a `touch` event; `enemy-method-75` then
turns a touch that involves a `deadly` primitive into an `attack`. Which shapes are even considered
comes from one field:

```lisp
;; citizen-enemy::common-post
(set! (-> a1-0 collide-with-filter) (-> this enemy-info overlaps-others-collide-with-filter))
```

and the retail values differ by exactly the bits that matter:

| `enemy-info` | `overlaps-others-collide-with-filter` |
|---|---|
| `metalhead-grunt` / `-flitter` / `-predator` | `jak civilian enemy vehicle-sphere hit-by-others-list player-list` |
| `rapid-gunner` / `spyder` (arena enemies) | `jak bot player-list` |

`civilian` is what Krimzon Guards and citizens register as, and `vehicle-sphere` is what city
traffic registers as. With the arena filter, an arena species in Haven City can only ever produce a
touch entry against **Jak**. The two shapes still collide as solids — hence the shoving — but no
touch entry means no `attack` in either direction, so neither the guard's rifle butt nor the
metal head's own body primitives can land.

The fix is a `common-post` override on `chaos-metalhead` that uses the city filter. Patching
`enemy-info` itself is not an option: `*rapid-gunner-nav-enemy-info*` is a shared static that the
Ruins gunners read too.

**That alone was not enough**, and the second half is the part worth remembering.
`find-overlapping-shapes` intersects the filter with the *root primitive's* `collide-with`:

```lisp
(s2-0 (logand (-> s3-0 prim-core collide-with) (-> arg0 collide-with-filter)))
```

but a collide-shape's root primitive is a `collide-shape-prim-group` — a bounding sphere used to
reject the whole actor cheaply. Only its **children** ever pair into a touching entry. Widening the
group and leaving the children alone, which is what the first attempt did, changes nothing at all:

| | children' `collide-with` |
|---|---|
| `metalhead-grunt` | `jak civilian hit-by-others-list player-list` |
| `rapid-gunner` / `spyder` (arena) | `jak bot player-list` |

So `chaos-cityify-collision!` now ORs `civilian enemy` into the root primitive **and every child**.

All three reported symptoms — bodies overlapping instead of shoving, immunity to the guard's rifle
butt, no damage dealt in return — were this one missing bit, since solid reaction and touch damage
both come from the same primitive pairing.

Note what `chaos-cityify-collision!` deliberately does **not** do: it does not force `deadly` onto
the children. An earlier version did, because a species whose group is `deadly` while none of its
children are could charge a guard and do nothing —

| | group | children |
|---|---|---|
| `metalhead-grunt` | `deadly` | two limbs `deadly` |
| `spyder` | `deadly` | four `deadly` |
| `rapid-gunner` | *not* `deadly` | one `deadly` (the gun arm) |

— but that asymmetry is never an oversight in the retail data: contact damage on these species is
*scripted*, opened and closed from inside an attack animation. The rapid gunner's `spin-attack`
grows child primitive 1 from 1 m to 1.8 m and arms it for exactly one animation, then puts it back;
outside that one spin it is harmless to walk into. Forcing `deadly` on permanently was a workaround
for not having ported the attack states. Now that they are ported (§4.6), the workaround is gone.

### 4.6 Porting the retail combat states

The first two playable builds gave both species a *generic* fight: charge the focus, re-stamp the
attack id every 0.8 s for a repeating contact hit, and fire a projectile on a fixed 1.5 s cadence
while running. It worked, and it was wrong in a way that is obvious on screen — both of these are
stand-and-shoot enemies that do not close, and both have damage windows that are scripted by their
animations rather than permanent auras. The brief is that these two fight exactly as they do in
their own missions, with the single difference that the thing they are fighting is a Krimzon Guard
rather than Jak.

**The targeting half of that is free.** Who a city enemy fights is decided by
`citizen-enemy-method-202`, which picks the nearest valid process and calls `go-hostile`;
`citizen-init!` sets the focus collide-spec to `jak civilian player-list bot-targetable
jak-vehicle`. Everything downstream of `(-> self focus handle)` is target-agnostic. "Make them
fight guards" needed the collision work in §4.5 and no combat code at all.

**The combat half cannot be inherited**, and this is the structural constraint the whole file is
shaped by. The retail `attack` / `hop` / `reload` / `backup` states read `rapid-gunner` and `spyder`
*fields* — `los`, `target-next-pos`, `fire-info`, `status-flags`, the IK joints — at offsets that
only exist in those types. A `citizen-enemy` subclass has `citizen`'s ~200 bytes of traffic plumbing
sitting where those fields would be, so the state objects cannot simply be pointed at a chaos
process. Nor can the problem be inverted by inheriting from `rapid-gunner` instead: `citizen` is
what makes a process poolable, recyclable, nav-graph-walking and traffic-aware, and reimplementing
that is an order of magnitude more work than reimplementing the combat.

So the states are **ported**: each species redeclares the fields its retail states read, and the
bodies are transcribed. Where the decompiler emitted `b!` / `label` control flow it is rewritten as
the `cond` it came from; everything else is verbatim, tuning numbers included, so a future reader
can diff against the retail file.

#### Rapid gunner

This one is an **emplacement**: in the Ruins it is hand-placed and never chases. Its whole fight is
aim, spin up, and walk a stream of rounds onto the target; when pressed it hops sideways rather
than closing.

| state | what it does |
|---|---|
| `hostile` | Stand and aim — `nav callback-info` is nulled, the post only faces the focus. `:trans` is the decision table: inside 5 m and roughly level → `spin-attack`; inside 100 m with line of sight → `attack`, or `reload` first if the drum is empty; no line of sight for 25 s → `hop` back toward where the fight started; focus lost → back to the city walk. |
| `attack` | **Stop and fire.** One round every 0.25 s while the barrel is within ~12° of the predicted aim point, from the `blast` joint (index 18). Twelve rounds, then `reload`. Breaks to `spin-attack` if the target closes to 5 m, `hop` if it loses sight, `hop-turn` if the target gets behind it, `hostile` past 105 m. |
| `spin-attack` | The melee, and the only time it deals contact damage: child primitive 1 is grown and armed `deadly` for exactly one spin animation, then restored. |
| `hop` | A 2 m sidestep along `hop-dir`, clamped to the nav mesh, animated by blending the four directional idle poses against the travel direction in local space. Costs two rounds of the drum, which is what stops it hopping forever. |
| `hop-turn` | Turn in place at four times the normal rate until the aim point is back inside a 35° arc. |
| `reload` / `cool-down` | Reload animation at half speed then hop if still exposed; half a second of aim with the drum reset. |

Two details are what make it read as the mission enemy rather than a turret with a timer:

- **Lead prediction.** `chaos-rgun-track-post` keeps `target-next-pos` one lead ahead of the focus,
  scaled by range and smoothed at 8 % per frame. *Every* aim test — the firing cone, the joint
  slerp, `enemy-method-96` — reads that, not the focus. It is why the stream lands in front of a
  running Krimzon Guard instead of trailing it.
- **Spin-up scatter.** For the first two seconds after a cold start, each round is pitched up by an
  angle that decays to zero, so the opening burst goes wide and walks down onto the target.

#### Spyder gunner

| state | what it does |
|---|---|
| `hostile` | A **stand-off**, not a chase. `chaos-spyder-reposition!` sets `move-dest` by rotating the vector to the focus 90° (alternating side each call) and scaling it to a random 8–16 m inside 35 m; outside 35 m it closes to 30 m. On arrival, if the focus is inside 35 m and in line of sight → `attack`. A spyder that walked *into* a guard was the clearest single sign the retail states were missing. |
| `attack` | **Stop**, drop the turn rate to a twentieth, blend `spyder-shoot-low-ja` and `spyder-shoot-high-ja` together and hold the volley for eight 0.2 s ticks, walking the aim point in along the ground and compensating for how far the target moved during each tick. |
| `backup` | Retreat to `move-dest` for up to six seconds, then back to `hostile`. |

The spyder's shots are fired **by the animation**, not by a timer: the art carries an
`event-attack` tag, the effect system sends that event, and the state's `:event` handler turns it
into a `spyder-shot` along whatever `fire-info` currently holds. That is why the gun fires in time
with the muzzle flash — and it is exactly the "if there is a firing animation, it must be played"
part of the brief.

Both projectiles are `metalhead-shot`s — the gunner goes through `spawn-metalhead-projectile`,
which reads only `entity` and the process handle off its first argument so the cast is safe, and
`spyder-shot` is a subclass. `metalhead-shot` already lists `civilian` and `enemy` in its
collide-with, so both damage Krimzon Guards with no change on the projectile side.

#### What is deliberately left out

- **The gunner's `spinup-angle` res-lump read** and **the spyder's cloak**. Both read the actor's
  `entity`, and a traffic-spawned process has none. (`spin-up-angle` is dead in retail anyway —
  written once, never read.) Retail spyders without an `extra-id` res tag are uncloaked too, so the
  city spyder takes the stock else-branch rather than an approximation.
- **`notice`.** City metal heads are pushed straight into `hostile` by `citizen-enemy-method-202`;
  there is no idle patrol to be noticed out of.
- **The Ruins particle connections** on the gunner (barrel heat haze, particles 1310–1312), whose
  definitions live in the Ruins level data and are not resident in Haven City.
- **The knockback and death paths** (`enemy-method-77` / `-78`, the retail `hit` event handling).
  `citizen-enemy` owns damage-to-death-to-recycle and the three retail city species all go through
  it. Combat is what had to match the mission; dying and being pooled is city business.

#### The gunner cannot walk, and the city does not check

The first build of this species crashed the moment one spawned — exit status 5, no GOAL error line
at all, just the process dying mid-frame. The cause is one field:

```lisp
;; *rapid-gunner-nav-enemy-info*
:walk-anim -1
:run-anim  -1
```

The Ruins gunner is an emplacement. It has **no walk cycle**; its only locomotion is the scripted
`hop`, which blends four directional idle poses. Every other city species has a real walk, and the
city code takes that for granted:

```lisp
;; citizen-enemy::active
(ja-no-eval :group! (-> self draw art-group data (-> self enemy-info walk-anim)) ...)
```

`(-> draw art-group data -1)` reads the word *before* the array, hands the animation system a
garbage `art-joint-anim` pointer, and the process segfaults. There is no bounds check anywhere on
that path — which is why the failure is a hard crash rather than a `process-drawable-art-error`.

Two fixes, and the second one matters more than it looks:

1. **`active` is overridden** with the retail idle loop, nav callback nulled and target speed
   zeroed. So a city gunner is a gun emplacement that the traffic engine happens to position: it
   appears at a pedestrian nav point, stands, and opens up on whatever walks into its arc. That is
   also the honest reading of "identical to its mission behaviour" for this species. Every handler
   is spelled out rather than partially overridden, because **a `defstate` handler you leave out is
   not inherited** — the `*no-state*` sentinel only tells the compiler to skip the field write, and
   `enter-state` then installs whatever is there (`(set! (-> pp post-hook) (-> new-state post))`).
   That is why `citizen-enemy::active`, which declares only `:code`, has no post at all.
   Deactivation is unaffected either way: the traffic engine tears an actor down with a
   `traffic-off` *event*, which reaches `citizen`'s handler through `:event`.
2. **`citizen-init!` is overridden** to point `anim-walk` / `anim-run` / `anim-shuffle` at the idle
   animation whenever `enemy-info` gave them -1. It has to be `citizen-init!` and not `init-enemy!`
   because the former runs on *every recycle*. This is the belt to the braces: if any city code
   path is ever reached that this port did not anticipate, the result is a gunner standing in a
   wrong pose rather than a dead game.

`chaos-chase-anim` on the shared base got the same treatment — it used to fall back from `run-anim`
to `walk-anim`, which for this species is -1 to -1.

#### One more city adaptation

The gunner's `start-pos` — the spot it hops back to when it loses sight of its target — is refreshed
on entering `hostile` rather than set once in `init-enemy!` from the entity's placement. A traffic
actor is recycled all over the map, so its fallback has to be wherever *this* fight started.

The spyder's leg IK (`chaos-spyder-legs!`) *is* kept — without it four legs float over the city's
kerbs and slopes. It costs one `*collide-cache*` fill per spyder per frame, which is why this
species carries the smallest population share of the five.

---

## 5. Guard-side changes

### 5.1 Health

```lisp
;; guard.gc -- crimson-guard::citizen-init!, after the retail dark-guard doubling
(when (!= *mod-chaos-guard-hp-scale* 1.0)
  (set! (-> this hit-points) (max 1 (the int (* *mod-chaos-guard-hp-scale* (the float (-> this hit-points)))))))
```

Red riot guards and yellow rifle guards are both `crimson-guard` — they differ only by
`guard-type` — so one scale covers "rouge & jaune". Applying it *after* the dark-guard doubling
keeps an elite proportionally elite. The scale is `1.0` while the mod is off, which leaves
`hit-points` identical to retail.

It is read once per spawn, so existing guards keep the health they were born with until the traffic
engine recycles them.

### 5.2 Gunships engaging Metal Heads

Retail guard vehicles only ever pursue Jak: their target comes from
`alert-state target-status-array 0`, which is only populated while `target-jak` is set — and the
invasion city clears it. Left alone they fly around doing nothing while the city burns.

The obvious implementation — call `vehicle-method-134`, the retail "start pursuing this process"
entry point — **does not work**, and this took a while to pin down. Two reasons:

1. `vehicle-method-134` also calls `vehicle-method-111`, which raises the *city alert level* with
   the given process as the alert target. That writes a Metal Head into
   `traffic-alert-state::target-status-array 0` — the slot the whole alert system reserves for Jak.
2. It then leaves the actual engagement to the retail path, and the retail path stalls:

   ```lisp
   ;; vehicle-guard::active, :post
   ((logtest? (rigid-body-object-flag alert) (-> self flags))
    (vehicle-guard-method-150 self)                       ;; LOS scan -> maybe in-pursuit
    (when (logtest? (rigid-body-object-flag in-pursuit) ...) (go-virtual hostile))
    ...
    (if (or (time-elapsed? (-> self state-time) (seconds 8)) ...)
        (logclear! (-> self flags) (rigid-body-object-flag persistent alert))))   ;; <-- same frame
   ```

   `alert` is cleared at the end of the same frame once the vehicle has been in `active` for eight
   seconds, which an ambient cruising vehicle always has. Meanwhile `vehicle-guard-method-150` only
   refreshes line-of-sight on the vehicle's own sync frame — `sync-mask-16`, one frame in sixteen.
   So the alert is raised and dropped again before the scan ever runs, and `in-pursuit` is never
   reached.

The mod sets `in-pursuit` itself, which closes the loop: `active`'s `:post` already reads
"alert && in-pursuit" as "go hostile", and from `hostile` onwards the retail chase, turret tracking
and `stop-and-shoot` logic all work unmodified on a non-Jak target — `traffic-engine-method-49`
marks any non-`target` process visible without a line-of-sight test at all.

```lisp
(set! (-> veh pursuit-target) (process->handle prey))
(logior! (-> veh flags) (rigid-body-object-flag alert target-in-sight))
(set-time! (-> veh target-in-sight-time))
(if (not (logtest? (-> veh flags) (rigid-body-object-flag in-pursuit)))
    (vehicle-method-108 veh))     ;; retail "begin pursuit": persistent + in-pursuit + ignore-others
```

> [!NOTE]
> `pursuit-target` and `traffic-target-status` look like two separate fields in the decompiled
> `vehicle-guard`, but they are not: the 80-byte `traffic-target-status` struct is stored inline and
> the decompiler split it, so `pursuit-target` *is* its `handle` member. Writing one writes the
> other, which is why the LOS code picks up the new target without a second assignment.

Scanned every 8 frames. The same pass also refreshes `target-in-sight-time` on vehicles already
engaged — `vehicle-guard::hostile` drops a pursuit as soon as that timestamp is half a second stale
with two other guards on the target, or eight seconds stale on its own — and skips any vehicle Jak
is driving.

### 5.3 The metal-head test

Used by the gunship retargeting and by the species' own focus checks:

| Actor | `process-mask enemy` | `process-mask guard` |
|---|---|---|
| City Metal Head (`citizen-enemy` subclass) | ✅ `citizen-enemy::citizen-init!` | ❌ |
| Krimzon Guard (`crimson-guard`) | ❌ explicitly cleared | ✅ |
| Citizen (`civilian`) | ❌ | ❌ |

`enemy && !guard` isolates Metal Heads exactly, with no type checks.

---

## 6. Architecture: two halves and a hook layer

The mod is split across two residency domains, and the split is forced by where the code it touches
lives:

```
GAME.CGO  (always resident)          CWI.DGO  (Haven City only)
├─ pc/mods/haven-city-chaos-h.gc     ├─ levels/city/chaos/chaos-species.gc
│   toggles, tuning, hook defaults   │   the two species
│   mod-chaos-apply-borrow!          ├─ levels/city/chaos/chaos-city.gc
└─ pc/debug/haven-city-chaos-menu.gc │   hook implementations, per-frame work
    Debug > Mods registration        └─ (installs the real hooks on load)
```

`guard.gc`, `traffic-engine.gc` and `traffic-manager.gc` ship in CWI, but the debug menu can be
opened in a level where CWI is gone — so the toggles must live in GAME. Meanwhile the hook
implementations must live in CWI, because that is where the types they touch are.

`nav-mesh.gc` is the one exception in the other direction: it is engine code that runs outside
Haven City too, so it carries its own `define-extern` for `*mod-chaos-enable*` and reads the
GAME-resident symbol directly.

### 6.1 The dangling-pointer rule

Function pointers into a level heap are a crash waiting to happen. `ctywide-deactivate` calls
`mod-chaos-reset-hooks!`, which points every pointer back at the always-resident no-ops in GAME
**before** the CWI heap is recycled. Every engine call site is a `(if *mod-chaos-enable* (*hook* ...))`,
so even a torn-down city only ever reaches a no-op.

### 6.2 Compile order, and why the menu flags instead of calling

The debug menu wanted to rebuild the species table on a toggle, but it is a GAME file and
`mod-chaos-apply-species!` is a CWI symbol. Instead it raises a flag the city half consumes:

```lisp
(set! *mod-chaos-species-dirty* #t)
```

Two rules fall out of this, worth generalising:

- **A symbol referenced from a CWI file must be `define-extern`'d in `traffic-h.gc`** (which is in
  ENGINE/GAME), because there is no build-graph guarantee that the GAME-resident mod file compiles
  before CWI's own sequence.
- **Never call across a residency boundary in the "wrong" direction.** Flag, and let the resident
  side consume.

### 6.3 Non-regression

Every engine touch point is `(if *mod-chaos-enable* ...)` or `(!= *mod-chaos-guard-hp-scale* 1.0)`.
With the mod off that is one symbol read; the retail branch next to it is untouched. The two new
traffic types are inert by construction — `lwide-activate` leaves their `level` at `#f` and
`init-params` gives them want-count 0, so `spawn-all` never builds a reserve pool for them.

One genuine behavioural cost when the mod is off: `LWIDEB.DGO` now carries two extra art groups
and one texture page, which the retail late-game invasion will also load. The PC port runs borrow
heaps at `BORROW_MULT = DEBUG_LEVEL_HEAP_MULT = 12.0`, so `ctywide` slot 1's `#x82f` KB budget
becomes ~25 MB and the addition should disappear into it. `:borrow-size` was deliberately **not**
raised — if it ever does overflow, that is the one line to change.

---

## 7. Build wiring

### 7.1 Circuit 1 — GOAL heap

| DGO | Added |
|---|---|
| `GAME.CGO` | `haven-city-chaos-h.o` (before `mods-menu.o`), `haven-city-chaos-menu.o` (after it) |
| `CWI.DGO` | `rapid-gunner.o`, `spyder.o`, `chaos-species.o` (before `traffic-engine.o`); `chaos-city.o` (after `traffic-manager.o`) |
| `LWIDEB.DGO` | `tpage-1607.go`, `tpage-853.go`, `rapid-gunner-ag.go`, `spyder-ag.go` |

Note that the enemies' **code** and **art** ship in different DGOs — code in CWI (resident
everywhere in the city), art in the LWIDEB borrow. That is retail's own arrangement: `hopper.o` is
in MTN/STA while `hopper-ag` is in MTX/STADBLMP.

The two species come from different levels, so the art cost is two texture pages:

| Home DGO | Texture page | Species |
|---|---|---|
| `ATE.DGO` | `tpage-1607` (atollext-vis-pris) | Spyder gunner |
| `RUI.DGO` | `tpage-853` (ruins-vis-pris) | Rapid gunner |

> [!NOTE]
> Identifying the right page is not always possible from the texture *names* — neither species has
> a single texture named after it. The reliable rule is the level's own `pris` page, since that is
> where a level's character (`pris` = "prisms", the character/prop bucket) textures live. If a model
> renders white after a rebuild, that is the first thing to re-check.

### 7.2 Circuit 2 — PC renderer

A `.gd` entry loads only the *skeleton*. The PC `Merc2` renderer reads mesh and texture data from
the resident `.fr3`:

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEB.DGO": ["rapid-gunner-ag:RUI.DGO", "spyder-ag:ATE.DGO"]
}
```

The `:HOME.DGO` suffix names the level whose texture remap table resolves the model's
(home-relative) texture ids. Omit it and the models render white and shiny.

**`task extract` is mandatory after checking out this branch.** See
[`docs/modding/tools/model_and_entity_level_injection_guide.md`](../tools/model_and_entity_level_injection_guide.md).

### 7.3 `game.gp`

The four new sources have no `all_objs.json` entry, so they are pre-marked in `*file-entry-map*`
and built by explicit `goal-src` steps whose dependencies pin the compile order:

```lisp
(goal-src "pc/mods/haven-city-chaos-h.gc" "traffic-h" "settings")
(goal-src "pc/debug/haven-city-chaos-menu.gc" "haven-city-chaos-h" "mods-menu")
(goal-src "levels/city/chaos/chaos-species.gc" "citizen-enemy" "metalhead-grunt" "rapid-gunner" "spyder")
(goal-src "levels/city/chaos/chaos-city.gc" "chaos-species" "traffic-manager" "haven-city-chaos-h")
```

---

## 8. Using it

```
Debug ▸ Mods ▸ haven-city-chaos
  Enable                          master switch
  species ▸ Grunt (30%)           on by default
  species ▸ Stinger (30%)         on by default   (metalhead-flitter)
  species ▸ Cloaker (10%)         on by default   (metalhead-predator)
  species ▸ Rapid gunner (10%)    off by default  (chaos-rapid-gunner, extra art)
  species ▸ Spyder gunner (5%)    off by default  (chaos-spyder, extra art)
  guards ▸ Tougher guards         1.5x health + gunships engaging metal heads
  guards ▸ Guards ignore Jak      the truce
```

The percentages in the labels are relative shares, not caps — see §3.5. Whatever is switched on
splits the whole population budget between itself in those proportions, so the three defaults on
their own are *more* numerous than they would be with all five running.

Flying Krimzon Guards are **not** part of this branch. That work lives on its own branch,
`jak2/features/jetpack-crimsonguard`.

Equally drivable from the REPL with the menu closed:

```lisp
(mod-chaos-set-enable! #t)
```

Enabling streams `lwideb` in, so give it a second or two before the first Metal Head appears.

---

## 9. Validation checklist

Nothing here has been run yet. In order:

1. `task set-game-jak2`
2. `task extract` — watch for
   `extra_art_groups_by_dgo: baking 'rapid-gunner-ag' into LWIDEB.DGO`
3. `task boot-game` — **cold boot, not `(mi)`**. This branch changes `traffic-engine`'s field
   layout, which is precisely the case the ghost-memory rule in
   [`AGENTS.md`](../../../AGENTS.md) warns about: a hot reload would leave the old layout in
   simulated memory and appear to work while being broken on a clean launch.
4. In the city: `Debug ▸ Mods ▸ haven-city-chaos ▸ Enable`.

| Symptom | First place to look |
|---|---|
| New species invisible, others fine | Step 2 skipped, or a wrong `:HOME.DGO` |
| New species white / untextured | `tpage-1607` / `tpage-853` missing from `lwideb.gd`, or the wrong `:HOME.DGO` |
| `process-drawable-art-error` on spawn | `<x>-ag.go` missing from LWIDEB, or the art check in `mod-chaos-probe-art!` is passing wrongly |
| No Metal Heads at all | Borrow did not apply — check `(-> *setting-control* user-current borrow)` in the REPL |
| Guards still chase Jak | `target-jak` re-set by a mission node; the `*mod-chaos-guards-ignore-jak*` override in `guard.gc` only applies to guards spawned since |
| Traffic pools look wrong / crash on district change | The `traffic-engine` resize — verify `vehicle-tracker-array` resolved via `overlay-at`, not the old `:offset 7024` |
| `too many users for nav-mesh #f` + crash on spawn | `*default-nav-mesh*` overflowed. First suspect a want-count above 20 (§3.5d), then the governor (§3.5c) |
| `traffic-manager: unable to spawn` spam | The 126-entry pedestrian tracker is full — lower `MOD_CHAOS_METALHEAD_POP` |
| Guard gunships circle but never engage | `mod-chaos-engage-vehicle!` not reaching them — check `(-> veh flags)` for `in-pursuit` in the REPL (§5.2) |
| New species and guard shove without damage | The `common-post` override is not being reached — confirm `chaos-metalhead` actually overrides it (§4.5) |
| Rapid gunner stands still and never shoots | `los` has no destination — check `enemy-method-63` is being inherited from `chaos-metalhead` (§4.6) |
| Hard crash (exit 5) with no GOAL error when a species spawns | An animation index of -1 reaching `(-> draw art-group data ...)`. Check that species' `enemy-info` for `-1` anims (§4.6) |

---

## 10. Known limitations

1. **Population ceiling per species** — 20, imposed by the traffic engine's fixed 20-handle
   reserve window per type. Not tunable without resizing `traffic-tracker` itself. See §3.5d.
2. **`:borrow-size` untouched** — relying on the PC port's 12× borrow multiplier to absorb the
   extra art. Deliberate (non-regression), but it is the first thing to raise if `lwideb` fails to
   load.
3. **Guard health applies on spawn only** — toggling mid-session affects new guards, not existing
   ones.
4. **Percentages are steady-state population, not spawn probability** — see §3.5. A species whose
   pool is momentarily empty is skipped by the draw, so short-term ratios will wobble.
5. **`*default-nav-mesh*` is enlarged unconditionally** — see §3.5c. It is the one change that is
   not behind `*mod-chaos-enable*`; it costs ~35 KB of extra global heap (122 unused slots x 288 bytes) and nothing else.
6. **The Metal Head population is whatever fits, not a fixed number** — the governor settles
   wherever the global nav-mesh has room, so the invasion is denser in a quiet district than in one
   already full of mission actors. `(mod-chaos-nav-report)` says what it settled on.

---

*(AI-assisted)*
