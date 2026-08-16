# Jak 3 — Declaring Scripts in Project File (`.gp`) / Déclarer un Script (`.gp`)

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Project Configuration

To add a new `.gc` script to the Jak 3 build tree:
1. Locate the configuration `.gp` file (e.g. `goal_src/jak3/jak3-game.gp`).
2. Add the path to the new script:
   ```
   (c "custom/my-jak3-mod.gc")
   ```
3. Recompile in the REPL with `(mi)`.

---

# 🇫🇷 Version Française

## Configuration du Projet

Pour ajouter un nouveau fichier `.gc` dans l'arbre de compilation de Jak 3 :
1. Localiser le fichier `.gp` de configuration (ex: `goal_src/jak3/jak3-game.gp`).
2. Ajouter le chemin vers le nouveau script :
   ```
   (c "custom/my-jak3-mod.gc")
   ```
3. Recompiler dans le REPL avec `(mi)`.
