# 17 — Traffic Engine: Spawn Rates, Alert Quotas, Distance Spheres & Nav-Mesh Limits / Moteur de Trafic : Taux de Spawn, Quotas d'Alerte, Sphères de Distance et Limites Nav-Mesh

> - **Origin / Provenance :** `jak2/config/enhanced_spawnrates`
> - **Last Updated / Dernière modification :** `jak2/config/enhanced_spawnrates`

---

# 🇬🇧 English Version

## 1. Context and Core Concepts
In Jak 2, ambient Haven City traffic and foot patrols are governed by the `traffic-manager` and `traffic-engine` subsystems. This document details the object quotas, alert escalation tiers, grid cell distance spheres, and nav-mesh user capacities.

---

## 2. Traffic Object Types & Quotas (`traffic-manager.gc`)

The traffic system controls ambient density via `want-count` entries assigned in `init-params` of `traffic-manager`:

| Type Index | Traffic Type Enum | Description | Vanilla Quota | Enhanced Quota Example |
| :---: | :--- | :--- | :---: | :---: |
| **0** | `citizen-norm` | Standard male citizen | 20 | 18 |
| **1** | `citizen-chick` | Female citizen | 20 | 18 |
| **2** | `citizen-fat` | Heavy citizen | 20 | 18 |
| **4** | `crimson-guard-0` | Crimson Guard (Patrol) | 1 | 6 |
| **6** | `crimson-guard-1` | Crimson Guard (Rifle) | 9 | 22 |
| **7** | `crimson-guard-2` | Crimson Guard (Tazer) | 0 | 10 |
| **11-13** | `car-a`, `car-b`, `car-c` | Civilian hover cars | 16 / 16 / 16 | 16 / 16 / 16 |
| **14-16** | `bike-a`, `bike-b`, `bike-c` | Civilian hover bikes | 14 / 14 / 14 | 14 / 14 / 14 |
| **18** | `guard-bike` | Crimson Guard hover bike | 4 | 10 |
| **19** | `hellcat` | Crimson Guard Hellcat cruiser | 3 | 8 |

---

## 3. Alert Level Settings (`traffic-engine.gc`)

When an alarm triggers in Haven City, the `traffic-alert-state` dynamically overrides guard want counts according to `*alert-level-settings*` (indexed 0 to 4):

```lisp
(define *alert-level-settings* (new 'static 'inline-array traffic-alert-state-settings 5
  ;; Alert Level 0 (Peacetime / Low Tension)
  (new 'static 'traffic-alert-state-settings
    :ped-tazer (new 'static 'traffic-guard-type-settings :target-count 12 ...)
    :ped-rifle (new 'static 'traffic-guard-type-settings :target-count 6 ...)
    :bike-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    :hellcat-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    )
  ;; Alert Level 4 (Maximum Alert / Heavy Reinforcements)
  (new 'static 'traffic-alert-state-settings
    :ped-tazer (new 'static 'traffic-guard-type-settings :target-count 8 ...)
    :ped-rifle (new 'static 'traffic-guard-type-settings :target-count 22 ...)
    :ped-grenade (new 'static 'traffic-guard-type-settings :target-count 6 ...)
    :bike-turret (new 'static 'traffic-guard-type-settings :target-count 10 ...)
    :hellcat-turret (new 'static 'traffic-guard-type-settings :target-count 8 ...)
    )
  )
)
```

---

## 4. Cell Activation Radii & Distance Spheres (`per-frame-cell-update`)

