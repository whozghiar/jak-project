# Jak 2 — Dark Jak Scaling, Multi-Tier Evolution & Super Attack Mechanics / Mise à l'Échelle de Dark Jak, Évolution Multi-Stades & Mécaniques des Super-Attaques

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/dark_jak_enhanced`
> - **Last Updated / Dernière modification:** `jak2/features/dark_jak_enhanced`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Context & Core Concepts

In Jak 2, Dark Jak's physical transformation is governed by an engine interpolation variable `darkjak-giant-interp` (ranging from `1.0` to `2.0` in retail code) and the `darkjak-stage` bitfield enum in [`goal_src/jak2/engine/target/target-h.gc`](../../../goal_src/jak2/engine/target/target-h.gc).

Because OpenGOAL couples character scaling across physics velocities (`ctrl-xz-vel`), animation bone scales, collision spheres, and damage penetration, understanding how to extend this pipeline unlocks seamless multi-tier transformations, acrobatic restoration, manual cancel controls, and robust super abilities.

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

## 3. Manual Cancel Control & Eco Consumption

### A. Universal Manual Revert (`R2`)

In `target-darkjak-post`, checking `(cpad-pressed? (-> self control cpad number) r2)` allows Jak to exit Dark Jak smoothly at any moment:

```lisp
(if (and (cpad-pressed? (-> self control cpad number) r2)
         (not (focus-test? self dead dangerous hit grabbed))
         (not (and (-> self next-state) (= (-> self next-state name) 'target-darkjak-get-off)))
         (not (logtest? (-> self darkjak stage) (darkjak-stage force-on)))
         )
    (go target-darkjak-get-off)
    )
```

### B. Full Eco Consumption on Exit

When Dark Jak ends (via `R2`, timeout, Dark Bomb, Dark Blast, or death), all remaining dark eco is consumed:

```lisp
(set! (-> self game eco-pill-dark) 0.0)
```

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Fondamentaux

Dans Jak 2, la métamorphose physique de Dark Jak est régie par une variable d'interpolation moteur `darkjak-giant-interp` (comprise entre `1.0` et `2.0` dans le code de base) et par l'énumération bitfield `darkjak-stage` dans [`goal_src/jak2/engine/target/target-h.gc`](../../../goal_src/jak2/engine/target/target-h.gc).

Comme OpenGOAL couple la mise à l'échelle du personnage à travers les vitesses physiques (`ctrl-xz-vel`), les échelles d'os d'animation, les sphères de collision et la pénétration des dégâts, la maîtrise de cette chaîne permet d'implémenter des transformations multi-stades fluides, la restauration des acrobaties, l'annulation manuelle des contrôles et des super-capacités fiabilisées.

---

## 2. Architecture de Mise à l'Échelle Progressive Multi-Stades

### A. Énumération des Stades & Transitions d'État Débloquées

L'énumération bitfield `darkjak-stage` peut être étendue sans risque avec de nouveaux paliers évolutifs (tel que `mega-giant`) :

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

Dans `target-darkjak.gc`, `want-to-darkjak?` autorise l'évolution progressive sur l'ensemble des paliers :

```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

### B. Requêtes de Collision « Headroom » & Décalages Progressifs de Caméra

Lors d'une expansion à une échelle colossale (ex. `3.5x`), les sphères de sonde de collision et les réglages de ressort de caméra sont mis à l'échelle proportionnellement :

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

## 3. Contrôle d'Annulation Manuelle & Consommation d'Éco

### A. Annulation Manuelle Universelle (`R2`)

Dans `target-darkjak-post`, la détection de `(cpad-pressed? (-> self control cpad number) r2)` permet à Jak de quitter Dark Jak proprement à n'importe quel moment :

```lisp
(if (and (cpad-pressed? (-> self control cpad number) r2)
         (not (focus-test? self dead dangerous hit grabbed))
         (not (and (-> self next-state) (= (-> self next-state name) 'target-darkjak-get-off)))
         (not (logtest? (-> self darkjak stage) (darkjak-stage force-on)))
         )
    (go target-darkjak-get-off)
    )
```

### B. Consommation Complète de l'Éco à la Sortie

Dès que Dark Jak se termine (via `R2`, expiration du timer, Dark Bomb, Dark Blast ou mort), toute l'éco noire restante est consommée :

```lisp
(set! (-> self game eco-pill-dark) 0.0)
```
