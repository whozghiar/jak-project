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
**fight each other autonomously in the background** without touching Jak's wanted level, and make a
district a **police safe haven**. Worked example: the *City Insurrection* mode of the
`crimson-blue-guard` mod (full writeup: `docs/modding/current_mod/blue_guard_reskin_readme.md`).

Files touched: `traffic-manager.gc`, `traffic-engine.gc`, `guard.gc`, `pc/debug/default-menu-pc.gc`.

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

Verified Jak 2 city level names (`level-info.gc`): Slums = `ctysluma`, `ctyslumb`, `ctyslumc`;
Industrial = `ctyinda`, `ctyindb`; everything else (Port `ctyport`, downtown `ctygena/b/c`, Farms
`ctyfarma/b`, Bazaar `ctymarka/b`, Palace, Stadium, …) is a loyalist district.

`city-get-pos-zone` maps the name → `'blue` / `'conflict` / `'red`, with a bsphere-nearest-level
fallback for the rare case where the grid lookup can't resolve `pos`. `city-get-current-zone`
does the same for Jak, falling back to `(-> *load-state* vis-nick)` when `*target*` is `#f`.

**Pitfall:** `sphere-in-grid?`'s cell flags are only maintained for the ≤2 traffic-tracked city
levels near Jak. That is exactly the scope you want for spawn points and for Jak, so it's fine —
just keep the bsphere fallback for everything else.

---

## 2. Strict per-district faction spawning — one pool, faction chosen by district

