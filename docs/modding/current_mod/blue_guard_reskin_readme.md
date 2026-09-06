# Jak 2 — Blue Crimson Guard Reskin (`crimson-blue-guard`)

> **Mod Readme / Readme du Mod**
>
> - **Branch / Branche :** `jak2/features/blueguard`
> - **Type :** `features`
> - **Depends on / Dépend de :** the existing `build-actor` custom-actor pipeline
>   (`goal_src/jak2/lib/project-lib.gp`, `goalc/build_actor/`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## 1. What this is

A blue-recolored Crimson Guard, added as its **own standalone GOAL entity** (`crimson-blue-guard`)
rather than a global texture replacement — the stock red `crimson-guard` keeps spawning
unmodified. The blue variant is identical to `crimson-guard` in every respect (animations, death,
collision, weapon loadout, ...) except one: it is passive toward Jak by default, and only becomes
personally hostile toward him if he attacks it directly (no city-wide alarm either way) — see §5.
A separate, manually-triggered function makes it fight another guard on purpose (also §5). It is
mixed into Haven City's ambient guard traffic.

The source asset is `custom_assets/jak2/models/custom_levels/crimson-blue-guard.glb` (also copied
to `custom_assets/jak2/models/common/crimson-blue-guard-lod0.glb`, see §4.3): the decompiled native
`crimson-guard` skeleton + all 40 of its animations, re-skinned with a recolored texture set in
Blender, then re-exported.

## 2. The core problem: animation slot indices

`crimson-guard`'s ~4700 lines of AI/state-machine code (`guard.gc`,
`levels/city/traffic/citizen/guard.gc`) reference its animations almost entirely by **numeric
slot index** into its art-group's element array — either through overridable fields
(`anim-walk`, `anim-run`, `anim-get-up-front`, ...) set once in `init-enemy!`, or, in a handful of
methods (`enemy-method-77`, `enemy-method-78`, `set-behavior!`), as **raw literals** baked
directly into the method body (`(-> this draw art-group data 42)` and friends).

The native `crimson-guard-ag` art-group has a fixed layout (see
`decompiler/config/jak2/ntsc_v1/art-group-info.min.json`, key `crimson-guard-ag`):

| Slot | Content |
|---|---|
| 0 | `crimson-guard-lod0-jg` (skinned mesh) |
| 1 | `crimson-guard-lod0-mg` |
| 2 | `crimson-guard-lod2-mg` |
| 3 | `crimson-guard-shadow-mg` |
| 4..43 | 40 animations, in a fixed order (`idle`@4, `walk`@5, `run`@6, ..., `get-up-front`@33, `get-up-back`@34, ...) |

The existing `build-actor` tool (`goalc/build_actor/jak2/build_actor.cpp`) does **not** reproduce
this layout for a standalone custom actor: it always emits a 2-slot header (`jgeo`, one dummy
null slot) before the animations, and it orders animations by their order in the source `.glb`'s
`animations` array — which a normal Blender/glTF export sorts alphabetically. Building the blue
guard "as-is" would have put `crimson-blue-guard-ag`'s `idle` at slot 2 instead of 4, `get-up-back`
at some alphabetically-derived slot instead of 34, etc. — silently playing the *wrong* animation
in every hardcoded-index code path, breaking the "identical behavior" requirement in subtle,
hard-to-notice ways (e.g. only the vehicle-knockout or yellow-eco-hit reactions, which use raw
literals, would be wrong).

## 3. The fix — two additive, opt-in pieces

### 3.1 `build-actor :native-header #t`

`goal_src/jak2/lib/project-lib.gp`'s `build-actor` macro gained a new `&key (native-header #f)`
parameter, threaded through to the `build-actor2` data-compiler tool
(`goalc/make/Tools.cpp::BuildActor2Tool`) and finally to
`jak2::BuildActorParams2::native_anim_header` (`goalc/build_actor/jak2/build_actor.h`). When set,
`run_build_actor` (`goalc/build_actor/jak2/build_actor.cpp`) emits **two extra null placeholder
slots** after the mesh, padding the header from 2 to 4 slots — matching the native layout exactly.
Default is `#f`, so every existing custom actor (`test-actor`, the jetboard, etc.) is completely
unaffected.

```lisp
(build-actor "crimson-blue-guard" :force-run #t :native-header #t)
```

### 3.2 Reordering the source `.glb`'s animation array

A one-off Python script reordered `crimson_blue_guard.glb`'s `animations` JSON array (pure
reordering of array elements — no accessor/bufferView/mesh data touched) to match the 40-name
canonical order from `art-group-info.min.json` above. Combined with the 4-slot native header,
this makes `crimson-blue-guard-ag`'s slot N hold the *same* animation as `crimson-guard-ag`'s slot
N, for every N. If you ever need to rebuild the `.glb` from a fresh Blender export, re-run
`python scripts/modding/reorder_crimson_guard_glb_anims.py <in.glb> <out.glb>` before running
`build-actor`, or your animation indices will drift again.

With both pieces in place, `crimson-blue-guard` needs only to override
`init-enemy!` (`goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`) to point at its
own skeleton-group by name — every other inherited method/state from `crimson-guard` keeps
working with the exact same numeric indices, unmodified.

```lisp
(deftype crimson-blue-guard (crimson-guard) ())

(def-art-elt crimson-blue-guard-ag crimson-blue-guard-lod0-jg 0)
(def-art-elt crimson-blue-guard-ag crimson-blue-guard-lod0-mg 1)

(defskelgroup skel-crimson-blue-guard crimson-blue-guard crimson-blue-guard-lod0-jg -1
              ((crimson-blue-guard-lod0-mg (meters 999999)))
              :bounds (static-spherem 0 0 0 5)
              :origin-joint-index 3)

(defmethod init-enemy! ((this crimson-blue-guard))
  ;; identical to crimson-guard's init-enemy!, except the skeleton-group name
  ...)
```

## 4. Getting it into the world

