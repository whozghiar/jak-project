# Jetpack Crimson Guard — Technical Deep-Dive

> **Branch:** `jak2/features/jetpack-crimsonguard`
> **Game:** Jak 2
> **Slug:** `jetpack-crimsonguard`
> **Status:** implemented, **not yet validated in-game** (needs `task extract` + cold boot)

---

## 1. What already existed, and why it never flew over Haven City

Jak 2 ships a jet-propelled Krimzon Guard: `crimson-guard-hover`
([`goal_src/jak2/levels/common/enemy/hover/crimson-guard-hover.gc`](../../../goal_src/jak2/levels/common/enemy/hover/crimson-guard-hover.gc)).
Model, animations, gun, engine particles, death spiral — all of it is finished retail content. It
appears in FRA, FOB, FOR, DMI, STR, NEB, D3A and UNB, and never in the city.

The reason is navigation, not art. `crimson-guard-hover` derives from `hover-enemy`, which steers
through a per-instance `hover-nav-control`. That control holds a pointer to the **global**
`*nav-network*`:

```lisp
;; hover-nav-control.gc
(define *nav-network* (the-as nav-network 0))          ;; <- 0 until a level installs one
```

and each level that hosts hover enemies installs its own static adjacency graph:

| Level | Installer |
|---|---|
| Forest | `forest-obs.gc` → `(nav-network-method-10 *nav-network* arg0 *forest-adjacency*)` |
| Drill | `drill-obs.gc` → `*drill-adjacency*` |
| Fortress rescue | `forresca-obs.gc` → `*fortress-adjacency*` |
| Nest boss | `nestb-scenes.gc` → `*nestb-adjacency*` |
| Under | `underb-master.gc` → `*under-adjacency*` |

Haven City installs nothing, so `*nav-network*` stays `0` there. Any network call on it
dereferences null.

### The three options, and why option 3 won

| Option | Cost | Verdict |
|---|---|---|
| 1. Author a `*ctywide-adjacency*` network for the whole city | Days of in-game data authoring through `hover-nav-edit.gc`, and a large static table shipped in CWI | Rejected — enormous, and mostly wasted on guards that spend their life above roof height |
| 2. Write a new flying actor from scratch on the `citizen-enemy` / traffic base | New state machine, new animation table, loses the retail gun/engine/death behaviour | Rejected — reimplements finished content |
| 3. Run the retail hover guard with network pathing switched off | One flag | **Chosen** |

---

## 2. The mechanism: `honflags-0`

Reading [`hover-nav-control.gc`](../../../goal_src/jak2/levels/common/enemy/hover/hover-nav-control.gc),
**every** network call sits behind the same guard:

```lisp
(when (not (logtest? (-> this flags) (hover-nav-flags honflags-0)))
  ... nav-network-method-2x ...
  )
```

| Method | What the guarded block does | What survives when the flag is set |
|---|---|---|
| `hover-nav-control-method-11` (set destination) | network re-path when line of sight is lost | the steering toward `dest-pos` that follows the block — it is **outside** the guard |
| `hover-nav-control-method-13` (per-frame physics) | `nav-network-method-26`, the network collision impulse | acceleration, friction, velocity integration |
| `hover-nav-control-method-24` | the line-of-sight probe that triggers re-pathing | nothing needed |

`honflags-0` is not a hack flag invented for this mod — it is retail's *"I am following a scripted
path, leave my route alone"* bit. `hover-nav-control-method-18` and `-19` set it when a
`path-control` is handed over, and `-20` clears it. Retail hover enemies therefore already spend
part of their life with it set, which is what makes this safe: the code path is exercised by the
shipping game.

**What is actually lost:** network-based obstacle avoidance. A jetpack guard will fly straight at
its target. That is why the dispatcher (below) drops them in at **18 m above the player** — at that
altitude Haven City is essentially empty air.

```lisp
;; jetpack-guard.gc -- init-enemy!
(if (nonzero? (-> this hover))
    (logior! (-> this hover flags) (hover-nav-flags honflags-0))
    )
```

