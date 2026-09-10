# Krimzon Guard Paddy Wagon in City Traffic — Mod Readme / Fourgon Cellulaire dans le Trafic — Readme de Mod

> - **Branch / Branche :** `jak2/features/paddywagon/traffic`
> - **Game / Jeu :** Jak II (OpenGOAL)
> - **Status / Statut :** Compiles clean (`CWI.DGO`, `LWIDE{A,B,C}.DGO`, `GAME.CGO`, full `build-game`); awaiting in-game verification after `task extract` / Compile proprement ; validation en jeu à faire après `task extract`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

## 🇬🇧 English Version

### 1. Overview & Objective

`paddywagon-v` is a **real ground-traffic vehicle**: a `vehicle-guard` subtype
(sibling of `hellcat` / `guard-bike` / `cara`) that spawns in Haven City's
ambient car lanes, follows the city nav-branches, shows a **red dot on the
minimap**, is **driven by a Crimson Guard**, carries a **random civilian
prisoner standing in its rear cage**, can be **boarded and driven by the
player**, and can be **destroyed** like any guard vehicle.

**Stealing it is a crime** — and this comes entirely from stock code, not from
mod code: the driver is a `crimson-guard-rider`, whose `vehicle-rider` `flags`
bit 3 makes the `'knocked-off` branch of `vehicle-rider-event-handler` do
`(send-event *traffic-manager* 'increase-alert-level 2)` and respawn a
`crimson-guard-1` on the street. Identical to hijacking a hellcat.

The wagon is **unarmed**. The `paddy-wagon` skeleton has only the joints
"steering", "hatch", "main", "prejoint", "align" — there is no gun joint — so
`turret info` is left at 0 and `turret-control-method-11`'s
`(when (nonzero? (-> this info)))` guard makes the inherited guard AI pursue
without ever firing.

This branch is *inspired by* `jak2/features/transport-ag/traffic` (the drivable
air gunship) and reuses its two structural techniques — the spare traffic slot
20 and the `extra_art_groups_by_dgo` merc `.fr3` injection — but shares no code
with it.

### 1b. Runtime toggle (mandatory procedure)

Per CLAUDE.md's golden rules the mod ships **OFF** and is switched from
`Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable`.

With the flag `#f` the traffic want-count for slot 20 is 0, so the traffic
engine never constructs a `paddywagon-v`; no code in `paddywagon-v.gc` runs and
no `paddywagon-prisoner` is ever spawned. The rest of the wiring is **inert
rather than gated**, because none of it is reachable without a slot-20 object:
the renamed enum entries, the extra `case` arms in `traffic-object-spawn` /
`type-from-vehicle-type`, and `guard.gc`'s object-type-20 knock-off animation
entry. The want-count is read by `traffic-manager::init-params` on city load, so
**the toggle applies on the next city (re)load**, not instantly.

The retail `paddywagon` type in `meet-brutter.gc` is **not touched at all**, so
the *Escort Brutter* mission is bit-for-bit stock whether the mod is on or off.

### 2. Why a new type instead of reusing retail `paddywagon`

The retail type cannot be used in free roam, for three independent reasons:

| Retail `paddywagon` does… | …and why that blocks traffic use |
|---|---|
| ships in `LMEETBRT.DGO` | a borrowed mission level — the type isn't even loaded in free roam |
| `init-skel-and-rigid-body` sets `(-> pp level)` to `'lmeetbrt` | art would resolve from a level that isn't resident; the van would art-error or vanish |
| sets `rigid-body-object-flag no-hijack` | `vehicle-util.gc`'s boarding probe tests this flag before it will even show the "press triangle" prompt — the mission van is deliberately un-stealable |
| forces `choose-next-branch-no-exit-level` | the mission van is pinned to one level's nav graph |
| `object-type` `#x13` | it impersonates the hellcat's traffic slot |
| overrides `vehicle-method-134` / `-108` / `active` / `hostile` / `die` | the meet-brutter chase script, not city traffic behaviour |

So `paddywagon-v` is a plain traffic `vehicle-guard` that reuses only the retail
**hull, physics constants and collision shape** — verbatim.

### 3. What `vehicle-guard` gives us for free