Ambient guards come from **one** traffic type: `crimson-guard-1` (6), the stock ambient guard
pool (base `want-count` 9) that the alert system already drives. (`crimson-guard-0` (4) exists but
is barely wired into stock ambient traffic — `activate-by-type` fills its pool yet never reliably
promotes it — so don't build on it; leave it at `want-count` 0.)

**Two traps to avoid:**

1. *Filtering a shared 50/50 pool per district.* Have `activate-from-params` scan the inactive
   list for the wanted faction and skip the spawn when it's absent. In a strict district **half
   the pool is the wrong faction and can never activate** → effective density silently drops ~50%
   (the "where did the red guards go?" bug). A recycled process also keeps its type, so a shared
   pool can never become *purely* one faction.
2. *Splitting the factions across `crimson-guard-0` / `crimson-guard-1`.* Clean in theory, but
   `crimson-guard-0` never activates as ambient traffic — you get a full inactive pool and zero
   guards on the street.

**What works: keep the single `crimson-guard-1` pool, and pick the concrete process type per
spawn from the district Jak is in.** Cache the district each frame (see §3) so the spawner can
read it cheaply:

```lisp
;; traffic-object-spawn (traffic-manager.gc), crimson-guard-1 branch:
(let ((spawn-blue?
        (cond
          (*mod-city-insurrection?*
           (case *mod-city-guard-zone*        ;; cached by the per-frame shaper
             (('blue) #t)                     ;; Slums: rebel stronghold
             (('conflict) (zero? (rand-vu-int-count 2)))   ;; Industrial: 50/50 roll
             (else #f)))                      ;; Loyalist: stock red
          (else (logtest? (-> arg1 id) 1)))))  ;; non-Insurrection: id-parity mix
  (set! v0-0 (citizen-spawn arg0 (if spawn-blue? crimson-blue-guard crimson-guard) arg1)))
```

`activate-from-params` then needs **no** faction logic under Insurrection —
`(get-from-inactive-by-type this gp-0)` activates whatever the pool holds, and the pool is already
100% the right faction. On a **district change**, purge and refill the pool (§6) so it isn't left
holding the previous district's faction. Keep the old id-parity + `activate-from-params`
faction-pick path for the **non-Insurrection** modes (City Peaceful = every guard blue, stock
ambient = 1-in-`*crimson-blue-guard-ratio*` blue), where a mixed pool is what you want.

---

## 3. Remove civilians / vehicles from a district — live `want-count`

`want-count` (per `traffic-object-type-info`, set once in `traffic-manager::init-params`) is the
ambient spawner's density lever: `kill-excess-once` deactivates anything over it and `spawn-all`
stops topping a type up. Edit it **every frame** from `traffic-manager::update` (before the
kill/spawn pass) based on the current zone, restoring from a captured baseline otherwise:

```lisp
;; static mirror of the init-params values -- single restore source
(define *traffic-want-count-base*
  (new 'static 'boxed-array :type int8 15 15 14 1 1 0 9 0 14 14 14 8 8 8 7 7 7 0 8 8 0))

;; in update, before (kill-excess-once) / (spawn-all): reset all 21, then shape for the district
(dotimes (i 21) (set! (-> engine object-type-info-array i want-count) (-> *traffic-want-count-base* i)))
(set! (-> engine object-type-info-array 4 want-count) 0)   ;; crimson-guard-0 unused (see §2)
(case (city-get-current-zone)
  (('blue)      ;; Slums: lone blue rebels, no loyalist gunships
   (set! (-> engine object-type-info-array 6 want-count) 10)
   (set! (-> engine object-type-info-array 6 target-count) 7)
   (set! (-> engine object-type-info-array 18 want-count) 0)
   (set! (-> engine object-type-info-array 19 want-count) 0))
  (('conflict)  ;; Industrial: dense, no civilians (0..3), no vehicles (11..19)
   (set! (-> engine object-type-info-array 6 want-count) 18)
   (set! (-> engine object-type-info-array 6 target-count) 14)
   (dotimes (i 4) (set! (-> engine object-type-info-array i want-count) 0))
   (dotimes (i 9) (set! (-> engine object-type-info-array (+ i 11) want-count) 0)))
  (else         ;; Loyalist: stock red police -- pool left fully vanilla (no want/target override)
   0))
```

Traffic types (`traffic-h.gc`): `0..3` citizens, `4`/`6`/`7` crimson-guard pools, `8..10`
metal-heads, `11..16` civilian bikes/cars, `18` guard-bike, `19` hellcat.

**Two levers, not one — `want-count` sizes the pool, `target-count` gates activation.** `want-count`
only controls how many processes `spawn-all` pre-creates (inactive pool). What actually walks the
street is capped by `object-type-info-array <type> target-count`, which `activate-by-type` checks
(`active-count < target-count`). For the guard type, `update-alert-state` **recomputes
`target-count` every frame** from `*alert-level-settings*[level]` (at peace, rifle/grenade guards
are 0 → only ~5 taser guards). So to run a denser battle you must **also** force `target-count`,
*after* `update-traffic` has run — i.e. from `traffic-manager::update`, which is already after it,
so your value is what `activate-by-type` sees next frame. In the Loyalist districts, force
**neither** lever: leave the guard pool completely vanilla and the stock alert-scaled police
response is preserved byte-for-byte. Zeroing the citizen want-counts also shifts
`activate-one-vehicle`'s random ped/guard roll toward guards (types with 0 inactive are masked out
of the pick).

**Snappy district transitions:** track the last-shaped zone; when it changes, `deactivate-by-type`
the guard pools (4, 6) and loyalist gunships (18, 19) so `kill-excess-once` can drain the
departing faction from the *active* list (not just inactive), and set `traffic-manager fast-spawn`
so `spawn-all` refills the new faction in one frame.

**Pitfall:** nothing else writes `want-count` at runtime, so a per-frame rewrite is safe — but
track a "was shaping" flag so you restore exactly once when the mode turns off, instead of fighting
other code every frame forever.

---

## 4. Autonomous guard-vs-guard combat with zero effect on Jak's wanted level

Two facts make this clean:

1. **`traffic-engine::increase-alert-level` is a no-op unless the attacker carries
   `process-mask target`** (i.e. Jak). Guard-vs-guard attacks never pass Jak as the attacker, so
   the wanted level simply cannot rise from a faction fight. No special-casing needed for the
   alarm itself.
