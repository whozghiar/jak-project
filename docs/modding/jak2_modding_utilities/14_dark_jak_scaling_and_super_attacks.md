# 14. Dark Jak Scaling, Multi-Tier Evolution & Super Attack Mechanics / Mise à l'Échelle de Dark Jak, Évolution Multi-Stades & Mécaniques des Super-Attaques

> - **Origin / Provenance:** `jak2/features/dark_jak_enhanced`
> - **Last Updated / Dernière modification:** `jak2/features/dark_jak_enhanced` (AI-assisted)

---

- [🇬🇧 English Version](#-english-version)
- [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Context & Core Concepts
In Jak 2, Dark Jak's physical transformation is governed by an engine interpolation variable `darkjak-giant-interp` (ranging from `1.0` to `2.0` in retail code) and the `darkjak-stage` bitfield enum in [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

Because OpenGOAL couples character scaling across physics velocities (`ctrl-xz-vel`), animation bone scales, collision spheres, and damage penetration, understanding how to extend this pipeline unlocks seamless multi-tier transformations, acrobatic restoration, proportional resource management, dedicated HUD timer bars, and robust super abilities.

---

## 2. Multi-Tier Progressive Scaling Architecture

### A. Stage Enumeration & Unlocked State Transitions
The `darkjak-stage` bitfield enum can be safely extended with new evolutionary tiers (such as `mega-giant`):

```lisp
(defenum darkjak-stage
  :bitfield #t
  :type uint32
  (force-on)
  (active)
  (bomb0)
  (bomb1)
  (invinc)
  (giant)
  (no-anim)
  (disable-force-on)
  (mega-giant)
  )
```

In `target-darkjak.gc`, `want-to-darkjak?` allows progressive evolution across all tiers:
```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

### B. Headroom Collision Queries & Progressive Camera Offsets
When expanding to a colossal scale (e.g. `3.5x`), collision probe spheres and camera spring settings scale proportionally:

```lisp
(let* ((already-giant? (logtest? (-> self darkjak stage) (darkjak-stage giant)))
       (target-scale (if already-giant? 3.5 2.0))
       (start-scale (if already-giant? (-> self darkjak-giant-interp) 1.0))
       )
  (+! (-> s5-1 0 y) (if already-giant? 22000.0 12697.6))
  (set! (-> s5-1 0 r) (if already-giant? 18000.0 11878.4))
  )
```

---

## 3. Dedicated HUD Timer Bar & Super Attacks

### A. Dedicated Purple Countdown Timer Bar
To leave the circular Dark Eco gauge pristine, an independent horizontal timer bar is rendered via unused sprites in `hud-dark-eco-symbol draw`:

```lisp
(if (and *target* (focus-test? *target* dark) (nonzero? (-> *target* darkjak)))
    (let* ((elapsed (- (current-time) (-> (the-as fact-info-target (-> *target* fact)) darkjak-start-time)))
           (total (-> (the-as fact-info-target (-> *target* fact)) darkjak-effect-time))
           (ratio (if (-> *setting-control* user-current darkjak) 1.0 (fmax 0.0 (/ (the float (- total elapsed)) (the float total)))))
           (bar-x (if (= (-> *setting-control* user-default aspect-ratio) 'aspect4x3) (the int (+ 22.0 (* -130.0 f30-0))) (the int (+ 32.0 (* -130.0 f30-0)))))
           (bar-y (the int (+ 294.0 (* 130.0 f30-0))))
           )
      ;; Background Track
      (set-hud-piece-position! (-> this sprites 1) bar-x bar-y)
      (set! (-> this sprites 1 tex) (get-texture hud-health-bar-lit-02 level-default-minimap))
      (set! (-> this sprites 1 scale-x) 3.5)
      (set! (-> this sprites 1 scale-y) 0.8)
      (set! (-> this sprites 1 color x) 45)
      (set! (-> this sprites 1 color y) 10)
      (set! (-> this sprites 1 color z) 65)
      (set! (-> this sprites 1 color w) 128)
      (set! (-> this sprites 1 pos z) #xfffff8)
      ;; Foreground Purple Fill
      (set-hud-piece-position! (-> this sprites 2) bar-x bar-y)
      (set! (-> this sprites 2 tex) (get-texture hud-health-bar-lit level-default-minimap))
      (set! (-> this sprites 2 scale-x) (* 3.5 ratio))
      (set! (-> this sprites 2 scale-y) 0.8)
      (set! (-> this sprites 2 color x) 190)
      (set! (-> this sprites 2 color y) 40)
      (set! (-> this sprites 2 color z) 255)
      (set! (-> this sprites 2 color w) 128)
      (set! (-> this sprites 2 pos z) #xfffff9)
      )
    (begin
      (set! (-> this sprites 1 scale-x) 0.0)
      (set! (-> this sprites 2 scale-x) 0.0)
      )
    )
```

### B. Full Eco Consumption on Super Attacks
When triggering Dark Bomb or Dark Blast, `eco-pill-dark` is zeroed out to consume 100% of the player's dark eco:
```lisp
(set! (-> self game eco-pill-dark) 0.0)
```

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux
Dans Jak 2, la métamorphose de Dark Jak est régie par `darkjak-giant-interp` (`1.0` à `2.0` dans le code de base) et l'énumération bitfield `darkjak-stage` dans [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

La maîtrise de cette chaîne permet d'implémenter des évolutions multi-stades, une barre de décompte dédiée dans l'HUD et une consommation totale de l'éco sur les attaques spéciales.

---

## 2. Architecture de Mise à l'Échelle Multi-Stades

### A. Évolution Débloquée
```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

---

## 3. Barre de Compte à Rebours Dédiée & Super-Attaques

### A. Barre Violette Horizontale dans l'HUD
Afin de préserver la jauge circulaire d'éco noire originale, une barre horizontale violette autonome est dessinée dans `hud-dark-eco-symbol draw` avec un fond sombre et un remplissage lumineux qui s'ajuste au ratio du temps restant.

### B. Consommation Totale de l'Éco sur Super-Attaques
Lors du déclenchement d'une Dark Bomb ou d'un Dark Blast, la réserve d'éco noire est immédiatement réinitialisée à `0.0`.