- **Code residency:** `crimson-blue-guard.gc` compiles to `crimson-blue-guard.o`, added next to
  `guard.o` in `goal_src/jak2/dgos/cwi.gd` (the always-resident common DGO that already carries
  `crimson-guard`'s own code).
- **Art residency:** `crimson-blue-guard-ag.go` was added next to every existing
  `crimson-guard-ag.go` entry (append-only, nothing removed) in the 10 level DGOs that carry it:
  `cas.gd`, `dg1.gd`, `fdb.gd`, `fea.gd`, `fob.gd`, `fra.gd`, `lwidea.gd`, `lwideb.gd`, `lwidec.gd`,
  `pae.gd`. This guarantees the blue variant's assets are loaded everywhere the stock guard's are,
  so it can never be picked for a spawn without its art being resident.
- **Ambient traffic spawning:** `traffic-manager.gc::traffic-object-spawn` is the single place
  where the traffic simulation turns a `(traffic-type crimson-guard-1)` /
  `(traffic-type crimson-guard-0)` pick into a concrete process, via
  `(citizen-spawn arg0 crimson-guard arg1)`. Both call sites now roll
  `(-> arg1 id)` (`traffic-object-spawn-params`'s per-spawn counter) against a new global,
  `*crimson-blue-guard-ratio*` (default `8`, i.e. roughly 1 spawn in 8), substituting
  `crimson-blue-guard` for `crimson-guard` on the hit — mirroring the pre-existing
  `dark-guard-ratio` mechanism used for the "dark guard" variant a few lines above. This is the
  **only** touch point in the whole traffic simulation: the `traffic-type` enum, the
  `guard-type-info-array` weighting table, and everything else about how/when/where a guard slot
  gets picked is completely untouched — `crimson-blue-guard` is just an alternate concrete type
  for an existing spawn decision, so all traffic-engine bookkeeping (nav mesh, alert state,
  population counts) behaves identically whichever variant lands in that process slot.
- `(declare-type crimson-blue-guard crimson-guard)` was added near the top of `traffic-manager.gc`
  so the reference above compiles independent of file ordering (same idiom as `crimson-guard`'s
  own forward declaration in `traffic-engine.gc`).

### 4.3 A second, easy-to-miss piece: the actual drawable geometry ("Circuit 2")

`build-actor` (Circuit 1, §3) only produces the skeleton/animations art-group. The actual triangles
+ textures the PC renderer draws (Circuit 2) come from a completely separate system: the
decompiler bakes them into `.fr3` files, looked up **by name** at runtime. See
`docs/modding/jak2_modding_utilities/19_injecting_a_model_into_a_level.md` for the full mechanism.
`build-actor`'s own merc-ctrl output is a placeholder (`generate_dummy_merc_ctrl` in
`build_actor.cpp` literally reuses a hardcoded dummy mesh) — without Circuit 2, the guard spawns,
moves and makes sound normally, but is **invisible**.

The fix: a second copy of the same `.glb`, renamed to match the placeholder merc-ctrl's own name
(`<art-group-name>-lod0`, here `crimson-blue-guard-lod0.glb`), dropped in
`custom_assets/jak2/models/common/`. The decompiler's `add_custom_model_to_level`
(`decompiler/level_extractor/extract_merc.cpp`) auto-scans that folder at `task extract` time — no
config needed — and bakes the model + all its textures into `GAME.fr3` (`common` → always
resident, regardless of level). This is a one-time step (or after any `.glb` model change); it
does **not** need to be repeated after ordinary `(mi)` GOAL-code iteration.

## 5. Faction behavior

`crimson-blue-guard` is deliberately **100% identical to `crimson-guard` in everything except one
thing**: it does not fight *for* the Crimson Guard side against Jak by default. Everything else —
collision, animations, death, movement, weapon loadout, spawn weighting — is whatever
`crimson-guard` already does, completely untouched. The only overrides, in
`goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`, are:

- **`citizen-init!` override** — forces the "not targeting Jak" `focus collide-with` collide-spec
  unconditionally (crimson-guard's own version picks it based on the *shared*, city-wide
  `traffic-alert-flag target-jak` flag, which can't be used to keep just one variant passive). The
  guard keeps its `enemy` collide-as bit (so it's still a valid target for others), it just never
  opportunistically treats Jak as a target on its own.
- **`general-event-handler` override**:
  - `'hit`/`'hit-flinch`/`'hit-knocked`: matches crimson-guard's own case line for line, with one
    change — if the attacker is Jak specifically (`(process-mask target)`), the guard remembers him
    as its target (`traffic-target-status handle` + focus) instead of calling `trigger-alert`, so
    the city-wide alarm never raises. Either way it still falls through to
    `(method-of-type nav-enemy general-event-handler)`, the exact same call stock crimson-guard
    makes — so the actual flinch/knockback/get-up/hostile transition, and everything about how it
    then fights, is 100% stock. Any non-Jak attacker is identical to stock crimson-guard (already a
    no-op on the city alert per `traffic-engine::increase-alert-level`'s own
    `(process-mask target)` check).
  - `'panic`/`'clear-path`: identical to stock, except danger attributed to Jak (gunfire near the
    guard, not necessarily a direct hit — see `traffic-engine::update-danger-from-target`, which
    always stores Jak's handle as the source) never raises the alert either. Without this, firing a
    weapon near the guard would still sound the alarm even with the `'hit` fix above.
  - `'alert-begin` is turned into a deliberate no-op: stock crimson-guard's version targets whoever
    triggered the alert (almost always Jak) and goes hostile toward them — exactly the "attacks Jak
    during a general alert" behavior this variant must not have.
- **`crimson-blue-guard-attack-guards`** (plain `defun`, not a method, not called from anywhere
  automatically) — the one way to make this guard fight another guard on purpose. Finds the nearest
  other (non-blue) `crimson-guard` within ~40m via the existing `find-nearest-attackable` utility
  (`engine/collide/find-nearest.gc`), excludes `crimson-blue-guard` itself via `type-type?` so blue
  guards can't be made to target each other, then sets the target and calls `go-hostile` — same
  mechanism `'alert-begin`/`'hit` use. Call it from the REPL once you have a handle on the guard
  (e.g. `(define g (spawn-crimson-blue-guard-debug 0))`, then
  `(crimson-blue-guard-attack-guards (the-as crimson-blue-guard g))`).

None of this touches `crimson-guard`/`guard.gc` itself. **Caveat on the manual trigger:** it reuses
crimson-guard's own combat state machine unmodified, which is generic about *what* the current
target is (it reads `(-> this focus handle)`/`traffic-target-status handle`, not a hardcoded
`*target*` check) — but stock `crimson-guard` never actually has occasion to point that machinery at
another guard, only at Jak, so this exact combination (guard vs. guard) has no native precedent to
verify against. Whether a red guard that gets shot back fights back is governed entirely by stock,
unmodified `crimson-guard` code — nothing here adds guard-vs-guard retaliation to the stock type.

## 6. Engine Changes Made on This Branch

| File | Change | Why |
|---|---|---|
| `goalc/build_actor/jak2/build_actor.h` | `BuildActorParams2` gained `bool native_anim_header = false;` | carries the new opt-in flag |
| `goalc/build_actor/jak2/build_actor.cpp` | `run_build_actor` emits 2 extra null header slots when the flag is set | matches the native 4-slot art-group header so reskins can reuse original anim indices |
| `goalc/make/Tools.cpp` | `BuildActor2Tool::needs_run`/`::run` accept a 9th `:in` element, parsed into `native_anim_header`; max input count raised from 8 to 9 | plumbs the flag from the GOAL macro through to the tool |
| `goal_src/jak2/lib/project-lib.gp` | `build-actor` macro gained `&key (native-header #f)`, appended to the `:in` list | GOAL-side opt-in switch, defaults preserve all existing custom actors |
| `goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc` (new) | `deftype`, `def-art-elt` x2, `defskelgroup`, `init-enemy!` override | the new entity itself |
| `goal_src/jak2/game.gp` | `(build-actor "crimson-blue-guard" ...)` + `(goal-src ...)` registration | builds the art-group, registers the new source file |
| `goal_src/jak2/dgos/cwi.gd` | `"crimson-blue-guard.o"` added next to `"guard.o"` | code residency |
| `goal_src/jak2/dgos/{cas,dg1,fdb,fea,fob,fra,lwidea,lwideb,lwidec,pae}.gd` | `"crimson-blue-guard-ag.go"` added next to each `"crimson-guard-ag.go"` | art residency, matching the stock guard's footprint exactly |
| `goal_src/jak2/levels/city/traffic/traffic-manager.gc` | `(declare-type crimson-blue-guard crimson-guard)`, `*crimson-blue-guard-ratio*`, probabilistic substitution in both `crimson-guard-1`/`crimson-guard-0` arms of `traffic-object-spawn`, `spawn-crimson-blue-guard-debug` REPL helper | mixes the blue variant into ambient city traffic, without touching the traffic-type enum or any weighting table; gives a one-liner to force-spawn one for testing |
| `custom_assets/jak2/models/common/crimson-blue-guard-lod0.glb` (new) | copy of the build-actor `.glb`, renamed | Circuit 2 — see §4.3 |
| `goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc` | `citizen-init!`, `general-event-handler` overrides + standalone `crimson-blue-guard-attack-guards` function | passivity toward Jak + manual guard-vs-guard trigger — see §5 |
| `goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc` | `crimson-guard-method-214`/`216`/`222` overrides (gun shot, line-of-sight probe, taser lightning) | purely positional fix: `crimson-blue-guard.glb`'s joint order differs from the native skeleton, so the muzzle/beam origin (native joints 14/15 "blast"/"dirblast") is read from this variant's own joints (28/29) instead — no behavior/timing/range change |
| `goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc` | `die` state + `crimson-blue-guard-dissolve-sequence` + `enemy-method-78` override | Robust custom actor death dissolution: skips standing die animation if `knocked-fatal?` so guard stays flat on the ground, plays `"enemy-fizz"`, launches purple dissolution particles (`merc-death-spawn 73`) across joints for 60 frames with jitter, and hides mesh on frame 5. Replaces `do-effect 'death-default` to prevent the C++ `generic_merc_death` crash (`exit status 5`) on dummy `build-actor` geometry |
| `goal_src/jak2/engine/ai/traffic-h.gc` | `(define-extern *mod-city-peaceful?* symbol)` / `(define-extern *mod-city-insurrection?* symbol)` | forward declarations, same idiom as the pre-existing `*traffic-alert-level-force*` a few lines above, so `default-menu-pc.gc` can reference the flags regardless of compile order |
| `goal_src/jak2/levels/city/traffic/traffic-manager.gc` | `*mod-city-peaceful?*` / `*mod-city-insurrection?*` globals, both default `#f` | mod-wide flags for two planned features (see §9) — defined here rather than in the debug-gated menu file so gameplay code can read them unconditionally; **no code reads them yet**, flipping them currently has zero effect |
| `goal_src/jak2/pc/debug/default-menu-pc.gc` | new "Mods" debug-menu tab, two mutually-exclusive toggle pick-funcs (`dm-mod-city-peaceful-pick-func` / `dm-mod-city-insurrection-pick-func`) | UI scaffolding for §9 — reversible, additive, does not touch any existing menu entry |

All changes are additive — no native file is emptied, no existing behavior is removed, and every
new knob defaults to a value that reproduces the original behavior exactly (`native-header #f`,
`*crimson-blue-guard-ratio*` only ever *substitutes* a spawn that was going to happen anyway).

## 7. How to Test

1. `task build-release-game` (or `build-debug-game`) — only needed after a C++ change
   (`build_actor.cpp`/`Tools.cpp`); not needed for GOAL-only iteration.
2. `task extract` — required once (or after the `.glb` model changes) to bake Circuit 2, see §4.3.
   Check the log for `Adding custom model crimson-blue-guard-lod0 to common` and no
   `merc failed to find texture` for it.
3. `task repl`, then `(mi)` — must reach "Successfully built all N targets" with no
   `could not find a master slot to link` / `link-art` errors.
4. `task boot-game` (or `(r)` from the REPL), reach Haven City.
5. At the REPL, `(set! *crimson-blue-guard-ratio* 1)` to force every ambient guard spawn blue, or
   `(spawn-crimson-blue-guard-debug 0)` / `(...  1)` to force-spawn a baton/gun guard regardless of the ratio;
   confirm it's textured and its idle/walk/run/notice/hostile/knocked/get-up/die animations all
   play correctly and match a regular guard's timing and sound cues 1:1.
6. **Passivity:** with no alert active, walk up to / bump a blue guard — it should not attack.
7. **No alarm on a general alert:** trigger a real city alert some other way (shoot a red guard,
   commit a crime). A nearby blue guard should stay passive toward Jak — it must not join the
   alert against him.
8. **Personal retaliation, no alarm:** hit/shoot a blue guard directly. It should react exactly
   like a red guard would (flinch/knockback/get-up animation, then fight back at normal range),
   but the city-wide alert (top-right alarm indicator) should **not** trigger from this.
9. **Death, collision, everything else:** kill a blue guard, get it hit by a vehicle, shocked
   (yellow hit), etc. It must look and behave identically to a red guard in every respect — same
   death animation, no different collision/attack range. Any difference here is a bug (most likely
   an animation-index drift — see the native-header/reorder pitfall in tip 23).
10. **Manual guard-vs-guard trigger:** `(define g (spawn-crimson-blue-guard-debug 0))` then
    `(crimson-blue-guard-attack-guards (the-as crimson-blue-guard g))` near a red guard — it should
    go hostile and fight. This combination has no native precedent (stock guards never fight each
    other), so pay attention to whether the approach/attack range looks normal.
11. Set `*crimson-blue-guard-ratio*` back to `8` (or remove the override) and confirm blue guards
    still show up occasionally, mixed naturally with red ones.
12. Regression: boot a couple of other, untouched levels/cities and confirm no new spawn/link-art
    errors in `log/jak2.<ts>.log`.

## 8. Status

| Item | State |
|---|---|
| `build-actor :native-header #t` (C++ + GOAL macro) | ✅ done, compiled and boot-tested |
| `.glb` animation reordering | ✅ done, verified programmatically and in-game (correct animations play) |
| `crimson-blue-guard` entity (`deftype`/`defskelgroup`/`init-enemy!`) | ✅ done, compiled and boot-tested |
| DGO residency (code + art, 11 files) | ✅ done |
| Ambient traffic mixing | ✅ done, boot-tested |
| Circuit 2 (`models/common` + `task extract`) | ✅ done — guard renders fully textured |
| Passivity toward Jak + personal retaliation, no alarm | ✅ done, verified in-game |
| `crimson-blue-guard-attack-guards` manual trigger | ✅ done, verified in-game |
| Death dissolve sequence (`die` state override + `merc-death-spawn 73` + `knocked-fatal?`) | ✅ done, verified in-game: solves the C++ `generic_merc_death` exit status 5 crash via direct GOAL particle dissolution loop, plays `"enemy-fizz"`, hides mesh, and keeps knocked-down guards flat on the ground |
| City Peaceful patrol squads (2-3 members, formation navigation, adaptive speed, leader promotion) | ✅ done, verified in-game: dynamic wing offsets, smooth squad pacing, clean automatic promotion if leader dies |
| Squad mutual defense & Faction friendly-fire immunity | ✅ done, verified in-game: squad responds as a unit without city sirens; blue members & projectiles are fully immune to friendly fire |
| Squad weapon loadout diversity | ✅ done, verified in-game: 3-man squads always have 1 Taser, 1 Rifle, 1 Grenade Launcher; 2-man squads have 2 distinct weapons |
| Faithful Crimson Guard combat AI | ✅ done, verified in-game: standoff distance (~6.5m–9m), reactive laser bursts/parabolic grenades, evasive sideways rolls, emergency-only close attack (< 2.5m) followed by evasive recovery roll |
| "Mods" debug menu tab (`City Peaceful` / `City Insurrection` + `Insurrection war zone` picker) | ✅ both modes implemented; mutually exclusive; each toggle/pick flushes & respawns the city guards so the new rules apply immediately |
| City Insurrection — nickname-based district zoning (`city-level-name-at-pos` → `city-district-of-level`) | ✅ done: Slums (`ctysluma/b/c`) = blue, the selected war-zone district = conflict, everything else = red — verified level names, no hardcoded coordinates; probes only the traffic-engine's linked `level-data-array` grids (never a raw `*level*` bsp pointer — that crashed on the `ctyport→ctyinda` transition) |
| City Insurrection — **configurable war zone** (`*mod-city-conflict-district*`) | ✅ done: `Debug ▸ Mods ▸ Insurrection war zone` cycles the war zone between Industrial (default), Port, Bazaar, Farmland and Market; changing it re-zones and flushes the guards live |
| City Insurrection — strict per-zone spawning (single-faction pools, faction by district) | ✅ done: `traffic-object-spawn` picks blue in the Slums, red in Loyalist districts, 50/50 in the war zone; a district change is reconciled incrementally (`mod-city-guard-pool-reconcile`, ≤2 wrong-faction retirements per pool per frame) so the pool is always the right faction — no filtering, no wasted slots |
| City Insurrection — war zone: no civilians/vehicles + dense guard battle | ✅ done: `want-count` for citizens (0–3), metalheads (8–10) and vehicles (11–19) forced to 0 in the war zone (drained by `kill-excess-once` + natural despawn); **two** guard pools — stock `crimson-guard-1` (18/16) + the unused `crimson-guard-2` (16/14) — `inv-density-factor` 2.0 → ~30 guards, 50/50, under the stock 64 nav ceiling; all restored on zone/mode change |
| City Insurrection — Loyalist district police density | ✅ the stock `crimson-guard-1` pool is left **byte-for-byte vanilla** in Loyalist districts (base `want-count`, alert-scaled `target-count`) |
| City Insurrection — autonomous inter-faction combat (`crimson-guard-insurrection-scan`) | ✅ done: red hunts blue / blue hunts red within **~60 m** (was 40 m) from `active` **and** `search`, full weapon AI, zero effect on Jak's wanted level; `find-nearest-enemy-guard` scans both trackers (the decomp's `citizen`/`vehicle` tracker aliases are swapped — guards are in `vehicle-tracker-array`) |
| City Insurrection — alert-free zones (`increase-alert-level` choke + `set-alert-level 0`) | ✅ done: no alert can start or persist in the Slums **or** the war zone, from any source — hitting a red guard in the war zone raises nothing; only loyalist districts run the wanted system |

## 9. "Mods" Debug Menu Tab & Features

The debug menu (on by default — `*debug-segment*` defaults to 1, and `task boot-game` runs with
`-debug`) has a "Mods" tab with two toggles, **City Peaceful** and **City Insurrection**. They are
mutually exclusive (turning one on clears the other) and freely reversible.

### 9.1 City Peaceful (✅ Fully Implemented)
When toggled on in the Mods menu:
- **Ambient Patrol Squads:** blue guards spawn in tight 2-to-3 member squads walking Haven City in
  formation (wingmen offset relative to the leader's rotation quaternion). Followers dynamically
  accelerate (up to 1.5×) or slow down (0.85×) to keep rank, and automatically promote follower 1
  to squad leader if the leader dies.
- **Weapon Diversity:** every 3-man squad features exactly one Taser guard (`guard-type 0`), one
  Rifle guard (`guard-type 1`), and one Grenade Launcher guard (`guard-type 2`). Every 2-man squad
  has two distinct weapons.
- **Mutual Defense:** if any squad member is attacked by Jak or another enemy, the entire squad
  retaliates together in self-defense, without triggering the city-wide alarm or calling red guards.
- **Friendly-Fire Immunity:** projectiles and attacks originating from blue guards are filtered out
  within the faction, preventing infighting or fratricidal aggro.
- **Faithful Combat AI:** ranged guards maintain standoff engagement distance, fire bursts or
  grenades upon acquiring LOS (up to 50m), and execute evasive sideways rolls (`roll-left` /
  `roll-right`). Melee rifle-butts are strictly an emergency counter (< 2.5m) immediately followed
  by an evasive roll.

### 9.2 City Insurrection (✅ Fully Implemented)
Haven City becomes a three-front territorial civil war. Districts are classified by the **loaded
city-level name** that owns a position — `city-level-name-at-pos` → `city-district-of-level` →
`city-zone-from-level-name` in
[`traffic-manager.gc`](../../../goal_src/jak2/levels/city/traffic/traffic-manager.gc) — using
only verified level names (`level-info.gc`), never hardcoded map coordinates:

> [!WARNING]
> ### ⚠️ Work in Progress — Stability Notice
> City Insurrection is currently under **active development**. While fully playable, players and testers may encounter **occasional unexpected game crashes** (e.g. `exit status 5` / process allocation limits) due to the high density of concurrent combatants, process slot exhaustion under sustained heavy battle, or level streaming crossfades.
> Detailed health telemetry is periodically printed to the console terminal to help monitor heap memory and active process slots.

| Zone | City levels | Rule |
|---|---|---|
| **Blue — Slums (Rebel Stronghold)** | `ctysluma`, `ctyslumb`, `ctyslumc` | 100% lone blue guards, random weapons; alert-free safe haven |
| **Red — Loyalist (Baron's districts)** | every district that is *not* the Slums or the selected war zone | 100% stock red/yellow Crimson Guards, **fully vanilla** density & policing toward Jak |
| **Conflict — War Zone** | the district picked in `Debug ▸ Mods ▸ Insurrection war zone` — **Industrial (`ctyinda/b`) by default**, or Port / Bazaar / Farmland / Market / All City | **60 guards (max engine limit)**, dynamic 70% loyalists / 30% insurgents, **no civilians, no metalheads, no vehicles**; the two factions fight each other on sight; alert-free |

When toggled on in the Mods menu:
- **Configurable war zone** (`*mod-city-conflict-district*`): the `Insurrection war zone` sub-menu
  is a radio picker over Industrial (default), Port, Bazaar, Farmland, Market, and All City. Changing it
  re-zones the city and re-rolls the guards. The Slums are always the blue haven and are never a
  war-zone option.
- **Strict territorial spawning — single-faction pools, faction chosen by district**
  (`mod-city-guard-spawn-blue?` + `mod-city-insurrection-shape-guard-pools`):
  `traffic-object-spawn` picks the concrete process type per spawn from the district Jak is in —
  `crimson-blue-guard` in the Slums, the stock red `crimson-guard` in Loyalist districts, a dynamic 70/30
  ratio in the war zone. A district change is reconciled **incrementally** — `mod-city-guard-pool-reconcile`
  retires up to 2 wrong-faction guards per pool per frame while `spawn-all` refills with the new
  faction, so the street crossfades over ~1-2 s and a red guard never ends up patrolling the Slums
  (nor a blue guard a Loyalist district).
- **Maximum Guard Density (60 Active Combatants)** (`mod-city-insurrection-shape-guard-pools`):
  All three guard pools are mobilized at full slice capacity (20 each = 60 total): Pool 4 (`crimson-guard-0`),
  Pool 6 (`crimson-guard-1`), and Pool 7 (`crimson-guard-2`). With `inv-density-factor` reduced to `0.1`
  (50x denser spacing) and continuous `fast-spawn #t`, the battlefield maintains a massive, relentless
  clash of 60 simultaneous combatants.
- **Dynamic Faction Balancing (70% Loyalists / 30% Insurgents):**
  Street-level real-time balancing ensures loyalist forces (red & yellow guards) maintain tactical superiority
  over the rebel forces.
- **Arsenal Overhaul & Melee Minimization:**
  - **0% Tasers:** Taser/baton guards are completely disabled.
  - **Grenade Launchers for Red & Yellow Guards:** Red and yellow guards are equipped with high-explosive
    grenade launchers (`vehicle-grenade`) featuring parabolic ballistic trajectories alongside standard pulse rifles.
  - **Melee Minimization:** Rifle-butt melee swings are suppressed, the vanilla 10-meter shooting lockout
    is eliminated, and guards maintain tactical standoff distances in flanking arcs (~6.5m for rifle, ~9m for grenade launcher).
- **Periodic Health Telemetry Logs:**
  Console terminal prints heap memory, alive/free process slots, combatant counts, and pool states every 5 seconds:
  `[INS-METRICS] Heap: ... | Slots: ... | Combatants (act/tot): ... | P4(...) P6(...) P7(...) | Zone: conflict`
- **Crash fixed — district transitions are incremental** ([commit 1](../../../goal_src/jak2/levels/city/traffic/traffic-manager.gc)):
  an earlier version force-deactivated every civilian + vehicle + hard-killed all three guard
  pools + fast-spawned on the frame Jak crossed a border — that coincides with the outgoing city
  level's teardown and hard-crashed the game (`exit status 5`, log ending at
  `kill #<level active ctysluma>`). Now the crossover is spread over ~1-2 s at a few process ops
  per frame, so it can never race a level transition.
- **Autonomous inter-faction warfare** (`crimson-guard-insurrection-scan` in `guard.gc`): in the
  war zone every guard scans for the nearest **opposing-faction** guard within **~150 m** (the faction is derived
  from `this`, so one helper covers both red and blue). On acquisition it targets the foe directly
  and goes hostile — laser bursts, parabolic grenades — and **never touches Jak's
  wanted level**. The hook runs from both `active` and `search`, so a guard that loses a foe
  re-acquires the next nearest one or drops back to patrol instead of idling.
  `find-nearest-enemy-guard` scans **both** of the traffic engine's trackers — the decomp aliases
  `citizen-tracker-array` / `vehicle-tracker-array` onto the two `tracker-array` slots *backwards*
  (guards live in the one called `vehicle-tracker-array`).
- **Reciprocal retaliation:** a red guard hit (melee *or* projectile — `incoming attacker-handle`
  resolves a bolt/grenade back to the firing guard via the process parent chain) by a blue guard
  targets and returns fire on that blue guard directly, no city alarm, no siren. The blue guard
  side already had this.
- **Alert-free zones (Slums *and* war zone):**
  - `increase-alert-level` (`traffic-engine.gc`) is short-circuited whenever Jak is in the blue
    zone **or** the war zone — the **single choke point** for the alert rising, so it blocks the
    menu event, the direct `citizen::trigger-alert` path *and* kill-count escalation. Hitting a
    red guard in the war zone raises nothing. Only loyalist districts run the wanted system.
  - `mod-city-insurrection-update-traffic` additionally snaps `set-alert-level` to `0` on every
    frame Jak is in either zone, so any alert he *carried in* drops instantly.
  - Loyalist gunships (`guard-bike` 18, `hellcat` 19) are kept out of the Slums and the war zone
    (`want-count` 0). Hitting a blue guard still triggers only that guard's personal self-defense.
- **Live mode / config switching** (`dm-mod-city-flush-guards` in `default-menu-pc.gc`): toggling
  any Mods entry — mode toggle or war-zone pick — parks all three crimson-guard pools (4, 6, 7)
  and the guard vehicles (18, 19); they respawn within a second or two rebuilt under the
  newly-selected rules — squads for Peaceful, lone factioned guards for Insurrection, the
  stock mix for off.
- **Crash fixed (`ctyport → ctyinda` transition):** `city-level-name-at-pos` used to probe
  `sphere-in-grid?` on every loaded level's raw `(-> lev bsp city-level-info)` pointer. During a
  level transition an outgoing city level's `-vis` heap is freed while the traffic manager keeps
  running, so that probe walked freed memory → hard crash with no GOAL error. It now only probes
  the ≤2 grids the traffic engine has linked in `level-data-array` (the same set `update-traffic`
  uses) and recovers the level name by pointer identity.

---
---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## 1. Ce que c'est

Un garde crimson recoloré en bleu, ajouté comme **entité GOAL à part entière**
(`crimson-blue-guard`) plutôt que comme remplacement de texture global — le garde rouge classique
(`crimson-guard`) continue d'apparaître sans modification. La variante bleue est identique à
`crimson-guard` en tout (animations, mort, collision, arsenal, ...) sauf une chose : elle est
passive envers Jak par défaut, et ne devient personnellement hostile envers lui que s'il l'attaque
directement (sans alarme de ville dans les deux cas) — voir §5. Une fonction séparée, à déclencher
manuellement, la fait combattre un autre garde volontairement (également §5). Elle est mélangée au
trafic de gardes ambiant de Haven City.

L'asset source est `custom_assets/jak2/models/custom_levels/crimson-blue-guard.glb` (aussi copié
vers `custom_assets/jak2/models/common/crimson-blue-guard-lod0.glb`, voir §4.3) : le squelette
natif décompilé de `crimson-guard` + ses 40 animations, reskinné avec un jeu de textures recoloré
dans Blender, puis réexporté.

## 2. Le problème central : les indices de slot d'animation

Les ~4700 lignes d'IA/machine à états de `crimson-guard`
(`goal_src/jak2/levels/city/traffic/citizen/guard.gc`) référencent ses animations presque
entièrement par **indice numérique de slot** dans le tableau d'éléments de son art-group — soit
via des champs surchargeables (`anim-walk`, `anim-run`, `anim-get-up-front`...) positionnés une
fois dans `init-enemy!`, soit, dans une poignée de méthodes (`enemy-method-77`, `enemy-method-78`,
`set-behavior!`), sous forme de **littéraux bruts** codés en dur directement dans le corps de la
méthode (`(-> this draw art-group data 42)` et consorts).

L'art-group natif `crimson-guard-ag` a une disposition fixe (voir
`decompiler/config/jak2/ntsc_v1/art-group-info.min.json`, clé `crimson-guard-ag`) :

| Slot | Contenu |
|---|---|
| 0 | `crimson-guard-lod0-jg` (mesh skinné) |
| 1 | `crimson-guard-lod0-mg` |
| 2 | `crimson-guard-lod2-mg` |
| 3 | `crimson-guard-shadow-mg` |
| 4..43 | 40 animations, dans un ordre fixe (`idle`@4, `walk`@5, `run`@6, ..., `get-up-front`@33, `get-up-back`@34, ...) |

L'outil `build-actor` existant (`goalc/build_actor/jak2/build_actor.cpp`) ne reproduit **pas**
cette disposition pour un acteur custom autonome : il émet toujours un header à 2 slots (`jgeo`,
un slot vide factice) avant les animations, et ordonne les animations selon leur ordre dans le
tableau `animations` du `.glb` source — qu'un export Blender/glTF normal trie alphabétiquement.
Construire le garde bleu « tel quel » aurait placé `idle` de `crimson-blue-guard-ag` au slot 2 au
lieu de 4, `get-up-back` à un slot dérivé de l'ordre alphabétique au lieu de 34, etc. — jouant
silencieusement la *mauvaise* animation dans chaque chemin de code à indice codé en dur, cassant
l'exigence de « comportement identique » de façon subtile et difficile à remarquer (par exemple
seules les réactions d'éjection de véhicule ou de choc éco-jaune, qui utilisent des littéraux
bruts, seraient fausses).

## 3. Le correctif — deux pièces additives et optionnelles

### 3.1 `build-actor :native-header #t`

La macro `build-actor` de `goal_src/jak2/lib/project-lib.gp` a reçu un nouveau paramètre
`&key (native-header #f)`, propagé jusqu'à l'outil de compilation de données `build-actor2`
(`goalc/make/Tools.cpp::BuildActor2Tool`) puis jusqu'à
`jak2::BuildActorParams2::native_anim_header` (`goalc/build_actor/jak2/build_actor.h`). Quand il
est activé, `run_build_actor` (`goalc/build_actor/jak2/build_actor.cpp`) émet **deux slots
factices supplémentaires** après le mesh, faisant passer le header de 2 à 4 slots — reproduisant
exactement la disposition native. La valeur par défaut est `#f`, donc tous les acteurs custom
existants (`test-actor`, le jetboard, etc.) restent totalement inchangés.

```lisp
(build-actor "crimson-blue-guard" :force-run #t :native-header #t)
```

### 3.2 Réordonner le tableau d'animations du `.glb` source

Un script Python ponctuel a réordonné le tableau JSON `animations` de `crimson_blue_guard.glb`
(simple réordonnancement des éléments du tableau — aucune donnée d'accessor/bufferView/mesh
touchée) pour correspondre à l'ordre canonique des 40 noms issu de
`art-group-info.min.json` ci-dessus. Combiné au header natif à 4 slots, cela fait que le slot N de
`crimson-blue-guard-ag` contient la *même* animation que le slot N de `crimson-guard-ag`, pour
tout N. Si vous devez un jour reconstruire le `.glb` depuis un nouvel export Blender, relancez
`python scripts/modding/reorder_crimson_guard_glb_anims.py <in.glb> <out.glb>` avant `build-actor`,
sinon les indices d'animation dériveront à nouveau.

Avec ces deux pièces en place, `crimson-blue-guard` n'a besoin de surcharger que `init-enemy!`
(`goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`) pour pointer vers son propre
skeleton-group par nom — toutes les autres méthodes/états hérités de `crimson-guard` continuent de
fonctionner avec exactement les mêmes indices numériques, sans modification.

## 4. Le faire apparaître dans le jeu

- **Résidence du code :** `crimson-blue-guard.gc` compile vers `crimson-blue-guard.o`, ajouté à
  côté de `guard.o` dans `goal_src/jak2/dgos/cwi.gd` (le DGO commun toujours résident qui contient
  déjà le code de `crimson-guard`).
- **Résidence de l'art :** `crimson-blue-guard-ag.go` a été ajouté à côté de chaque entrée
  `crimson-guard-ag.go` existante (ajout uniquement, rien retiré) dans les 10 DGOs de niveau qui
  le portent : `cas.gd`, `dg1.gd`, `fdb.gd`, `fea.gd`, `fob.gd`, `fra.gd`, `lwidea.gd`,
  `lwideb.gd`, `lwidec.gd`, `pae.gd`. Cela garantit que les assets de la variante bleue sont
  chargés partout où ceux du garde classique le sont, donc elle ne peut jamais être choisie pour
  un spawn sans que son art soit résident.
- **Spawn dans le trafic ambiant :** `traffic-manager.gc::traffic-object-spawn` est l'unique
  endroit où la simulation de trafic transforme un choix `(traffic-type crimson-guard-1)` /
  `(traffic-type crimson-guard-0)` en process concret, via
  `(citizen-spawn arg0 crimson-guard arg1)`. Les deux points d'appel tirent maintenant
  `(-> arg1 id)` (le compteur de spawn de `traffic-object-spawn-params`) modulo un nouveau global,
  `*crimson-blue-guard-ratio*` (8 par défaut, soit environ 1 spawn sur 8), substituant
  `crimson-blue-guard` à `crimson-guard` sur le coup — reprenant le mécanisme préexistant
  `dark-guard-ratio` utilisé pour la variante « dark guard » quelques lignes plus haut. C'est le
  **seul** point de contact dans toute la simulation de trafic : l'enum `traffic-type`, la table
  de pondération `guard-type-info-array`, et tout le reste de la logique de qui/quand/où un slot
  de garde est choisi restent totalement intouchés — `crimson-blue-guard` n'est qu'un type concret
  alternatif pour une décision de spawn déjà existante, donc toute la comptabilité du
  traffic-engine (nav mesh, état d'alerte, comptages de population) se comporte identiquement
  quelle que soit la variante qui atterrit dans ce slot de process.
- `(declare-type crimson-blue-guard crimson-guard)` a été ajouté en haut de `traffic-manager.gc`
  pour que la référence ci-dessus compile indépendamment de l'ordre des fichiers (même idiome que
  la déclaration anticipée de `crimson-guard` lui-même dans `traffic-engine.gc`).

### 4.3 Une seconde pièce, facile à manquer : la géométrie de rendu réelle (« Circuit 2 »)

`build-actor` (Circuit 1, §3) ne produit que l'art-group squelette/animations. Les triangles +
textures réellement dessinés par le renderer PC (Circuit 2) viennent d'un système totalement
séparé : le décompilateur les cuit dans des fichiers `.fr3`, recherchés **par nom** au runtime.
Voir `docs/modding/jak2_modding_utilities/19_injecting_a_model_into_a_level.md` pour le mécanisme
complet. Le merc-ctrl produit par `build-actor` lui-même est un placeholder
(`generate_dummy_merc_ctrl` dans `build_actor.cpp` réutilise littéralement un mesh factice codé en
dur) — sans le Circuit 2, le garde apparaît, se déplace et fait du bruit normalement, mais est
**invisible**.

Le correctif : une seconde copie du même `.glb`, renommée pour correspondre au nom du merc-ctrl
placeholder (`<nom-art-group>-lod0`, ici `crimson-blue-guard-lod0.glb`), déposée dans
`custom_assets/jak2/models/common/`. `add_custom_model_to_level` du décompilateur
(`decompiler/level_extractor/extract_merc.cpp`) scanne automatiquement ce dossier à `task extract`
— aucune config nécessaire — et cuit le modèle + toutes ses textures dans `GAME.fr3` (`common` →
toujours résident, peu importe le niveau). C'est une étape ponctuelle (ou à refaire après tout
changement du `.glb`) ; elle n'est **pas** à refaire après une simple itération de code GOAL
(`(mi)`).

