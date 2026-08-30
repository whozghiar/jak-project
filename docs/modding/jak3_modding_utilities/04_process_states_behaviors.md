# Jak 3 — Processes, States & Behaviors / Processus, États & Comportements

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Actor Architecture

Standard focusable actor structure in Jak 3:
```lisp
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag  uint32)
   (energy-level      float))
  (:state-methods
    idle
    patrol
    die)
  )
```

---

# 🇫🇷 Version Française

## Architecture des Acteurs

Structure standard d'un acteur focusable dans Jak 3 :
```lisp
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag  uint32)
   (energy-level      float))
  (:state-methods
    idle
    patrol
    die)
  )
```
