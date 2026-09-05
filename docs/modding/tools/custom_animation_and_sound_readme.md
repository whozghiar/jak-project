# Jak 2 — Custom Model & Sound Import / Import de Modèle & Son Custom

> **Mod Readme / Readme du Mod**
>
> - **Branch / Branche :** `jak2/config/custom_animation_and_sound`
> - **Type :** `config` (tooling + engine hooks / outillage + hooks moteur)
> - **Depends on / Dépend de :** `retarget_anim`, `build_sbk`, `extract_sbk`, `build-actor2`
>   (tous déjà présents sur cette branche / all already present on this branch)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)
>
> Companion knowledge-base tips (read them too) /
> Fiches de connaissances associées (à lire également) :
> [`../jak2_modding_utilities/13_custom_animation_and_sound_import_pipeline.md`](../jak2_modding_utilities/13_custom_animation_and_sound_import_pipeline.md),
> [`../jak2_modding_utilities/10_gltf_retargeting_build_actor.md`](../jak2_modding_utilities/10_gltf_retargeting_build_actor.md),
> [`../jak2_modding_utilities/09_custom_art_groups_link_art.md`](../jak2_modding_utilities/09_custom_art_groups_link_art.md).

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## 1. Features

This branch makes it possible to ship, in a Jak 2 mod, **assets that do not exist in the retail
game**: a brand-new 3D model (`.glb`) turned into a real GOAL actor, and brand-new sound effects
added to a sound bank.

It provides:

| Piece | Where | Status |
|---|---|---|
| `build-actor` (`build-actor2` tool) with `:master-art-group` / `:master-ag-map` / `:framerate` / `:joint-channel` | `goal_src/jak2/lib/project-lib.gp` | pre-existing |
| `retarget_anim` — CLI that retargets GLTF animation curves onto a native skeleton by bone name | `goalc/retarget_anim/` | pre-existing |
| `extract_sbk` — decompiler pass: rip `.SBK` banks to `.wav` + `metadata.txt` | `decompiler/data/extract_sbk.cpp` (`rip_sound_banks`) | pre-existing |
| `build_sbk` / `append_sbk` — rebuild a bank / append sounds into an existing bank | `goalc/build_sbk/` | pre-existing |
| `append-sbk` macro | `goal_src/jak2/lib/project-lib.gp` | pre-existing |
| **`build-sbk` macro** (create a self-contained new `.SBK`) | `goal_src/jak2/lib/project-lib.gp` | **added on this branch** |
| **Generic custom art-group link hook** (`register-custom-art-group`) | `goal_src/jak2/engine/anim/joint.gc` + `level.gc` | **added on this branch** |

The two additions are the "last mile": everything else was already here but you still had to
hand-patch `joint.gc` with a hard-coded art-group name (see tip 09) for custom animations to link,
and there was no macro to build a fresh bank.

---

## 2. Prerequisites

Before you start, you need:

1. **A working OpenGOAL dev setup for Jak 2**
   - `iso_data/jak2/` populated (retail ISO extracted).
   - `task set-game-jak2` then `task extract` at least once → `decompiler_out/jak2/` present.
   - `task build-release` (or `build-debug`) → `goalc`, `gk`, and the standalone tools built.

2. **The standalone import tools built** (they are separate CMake targets, seconds to build):
   ```bash
   cmake --build out/build/Release --target retarget_anim --config Release
   cmake --build out/build/Release --target build_sbk    --config Release
   cmake --build out/build/Release --target build_actor   --config Release
   ```

3. **Blender 2.83+** with the two plugins from `custom_assets/blender_plugins/`:
   - `opengoal.py` (mesh tools, PAT surfaces, vertex-colour bake helpers)
   - `gltf2_blender_extract.py` (drop-in replacement for Blender's glTF exporter extract module —
     needed so joint/vertex-colour data export in the layout `build-actor` expects)
   Install `opengoal.py` via *Edit → Preferences → Add-ons → Install*, and copy
   `gltf2_blender_extract.py` over the file of the same name inside your Blender install's
   `scripts/addons/io_scene_gltf2/blender/exp/` folder.