## 5. Comportement de faction

`crimson-blue-guard` est délibérément **100% identique à `crimson-guard` en tout, sauf une seule
chose** : il ne combat pas *pour* la faction des Crimson Guards contre Jak par défaut. Tout le
reste — collision, animations, mort, déplacement, arsenal, pondération de spawn — est exactement ce
que fait déjà `crimson-guard`, sans aucune modification. Les seules surcharges, dans
`goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`, sont :

- **Surcharge de `citizen-init!`** — force sans condition le collide-spec « ne cible pas Jak » (la
  version de crimson-guard le choisit selon le flag *partagé*, à l'échelle de la ville,
  `traffic-alert-flag target-jak`, qu'on ne peut pas utiliser pour garder passive une seule
  variante). Le garde garde son bit `enemy` de collide-as (il reste donc une cible valide pour les
  autres), il ne traite simplement jamais Jak comme cible de sa propre initiative.
- **Surcharge de `general-event-handler`** :
  - `'hit`/`'hit-flinch`/`'hit-knocked` : reproduit ligne à ligne le cas propre de crimson-guard,
    avec un seul changement — si l'attaquant est Jak spécifiquement (`(process-mask target)`), le
    garde le mémorise comme cible (`traffic-target-status handle` + focus) au lieu d'appeler
    `trigger-alert`, donc l'alarme de ville n'est jamais déclenchée. Dans les deux cas, il retombe
    ensuite sur `(method-of-type nav-enemy general-event-handler)` — exactement le même appel que
    fait crimson-guard — donc la transition flinch/coup/relevé/hostile, et tout le reste du combat,
    reste 100% natif. Tout attaquant non-Jak est identique à crimson-guard natif (déjà un no-op sur
    l'alerte de ville via le contrôle `(process-mask target)` de
    `traffic-engine::increase-alert-level`).
  - `'panic`/`'clear-path` : identique au natif, sauf que le danger attribué à Jak (tir d'arme près
    du garde, pas forcément un coup direct — voir `traffic-engine::update-danger-from-target`, qui
    stocke toujours le handle de Jak comme source) ne déclenche pas non plus l'alerte. Sans ça,
    tirer près du garde sonnerait quand même l'alarme malgré le correctif du cas `'hit`.
  - `'alert-begin` devient un no-op délibéré : la version native de crimson-guard cible qui a
    déclenché l'alerte (presque toujours Jak) et devient hostile envers lui — exactement le
    comportement « attaque Jak pendant une alerte générale » que cette variante ne doit pas avoir.
