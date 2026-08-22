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

Because OpenGOAL couples character scaling across physics velocities (`ctrl-xz-vel`), animation bone scales, collision spheres, and damage penetration, understanding how to extend this pipeline unlocks seamless multi-tier transformations, acrobatic restoration, proportional resource management, and robust super abilities.

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

In `target-darkjak.gc`, `want-to-darkjak?` determines whether an `L2` press triggers an initial transformation or evolves an existing active state without gating behind story cheats:
```lisp
(defbehavior want-to-darkjak? target ()
  (and (cpad-pressed? (-> self control cpad number) l2)
       ;; ... standard filters ...
       (or (and (not (and (focus-test? self dark) (nonzero? (-> self darkjak))))
                (and (time-elapsed? (-> (the-as fact-info-target (-> self fact)) darkjak-start-time) (seconds 0.05))
                     (>= (-> self game eco-pill-dark) (-> *FACT-bank* eco-pill-dark-max-default))
                     )
                )
           ;; Allow progressive evolution to giant & mega-giant in all game modes:
           (and (focus-test? self dark)
                (nonzero? (-> self darkjak))
                (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
                )
           )
       )
  )
```

### B. Headroom Collision Queries & Progressive Camera Offsets
When expanding to a colossal scale (e.g. `3.5x`), the collision probe sphere and camera spring settings must scale proportionally:

```lisp
(let* ((already-giant? (logtest? (-> self darkjak stage) (darkjak-stage giant)))
       (target-scale (if already-giant? 3.5 2.0))
       (start-scale (if already-giant? (-> self darkjak-giant-interp) 1.0))
       )
  ;; Headroom probe:
  (+! (-> s5-1 0 y) (if already-giant? 22000.0 12697.6))
  (set! (-> s5-1 0 r) (if already-giant? 18000.0 11878.4))
  
  ;; Panoramic camera parameters:
  (when gp-2
    (if already-giant?
        (begin
          (set-setting! 'string-min-length 'rel 3.2 0)
          (set-setting! 'string-max-length 'rel 2.8 0)
          (set-setting! 'string-spline-max-move 'abs (meters 4.5) 0)
          (set-setting! 'string-spline-accel 'abs (meters 0.09) 0)
          )
        (begin
          (set-setting! 'string-min-length 'rel 1.8 0)
          (set-setting! 'string-max-length 'rel 1.5 0)
          )
        )
    )
  )
```

---

## 3. Resource Management, HUD & Locomotion

### A. Proportional Real-Time Eco Drain & `R2` Early Cancel
Rather than immediately zeroing out `eco-pill-dark` on transformation start, dark eco is drained proportionally in real-time. If the player interrupts Dark Jak early using `R2`, the remaining dark eco is preserved:

```lisp
;; In target-darkjak-process (target-darkjak.gc):
(when (not (-> *setting-control* user-current darkjak))
  (let* ((elapsed (- (current-time) (-> (the-as fact-info-target (-> self fact)) darkjak-start-time)))
         (total (-> (the-as fact-info-target (-> self fact)) darkjak-effect-time))
         (remaining-ratio (fmax 0.0 (/ (the float (- total elapsed)) (the float total))))
         )
    (set! (-> self game eco-pill-dark) (* (-> *FACT-bank* eco-pill-dark-max-default) remaining-ratio))
    )
  )
```

### B. HUD Countdown Meter & Icon Scaling
Scaling `hud-darkjak-head-01` to `1.0` inside `hud-dark-eco-symbol draw` ensures the circular purple gauge is clearly readable without clipping or visual obstruction.

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux
Dans Jak 2, la métamorphose de Dark Jak est gérée par une variable d'interpolation globale `darkjak-giant-interp` (`1.0` à `2.0` dans le code original) et l'énumération bitfield `darkjak-stage` dans [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

Le moteur OpenGOAL liant directement l'échelle du personnage à ses vitesses physiques (`ctrl-xz-vel`), aux échelles osseuses, aux sphères de collision et à la pénétration des dégâts, la compréhension de cette chaîne permet d'implémenter des évolutions multi-stades fluides, une gestion proportionnelle des ressources d'éco et des super-attaques fiabilisées.

---

## 2. Architecture de Mise à l'Échelle Multi-Stades

### A. Énumération des Stades & Évolution Débloquée
L'énumération bitfield `darkjak-stage` peut être étendue sans risque :

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

Dans `target-darkjak.gc`, la fonction `want-to-darkjak?` autorise l'évolution successive sans blocage lié aux secrets :
```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

### B. Test d'Espace Libre (Headroom) & Caméra Panoramique
Lors d'une mise à l'échelle colossale (ex: `3.5x`), les sphères de test de collision et les paramètres de ressort de caméra sont ajustés :

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

## 3. Gestion Proportionnelle des Ressources & HUD

### A. Drain Proportionnel d'Éco & Annulation Précoce (`R2`)
Au lieu de vider instantanément l'éco noire lors de l'activation, l'éco diminue progressivement au fil du temps. Une interruption prématurée via `R2` permet à Jak de conserver toute l'éco restante :

```lisp
;; Dans target-darkjak-process (target-darkjak.gc) :
(when (not (-> *setting-control* user-current darkjak))
  (let* ((elapsed (- (current-time) (-> (the-as fact-info-target (-> self fact)) darkjak-start-time)))
         (total (-> (the-as fact-info-target (-> self fact)) darkjak-effect-time))
         (remaining-ratio (fmax 0.0 (/ (the float (- total elapsed)) (the float total))))
         )
    (set! (-> self game eco-pill-dark) (* (-> *FACT-bank* eco-pill-dark-max-default) remaining-ratio))
    )
  )
```

### B. Ajustement de l'Icône de Tête HUD
La mise à l'échelle à `1.0` de la tête de Dark Jak dans `hud-dark-eco-symbol draw` permet de laisser la jauge circulaire violette parfaitement lisible à l'écran.
