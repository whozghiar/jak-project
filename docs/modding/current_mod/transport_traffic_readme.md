# Crimson Guard Air-Traffic Gunship — Mod Readme / Canonnière du Trafic Aérien — Readme de Mod

> - **Branch / Branche :** `jak2/features/transport_traffic`
> - **Game / Jeu :** Jak II (OpenGOAL)
> - **Status / Statut :** Working — `transport-v`, a drivable `vehicle-guard` in Haven City's ambient AIR traffic / Fonctionnel — `transport-v`, un `vehicle-guard` pilotable dans le trafic AÉRIEN ambiant d'Abriville
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

## 🇬🇧 English Version

### 1. Overview & Objective

`transport-v` is a **real air-traffic vehicle**: a `vehicle-guard` subtype (sibling of `hellcat` / `guard-bike`) that spawns in Haven City's ambient traffic pool, flies the city nav-lanes, shows a **red dot on the minimap**, is **guard-piloted** (seated), can be **boarded and driven by the player** with a **usable turret**, and can be **shot down** like any guard vehicle.

During a city alert it joins the pursuit like a hellcat and, while over solid ground, **drops one aerial level, deploys a squad of Crimson Guards, then climbs back to the normal lane and guns for Jak**.

This is the sibling branch of `jak2/features/transport_alert` (the scripted, non-interactive alert drop-ship). They share only the `.fr3` merc-geometry injection that makes the transport hull renderable in free-roam.

### 2. Why `vehicle-guard` / `hellcat` is the base

Almost every requirement is already implemented on `vehicle-guard`:

| Requirement | Inherited from | Mechanism |
|---|---|---|
| Guard pilot | `vehicle-guard::vehicle-method-137` | spawns a `crimson-guard-rider` (traffic sets `trsflags-01` + `behavior 1` on every pooled vehicle → a hidden rider, shown on `'traffic-on`). `transport-v` sets `rider-stance` = 0 so it is **seated**, not gripping handlebars. |
| Red dot on the minimap | `vehicle-guard::vehicle-method-128` | `add-icon! *minimap* … (minimap-class guard)` — icon 14, the red guard marker |
| Follows the ship nav-path | `vehicle` + `vehicle-controller` + `vehicle-guard-choose-branch` | activated onto a city nav-segment (`behavior` 2), follows nav-branches; altitude from `*traffic-height-map*` |
| Flies like a hellcat | cloned `*hellcat-constants*` | the flight model is a **byte-for-byte `mem-copy!` of `*hellcat-constants*`** — mass, inertial tensor, `cm-offset-joint`, thrust, speed, every `*-thruster-array` / `stabilizer-array` |
| Hostile pursuit during alerts | `vehicle-guard` `hostile` / `stop-and-shoot` states | slot 20 gets `trtflags-0` in `restore-default-settings`, so alerts notify it |
| Player boards & drives | `vehicle` `check-player-get-on` | same as any traffic car/hellcat; the guard pilot is knocked off (`target-pilot` handles `crimson-guard-rider` in any seat) |
| Player fires the turret | `transport-v::vehicle-method-94` → `transport-v-fire-turret` | hold **R1** while piloting → the **visible chin gun** aims down the nose and fires `guard-shot` from its real muzzle joint |

### 3. What is new (`car.gc`, appended after `hellcat`)

