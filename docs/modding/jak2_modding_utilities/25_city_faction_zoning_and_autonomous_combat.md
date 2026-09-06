# Jak 2 — City Faction Zoning & Autonomous Guard-vs-Guard Combat / Zonage de Factions & Combats Autonomes Garde contre Garde

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/blueguard`
> - **Last Updated / Dernière modification:** `jak2/features/blueguard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## What this covers

How to split Haven City into **districts with different spawn rules**, make two guard factions
**fight each other autonomously in the background** without touching Jak's wanted level, make a
district a **police safe haven**, and expose the war-zone district as a **debug-menu config
option**. Worked example: the *City Insurrection* mode of the `crimson-blue-guard` mod (full
writeup: `docs/modding/current_mod/blue_guard_reskin_readme.md`).

Files touched: `traffic-manager.gc`, `traffic-engine.gc`, `guard.gc`, `crimson-blue-guard.gc`,
`engine/nav/nav-mesh.gc`, `engine/ai/traffic-h.gc`, `pc/debug/default-menu-pc.gc`.

---

## 1. Classify a world position into a district — by level name, not coordinates

The reliable way to say "which part of the city is this point in" is the **loaded city-level name**
that owns the point, *not* hardcoded XZ boxes (those are guesswork and break at seams).

Every city sub-level has a `city-level-info` in its BSP (`bsp-header` field `city-level-info`,
offset 208) with a `grid-info` bounding the level. `city-level-info::sphere-in-grid?`
(`traffic-engine.gc`) tests whether a position sits in an *active* nav cell of that level — the
exact test `update-traffic-amount` uses for citizens (`bit 0`) and vehicles (`bit 1`).

> **Critical pitfall — never call `sphere-in-grid?` on a raw `(-> lev bsp city-level-info)`.**
> That BSP pointer is part of the level's `-vis` heap. During a level transition the traffic
> manager keeps running while an outgoing city level is torn down: `level-unlink` has already
> zeroed the engine's `level-data-array` entry, **but the BSP field still dangles**, and
> `sphere-in-grid?` then walks a freed `grid-info` / `cell-array` → **hard crash, no GOAL error**
> (the game window just closes; the runtime log ends mid-frame right after `GAMEPLAY: enter <lvl>`).
> Only ever probe the ≤2 city grids the engine has fully linked *this* frame —
> `(-> *traffic-engine* level-data-array N city-info)`, the exact set `update-traffic` /
> `sphere-in-loaded-city-infos?` walk — and recover the level name by **pointer identity** (no
> deref of the possibly-dead data behind the pointer):

```lisp
(defun city-level-name-at-pos ((pos vector))
  (let ((engine *traffic-engine*))
    (when (and engine *level* pos)
      (let ((probe (new 'stack-no-clear 'vector)))
        (set! (-> probe quad) (-> pos quad))
        (set! (-> probe w) 4096.0)              ;; ~1m radius so a point on a seam still resolves
        (dotimes (di 2)                          ;; only the engine's linked city grids
          (let ((info (-> engine level-data-array di city-info)))
            (when (and (nonzero? info) (sphere-in-grid? info probe 0))
              (dotimes (li (-> *level* length))
                (let ((lev (-> *level* level li)))
                  (when (and (= (-> lev status) 'active)
                             (= (the-as int (-> lev bsp city-level-info)) (the-as int info)))
                    (return (-> lev name)))))))))))  ;; runtime `level` name symbol, e.g. 'ctysluma
  #f)
```

Verified Jak 2 city level names (`level-info.gc`) grouped into districts:

| District tag | Level names | Role |
|---|---|---|
| `slums` | `ctysluma` `ctyslumb` `ctyslumc` | always the blue rebel haven |
| `industrial` | `ctyinda` `ctyindb` | default war zone |
| `port` | `ctyport` | selectable war zone |
| `bazaar` | `ctygena` `ctygenb` `ctygenc` | selectable war zone |
| `farm` | `ctyfarma` `ctyfarmb` | selectable war zone |
| `market` | `ctymarka` `ctymarkb` | selectable war zone |
| `other` | `ctypal`, `ctyasha`, `ctykora`, `ctyfence`, `ctywide` | always loyalist |