2. **`incoming attacker-handle` already resolves a projectile to its firer.**
   `find-offending-process-focusable` (`process-drawable.gc`) walks the attack's process parent
   chain, and guard shots (`crimson-guard-method-214`, `spawn-projectile ... this ...`) parent the
   projectile to the firing guard. So a `'hit` handler can type-check `incoming attacker-handle`
   directly — for melee *and* ranged — to see who really hit it.

The acquisition hook (one faction-aware helper, safe in shared states a subtype inherits):

```lisp
(defun crimson-guard-insurrection-scan ((this crimson-guard))
  (when (and *mod-city-insurrection?* (= (city-get-pos-zone (-> this root trans)) 'conflict))
    ;; search-blue? = #t for a red guard (hunts blue), #f for a blue guard (hunts red)
    (let ((foe (find-nearest-enemy-guard this (not (type-type? (-> this type) crimson-blue-guard)) (meters 40))))
      (when foe
        (set! (-> this traffic-target-status handle) (process->handle foe))
        (try-update-focus (-> this focus) foe this)
        (go-hostile this)))))     ;; never calls trigger-alert / increase-alert-level
```

`find-nearest-enemy-guard` (`guard.gc`) walks the traffic-engine's active-object lists and filters
by `type-type?`. Call the hook from **both** `active:trans` and `search:trans` — a guard that loses
a foe in `search` must re-acquire or drop back to `active`, otherwise stock `search` (which keys
off `traffic-target-flag visible-recently`, only maintained for Jak) can leave it walking forever.

> **Critical pitfall — the two traffic trackers are named backwards in the decomp.**
> `traffic-engine` has `tracker-array` (2 inline `traffic-tracker`s). The decomp aliases
> `citizen-tracker-array` onto `tracker-array[0]` and `vehicle-tracker-array` onto
> `tracker-array[1]` — **but the contents are the other way round**: pedestrians and guards
> (traffic-types `0..10`) live in `vehicle-tracker-array` / `tracker-array[1]`, and vehicles
> (`11..20`) live in `citizen-tracker-array` / `tracker-array[0]`. Proof: `traffic-engine::child-killed`
> routes a `citizen` to `vehicle-tracker-array` and a `vehicle` to `citizen-tracker-array`; the
> `activate-one-citizen` / `activate-one-vehicle` method names are swapped the same way.
> The first cut of this mod scanned `citizen-tracker-array` for guards, found only vehicles, and
> **got zero inter-faction combat**. Scan `(-> engine tracker-array tk)` for `tk` in `0..1` and
> you don't have to care which alias is which.