4. **Source assets**
   - *Model*: a `.glb` with a skeleton whose **joint 0 is named `align`** (see tip 10 — the
     off-by-one pitfall). The safest base is a decompiled native skeleton
     (`decompiler_out/jak2/levels/**/<name>-lod0.glb`); build your mesh onto it, or model from
     scratch but keep the `align` root.
   - *Sounds*: `.wav` files (PCM) + a `metadata.txt` describing the sounds/grains, in the exact
     layout the decompiler's `extract_sbk` produces. The easiest way to get a correct
     `metadata.txt` is to extract an existing bank and edit it.

5. **To extract reference sound banks** (once), flip `rip_sound_banks` on:
   ```bash
   ./out/build/Release/bin/decompiler ./decompiler/config/jak2/jak2_config.jsonc ./iso_data ./decompiler_out \
     --version ntscv1 --config-override '{"decompile_code": false, "levels_extract": true, "rip_sound_banks": true}'
   ```
   → `decompiler_out/jak2/audio/sfx/<BANK>/metadata.txt` + `.wav` files.

6. **To extract reference animations / skeletons**, use `task rip-levels` (sets `rip_levels`) →
   `decompiler_out/jak2/levels/<level>/<art-group>-lod0.glb` with the native animations baked in
   as GLTF keyframes.

---

## 3. Procedure — Adding a Custom Model

A custom model becomes a **standalone GOAL actor** (its own `art-group`, `skeleton-group`, and
`process` type). There are two delivery routes:

- **Route A — custom level actor** (fully supported, no engine change): the actor is part of a
  custom level built with `build-custom-level`. Use this if the model only needs to appear in your
  own level.
- **Route B — global actor** (available everywhere, like the native jetboard): the art-group is
  added to a resident DGO. Use this for a feature that touches the whole game.

### 3.1 Author the model (Blender)

1. Open the base skeleton GLB (or start from your own, root joint **named `align`**).
2. Build/skin your mesh. One material per texture; keep vertex colours if you baked lighting.
3. If you want custom **animations**: animate the actions you need, name each action exactly as you
   will reference it in code.
4. Export as **glTF Binary (`.glb`)** with the OpenGOAL exporter plugin active.
5. Save to:
   ```
   custom_assets/jak2/models/custom_levels/<name>.glb
   ```

### 3.2 Declare it with `build-actor`

In `goal_src/jak2/game.gp` (near the existing `(build-actor "test-actor" ...)`):

```lisp
;; static prop / new creature with its own animations:
(build-actor "my-actor" :gen-mesh #t :force-run #t)

;; OR: custom animations meant for an EXISTING character (jakb, daxter, ...):
(build-actor "my-jak-anims"
             :force-run #t
             :framerate 60
             :joint-channel 24
             :master-art-group jakb
             :master-ag-map ((my-run-anim 330) (my-wave-anim 331)))
```

`:master-ag-map` pairs are `(anim-name master-slot-index)`. Pick **free** slots in the target
art-group (inspect it in-game or check `art-elts.gc`). This bakes `master-art-group-name` /
`master-art-group-index` into the compiled `art-joint-anim`.

Output: `out/jak2/obj/<name>-ag.go`.

### 3.3 Put the art-group into a DGO

- **Route A (custom level):** add the model name to your level's `.jsonc`
  (`"custom_models": ["my-actor"]`) **and** to the level `.gd` file
  (`"my-actor-ag.go"`), exactly like `test-actor` in `custom_assets/jak2/levels/test-zone/`.

- **Route B (global):** add one line to `goal_src/jak2/dgos/art.gd`, next to `jakb-ag.go` /
  `board-ag.go`:
  ```
  "my-actor-ag.go"
  ```
  This is append-only; do not remove anything.

### 3.4 Write the GOAL actor

Create `goal_src/jak2/<path>/my-actor.gc` (register it in `game.gp` **and** the matching `.gd`).
Minimal shape (see `test-zone-obs.gc` for a complete example):

```lisp
(in-package goal)

(deftype my-actor (process-drawable)
  ((root collide-shape-moving :override)))

;; def-actor auto-generates: <name>-ag art-elts, joint-node names, and *my-actor-sg*
(def-actor my-actor
  :bounds (0 0 0 5)
  :art (my-actor-idle-ja)                 ;; animation symbols, in art-group slot order
  :joints (align prejoint main ...))      ;; joint names as in the GLB skeleton

(defmethod init-from-entity! ((this my-actor) (e entity-actor))
  (process-drawable-from-entity! this e)
  (initialize-skeleton this *my-actor-sg* '())
  (go-virtual idle :proc this)
  (none))

(defstate idle (my-actor)
  :virtual #t
  :code (behavior () (loop (ja-no-eval :group! (ja-group) :num! (loop!)) (suspend))))
```