`city-district-of-level` maps a level name → district tag. `city-zone-from-level-name` then maps
tag → zone: `slums → 'blue`, `tag == *mod-city-conflict-district* → 'conflict`, everything else
`→ 'red`. `city-get-pos-zone` runs a position through it (with a bsphere-nearest-level fallback
for the rare case the grid lookup can't resolve `pos`); `city-get-current-zone` does the same for
Jak, falling back to `(-> *load-state* vis-nick)` when `*target*` is `#f`.

Making the war zone a **config value** (`*mod-city-conflict-district*`, a symbol) rather than a
hardcoded name is one `define` + threading it through the tag comparison — the district system
above already does the work.

---

## 2. Strict per-district faction spawning — two pools, faction chosen per spawn

Ambient guards come from **two** traffic types:

* `crimson-guard-1` (6) — the stock ambient guard pool (base `want-count` 9), driven by the alert
  system. Always active.
* `crimson-guard-2` (7) — a **fully-wired but unused** pool. `restore-default-settings` reserves
  it and gives it the alert flag (`trtflags-0`) exactly like type 6, but stock jak2 never assigns
  it a `want-count`/`target-count` and there is **no `traffic-object-spawn` case** for it. Add the
  case (spawn the same `crimson-guard` / `crimson-blue-guard` processes as type 6) and drive its
  counts, and it works identically to type 6 — a free second 20-slot pool. Used here only in the
  war zone, to double the combatant ceiling for a genuinely chaotic battle.

Do **not** build on `crimson-guard-0` (4): `restore-default-settings` clears its `trtflags-2`, so
`activate-by-type` can never promote it — its pool fills and nothing ever walks the street. Leave
it at `want-count` 0.

**Two traps that look reasonable and fail:**

1. *Filtering a shared 50/50 pool per district* — have `activate-from-params` scan the inactive
   list for the wanted faction and skip when it's absent. In a strict district **half the pool is
   the wrong faction and can never activate** → effective density silently drops ~50% (the "where
   did the red guards go?" bug). A recycled process keeps its type, so a shared pool never becomes
   *purely* one faction.
2. *Splitting the factions across `crimson-guard-0` / `crimson-guard-1`* — clean in theory, but
   `crimson-guard-0` never activates (trap above), so you get zero of that faction on the street.

**What works: single-faction pools, faction chosen per spawn from the district Jak is in.** Cache
the district each frame (see §3) so the spawner reads it cheaply:

```lisp
;; traffic-object-spawn (traffic-manager.gc) -- crimson-guard-1 AND crimson-guard-2 branches:
(defun mod-city-guard-spawn-blue? ((params traffic-object-spawn-params))
  (cond
    (*mod-city-insurrection?*
     (case *mod-city-guard-zone*          ;; cached by the per-frame shaper
       (('blue) #t)                       ;; Slums: rebel stronghold
       (('conflict) (zero? (rand-vu-int-count 2)))   ;; war zone: 50/50 roll
       (else #f)))                        ;; loyalist: stock red
    (else (logtest? (-> params id) 1))))  ;; non-Insurrection: id-parity mix
```

`activate-from-params` then needs **no** faction logic under Insurrection —
`(get-from-inactive-by-type this gp-0)` activates whatever the pool holds, and the pool is kept
the right faction by the per-frame reconciliation in §3 (which retires a couple of wrong-faction
guards per frame after a district change while `spawn-all` refills with the new one). Keep the old
id-parity + `activate-from-params` faction-pick path for the **non-Insurrection** modes (City
Peaceful = every guard blue, stock ambient = 1-in-`*crimson-blue-guard-ratio*` blue), where a
mixed pool is what you want.

---

## 3. Density & suppression — live `want-count` / `target-count` / `inv-density-factor`

`want-count` (per `traffic-object-type-info`, set once in `traffic-manager::init-params`) sizes the
inactive pool; `target-count` caps how many are *active*; `traffic-engine inv-density-factor`
controls spawn spacing along a nav segment (lower = tighter = denser on screen). Edit all three
**every frame** from `traffic-manager::update` (before the kill/spawn pass) based on the current
zone, restoring from a captured baseline otherwise:

```lisp
;; static mirror of the init-params values -- single restore source
(define *traffic-want-count-base*
  (new 'static 'boxed-array :type int8 15 15 14 1 1 0 9 0 14 14 14 8 8 8 7 7 7 0 8 8 0))

;; in update, before (kill-excess-once) / (spawn-all): reset all 21, then shape for the district
(dotimes (i 21) (set! (-> engine object-type-info-array i want-count) (-> *traffic-want-count-base* i)))
(set! (-> engine object-type-info-array 4 want-count) 0)   ;; crimson-guard-0 unused (see §2)
(case (city-get-current-zone)
  (('conflict)   ;; war zone: two guard pools (~30), NO civilians (0..3), metalheads (8..10) or vehicles (11..19)
   (set! (-> engine object-type-info-array 6 want-count) 18) (set! (-> engine object-type-info-array 6 target-count) 16)
   (set! (-> engine object-type-info-array 7 want-count) 16) (set! (-> engine object-type-info-array 7 target-count) 14)
   (set! (-> engine object-type-info-array 7 guard-type) (-> engine object-type-info-array 6 guard-type)) ;; mirror the weapon roll
   (dotimes (i 4) (set! (-> engine object-type-info-array i want-count) 0))
   (dotimes (i 3) (set! (-> engine object-type-info-array (+ i 8) want-count) 0))
   (dotimes (i 9) (set! (-> engine object-type-info-array (+ i 11) want-count) 0))
   (set! (-> engine inv-density-factor) 2.0))   ;; pack the fight into the on-screen slice
  (('blue)       ;; Slums: lone blue rebels, stock pool only, no loyalist gunships
   (set! (-> engine object-type-info-array 6 want-count) 10) (set! (-> engine object-type-info-array 6 target-count) 7)
   (set! (-> engine object-type-info-array 7 want-count) 0)  (set! (-> engine object-type-info-array 7 target-count) 0)
   (set! (-> engine object-type-info-array 18 want-count) 0) (set! (-> engine object-type-info-array 19 want-count) 0)
   (set! (-> engine inv-density-factor) 5.0))
  (else          ;; loyalist: stock red police -- pool 6 fully vanilla (no want/target override), pool 7 off, stock density
   (set! (-> engine object-type-info-array 7 want-count) 0) (set! (-> engine object-type-info-array 7 target-count) 0)
   (set! (-> engine inv-density-factor) 5.0)))
```

The two war-zone counts stay **well under the stock 64 nav-user ceiling** — every non-guard is
suppressed there, so ~30 guards plus a neighbouring district fit with room to spare, and an
over-cap guard just fails to spawn (graceful). Do **not** raise `nav-max-users` in
`engine/nav/nav-mesh.gc` for this — an early attempt did (floor 96) and it contributed to a
loading-level heap overrun on the district transition (see the pitfall at the end of this section).

Traffic types (`traffic-h.gc`): `0..3` citizens, `4`/`6`/`7` crimson-guard pools, `8..10`
metal-heads, `11..16` civilian bikes/cars, `18` guard-bike, `19` hellcat.

**`target-count` fights the alert system.** Guard types are alert-managed: `update-alert-state`
recomputes `object-type-info-array <type> target-count` every frame from `*alert-level-settings*[level]`
(sum of the tazer/rifle/grenade slots for type 6; the never-populated `ped-roboguard` slot for
type 7 → **0**). At peace that caps type 6 at ~5 and type 7 at 0. To run a denser battle you must
force `target-count` **after** `update-traffic` has run — i.e. from `traffic-manager::update`,
which is already after it, so your value is what `activate-by-type` sees next frame. In loyalist
districts, force **neither** lever on pool 6: the stock alert-scaled police response is preserved
byte-for-byte.

**`reserve-count` is a per-session spawn budget that quietly runs out.** It starts at
`(max 1000 (* 1000 want-count))` (so ~1000 for a pool whose stock want-count is 0, like type 7),
decrements on every activation and on every hard kill (`get-from-inactive-by-type` /
`set-process-to-killed`). The per-frame reconciliation below hard-kills wrong-faction guards on a
district change, so top the two war-zone pools' `reserve-count` up to `#x2000` **when Jak first
enters the war zone** (not every frame — that would fight `transport.gc` / mission scripts that
read `get-object-reserve-count` for `crimson-guard-1`). `spawn-all` still stops at `want-count`,
so a high reserve can't over-allocate.

**`activate-one-vehicle`** (peds/guards; the decomp name is misleading, see §4) picks a random
traffic type in `0..10` excluding those with `inactive-count == 0`, then calls `activate-by-type`.
Zeroing the citizen/metalhead want-counts drains those pools, masking them out of the roll so it
lands on `{6, 7}` — the two guard pools — almost every time.

**District transitions must be INCREMENTAL — never a single-frame flush.** The first cut did the
whole turnover on the frame the zone changed: hard-kill all three guard pools + `deactivate-by-type`
every civilian / metalhead / civilian-vehicle / gunship type + `fast-spawn` (→ `spawn-all` runs
120 spawns). That frame often coincides with the outgoing city level's teardown (`level-unlink`,
process cleanup) — the mass process churn plus the (mistaken) raised `nav-max-users` allocation
overran a fixed buffer / the loading-level heap → **hard crash, no GOAL error, log ends mid-frame
at `kill #<level active ctysluma>`**. Same failure family as the `sphere-in-grid?` pitfall in §1.

Do it a couple of ops per frame instead:

```lisp
;; each frame, after shaping want/target: retire <=2 wrong-faction guards per pool
(mod-city-guard-pool-reconcile this (traffic-type crimson-guard-1) zone 2)
(mod-city-guard-pool-reconcile this (traffic-type crimson-guard-2) zone 2)
;; reconcile: kill <=budget wrong-faction INACTIVE guards (get-from-inactive-by-handle + reserve--
;;            + deactivate); if budget remains, park <=that many wrong-faction ACTIVE ones
;;            (deactivate-object force -> re-enters inactive, killed next frame). No-op when pure.
```

`kill-excess-once` (already in `traffic-manager::update`) drains the want-0 civilian / gunship
pools 1/frame; `spawn-all` (no `fast-spawn`) refills the guard pools 1/frame with the right
faction via the spawn-time faction pick (§2); the reconcile pass clears the departing faction
2/frame. Net: the street crossfades over ~1–2 s, and no frame ever does more than a handful of
process operations, so it can't race a level transition. Active civilians the reconcile can't
touch simply drain as they leave Jak's loaded vis-grid (`update-traffic-amount` deactivates
out-of-grid traffic) — a few seconds, not instant, and it only happens once on entry.