- **`skel-transport-v`** — a `defskelgroup` over the `transport` art group whose **far LOD reuses `transport-lod1-mg`** instead of the empty `transport-lod2-mg` (so an ambient ship never vanishes at distance).
- **`*transport-v-constants*`** — a runtime `mem-copy!` of `*hellcat-constants*`. Only NON-flight fields change: `object-type` 20; **constants-flag bit 3 cleared** (sphere-only collision → `alloc-and-init-rigid-body-control` writes `jak`/`player-list` into every prim, so the player collides with the hull); chase-camera pulled well back (string length 20–36 m, height 13–15 m) for the ~17 m hull; bigger rear engine flames; `rider-stance` 0 (seated); hull-height seats.
- **`*transport-v-*` tuning `define`s** (all REPL-editable): `*transport-v-drop-interval*` (4 s between drops), `*transport-v-max-drop*` (5 guards per traffic-life), `*transport-v-deploy-descent*` (10 m altitude drop while deploying), `*transport-v-deploy-spin-damp*` (0.82 — angular-momentum retention per frame while deploying), `*transport-v-turret-fire-interval*` (0.3 s), `*transport-v-turret-muzzle-z*` (2 m muzzle push).
- **Visible chin turret** — a `vehicle-turret` child (retail `transport.gc` model + `*transport-turret-control-info*`, `vehicle-turret-ag` baked into the always-resident `ctywide.fr3`). `transport-v` **aims** it (`turret-control-method-9` on the child, whose `idle` state applies the resulting `aim-rot` to the gun joint) and **fires** it through **`transport-v-fire-turret`** — a hand-rolled `guard-shot` spawn that parents *and* `ignore-handle`s the projectile to the hull, so the round leaves the muzzle instead of detonating on the transport's own `vehicle-sphere` prims. The child's built-in self-fire is never armed (its `target` handle is force-cleared each frame). The inherited hull `turret-control` is left uninitialised (`info` = 0).
- **Overrides:** `allocate-and-init-cshape` (7 spheres in joint-0 space, `rideable` root, one `nav-sphere` — mirrors retail `transport-method-31`), `init-skel-and-rigid-body` (spawns the chin turret, inits deploy state), `vehicle-guard-method-153` (AI turret aim + fire), `vehicle-method-94` (player R1), `vehicle-method-121` (silent descent bias + spin damping while deploying), `vehicle-method-128` (reset per-life deploy state on re-activation), `vehicle-method-129` (drop the turret on death), `update-joint-mods` (loading-hatch animation, keeps the child's self-fire disarmed), **`vehicle-guard-method-154`** (the deploy behaviour, see §4).
- **Traffic-type wiring:** `traffic-h.gc` renames the spare `(traffic-type 20)` → `transport-v`; `vehicle-h.gc` + `entity-h.gc` + `all-types.gc` add `(vehicle-type transport-v 11)`; `traffic-manager.gc` gets `traffic-object-spawn` + `type-from-vehicle-type` cases and `want-count[20]` = **2**; `guard.gc` adds object-type 20 to the "car" knock-off animation group; the mission scripts that `deactivate-by-type` slot 20 use the new name.

### 4. Alert behaviour — descend, deploy, then hunt

`vehicle-guard-method-154` (the per-frame pursuit tick), on top of the stock hellcat chase. The trigger is **`transport-v-deploy-active?`**, recomputed every frame = *alert up* **and** *over solid ground (not water)* **and** *`guards-dropped` < cap*.

- **While deploying:**
  - **Descent, silent.** `vehicle-method-121` subtracts `*transport-v-deploy-descent*` (10 m) from the height-map `flight-level`; the lift thrusters chase the lowered target. `flight-level-index` stays **1** for the ship's whole life — the earlier build used `switch-zone-low!`/`switch-zone-high!` here, which ping-ponged against the guard ai-hooks' per-frame `switch-zone-high!` and looped the "bike-down" sound.
  - **Stabilised, no spin.** The pursuit ai-hook's per-frame steering command is what makes the hull yaw-spin while it hovers to unload, so `vehicle-guard-method-154` zeroes `(-> this controls steering)` and `vehicle-method-121` bleeds `ang-momentum` / `ang-velocity` by `*transport-v-deploy-spin-damp*` each frame. The ship holds a steady attitude over the drop zone.
  - **Hatch open.** `update-joint-mods` seeks skeleton channel 0 to the last frame of `transport-hatch-open-ja`.
  - **Guards.** One `crimson-guard-1` every `*transport-v-drop-interval*` (`behavior` 6, alternating L/R), a straight port of retail `transport-method-33`.
- **Once the load is delivered** (`guards-dropped` reaches the cap) `transport-v-deploy-active?` goes false: the descent bias and the spin damping release together, the ship climbs back to the normal traffic lane, the hatch closes, and the stock guard chase + `vehicle-guard-method-153` turret fire take over — it hunts Jak like a hellcat with a gun.
- **Over water / no ground / alert over:** same as "done" — no descent, no drop, normal flight.
- `guards-dropped` is a **per-traffic-life** counter — it does not reset when an alert ends, only when a pooled transport is re-activated into traffic (`vehicle-method-128`). One deploy run per hull; the traffic pool cycles fresh ones.

### 5. Rendering — the merc geometry `.fr3` injection (shared with the sibling branch)

`transport-ag`'s hull geometry only ever shipped in `lprotect/ctykora/forestb/nest`. `extra_art_groups_by_dgo` in `decompiler/config/jak2/jak2_config.jsonc` bakes it into the always-resident `lwidea/lwideb/lwidec.fr3` (textures resolved via `LPROTECT`'s remap table); the matching `transport-ag.go` + `tpage-2869.go` entries are added to the three `lwide*.gd`. See [utility #18](../jak2_modding_utilities/18_merc_geometry_fr3_residency.md).

> **Requires a re-extraction** (`task extract`) so the three `.fr3` are rebuilt. The `vehicle-turret` chin gun needs none (retail `CWI.DGO`).

### 6. How to Test

1. **Extract (once):** `task extract` — rebuilds `lwide*.fr3` with `transport-ag`.
2. **Rebuild:** `task repl` then `(mi)` (the `traffic-manager` and `transport-v` deftypes — restart the REPL if `(mi)` complains).
3. **Launch:** `task boot-game`, enter Haven City free-roam.
4. **Ambient:** look up — occasionally a large twin-hull transport cruises the high air-lane above the hellcats, a seated Crimson Guard at the controls, red dot on the minimap. It should sit level and fly straight.
5. **Alert:** aggro a guard, stay in the transport's sight. It joins the hunt, then — over streets, not water — drops ~10 m **with no repeating sound**, **holds a steady heading (no spin)**, opens its hatch and drops 5 guards over ~20 s. Then it **climbs back to the normal lane, closes the hatch, and its chin gun tracks and fires at Jak** (tracers from the muzzle, never hitting the transport).
6. **Board it:** jump on (you land on the hull), the guard is knocked off, you pilot it seated — **the camera should sit well back so you see the whole ship**. Hold **R1** to fire the chin gun forward.
7. **Shoot one down:** it crashes and explodes like any guard vehicle; the chin turret goes with it.
8. From the REPL: `(send-event *traffic-manager* 'set-object-target-count (traffic-type transport-v) 4)` for more; live-tweak the `*transport-v-*` `define`s.

**Key source files:**

- `goal_src/jak2/levels/city/traffic/vehicle/car.gc` — `transport-v` type, `*transport-v-constants*`, the `*transport-v-*` `define`s, `transport-v-deploy-active?` / `transport-v-fire-turret` / `transport-v-drop-guard` / `transport-v-over-solid-ground?`, all method overrides, `skel-transport-v`.
- `goal_src/jak2/engine/ai/traffic-h.gc` — `(traffic-type transport-v 20)`.
- `goal_src/jak2/levels/city/traffic/vehicle/vehicle-h.gc`, `goal_src/jak2/engine/entity/entity-h.gc`, `decompiler/config/jak2/all-types.gc` — `(vehicle-type transport-v 11)`.
- `goal_src/jak2/levels/city/traffic/traffic-manager.gc` — spawn case + `want-count`.
- `goal_src/jak2/levels/city/traffic/citizen/guard.gc` — knock-off anim group.
- `goal_src/jak2/levels/city/{ctywide-tasks,protect/protect,slums/kor/hal3-course,kiddogescort/hal4-course}.gc` — `traffic-type-20` → `transport-v` in mission `deactivate-by-type` calls.
- `decompiler/config/jak2/jak2_config.jsonc`, `goal_src/jak2/dgos/lwide{a,b,c}.gd` — `.fr3` merc injection.

### 7. Current State & Known Tradeoffs

- **Working:** spawn / flight (hellcat-verbatim) / pursuit / minimap / seated guard pilot / player boarding / turret fire (AI + player R1, no hull hits) / silent descent + deploy / stabilised hover / return-to-lane / loading-hatch animation / pulled-back piloting camera.
- **Flight physics:** the CoM stays where the hellcat clone puts it (just above joint 0). Moving `cm-offset-joint` without moving every flight control-point array by the same vector is what flipped an earlier build ("turtle") — see [utility notes]. Don't.
- **Turret self-collision (fixed):** `transport-v-fire-turret` parents + `ignore-handle`s the round to the hull. It can still hit the turret child's own 1 m `enemy` sphere at point-blank — the muzzle is pushed to `*transport-v-turret-muzzle-z*` (2 m) to clear it.
- **Spin damping / steering-zero** only apply while `transport-v-deploy-active?`. If the ship still drifts toward Jak while unloading, lower `*transport-v-deploy-spin-damp*` or add a linear-momentum bleed in the same block.
- **Seats & turret muzzle offset** are estimates (no cockpit/gun joint on the `transport` skeleton). If the guard renders buried in the fuselage, nudge `seat-array 0` in `car.gc`.
- **Hatch animation** assumes `transport-hatch-open-ja` (art-elt 5) shares a rest pose with `transport-idle-ja`; guarded by a `type?` check. If it pops, delete the channel-0 block in `update-joint-mods`.
- **`jak2_config.jsonc`** also carries a local `rip_levels: true` + whitespace reformat inherited from the combined branch — harmless, not part of this feature.

---

### 8. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-09-01 → 09-02 | `car.gc`<br>`traffic-h.gc` / `vehicle-h.gc` / `entity-h.gc` / `all-types.gc`<br>`traffic-manager.gc`<br>`guard.gc`<br>`ctywide-tasks.gc` / `protect.gc` / `hal3-course.gc` / `hal4-course.gc`<br>`jak2_config.jsonc` / `lwide{a,b,c}.gd` | Ported from the combined `jak2/features/transport_v2` branch: the whole `transport-v` `vehicle-guard` (skel, cloned hellcat constants, sphere collision, chin-turret child, deploy behaviour, `transport-v-fire-turret` correct-ignore turret fire, silent `vehicle-method-121` descent, seated pilot, hatch animation), the traffic-type wiring, and the shared `transport-ag` merc `.fr3` injection. | A drivable, minimap-flagged, hellcat-like guard gunship in ambient air traffic with a player-usable turret and an alert troop-deploy role. |
| 2026-09-02 | `traffic-manager.gc`<br>`car.gc`<br>`docs/modding/current_mod/transport_traffic_readme.md` | **Branch split + stabilise / return-to-lane / camera.** Isolated the traffic gunship onto its own branch (the scripted alert drop-ship moved to `jak2/features/transport_alert` — `update-alert-transport` + its fields removed here). Deploy rework: `transport-v-deploy-active?` now also requires `guards-dropped` < cap, so once the squad is delivered the descent bias + spin damping release and the ship climbs back to the normal lane to gun for Jak; `guards-dropped` is a per-traffic-life counter, reset in a new `vehicle-method-128` override. Stabilisation: `vehicle-guard-method-154` zeroes AI steering while deploying and `vehicle-method-121` bleeds `ang-momentum`/`ang-velocity` by `*transport-v-deploy-spin-damp*` (new `define`), so the hull no longer yaw-spins over the drop zone. Camera: `camera-string` length 11/24 → **20/36 m**, height 10/11 → **13/15 m**, so the piloting chase-cam frames the whole ship. | One clean feature per branch; make the deploy hover stable, hand control back to a normal-altitude gunship afterwards, and fix the too-close piloting camera. |

---

## 🇫🇷 Version Française

### 1. Présentation & Objectif

`transport-v` est un **vrai véhicule du trafic aérien** : un sous-type de `vehicle-guard` (frère du `hellcat` / `guard-bike`) qui apparaît dans le pool de trafic ambiant d'Abriville, suit les voies de navigation, affiche un **point rouge sur la carte**, est **piloté par un garde** (assis), peut être **pris en main et piloté par le joueur** avec une **tourelle utilisable**, et peut être **abattu** comme tout véhicule de garde.

Pendant une alerte il rejoint la poursuite comme un hellcat et, au-dessus d'une surface solide, **descend d'un niveau aérien, dépose une escouade de Gardes Grenat, puis remonte à la voie normale et tire sur Jak**.

C'est la branche sœur de `jak2/features/transport_alert` (le drop-ship d'alerte scripté, non interactif). Elles ne partagent que l'injection de géométrie merc `.fr3`.

