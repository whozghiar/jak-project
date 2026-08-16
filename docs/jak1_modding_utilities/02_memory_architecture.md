# Jak 1 — Memory Architecture & Constants / Architecture Mémoire & Constantes

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Architecture & Core Constants

* **Kernel Entry Point:** `goal_src/jak1/kernel/gcommon.gc` and `goal_src/jak1/engine/level/level.gc`.
* **Address Validation (`valid?`):** `END_OF_MEMORY` in `goal_src/jak1/kernel/gcommon.gc` protects pointer dereferencing across memory bounds.
* **Shared C++ Memory:** `EE_MAIN_MEM_SIZE` is defined in `common/goal_constants.h` and allocated by the C++ runtime via `mmap`.

---

# 🇫🇷 Version Française

## Architecture & Constantes Fondamentales

* **Point d'Entrée Kernel :** `goal_src/jak1/kernel/gcommon.gc` et `goal_src/jak1/engine/level/level.gc`.
* **Vérification d'Adresses (`valid?`) :** `END_OF_MEMORY` dans `goal_src/jak1/kernel/gcommon.gc` sécurise les déréférencements de pointeurs.
* **Mémoire C++ Partagée :** `EE_MAIN_MEM_SIZE` est défini dans `common/goal_constants.h` et alloué via le runtime C++ via `mmap`.
