# Jak 2 — Vehicle Mechanics: Hijacking, Grab Rails, Weapons & Flight Levels / Mécaniques des Véhicules : Détournement, Barres d'Accroche, Armes & Niveaux de Vol

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/paddy-wagon`
> - **Last Updated / Dernière modification:** `jak2/features/guard_transport`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Context & Core Concepts

In Jak 2, all ambient and player vehicles inherit from the base `vehicle` class (defined in [`goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc`](../../../goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc)). This document outlines the generic engine mechanics governing vehicle boarding, edge-grabbing, weapons while driving, and flight altitude zones.

---

## 2. Vehicle Constant Flags (`info flags`)

The `rigid-body-vehicle-constants` struct contains a `:flags` bitfield that configures key gameplay behaviors:

| Flag Bit | Hex Value | Name / Effect | Description |
| :--- | :--- | :--- | :--- |
| **Bit 2** | `#x04` | `guard-vehicle` | Marks the vehicle as a Crimson Guard asset (Hellcat, Guard Bike, Prison Zoomer). |
| **Bit 3** | `#x08` | `vehicle` | Standard vehicle physics flag. |
| **Bit 5** | `#x20` | `allow-gun` (`gun?`) | Enables Jak to draw, aim, and fire all guns while driving (`(-> self pilot gun?)` in `target-pilot.gc`). |
| **Bit 6** | `#x40` | `allow-flight-zones` | Enables altitude switching (`switch-zone-high!` / `switch-zone-low!`) via **R2** and vertical flight-level transitions. |

> [!TIP]
> To allow Jak to both change altitude levels with **R2** and use guns on a guard vehicle, set `:flags #x6c` (`#x04 | #x08 | #x20 | #x40`).

---

## 3. Hijacking & Grab Rails (`grab-rail-array`)

Jak 2 distinguishes between two boarding behaviors based on the vehicle's grab rails:

### A. Small Vehicles (Bikes, no grab rails)

- `:grab-rail-array #f` and `:grab-rail-count 0`.
- Pressing **Triangle** immediately seats Jak without an intermediate suspension phase.

### B. Large Vehicles (Cars, Transports, Hellcats)

- Defining `:grab-rail-count` and `:grab-rail-array` enables long-range edge-grabbing (up to 20 meters / `81920.0` units):

  ```lisp
  :grab-rail-count 6
  :grab-rail-array (new 'static 'inline-array vehicle-grab-rail-info 6
    (new 'static 'vehicle-grab-rail-info
      :local-pos (new 'static 'inline-array vector 2
        (new 'static 'vector :x 5120.0 :y 1024.0 :z 8192.0 :w 1.0)
        (new 'static 'vector :x -5120.0 :y 1024.0 :z 8192.0 :w 1.0)
        )
      :normal (new 'static 'vector :z 1.0 :w 1.0)
      )
    ;; Additional side, rear, and corner rails...
    )
  ```

- **Workflow:**
  1. When Jak is on the ground underneath or jumping near the vehicle, the prompt `PRESS TRIANGLE TO USE` appears.
  2. Pressing **Triangle** sends `'pilot-edge-grab` to `*target*`.
  3. Jak leaps up and **hangs / suspends from the rail** (`target-pilot-edge-grab` state).
  4. Pressing **Jump (Cross)** or **Triangle** while hanging pulls Jak up into the cockpit, ejects the driver, and takes full control.

---

## 4. Player Driving Controls & Uninitialized Turret Pitfalls

When a vehicle enters the `player-control` state (`vehicle-states.gc`), its `:post` handler executes `vehicle-method-94`:

- **`vehicle-guard` assumption:** The default `(vehicle-method-94 ((this vehicle-guard)))` assumes the vehicle is armed with a turret (`hellcat`, `guard-bike`) and attempts to update `(-> this turret info)`.
- **Unarmed vehicles (`paddywagon`):** If a child of `vehicle-guard` has no turret, calling `vehicle-guard`'s `vehicle-method-94` causes an immediate **null pointer dereference (exit status 5 / SIGSEGV)**.
- **Fix:** Override `vehicle-method-94` to call the base `vehicle` method directly:

  ```lisp
  (defmethod vehicle-method-94 ((this paddywagon))
    ((method-of-type vehicle vehicle-method-94) this)
    0
    (none)
    )
  ```