### 2. Pourquoi `vehicle-guard` / `hellcat` est la base

Presque tout est déjà implémenté sur `vehicle-guard` :

| Besoin | Hérité de | Mécanisme |
|---|---|---|
| Pilote garde | `vehicle-guard::vehicle-method-137` | fait apparaître un `crimson-guard-rider` (le trafic met `trsflags-01` + `behavior 1` sur tout véhicule du pool → un rider caché, montré sur `'traffic-on`). `transport-v` met `rider-stance` = 0 pour qu'il soit **assis**. |
| Point rouge sur la carte | `vehicle-guard::vehicle-method-128` | `add-icon! *minimap* … (minimap-class guard)` — icône 14 |
| Suit le chemin de navigation | `vehicle` + `vehicle-controller` + `vehicle-guard-choose-branch` | activé sur un segment de nav (`behavior` 2) ; altitude via `*traffic-height-map*` |
| Vole comme un hellcat | clone de `*hellcat-constants*` | modèle de vol = `mem-copy!` bit-à-bit de `*hellcat-constants*` |
| Poursuite hostile en alerte | états `hostile` / `stop-and-shoot` de `vehicle-guard` | le slot 20 reçoit `trtflags-0` dans `restore-default-settings` |
| Le joueur monte et pilote | `vehicle` `check-player-get-on` | le garde pilote est éjecté (`target-pilot`) |
| Le joueur tire à la tourelle | `transport-v::vehicle-method-94` → `transport-v-fire-turret` | maintenir **R1** en pilotant → le canon-menton visible tire des `guard-shot` depuis son vrai joint de bouche |