### 3.5 If the model carries animations for an existing character — register the link

An art-group built with `:master-art-group` has a `joint-geo` at slot 0, so the stock
`needs-link?` returns `#f` and its animations would never splice into the master art-group. On this
branch you no longer hand-patch `joint.gc` — instead, from a **top-level form** in your mod `.gc`:

```lisp
;; runs once at boot; the name is the string passed to build-actor, WITHOUT "-ag"
(register-custom-art-group "my-jak-anims")
```

Order does not matter — the list is only consulted at level login (`art-group::relocate` and the
level-load path in `level.gc`). Standalone actors that keep animations in their own art-group do
**not** need this.

### 3.6 Compile & test

Pure GOAL change (unless you touched C++): `./goalc.exe --game jak2 -c "(mi)"` then boot. If you
touched C++ (`game/**`), rebuild the engine first (`task build-release`).

---

## 4. Procedure — Adding Custom Sounds

### 4.1 Prepare the source folder

```
custom_assets/jak2/sounds/sfx/MYSOUNDS/
├── metadata.txt          # sound + grain description (extract_sbk layout)
├── MY_SOUND_A.wav
└── MY_SOUND_B.wav
```

Get a valid `metadata.txt` by extracting a real bank (Prerequisite 5) and editing it: add your
sound blocks, point the `TONE` grains at your `.wav` files, keep the header lines consistent.

### 4.2 Choose the delivery route

- **Route A — append onto `COMMON` (recommended for global sounds).**
  `COMMON.SBK` is always resident and allocated under the special-cased `common` slot, so nothing
  else is needed at runtime.
  In `goal_src/jak2/game.gp`:
  1. **Remove `"COMMON"`** from the `(copy-sbk-files ...)` list (otherwise two build steps produce
     `$OUT/iso/COMMON.SBK` and the make system errors with *"multiple ways to make output"*).
  2. Add:
     ```lisp
     (append-sbk "COMMON" "MYSOUNDS" :force-run #t)
     ;; optional: restrict to some names
     ;; (append-sbk "COMMON" "MYSOUNDS" :only-names (MY_SOUND_A MY_SOUND_B))
     ```

- **Route B — a brand-new self-contained bank (`build-sbk`).**
  ```lisp
  (build-sbk "MYSOUNDS" "MYSOUNDS" :force-run #t :bank-id #x6d79736e)
  ```
  This writes `$OUT/iso/MYSOUNDS.SBK`. ⚠️ At runtime it needs a **free overlord sound-bank slot**.
  Jak 2 has three dedicated slots (`common`, `gun`, `board`) plus a 3-slot rotating pool used by
  level banks. A new name falls into the rotating pool and will fight with level sounds. Only use
  Route B for a **custom level** bank (loaded/unloaded with the level), or add a dedicated slot in
  `game/overlord/common/sbank.cpp` (`N_BANKS`, a new `gXxxBank`, an `AllocateBankName` case, an SPU
  location/size) — that is a C++ engine change and out of scope for this branch.

### 4.3 Verify the bank binary (before booting)

`append_sbk` / `build_sbk` write a real PS2 SPU-ADPCM bank. A quick Python script over the raw
`.SBK` bytes (12-byte-ish header, sound table, grain table) catches a malformed layout instantly —
see tip 13 §B1 / §C3. Do this before spending a boot.

### 4.4 Load & trigger

- **Route A:** nothing to load — the sounds are in `COMMON`, play them directly.
- **Route B:** load the bank once it is needed:
  ```lisp
  (sound-bank-load (static-sound-name "MYSOUNDS"))
  ```
- Trigger from GOAL, same as any native sound:
  ```lisp
  (sound-play "my-sound-a")
  ;; or, for a positioned / updatable sound:
  (sound-play-by-name (static-sound-name "my-sound-a") (new-sound-id) 1024 0 0 (sound-group sfx) (-> self root trans))
  ```
  For a **looping / per-frame-updated** sound, pre-allocate its id with `(new-sound-id)` **once** in
  the owning object's `-init` (tip 13 §B3) — `sound-play-by-name` never generates one.

---

## 5. The Engine Changes Made on This Branch