---

## 3. The actor

```lisp
(deftype jetpack-crimson-guard (crimson-guard-hover)
  ((next-scan-time  time-frame))
  )
```

One field, one overridden method, one overridden state. Everything else — the gun, the kick attack,
the knocked/recover arc, the flying death and explosion — is inherited untouched.

### 3.1 `init-enemy!` — four adjustments

```lisp
(defmethod init-enemy! ((this jetpack-crimson-guard))
  ((method-of-type crimson-guard-hover init-enemy!) this)   ;; 1. full retail bring-up first
  (logior! (-> this hover flags) (hover-nav-flags honflags-0))  ;; 2. free flight
  (logclear! (-> this mask) (process-mask enemy))           ;; 3. faction: a guard...
  (logior! (-> this mask) (process-mask guard))
  (reset-to-collide-spec (-> this focus) (collide-spec enemy))  ;; 4. ...that only sees metal heads
  ...)
```

The parent init must run **first**: `hover` is allocated inside it, by
`hover-enemy-method-155`, so the flag cannot be set any earlier.

Adjustment 3 mirrors exactly what `crimson-guard::citizen-init!` does for the ground guards. It is
what stops the Haven City : Chaos blast bot — whose target test is `enemy && !guard` — from
gunning down its own air support.

There is a fourth, easy-to-miss piece: a guard that only *sees* metal heads is still invisible *to*
them. Metal heads focus on `collide-spec civilian`, which is how they find citizens and ground
guards, so the root primitive's `collide-as` gains `civilian`:

```lisp
(set! (-> root-prim prim-core collide-as) (collide-spec enemy civilian))
(set! (-> cshape backup-collide-as) (-> root-prim prim-core collide-as))
```

`backup-collide-as` has to be refreshed too — it is what the collide shape is restored from.

### 3.2 The `hostile` override

`hover-enemy`'s `hostile` is `:code hover-enemy-fly-code` + `:post hover-enemy-hostile-post` and
has **no `:trans`**. `crimson-guard-hover` adds a `:trans` that only handles speech and the
commit-to-attack range test. Neither ever re-acquires a target, because retail hover guards are
placed with a single scripted quarry.

A dispatched city guard needs to keep finding new work, so the override adds a re-scan:

```lisp
:trans (behavior ()
  (when (>= (current-time) (-> self next-scan-time))
    (set! (-> self next-scan-time) (+ (current-time) (seconds 0.35)))
    (let ((current (handle->process (-> self focus handle))))
      (when (or (not current) (logtest? ... (focus-status dead disable ignore inactive)))
        (let ((prey (jetpack-guard-nearest-prey self MOD_JETPACK_PREY_DIST)))
          (if prey (try-update-focus (-> self focus) prey self) (clear-focused (-> self focus)))))))
  ;; then the retail trans
  (let ((parent-trans (-> (method-of-type crimson-guard-hover hostile) trans)))
    (if parent-trans (parent-trans))))
```

Three details worth keeping in mind:

- **Only re-scan when the current focus is gone.** Re-picking every scan would make the guard
  flip-flop between two equidistant metal heads and never close.
- **A 0.35 s period, not every frame.** `jetpack-guard-nearest-prey` walks `*actor-hash*`.
- **No focus is a valid state.** `hover-enemy-hostile-post` handles `focus == #f` by setting
  `dest-pos` to the guard's own position — it hovers in place. Since the state has no exit
  condition, the guard simply loiters until something shows up. That is the desired behaviour and
  it is why the state never needs an `active` or `idle` counterpart.

### 3.3 Target selection

```lisp
(and (logtest? (-> proc mask) (process-mask enemy))
     (not (logtest? (-> proc mask) (process-mask guard))))
```

This is the project-wide metal-head test and it is worth stating once:

| Actor | `process-mask enemy` | `process-mask guard` |
|---|---|---|
| City metal head (`citizen-enemy` subclass) | ✅ set by `citizen-enemy::citizen-init!` | ❌ |
| Krimzon Guard (`crimson-guard`) | ❌ explicitly cleared | ✅ |
| Citizen (`civilian`) | ❌ | ❌ |

