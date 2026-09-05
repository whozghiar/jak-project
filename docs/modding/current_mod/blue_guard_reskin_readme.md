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
| Passivity toward Jak + personal retaliation, no alarm | ✅ written, pending the user's in-game pass through the §7 checklist above |
| `crimson-blue-guard-attack-guards` manual trigger | ✅ written, untested combination (no native precedent) — needs in-game verification |
| Muzzle/taser joint fix (methods 214/216/222) | ⚠️ code confirmed correct (joint indices 28/29 verified against the actual `.glb` and `build_actor.cpp`'s joint-numbering logic) — but root-caused the remaining visual bug to the `.glb`'s **rigging**, not the code: joints 28/29 ("blast"/"dirblast") have a `(0,0,0)` local translation from their "gun" parent, i.e. they were never actually moved out to the barrel tip in Blender. Needs a re-export with those bones repositioned, not a code change |
| Death dissolve sequence (`die` state override + `merc-death-spawn 73` + `knocked-fatal?`) | ✅ done, verified in-game: solves the C++ `generic_merc_death` exit status 5 crash via direct GOAL particle dissolution loop, plays `"enemy-fizz"`, hides mesh, and keeps knocked-down guards flat on the ground |
| Guard-vs-guard combat noise raising the city alert against Jak | ⚠️ known limitation, not a bug in this file: `traffic-engine::update-danger-from-target` always attributes nearby combat danger to Jak's own handle regardless of who's actually fighting — a vanilla assumption (only Jak causes danger) that a guard-vs-guard fight breaks if Jak is standing nearby. No surgical fix identified yet (would require touching shared `traffic-engine.gc` danger code used by every citizen in the city) |
| Gun burst-fire animation "jump" between shots | ❓ reported, root cause not isolated yet — needs testing on a stock, unmodified `crimson-guard` to check whether this is pre-existing native behavior or specific to this variant |

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
| Passivité envers Jak + riposte personnelle sans alarme | ✅ écrite, en attente du passage de l'utilisateur sur la checklist §7 |
| Déclencheur manuel `crimson-blue-guard-attack-guards` | ✅ écrit, combinaison non testée (aucun précédent natif) — vérification en jeu nécessaire |
| Correctif de joint pour l'embout de tir/tazer (méthodes 214/216/222) | ⚠️ code confirmé correct (indices de joints 28/29 vérifiés directement dans le `.glb` et dans la logique de numérotation de `build_actor.cpp`) — mais cause racine du bug visuel restant identifiée dans le **rigging** du `.glb`, pas dans le code : les joints 28/29 ("blast"/"dirblast") ont une translation locale de `(0,0,0)` par rapport à leur parent "gun", c'est-à-dire qu'ils n'ont jamais été réellement déplacés jusqu'au bout du canon dans Blender. Nécessite une réexportation avec ces bones repositionnés, pas un changement de code |
| Séquence de dissolution à la mort (surcharge état `die` + `merc-death-spawn 73` + `knocked-fatal?`) | ✅ fait, vérifié en jeu : élimine le crash C++ `generic_merc_death` (exit status 5) via une boucle GOAL de particules violettes, joue `"enemy-fizz"`, masque le mesh et maintient le garde au sol en cas de mort par knockdown |
| Le bruit de combat garde-contre-garde déclenche l'alerte de ville contre Jak | ⚠️ limitation connue, pas un bug de ce fichier : `traffic-engine::update-danger-from-target` attribue toujours le danger de combat à proximité à Jak lui-même, peu importe qui se bat réellement — une hypothèse native (seul Jak cause du danger) que ce combat garde-contre-garde met en défaut si Jak est à proximité. Aucun correctif chirurgical identifié pour l'instant (nécessiterait de toucher le code de danger partagé de `traffic-engine.gc`, utilisé par tous les citoyens de la ville) |
| « Saut » d'animation entre les tirs en rafale | ❓ signalé, cause racine non isolée pour l'instant — à tester sur un `crimson-guard` rouge natif non modifié pour vérifier si c'est un comportement natif préexistant ou spécifique à cette variante |

---
*(AI-assisted)*