| Requirement | Inherited from | Mechanism |
|---|---|---|
| Crimson Guard driver | `vehicle-guard::vehicle-method-137` | spawns a `crimson-guard-rider` into seat 0. Traffic sets `trsflags-01` + `behavior 1` on every pooled vehicle → a hidden rider, revealed on `'traffic-on`. |
| Red dot on the minimap | `vehicle-guard::vehicle-method-128` | `add-icon! *minimap* … 14` — the red guard marker. |
| Follows the city lanes | `vehicle-guard-choose-branch`, installed by `vehicle-guard::alloc-and-init-rigid-body-control` | ordinary nav-branch following |
| Hostile pursuit during alerts | `vehicle-guard` `hostile` / `stop-and-shoot` states | **retail already** gives slot 20 `trtflags-0` in `traffic-engine::restore-default-settings` (line ~2918), so it receives `'alert-begin` / `'alert-end` and never parks |
| Player boards & drives | `vehicle::check-player-get-on` | we simply do **not** set `no-hijack` |
| Theft raises the alert | `vehicle-rider-event-handler` `'knocked-off` + `crimson-guard-rider`'s `flags` bit 3 | alert level 2 + a `crimson-guard-1` spawned on the spot |
| Pooling (hide/show/re-seat) | `vehicle-method-127` / `-128` broadcast `'traffic-off` / `'traffic-on` to **every child** | both riders are children, so both follow the pool automatically |
| Rider positioning | `vehicle-method-119` | places each `rider-array` entry at its seat and applies the seat's `angle` |

### 4. The prisoner

`paddywagon-prisoner` is a `vehicle-rider` — the same lightweight,
seat-parented, nav-mesh-free actor retail uses for car passengers
(`citizen-norm-rider`) and guard pilots (`crimson-guard-rider`).

**The seat was already there.** Retail `*paddywagon-constants*` declares
`seat-count 2`:

| seat | `position` (x, y, z) | `angle` | `flags` | role |
|---|---|---|---|---|
| 0 | 0, 9420.8, 2457.6 | 0 | 1 | driver / player seat |
| 1 | 0, 819.2, **-13107.2** | `#x8000` = 180° | 4 | **the rear cage**, facing backwards |

Seat 1 is exactly where the meet-brutter mission drops the captured lurker
(`(get-best-seat-for-vehicle … 4 0)` → `put-rider-in-seat`). This mod puts a
civilian there instead. Because the seat's `flags` is 4 and the player seat's is
1, `target-pilot`'s `(get-best-seat-for-vehicle … 1 1)` can never put Jak in the
cage.

**Body-type roll and the arms-crossed pose.** Unlike `citizen-norm-rider` —
which uses the stripped-down `citizen-norm-rider-ag` art group whose only poses
are idle / bike-stance / car-stance — the prisoner uses the **full** civilian
art groups, because those are the only ones carrying the standing arms-crossed
pose:

| variant | skeleton group | pose | art elt |
|---|---|---|---|
| `norm` | `skel-citizen-norm` | `citizen-norm-arms-crossed-ja` | 8 |
| `fat` | `skel-citizen-fat` | `citizen-fat-arms-crossed-ja` | 8 |
| `chick` | `skel-citizen-chick` | `citizen-chick-idle-ja` | 10 |

> [!IMPORTANT]
> **`citizen-chick` genuinely has no arms-crossed animation in retail.** Its only
> standing poses in `engine/data/art-elts.gc` are `idle` (10), `shuffle` (26)
> and `riding-stance` (27). The female prisoner therefore stands at ease. To
> change that, edit `*paddywagon-prisoner-chick-anim*` in `paddywagon-v.gc`
> (27 = riding-stance is the other plausible choice).

**Zone-dependent variety.** `skeleton-group->draw-control` resolves a model
through the **process's own level** (`(-> (-> proc level) art-group)`), and
traffic riders are re-homed onto the lwide level by `(lwide-entity-hack)`.
Retail only ships:

| level | `citizen-norm-ag` | `citizen-fat-ag` | `citizen-chick-ag` |
|---|---|---|---|
| LWIDEA | ✅ | ✅ | ✅ |
| LWIDEB | ✅ | ❌ | ❌ |
| LWIDEC | ✅ | ❌ | ✅ |

So `paddywagon-prisoner-pick-variant` **checks residency first** (via
`paddywagon-prisoner-art-group-loaded?`, which reads
`(-> lvl art-group string-array)` directly rather than going through
`art-group-load-check`, whose debug-build disk load would make debug and release
behave differently) and rolls only among what is actually available, falling
back to `norm`, which ships everywhere. Result: all three body types in the
LWIDEA zone, norm+chick in LWIDEC, norm only in LWIDEB — which mirrors what
retail pedestrians look like in those zones anyway.

**The prisoner stays put when Jak steals the wagon.** `target-pilot` walks
*every* seat on boarding and sends `'knocked-off` to whoever is in it. That is
correct for the guard driver; for a prisoner it is not, so
`paddywagon-prisoner-event-handler` intercepts `'knocked-off` and returns `#f`.
That matters twice over: `target-pilot` only frees the seat when `send-event`
comes back truthy, so refusing the event also keeps the prisoner registered in
`rider-array` and therefore still positioned every frame by
`vehicle-method-119`.

**No lean.** The base `vehicle-rider-method-34` pins the channel to
`num-func-identity` and drives `frame-num` off a sine blended with the vehicle's
steering — the lean a driver does into a turn. The override reduces it to a bare
`(ja-post)`, and the `active` state's `:enter` installs a plain `:num! (loop!)`,
so the prisoner just holds his pose.