---

## 5. Flight Altitude & Zone Switching

- **Player Control:** Pressing **R2** toggles between low and high altitude flight corridors (provided `#x40` is set in `:flags`).
- **Ambient Guard Traffic:** `vehicle-guard-method-150` forces all guard vehicles to `(switch-zone-high! this)` on every cycle. If an ambient vehicle should roam both low and high traffic lanes naturally, ensure its `vehicle-method-120` delegates to `(method-of-type vehicle vehicle-method-120)` rather than `vehicle-guard`.

---

## 6. Known Pitfalls — Passenger Ejection & Nav-Mesh Saturation

During `target-pilot-init`, the engine sends `'knocked-off` to **all seats** of the vehicle:

- For rear passenger / captive seats (e.g. `seat-index > 0`), the rider should return `#f` on `'knocked-off` to remain safely seated inside.
- When spawning ejected riders onto the ground, always verify `(when (-> gp-0 nav-mesh) ...)` before sending `'activate-object` to `*traffic-manager*` to prevent infinite spawn retry loops and memory exhaustion crashes.

---

## 7. Verification Steps

1. `task repl` → `(mi)` must report `Successfully built all N targets`.
2. `task boot-game`, free-roam in Haven City.
3. Stand under a large guard vehicle: `PRESS TRIANGLE TO USE` must appear; Triangle → edge-grab → Cross → cockpit control.
4. With `#x40` set, **R2** must swap altitude corridors without dropping the vehicle.
5. With `#x20` set, guns must draw and fire while driving.
6. Drive an unarmed guard-derived vehicle for 30+ seconds: no `exit status 5` from the turret path.

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux

Dans Jak 2, tous les véhicules ambiants et pilotables héritent de la classe de base `vehicle` (définie dans [`goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc`](../../../goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc)). Ce document décrit les mécaniques moteur génériques régissant l'embarquement, l'accroche aux rebords, l'usage des armes en conduite et les zones d'altitude de vol.

---

## 2. Drapeaux de Constantes de Véhicule (`info flags`)

La structure `rigid-body-vehicle-constants` contient un champ de bits `:flags` qui configure des comportements de gameplay clés :

| Bit du drapeau | Valeur hex | Nom / Effet | Description |
| :--- | :--- | :--- | :--- |
| **Bit 2** | `#x04` | `guard-vehicle` | Marque le véhicule comme un asset de la Garde Grenat (Hellcat, moto de garde, Prison Zoomer). |
| **Bit 3** | `#x08` | `vehicle` | Drapeau de physique de véhicule standard. |
| **Bit 5** | `#x20` | `allow-gun` (`gun?`) | Autorise Jak à dégainer, viser et tirer avec toutes ses armes en conduisant (`(-> self pilot gun?)` dans `target-pilot.gc`). |
| **Bit 6** | `#x40` | `allow-flight-zones` | Active le changement d'altitude (`switch-zone-high!` / `switch-zone-low!`) via **R2** et les transitions de niveau de vol verticales. |

> [!TIP]
> Pour permettre à Jak à la fois de changer de niveau d'altitude avec **R2** et d'utiliser ses armes sur un véhicule de garde, définir `:flags #x6c` (`#x04 | #x08 | #x20 | #x40`).

---

## 3. Détournement & Barres d'Accroche (`grab-rail-array`)

Jak 2 distingue deux comportements d'embarquement selon les barres d'accroche du véhicule :

### A. Petits véhicules (motos, sans barres d'accroche)

- `:grab-rail-array #f` et `:grab-rail-count 0`.
- Un appui sur **Triangle** installe immédiatement Jak sans phase de suspension intermédiaire.

### B. Grands véhicules (voitures, transports, Hellcats)

