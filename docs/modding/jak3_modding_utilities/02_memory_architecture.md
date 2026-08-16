# Jak 3 — Memory Architecture & Constants / Architecture Mémoire & Constantes

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Architecture & Memory Layout

* **Kernel Entry Point:** `goal_src/jak3/kernel/gcommon.gc` and `goal_src/jak3/engine/level/level.gc`.
* **Memory Budget (PC Extension):**
  - `END_OF_MEMORY`: configured to support 512 MB (`#x20000000`).
  - `DEBUG_LEVEL_HEAP_MULT`: level heap size multiplier in `level.gc` (default value: `15.0`).
* **Shared C++ Memory:** `EE_MAIN_MEM_SIZE` is shared in `common/goal_constants.h`.

---

# 🇫🇷 Version Française

## Architecture Mémoire & Constantes

* **Point d'Entrée Kernel :** `goal_src/jak3/kernel/gcommon.gc` et `goal_src/jak3/engine/level/level.gc`.
* **Budget Mémoire (Extension PC) :**
  - `END_OF_MEMORY` : configuré pour supporter 512 Mo (`#x20000000`).
  - `DEBUG_LEVEL_HEAP_MULT` : multiplicateur de taille du heap de niveau dans `level.gc` (valeur native : `15.0`).
* **Mémoire C++ Partagée :** `EE_MAIN_MEM_SIZE` est partagé dans `common/goal_constants.h`.