**Pitfall:** nothing else writes `want-count` at runtime, so a per-frame rewrite is safe — but
track a "was shaping" flag so you restore exactly once when the mode turns off.

---

## 4. Autonomous guard-vs-guard combat with zero effect on Jak's wanted level

Two facts make this clean:

1. **`traffic-engine::increase-alert-level` is a no-op unless the attacker carries
   `process-mask target`** (i.e. Jak). Guard-vs-guard attacks never pass Jak as the attacker, so
   the wanted level cannot rise from a faction fight — no special-casing for the alarm itself.
2. **`incoming attacker-handle` already resolves a projectile to its firer.**
   `find-offending-process-focusable` (`process-drawable.gc`) walks the attack's process parent
   chain, and guard shots (`crimson-guard-method-214`, `spawn-projectile ... this ...`) parent the
   projectile to the firing guard. So a `'hit` handler can type-check `incoming attacker-handle`
   directly — melee *and* ranged — to see who really hit it.

The acquisition hook (one faction-aware helper, safe in shared states a subtype inherits):

```lisp
(defun crimson-guard-insurrection-scan ((this crimson-guard))
  (when (and *mod-city-insurrection?* (= (city-get-pos-zone (-> this root trans)) 'conflict))
    ;; search-blue? = #t for a red guard (hunts blue), #f for a blue guard (hunts red)
    (let ((foe (find-nearest-enemy-guard this (not (type-type? (-> this type) crimson-blue-guard)) (meters 60))))
      (when foe
        (set! (-> this traffic-target-status handle) (process->handle foe))
        (try-update-focus (-> this focus) foe this)
        (go-hostile this)))))     ;; never calls trigger-alert / increase-alert-level
```

**Acquisition range** was 40 m in the first cut and read as guards ignoring visible enemies across
a street; `(meters 60)` is a war-zone sightline down an Industrial block. Same value in
`crimson-blue-guard-attack-guards`.

`find-nearest-enemy-guard` (`guard.gc`) walks the traffic-engine's active-object lists and filters
by `type-type?`. Call the hook from **both** `active:trans` and `search:trans` — a guard that
loses a foe in `search` must re-acquire or drop back to `active`, else stock `search` (keyed off
`traffic-target-flag visible-recently`, only maintained for Jak) can leave it walking forever.