### 3. Ce qui est nouveau (`car.gc`, ajouté après `hellcat`)

- **`skel-transport-v`** — LOD lointain → `transport-lod1-mg` (ne disparaît jamais à distance).
- **`*transport-v-constants*`** — `mem-copy!` runtime de `*hellcat-constants*`. Seuls les champs HORS-vol changent : `object-type` 20 ; **bit 3 des flags effacé** (collision à sphères → le joueur entre en collision avec la coque) ; caméra bien reculée (longueur de string 20–36 m, hauteur 13–15 m) pour la coque de ~17 m ; flammes de réacteur plus grosses ; `rider-stance` 0 (assis) ; sièges à la hauteur de la coque.
- **`define` de réglage `*transport-v-*`** (tous éditables au REPL) : `*transport-v-drop-interval*` (4 s), `*transport-v-max-drop*` (5 gardes par vie de trafic), `*transport-v-deploy-descent*` (10 m), `*transport-v-deploy-spin-damp*` (0,82 — rétention de moment angulaire par frame pendant la dépose), `*transport-v-turret-fire-interval*` (0,3 s), `*transport-v-turret-muzzle-z*` (2 m).
- **Tourelle-menton visible** — un enfant `vehicle-turret`. `transport-v` la **vise** (`turret-control-method-9` sur l'enfant) et la **fait tirer** via **`transport-v-fire-turret`** — un spawn de `guard-shot` maison qui parente *et* `ignore-handle` le projectile à la coque, donc le tir sort de la bouche au lieu d'exploser sur les prims `vehicle-sphere` du transport. L'auto-tir de l'enfant n'est jamais armé (`target` forcé à #f chaque frame). La `turret-control` de coque héritée reste non initialisée.
- **Surcharges :** `allocate-and-init-cshape` (7 sphères en espace joint-0, racine `rideable`, une `nav-sphere`), `init-skel-and-rigid-body` (crée la tourelle, initialise l'état de dépose), `vehicle-guard-method-153` (visée + tir IA), `vehicle-method-94` (R1 joueur), `vehicle-method-121` (biais de descente silencieux + amortissement de rotation pendant la dépose), `vehicle-method-128` (remet à zéro l'état de dépose à la ré-activation), `vehicle-method-129` (retire la tourelle à la mort), `update-joint-mods` (animation de porte de soute, désarme l'auto-tir de l'enfant), **`vehicle-guard-method-154`** (le comportement de dépose, voir §4).
- **Câblage du type de trafic :** `traffic-h.gc` renomme `(traffic-type 20)` → `transport-v` ; `vehicle-h.gc` + `entity-h.gc` + `all-types.gc` ajoutent `(vehicle-type transport-v 11)` ; `traffic-manager.gc` reçoit les cas `traffic-object-spawn` + `type-from-vehicle-type` et `want-count[20]` = **2** ; `guard.gc` ajoute l'object-type 20 au groupe d'anim de chute « voiture » ; les scripts de mission qui `deactivate-by-type` le slot 20 utilisent le nouveau nom.

### 4. Comportement d'alerte — descendre, déposer, puis chasser

`vehicle-guard-method-154` (le tick de poursuite par frame), en plus de la chasse hellcat standard. Le déclencheur est **`transport-v-deploy-active?`**, recalculé chaque frame = *alerte active* **et** *au-dessus d'une surface solide (pas l'eau)* **et** *`guards-dropped` < plafond*.