- **`crimson-blue-guard-attack-guards`** (simple `defun`, pas une méthode, jamais appelée
  automatiquement nulle part) — le seul moyen de faire combattre ce garde contre un autre
  volontairement. Cherche le `crimson-guard` (non-bleu) le plus proche dans ~40 m via l'utilitaire
  existant `find-nearest-attackable` (`engine/collide/find-nearest.gc`), exclut
  `crimson-blue-guard` lui-même via `type-type?` pour que les gardes bleus ne puissent jamais se
  cibler entre eux, puis fixe la cible et appelle `go-hostile` — même mécanisme que `'alert-begin`/
  `'hit`. À appeler au REPL une fois qu'on a un handle sur le garde (ex.
  `(define g (spawn-crimson-blue-guard-debug 0))`, puis
  `(crimson-blue-guard-attack-guards (the-as crimson-blue-guard g))`).

Rien de tout cela ne touche `crimson-guard`/`guard.gc` lui-même. **Réserve sur le déclencheur
manuel :** il réutilise tel quel la machine à états de combat de crimson-guard, générique sur
*quelle* est la cible actuelle (elle lit `(-> this focus handle)`/`traffic-target-status handle`,
pas un contrôle codé en dur sur `*target*`) — mais le `crimson-guard` natif n'a jamais l'occasion de
pointer cette machinerie vers un autre garde, seulement vers Jak, donc cette combinaison précise
(garde contre garde) n'a aucun précédent natif pour la vérifier. Le fait qu'un garde rouge touché en
retour riposte ou non dépend entièrement du code natif inchangé de `crimson-guard` — rien ici
n'ajoute de logique de riposte garde-contre-garde au type natif.