**Wardrobe.** `vehicle-rider-method-33` re-rolls the `setup-masks` submesh
groups transcribed from each civilian's own `citizen-init!`
(`citizen-norm.gc` / `citizen-fat.gc` / `citizen-chick.gc`), using
`rand-vu-int-count` in place of the `citizen`-only `rnd-int-count` method. It
runs on first spawn **and** on every `'traffic-on`, so each traffic life gets a
freshly dressed prisoner.

### 5. Traffic-type wiring

- `engine/ai/traffic-h.gc` — renames the spare `(traffic-type-20 20)` →
  `(paddywagon-v 20)`. **Slot 20 is the last usable slot**: every engine loop is
  `(dotimes … 21)` and `traffic-engine`'s `object-type-info-array` is 21 inline
  entries with `inactive-object-array` sized 420 = 21 × 20, so slot 21 cannot be
  used without resizing those structures (and the hard `:offset 7024` on
  `vehicle-tracker-array`). Retail already wired slot 20 as a `ctywide`-level,
  vehicle-tracker, `trtflags-0` guard slot — it just had want-count 0 and no
  spawn handler.
- `levels/city/traffic/vehicle/vehicle-h.gc`, `engine/entity/entity-h.gc`,
  `decompiler/config/jak2/all-types.gc` — add `(vehicle-type paddywagon-v 11)`.
- `levels/city/traffic/traffic-manager.gc` — `define-perm
  *mod-paddywagon-traffic-enable*`, the `traffic-object-spawn` and
  `type-from-vehicle-type` `case` arms, and
  `want-count[20] = (if *mod-paddywagon-traffic-enable* 2 0)`.
- `levels/city/traffic/citizen/guard.gc` — object-type 20 added to the **car**
  knock-off animation group `(14 15 16 19)`, so a guard thrown out of the van
  uses the car animation rather than the bike one.
- `levels/city/{ctywide-tasks, protect/protect, slums/kor/hal3-course,
  kiddogescort/hal4-course}.gc` — the four mission scripts that
  `deactivate-by-type` slot 20 now use the new enum name.

### 6. Rendering — the merc geometry `.fr3` injection

The paddy wagon's merc geometry only ever shipped in `LMEETBRT.DGO`.
`extra_art_groups_by_dgo` in `decompiler/config/jak2/jak2_config.jsonc` bakes
`paddy-wagon-ag:LMEETBRT.DGO` into `lwidea.fr3` / `lwideb.fr3` / `lwidec.fr3`
(the `:LMEETBRT.DGO` suffix resolves the texture ids through LMEETBRT's remap
table — the `lmeetbrt-pris` tpage — without which the van renders white), and
`paddy-wagon-ag.go` + `tpage-2438.go` are added to the three `lwide*.gd`.
See [`docs/modding/tools/model_and_entity_level_injection_guide.md`](../tools/model_and_entity_level_injection_guide.md).

> **Requires a re-extraction** (`task extract`) so the three `.fr3` are rebuilt.
> Without it the process runs (sounds, collision, riders) but the hull is
> **invisible**.

### 7. How to Test

1. **Extract (once):** `task extract` — rebuilds `lwide*.fr3` with
   `paddy-wagon-ag`. Look for
   `extra_art_groups_by_dgo: baking 'paddy-wagon-ag' into LWIDEA.DGO (.fr3)` in
   the log.
2. **Rebuild:** `task repl` then `(mi)` (new deftypes + a new `.o` in `cwi.gd` —
   restart the REPL if `(mi)` complains).
3. **Launch:** `task boot-game`, enter Haven City free-roam.
4. **Enable:** `Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable` (OFF by default),
   then reload the city (re-enter from an interior / warp) so `init-params`
   re-reads the want-count.
5. **Ambient:** drive around — a boxy armoured van in the car lanes, a Crimson
   Guard at the wheel, a civilian standing arms-crossed in the open rear cage,
   red dot on the minimap.
6. **Alert:** aggro a guard. The wagon joins the pursuit like a hellcat but
   never fires.
7. **Steal it:** press triangle. The guard is thrown clear, the **city alarm
   sounds (alert level 2)**, a Crimson Guard respawns on the street, and the
   **prisoner is still standing in the back** as you drive off.
8. **Destroy one:** it explodes like any guard vehicle.
9. From the REPL:
   `(send-event *traffic-manager* 'set-object-target-count (traffic-type paddywagon-v) 4)`
   for more of them.

**Key source files:**

- `goal_src/jak2/levels/city/traffic/vehicle/paddywagon-v.gc` *(new)* —
  `skel-paddywagon-v`, `*paddywagon-v-constants*`, `paddywagon-prisoner`
  (+ its variant roll, wardrobe, pose and `'knocked-off` refusal), `paddywagon-v`
  and its `allocate-and-init-cshape` / `init-skel-and-rigid-body` /
  `vehicle-method-137` overrides.
