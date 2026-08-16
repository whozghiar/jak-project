# Jak 2 — Known Pitfalls & Best Practices / Pièges Connus & Bonnes Pratiques

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/config/memory_increase`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Common Traps & Points of Vigilance

1. **Shared C++ Constants:** Modifying `GLOBAL_HEAP_END` affects Jak 1, 2, 3, and Jak X simultaneously.
2. **Boot Allocation Differences:** Available global heap budget varies per game depending on resident boot code.
3. **Always Validate at Runtime:** A change that compiles cleanly can still crash at runtime; always verify via `(mi)` -> boot -> log check.

---

# 🇫🇷 Version Française

## Pièges Fréquents & Points de Vigilance

1. **Constantes C++ Partagées :** Modifier `GLOBAL_HEAP_END` impacte simultanément Jak 1, 2, 3 et Jak X.
2. **Différences d'Allocation au Boot :** L'espace global heap disponible varie selon la quantité de code résident chargée au boot par chaque jeu.
3. **Validation Runtime Obligatoire :** Un changement qui compile sans erreur peut crasher à l'exécution ; toujours valider avec `(mi)` -> boot -> vérification des logs.