`enemy && !guard` therefore isolates metal heads exactly, with no type checks and no dependence on
the Haven City : Chaos branch being present. That independence is deliberate: this branch has to
stand alone.

---

## 4. Spawning without an entity

A dynamically created actor has no BSP entity, and `initialize-skeleton` needs one to bind a draw
control — without it the process dies with `process-drawable-art-error`. The city's answer is
`lwide-entity-hack`, the same call every traffic citizen makes:

```lisp
(defbehavior jetpack-guard-init-by-other jetpack-crimson-guard ((arg0 vector))
  (stack-size-set! (-> self main-thread) 512)
  (lwide-entity-hack)          ;; re-home onto a resident city entity
  (init-enemy-collision! self)
  (set! (-> self root trans quad) (-> arg0 quad))
  (quaternion-identity! (-> self root quat))
  (vector-identity! (-> self root scale))
  (init-enemy! self)
  (go-virtual hostile)         ;; NOT ambush
  (none))
```

`go-virtual hostile` is the other half of the network workaround. Retail hover guards enter
`ambush`, which reads a `path-control` off the placed entity and feeds it to
`hover-nav-control-method-18` — both unavailable and both network-bound. Jumping straight to
`hostile` is the same trick `bombbot-init-by-other` uses.

---

## 5. Dispatcher

`mod-jetpack-tick` is a plain function called once per frame from `traffic-manager::update`:

```lisp
;; traffic-manager.gc
(if *mod-jetpack-enable*
    (mod-jetpack-tick this)
    )
```

Driven by the traffic manager rather than by a process of its own, deliberately: it inherits the
manager's lifetime exactly, so it can never tick after Haven City is gone, and there is no
lifecycle of its own to get wrong.

Each frame it:

1. **Reaps** — clears dead handles and deactivates any guard further than `MOD_JETPACK_CULL_DIST`
   (140 m) from the player. Without a city nav graph these guards do not patrol, so one that has
   chased a metal head into the distance is pure waste.
2. **Dispatches** — every `MOD_JETPACK_ROLL_PERIOD` (6 s), rolls `MOD_JETPACK_SPAWN_PERCENT` (35%)
   for one new guard into the first free slot, on a ring `MOD_JETPACK_SPAWN_DIST` (45 m) around the
   player and `MOD_JETPACK_SPAWN_HEIGHT` (18 m) up.

Population is capped at `MOD_JETPACK_MAX_GUARDS` (3). Every number is a `defconstant` in
[`pc/mods/jetpack-crimsonguard-h.gc`](../../../goal_src/jak2/pc/mods/jetpack-crimsonguard-h.gc).

---

## 6. Build wiring

### 6.1 Circuit 1 — GOAL heap

`CWI.DGO` gains the retail hover stack, in FRA.DGO's order:

```
hover-formation-h.o  hover-nav-control-h.o  hover-enemy-h.o  hover-nav-network.o
hover-nav-control.o  hover-enemy.o  hover-enemy-battle.o  hover-formation.o
crimson-guard-hover.o
```

`hover-nav-network.o` is included even though the city has no network — it is the file that
*defines* `*nav-network*`, and the symbol has to exist.

`jetpack-guard.o` goes in after `traffic-manager.o`, because the manager drives it.

Art goes into **all three** ambient-population levels (`lwidea.gd`, `lwideb.gd`, `lwidec.gd`), so a
district transition can never strand a dispatched guard without a skeleton:

```
"tpage-3192.go"                 ;; forresca-vis-pris -- the hover guard's home texture page
"crimson-guard-hover-ag.go"
```

### 6.2 Circuit 2 — PC renderer

Adding the art group to a `.gd` only loads the *skeleton*. The PC `Merc2` renderer reads mesh and
texture data from the resident `.fr3`, so the geometry has to be baked there as well:

```jsonc
// decompiler/config/jak2/jak2_config.jsonc
"extra_art_groups_by_dgo": {
  "LWIDEA.DGO": ["crimson-guard-hover-ag:FRA.DGO"],
  "LWIDEB.DGO": ["crimson-guard-hover-ag:FRA.DGO"],
  "LWIDEC.DGO": ["crimson-guard-hover-ag:FRA.DGO"]
}
```

The `:FRA.DGO` suffix names the **home** level, whose texture remap table resolves the model's
(home-relative) texture ids. Omit it and the guards render white and shiny.

**`task extract` is mandatory after checking out this branch.** Skip it and the guards fly, shoot
and die — invisibly. See
[`docs/modding/tools/model_and_entity_level_injection_guide.md`](../tools/model_and_entity_level_injection_guide.md).

### 6.3 `game.gp`

The three new sources have no `all_objs.json` entry (they are not decompiler output), so they are
pre-marked in `*file-entry-map*` and built by explicit `goal-src` steps whose dependencies pin the
compile order:

```lisp
(goal-src "pc/mods/jetpack-crimsonguard-h.gc" "traffic-h")
(goal-src "pc/debug/jetpack-crimsonguard-menu.gc" "jetpack-crimsonguard-h" "mods-menu")
(goal-src "levels/city/jetpack/jetpack-guard.gc" "crimson-guard-hover" "traffic-manager" "jetpack-crimsonguard-h")
```

`mod-jetpack-tick` is `define-extern`'d in the `-h` file because `traffic-manager.gc` (CWI) calls
it while `jetpack-guard.gc` (also CWI) is compiled afterwards.

---

## 7. Validation checklist

No part of this has been run yet. In order:

1. `task set-game-jak2`
2. `task extract` — watch for
   `extra_art_groups_by_dgo: baking 'crimson-guard-hover-ag' into LWIDEA.DGO`
3. `task boot-game` — **cold boot, not `(mi)`**. This branch adds types to CWI.DGO, and the
   ghost-memory rule in [`AGENTS.md`](../../../AGENTS.md) applies.
4. In the city: `Debug ▸ Mods ▸ jetpack-crimsonguard ▸ Enable`.

What to watch for, and where to look first if it goes wrong:

| Symptom | First place to look |
|---|---|
| Guards are invisible | Step 2 was skipped, or `:FRA.DGO` is wrong |
| White / untextured guards | `tpage-3192.go` missing from the `lwide*.gd` you are in |
| `process-drawable-art-error` on spawn | `lwide-entity-hack` not reached, or `crimson-guard-hover-ag.go` missing from the active `lwide*` |
| Crash the moment one flies | `honflags-0` not set — confirm `init-enemy!` runs the parent first |
| Guards clip through buildings | Expected: there is no obstacle avoidance. Raise `MOD_JETPACK_SPAWN_HEIGHT` |
| Guards ignore metal heads | Metal heads not present (this branch alone does not spawn any — pair it with Haven City : Chaos, or test during the retail late-game invasion) |

> [!IMPORTANT]
> On its own this branch adds flying guards but **no metal heads**. To see them fight, either merge
> `jak2/features/haven-city-chaos` or test during the retail end-game invasion, when `lwideb` is
> borrowed by the story.

---

## 8. Integration with Haven City : Chaos

This branch is merged into `jak2/features/haven-city-chaos`, where it keeps its own submenu and
its own dispatcher call — the chaos menu's `guards ▸ Jetpack guards` row just writes the same
`*mod-jetpack-enable*` symbol, so there is a single switch reachable from two places.

The merge conflicts are all additive (both branches append to `cwi.gd`, `game.gd`, `lwideb.gd`,
`game.gp`, `jak2_config.jsonc` and `traffic-manager::update`); resolving them is a matter of
keeping both sides. The one judgement call is `traffic-manager::update`: keep both hook lines
rather than folding the jetpack dispatcher behind the chaos hook, so this mod stays usable on
its own.

On its own this branch adds flying guards but no metal heads; merged, it gets a city full of
them.

---

*(AI-assisted)*