- `goal_src/jak2/engine/ai/traffic-h.gc` — `(traffic-type paddywagon-v 20)`.
- `goal_src/jak2/levels/city/traffic/vehicle/vehicle-h.gc`,
  `goal_src/jak2/engine/entity/entity-h.gc`,
  `decompiler/config/jak2/all-types.gc` — `(vehicle-type paddywagon-v 11)`.
- `goal_src/jak2/levels/city/traffic/traffic-manager.gc` — spawn case + gated
  `want-count` + `define-perm *mod-paddywagon-traffic-enable*`.
- `goal_src/jak2/levels/city/traffic/citizen/guard.gc` — car knock-off anim group.
- `goal_src/jak2/pc/debug/paddywagon-traffic-menu.gc` *(new)* — Debug ▸ Mods toggle.
- `goal_src/jak2/dgos/cwi.gd` — `"paddywagon-v.o"` after `car.o`.
- `goal_src/jak2/dgos/game.gd` — `"paddywagon-traffic-menu.o"` after `mods-menu.o`.
- `goal_src/jak2/dgos/lwide{a,b,c}.gd`, `decompiler/config/jak2/jak2_config.jsonc`
  — the `.fr3` merc injection.
- `goal_src/jak2/levels/city/{ctywide-tasks, protect/protect,
  slums/kor/hal3-course, kiddogescort/hal4-course}.gc` — enum rename.

### 8. Current State & Known Tradeoffs

- **Verified by build only.** `CWI.DGO`, `LWIDEA/B/C.DGO`, `GAME.CGO` and the
  full `(build-game)` all compile clean. In-game behaviour has **not** been
  observed yet — that needs `task extract` first.
- **Slot 20 is shared with `jak2/features/transport-ag/traffic`.** Both mods
  claim the same last free traffic slot, so as written they are **mutually
  exclusive**. Merging them would require extending `traffic-engine`'s
  `object-type-info-array` (21 → 22), `inactive-object-array` (420 → 440), the
  hard `:offset 7024` on `vehicle-tracker-array`, and every `(dotimes … 21)` in
  `traffic-engine.gc` / `traffic-manager.gc`.
- **Seat 1's height (`y` 819.2) is retail data tuned for the standing `babak`
  lurker.** A citizen skeleton has a different root height, so the prisoner may
  render slightly sunk into or floating above the cage floor. If so, nudge
  `seat-array 1 position` `y` in `*paddywagon-v-constants*` — it is the only
  cosmetic figure worth touching; the flight/handling figures must not move (see
  the `cm-offset-joint` warning in
  [`docs/modding/jak2_lisp_instructions.md`](../jak2_lisp_instructions.md)).
- **`chick` has no arms-crossed pose** (see §4) — she stands at ease.
- **Zone-dependent prisoner variety** (see §4) — LWIDEB only ever produces a
  `norm` prisoner, because retail ships no other civilian art group there.
  Making all three appear everywhere would mean injecting `citizen-fat-ag` /
  `citizen-chick-ag` into LWIDEB/LWIDEC too, which changes ordinary pedestrian
  residency — deliberately out of scope.
- **Unarmed by design** — no gun joint on the skeleton (see §1).
- **The wagon rides the low ground lanes,** not the hellcats' air lane, because
  retail `*paddywagon-constants*` `flags` `#xc` does not carry bit 6 (the
  flight-level bit the hellcat has). That is what "city traffic" means here.

---

### 9. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-09-10 | `levels/city/traffic/vehicle/paddywagon-v.gc` *(new)*<br>`engine/ai/traffic-h.gc`<br>`levels/city/traffic/vehicle/vehicle-h.gc`<br>`engine/entity/entity-h.gc`<br>`decompiler/config/jak2/all-types.gc`<br>`levels/city/traffic/traffic-manager.gc`<br>`levels/city/traffic/citizen/guard.gc`<br>`pc/debug/paddywagon-traffic-menu.gc` *(new)*<br>`dgos/{cwi,game,lwidea,lwideb,lwidec}.gd`<br>`decompiler/config/jak2/jak2_config.jsonc`<br>`levels/city/{ctywide-tasks,protect/protect,slums/kor/hal3-course,kiddogescort/hal4-course}.gc` | **Initial implementation.** New `paddywagon-v` (`vehicle-guard`) on traffic slot 20, reusing retail `paddy-wagon` hull + `*paddywagon-constants*` verbatim except `object-type` → `#x14`; no `no-hijack`, no `'lmeetbrt` re-home, no `choose-branch-callback` override, so it is an ordinary stealable traffic guard vehicle. New `paddywagon-prisoner` (`vehicle-rider`) in retail seat 1 (the rear cage, flags 4 / 180°): rolls `norm`/`fat`/`chick` among the art groups actually resident in the process's lwide level, holds `*-arms-crossed-ja` (idle for chick), re-rolls the retail `setup-masks` wardrobe on every `'traffic-on`, drops the base sine "lean", and refuses `'knocked-off` so it stays caged when Jak steals the van. `vehicle-method-137` override spawns both riders. Merc `.fr3` injection of `paddy-wagon-ag:LMEETBRT.DGO` into the three lwide levels + `paddy-wagon-ag.go`/`tpage-2438.go` in their `.gd`. Mandatory `Debug ▸ Mods ▸ paddywagon-traffic` toggle via `define-perm *mod-paddywagon-traffic-enable*` gating `want-count[20]`. | Put the Krimzon Guard prisoner van into ambient city traffic with a civilian prisoner and a Crimson Guard driver, drivable and stealable under the same conditions as every other guard vehicle — while leaving stock Haven City and the *Escort Brutter* mission untouched when the toggle is OFF. |