**Reciprocal retaliation** lives in the victim's `'hit` handler: resolve the attacker, and if it's
the opposing faction, `try-update-focus` + `go-hostile` on it directly — skip the
`speech-control` "spotted!" bark and the `trigger-alert` call the stock path would do.

---

## 5. Police safe haven — one choke point

`increase-alert-level` is the *single* place the alert level goes up (menu event,
`citizen::trigger-alert` calling it directly, and the kill-count escalation in
`update-alert-state` all route through it). Guard it:

```lisp
(defmethod increase-alert-level ((this traffic-engine) (arg0 int) (arg1 target))
  (when (not (and *mod-city-insurrection?* (= (city-get-current-zone) 'blue)))
    ... stock body ...))
```

Then also `(set-alert-level engine 0)` each frame Jak is in the safe zone, so an alert he
*carried in* drops immediately (note: `decrease-alert-level` takes a *floor* — `(min level arg)` —
so passing `4` does nothing; use `set-alert-level` or `decrease-alert-level 0`).

---

## 6. Apply mode changes to guards already spawned

`send-event *traffic-manager* 'deactivate-by-type <n>` flushes a traffic type; the spawner
rebuilds it from scratch within seconds under the current rules. Flush the guard pools (`4`, `6`)
and guard vehicles (`18`, `19`) from the debug-menu pick-func so faction / squad / weapon / zone
composition all re-roll immediately, and do the same on a district change (see §3). It is a
one-shot nudge — the *persistent* per-district composition is carried by the per-frame `want-count`
shaping in §3, which `kill-excess-once` + `spawn-all` enforce every frame regardless.

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
recherche de Jak, et faire d'un quartier une **zone refuge de police**. Exemple concret : le mode
*City Insurrection* du mod `crimson-blue-guard` (rédaction complète :
`docs/modding/current_mod/blue_guard_reskin_readme.md`).

Fichiers modifiés : `traffic-manager.gc`, `traffic-engine.gc`, `guard.gc`,
`pc/debug/default-menu-pc.gc`.

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

Noms de niveaux de ville Jak 2 vérifiés (`level-info.gc`) : Slums = `ctysluma`, `ctyslumb`,
`ctyslumc` ; Industriel = `ctyinda`, `ctyindb` ; tout le reste (Port `ctyport`, centre-ville
`ctygena/b/c`, Fermes `ctyfarma/b`, Bazar `ctymarka/b`, Palais, Stade, …) est un quartier
loyaliste.

`city-get-pos-zone` mappe le nom → `'blue` / `'conflict` / `'red`, avec un repli sur le niveau de
ville actif le plus proche (bsphere) pour le cas rare où la recherche par grille échoue.
`city-get-current-zone` fait pareil pour Jak, avec repli sur `(-> *load-state* vis-nick)` quand
`*target*` est `#f`.

**Piège :** les flags de cellule de `sphere-in-grid?` ne sont maintenus que pour les ≤2 niveaux de
ville suivis par le trafic autour de Jak. C'est exactement la portée voulue pour les points de
spawn et pour Jak — garde juste le repli bsphere pour le reste.

---

## 2. Spawn de faction strict par quartier — un seul pool, faction choisie par quartier

Les gardes ambiants viennent d'**un seul** traffic-type : `crimson-guard-1` (6), le pool de gardes
ambiants d'origine (`want-count` de base 9), celui que le système d'alerte pilote déjà.
(`crimson-guard-0` (4) existe mais est à peine branché au trafic ambiant d'origine —
`activate-by-type` remplit son pool mais ne l'active jamais de façon fiable — donc ne construis
rien dessus ; laisse-le à `want-count` 0.)

**Deux pièges à éviter :**

1. *Filtrer un pool partagé 50/50 par quartier.* Faire scanner la liste inactive par
   `activate-from-params` pour la faction voulue et sauter le spawn quand elle est absente. Dans un
   quartier strict, **la moitié du pool est la mauvaise faction et ne peut jamais s'activer** → la
   densité effective chute de ~50 % (le bug « où sont passés les gardes rouges ? »). Un process
   recyclé garde aussi son type, donc un pool partagé ne peut jamais devenir *purement* d'une
   faction.
2. *Séparer les factions sur `crimson-guard-0` / `crimson-guard-1`.* Propre en théorie, mais
   `crimson-guard-0` ne s'active jamais en trafic ambiant — pool inactif plein, zéro garde en rue.

**Ce qui marche : garder le pool unique `crimson-guard-1` et choisir le type de process concret à
chaque spawn selon le quartier de Jak.** Mémorise le quartier chaque frame (voir §3) pour que le
générateur le lise à moindre coût :

```lisp
;; traffic-object-spawn (traffic-manager.gc), branche crimson-guard-1 :
(let ((spawn-blue?
        (cond
          (*mod-city-insurrection?*
           (case *mod-city-guard-zone*        ;; mis en cache par le modeleur par-frame
             (('blue) #t)                     ;; Slums : bastion rebelle
             (('conflict) (zero? (rand-vu-int-count 2)))   ;; Industriel : tirage 50/50
             (else #f)))                      ;; Loyaliste : rouge d'origine
          (else (logtest? (-> arg1 id) 1)))))  ;; hors Insurrection : mélange parité-id
  (set! v0-0 (citizen-spawn arg0 (if spawn-blue? crimson-blue-guard crimson-guard) arg1)))
```

`activate-from-params` n'a alors besoin d'**aucune** logique de faction sous Insurrection —
`(get-from-inactive-by-type this gp-0)` active ce que le pool contient, et le pool est déjà 100 %
la bonne faction. Au **changement de quartier**, vide et recharge le pool (§6) pour qu'il ne reste
pas la faction du quartier précédent. Garde l'ancien chemin parité-id + filtre-faction de
`activate-from-params` pour les modes **hors Insurrection** (City Peaceful = tous les gardes bleus,
ambiant d'origine = 1-sur-`*crimson-blue-guard-ratio*` bleu), où un pool mixte est ce qu'on veut.

---

## 3. Retirer les civils / véhicules d'un quartier — `want-count` en direct

`want-count` (par `traffic-object-type-info`, défini une fois dans
`traffic-manager::init-params`) est le levier de densité du générateur ambiant :
`kill-excess-once` désactive tout ce qui dépasse et `spawn-all` arrête de remplir un type.
Modifie-le **à chaque frame** depuis `traffic-manager::update` (avant la passe kill/spawn) selon
la zone courante, en restaurant depuis une base capturée sinon :

```lisp
;; miroir statique des valeurs d'init-params -- source unique de restauration
(define *traffic-want-count-base*
  (new 'static 'boxed-array :type int8 15 15 14 1 1 0 9 0 14 14 14 8 8 8 7 7 7 0 8 8 0))

;; dans update, avant (kill-excess-once) / (spawn-all) : reset des 21, puis modelage du quartier
(dotimes (i 21) (set! (-> engine object-type-info-array i want-count) (-> *traffic-want-count-base* i)))
(set! (-> engine object-type-info-array 4 want-count) 0)   ;; crimson-guard-0 inutilisé (voir §2)
(case (city-get-current-zone)
  (('blue)      ;; Slums : rebelles bleus solitaires, pas de vaisseaux loyalistes
   (set! (-> engine object-type-info-array 6 want-count) 10)
   (set! (-> engine object-type-info-array 6 target-count) 7)
   (set! (-> engine object-type-info-array 18 want-count) 0)
   (set! (-> engine object-type-info-array 19 want-count) 0))
  (('conflict)  ;; Industriel : dense, pas de civils (0..3), pas de véhicules (11..19)
   (set! (-> engine object-type-info-array 6 want-count) 18)
   (set! (-> engine object-type-info-array 6 target-count) 14)
   (dotimes (i 4) (set! (-> engine object-type-info-array i want-count) 0))
   (dotimes (i 9) (set! (-> engine object-type-info-array (+ i 11) want-count) 0)))
  (else         ;; Loyaliste : police rouge d'origine -- pool 100% vanilla (aucun override want/target)
   0))
```

Types de trafic (`traffic-h.gc`) : `0..3` civils, `4`/`6`/`7` pools crimson-guard, `8..10`
têtes-de-métal, `11..16` motos/voitures civiles, `18` guard-bike, `19` hellcat.

**Deux leviers, pas un — `want-count` dimensionne le pool, `target-count` gate l'activation.**
`want-count` ne contrôle que le nombre de process pré-créés par `spawn-all` (pool inactif). Ce qui
marche réellement dans la rue est plafonné par `object-type-info-array <type> target-count`, que
`activate-by-type` vérifie (`active-count < target-count`). Pour le type garde,
`update-alert-state` **recalcule `target-count` chaque frame** depuis `*alert-level-settings*[level]`
(en paix, les gardes fusil/grenade sont à 0 → seulement ~5 gardes taser). Donc pour une bataille
plus dense il faut **aussi** forcer `target-count`, *après* que `update-traffic` a tourné — donc
depuis `traffic-manager::update`, qui est déjà après, pour que ta valeur soit celle que voit
`activate-by-type` à la frame suivante. Dans les quartiers loyalistes, ne force **aucun** levier :
laisse le pool de gardes complètement vanilla et la réponse policière échelonnée par l'alerte est
préservée à l'identique. Mettre les want-counts civils à 0 décale aussi le tirage piéton/garde de
`activate-one-vehicle` vers les gardes (les types à 0 inactif sont masqués).

**Transitions de quartier réactives :** mémorise la dernière zone modelée ; au changement,
`deactivate-by-type` sur les pools de gardes (4, 6) et les vaisseaux loyalistes (18, 19) pour que
`kill-excess-once` puisse drainer la faction quittée depuis la liste *active* (pas seulement
inactive), et met `traffic-manager fast-spawn` pour que `spawn-all` remplisse la nouvelle faction
en une frame.

**Piège :** rien d'autre n'écrit `want-count` au runtime, donc une réécriture par frame est sûre —
mais garde un flag « était en train de modeler » pour restaurer exactement une fois quand le mode
s'éteint.

---

## 4. Combat garde contre garde autonome, sans effet sur le niveau de recherche de Jak

Deux faits rendent ça propre :

1. **`traffic-engine::increase-alert-level` ne fait rien à moins que l'attaquant porte
   `process-mask target`** (c.-à-d. Jak). Les attaques garde contre garde ne passent jamais Jak
   comme attaquant, donc le niveau de recherche ne peut simplement pas monter à cause d'un combat
   de factions. Aucun cas particulier nécessaire pour l'alarme elle-même.
2. **`incoming attacker-handle` remonte déjà d'un projectile vers son tireur.**
   `find-offending-process-focusable` (`process-drawable.gc`) parcourt la chaîne parente du
   process de l'attaque, et les tirs de garde (`crimson-guard-method-214`,
   `spawn-projectile ... this ...`) parentent le projectile au garde tireur. Donc un handler
   `'hit` peut type-checker `incoming attacker-handle` directement — pour le corps à corps *et* le
   tir à distance — pour voir qui l'a vraiment touché.

Le hook d'acquisition (un seul helper conscient de la faction, sûr dans les états partagés qu'un
sous-type hérite) :

```lisp
(defun crimson-guard-insurrection-scan ((this crimson-guard))
  (when (and *mod-city-insurrection?* (= (city-get-pos-zone (-> this root trans)) 'conflict))
    ;; search-blue? = #t pour un garde rouge (chasse bleu), #f pour un garde bleu (chasse rouge)
    (let ((foe (find-nearest-enemy-guard this (not (type-type? (-> this type) crimson-blue-guard)) (meters 40))))
      (when foe
        (set! (-> this traffic-target-status handle) (process->handle foe))
        (try-update-focus (-> this focus) foe this)
        (go-hostile this)))))     ;; n'appelle jamais trigger-alert / increase-alert-level
```

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

## 5. Zone refuge de police — un seul point de passage

`increase-alert-level` est le *seul* endroit où le niveau d'alerte monte (événement du menu,
`citizen::trigger-alert` qui l'appelle directement, et l'escalade par nombre de morts dans
`update-alert-state` passent tous par lui). Verrouille-le :

```lisp
(defmethod increase-alert-level ((this traffic-engine) (arg0 int) (arg1 target))
  (when (not (and *mod-city-insurrection?* (= (city-get-current-zone) 'blue)))
    ... corps d'origine ...))
```

Puis aussi `(set-alert-level engine 0)` à chaque frame où Jak est dans la zone refuge, pour
qu'une alerte qu'il *amène* retombe immédiatement (note : `decrease-alert-level` prend un
*plancher* — `(min level arg)` — donc passer `4` ne fait rien ; utilise `set-alert-level` ou
`decrease-alert-level 0`).

---

## 6. Appliquer les changements de mode aux gardes déjà présents

`send-event *traffic-manager* 'deactivate-by-type <n>` vide un type de trafic ; le générateur le
reconstruit de zéro en quelques secondes selon les règles courantes. Vide les pools de gardes
(`4`, `6`) et les vaisseaux de gardes (`18`, `19`) depuis la pick-func du menu debug pour que
faction / escouade / arme / composition de zone se retirent au sort immédiatement, et fais pareil
au changement de quartier (voir §3). C'est un coup de pouce ponctuel — la composition *persistante*
par quartier est portée par le modelage `want-count` par frame du §3, que `kill-excess-once` +
`spawn-all` imposent chaque frame de toute façon.

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