> **Critical pitfall — the two traffic trackers are named backwards in the decomp.**
> `traffic-engine` has `tracker-array` (2 inline `traffic-tracker`s). The decomp aliases
> `citizen-tracker-array` onto `tracker-array[0]` and `vehicle-tracker-array` onto
> `tracker-array[1]` — **but the contents are the other way round**: pedestrians and guards
> (traffic-types `0..10`) live in `vehicle-tracker-array` / `tracker-array[1]`, and vehicles
> (`11..20`) live in `citizen-tracker-array` / `tracker-array[0]`. Proof:
> `traffic-engine::child-killed` routes a `citizen` to `vehicle-tracker-array` and a `vehicle` to
> `citizen-tracker-array`; the `activate-one-citizen` / `activate-one-vehicle` method names are
> swapped the same way. The first cut of this mod scanned `citizen-tracker-array` for guards,
> found only vehicles, and got **zero** inter-faction combat. Scan `(-> engine tracker-array tk)`
> for `tk` in `0..1` and you don't have to care which alias is which.

**Reciprocal retaliation** lives in the victim's `'hit` handler: resolve the attacker, and if it's
the opposing faction, `try-update-focus` + `go-hostile` on it directly — skip the `speech-control`
"spotted!" bark and the `trigger-alert` call the stock path would do.

---

## 5. Police safe haven / alert-free zones — one choke point

`increase-alert-level` is the *single* place the alert level goes up (menu event,
`citizen::trigger-alert` calling it directly, and the kill-count escalation in
`update-alert-state` all route through it). Guard it so **only loyalist districts** run the
wanted system — the Slums *and* the war zone are alert-free (so hitting a red guard in the war
zone raises nothing):

```lisp
(defmethod increase-alert-level ((this traffic-engine) (arg0 int) (arg1 target))
  (when (not (and *mod-city-insurrection?*
                  (let ((z (city-get-current-zone))) (or (= z 'blue) (= z 'conflict)))))
    ... stock body ...))
```

Then also `(set-alert-level engine 0)` each frame Jak is in an alert-free zone, so an alert he
*carried in* drops immediately (note: `decrease-alert-level` takes a *floor* — `(min level arg)` —
so passing `4` does nothing; use `set-alert-level` or `decrease-alert-level 0`).

---

## 6. Apply mode / config changes to guards already spawned

`send-event *traffic-manager* 'deactivate-by-type <n>` parks every active process of a traffic
type (they go to the inactive list, not killed); the spawner rebuilds under the current rules over
the next second or two. This is safe **only from a debug-menu pick-func** — an explicit user
action, never during a level transition. Send it for the guard pools (`4`, `6`, `7`) and guard
vehicles (`18`, `19`) from the mode toggles and the war-zone picker so faction / squad / weapon /
zone composition re-roll promptly.

Do **not** do this on a *district change* — that fires while the outgoing city level is being torn
down and a big `deactivate-by-type` burst there crashes the game (§3). A district change instead
relies purely on the per-frame reconciliation in §3: `want-count` / `target-count` shaping +
`mod-city-guard-pool-reconcile` (≤2 wrong-faction retirements per pool per frame) +
`kill-excess-once` + `spawn-all`, all bounded to a handful of process ops per frame.

A radio-style menu picker over a symbol config value is one shared `flag` pick-func — the menu
template's 3rd element is passed to the pick-func as `arg0`, so bake the choice into it:

```lisp
'(menu "Insurrection war zone"
   (flag "Industrial (default)" industrial dm-mod-city-conflict-district-pick-func)
   (flag "Port"                 port       dm-mod-city-conflict-district-pick-func)
   ...)

(defun dm-mod-city-conflict-district-pick-func ((arg0 symbol) (arg1 debug-menu-msg))
  (when (= arg1 (debug-menu-msg press))
    (set! *mod-city-conflict-district* arg0)
    (dm-mod-city-flush-guards))
  (= *mod-city-conflict-district* arg0))   ;; return -> checkmark on the current row
```

---

## Prior art — Jak 3's faction system

Jak 3 ships a full faction war for the same city geometry (CWI): `cty-faction-h.gc`
(`cty-faction-manager`, `nav-territory-type` with deep/border sub-zones per faction,
per-territory strength), and `kg-squad-control` / `mh-squad-control` / `ff-squad-control` with
per-member `hatred-memory`. It is the canonical, much heavier design, and it depends on jak3
nav-graph territory metadata the jak2 city does not have — hence the lightweight
position→zone→AI-hook approach above. If you ever port that system, start at `cty-faction-h.gc`.

---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## Ce que ça couvre

Comment découper Haven City en **quartiers aux règles de spawn différentes**, faire **combattre
deux factions de gardes entre elles de façon autonome** en arrière-plan sans toucher au niveau de
recherche de Jak, faire d'un quartier une **zone refuge de police**, et exposer le quartier de
guerre comme **option de config du menu debug**. Exemple concret : le mode *City Insurrection* du
mod `crimson-blue-guard` (rédaction complète :
`docs/modding/current_mod/blue_guard_reskin_readme.md`).

Fichiers modifiés : `traffic-manager.gc`, `traffic-engine.gc`, `guard.gc`, `crimson-blue-guard.gc`,
`engine/nav/nav-mesh.gc`, `engine/ai/traffic-h.gc`, `pc/debug/default-menu-pc.gc`.

---

## 1. Classer une position en quartier — par nom de niveau, pas par coordonnées

La façon fiable de dire « dans quelle partie de la ville se trouve ce point » est le **nom du
niveau de ville chargé** qui contient le point, et *non* des boîtes XZ codées en dur (approximatives
et cassées aux jointures).

Chaque sous-niveau de ville a un `city-level-info` dans son BSP (champ `city-level-info` de
`bsp-header`, offset 208) avec un `grid-info` qui borne le niveau.
`city-level-info::sphere-in-grid?` (`traffic-engine.gc`) teste si une position est dans une
cellule nav *active* de ce niveau — le test exact qu'utilise `update-traffic-amount` pour les
civils (`bit 0`) et les véhicules (`bit 1`).