---

## 🇫🇷 Version Française

### 1. Présentation & Objectif

`paddywagon-v` est un **véritable véhicule du trafic terrestre** : un sous-type
de `vehicle-guard` (frère du `hellcat` / `guard-bike` / `cara`) qui apparaît
dans les voies de circulation d'Abriville, suit les branches de navigation de la
ville, affiche un **point rouge sur la carte**, est **conduit par un Garde
Grenat**, transporte un **civil prisonnier debout dans sa cage arrière**, peut
être **pris en main et conduit par le joueur**, et peut être **détruit** comme
tout véhicule de garde.

**Le voler est un crime** — et cela vient entièrement du code d'origine, pas du
mod : le chauffeur est un `crimson-guard-rider`, dont le bit 3 des `flags` de
`vehicle-rider` fait que la branche `'knocked-off` de
`vehicle-rider-event-handler` exécute
`(send-event *traffic-manager* 'increase-alert-level 2)` et fait réapparaître un
`crimson-guard-1` dans la rue. Identique au vol d'un hellcat.

Le fourgon est **non armé**. Le squelette `paddy-wagon` ne possède que les
joints « steering », « hatch », « main », « prejoint », « align » — aucun joint
d'arme — donc `turret info` reste à 0 et le garde-fou
`(when (nonzero? (-> this info)))` de `turret-control-method-11` fait que l'IA
de garde héritée poursuit sans jamais tirer.

Cette branche s'**inspire** de `jak2/features/transport-ag/traffic` (la
canonnière aérienne pilotable) et en réutilise les deux techniques structurelles
— le slot de trafic libre 20 et l'injection merc `.fr3` via
`extra_art_groups_by_dgo` — mais ne partage aucun code avec elle.

### 1b. Interrupteur runtime (procédure obligatoire)

Conformément aux règles d'or de CLAUDE.md, le mod est livré **désactivé** et
s'active depuis `Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable`.

Avec le drapeau à `#f`, le quota de trafic du slot 20 vaut 0 : le moteur de
trafic ne construit jamais de `paddywagon-v` ; aucun code de `paddywagon-v.gc`
ne s'exécute et aucun `paddywagon-prisoner` n'est jamais créé. Le reste du
câblage est **inerte plutôt que gardé**, car rien n'est atteignable sans un
objet de slot 20 : les renommages d'enums, les `case` supplémentaires dans
`traffic-object-spawn` / `type-from-vehicle-type`, et l'entrée d'animation de
chute pour l'object-type 20 dans `guard.gc`. Le quota est lu par
`traffic-manager::init-params` au chargement de la ville : **le toggle s'applique
au prochain (re)chargement de la ville**, pas instantanément.

Le type `paddywagon` d'origine dans `meet-brutter.gc` n'est **absolument pas
touché** : la mission *Escorter Brutter* est identique au jeu d'origine, mod
activé ou non.

### 2. Pourquoi un nouveau type plutôt que le `paddywagon` d'origine

Le type d'origine est inutilisable en monde ouvert, pour trois raisons
indépendantes :

| Le `paddywagon` d'origine… | …et pourquoi cela bloque un usage en trafic |
|---|---|
| est livré dans `LMEETBRT.DGO` | un niveau de mission emprunté — le type n'est même pas chargé en monde ouvert |
| `init-skel-and-rigid-body` force `(-> pp level)` à `'lmeetbrt` | l'art serait résolu depuis un niveau non résident : erreur d'art ou véhicule invisible |
| pose `rigid-body-object-flag no-hijack` | c'est le drapeau que teste la sonde d'embarquement de `vehicle-util.gc` avant même d'afficher l'invite « appuyez sur triangle » — le fourgon de mission est délibérément involable |
| force `choose-next-branch-no-exit-level` | le fourgon de mission est cloué au graphe de nav d'un seul niveau |
| `object-type` `#x13` | il usurpe le slot de trafic du hellcat |
| surcharge `vehicle-method-134` / `-108` / `active` / `hostile` / `die` | le script de poursuite de meet-brutter, pas un comportement de trafic urbain |

