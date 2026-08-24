# 16 — Vehicle Mechanics: Hijacking, Grab Rails, Weapons & Flight Levels

In Jak 2, all ambient and player vehicles inherit from the base `vehicle` class (defined in [`goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/levels/city/traffic/vehicle/vehicle.gc)). This document outlines the generic engine mechanics governing vehicle boarding, edge-grabbing, weapons while driving, and flight altitude zones.

---

## 1. Vehicle Constant Flags (`info flags`)

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

## 2. Hijacking & Grab Rails (`grab-rail-array`)

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
- **Workflow :**
  1. When Jak is on the ground underneath or jumping near the vehicle, the prompt `PRESS TRIANGLE TO USE` appears.
  2. Pressing **Triangle** sends `'pilot-edge-grab` to `*target*`.
  3. Jak leaps up and **hangs / suspends from the rail** (`target-pilot-edge-grab` state).
  4. Pressing **Jump (Croix)** or **Triangle** while hanging pulls Jak up into the cockpit, ejects the driver, and takes full control.

---

## 3. Player Driving Controls & Uninitialized Turret Pitfalls

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

## 4. Flight Altitude & Zone Switching

- **Player Control:** Pressing **R2** toggles between low and high altitude flight corridors (provided `#x40` is set in `:flags`).
- **Ambient Guard Traffic:** `vehicle-guard-method-150` forces all guard vehicles to `(switch-zone-high! this)` on every cycle. If an ambient vehicle should roam both low and high traffic lanes naturally, ensure its `vehicle-method-120` delegates to `(method-of-type vehicle vehicle-method-120)` rather than `vehicle-guard`.

---

## 5. Passenger Ejection & Nav-Mesh Saturation

During `target-pilot-init`, the engine sends `'knocked-off` to **all seats** of the vehicle:
- For rear passenger / captive seats (e.g. `seat-index > 0`), the rider should return `#f` on `'knocked-off` to remain safely seated inside.
- When spawning ejected riders onto the ground, always verify `(when (-> gp-0 nav-mesh) ...)` before sending `'activate-object` to `*traffic-manager*` to prevent infinite spawn retry loops and memory exhaustion crashes.
