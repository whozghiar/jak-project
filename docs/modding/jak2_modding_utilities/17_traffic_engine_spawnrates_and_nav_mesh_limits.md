# Jak 2 — Traffic Engine: Spawn Rates, Alert Quotas, Distance Spheres & Nav-Mesh Limits / Moteur de Trafic : Taux d'Apparition, Quotas d'Alerte, Sphères de Distance & Limites de Nav-Mesh

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/config/enhanced_spawnrates`
> - **Last Updated / Dernière modification:** `jak2/config/enhanced_spawnrates`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Context & Core Concepts

This document details the city traffic engine in Jak 2 — how ambient citizens, Crimson Guards, and vehicles are managed, and how to scale spawn densities and ranges without exceeding engine limits.

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

The method `(per-frame-cell-update ((this traffic-level-data)))` in [`traffic-engine.gc`](../../../goal_src/jak2/levels/city/traffic/traffic-engine.gc) evaluates visibility and distance for each cell in the level's grid:

```lisp
(let ((s5-0 (math-camera-pos))
      (f30-0 122880.0)    ;; 30m - Frustum cull threshold
      (f28-0 983040.0)    ;; 240m - Active vehicle sphere (vanilla: 200m)
      (f26-0 655360.0)    ;; 160m - Active pedestrian sphere (vanilla: 120m)
      )
  ...)
```

> [!WARNING]
> **Static Cell Limit (255 Cells):**
> `traffic-level-data` defines `(active-cell-list vis-cell 255)`. If the vehicle/pedestrian distance sphere is set too high (e.g. > 300m), especially during level streaming transitions where multiple levels are resident simultaneously, more than 255 cells become active, resulting in buffer overflows and rendering DMA crashes (`exit status 5`).
> Keep vehicle activation around **240m** and pedestrian activation around **160m** for optimal density and stability.

---

## 5. Nav-Mesh Capacity & Multi-Level Streaming (`nav-mesh.gc`)

Every city district (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, etc.) has its own `nav-mesh` containing navigation polygons. When an enemy or pedestrian spawns, `(new-nav-control this proc)` requests a slot on that nav-mesh.

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

Update `init-from-entity` in [`nav-mesh.gc`](../../../goal_src/jak2/engine/nav/nav-mesh.gc) to raise the default user limit:

```lisp
(let ((s5-1 (the-as uint128 (min 200 (max 128 (the-as int (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 128) :time -1000000000.0)))))))
```

This safely allocates `nav-control-array` and engine `user-list` for up to **128 concurrent pathfinding actors** per level.

---

## 6. Known Pitfalls — Console Diagnostics & OpenGOAL Constraints

- **8-Parameter Function Limit:** GOAL functions strictly limit calls to 8 parameters (including `#t` and format strings). Split diagnostic logging into multiple `format` statements if more parameters are required.
- **Dead-Pool Type Casting:** `*default-dead-pool*` is typed as generic `dead-pool`. To invoke `(memory-free ...)` or `(memory-total ...)`, cast it explicitly:

  ```lisp
  (/ (memory-free (the-as dead-pool-heap *default-dead-pool*)) 1024)
  ```

---

## 7. Verification Steps

1. `task repl` → `(mi)` reports `Successfully built all N targets`.
2. `task boot-game`, roam Haven City: guard density should visibly match the tuned quotas.
3. Trigger a full city alert (attack a guard): reinforcement waves scale up to the level-4 targets.
4. Cross several district boundaries at high alert: no `too many users for nav-mesh` error, no DMA `exit status 5`.
5. Check the console diagnostic line for free `*default-dead-pool*` headroom staying comfortably positive.

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux

Ce document détaille le moteur de trafic urbain de Jak 2 — comment les citoyens ambiants, les Gardes Grenat et les véhicules sont gérés, et comment mettre à l'échelle les densités et portées d'apparition sans dépasser les limites du moteur.

---

## 2. Types d'Objets de Trafic & Quotas (`traffic-manager.gc`)

Le système de trafic contrôle la densité ambiante via les entrées `want-count` assignées dans `init-params` de `traffic-manager` :

| Index de type | Énum `traffic-type` | Description | Quota vanilla | Exemple de quota renforcé |
| :---: | :--- | :--- | :---: | :---: |
| **0** | `citizen-norm` | Citoyen masculin standard | 20 | 18 |
| **1** | `citizen-chick` | Citoyenne | 20 | 18 |
| **2** | `citizen-fat` | Citoyen corpulent | 20 | 18 |
| **4** | `crimson-guard-0` | Garde Grenat (patrouille) | 1 | 6 |
| **6** | `crimson-guard-1` | Garde Grenat (fusil) | 9 | 22 |
| **7** | `crimson-guard-2` | Garde Grenat (tazer) | 0 | 10 |
| **11-13** | `car-a`, `car-b`, `car-c` | Voitures volantes civiles | 16 / 16 / 16 | 16 / 16 / 16 |
| **14-16** | `bike-a`, `bike-b`, `bike-c` | Motos volantes civiles | 14 / 14 / 14 | 14 / 14 / 14 |
| **18** | `guard-bike` | Moto volante de la Garde Grenat | 4 | 10 |
| **19** | `hellcat` | Croiseur Hellcat de la Garde Grenat | 3 | 8 |