`paddywagon-v` est donc un simple `vehicle-guard` de trafic qui ne réutilise que
la **coque, les constantes physiques et la forme de collision** d'origine — au
mot près.

### 3. Ce que `vehicle-guard` fournit gratuitement

| Besoin | Hérité de | Mécanisme |
|---|---|---|
| Chauffeur Garde Grenat | `vehicle-guard::vehicle-method-137` | fait apparaître un `crimson-guard-rider` au siège 0. Le trafic met `trsflags-01` + `behavior 1` sur tout véhicule du pool → rider caché, révélé sur `'traffic-on`. |
| Point rouge sur la carte | `vehicle-guard::vehicle-method-128` | `add-icon! *minimap* … 14` — le marqueur rouge de garde. |
| Suit les voies de la ville | `vehicle-guard-choose-branch`, installé par `vehicle-guard::alloc-and-init-rigid-body-control` | suivi de nav-branch ordinaire |
| Poursuite hostile en alerte | états `hostile` / `stop-and-shoot` de `vehicle-guard` | le jeu d'origine donne **déjà** `trtflags-0` au slot 20 dans `traffic-engine::restore-default-settings` (ligne ~2918) : il reçoit `'alert-begin` / `'alert-end` et ne se gare jamais |
| Le joueur monte et conduit | `vehicle::check-player-get-on` | on ne pose simplement **pas** `no-hijack` |
| Le vol déclenche l'alerte | `'knocked-off` de `vehicle-rider-event-handler` + bit 3 des `flags` du `crimson-guard-rider` | alerte niveau 2 + un `crimson-guard-1` qui apparaît sur place |
| Pooling (masquage / réassise) | `vehicle-method-127` / `-128` diffusent `'traffic-off` / `'traffic-on` à **tous les enfants** | les deux riders sont des enfants : ils suivent le pool automatiquement |
| Positionnement des riders | `vehicle-method-119` | place chaque entrée de `rider-array` à son siège et applique l'`angle` du siège |

### 4. Le prisonnier

`paddywagon-prisoner` est un `vehicle-rider` — le même acteur léger, parenté au
siège et sans nav-mesh que le jeu d'origine utilise pour les passagers de
voiture (`citizen-norm-rider`) et les pilotes de garde (`crimson-guard-rider`).

**Le siège existait déjà.** Le `*paddywagon-constants*` d'origine déclare
`seat-count 2` :

| siège | `position` (x, y, z) | `angle` | `flags` | rôle |
|---|---|---|---|---|
| 0 | 0, 9420.8, 2457.6 | 0 | 1 | siège chauffeur / joueur |
| 1 | 0, 819.2, **-13107.2** | `#x8000` = 180° | 4 | **la cage arrière**, dos à la route |

Le siège 1 est exactement l'endroit où la mission meet-brutter dépose le lurker
capturé (`(get-best-seat-for-vehicle … 4 0)` → `put-rider-in-seat`). Ce mod y
place un civil à la place. Comme les `flags` du siège valent 4 et ceux du siège
joueur 1, le `(get-best-seat-for-vehicle … 1 1)` de `target-pilot` ne peut jamais
mettre Jak dans la cage.

**Tirage du gabarit et pose bras croisés.** Contrairement à
`citizen-norm-rider` — qui utilise l'art group allégé `citizen-norm-rider-ag`
dont les seules poses sont idle / bike-stance / car-stance — le prisonnier
utilise les art groups civils **complets**, seuls porteurs de la pose debout
bras croisés :

| variante | skeleton group | pose | elt d'art |
|---|---|---|---|
| `norm` | `skel-citizen-norm` | `citizen-norm-arms-crossed-ja` | 8 |
| `fat` | `skel-citizen-fat` | `citizen-fat-arms-crossed-ja` | 8 |
| `chick` | `skel-citizen-chick` | `citizen-chick-idle-ja` | 10 |

