# Jak 3 — Skeleton, Joints & Animations / Squelette, Joints & Animations

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Skeletons & Animation System

* **Animation Pipeline:** Managed by `merc` / `mips2c` for skinning and skeletal evaluations.
* **Direct Joint Transform Access:** Joint transformation matrices can be read and manipulated via `(-> self node-list data [index] bone transform)`.
* **Animation Scrubbing:**
  ```lisp
  (ja :num! (seek!))
  (suspend)
  ```

---

# 🇫🇷 Version Française

## Squelette & Système d'Animation

* **Moteur d'Animation :** Système `merc` / `mips2c` pour le calcul squelettique et le rendu.
* **Accès Direct aux Joints :** Les matrices de transformation sont accessibles via `(-> self node-list data [index] bone transform)`.
* **Avancement de l'Animation :**
  ```lisp
  (ja :num! (seek!))
  (suspend)
  ```