| File | Change | Why |
|---|---|---|
| `goal_src/jak2/engine/anim/joint.gc` | `*custom-art-groups-to-link*` list + `register-custom-art-group` + `custom-art-group-to-link?` ; `art-group::relocate` now links when either `needs-link?` **or** `custom-art-group-to-link?` is true | replace the per-mod hard-coded art-group name from tip 09 with an opt-in registry; zero cost when nothing is registered |
| `goal_src/jak2/engine/level/level.gc` | same `(or (needs-link? …) (custom-art-group-to-link? …))` guard on the level-load art-group linking path | custom-level actors login through `level.gc`, not `relocate` |
| `goal_src/jak2/lib/project-lib.gp` | new `build-sbk` macro (wraps the existing `build-sbk` make tool) | there was only `append-sbk`; no way to declare a fresh bank |

All changes are additive — no native file is emptied, no method is removed.

---

## 6. How to Test

1. `./goalc.exe --game jak2 -c "(mi)"` — must reach *"Successfully built all N targets"*.
2. **Model (Route A):** boot into `test-zone` (or your level), confirm the actor spawns with the
   right mesh and its idle animation plays without the mesh dislocating (dislocation ⇒ joint
   off-by-one, tip 10).
3. **Model (Route B):** boot any level, spawn your actor via the debug spawn menu or a script,
   same visual checks.
4. **Custom anims on jakb/daxter:** boot, trigger the state that plays the imported clip, check the
   `log/jak2.<ts>.log` for `could not find a master slot to link` — its absence means the link
   worked.
5. **Sounds (Route A):** boot, trigger the sound; grep the log for sound-loader errors.
6. Regression: boot a couple of untouched levels and confirm no new `link-art` / sound-bank errors
   in the log (the guards must not affect native art-groups).

---

## 7. Status

| Item | State |
|---|---|
| `build-actor2` with master art-group | ✅ working (pre-existing) |
| Generic `register-custom-art-group` link hook | ✅ added, compiles (`(mi)` green, 936 targets) |
| `build-sbk` macro | ✅ added, compiles |
| `append-sbk` onto `COMMON` | ⚠️ path documented; needs a real end-to-end test with a sample bank |
| Dedicated new sound-bank slot (Route B, global) | ❌ not done — needs a C++ `sbank.cpp` change |
| Worked example (sample `.glb` + sample sounds) | ❌ not included — this branch ships the capability, not a demo asset |

---

## 8. Modding Changes Log

| Date | File | Change | Rationale |
|---|---|---|---|
| 2026-08-30 | `goal_src/jak2/engine/anim/joint.gc` | Added `*custom-art-groups-to-link*`, `register-custom-art-group`, `custom-art-group-to-link?`; `relocate` links on `(or (needs-link? this) (custom-art-group-to-link? this))` | Generic, opt-in replacement for the hard-coded art-group name hack (tip 09) so imported animations on native characters link at load time |
| 2026-08-30 | `goal_src/jak2/engine/level/level.gc` | Added `custom-art-group-to-link?` to the level-load art-group link guard | Custom-level actors log in via `level.gc`, not `art-group::relocate` |
| 2026-08-30 | `goal_src/jak2/lib/project-lib.gp` | Added `build-sbk` macro (create a standalone `.SBK` from a `metadata.txt` + wav folder) | `append-sbk` existed but there was no macro to declare a brand-new bank |
| 2026-08-30 | `docs/modding/current_mod/custom_animation_and_sound_readme.md` | This document | Procedure + prerequisites for importing a custom model and custom sounds into Jak 2 |

---
---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## 1. Fonctionnalités

Cette branche permet de livrer, dans un mod Jak 2, des **assets qui n'existent pas dans le jeu
commercial** : un modèle 3D neuf (`.glb`) transformé en véritable acteur GOAL, et des effets
sonores neufs ajoutés à une banque de sons.

Elle fournit :