> **Piège critique — n'appelle JAMAIS `sphere-in-grid?` sur un `(-> lev bsp city-level-info)` brut.**
> Ce pointeur BSP fait partie du tas `-vis` du niveau. Pendant une transition de niveau, le
> traffic-manager continue de tourner pendant qu'un niveau de ville sortant est démonté :
> `level-unlink` a déjà mis à zéro l'entrée `level-data-array` du moteur, **mais le champ BSP
> pointe toujours dans le vide**, et `sphere-in-grid?` parcourt alors un `grid-info` / `cell-array`
> libéré → **crash brutal, aucune erreur GOAL** (la fenêtre du jeu se ferme ; le log runtime
> s'arrête en pleine frame juste après `GAMEPLAY: enter <lvl>`). Ne sonde que les ≤2 grilles de
> ville que le moteur a entièrement liées *cette* frame — `(-> *traffic-engine* level-data-array N
> city-info)`, l'ensemble exact que parcourent `update-traffic` / `sphere-in-loaded-city-infos?` —
> et retrouve le nom du niveau par **identité de pointeur** (pas de déréférencement des données
> potentiellement mortes derrière le pointeur) :

```lisp
(defun city-level-name-at-pos ((pos vector))
  (let ((engine *traffic-engine*))
    (when (and engine *level* pos)
      (let ((probe (new 'stack-no-clear 'vector)))
        (set! (-> probe quad) (-> pos quad))
        (set! (-> probe w) 4096.0)              ;; rayon ~1m : un point sur une jointure se résout quand même
        (dotimes (di 2)                          ;; uniquement les grilles de ville liées par le moteur
          (let ((info (-> engine level-data-array di city-info)))
            (when (and (nonzero? info) (sphere-in-grid? info probe 0))
              (dotimes (li (-> *level* length))
                (let ((lev (-> *level* level li)))
                  (when (and (= (-> lev status) 'active)
                             (= (the-as int (-> lev bsp city-level-info)) (the-as int info)))
                    (return (-> lev name)))))))))))  ;; symbole `name` du `level`, ex. 'ctysluma
  #f)
```

Noms de niveaux de ville Jak 2 vérifiés (`level-info.gc`), regroupés en quartiers :

| Tag de quartier | Noms de niveaux | Rôle |
|---|---|---|
| `slums` | `ctysluma` `ctyslumb` `ctyslumc` | toujours le refuge rebelle bleu |
| `industrial` | `ctyinda` `ctyindb` | zone de guerre par défaut |
| `port` | `ctyport` | zone de guerre sélectionnable |
| `bazaar` | `ctygena` `ctygenb` `ctygenc` | zone de guerre sélectionnable |
| `farm` | `ctyfarma` `ctyfarmb` | zone de guerre sélectionnable |
| `market` | `ctymarka` `ctymarkb` | zone de guerre sélectionnable |
| `other` | `ctypal`, `ctyasha`, `ctykora`, `ctyfence`, `ctywide` | toujours loyaliste |

`city-district-of-level` mappe un nom de niveau → tag de quartier. `city-zone-from-level-name`
mappe ensuite tag → zone : `slums → 'blue`, `tag == *mod-city-conflict-district* → 'conflict`,
tout le reste `→ 'red`. `city-get-pos-zone` fait passer une position dedans (avec un repli sur le
niveau de ville actif le plus proche pour le cas rare où la grille échoue) ;
`city-get-current-zone` fait pareil pour Jak, avec repli sur `(-> *load-state* vis-nick)` quand
`*target*` est `#f`.

Faire de la zone de guerre une **valeur de config** (`*mod-city-conflict-district*`, un symbole)
plutôt qu'un nom codé en dur, c'est un `define` + le passer dans la comparaison de tag — le
système de quartiers ci-dessus fait déjà le travail.

---

## 2. Spawn de faction strict par quartier — deux pools, faction choisie à chaque spawn

Les gardes ambiants viennent de **deux** traffic-types :

* `crimson-guard-1` (6) — le pool de gardes ambiants d'origine (`want-count` de base 9), piloté par
  le système d'alerte. Toujours actif.
* `crimson-guard-2` (7) — un pool **entièrement câblé mais inutilisé**. `restore-default-settings`
  le réserve et lui donne le flag d'alerte (`trtflags-0`) exactement comme le type 6, mais le jak2
  d'origine ne lui assigne jamais de `want-count`/`target-count` et il n'y a **aucune branche
  `traffic-object-spawn`** pour lui. Ajoute la branche (spawn des mêmes process `crimson-guard` /
  `crimson-blue-guard` que le type 6) et pilote ses compteurs, et il fonctionne à l'identique du
  type 6 — un second pool de 20 slots gratuit. Utilisé ici uniquement dans la zone de guerre, pour
  doubler le plafond de combattants et une vraie bataille chaotique.

Ne construis **rien** sur `crimson-guard-0` (4) : `restore-default-settings` efface son
`trtflags-2`, donc `activate-by-type` ne peut jamais l'activer — son pool se remplit et rien ne
marche dans la rue. Laisse-le à `want-count` 0.

**Deux pièges qui paraissent raisonnables et échouent :**

1. *Filtrer un pool partagé 50/50 par quartier* — faire scanner la liste inactive par
   `activate-from-params` pour la faction voulue et sauter quand elle est absente. Dans un quartier
   strict, **la moitié du pool est la mauvaise faction et ne peut jamais s'activer** → la densité
   effective chute de ~50 % (le bug « où sont passés les gardes rouges ? »). Un process recyclé
   garde son type, donc un pool partagé ne devient jamais *purement* d'une faction.
2. *Séparer les factions sur `crimson-guard-0` / `crimson-guard-1`* — propre en théorie, mais
   `crimson-guard-0` ne s'active jamais (piège ci-dessus), donc zéro garde de cette faction en rue.

**Ce qui marche : pools mono-faction, faction choisie à chaque spawn selon le quartier de Jak.**
Mémorise le quartier chaque frame (voir §3) pour que le générateur le lise à moindre coût :

```lisp
;; traffic-object-spawn (traffic-manager.gc) -- branches crimson-guard-1 ET crimson-guard-2 :
(defun mod-city-guard-spawn-blue? ((params traffic-object-spawn-params))
  (cond
    (*mod-city-insurrection?*
     (case *mod-city-guard-zone*          ;; mis en cache par le modeleur par-frame
       (('blue) #t)                       ;; Slums : bastion rebelle
       (('conflict) (zero? (rand-vu-int-count 2)))   ;; zone de guerre : tirage 50/50
       (else #f)))                        ;; loyaliste : rouge d'origine
    (else (logtest? (-> params id) 1))))  ;; hors Insurrection : mélange parité-id
```

`activate-from-params` n'a alors besoin d'**aucune** logique de faction sous Insurrection —
`(get-from-inactive-by-type this gp-0)` active ce que le pool contient, et le pool est déjà 100 %
la bonne faction. Au **changement de quartier**, vide + recharge chaque pool de gardes (§6) pour
qu'aucun ne reste la faction du quartier précédent. Garde l'ancien chemin parité-id +
filtre-faction de `activate-from-params` pour les modes **hors Insurrection** (City Peaceful = tous
bleus, ambiant d'origine = 1-sur-`*crimson-blue-guard-ratio*` bleu), où un pool mixte est voulu.

---

## 3. Densité & suppression — `want-count` / `target-count` / `inv-density-factor` en direct

`want-count` (par `traffic-object-type-info`, défini une fois dans `traffic-manager::init-params`)
dimensionne le pool inactif ; `target-count` plafonne le nombre d'*actifs* ;
`traffic-engine inv-density-factor` contrôle l'espacement de spawn le long d'un segment nav (plus
bas = plus serré = plus dense à l'écran). Modifie les trois **à chaque frame** depuis
`traffic-manager::update` (avant la passe kill/spawn) selon la zone courante, en restaurant depuis
une base capturée sinon :

```lisp
;; miroir statique des valeurs d'init-params -- source unique de restauration
(define *traffic-want-count-base*
  (new 'static 'boxed-array :type int8 15 15 14 1 1 0 9 0 14 14 14 8 8 8 7 7 7 0 8 8 0))

;; dans update, avant (kill-excess-once) / (spawn-all) : reset des 21, puis modelage du quartier
(dotimes (i 21) (set! (-> engine object-type-info-array i want-count) (-> *traffic-want-count-base* i)))
(set! (-> engine object-type-info-array 4 want-count) 0)   ;; crimson-guard-0 inutilisé (voir §2)
(case (city-get-current-zone)
  (('conflict)   ;; zone de guerre : deux pools de gardes (~30), AUCUN civil (0..3), tête-de-métal (8..10) ni véhicule (11..19)
   (set! (-> engine object-type-info-array 6 want-count) 18) (set! (-> engine object-type-info-array 6 target-count) 16)
   (set! (-> engine object-type-info-array 7 want-count) 16) (set! (-> engine object-type-info-array 7 target-count) 14)
   (set! (-> engine object-type-info-array 7 guard-type) (-> engine object-type-info-array 6 guard-type)) ;; miroir du tirage d'arme
   (dotimes (i 4) (set! (-> engine object-type-info-array i want-count) 0))
   (dotimes (i 3) (set! (-> engine object-type-info-array (+ i 8) want-count) 0))
   (dotimes (i 9) (set! (-> engine object-type-info-array (+ i 11) want-count) 0))
   (set! (-> engine inv-density-factor) 2.0))   ;; concentre le combat dans la tranche visible
  (('blue)       ;; Slums : rebelles bleus solitaires, pool d'origine seul, pas de vaisseaux loyalistes
   (set! (-> engine object-type-info-array 6 want-count) 10) (set! (-> engine object-type-info-array 6 target-count) 7)
   (set! (-> engine object-type-info-array 7 want-count) 0)  (set! (-> engine object-type-info-array 7 target-count) 0)
   (set! (-> engine object-type-info-array 18 want-count) 0) (set! (-> engine object-type-info-array 19 want-count) 0)
   (set! (-> engine inv-density-factor) 5.0))
  (else          ;; loyaliste : police rouge d'origine -- pool 6 100% vanilla (aucun override want/target), pool 7 éteint, densité d'origine
   (set! (-> engine object-type-info-array 7 want-count) 0) (set! (-> engine object-type-info-array 7 target-count) 0)
   (set! (-> engine inv-density-factor) 5.0)))
```

Types de trafic (`traffic-h.gc`) : `0..3` civils, `4`/`6`/`7` pools crimson-guard, `8..10`
têtes-de-métal, `11..16` motos/voitures civiles, `18` guard-bike, `19` hellcat.

Les deux compteurs de la zone de guerre restent **bien sous le plafond nav d'origine de 64** —
tous les non-gardes y sont supprimés, donc ~30 gardes plus un quartier voisin tiennent avec de la
marge, et un garde au-delà du plafond échoue simplement à spawner (sans crash). Ne **pas** relever
`nav-max-users` dans `engine/nav/nav-mesh.gc` pour ça — un essai l'a fait (plancher 96) et ça a
contribué à un débordement du tas loading-level à la transition de quartier (voir le piège en fin
de section).

**`target-count` se bat contre le système d'alerte.** Les types garde sont pilotés par l'alerte :
`update-alert-state` recalcule `object-type-info-array <type> target-count` chaque frame depuis
`*alert-level-settings*[level]` (somme des slots taser/fusil/grenade pour le type 6 ; le slot
`ped-roboguard` jamais peuplé pour le type 7 → **0**). En paix ça plafonne le type 6 à ~5 et le
type 7 à 0. Pour une bataille plus dense il faut forcer `target-count` **après** que
`update-traffic` a tourné — donc depuis `traffic-manager::update`, qui est déjà après, pour que ta
valeur soit celle que voit `activate-by-type` la frame suivante. Dans les quartiers loyalistes, ne
force **aucun** levier sur le pool 6 : la réponse policière échelonnée d'origine est préservée à
l'identique.

**`reserve-count` est un budget de spawn par session qui s'épuise silencieusement.** Il démarre à
`(max 1000 (* 1000 want-count))` (donc ~1000 pour un pool dont le want-count d'origine est 0, comme
le type 7), décrémente à chaque activation et à chaque kill dur (`get-from-inactive-by-type` /
`set-process-to-killed`). La réconciliation par frame ci-dessous tue des gardes de la mauvaise
faction au changement de quartier, donc épingle le `reserve-count` des deux pools de la zone de
guerre à `#x2000` **quand Jak entre dans la zone de guerre** (pas chaque frame — ça se battrait
avec `transport.gc` / les scripts de mission qui lisent `get-object-reserve-count` pour
`crimson-guard-1`). `spawn-all` s'arrête toujours à `want-count`, donc un reserve élevé ne peut
pas sur-allouer.

**`activate-one-vehicle`** (piétons/gardes ; le nom du décomp est trompeur, voir §4) tire un
traffic-type aléatoire dans `0..10` en excluant ceux à `inactive-count == 0`, puis appelle
`activate-by-type`. Mettre à 0 les want-counts civils/tête-de-métal draine ces pools, les masquant
du tirage pour qu'il tombe sur `{6, 7}` — les deux pools de gardes — presque à chaque fois.

**Les transitions de quartier doivent être INCRÉMENTALES — jamais un flush en une frame.** La
première version faisait tout le renouvellement sur la frame du changement de zone : kill dur des
trois pools de gardes + `deactivate-by-type` de tous les types civils / tête-de-métal / véhicules
civils / vaisseaux + `fast-spawn` (→ `spawn-all` fait 120 spawns). Cette frame coïncide souvent
avec le démontage du niveau de ville sortant (`level-unlink`, nettoyage des process) — le brassage
massif de process plus l'allocation `nav-max-users` (à tort) relevée débordaient un buffer fixe /
le tas loading-level → **crash brutal, aucune erreur GOAL, log qui s'arrête en pleine frame à
`kill #<level active ctysluma>`**. Même famille de panne que le piège `sphere-in-grid?` du §1.

Fais-le plutôt quelques opérations par frame :

```lisp
;; chaque frame, après le modelage want/target : retire <=2 gardes de la mauvaise faction par pool
(mod-city-guard-pool-reconcile this (traffic-type crimson-guard-1) zone 2)
(mod-city-guard-pool-reconcile this (traffic-type crimson-guard-2) zone 2)
;; reconcile : tue <=budget gardes INACTIFS de la mauvaise faction (get-from-inactive-by-handle +
;;             reserve-- + deactivate) ; s'il reste du budget, parque autant de gardes ACTIFS
;;             (deactivate-object force -> repasse inactif, tué la frame suivante). No-op si pur.
```

`kill-excess-once` (déjà dans `traffic-manager::update`) draine les pools civils / vaisseaux à
want 0 à raison de 1/frame ; `spawn-all` (sans `fast-spawn`) remplit les pools de gardes 1/frame
avec la bonne faction via le choix de faction au spawn (§2) ; la passe reconcile retire la faction
sortante 2/frame. Net : la rue fait un fondu enchaîné sur ~1-2 s, et aucune frame ne fait plus
qu'une poignée d'opérations sur des process, donc ça ne peut pas entrer en course avec une
transition de niveau. Les civils actifs que reconcile ne touche pas se drainent en quittant la
grille de visibilité de Jak (`update-traffic-amount` désactive le trafic hors grille) — quelques
secondes, pas instantané, et seulement une fois à l'entrée.

**Piège :** rien d'autre n'écrit `want-count` au runtime, donc une réécriture par frame est sûre —
mais garde un flag « était en train de modeler » pour restaurer exactement une fois quand le mode
s'éteint.

---

## 4. Combat garde contre garde autonome, sans effet sur le niveau de recherche de Jak

Deux faits rendent ça propre :

1. **`traffic-engine::increase-alert-level` ne fait rien à moins que l'attaquant porte
   `process-mask target`** (c.-à-d. Jak). Les attaques garde contre garde ne passent jamais Jak
   comme attaquant, donc le niveau de recherche ne peut pas monter à cause d'un combat de
   factions — aucun cas particulier pour l'alarme elle-même.
2. **`incoming attacker-handle` remonte déjà d'un projectile vers son tireur.**
   `find-offending-process-focusable` (`process-drawable.gc`) parcourt la chaîne parente du
   process de l'attaque, et les tirs de garde (`crimson-guard-method-214`,
   `spawn-projectile ... this ...`) parentent le projectile au garde tireur. Donc un handler
   `'hit` peut type-checker `incoming attacker-handle` directement — corps à corps *et* tir — pour
   voir qui l'a vraiment touché.

Le hook d'acquisition (un seul helper conscient de la faction, sûr dans les états partagés qu'un
sous-type hérite) :

```lisp
(defun crimson-guard-insurrection-scan ((this crimson-guard))
  (when (and *mod-city-insurrection?* (= (city-get-pos-zone (-> this root trans)) 'conflict))
    ;; search-blue? = #t pour un garde rouge (chasse bleu), #f pour un garde bleu (chasse rouge)
    (let ((foe (find-nearest-enemy-guard this (not (type-type? (-> this type) crimson-blue-guard)) (meters 60))))
      (when foe
        (set! (-> this traffic-target-status handle) (process->handle foe))
        (try-update-focus (-> this focus) foe this)
        (go-hostile this)))))     ;; n'appelle jamais trigger-alert / increase-alert-level
```

**La portée d'acquisition** était de 40 m dans la première version et donnait l'impression que les
gardes ignoraient des ennemis visibles de l'autre côté de la rue ; `(meters 60)` est une ligne de
vue de zone de guerre le long d'un bloc industriel. Même valeur dans
`crimson-blue-guard-attack-guards`.

`find-nearest-enemy-guard` (`guard.gc`) parcourt les listes d'objets actifs du traffic-engine et
filtre par `type-type?`. Appelle le hook depuis `active:trans` **et** `search:trans` — un garde
qui perd un ennemi dans `search` doit en réacquérir un ou retourner en `active`, sinon le `search`
d'origine (qui dépend de `traffic-target-flag visible-recently`, seul maintenu pour Jak) peut le
laisser marcher indéfiniment.

> **Piège critique — les deux trackers de trafic ont des noms inversés dans le décomp.**
> `traffic-engine` a `tracker-array` (2 `traffic-tracker` inline). Le décomp alie
> `citizen-tracker-array` sur `tracker-array[0]` et `vehicle-tracker-array` sur `tracker-array[1]`
> — **mais les contenus sont inversés** : les piétons et les gardes (traffic-types `0..10`) sont
> dans `vehicle-tracker-array` / `tracker-array[1]`, et les véhicules (`11..20`) dans
> `citizen-tracker-array` / `tracker-array[0]`. Preuve : `traffic-engine::child-killed` route un
> `citizen` vers `vehicle-tracker-array` et un `vehicle` vers `citizen-tracker-array` ; les noms
> de méthodes `activate-one-citizen` / `activate-one-vehicle` sont inversés pareil. La première
> version de ce mod scannait `citizen-tracker-array` pour les gardes, ne trouvait que des
> véhicules, et **n'avait aucun combat inter-factions**. Scanne `(-> engine tracker-array tk)` pour
> `tk` dans `0..1` et tu n'as pas à savoir quel alias est quel.

**La riposte réciproque** vit dans le handler `'hit` de la victime : résous l'attaquant, et si
c'est la faction opposée, `try-update-focus` + `go-hostile` directement dessus — saute le cri
`speech-control` « repéré ! » et l'appel `trigger-alert` que ferait le chemin d'origine.

---

## 5. Zone refuge de police / zones sans alerte — un seul point de passage

`increase-alert-level` est le *seul* endroit où le niveau d'alerte monte (événement du menu,
`citizen::trigger-alert` qui l'appelle directement, et l'escalade par nombre de morts dans
`update-alert-state` passent tous par lui). Verrouille-le pour que **seuls les quartiers
loyalistes** appliquent le système de recherche — les Slums *et* la zone de guerre sont sans
alerte (donc frapper un garde rouge dans la zone de guerre ne déclenche rien) :