> [!IMPORTANT]
> **`citizen-chick` n'a réellement aucune animation bras croisés dans le jeu
> d'origine.** Ses seules poses debout dans `engine/data/art-elts.gc` sont
> `idle` (10), `shuffle` (26) et `riding-stance` (27). La prisonnière se tient
> donc au repos. Pour changer cela, éditez `*paddywagon-prisoner-chick-anim*`
> dans `paddywagon-v.gc` (27 = riding-stance est l'autre choix plausible).

**Variété dépendante de la zone.** `skeleton-group->draw-control` résout un
modèle via le **niveau du process lui-même** (`(-> (-> proc level) art-group)`),
et les riders de trafic sont re-domiciliés sur le niveau lwide par
`(lwide-entity-hack)`. Le jeu d'origine ne livre que :

| niveau | `citizen-norm-ag` | `citizen-fat-ag` | `citizen-chick-ag` |
|---|---|---|---|
| LWIDEA | ✅ | ✅ | ✅ |
| LWIDEB | ✅ | ❌ | ❌ |
| LWIDEC | ✅ | ❌ | ✅ |

`paddywagon-prisoner-pick-variant` **vérifie donc la résidence d'abord** (via
`paddywagon-prisoner-art-group-loaded?`, qui lit directement
`(-> lvl art-group string-array)` plutôt que de passer par
`art-group-load-check`, dont le chargement disque en build debug ferait diverger
debug et release) et ne tire que parmi ce qui est réellement disponible, avec
`norm` en repli garanti. Résultat : les trois gabarits dans la zone LWIDEA,
norm+chick dans LWIDEC, norm seul dans LWIDEB — ce qui reflète de toute façon
l'aspect des piétons d'origine dans ces zones.

**Le prisonnier reste en place quand Jak vole le fourgon.** `target-pilot`
parcourt *tous* les sièges à l'embarquement et envoie `'knocked-off` à leurs
occupants. C'est correct pour le garde chauffeur ; pas pour un prisonnier. Donc
`paddywagon-prisoner-event-handler` intercepte `'knocked-off` et renvoie `#f`.
Cela compte doublement : `target-pilot` ne libère le siège que si `send-event`
renvoie quelque chose de vrai, donc refuser l'événement garde aussi le
prisonnier inscrit dans `rider-array`, et donc toujours positionné chaque frame
par `vehicle-method-119`.

**Pas d'inclinaison.** Le `vehicle-rider-method-34` de base fixe le canal à
`num-func-identity` et pilote `frame-num` avec un sinus mêlé au braquage du
véhicule — l'inclinaison d'un conducteur dans un virage. La surcharge le réduit
à un simple `(ja-post)`, et le `:enter` de l'état `active` installe un
`:num! (loop!)` ordinaire : le prisonnier se contente de tenir sa pose.

**Garde-robe.** `vehicle-rider-method-33` re-tire les groupes `setup-masks`
transcrits depuis le `citizen-init!` de chaque civil (`citizen-norm.gc` /
`citizen-fat.gc` / `citizen-chick.gc`), avec `rand-vu-int-count` à la place de
la méthode `rnd-int-count` réservée aux `citizen`. Cela s'exécute à la création
**et** à chaque `'traffic-on` : chaque vie de trafic donne un prisonnier
fraîchement habillé.

### 5. Câblage du type de trafic

