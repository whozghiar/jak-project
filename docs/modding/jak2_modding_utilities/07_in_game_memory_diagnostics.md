# Jak 2 — In-Game Memory Diagnostics / Outils de Diagnostic Mémoire en Jeu

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/config/memory_increase`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Live Memory Diagnostics

To display the live memory overlay in `-debug` mode:
```lisp
(set! *stats-memory* #t)
```
This prints the real-time breakdown of textures, collision, animations, and level heap usage per loaded sector.

---

# 🇫🇷 Version Française

## Diagnostic Mémoire en Temps Réel

Pour afficher l'overlay mémoire en temps réel (mode `-debug`) :
```lisp
(set! *stats-memory* #t)
```
Affiche la répartition exacte des textures, collisions, animations et l'espace restant sur le level heap pour chaque niveau chargé.
