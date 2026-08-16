# Jak 1 — Declaring Scripts in Project File (`.gp`) / Déclarer un Script (`.gp`)

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Project Configuration Workflow

To register a new `.gc` file created under `goal_src/jak1/custom/`:
1. Open the project configuration file: `goal_src/jak1/jak1-game.gp`.
2. Add the file entry:
   ```
   (c "custom/my-script.gc")
   ```
3. Recompile via the REPL with `(mi)`.

---

# 🇫🇷 Version Française

## Workflow de Déclaration Projet

Pour faire reconnaître un nouveau fichier `.gc` créé sous `goal_src/jak1/custom/` :
1. Ouvrir le fichier projet : `goal_src/jak1/jak1-game.gp`.
2. Ajouter la ligne correspondant au fichier :
   ```
   (c "custom/my-script.gc")
   ```
3. Lancer la compilation dans le REPL avec `(mi)`.