```lisp
(defmethod increase-alert-level ((this traffic-engine) (arg0 int) (arg1 target))
  (when (not (and *mod-city-insurrection?*
                  (let ((z (city-get-current-zone))) (or (= z 'blue) (= z 'conflict)))))
    ... corps d'origine ...))
```

Puis aussi `(set-alert-level engine 0)` à chaque frame où Jak est dans une zone sans alerte, pour
qu'une alerte qu'il *amène* retombe immédiatement (note : `decrease-alert-level` prend un
*plancher* — `(min level arg)` — donc passer `4` ne fait rien ; utilise `set-alert-level` ou
`decrease-alert-level 0`).

---

## 6. Appliquer les changements de mode / config aux gardes déjà présents

`send-event *traffic-manager* 'deactivate-by-type <n>` parque tous les process actifs d'un type
(ils passent inactifs, pas tués) ; le générateur reconstruit selon les règles courantes sur la
seconde ou deux qui suit. C'est sûr **uniquement depuis une pick-func du menu debug** — une action
explicite de l'utilisateur, jamais pendant une transition de niveau. Envoie-le pour les pools de
gardes (`4`, `6`, `7`) et les vaisseaux (`18`, `19`) depuis les bascules de mode et le sélecteur
de quartier de guerre pour que faction / escouade / arme / composition de zone se re-tirent vite.