- **Pendant la dépose :**
  - **Descente, silencieuse.** `vehicle-method-121` soustrait `*transport-v-deploy-descent*` (10 m) du `flight-level` de la height-map ; les propulseurs de portance chassent la cible abaissée. `flight-level-index` reste à **1** toute la vie du vaisseau — l'ancienne version utilisait `switch-zone-low!`/`switch-zone-high!` ici, qui faisaient du ping-pong avec le `switch-zone-high!` par frame des ai-hooks et bouclaient le son « bike-down ».
  - **Stabilisé, sans rotation.** La commande de direction par frame de l'ai-hook de poursuite est ce qui fait tourner la coque sur elle-même pendant qu'elle plane pour décharger, donc `vehicle-guard-method-154` met `(-> this controls steering)` à 0 et `vehicle-method-121` amortit `ang-momentum` / `ang-velocity` de `*transport-v-deploy-spin-damp*` chaque frame. Le vaisseau garde une attitude stable au-dessus de la zone.
  - **Porte ouverte.** `update-joint-mods` amène le canal 0 du squelette à la dernière frame de `transport-hatch-open-ja`.
  - **Gardes.** Un `crimson-guard-1` toutes les `*transport-v-drop-interval*` (`behavior` 6, alternance gauche/droite), portage direct de `transport-method-33`.