The method `(per-frame-cell-update ((this traffic-level-data)))` in [`traffic-engine.gc`](file:///goal_src/jak2/levels/city/traffic/traffic-engine.gc) evaluates visibility and distance for each cell in the level's grid:

```lisp
(let ((s5-0 (math-camera-pos))
      (f30-0 122880.0)    ;; 30m - Frustum cull threshold
      (f28-0 983040.0)    ;; 240m - Active vehicle sphere (vanilla: 200m)
      (f26-0 655360.0)    ;; 160m - Active pedestrian sphere (vanilla: 120m)
      )
  ...)
```

> [!WARNING]
> **Static Cell Limit (255 Cells)**:
> `traffic-level-data` defines `(active-cell-list vis-cell 255)`. If the vehicle/pedestrian distance sphere is set too high (e.g. > 300m), especially during level streaming transitions where multiple levels are resident simultaneously, more than 255 cells become active, resulting in buffer overflows and rendering DMA crashes (`exit status 5`).
> Keep vehicle activation around **240m** and pedestrian activation around **160m** for optimal density and stability.

---

## 5. Nav-Mesh Capacity & Multi-Level Streaming (`nav-mesh.gc`)

Every city district (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, etc.) has its own `nav-mesh` containing navigation polygons.
When an enemy or pedestrian spawns, `(new-nav-control this proc)` requests a slot on that nav-mesh.

### The 64-User Nav-Mesh Bottleneck
In vanilla Jak 2, `(init-from-entity ((this nav-mesh) (arg0 entity-nav-mesh)))` defaults `nav-max-users` to `64`:
```lisp
(let ((s5-1 (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 64) :time -1000000000.0)))
```
When moving between districts with high density, all active guards and civilians request nav slots on the destination district's mesh. Exceeding 64 users outputs:
```text
nav-mesh::new-nav-control:  too many users for nav-mesh #f
ERROR: nav-mesh::change-to: unable to allocate nav-mesh for #<crimson-guard ...>
```
and crashes the runtime.

### The Fix
Update `init-from-entity` in [`nav-mesh.gc`](file:///goal_src/jak2/engine/nav/nav-mesh.gc) to raise the default user limit:
```lisp
(let ((s5-1 (the-as uint128 (min 200 (max 128 (the-as int (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 128) :time -1000000000.0)))))))
```
This safely allocates `nav-control-array` and engine `user-list` for up to **128 concurrent pathfinding actors** per level.

---

## 6. Console Diagnostics & OpenGOAL Constraints

- **8-Parameter Function Limit**: GOAL functions strictly limit calls to 8 parameters (including `#t` and format strings). Split diagnostic logging into multiple `format` statements if more parameters are required.
- **Dead-Pool Type Casting**: `*default-dead-pool*` is typed as generic `dead-pool`. To invoke `(memory-free ...)` or `(memory-total ...)`, cast it explicitly:
  ```lisp
  (/ (memory-free (the-as dead-pool-heap *default-dead-pool*)) 1024)
  ```

---

# 🇫🇷 Version Française

## 1. Contexte et Notions Clés
Dans Jak 2, la circulation générale et les patrouilles d'Abriville sont orchestrées par `traffic-manager` et `traffic-engine`. Ce document détaille les quotas d'apparition, les paliers d'alerte, les sphères d'activation de la grille et la capacité des maillages de navigation (`nav-mesh`).

---

## 2. Types d'Objets & Quotas de Circulation (`traffic-manager.gc`)

Le moteur contrôle la densité via les entrées `want-count` dans `init-params` de `traffic-manager` :

| Index Type | Enum Traffic Type | Description | Quota Vanilla | Exemple Quota Renforcé |
| :---: | :--- | :--- | :---: | :---: |
| **0** | `citizen-norm` | Citoyen homme standard | 20 | 18 |
| **1** | `citizen-chick` | Citoyenne femme | 20 | 18 |
| **2** | `citizen-fat` | Citoyen corpulent | 20 | 18 |
| **4** | `crimson-guard-0` | Crimson Guard (Patrouilleur) | 1 | 6 |
| **6** | `crimson-guard-1` | Crimson Guard (Fusilier) | 9 | 22 |
| **7** | `crimson-guard-2` | Crimson Guard (Tazer) | 0 | 10 |
| **11-13** | `car-a`, `car-b`, `car-c` | Voitures civiles volantes | 16 / 16 / 16 | 16 / 16 / 16 |
| **14-16** | `bike-a`, `bike-b`, `bike-c` | Motos civiles volantes | 14 / 14 / 14 | 14 / 14 / 14 |
| **18** | `guard-bike` | Moto volante de Crimson Guard | 4 | 10 |
| **19** | `hellcat` | Croiseur Hellcat de Crimson Guard | 3 | 8 |

---

## 3. Paramétrage des Paliers d'Alerte (`traffic-engine.gc`)

Lorsqu'une alarme se déclenche en ville, l'état d'alerte (`traffic-alert-state`) surcharge dynamiquement les quotas de gardes selon `*alert-level-settings*` (niveaux 0 à 4) :

```lisp
(define *alert-level-settings* (new 'static 'inline-array traffic-alert-state-settings 5
  ;; Niveau d'alerte 0 (Temps de paix / Faible tension)
  (new 'static 'traffic-alert-state-settings
    :ped-tazer (new 'static 'traffic-guard-type-settings :target-count 12 ...)
    :ped-rifle (new 'static 'traffic-guard-type-settings :target-count 6 ...)
    :bike-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    :hellcat-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    )
  ;; Niveau d'alerte 4 (Alerte maximale / Renforts lourds)
  (new 'static 'traffic-alert-state-settings
    :ped-tazer (new 'static 'traffic-guard-type-settings :target-count 8 ...)
    :ped-rifle (new 'static 'traffic-guard-type-settings :target-count 22 ...)
    :ped-grenade (new 'static 'traffic-guard-type-settings :target-count 6 ...)
    :bike-turret (new 'static 'traffic-guard-type-settings :target-count 10 ...)
    :hellcat-turret (new 'static 'traffic-guard-type-settings :target-count 8 ...)
    )
  )
)
```

---

## 4. Rayons d'Activation des Cellules de Grille (`per-frame-cell-update`)

La méthode `(per-frame-cell-update ((this traffic-level-data)))` dans [`traffic-engine.gc`](file:///goal_src/jak2/levels/city/traffic/traffic-engine.gc) recalcule à chaque trame la visibilité et la distance des cellules de la grille :

```lisp
(let ((s5-0 (math-camera-pos))
      (f30-0 122880.0)    ;; 30m - Seuil de culling par frustum
      (f28-0 983040.0)    ;; 240m - Sphère véhicules actifs (vanilla : 200m)
      (f26-0 655360.0)    ;; 160m - Sphère piétons actifs (vanilla : 120m)
      )
  ...)
```

> [!WARNING]
> **Limite des 255 Cellules Statiques** :
> `traffic-level-data` alloue un tableau fixe `(active-cell-list vis-cell 255)`. Si la portée est trop vaste (> 300m), le nombre de cellules actives dépasse 255 lors du streaming simultané de plusieurs quartiers, ce qui fait exploser le buffer DMA vidéo (`exit status 5`).
> Maintenir 240m (véhicules) et 160m (piétons) offre un compromis idéal entre densité et stabilité.

---

## 5. Capacité des Maillages de Navigation (`nav-mesh.gc`)

Chaque quartier possède son propre `nav-mesh`. Lorsqu'une entité apparaît, `(new-nav-control this proc)` réserve un emplacement dans le maillage.

### Le goulot d'étranglement à 64 utilisateurs
En version d'origine, `(init-from-entity ((this nav-mesh) (arg0 entity-nav-mesh)))` bride `nav-max-users` à **64** :
```lisp
(let ((s5-1 (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 64) :time -1000000000.0)))
```
Lors des transitions de zones à haute densité, l'arrivée de gardes supplémentaires sature le quota :
```text
nav-mesh::new-nav-control:  too many users for nav-mesh #f
ERROR: nav-mesh::change-to: unable to allocate nav-mesh for #<crimson-guard ...>
```

### Le Correctif
Dans [`nav-mesh.gc`](file:///goal_src/jak2/engine/nav/nav-mesh.gc), élever le plancher par défaut à **128 acteurs** :
```lisp
(let ((s5-1 (the-as uint128 (min 200 (max 128 (the-as int (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 128) :time -1000000000.0)))))))
```

---

## 6. Diagnostics Console et Règles GOAL

- **Limite de 8 paramètres :** Les fonctions GOAL n'acceptent pas plus de 8 paramètres (y compris `#t` et la chaîne de formatage). Découper les logs `format` volumineux en deux appels successifs.
- **Cast de type Dead-Pool :** `*default-dead-pool*` est typé en `dead-pool` générique. Pour appeler `(memory-free ...)` ou `(memory-total ...)`, le caster explicitement :
  ```lisp
  (/ (memory-free (the-as dead-pool-heap *default-dead-pool*)) 1024)
  ```