## 6. Les Changements Moteur de Cette Branche

Voir le tableau en anglais ci-dessus (section 6) — identique, fichier par fichier.

## 7. Comment Tester

1. `task build-release-game` (ou `build-debug-game`) — nécessaire seulement après un changement
   C++ (`build_actor.cpp`/`Tools.cpp`) ; pas nécessaire pour de l'itération GOAL seule.
2. `task extract` — requis une fois (ou après un changement du `.glb`) pour cuire le Circuit 2,
   voir §4.3. Vérifier dans le log la ligne `Adding custom model crimson-blue-guard-lod0 to common`
   et l'absence d'erreur `merc failed to find texture` pour lui.
3. `task repl`, puis `(mi)` — doit atteindre « Successfully built all N targets » sans erreur
   `could not find a master slot to link` / `link-art`.
4. `task boot-game` (ou `(r)` depuis le REPL), rejoindre Haven City.
5. Au REPL, `(set! *crimson-blue-guard-ratio* 1)` pour forcer chaque spawn de garde ambiant en
   bleu, ou `(spawn-crimson-blue-guard-debug 0)` / `(... 1)` pour en faire apparaître un (matraque
   / fusil) devant vous sans dépendre du ratio ; vérifier qu'il est bien texturé et que ses animations
   idle/walk/run/notice/hostile/knocked/get-up/die jouent toutes correctement et correspondent 1:1
   au timing et aux sons d'un garde normal.