Ne **pas** faire ça à un *changement de quartier* — ça se déclenche pendant le démontage du niveau
sortant et une grosse rafale de `deactivate-by-type` là crashe le jeu (§3). Un changement de
quartier repose uniquement sur la réconciliation par frame du §3 : modelage `want-count` /
`target-count` + `mod-city-guard-pool-reconcile` (≤2 retraits de mauvaise faction par pool par
frame) + `kill-excess-once` + `spawn-all`, tout borné à une poignée d'opérations process par frame.

Un sélecteur de menu type radio sur une valeur de config symbole est une seule pick-func `flag`
partagée — le 3e élément du template de menu est passé à la pick-func comme `arg0`, donc encode le
choix dedans :

```lisp
'(menu "Insurrection war zone"
   (flag "Industrial (default)" industrial dm-mod-city-conflict-district-pick-func)
   (flag "Port"                 port       dm-mod-city-conflict-district-pick-func)
   ...)

(defun dm-mod-city-conflict-district-pick-func ((arg0 symbol) (arg1 debug-menu-msg))
  (when (= arg1 (debug-menu-msg press))
    (set! *mod-city-conflict-district* arg0)
    (dm-mod-city-flush-guards))
  (= *mod-city-conflict-district* arg0))   ;; retour -> coche sur la ligne courante
```

---

## Antériorité — le système de factions de Jak 3

Jak 3 livre une guerre de factions complète pour la même géométrie de ville (CWI) :
`cty-faction-h.gc` (`cty-faction-manager`, `nav-territory-type` avec sous-zones deep/border par
faction, force par territoire), et `kg-squad-control` / `mh-squad-control` / `ff-squad-control`
avec `hatred-memory` par membre. C'est le design canonique, bien plus lourd, et il dépend de
métadonnées de territoire du nav-graph de jak3 que la ville de jak2 n'a pas — d'où l'approche
légère position→zone→hook-IA ci-dessus. Si tu portes un jour ce système, commence par
`cty-faction-h.gc`.

---
*(AI-assisted)*
