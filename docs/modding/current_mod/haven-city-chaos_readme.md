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
(chaos-juicer 22) (chaos-spyder 23)
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
(defconstant MOD_CHAOS_SHARE_JUICER   10)  ;; "Juice goon"
(defconstant MOD_CHAOS_SHARE_SPYDER    5)  ;; "Spyder gunner"
(defconstant MOD_CHAOS_METALHEAD_POP  60)  ;; retail lwideb runs 14 + 14 + 14 = 42

;; want = share * POP / (sum of the shares that are currently switched on)
```

Only the species that are enabled contribute to the denominator, so the whole budget is always
spent: with everything on it is 85, with only the three defaults on it is 70 and those three
absorb the rest. That is what makes a per-species menu switch meaningful — turning Juice goon off
makes the Grunts *more* numerous rather than making the invasion smaller.

`mod-chaos-enroll-species!` writes `want-count`, `target-count` and `reserve-count` together,
mirroring `restore-default-settings`' own `(max 1000 (min #xfde8 (* 1000 want-count)))` formula so
that a mid-session toggle behaves exactly like a fresh city load.

### 3.5b Raising the overall spawn rates

`MOD_CHAOS_METALHEAD_POP` alone is not enough: three other ceilings decide whether the extra
actors ever materialise. Modelled on `jak2/config/enhanced_spawnrates`, all gated on
`*mod-chaos-enable*`:

| Lever | Retail | Mod | Where |
|---|---|---|---|
| Krimzon Guard want-count (type 6) | 9 | 16 | `mod-chaos-boost-ambient!` |
| guard-bike / hellcat want-count (18 / 19) | 4 / 3 | 8 / 6 | `mod-chaos-boost-ambient!` |
| `inv-density-factor` | 5.0 | 3.0 | `mod-chaos-boost-ambient!` |
| per-cell activation ranges | 81920 / 819200 / 491520 | 122880 / 983040 / 655360 | `traffic-engine.gc` |
| nav-mesh `nav-max-users` | default 64 | clamped to `[128, 200]` | `nav-mesh.gc` |

The nav-mesh ceiling is the one that bites hardest in practice: hitting it does not crash, it just
makes `spawn-all` fail quietly (`traffic-manager: unable to spawn`) and the city stays half-empty
however high the want-counts are. It is read once, in `nav-mesh::init-from-entity`, so **it only
takes effect on the next Haven City load** — enable the mod, step indoors and come back out.

Citizen want-counts are deliberately left at retail values: the pedestrian tracker is capped at
126 live processes (`traffic-tracker::active-object-list`) and the metal-head budget plus the guard
bump already claims the headroom.

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
(defmethod get-nav-info ((this chaos-juicer)) *juicer-nav-enemy-info*)

(defmethod init-enemy-collision! ((this chaos-juicer))
  ((method-of-type juicer init-enemy-collision!) (the-as juicer this))
  (chaos-cityify-collision! this))
```

Both of these point straight at the retail enemy rather than copying it:

- **`get-nav-info` returns the retail static.** Hit points, notice distances, knock-back curves,
  the full idle-animation script and the walk/run animation indices all come across exactly right,
  for free. It is read-only — never mutate it, the Pumping Station juicers share the object.
- **`init-enemy-collision!` calls the retail method through a cast.** Those methods only ever touch
  `(-> this root)`, which sits at the same offset in every `nav-enemy` subclass, so the cast is
  safe — and the primitive layout stays keyed to the right joint indices instead of drifting from
  a hand-written copy.

### 4.3 `chaos-cityify-collision!` — the two bits that matter

Retail enemies live in arenas where the only thing worth colliding with is Jak. Comparing
`metalhead-grunt::init-enemy-collision!` with `juicer::init-enemy-collision!` isolates the
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

### 4.4 The one behaviour that had to be written

`nav-enemy`'s `hostile` has a `:trans` and a `:post` but **no `:code`** — each retail enemy
supplies its own chase animation loop. Inherited as-is, a chasing species would keep playing the
`active` walk cycle while moving at run speed. `chaos-metalhead` solves it once for both, with a
fallback for species that ship with `run-anim -1` because they have no run cycle at all:

```lisp
(defmethod chaos-chase-anim ((this chaos-metalhead))
  (let ((run (-> this enemy-info run-anim)))
    (if (>= run 0) run (-> this enemy-info walk-anim))))
```

Doing it this way rather than patching `run-anim` on the shared static is the point: patching would
leak into the retail enemies that share the object.

### 4.5 The intangibility bug, and the filter that caused it

The first playable build had the Juice goon and the Krimzon Guard walk into each other, shove, and
then stand there: the guard swung its rifle butt with no effect, the juicer did nothing at all.

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
| `juicer` / `spyder` (arena enemies) | `jak bot player-list` |

`civilian` is what Krimzon Guards and citizens register as, and `vehicle-sphere` is what city
traffic registers as. With the arena filter, a Juice goon in Haven City can only ever produce a
touch entry against **Jak**. The two shapes still collide as solids — hence the shoving — but no
touch entry means no `attack` in either direction, so neither the guard's rifle butt nor the
juicer's own permanently-`deadly` body primitive can land.

The fix is a `common-post` override on `chaos-metalhead` that uses the city filter. Patching
`enemy-info` itself is not an option: `*juicer-nav-enemy-info*` is a shared static that the Pumping
Station juicers read too.

**Second half of the same bug.** `enemy-method-104` stamps every `attack` event with the attacker's
`attack-id`, and the victim remembers the last id it took damage from — so an unchanging id lands
exactly once however long the contact lasts. Retail enemies get a fresh id every time they enter
their `attack` state. `chaos-metalhead` has no scripted attack state to enter (the retail `attack`
states are written against `juicer` / `spyder` fields that a `citizen-enemy` subclass does not
have), so it re-stamps on a cadence instead:

```lisp
(when (time-elapsed? (-> self next-melee-time) MOD_CHAOS_MELEE_PERIOD)   ;; 0.8s
  (set-time! (-> self next-melee-time))
  ... bump *game-info* attack-id into (-> self attack-id) ...
  (logior! (-> self focus-status) (focus-status dangerous)))
```

That turns a permanent shove into a repeating melee. It is a charge-and-contact model, not a
frame-accurate reproduction of the arena attacks — which for the juicer, a suicide charger whose
root primitive is permanently `deadly` in retail, is close to the original intent anyway.

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
| `CWI.DGO` | `juicer.o`, `spyder.o`, `chaos-species.o` (before `traffic-engine.o`); `chaos-city.o` (after `traffic-manager.o`) |
| `LWIDEB.DGO` | `tpage-1607.go`, `juicer-ag.go`, `spyder-ag.go` |

Note that the enemies' **code** and **art** ship in different DGOs — code in CWI (resident
everywhere in the city), art in the LWIDEB borrow. That is retail's own arrangement: `hopper.o` is
in MTN/STA while `hopper-ag` is in MTX/STADBLMP.

Both species share a single texture page, so the art cost is one page:

| Home DGO | Texture page | Species |
|---|---|---|
| `ATE.DGO` | `tpage-1607` (atollext-vis-pris) | juicer, spyder |

### 7.2 Circuit 2 — PC renderer

A `.gd` entry loads only the *skeleton*. The PC `Merc2` renderer reads mesh and texture data from
the resident `.fr3`:

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEB.DGO": ["juicer-ag:ATE.DGO", "spyder-ag:ATE.DGO"]
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
(goal-src "levels/city/chaos/chaos-species.gc" "citizen-enemy" "metalhead-grunt" "juicer" "spyder")
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
  species ▸ Juice goon (10%)      off by default  (chaos-juicer, extra art)
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
   `extra_art_groups_by_dgo: baking 'juicer-ag' into LWIDEB.DGO`
3. `task boot-game` — **cold boot, not `(mi)`**. This branch changes `traffic-engine`'s field
   layout, which is precisely the case the ghost-memory rule in
   [`AGENTS.md`](../../../AGENTS.md) warns about: a hot reload would leave the old layout in
   simulated memory and appear to work while being broken on a clean launch.
4. In the city: `Debug ▸ Mods ▸ haven-city-chaos ▸ Enable`.

| Symptom | First place to look |
|---|---|
| New species invisible, others fine | Step 2 skipped, or a wrong `:HOME.DGO` |
| New species white / untextured | `tpage-1607` missing from `lwideb.gd` |
| `process-drawable-art-error` on spawn | `<x>-ag.go` missing from LWIDEB, or the art check in `mod-chaos-probe-art!` is passing wrongly |
| No Metal Heads at all | Borrow did not apply — check `(-> *setting-control* user-current borrow)` in the REPL |
| Guards still chase Jak | `target-jak` re-set by a mission node; the `*mod-chaos-guards-ignore-jak*` override in `guard.gc` only applies to guards spawned since |
| Traffic pools look wrong / crash on district change | The `traffic-engine` resize — verify `vehicle-tracker-array` resolved via `overlay-at`, not the old `:offset 7024` |
| City feels no busier than retail | The nav-mesh ceiling is read at level init — reload Haven City after enabling (§3.5b) |
| `traffic-manager: unable to spawn` spam | Same ceiling, or the 126-entry pedestrian tracker is full — lower `MOD_CHAOS_METALHEAD_POP` |
| Guard gunships circle but never engage | `mod-chaos-engage-vehicle!` not reaching them — check `(-> veh flags)` for `in-pursuit` in the REPL (§5.2) |
| Juice goon and guard shove without damage | The `common-post` override is not being reached — confirm `chaos-metalhead` actually overrides it (§4.5) |

---

## 10. Known limitations

1. **Combat fidelity of the two new species** — charge-and-contact on a fixed melee cadence rather
   than their home levels' bespoke attacks (the juicer's scripted charge, the spyder's
   cloak-and-shoot). See §4.5.
2. **`:borrow-size` untouched** — relying on the PC port's 12× borrow multiplier to absorb the
   extra art. Deliberate (non-regression), but it is the first thing to raise if `lwideb` fails to
   load.
3. **Guard health applies on spawn only** — toggling mid-session affects new guards, not existing
   ones.
4. **Percentages are steady-state population, not spawn probability** — see §3.5. A species whose
   pool is momentarily empty is skipped by the draw, so short-term ratios will wobble.
5. **The nav-mesh user ceiling needs a level reload** — see §3.5b. Enabling the mod mid-session
   gives the new want-counts immediately but not the headroom to fill them.

---

*(AI-assisted)*