6. **Passivité :** sans alerte active, approchez-vous d'un garde bleu / bousculez-le — il ne doit
   pas attaquer.
7. **Pas d'alarme sur une alerte générale :** déclenchez une vraie alerte de ville autrement (tirez
   sur un garde rouge, commettez un délit). Un garde bleu à proximité doit rester passif envers
   Jak — il ne doit pas rejoindre l'alerte contre lui.
8. **Riposte personnelle, pas d'alarme :** frappez/tirez directement sur un garde bleu. Il doit
   réagir exactement comme le ferait un garde rouge (animation de flinch/coup/relevé, puis riposte
   à portée normale), mais l'alerte de ville (indicateur en haut à droite) ne doit **pas** se
   déclencher pour autant.
9. **Mort, collision, tout le reste :** tuez un garde bleu, faites-le renverser par un véhicule,
   choquer (yellow hit), etc. Il doit se comporter et avoir l'air identique à un garde rouge en
   tout point — même animation de mort, pas de différence de collision/portée d'attaque. Toute
   différence ici est un bug (le plus probable : une dérive d'indice d'animation — voir le piège
    native-header/réordonnancement du tip 23).
10. **Déclencheur manuel garde-contre-garde :** `(define g (spawn-crimson-blue-guard-debug 0))`
    puis `(crimson-blue-guard-attack-guards (the-as crimson-blue-guard g))` près d'un garde rouge —
    il doit devenir hostile et se battre. Cette combinaison n'a aucun précédent natif (les gardes
    natifs ne se combattent jamais entre eux), donc soyez attentif à l'approche/la portée d'attaque.
11. Remettre `*crimson-blue-guard-ratio*` à `8` (ou retirer la surcharge) et vérifier que des
    gardes bleus continuent d'apparaître occasionnellement, mélangés naturellement aux rouges.