| Élément | Emplacement | Statut |
|---|---|---|
| `build-actor` (outil `build-actor2`) avec `:master-art-group` / `:master-ag-map` / `:framerate` / `:joint-channel` | `goal_src/jak2/lib/project-lib.gp` | pré-existant |
| `retarget_anim` — CLI qui recible des courbes d'animation GLTF sur un squelette natif par nom d'os | `goalc/retarget_anim/` | pré-existant |
| `extract_sbk` — passe décompilateur : extrait les banques `.SBK` en `.wav` + `metadata.txt` | `decompiler/data/extract_sbk.cpp` (`rip_sound_banks`) | pré-existant |
| `build_sbk` / `append_sbk` — reconstruit une banque / ajoute des sons à une banque existante | `goalc/build_sbk/` | pré-existant |
| macro `append-sbk` | `goal_src/jak2/lib/project-lib.gp` | pré-existant |
| **macro `build-sbk`** (créer une nouvelle `.SBK` autonome) | `goal_src/jak2/lib/project-lib.gp` | **ajouté sur cette branche** |
| **Hook générique de liaison d'art-group custom** (`register-custom-art-group`) | `goal_src/jak2/engine/anim/joint.gc` + `level.gc` | **ajouté sur cette branche** |

Les deux ajouts sont le « dernier kilomètre » : tout le reste était déjà là, mais il fallait encore
patcher `joint.gc` à la main avec un nom d'art-group en dur (cf. fiche 09) pour que les animations
custom se lient, et aucune macro ne permettait de créer une banque neuve.

---

## 2. Pré-requis

Avant de commencer, il vous faut :

1. **Un environnement OpenGOAL fonctionnel pour Jak 2**
   - `iso_data/jak2/` rempli (ISO commercial extrait).
   - `task set-game-jak2` puis `task extract` au moins une fois → `decompiler_out/jak2/` présent.
   - `task build-release` (ou `build-debug`) → `goalc`, `gk` et les outils autonomes compilés.

2. **Les outils d'import autonomes compilés** (cibles CMake séparées, quelques secondes) :
   ```bash
   cmake --build out/build/Release --target retarget_anim --config Release
   cmake --build out/build/Release --target build_sbk    --config Release
   cmake --build out/build/Release --target build_actor   --config Release
   ```

3. **Blender 2.83+** avec les deux plugins de `custom_assets/blender_plugins/` :
   - `opengoal.py` (outils de mesh, surfaces PAT, aides au bake de couleurs de sommets)
   - `gltf2_blender_extract.py` (remplace le module d'extraction de l'exporteur glTF de Blender —
     nécessaire pour que les données de joints / couleurs de sommets s'exportent dans la disposition
     attendue par `build-actor`)
   Installez `opengoal.py` via *Edit → Preferences → Add-ons → Install*, et copiez
   `gltf2_blender_extract.py` par-dessus le fichier du même nom dans
   `scripts/addons/io_scene_gltf2/blender/exp/` de votre installation Blender.

4. **Assets source**
   - *Modèle* : un `.glb` avec un squelette dont **le joint 0 s'appelle `align`** (cf. fiche 10 — le
     piège du décalage de +1). La base la plus sûre est un squelette natif décompilé
     (`decompiler_out/jak2/levels/**/<name>-lod0.glb`) ; construisez votre mesh dessus, ou modélisez
     de zéro mais gardez la racine `align`.
   - *Sons* : des `.wav` (PCM) + un `metadata.txt` décrivant les sons/grains, dans la disposition
     exacte produite par `extract_sbk`. Le plus simple pour obtenir un `metadata.txt` correct est
     d'extraire une banque existante et de l'éditer.

5. **Pour extraire des banques de sons de référence** (une fois), activez `rip_sound_banks` :
   ```bash
   ./out/build/Release/bin/decompiler ./decompiler/config/jak2/jak2_config.jsonc ./iso_data ./decompiler_out \
     --version ntscv1 --config-override '{"decompile_code": false, "levels_extract": true, "rip_sound_banks": true}'
   ```
   → `decompiler_out/jak2/audio/sfx/<BANQUE>/metadata.txt` + fichiers `.wav`.

6. **Pour extraire les animations / squelettes de référence**, utilisez `task rip-levels` (active
   `rip_levels`) → `decompiler_out/jak2/levels/<niveau>/<art-group>-lod0.glb` avec les animations
   natives incrustées en keyframes GLTF.

---

## 3. Démarche — Ajouter un Modèle Custom

Un modèle custom devient un **acteur GOAL autonome** (son propre `art-group`, `skeleton-group` et
type `process`). Deux voies de livraison :

- **Voie A — acteur de niveau custom** (entièrement supportée, aucun changement moteur) : l'acteur
  fait partie d'un niveau custom construit avec `build-custom-level`. À utiliser si le modèle ne
  doit apparaître que dans votre niveau.