---

## 3. Réglages des Niveaux d'Alerte (`traffic-engine.gc`)

Lorsqu'une alarme se déclenche à Haven City, `traffic-alert-state` surcharge dynamiquement les quotas de gardes selon `*alert-level-settings*` (indexé de 0 à 4) :

```lisp
(define *alert-level-settings* (new 'static 'inline-array traffic-alert-state-settings 5
  ;; Niveau d'alerte 0 (temps de paix / faible tension)
  (new 'static 'traffic-alert-state-settings
    :ped-tazer (new 'static 'traffic-guard-type-settings :target-count 12 ...)
    :ped-rifle (new 'static 'traffic-guard-type-settings :target-count 6 ...)
    :bike-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    :hellcat-turret (new 'static 'traffic-guard-type-settings :target-count 2 ...)
    )
  ;; Niveau d'alerte 4 (alerte maximale / renforts massifs)
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

## 4. Rayons d'Activation des Cellules & Sphères de Distance (`per-frame-cell-update`)

La méthode `(per-frame-cell-update ((this traffic-level-data)))` dans [`traffic-engine.gc`](../../../goal_src/jak2/levels/city/traffic/traffic-engine.gc) évalue la visibilité et la distance de chaque cellule de la grille du niveau :

```lisp
(let ((s5-0 (math-camera-pos))
      (f30-0 122880.0)    ;; 30m - Seuil de culling du frustum
      (f28-0 983040.0)    ;; 240m - Sphère de véhicules actifs (vanilla : 200m)
      (f26-0 655360.0)    ;; 160m - Sphère de piétons actifs (vanilla : 120m)
      )
  ...)
```

> [!WARNING]
> **Limite statique de cellules (255) :**
> `traffic-level-data` définit `(active-cell-list vis-cell 255)`. Si la sphère de distance véhicules/piétons est réglée trop haut (ex. > 300m), en particulier durant les transitions de streaming où plusieurs niveaux sont résidents simultanément, plus de 255 cellules deviennent actives, provoquant des débordements de tampon et des plantages DMA du rendu (`exit status 5`).
> Conserver l'activation des véhicules autour de **240m** et celle des piétons autour de **160m** pour un bon compromis densité / stabilité.

---

## 5. Capacité du Nav-Mesh & Streaming Multi-Niveaux (`nav-mesh.gc`)

Chaque quartier de la ville (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, etc.) possède son propre `nav-mesh` contenant les polygones de navigation. Lorsqu'un ennemi ou un piéton apparaît, `(new-nav-control this proc)` demande un emplacement sur ce nav-mesh.

### Le goulot d'étranglement des 64 utilisateurs

Dans Jak 2 vanilla, `(init-from-entity ((this nav-mesh) (arg0 entity-nav-mesh)))` fixe `nav-max-users` à `64` par défaut :

```lisp
(let ((s5-1 (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 64) :time -1000000000.0)))
```

Lors du passage entre quartiers à forte densité, tous les gardes et civils actifs demandent un emplacement sur le mesh du quartier de destination. Dépasser 64 utilisateurs affiche :

```text
nav-mesh::new-nav-control:  too many users for nav-mesh #f
ERROR: nav-mesh::change-to: unable to allocate nav-mesh for #<crimson-guard ...>
```

et fait planter le runtime.

### Le correctif

Mettre à jour `init-from-entity` dans [`nav-mesh.gc`](../../../goal_src/jak2/engine/nav/nav-mesh.gc) pour relever la limite d'utilisateurs par défaut :

```lisp
(let ((s5-1 (the-as uint128 (min 200 (max 128 (the-as int (res-lump-value arg0 'nav-max-users uint128 :default (the-as uint128 128) :time -1000000000.0)))))))
```

Cela alloue en toute sécurité `nav-control-array` et le `user-list` moteur pour jusqu'à **128 acteurs de pathfinding simultanés** par niveau.

---

## 6. Pièges Connus — Diagnostics Console & Contraintes OpenGOAL

- **Limite de 8 paramètres de fonction :** les fonctions GOAL limitent strictement les appels à 8 paramètres (y compris `#t` et les chaînes de format). Découper la journalisation de diagnostic en plusieurs instructions `format` si davantage de paramètres sont nécessaires.
- **Cast de type du Dead-Pool :** `*default-dead-pool*` est typé comme un `dead-pool` générique. Pour invoquer `(memory-free ...)` ou `(memory-total ...)`, le caster explicitement :

  ```lisp
  (/ (memory-free (the-as dead-pool-heap *default-dead-pool*)) 1024)
  ```

---

## 7. Procédure de Validation

1. `task repl` → `(mi)` affiche `Successfully built all N targets`.
2. `task boot-game`, se promener dans Haven City : la densité de gardes doit correspondre visiblement aux quotas réglés.
3. Déclencher une alerte générale (attaquer un garde) : les vagues de renfort montent jusqu'aux cibles du niveau 4.
4. Franchir plusieurs frontières de quartier en alerte maximale : aucune erreur `too many users for nav-mesh`, aucun `exit status 5` DMA.
5. Vérifier la ligne de diagnostic console : la marge libre de `*default-dead-pool*` doit rester confortablement positive.
