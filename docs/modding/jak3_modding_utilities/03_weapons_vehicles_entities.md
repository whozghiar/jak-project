# Jak 3 — Weapons, Vehicles & Entities / Armes, Véhicules & Entités

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Weapon and Vehicle Systems

### Weapon System (`gun`)
Weapon properties, ammo counts, and projectile configurations are accessed through the target process:
```lisp
(when *target*
  (let ((gun (-> *target* gun)))
    ;; Access weapon firing modes, ammo counts, morph attachments
    ))
```

### Vehicles & Physics
* Wasteland buggy and vehicle actors derive from `vehicle` (`goal_src/jak3/engine/vehicle/`).
* Dynamic suspension, tire friction, and torque resolution execute every tick via specialized behavior routines.

---

# 🇫🇷 Version Française

## Systèmes d'Armes & Véhicules

### Système d'Armes (`gun`)
L'état de l'arme, les munitions et le morphing s'interrogent via le processus joueur :
```lisp
(when *target*
  (let ((gun (-> *target* gun)))
    ;; Accès aux propriétés de tir, munitions, type d'arme
    ))
```

### Véhicules & Physique
* Les véhicules du désert dérivent de la hiérarchie `vehicle` (`goal_src/jak3/engine/vehicle/`).
* Les forces de suspension, frottement et adhérence sont résolues à chaque cycle via des behaviors dédiés.