12. Non-régression : booter d'autres niveaux/villes intacts et vérifier qu'aucune nouvelle erreur
    de spawn/link-art n'apparaît dans `log/jak2.<ts>.log`.

## 8. Statut

| Élément | État |
|---|---|
| `build-actor :native-header #t` (C++ + macro GOAL) | ✅ fait, compilé et testé en jeu |
| Réordonnancement des animations du `.glb` | ✅ fait, vérifié programmatiquement et en jeu (les bonnes animations jouent) |
| Entité `crimson-blue-guard` (`deftype`/`defskelgroup`/`init-enemy!`) | ✅ fait, compilé et testé en jeu |
| Résidence DGO (code + art, 11 fichiers) | ✅ fait |
| Mélange dans le trafic ambiant | ✅ fait, testé en jeu |
| Circuit 2 (`models/common` + `task extract`) | ✅ fait — le garde s'affiche entièrement texturé |
| Passivité envers Jak + riposte personnelle sans alarme | ✅ fait, vérifié en jeu |
| Déclencheur manuel `crimson-blue-guard-attack-guards` | ✅ fait, vérifié en jeu |
| Séquence de dissolution à la mort (surcharge état `die` + `merc-death-spawn 73` + `knocked-fatal?`) | ✅ fait, vérifié en jeu : élimine le crash C++ `generic_merc_death` (exit status 5) via une boucle GOAL de particules violettes, joue `"enemy-fizz"`, masque le mesh et maintient le garde au sol en cas de mort par knockdown |
| Escouades de patrouille City Peaceful (2-3 membres, patrouille en formation, vitesse adaptative, promotion de chef) | ✅ fait, vérifié en jeu : offsets dynamiques en éventail, allure d'escouade fluide et promotion automatique du chef en cas de mort |
| Défense mutuelle d'escouade & immunité aux tirs alliés | ✅ fait, vérifié en jeu : l'escouade riposte comme un seul homme sans alarme générale ; membres et tirs bleus immunisés aux tirs fratricides |
| Diversité de l'arsenal par escouade | ✅ fait, vérifié en jeu : les escouades de 3 possèdent toujours 1 Taser, 1 Fusil, 1 Lance-Grenades ; celles de 2 ont 2 armes distinctes |
| IA de combat fidèle aux Crimson Guards | ✅ fait, vérifié en jeu : distance tactique (~6,5m–9m), tirs réactifs de rafales/grenades dès ldv acquise (jusqu'à 50m), roulades d'esquive latérales, coup de crosse de secours (< 2,5m) suivi d'une roulade de dégagement |
| Onglet menu debug « Mods » (bascules `City Peaceful` / `City Insurrection` + sélecteur `Insurrection war zone`) | ✅ les deux modes implémentés ; mutuellement exclusifs ; chaque bascule/choix vide et fait réapparaître les gardes pour appliquer les règles immédiatement |
| City Insurrection — zonage par nom de niveau (`city-level-name-at-pos` → `city-district-of-level`) | ✅ fait : Slums (`ctysluma/b/c`) = bleu, le quartier de guerre sélectionné = conflit, tout le reste = rouge — noms de niveaux vérifiés, aucune coordonnée codée en dur ; ne sonde que les grilles `level-data-array` liées du moteur de trafic (jamais un pointeur bsp `*level*` brut — ça crashait à la transition `ctyport→ctyinda`) |
| City Insurrection — **zone de guerre configurable** (`*mod-city-conflict-district*`) | ✅ fait : `Debug ▸ Mods ▸ Insurrection war zone` fait tourner la zone de guerre entre Industriel (défaut), Port, Bazar, Fermes et Marché ; le changement re-zone et re-tire les gardes en direct |
| City Insurrection — spawns stricts par zone (pools mono-faction, faction par quartier) | ✅ fait : `traffic-object-spawn` choisit bleu dans les Slums, rouge chez les loyalistes, 50/50 dans la zone de guerre ; un changement de quartier est réconcilié incrémentalement (`mod-city-guard-pool-reconcile`, ≤2 retraits de mauvaise faction par pool par frame) — pool toujours de la bonne faction, aucun filtrage, aucun slot gaspillé |
| City Insurrection — zone de guerre : aucun civil/véhicule + bataille de gardes dense | ✅ fait : `want-count` des civils (0–3), tête-de-métal (8–10) et véhicules (11–19) forcé à 0 (drainé par `kill-excess-once` + despawn naturel) ; **deux** pools de gardes — `crimson-guard-1` d'origine (18/16) + `crimson-guard-2` inutilisé (16/14) — `inv-density-factor` 2.0 → ~30 gardes, 50/50, sous le plafond nav d'origine de 64 ; tout restauré au changement de zone/mode |
| City Insurrection — densité de police des quartiers loyalistes | ✅ le pool `crimson-guard-1` d'origine est laissé **strictement vanilla** dans les quartiers loyalistes (`want-count` de base, `target-count` échelonné par l'alerte) |
| City Insurrection — combat inter-factions autonome (`crimson-guard-insurrection-scan`) | ✅ fait : rouge chasse bleu / bleu chasse rouge dans **~60 m** (au lieu de 40 m) depuis `active` **et** `search`, IA d'armes complète, aucun effet sur le niveau d'alerte de Jak ; `find-nearest-enemy-guard` scanne les deux trackers (les alias `citizen`/`vehicle` du décomp sont inversés — les gardes sont dans `vehicle-tracker-array`) |
| City Insurrection — zones sans alerte (verrou `increase-alert-level` + `set-alert-level 0`) | ✅ fait : aucune alerte ne peut démarrer ni persister dans les Slums **ou** la zone de guerre, quelle qu'en soit la source — frapper un garde rouge dans la zone de guerre ne déclenche rien ; seuls les quartiers loyalistes appliquent le système de recherche |

## 9. Onglet Menu Debug « Mods » & Fonctionnalités

Le menu debug (actif par défaut — `*debug-segment*` vaut 1 par défaut, et `task boot-game`
tourne avec `-debug`) a un onglet « Mods » avec deux bascules, **City Peaceful** et
**City Insurrection**. Elles sont mutuellement exclusives (activer l'une désactive l'autre) et
réversibles à tout moment.

### 9.1 City Peaceful (✅ Entièrement Implémenté)
Lorsque cette option est activée dans le menu Mods :
- **Escouades de patrouille ambiantes :** les gardes bleus apparaissent en escouades soudées de 2 à 3
  membres arpentant Haven City en formation (ailiers décalés par rapport au quaternion de rotation du chef).
  Les ailiers accélèrent dynamiquement (jusqu'à 1,5×) ou ralentissent (0,85×) pour maintenir leur rang,
  et promeuvent automatiquement le premier ailier comme chef si le leader est éliminé.
- **Diversité de l'arsenal :** chaque escouade de 3 comprend exactement un garde au Taser (`guard-type 0`),
  un garde au Fusil (`guard-type 1`) et un garde au Lance-Grenades (`guard-type 2`). Chaque escouade de 2
  possède deux armes distinctes.
- **Défense mutuelle :** si un membre de l'escouade est attaqué par Jak ou un autre ennemi, toute l'escouade
  riposte solidairement en état d'autodéfense, sans déclencher la sirène de la ville ni alerter les gardes rouges.
- **Immunité aux tirs alliés :** les attaques et projectiles émis par les gardes bleus sont filtrés au sein de
  la faction, éliminant tout tir fratricide ou dispute interne.
- **IA de combat fidèle :** les gardes armés à distance maintiennent une distance d'engagement tactique, tirent
  des rafales ou grenades dès qu'ils ont une ligne de vue dégagée (jusqu'à 50m), et effectuent des roulades d'esquive
  latérales (`roll-left` / `roll-right`). Les coups de crosse au corps à corps ne surviennent qu'en situation
  d'urgence absolue (< 2,5m) et sont immédiatement suivis d'une roulade de dégagement pour reprendre une posture de tir.

### 9.2 City Insurrection (✅ Entièrement Implémenté)
Haven City devient une guerre civile territoriale à trois fronts. Les quartiers sont classés par
le **nom du niveau de ville chargé** qui contient une position — `city-level-name-at-pos` →
`city-district-of-level` → `city-zone-from-level-name` dans
[`traffic-manager.gc`](../../../goal_src/jak2/levels/city/traffic/traffic-manager.gc) — en
utilisant uniquement des noms de niveaux vérifiés (`level-info.gc`), jamais de coordonnées codées
en dur :

