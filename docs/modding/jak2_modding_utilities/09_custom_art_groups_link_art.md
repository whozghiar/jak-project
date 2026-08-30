# Jak 2 — Custom Art-Groups & Dynamic Animation Linking (`link-art!`) / Art-Groups Custom & Liaison Dynamique

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/jak3-jetBoard`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Custom Art-Groups: Dynamically Linking Imported Animations

### The Requirement
Add custom animations imported from a `.glb` into a resident character art-group (`jakb-ag`, `daxter-ag`) without modifying or recompiling the hundreds of native animations.

### The Engine Mechanism
1. `build-actor` (in `goal_src/jak2/game.gp`) uses `:master-art-group` and `:master-ag-map` to bake target slot indices into the compiled art-group.
2. `link-art!` (`loader.gc`) iterates through the custom group's entries and attaches pointers to the target slots in the master group.
3. `needs-link?` (`joint.gc`) only returns `#t` if slot 0 is an `art-joint-anim`. In `build-actor` outputs with a skeleton, slot 0 is a `joint-geo`, so `needs-link?` is always `#f`.

### ⚠️ Where to Hook `link-art!`
- ❌ **NEVER call `link-art!` during gameplay** (e.g. `target-board-init`): level art-group array states may be inconsistent, risking memory crashes.
- ✅ **The Correct Hook is `art-group::relocate`** in `goal_src/jak2/engine/anim/joint.gc`:
```lisp
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "jakb-jak3-board-import"))
      (link-art! this)))
```

---

# 🇫🇷 Version Française

## Art-Groups Custom : Lier des Animations Importées (`link-art!`)

### L'Objectif
Injecter des animations importées d'un `.glb` dans un art-group résident (`jakb-ag`, `daxter-ag`) sans modifier ni recompiler les centaines d'animations natives d'origine.

### Le Mécanisme Moteur
1. `build-actor` (dans `goal_src/jak2/game.gp`) utilise `:master-art-group` et `:master-ag-map` pour inscrire les index cibles dans l'art-group compilé.
2. `link-art!` (`loader.gc`) parcourt le groupe custom et attache les pointeurs d'animations dans les slots cibles du master group.
3. `needs-link?` (`joint.gc`) ne renvoie `#t` que si le slot 0 est un `art-joint-anim`. Dans les sorties de `build-actor` avec squelette, le slot 0 est un `joint-geo`, donc `needs-link?` renvoie `#f`.

### ⚠️ Où Accrocher `link-art!`
- ❌ **Ne JAMAIS appeler `link-art!` pendant le gameplay** (ex : `target-board-init`) : les tableaux d'art-groups en RAM ne sont pas dans un état stable, provoquant des plantages mémoire.
- ✅ **Le Bon Emplacement est `art-group::relocate`** dans `goal_src/jak2/engine/anim/joint.gc` :
```lisp
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "jakb-jak3-board-import"))
      (link-art! this)))
```