- `engine/ai/traffic-h.gc` — renomme `(traffic-type-20 20)` → `(paddywagon-v 20)`.
  **Le slot 20 est le dernier slot utilisable** : toutes les boucles du moteur
  sont des `(dotimes … 21)` et l'`object-type-info-array` de `traffic-engine`
  fait 21 entrées inline avec un `inactive-object-array` dimensionné à
  420 = 21 × 20 ; le slot 21 est donc inutilisable sans redimensionner ces
  structures (et l'`:offset 7024` en dur de `vehicle-tracker-array`). Le jeu
  d'origine avait déjà câblé le slot 20 comme slot de garde de niveau `ctywide`,
  tracker véhicule, `trtflags-0` — il n'avait qu'un quota de 0 et aucun handler
  de spawn.
- `levels/city/traffic/vehicle/vehicle-h.gc`, `engine/entity/entity-h.gc`,
  `decompiler/config/jak2/all-types.gc` — ajout de `(vehicle-type paddywagon-v 11)`.
- `levels/city/traffic/traffic-manager.gc` — `define-perm
  *mod-paddywagon-traffic-enable*`, les `case` de `traffic-object-spawn` et
  `type-from-vehicle-type`, et
  `want-count[20] = (if *mod-paddywagon-traffic-enable* 2 0)`.
- `levels/city/traffic/citizen/guard.gc` — object-type 20 ajouté au groupe
  d'animation de chute **voiture** `(14 15 16 19)`, pour qu'un garde éjecté du
  van utilise l'animation voiture et non celle de moto.
- `levels/city/{ctywide-tasks, protect/protect, slums/kor/hal3-course,
  kiddogescort/hal4-course}.gc` — les quatre scripts de mission qui font
  `deactivate-by-type` sur le slot 20 utilisent le nouveau nom d'enum.

### 6. Rendu — l'injection de géométrie merc `.fr3`

La géométrie merc du fourgon n'a jamais existé que dans `LMEETBRT.DGO`.
`extra_art_groups_by_dgo` dans `decompiler/config/jak2/jak2_config.jsonc` la
cuit sous la forme `paddy-wagon-ag:LMEETBRT.DGO` dans `lwidea.fr3` /
`lwideb.fr3` / `lwidec.fr3` (le suffixe `:LMEETBRT.DGO` résout les ids de
texture via la table de remap de LMEETBRT — la tpage `lmeetbrt-pris` — sans
laquelle le van s'affiche en blanc), et `paddy-wagon-ag.go` + `tpage-2438.go`
sont ajoutés aux trois `lwide*.gd`. Voir
[`docs/modding/tools/model_and_entity_level_injection_guide.md`](../tools/model_and_entity_level_injection_guide.md).

> **Impose une re-extraction** (`task extract`) pour reconstruire les trois
> `.fr3`. Sans cela le process tourne (sons, collisions, occupants) mais la
> coque est **invisible**.

### 7. Procédure de Test

1. **Extraire (une fois) :** `task extract` — reconstruit les `lwide*.fr3` avec
   `paddy-wagon-ag`. Vérifiez dans le log :
   `extra_art_groups_by_dgo: baking 'paddy-wagon-ag' into LWIDEA.DGO (.fr3)`.
2. **Recompiler :** `task repl` puis `(mi)` (nouveaux deftypes + nouveau `.o`
   dans `cwi.gd` — redémarrez le REPL si `(mi)` proteste).
3. **Lancer :** `task boot-game`, entrez dans Abriville en monde ouvert.
4. **Activer :** `Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable` (OFF par défaut),
   puis rechargez la ville (ressortez d'un intérieur / téléportez-vous) pour que
   `init-params` relise le quota.
5. **Ambiant :** roulez — un van blindé anguleux dans les voies de circulation,
   un Garde Grenat au volant, un civil debout bras croisés dans la cage arrière
   ouverte, point rouge sur la carte.
6. **Alerte :** provoquez un garde. Le fourgon rejoint la poursuite comme un
   hellcat mais ne tire jamais.
7. **Le voler :** appuyez sur triangle. Le garde est éjecté, **l'alarme de la
   ville retentit (alerte niveau 2)**, un Garde Grenat réapparaît dans la rue, et
   le **prisonnier est toujours debout à l'arrière** pendant que vous filez.
8. **En détruire un :** il explose comme tout véhicule de garde.
9. Depuis le REPL :
   `(send-event *traffic-manager* 'set-object-target-count (traffic-type paddywagon-v) 4)`
   pour en avoir davantage.

### 8. État Actuel & Compromis Connus

- **Vérifié à la compilation seulement.** `CWI.DGO`, `LWIDEA/B/C.DGO`,
  `GAME.CGO` et le `(build-game)` complet compilent proprement. Le comportement
  en jeu n'a **pas** encore été observé — cela nécessite `task extract` d'abord.
- **Le slot 20 est partagé avec `jak2/features/transport-ag/traffic`.** Les deux
  mods revendiquent le même dernier slot de trafic libre : en l'état ils sont
  **mutuellement exclusifs**. Les fusionner exigerait d'étendre
  l'`object-type-info-array` de `traffic-engine` (21 → 22),
  l'`inactive-object-array` (420 → 440), l'`:offset 7024` en dur de
  `vehicle-tracker-array`, et chaque `(dotimes … 21)` de `traffic-engine.gc` /
  `traffic-manager.gc`.
- **La hauteur du siège 1 (`y` 819.2) est une donnée d'origine calibrée pour le
  lurker `babak` debout.** Un squelette de citoyen a une hauteur de racine
  différente : le prisonnier peut donc apparaître légèrement enfoncé dans le
  plancher de la cage ou flottant au-dessus. Le cas échéant, ajustez le `y` de
  `seat-array 1 position` dans `*paddywagon-v-constants*` — c'est la seule
  valeur cosmétique à toucher ; les valeurs de vol/tenue de route ne doivent pas
  bouger (voir l'avertissement sur `cm-offset-joint` dans
  [`docs/modding/jak2_lisp_instructions.md`](../jak2_lisp_instructions.md)).
- **`chick` n'a pas de pose bras croisés** (voir §4) — elle se tient au repos.
- **Variété du prisonnier dépendante de la zone** (voir §4) — LWIDEB ne produira
  jamais qu'un prisonnier `norm`, faute d'autre art group civil livré là. Faire
  apparaître les trois partout impliquerait d'injecter `citizen-fat-ag` /
  `citizen-chick-ag` dans LWIDEB/LWIDEC, ce qui modifierait la résidence des
  piétons ordinaires — délibérément hors périmètre.
- **Non armé par conception** — aucun joint d'arme sur le squelette (voir §1).
- **Le fourgon roule dans les voies terrestres basses,** pas dans la voie
  aérienne des hellcats, car les `flags` `#xc` du `*paddywagon-constants*`
  d'origine ne portent pas le bit 6 (le bit de niveau de vol qu'a le hellcat).
  C'est ce que « trafic urbain » signifie ici.