- **Voie B — acteur global** (disponible partout, comme le jetboard natif) : l'art-group est ajouté
  à un DGO résident. À utiliser pour une fonctionnalité qui touche tout le jeu.

### 3.1 Créer le modèle (Blender)

1. Ouvrez le GLB du squelette de base (ou partez du vôtre, joint racine **nommé `align`**).
2. Construisez/skinnez votre mesh. Un matériau par texture ; gardez les couleurs de sommets si vous
   avez baké l'éclairage.
3. Pour des **animations** custom : animez les actions voulues, nommez chaque action exactement
   comme vous la référencerez dans le code.
4. Exportez en **glTF Binary (`.glb`)** avec le plugin exporteur OpenGOAL actif.
5. Enregistrez dans :
   ```
   custom_assets/jak2/models/custom_levels/<nom>.glb
   ```

### 3.2 Le déclarer avec `build-actor`

Dans `goal_src/jak2/game.gp` (près du `(build-actor "test-actor" ...)` existant) :

```lisp
;; prop statique / nouvelle créature avec ses propres animations :
(build-actor "mon-acteur" :gen-mesh #t :force-run #t)

;; OU : animations custom destinées à un personnage EXISTANT (jakb, daxter, ...) :
(build-actor "mes-anims-jak"
             :force-run #t
             :framerate 60
             :joint-channel 24
             :master-art-group jakb
             :master-ag-map ((ma-course-anim 330) (mon-salut-anim 331)))
```

Les paires `:master-ag-map` sont `(nom-anim index-slot-master)`. Choisissez des slots **libres**
dans l'art-group cible (inspectez-le en jeu ou consultez `art-elts.gc`). Cela inscrit
`master-art-group-name` / `master-art-group-index` dans l'`art-joint-anim` compilé.

Sortie : `out/jak2/obj/<nom>-ag.go`.

### 3.3 Placer l'art-group dans un DGO

- **Voie A (niveau custom) :** ajoutez le nom du modèle au `.jsonc` de votre niveau
  (`"custom_models": ["mon-acteur"]`) **et** au fichier `.gd` du niveau
  (`"mon-acteur-ag.go"`), exactement comme `test-actor` dans
  `custom_assets/jak2/levels/test-zone/`.

- **Voie B (global) :** ajoutez une ligne à `goal_src/jak2/dgos/art.gd`, à côté de `jakb-ag.go` /
  `board-ag.go` :
  ```
  "mon-acteur-ag.go"
  ```
  Ajout uniquement ; ne retirez rien.

### 3.4 Écrire l'acteur GOAL

Créez `goal_src/jak2/<chemin>/mon-acteur.gc` (enregistrez-le dans `game.gp` **et** le `.gd`
correspondant). Forme minimale (voir `test-zone-obs.gc` pour un exemple complet) :

```lisp
(in-package goal)

(deftype mon-acteur (process-drawable)
  ((root collide-shape-moving :override)))

;; def-actor génère automatiquement : les art-elts <nom>-ag, les noms de joint-node, et *mon-acteur-sg*
(def-actor mon-acteur
  :bounds (0 0 0 5)
  :art (mon-acteur-idle-ja)               ;; symboles d'animation, dans l'ordre des slots de l'art-group
  :joints (align prejoint main ...))      ;; noms de joints tels que dans le squelette du GLB

(defmethod init-from-entity! ((this mon-acteur) (e entity-actor))
  (process-drawable-from-entity! this e)
  (initialize-skeleton this *mon-acteur-sg* '())
  (go-virtual idle :proc this)
  (none))

(defstate idle (mon-acteur)
  :virtual #t
  :code (behavior () (loop (ja-no-eval :group! (ja-group) :num! (loop!)) (suspend))))
```

### 3.5 Si le modèle porte des animations pour un personnage existant — enregistrer la liaison

Un art-group construit avec `:master-art-group` a un `joint-geo` au slot 0, donc le `needs-link?`
d'origine renvoie `#f` et ses animations ne seraient jamais insérées dans le master art-group. Sur
cette branche, vous ne patchez plus `joint.gc` à la main — à la place, depuis une **forme
top-level** de votre `.gc` de mod :

```lisp
;; s'exécute une fois au boot ; le nom est la chaîne passée à build-actor, SANS "-ag"
(register-custom-art-group "mes-anims-jak")
```