> [!WARNING]
> ### ⚠️ En Cours de Développement — Avis de Stabilité
> City Insurrection est actuellement en **cours de développement actif**. Bien que pleinement fonctionnel, les joueurs et testeurs peuvent faire face à des **crashs inopinés** (ex. `exit status 5` / saturation de processus) en raison de la très forte densité d'entités, de la fatigue de la mémoire de tas (heap) lors de combats intenses prolongés ou des transitions rapides de quartiers.
> Des métriques de santé sont affichées régulièrement dans les logs du terminal pour surveiller l'état de la mémoire et des slots disponibles.

| Zone | Niveaux de ville | Règle |
|---|---|---|
| **Bleu — Slums (Bastion Rebelle)** | `ctysluma`, `ctyslumb`, `ctyslumc` | 100% de gardes bleus solitaires, armes aléatoires ; zone refuge anti-alerte |
| **Rouge — Loyaliste (quartiers du Baron)** | tout quartier qui n'est *ni* les Slums *ni* la zone de guerre sélectionnée | 100% de Crimson Guards rouges/jaunes classiques, densité & police envers Jak **100% vanilla** |
| **Conflit — Zone de Guerre** | le quartier choisi dans `Debug ▸ Mods ▸ Insurrection war zone` — **Industriel (`ctyinda/b`) par défaut**, ou Port / Bazar / Fermes / Marché / All City | **60 gardes (plafond max du moteur)**, ratio dynamique 70% loyalistes / 30% insurgés, **aucun civil, aucune tête-de-métal, aucun véhicule** ; les deux factions se combattent à vue ; sans alerte |

Lorsque cette option est activée dans le menu Mods :
- **Zone de guerre configurable** (`*mod-city-conflict-district*`) : le sous-menu
  `Insurrection war zone` est un sélecteur radio entre Industriel (défaut), Port, Bazar, Fermes, Marché et All City.
  Le changement re-zone la ville et re-tire les gardes. Les Slums sont toujours le refuge bleu et ne sont jamais une option de zone de guerre.
- **Génération territoriale stricte — pools mono-faction, faction choisie par quartier**
  (`mod-city-guard-spawn-blue?` + `mod-city-insurrection-shape-guard-pools`) :
  `traffic-object-spawn` choisit le type de process concret à chaque spawn selon le quartier de
  Jak — `crimson-blue-guard` dans les Slums, `crimson-guard` rouge d'origine chez les loyalistes,
  et un ratio dynamique 70% loyalistes / 30% insurgés dans la zone de guerre. Un changement de quartier est réconcilié
  **incrémentalement** — `mod-city-guard-pool-reconcile` retire jusqu'à 2 gardes de la mauvaise
  faction par pool par frame pendant que `spawn-all` remplit avec la nouvelle, donc la rue fait un
  fondu sur ~1-2 s et jamais de garde rouge dans les Slums (ni de garde bleu chez les loyalistes).
- **Densité Maximale des Gardes (60 Combattants Actifs)** (`mod-city-insurrection-shape-guard-pools`) :
  Les trois pools de gardes sont mobilisés à pleine capacité (20 chacun = 60 au total) : Pool 4 (`crimson-guard-0`),
  Pool 6 (`crimson-guard-1`) et Pool 7 (`crimson-guard-2`). Avec un espacement ultra-serré (`inv-density-factor 0.1`)
  et `fast-spawn #t` maintenu en continu, la zone de guerre offre un affrontement massif et ininterrompu de 60 gardes simultanés.
- **Équilibrage Dynamique (70% Loyalistes / 30% Insurgés) :**
  Régulation en direct au niveau de la rue garantissant la supériorité numérique des forces loyalistes (gardes rouges et jaunes) sur les rebelles bleus.
- **Arsenal Rénové & Minimisation du Corps à Corps :**
  - **0% de Tasers :** Les armes de corps à corps (bâtons/tasers) sont totalement supprimées en mode Insurrection.
  - **Lance-Grenades pour les Gardes Rouges et Jaunes :** Tir de projectiles explosifs (`vehicle-grenade`) en cloche balistique parabolique et tirs au fusil d'assaut.
  - **Minimisation des Tentatives de Mêlée :** Suppression des coups de crosse intempestifs, levée de l'interdiction de tir sous 10 mètres (tirs autorisés à bout portant), et maintien d'une distance tactique en arc de cercle (~6,5 m au fusil, ~9 m au lance-grenades).
- **Télémétrie en Direct (Logs Terminal) :**
  La console affiche périodiquement toutes les 5 secondes la mémoire heap, les slots de process libres/alloués, le décompte des combattants et l'état des pools :
  `[INS-METRICS] Heap: ... | Slots: ... | Combatants (act/tot): ... | P4(...) P6(...) P7(...) | Zone: conflict`
- **Crash corrigé — les transitions de quartier sont incrémentales** : une version antérieure
  force-désactivait tous les civils + véhicules + tuait les trois pools de gardes + fast-spawn sur
  la frame où Jak franchissait une frontière — ça coïncide avec le démontage du niveau sortant et
  crashait le jeu (`exit status 5`, log qui s'arrête à `kill #<level active ctysluma>`). Le
  renouvellement est maintenant étalé sur ~1-2 s à quelques opérations process par frame, donc ça
  ne peut plus entrer en course avec une transition de niveau.
- **Guerre autonome inter-factions** (`crimson-guard-insurrection-scan` dans `guard.gc`) : dans la
  zone de guerre, chaque garde scanne le garde de la **faction opposée** le plus proche dans
  **~150 m** (la faction est déduite de `this`, donc un seul helper couvre rouges et bleus). À l'acquisition
  il cible directement l'ennemi et devient hostile — rafales laser, tirs au lance-grenades — et **ne touche jamais au niveau de
  recherche de Jak**. Le hook tourne depuis `active` ET `search`.
  `find-nearest-enemy-guard` scanne **les deux** trackers du moteur de trafic — le décomp alie
  `citizen-tracker-array` / `vehicle-tracker-array` sur les deux slots de `tracker-array` *à
  l'envers* (les gardes sont dans celui nommé `vehicle-tracker-array`).
- **Riposte réciproque :** un garde rouge touché (corps à corps *ou* projectile —
  `incoming attacker-handle` remonte d'un tir/grenade jusqu'au garde tireur via la chaîne parente
  du process) par un garde bleu cible et riposte directement contre ce garde bleu, sans alarme de
  ville, sans sirène. Le côté garde bleu l'avait déjà.
- **Zones sans alerte (Slums *et* zone de guerre) :**
  - `increase-alert-level` (`traffic-engine.gc`) est court-circuité dès que Jak est dans la zone
    bleue **ou** la zone de guerre — le **point de passage unique** de la montée d'alerte, donc il
    bloque l'événement du menu, l'appel direct `citizen::trigger-alert` *et* l'escalade par nombre
    de morts. Frapper un garde rouge dans la zone de guerre ne déclenche rien. Seuls les quartiers
    loyalistes appliquent le système de recherche.
  - `mod-city-insurrection-update-traffic` force en plus `set-alert-level` à `0` à chaque frame où
    Jak est dans l'une des deux zones, donc toute alerte qu'il *amène avec lui* retombe
    instantanément.
  - Les vaisseaux loyalistes (`guard-bike` 18, `hellcat` 19) sont tenus hors des Slums et de la
    zone de guerre (`want-count` 0). Frapper un garde bleu ne déclenche que l'autodéfense de ce garde.
- **Bascule à chaud du mode / config** (`dm-mod-city-flush-guards` dans `default-menu-pc.gc`) :
  basculer une entrée Mods — bascule de mode ou choix de zone de guerre — parque les trois pools de
  crimson-guards (4, 6, 7) et les vaisseaux de gardes (18, 19) ; ils réapparaissent en une seconde
  ou deux selon les nouvelles règles — escouades pour Peaceful, gardes solitaires à faction pour
  Insurrection, mélange classique pour off.
- **Crash corrigé (transition `ctyport → ctyinda`) :** `city-level-name-at-pos` sondait
  `sphere-in-grid?` sur le pointeur `(-> lev bsp city-level-info)` brut de chaque niveau chargé.
  Pendant une transition de niveau, le tas `-vis` d'un niveau de ville sortant est libéré alors que
  le traffic-manager continue de tourner — cette sonde parcourait alors de la mémoire libérée →
  crash brutal sans erreur GOAL. Elle ne sonde désormais que les ≤2 grilles que le moteur de
  trafic a liées dans `level-data-array` (le même ensemble qu'utilise `update-traffic`) et retrouve
  le nom du niveau par identité de pointeur.

---
*(AI-assisted)*