- Définir `:grab-rail-count` et `:grab-rail-array` active l'accroche aux rebords à longue portée (jusqu'à 20 mètres / `81920.0` unités) :

  ```lisp
  :grab-rail-count 6
  :grab-rail-array (new 'static 'inline-array vehicle-grab-rail-info 6
    (new 'static 'vehicle-grab-rail-info
      :local-pos (new 'static 'inline-array vector 2
        (new 'static 'vector :x 5120.0 :y 1024.0 :z 8192.0 :w 1.0)
        (new 'static 'vector :x -5120.0 :y 1024.0 :z 8192.0 :w 1.0)
        )
      :normal (new 'static 'vector :z 1.0 :w 1.0)
      )
    ;; Rails latéraux, arrière et d'angle supplémentaires...
    )
  ```

- **Déroulé :**
  1. Lorsque Jak est au sol sous le véhicule ou saute à proximité, l'indication `Appuyez sur Triangle` apparaît.
  2. Un appui sur **Triangle** envoie `'pilot-edge-grab` à `*target*`.
  3. Jak bondit et **s'agrippe / se suspend au rail** (état `target-pilot-edge-grab`).
  4. Un appui sur **Saut (Croix)** ou **Triangle** pendant la suspension hisse Jak dans le cockpit, éjecte le conducteur et donne le contrôle total.

---

## 4. Contrôles de Conduite & Pièges des Tourelles Non Initialisées

Lorsqu'un véhicule entre dans l'état `player-control` (`vehicle-states.gc`), son gestionnaire `:post` exécute `vehicle-method-94` :

- **Hypothèse de `vehicle-guard` :** Le `(vehicle-method-94 ((this vehicle-guard)))` par défaut suppose que le véhicule est armé d'une tourelle (`hellcat`, `guard-bike`) et tente de mettre à jour `(-> this turret info)`.
- **Véhicules non armés (`paddywagon`) :** Si un enfant de `vehicle-guard` n'a pas de tourelle, appeler le `vehicle-method-94` de `vehicle-guard` provoque un **déréférencement de pointeur nul immédiat (exit status 5 / SIGSEGV)**.
- **Correctif :** Surcharger `vehicle-method-94` pour appeler directement la méthode de base `vehicle` :

  ```lisp
  (defmethod vehicle-method-94 ((this paddywagon))
    ((method-of-type vehicle vehicle-method-94) this)
    0
    (none)
    )
  ```

---

## 5. Altitude de Vol & Changement de Zone

- **Contrôle joueur :** Un appui sur **R2** bascule entre les couloirs de vol basse et haute altitude (à condition que `#x40` soit présent dans `:flags`).
- **Trafic de gardes ambiant :** `vehicle-guard-method-150` force tous les véhicules de garde à `(switch-zone-high! this)` à chaque cycle. Si un véhicule ambiant doit circuler naturellement sur les couloirs bas et hauts, s'assurer que son `vehicle-method-120` délègue à `(method-of-type vehicle vehicle-method-120)` plutôt qu'à `vehicle-guard`.

---

## 6. Pièges Connus — Éjection des Passagers & Saturation du Nav-Mesh

Pendant `target-pilot-init`, le moteur envoie `'knocked-off` à **tous les sièges** du véhicule :

- Pour les sièges de passager arrière / captif (ex. `seat-index > 0`), le passager doit renvoyer `#f` sur `'knocked-off` pour rester assis à l'intérieur en sécurité.
- Lors de l'apparition de passagers éjectés au sol, toujours vérifier `(when (-> gp-0 nav-mesh) ...)` avant d'envoyer `'activate-object` à `*traffic-manager*` afin d'éviter les boucles infinies de nouvelle tentative d'apparition et les plantages par épuisement mémoire.

---

## 7. Procédure de Validation

1. `task repl` → `(mi)` doit afficher `Successfully built all N targets`.
2. `task boot-game`, exploration libre dans Haven City.
3. Se placer sous un grand véhicule de garde : `Appuyez sur Triangle` doit apparaître ; Triangle → accroche → Croix → contrôle du cockpit.
4. Avec `#x40` défini, **R2** doit changer de couloir d'altitude sans faire chuter le véhicule.
5. Avec `#x20` défini, les armes doivent se dégainer et tirer pendant la conduite.
6. Conduire un véhicule dérivé de garde non armé pendant 30 s et plus : aucun `exit status 5` provenant du chemin de la tourelle.