L'ordre n'a pas d'importance — la liste n'est consultée qu'au login du niveau
(`art-group::relocate` et le chemin de chargement de niveau dans `level.gc`). Les acteurs autonomes
qui gardent leurs animations dans leur propre art-group n'en ont **pas** besoin.

### 3.6 Compiler & tester

Changement purement GOAL (sauf si vous avez touché du C++) : `./goalc.exe --game jak2 -c "(mi)"`
puis boot. Si vous avez touché du C++ (`game/**`), recompilez d'abord le moteur
(`task build-release`).

---

## 4. Démarche — Ajouter des Sons Custom

### 4.1 Préparer le dossier source

```
custom_assets/jak2/sounds/sfx/MESSONS/
├── metadata.txt          # description sons + grains (disposition extract_sbk)
├── MON_SON_A.wav
└── MON_SON_B.wav
```

Obtenez un `metadata.txt` valide en extrayant une vraie banque (pré-requis 5) et en l'éditant :
ajoutez vos blocs de sons, pointez les grains `TONE` vers vos `.wav`, gardez les lignes d'en-tête
cohérentes.

### 4.2 Choisir la voie de livraison

- **Voie A — ajout à `COMMON` (recommandée pour des sons globaux).**
  `COMMON.SBK` est toujours résidente et allouée sur le slot `common` traité en cas spécial ; rien
  d'autre n'est nécessaire à l'exécution.
  Dans `goal_src/jak2/game.gp` :
  1. **Retirez `"COMMON"`** de la liste `(copy-sbk-files ...)` (sinon deux étapes de build
     produisent `$OUT/iso/COMMON.SBK` et le make échoue avec *« multiple ways to make output »*).
  2. Ajoutez :
     ```lisp
     (append-sbk "COMMON" "MESSONS" :force-run #t)
     ;; optionnel : restreindre à certains noms
     ;; (append-sbk "COMMON" "MESSONS" :only-names (MON_SON_A MON_SON_B))
     ```

- **Voie B — une banque neuve autonome (`build-sbk`).**
  ```lisp
  (build-sbk "MESSONS" "MESSONS" :force-run #t :bank-id #x6d79736e)
  ```
  Cela écrit `$OUT/iso/MESSONS.SBK`. ⚠️ À l'exécution, il faut un **slot de banque overlord libre**.
  Jak 2 a trois slots dédiés (`common`, `gun`, `board`) plus un pool tournant de 3 slots utilisé par
  les banques de niveau. Un nom nouveau tombe dans le pool tournant et entrera en conflit avec les
  sons de niveau. N'utilisez la Voie B que pour une banque de **niveau custom** (chargée/déchargée
  avec le niveau), ou ajoutez un slot dédié dans `game/overlord/common/sbank.cpp` (`N_BANKS`, un
  nouveau `gXxxBank`, un cas dans `AllocateBankName`, un emplacement/taille SPU) — c'est un
  changement C++ moteur, hors périmètre de cette branche.

### 4.3 Vérifier le binaire de la banque (avant de booter)

`append_sbk` / `build_sbk` écrivent une vraie banque PS2 SPU-ADPCM. Un petit script Python sur les
octets bruts du `.SBK` (en-tête ~12 octets, table des sons, table des grains) détecte
instantanément une disposition malformée — cf. fiche 13 §B1 / §C3. Faites-le avant de dépenser un
boot.

### 4.4 Charger & déclencher

- **Voie A :** rien à charger — les sons sont dans `COMMON`, jouez-les directement.
- **Voie B :** chargez la banque quand elle est nécessaire :
  ```lisp
  (sound-bank-load (static-sound-name "MESSONS"))
  ```
- Déclenchez depuis GOAL, comme tout son natif :
  ```lisp
  (sound-play "mon-son-a")
  ;; ou, pour un son positionné / actualisable :
  (sound-play-by-name (static-sound-name "mon-son-a") (new-sound-id) 1024 0 0 (sound-group sfx) (-> self root trans))
  ```
  Pour un son **en boucle / actualisé par frame**, pré-allouez son id avec `(new-sound-id)` **une
  seule fois** dans le `-init` de l'objet propriétaire (fiche 13 §B3) — `sound-play-by-name` n'en
  génère jamais.

---

