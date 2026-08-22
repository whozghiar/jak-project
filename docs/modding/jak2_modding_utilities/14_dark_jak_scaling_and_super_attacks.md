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

Because OpenGOAL couples character scaling across physics velocities (`ctrl-xz-vel`), animation bone scales, collision spheres, and damage penetration, understanding how to extend this pipeline unlocks seamless multi-tier transformations and robust super abilities.

---

## 2. Multi-Tier Progressive Scaling Architecture

### A. Stage Enumeration & State Transitions
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

In `target-darkjak.gc`, `want-to-darkjak?` determines whether an `L2` press triggers an initial transformation or evolves an existing active state:
```lisp
(defbehavior want-to-darkjak? target ()
  (and (cpad-pressed? (-> self control cpad number) l2)
       ;; ... standard filters ...
       (or (and (not (and (focus-test? self dark) (nonzero? (-> self darkjak))))
                (and (time-elapsed? (-> (the-as fact-info-target (-> self fact)) darkjak-start-time) (seconds 0.05))
                     (>= (-> self game eco-pill-dark) (-> *FACT-bank* eco-pill-dark-max-default))
                     )
                )
           ;; Allow transition until maximum evolutionary stage is reached:
           (and (and (focus-test? self dark) (nonzero? (-> self darkjak)))
                (not (and (focus-test? self dark)
                          (nonzero? (-> self darkjak))
                          (logtest? (-> self darkjak stage) (darkjak-stage mega-giant))
                          )
                     )
                (logtest? (game-feature darkjak-giant) (-> self game features))
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

## 3. Super Attack Optimization & Edge Cases

### A. Dark Bomb Velocity Gating (Preventing Jump Lockout)
In vanilla `target.gc`, jump states gate the `target-flop` (and Dark Bomb) transition behind hardcoded vertical velocity checks (`< 73728.0` and `< 22118.4`). Because scaled jump impulses exceed these bounds, `darkjak-giant-interp` must scale the thresholds, or Dark Jak must bypass the check directly for instant response:

```lisp
(if (and (recently-pressed? square)
         (or (and (focus-test? self dark) (nonzero? (-> self darkjak)))
             (and (< (vector-dot (-> self control dynam gravity-normal) (-> self control transv))
                     (* 73728.0 (-> self darkjak-giant-interp))
                     )
                  (< (* -61440.0 (-> self darkjak-giant-interp)) (vector-dot (-> self control dynam gravity-normal) (-> self control transv)))
                  )
             )
         ;; ...
         )
    (go target-flop ...)
    )
```

### B. Dark Blast Surface Abort Fix
`target-darkjak-bomb1` originally inherited `:trans` logic from `target-attack-uppercut-jump`, aborting into `target-hit-ground` whenever `collide-status on-surface` was true. This caused premature termination and an instant exit to normal Jak in confined spaces. Removing surface-grounding checks in `:trans` ensures the full barrage completes regardless of geometry.

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux
Dans Jak 2, la métamorphose de Dark Jak est gérée par une variable d'interpolation globale `darkjak-giant-interp` (`1.0` à `2.0` dans le code original) et l'énumération bitfield `darkjak-stage` dans [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

Le moteur OpenGOAL liant directement l'échelle du personnage à ses vitesses physiques (`ctrl-xz-vel`), aux échelles osseuses, aux sphères de collision et à la pénétration des dégâts, la compréhension de cette chaîne permet d'implémenter des évolutions multi-stades fluides et des super-attaques fiables.

---

## 2. Architecture de Mise à l'Échelle Multi-Stades

### A. Énumération des Stades & Transitions d'États
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

Dans `target-darkjak.gc`, la fonction `want-to-darkjak?` autorise l'évolution successive lors des appuis sur `L2` :
```lisp
(and (and (focus-test? self dark) (nonzero? (-> self darkjak)))
     (not (and (focus-test? self dark)
               (nonzero? (-> self darkjak))
               (logtest? (-> self darkjak stage) (darkjak-stage mega-giant))
               )
          )
     (logtest? (game-feature darkjak-giant) (-> self game features))
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

## 3. Optimisation des Super-Attaques & Cas Limites

### A. Vélocité de Déclenchement de la Dark Bomb
Dans `target.gc`, les états de saut verrouillent la transition vers le plongeon derrière des seuils de vitesse verticale stricts (`< 73728.0`). L'impulsion de saut étant multipliée en mode géant, ces seuils doivent être mis à l'échelle ou contournés pour Dark Jak afin de permettre un plongeon instantané.

### B. Fiabilisation du Dark Blast contre les Murs et Plafonds
`target-darkjak-bomb1` héritait à l'origine d'un test de contact au sol (`on-surface`) issu de l'uppercut classique, provoquant un arrêt immédiat de l'attaque et un retour prématuré à Jak normal dans les zones exiguës. La suppression de ce test dans `:trans` garantit l'exécution intégrale des tirs.
