# Jak 1 — Skeleton, Joints & Animations / Squelette, Joints & Animations

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Joints & Animation Control

* **Joint Subsystem:** Managed by `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
* **Common Animation Macros:**
  - `(ja-no-eval :group! ... :num! (seek!) :frame-num 0.0)`: Starts animation playback from frame 0.
  - `(ja :num! (seek!))`: Advances the active animation frame.
  - `(ja-done? 0)`: Evaluates whether channel 0 reached the end of its sequence.
  - `(suspend)`: Yields execution back to the game engine for the current frame.

---

# 🇫🇷 Version Française

## Squelette & Contrôle d'Animation

* **Sous-Système d'Os & Joints :** Géré par `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
* **Macros d'Animation Courantes :**
  - `(ja-no-eval :group! ... :num! (seek!) :frame-num 0.0)` : Lance une animation à la frame 0.
  - `(ja :num! (seek!))` : Fait avancer la frame courante d'animation.
  - `(ja-done? 0)` : Vérifie si le canal d'animation 0 a terminé son cycle.
  - `(suspend)` : Rend la main au moteur pour la frame courante (équivalent d'un `yield`).