## 5. Les Changements Moteur de Cette Branche

| Fichier | Changement | Pourquoi |
|---|---|---|
| `goal_src/jak2/engine/anim/joint.gc` | Liste `*custom-art-groups-to-link*` + `register-custom-art-group` + `custom-art-group-to-link?` ; `art-group::relocate` lie désormais si `needs-link?` **ou** `custom-art-group-to-link?` est vrai | remplace le nom d'art-group en dur par-mod de la fiche 09 par un registre opt-in ; coût nul quand rien n'est enregistré |
| `goal_src/jak2/engine/level/level.gc` | Même garde `(or (needs-link? …) (custom-art-group-to-link? …))` sur le chemin de liaison d'art-group au chargement de niveau | les acteurs de niveau custom loguent via `level.gc`, pas via `relocate` |
| `goal_src/jak2/lib/project-lib.gp` | Nouvelle macro `build-sbk` (encapsule l'outil make `build-sbk` existant) | il n'y avait que `append-sbk` ; aucun moyen de déclarer une banque neuve |

Tous les changements sont additifs — aucun fichier natif vidé, aucune méthode retirée.

---

## 6. Comment Tester

1. `./goalc.exe --game jak2 -c "(mi)"` — doit atteindre *« Successfully built all N targets »*.
2. **Modèle (Voie A) :** bootez dans `test-zone` (ou votre niveau), vérifiez que l'acteur apparaît
   avec le bon mesh et que son animation idle joue sans que le mesh se disloque (dislocation ⇒
   décalage de joint, fiche 10).
3. **Modèle (Voie B) :** bootez n'importe quel niveau, spawnez votre acteur via le menu debug ou un
   script, mêmes vérifications visuelles.
4. **Anims custom sur jakb/daxter :** bootez, déclenchez l'état qui joue le clip importé, cherchez
   dans `log/jak2.<ts>.log` la ligne `could not find a master slot to link` — son absence signifie
   que la liaison a marché.
5. **Sons (Voie A) :** bootez, déclenchez le son ; cherchez dans le log les erreurs du sound-loader.
6. Non-régression : bootez deux ou trois niveaux intacts et vérifiez qu'aucune nouvelle erreur
   `link-art` / banque de sons n'apparaît dans le log (les gardes ne doivent pas affecter les
   art-groups natifs).

---

## 7. Statut

| Élément | État |
|---|---|
| `build-actor2` avec master art-group | ✅ fonctionnel (pré-existant) |
| Hook de liaison générique `register-custom-art-group` | ✅ ajouté, compile (`(mi)` OK, 936 cibles) |
| macro `build-sbk` | ✅ ajoutée, compile |
| `append-sbk` sur `COMMON` | ⚠️ voie documentée ; nécessite un vrai test bout-en-bout avec une banque d'exemple |
| Slot de banque de sons dédié (Voie B, global) | ❌ non fait — nécessite un changement C++ `sbank.cpp` |
| Exemple concret (`.glb` + sons d'exemple) | ❌ non inclus — cette branche livre la capacité, pas une démo |

---

## 8. Journal des Modifications de Modding

| Date | Fichier | Changement | Justification |
|---|---|---|---|
| 2026-08-30 | `goal_src/jak2/engine/anim/joint.gc` | Ajout de `*custom-art-groups-to-link*`, `register-custom-art-group`, `custom-art-group-to-link?` ; `relocate` lie sur `(or (needs-link? this) (custom-art-group-to-link? this))` | Remplacement générique et opt-in du hack de nom d'art-group en dur (fiche 09) pour que les animations importées sur des personnages natifs se lient au chargement |
| 2026-08-30 | `goal_src/jak2/engine/level/level.gc` | Ajout de `custom-art-group-to-link?` à la garde de liaison d'art-group au chargement de niveau | Les acteurs de niveau custom loguent via `level.gc`, pas `art-group::relocate` |
| 2026-08-30 | `goal_src/jak2/lib/project-lib.gp` | Ajout de la macro `build-sbk` (créer une `.SBK` autonome depuis un dossier `metadata.txt` + wav) | `append-sbk` existait mais aucune macro ne permettait de déclarer une banque neuve |
| 2026-08-30 | `docs/modding/current_mod/custom_animation_and_sound_readme.md` | Ce document | Démarche + pré-requis pour importer un modèle custom et des sons custom dans Jak 2 |