- **Une fois la charge livrée** (`guards-dropped` atteint le plafond) `transport-v-deploy-active?` devient faux : le biais de descente et l'amortissement se relâchent ensemble, le vaisseau remonte à la voie normale, la porte se ferme, et la chasse standard + le tir de tourelle `vehicle-guard-method-153` prennent le relais — il chasse Jak comme un hellcat armé.
- **Au-dessus de l'eau / sans sol / alerte finie :** comme « terminé » — pas de descente, pas de dépose, vol normal.
- `guards-dropped` est un compteur **par vie de trafic** — il ne se remet pas à zéro à la fin d'une alerte, seulement quand un transport du pool est ré-activé dans le trafic (`vehicle-method-128`). Une passe de dépose par coque ; le pool en fait tourner de nouvelles.

### 5. Rendu — l'injection de géométrie merc `.fr3` (partagée avec la branche sœur)

`extra_art_groups_by_dgo` dans `decompiler/config/jak2/jak2_config.jsonc` cuit la géométrie de `transport-ag` dans `lwidea/lwideb/lwidec.fr3` toujours résidents (textures résolues via la table de remap de `LPROTECT`) ; les entrées `transport-ag.go` + `tpage-2869.go` sont ajoutées aux trois `lwide*.gd`. Voir la [fiche #18](../jak2_modding_utilities/18_merc_geometry_fr3_residency.md).

> **Impose une re-extraction** (`task extract`). La tourelle `vehicle-turret` n'en demande aucune (`CWI.DGO` retail).

### 6. Procédure de Test

1. **Extraire (une fois) :** `task extract`.
2. **Recompiler :** `task repl` puis `(mi)` (deftypes `traffic-manager` et `transport-v` — relancer le REPL si `(mi)` proteste).
3. **Lancer :** `task boot-game`, exploration libre d'Abriville.
4. **Ambiant :** lever les yeux — de temps à autre un grand transport à double coque croise dans la voie haute, un Garde Grenat assis aux commandes, point rouge sur la carte. Il doit rester à plat.
5. **Alerte :** agresser un garde, rester dans son champ de vision. Il rejoint la chasse, puis — au-dessus des rues, pas de l'eau — descend d'~10 m **sans son en boucle**, **garde un cap stable (pas de rotation)**, ouvre sa porte et dépose 5 gardes en ~20 s. Puis il **remonte à la voie normale, referme la porte, et son canon-menton suit et tire sur Jak** (traçantes depuis la bouche, jamais sur le transport).
6. **Monter à bord :** sauter dessus (on atterrit sur la coque), le garde est éjecté, on pilote assis — **la caméra doit être bien reculée pour voir tout le vaisseau**. Maintenir **R1** pour tirer.
7. **En abattre un :** il s'écrase et explose comme tout véhicule de garde ; la tourelle disparaît avec lui.
8. Depuis le REPL : `(send-event *traffic-manager* 'set-object-target-count (traffic-type transport-v) 4)` pour en forcer plus ; ajuster à chaud les `define` `*transport-v-*`.

**Fichiers sources clés :**

- `goal_src/jak2/levels/city/traffic/vehicle/car.gc` — type `transport-v`, `*transport-v-constants*`, les `define` `*transport-v-*`, `transport-v-deploy-active?` / `transport-v-fire-turret` / `transport-v-drop-guard` / `transport-v-over-solid-ground?`, toutes les surcharges, `skel-transport-v`.
- `goal_src/jak2/engine/ai/traffic-h.gc` — `(traffic-type transport-v 20)`.
- `goal_src/jak2/levels/city/traffic/vehicle/vehicle-h.gc`, `goal_src/jak2/engine/entity/entity-h.gc`, `decompiler/config/jak2/all-types.gc` — `(vehicle-type transport-v 11)`.
- `goal_src/jak2/levels/city/traffic/traffic-manager.gc` — cas d'apparition + `want-count`.
- `goal_src/jak2/levels/city/traffic/citizen/guard.gc` — groupe d'anim de chute.
- `goal_src/jak2/levels/city/{ctywide-tasks,protect/protect,slums/kor/hal3-course,kiddogescort/hal4-course}.gc` — `traffic-type-20` → `transport-v`.
- `decompiler/config/jak2/jak2_config.jsonc`, `goal_src/jak2/dgos/lwide{a,b,c}.gd` — injection merc `.fr3`.

### 7. État Actuel & Compromis Connus

- **Fonctionnel :** apparition / vol (hellcat au bit près) / poursuite / minimap / pilote garde assis / embarquement joueur / tir de tourelle (IA + R1 joueur, sans toucher la coque) / descente + dépose silencieuses / vol stationnaire stabilisé / retour à la voie / animation de porte / caméra de pilotage reculée.
- **Physique de vol :** le CdM reste là où le clone hellcat le place. Bouger `cm-offset-joint` sans décaler d'autant chaque tableau de points de contrôle de vol est ce qui a retourné une version précédente (« tortue »). À ne pas faire.
- **Auto-collision de la tourelle (corrigée) :** `transport-v-fire-turret` parente + `ignore-handle` le tir à la coque. Il peut encore toucher la propre sphère `enemy` de 1 m de l'enfant tourelle à bout portant — la bouche est poussée à `*transport-v-turret-muzzle-z*` (2 m).
- **Amortissement de rotation / direction à zéro** ne s'appliquent que pendant `transport-v-deploy-active?`. Si le vaisseau dérive encore vers Jak en déchargeant, baisser `*transport-v-deploy-spin-damp*` ou ajouter un amortissement du moment linéaire dans le même bloc.
- **Sièges & décalage de bouche** sont des estimations (pas de joint de cockpit/canon sur le squelette `transport`). Si le garde apparaît enfoui, ajuster `seat-array 0` dans `car.gc`.
- **Animation de porte** suppose que `transport-hatch-open-ja` (art-elt 5) partage une pose de repos avec `transport-idle-ja` ; protégée par un test `type?`. Si elle « saute », supprimer le bloc canal-0 dans `update-joint-mods`.
- **`jak2_config.jsonc`** porte aussi un `rip_levels: true` local + reformatage d'espaces hérités de la branche combinée — sans conséquence, hors périmètre.

---

### 8. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
| :--- | :--- | :--- | :--- |
| 2026-09-01 → 09-02 | `car.gc`<br>`traffic-h.gc` / `vehicle-h.gc` / `entity-h.gc` / `all-types.gc`<br>`traffic-manager.gc`<br>`guard.gc`<br>`ctywide-tasks.gc` / `protect.gc` / `hal3-course.gc` / `hal4-course.gc`<br>`jak2_config.jsonc` / `lwide{a,b,c}.gd` | Porté depuis la branche combinée `jak2/features/transport_v2` : tout le `vehicle-guard` `transport-v` (skel, constantes hellcat clonées, collision à sphères, enfant tourelle-menton, comportement de dépose, tir de tourelle `transport-v-fire-turret` à ignore correct, descente silencieuse `vehicle-method-121`, pilote assis, animation de porte), le câblage du type de trafic, et l'injection merc `.fr3` partagée de `transport-ag`. | Une canonnière de garde pilotable, signalée sur la carte, volant comme un hellcat, dans le trafic aérien ambiant, avec une tourelle utilisable et un rôle de dépose de troupes en alerte. |
| 2026-09-02 | `traffic-manager.gc`<br>`car.gc`<br>`docs/modding/current_mod/transport_traffic_readme.md` | **Séparation de branche + stabilisation / retour à la voie / caméra.** Isolé la canonnière de trafic sur sa propre branche (le drop-ship d'alerte scripté est passé sur `jak2/features/transport_alert` — `update-alert-transport` + ses champs retirés ici). Refonte de la dépose : `transport-v-deploy-active?` exige maintenant aussi `guards-dropped` < plafond, donc une fois l'escouade livrée le biais de descente + l'amortissement se relâchent et le vaisseau remonte à la voie normale pour tirer sur Jak ; `guards-dropped` est un compteur par vie de trafic, remis à zéro dans une nouvelle surcharge `vehicle-method-128`. Stabilisation : `vehicle-guard-method-154` met la direction IA à zéro pendant la dépose et `vehicle-method-121` amortit `ang-momentum`/`ang-velocity` de `*transport-v-deploy-spin-damp*` (nouveau `define`), donc la coque ne tourne plus sur elle-même au-dessus de la zone. Caméra : longueur de `camera-string` 11/24 → **20/36 m**, hauteur 10/11 → **13/15 m**, pour cadrer tout le vaisseau en pilotage. | Une fonctionnalité propre par branche ; rendre le vol stationnaire de dépose stable, rendre la main à une canonnière à altitude normale ensuite, et corriger la caméra de pilotage trop proche. |
