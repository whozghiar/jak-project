# Jak 2 — Injecting a Model into a Level it Never Shipped In / Injecter un Modèle dans un Niveau où il n'a Jamais Été Livré

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/merc-fr3-injection-poc`
> - **Last Updated / Dernière modification:** `jak2/features/merc-fr3-injection-poc`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. The problem this solves

You want a skeletal model — a vehicle, an enemy, a prop with joints/animation — to
appear in a level where the retail game never used it. You add its art group to the
level's `.gd`, it compiles, the process spawns, animations play, sounds play… **but the
model is invisible** (or visible but untextured). Only its child processes (a turret, a
rider) show up.

This is because a skeletal model needs **two independent pieces of data**, and the
`.gd` edit only provides one of them.

## 2. The two circuits

| Circuit | What it is | Where it lives | Loaded into | Used by |
|---|---|---|---|---|
| **1 — art group** | skeleton, joint geometry (`*-lod*-jg`), animations (`*-ja`), LOD distances | `<model>-ag.go`, listed in a level's `.gd` (→ DGO) | the GOAL heap | `art-group-get-by-name`, `initialize-skeleton`, the animation system |
| **2 — merc render geometry** | the actual triangles the PC renderer draws (`*-lod*-mg`), plus the textures they use | baked into `<level>.fr3` by the **decompiler**, from the **retail** DGO contents | the OpenGL renderer / VRAM | `Merc2::handle_pc_model`, which looks models up **by name** |

Key facts:

- **`.gd` / DGO edits only ever add Circuit 1.** They put the skeleton + animations in
  the GOAL heap. They do nothing for the renderer.
- **`Merc2` draws only from Circuit 2.** For every skinned draw, GOAL sends a model
  name (e.g. `transport-lod0-mg`). `Merc2` looks it up in `m_all_merc_models`, which is
  populated only from the `merc_data.models` of each **resident `.fr3`**. Miss = silent
  `num_missing_models++; return;` — no crash, no log, nothing drawn.
- **What is in a `.fr3` is fixed by the *retail* DGO membership**, read by the
  decompiler from `iso_data/jak2/DGO/*.DGO`. It is **not** controlled by
  `goal_src/jak2/dgos/*.gd`. Editing a `.gd` never changes a `.fr3`.
- So: to make a model drawable in a level it never shipped in, you must get its
  Circuit-2 geometry **baked into a `.fr3` that is resident there**. That is what the
  `extra_art_groups_by_dgo` decompiler config field does.

See also: the merc renderer path is `foreground.gc` DMA → `Merc2.cpp` →
`Loader.cpp`/`LoaderStages.cpp` (`MercLoaderStage`).

## 3. The mechanism — `extra_art_groups_by_dgo`

In `decompiler/config/jak2/jak2_config.jsonc`:

```jsonc
"extra_art_groups_by_dgo": {
  "<TARGET DGO>": [ "<art-group>:<HOME.DGO>", ... ],
  ...
}
```

- **`<TARGET DGO>`** — the level whose `.fr3` gets the geometry, written as the DGO
  name exactly as in `inputs.jsonc` → `levels_to_extract` (e.g. `CWI.DGO`,
  `LWIDEA.DGO`, or `GAME.CGO` for the global `GAME.fr3`).
- **`<art-group>`** — the base name of the model's art group, e.g. `transport-ag`. It
  must be reachable from *some* DGO already in `inputs.jsonc` → `dgo_names` (every
  level is, by default) — its own home level does **not** need to be a borrow target.
- **`<HOME.DGO>`** — the level the model shipped in. Its `texture-remap-table` is used
  to resolve the model's texture ids. **This part matters**: a merc's texture ids are
  *relative to the level it was built for*. Resolve them against the wrong level's
  remap and the model renders **untextured** (shiny, environment-map only, no albedo).
  If you omit `:<HOME.DGO>`, the decompiler auto-picks the first real level DGO the art
  group shipped in — often wrong, so **always specify it**.

At `task extract`, for each `<TARGET DGO>`, the decompiler runs the same
`extract_merc` / `extract_joint_group` / `extract_animations` it runs for that level's
native art groups — but for the listed extras, sourced globally from the object DB and
textured via `<HOME.DGO>`'s remap. The referenced texture pages are pulled into the
`.fr3` automatically. No C++ patch, no runtime change — the `gk`/`game` binaries are
untouched. Cost: one `task extract` (offline, needs a legally-dumped ISO) for anyone
who builds the mod.

Implementation: `decompiler/config.{h,cpp}` (the field), and
`decompiler/level_extractor/extract_level.cpp` → `extract_art_groups_from_level` (the
extra loop, after the native `-ag` loop).

## 4. Choosing the target level

The geometry only helps while its `.fr3` is **resident**. Pick the target by where the
model needs to be visible:

| Target | `.fr3` | Resident when | Use for |
|---|---|---|---|
| `GAME.CGO` | `GAME.fr3` | always, every level | a model needed everywhere; cheapest to reason about, costs a bit of RAM in every level |
| `CWI.DGO` | `ctywide.fr3` | the whole time you are in Haven City (`small-center`) | anything city-wide. **But** `ctywide`'s DGO heap is tight — a large `-ag.go` (Circuit 1) may not fit in `cwi.gd` (same issue as `paddy-wagon-ag.go`) |
| `LWIDEA.DGO` / `LWIDEB.DGO` / `LWIDEC.DGO` | `lwidea/b/c.fr3` | borrowed into `ctywide` slot 1 during free-roam; the traffic manager picks one of the three by city region | traffic-actor-sized vehicle art in the city. Bake into **all three** so the model is in whichever one is resident where the player is |
| a mission level DGO (`FRA.DGO`, `NEB.DGO`, …) | that level's `.fr3` | only while that mission level is loaded | a model needed in one specific mission |

## 5. Worked example — the Crimson Guard troop transport in Haven City

Goal: make the `transport` drop-ship hull draw in free-roam Haven City, the same way
its chin `vehicle-turret` already does. (This is the `jak2/features/guard_transport`
mod; the POC branch is `jak2/features/merc-fr3-injection-poc`.)

### Step 0 — confirm the diagnosis

In the REPL, in Haven City, spawn the model. Hull invisible, turret + guards fine →
Circuit 2 missing. Confirm the geometry is *not* in any resident `.fr3`:

```bash
git grep -l "transport-ag" master -- goal_src/jak2/dgos/
# -> ctykora.gd fob.gd lprotect.gd nes.gd nestt.gd   (no city level)
```

### Step 1 — find the pieces

| Piece | How | Value here |
|---|---|---|
| art-group base name | `grep transport-ag goal_src/jak2/build/all_objs.json` | `transport-ag` |
| the model names GOAL sends | the `defskelgroup` in the model's `.gc` | `transport-lod0-mg`, `-lod1-mg`, `-lod2-mg` |
| home level DGO (for textures) | which retail DGO has the `-ag` **and** its `tpage-*.go` | `LPROTECT.DGO` (its `lprotect.gd` lists both `transport-ag.go` and `tpage-2869.go`) |
| the tpage | `all_objs.json` line for the `tpage-*` next to the `-ag`, or `lprotect.gd` | `tpage-2869` |
| target level(s) | where it must be visible → §4 | `LWIDEA.DGO`, `LWIDEB.DGO`, `LWIDEC.DGO` |

### Step 2 — Circuit 2: the `.fr3` bake

`decompiler/config/jak2/jak2_config.jsonc`:

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEA.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEB.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEC.DGO": ["transport-ag:LPROTECT.DGO"]
}
```

### Step 3 — Circuit 1: the art group in the target levels

`goal_src/jak2/dgos/lwidea.gd`, `lwideb.gd`, `lwidec.gd` — add **before** the level's
own `<level>.go` (the bsp must stay last):

```
  "tpage-2869.go"
  "transport-ag.go"
```

`transport-ag` already has a source-folder entry in `all_objs.json` (it is a
retail object), so no `.gp` change is needed — the DGO build picks it up.

### Step 4 — make it reachable at runtime

A model spawned in the city has no home entity, so `*level*` art lookups and the merc
draw-control's texture level bind to the wrong level. Re-home the process onto the
resident city level, exactly like `vehicle-turret-init-by-other` does:

```lisp
;; in transport-init-by-other, before initialize-skeleton
(ctywide-entity-hack)
```

### Step 5 — build and verify

```bash
task extract        # re-bakes lwidea/lwideb/lwidec.fr3 with transport-lod*-mg + tpage-2869
# no task build-release needed for the .fr3 — it is runtime data
```

The extract log must show, per target DGO:

```
extra_art_groups_by_dgo: 'transport-ag' textures remapped via LPROTECT.DGO
extra_art_groups_by_dgo: baking 'transport-ag' into LWIDEA.DGO (.fr3)
```

and **no** `merc failed to find texture: … for transport-…`.

Then run the game, go to Haven City, spawn the model. Hull draws, textured, and stays
visible as you move around (it is in the resident `lwide*` `.fr3`, not gated on any
runtime borrow).

## 6. Template — any model into any level

1. **Pick the target level DGO** (§4). If it must be visible city-wide and its `-ag.go`
   is large, use `LWIDEA/LWIDEB/LWIDEC.DGO` (bake into all three), not `CWI.DGO`.
2. **Find `<model>-ag`** and its **`<HOME.DGO>`** (a retail level that has both the
   `-ag.go` and its `tpage-*.go` in its `.gd`).
3. **Config:** add `"<TARGET DGO>": ["<model>-ag:<HOME.DGO>"]` to
   `extra_art_groups_by_dgo` (append to the target's list if it already has one).
4. **`.gd`:** add `"<tpage>.go"` and `"<model>-ag.go"` to the target level's `.gd`,
   before the bsp `.go`. (Skip if you only need the model *drawable* as a child of
   something whose art is already resident, and never call `initialize-skeleton` /
   `art-group-get-by-name` for it yourself.)
5. **Runtime:** if you spawn it yourself in a level it has no entity in, call the
   level's entity hack (`ctywide-entity-hack`, `lwide-entity-hack`, …) in its
   `init-by-other` before `initialize-skeleton`.
6. **`task extract`**, check the log, run the game.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| model **invisible**, child processes fine | Circuit 2 missing — geometry not in a resident `.fr3` | add / fix the `extra_art_groups_by_dgo` entry; check the target `.fr3` is actually resident where you tested (§4) |
| `process-drawable-art-error` / process dies at spawn | Circuit 1 missing — `<model>-ag.go` not resident | add it (+ its tpage) to the resident level's `.gd`, rebuild GOAL |
| model visible but **untextured** (shiny, envmap only) | textures resolved against the wrong level's remap | add / fix `:<HOME.DGO>` — pick the retail level that carries the model's `tpage-*.go` |
| `merc failed to find texture: 0x… Should be in tpage N` in the extract log | that tpage was not processed, or the remap points nowhere | make sure `<HOME.DGO>` (or the DGO holding `tpage-N`) is in `inputs.jsonc` `dgo_names` |
| model visible only in part of the city | only one of `lwidea/lwideb/lwidec` was baked | bake into all three |
| `extra_art_groups_by_dgo: '<x>' not found in the object DB` | the `-ag`'s source DGO is not a decompiler input | add its DGO to `inputs.jsonc` `dgo_names` |
| `task extract` seems to run but the `.fr3` is unchanged | **you ran a stale decompiler** — see §8 | rebuild it into the path the Taskfile uses |

## 8. Build gotcha — Ninja vs Visual Studio output layout

The Taskfile (`task extract`, `task build-release`, …) expects the **Ninja** preset
(`Release-windows-clang`), which puts binaries flat in `out/build/Release/bin/`. If
your `out/build/Release` was instead configured with the **Visual Studio** generator
(VS, or VS Code's CMake Tools default on Windows), binaries go to
`out/build/Release/bin/Release/` and the flat `bin/` keeps whatever old build was there.

`task extract` runs `out/build/Release/bin/decompiler.exe` + `bin/decomp.dll`. If those
are stale, your decompiler config changes silently do nothing.

- **One-off fix:** `cp out/build/Release/bin/Release/{decomp,common,compiler}.dll
  out/build/Release/bin/Release/decompiler.exe → out/build/Release/bin/` after building.
  (The DLL is the one that matters; it holds the decompiler code.)
- **Permanent fix:** `rm -rf out/build/Release && task gen-cmake-release && task
  build-release` — reconfigures with the Ninja preset so every `task` uses the same,
  fresh binaries.
- **Check:** `grep -ac extra_art_groups_by_dgo out/build/Release/bin/decomp.dll` should
  be non-zero.

## 9. Limits and alternatives

- **Offline cost.** Everyone who builds the mod must run `task extract` (needs a
  legally-dumped ISO). Pure-source mods (`(mi)` and go) do not. This is the price of
  Circuit 2.
- **`.fr3` size.** Each injected model adds its vertices + textures (typically a few
  hundred KB) to every target `.fr3`. Do not inject the whole game catalog into
  `GAME.fr3`.
- **Drawable ≠ placed entity.** This makes a model *renderable* and lets you spawn it
  from code. Hand-placing it as an `entity-actor` in a level still needs level/bsp
  editing (custom level tools).
- **Collision, nav-mesh, LOD ranges** all come from Circuit 1 (`-ag` + the model's
  `.gc`) and behave normally once both circuits are present.
- **Alternatives:**
  - `custom_assets/jak2/merc_replacements/<ctrl>.glb` — *replace* an existing merc.
  - `custom_assets/jak2/models/<level|common>/<name>.glb` — *add* a merc from a GLB
    (auto directory-scan, no config; needs the GLB, which loses some material
    fidelity). `extra_art_groups_by_dgo` is the no-GLB-roundtrip variant for
    game-native models.
  - a runtime level **borrow** of the model's home level — no re-extract, but it
    consumes one of `ctywide`'s two borrow slots for the borrow's lifetime.

---

# 🇫🇷 Version Française

## 1. Le problème que ça résout

Tu veux qu'un modèle squelettique — un véhicule, un ennemi, un accessoire avec
articulations/animation — apparaisse dans un niveau où le jeu retail ne l'a jamais
utilisé. Tu ajoutes son groupe d'art au `.gd` du niveau, ça compile, le process
apparaît, les animations jouent, les sons jouent… **mais le modèle est invisible** (ou
visible mais sans textures). Seuls ses process enfants (une tourelle, un pilote)
s'affichent.

C'est parce qu'un modèle squelettique a besoin de **deux données indépendantes**, et la
modification du `.gd` n'en fournit qu'une.

## 2. Les deux circuits

| Circuit | Ce que c'est | Où ça réside | Chargé dans | Utilisé par |
|---|---|---|---|---|
| **1 — groupe d'art** | squelette, géométrie de joints (`*-lod*-jg`), animations (`*-ja`), distances de LOD | `<modele>-ag.go`, listé dans le `.gd` d'un niveau (→ DGO) | le tas GOAL | `art-group-get-by-name`, `initialize-skeleton`, le système d'animation |
| **2 — géométrie de rendu merc** | les triangles que le renderer PC dessine réellement (`*-lod*-mg`), + les textures qu'ils utilisent | cuit dans `<niveau>.fr3` par le **décompilateur**, depuis le contenu du DGO **retail** | le renderer OpenGL / VRAM | `Merc2::handle_pc_model`, qui cherche les modèles **par nom** |

Faits clés :

- **Les modifications de `.gd` / DGO n'ajoutent jamais que le Circuit 1.** Elles
  mettent le squelette + animations dans le tas GOAL. Elles ne font rien pour le
  renderer.
- **`Merc2` ne dessine que depuis le Circuit 2.** Pour chaque draw skinné, GOAL envoie
  un nom de modèle (ex. `transport-lod0-mg`). `Merc2` le cherche dans
  `m_all_merc_models`, rempli uniquement depuis les `merc_data.models` de chaque `.fr3`
  **résident**. Absent = `num_missing_models++; return;` silencieux — pas de crash, pas
  de log, rien de dessiné.
- **Le contenu d'un `.fr3` est fixé par l'appartenance au DGO *retail***, lu par le
  décompilateur depuis `iso_data/jak2/DGO/*.DGO`. Ce n'est **pas** contrôlé par
  `goal_src/jak2/dgos/*.gd`. Modifier un `.gd` ne change jamais un `.fr3`.
- Donc : pour rendre un modèle affichable dans un niveau où il n'a jamais été livré, il
  faut faire **cuire sa géométrie Circuit 2 dans un `.fr3` qui y est résident**. C'est
  ce que fait le champ de config décompilateur `extra_art_groups_by_dgo`.

Voir aussi : le chemin du renderer merc est DMA `foreground.gc` → `Merc2.cpp` →
`Loader.cpp`/`LoaderStages.cpp` (`MercLoaderStage`).

## 3. Le mécanisme — `extra_art_groups_by_dgo`

Dans `decompiler/config/jak2/jak2_config.jsonc` :

```jsonc
"extra_art_groups_by_dgo": {
  "<DGO CIBLE>": [ "<groupe-art>:<HOME.DGO>", ... ],
  ...
}
```

- **`<DGO CIBLE>`** — le niveau dont le `.fr3` reçoit la géométrie, écrit comme le nom
  de DGO exactement comme dans `inputs.jsonc` → `levels_to_extract` (ex. `CWI.DGO`,
  `LWIDEA.DGO`, ou `GAME.CGO` pour le `GAME.fr3` global).
- **`<groupe-art>`** — le nom de base du groupe d'art du modèle, ex. `transport-ag`. Il
  doit être atteignable depuis *un* DGO déjà dans `inputs.jsonc` → `dgo_names` (tous
  les niveaux le sont par défaut) — son niveau d'origine n'a **pas** besoin d'être une
  cible de « borrow ».
- **`<HOME.DGO>`** — le niveau dans lequel le modèle a été livré. Sa
  `texture-remap-table` sert à résoudre les ids de texture du modèle. **Cette partie
  compte** : les ids de texture d'un merc sont *relatifs au niveau pour lequel il a été
  construit*. Résous-les avec le remap du mauvais niveau et le modèle s'affiche **sans
  textures** (brillant, environment-map seul, pas d'albédo). Si tu omets `:<HOME.DGO>`,
  le décompilateur auto-choisit le premier DGO de niveau où le groupe d'art a été livré
  — souvent faux, donc **spécifie-le toujours**.

Au `task extract`, pour chaque `<DGO CIBLE>`, le décompilateur lance les mêmes
`extract_merc` / `extract_joint_group` / `extract_animations` que pour les groupes
d'art natifs du niveau — mais pour les extras listés, sourcés globalement depuis la DB
d'objets et texturés via le remap de `<HOME.DGO>`. Les pages de textures référencées
sont tirées dans le `.fr3` automatiquement. Aucun patch C++, aucun changement runtime —
les binaires `gk`/`game` sont intacts. Coût : un `task extract` (hors-ligne, nécessite
un ISO légalement extrait) pour quiconque build le mod.

Implémentation : `decompiler/config.{h,cpp}` (le champ), et
`decompiler/level_extractor/extract_level.cpp` → `extract_art_groups_from_level` (la
boucle extra, après la boucle `-ag` native).

## 4. Choisir le niveau cible

La géométrie ne sert que tant que son `.fr3` est **résident**. Choisis la cible selon
l'endroit où le modèle doit être visible :

| Cible | `.fr3` | Résident quand | À utiliser pour |
|---|---|---|---|
| `GAME.CGO` | `GAME.fr3` | toujours, dans chaque niveau | un modèle nécessaire partout ; le plus simple à raisonner, coûte un peu de RAM dans chaque niveau |
| `CWI.DGO` | `ctywide.fr3` | tout le temps où tu es dans Haven City (`small-center`) | tout ce qui est à l'échelle de la ville. **Mais** le tas DGO de `ctywide` est serré — un gros `-ag.go` (Circuit 1) peut ne pas rentrer dans `cwi.gd` (même souci que `paddy-wagon-ag.go`) |
| `LWIDEA.DGO` / `LWIDEB.DGO` / `LWIDEC.DGO` | `lwidea/b/c.fr3` | emprunté dans le slot 1 de `ctywide` en jeu libre ; le gestionnaire de trafic choisit l'un des trois par région | l'art de véhicules dimensionné pour les acteurs de trafic en ville. Cuire dans **les trois** pour que le modèle soit dans celui qui est résident là où est le joueur |
| un DGO de niveau de mission (`FRA.DGO`, `NEB.DGO`, …) | le `.fr3` de ce niveau | seulement quand ce niveau de mission est chargé | un modèle nécessaire dans une mission précise |

## 5. Exemple concret — le transport de troupes des Crimson Guards dans Haven City

Objectif : faire s'afficher la carlingue du drop-ship `transport` en jeu libre à Haven
City, comme sa tourelle de menton `vehicle-turret` le fait déjà. (C'est le mod
`jak2/features/guard_transport` ; la branche POC est
`jak2/features/merc-fr3-injection-poc`.)

### Étape 0 — confirmer le diagnostic

Dans le REPL, à Haven City, fais apparaître le modèle. Carlingue invisible, tourelle +
gardes OK → Circuit 2 manquant. Confirme que la géométrie n'est dans **aucun** `.fr3`
résident :

```bash
git grep -l "transport-ag" master -- goal_src/jak2/dgos/
# -> ctykora.gd fob.gd lprotect.gd nes.gd nestt.gd   (aucun niveau de ville)
```

### Étape 1 — trouver les pièces

| Pièce | Comment | Valeur ici |
|---|---|---|
| nom de base du groupe d'art | `grep transport-ag goal_src/jak2/build/all_objs.json` | `transport-ag` |
| les noms de modèle que GOAL envoie | le `defskelgroup` dans le `.gc` du modèle | `transport-lod0-mg`, `-lod1-mg`, `-lod2-mg` |
| DGO du niveau d'origine (pour les textures) | quel DGO retail a le `-ag` **et** son `tpage-*.go` | `LPROTECT.DGO` (son `lprotect.gd` liste `transport-ag.go` **et** `tpage-2869.go`) |
| la tpage | la ligne `all_objs.json` du `tpage-*` à côté du `-ag`, ou `lprotect.gd` | `tpage-2869` |
| niveau(x) cible(s) | où il doit être visible → §4 | `LWIDEA.DGO`, `LWIDEB.DGO`, `LWIDEC.DGO` |

### Étape 2 — Circuit 2 : la cuisson `.fr3`

`decompiler/config/jak2/jak2_config.jsonc` :

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEA.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEB.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEC.DGO": ["transport-ag:LPROTECT.DGO"]
}
```

### Étape 3 — Circuit 1 : le groupe d'art dans les niveaux cibles

`goal_src/jak2/dgos/lwidea.gd`, `lwideb.gd`, `lwidec.gd` — ajouter **avant** le
`<niveau>.go` propre du niveau (le bsp doit rester en dernier) :

```
  "tpage-2869.go"
  "transport-ag.go"
```

`transport-ag` a déjà une entrée de dossier source dans `all_objs.json` (c'est un objet
retail), donc aucun changement `.gp` n'est nécessaire — le build du DGO le récupère.

### Étape 4 — le rendre atteignable au runtime

Un modèle spawné en ville n'a pas d'entité d'origine, donc les recherches d'art
`*level*` et le niveau de texture du draw-control merc se lient au mauvais niveau.
Re-rattache le process au niveau de ville résident, exactement comme
`vehicle-turret-init-by-other` le fait :

```lisp
;; dans transport-init-by-other, avant initialize-skeleton
(ctywide-entity-hack)
```

### Étape 5 — build et vérification

```bash
task extract        # re-cuit lwidea/lwideb/lwidec.fr3 avec transport-lod*-mg + tpage-2869
# pas de task build-release pour le .fr3 — c'est de la donnée runtime
```

Le log d'extraction doit montrer, par DGO cible :

```
extra_art_groups_by_dgo: 'transport-ag' textures remapped via LPROTECT.DGO
extra_art_groups_by_dgo: baking 'transport-ag' into LWIDEA.DGO (.fr3)
```

et **aucun** `merc failed to find texture: … for transport-…`.

Puis lance le jeu, va à Haven City, fais apparaître le modèle. La carlingue s'affiche,
texturée, et reste visible quand tu te déplaces (elle est dans le `.fr3` résident
`lwide*`, plus conditionnée à un borrow runtime).

## 6. Modèle — n'importe quel modèle dans n'importe quel niveau

1. **Choisir le DGO du niveau cible** (§4). S'il doit être visible à l'échelle de la
   ville et que son `-ag.go` est gros, utiliser `LWIDEA/LWIDEB/LWIDEC.DGO` (cuire dans
   les trois), pas `CWI.DGO`.
2. **Trouver `<modele>-ag`** et son **`<HOME.DGO>`** (un niveau retail qui a à la fois
   le `-ag.go` et son `tpage-*.go` dans son `.gd`).
3. **Config :** ajouter `"<DGO CIBLE>": ["<modele>-ag:<HOME.DGO>"]` à
   `extra_art_groups_by_dgo` (l'ajouter à la liste de la cible si elle en a déjà une).
4. **`.gd` :** ajouter `"<tpage>.go"` et `"<modele>-ag.go"` au `.gd` du niveau cible,
   avant le `.go` du bsp. (À sauter si tu as seulement besoin que le modèle soit
   *affichable* comme enfant de quelque chose dont l'art est déjà résident, et que tu
   n'appelles jamais `initialize-skeleton` / `art-group-get-by-name` pour lui.)
5. **Runtime :** si tu le spawnes toi-même dans un niveau où il n'a pas d'entité,
   appelle l'entity hack du niveau (`ctywide-entity-hack`, `lwide-entity-hack`, …) dans
   son `init-by-other` avant `initialize-skeleton`.
6. **`task extract`**, vérifier le log, lancer le jeu.

## 7. Dépannage

| Symptôme | Cause | Correctif |
|---|---|---|
| modèle **invisible**, process enfants OK | Circuit 2 manquant — géométrie absente d'un `.fr3` résident | ajouter / corriger l'entrée `extra_art_groups_by_dgo` ; vérifier que le `.fr3` cible est bien résident là où tu as testé (§4) |
| `process-drawable-art-error` / le process meurt au spawn | Circuit 1 manquant — `<modele>-ag.go` pas résident | l'ajouter (+ sa tpage) au `.gd` du niveau résident, recompiler le GOAL |
| modèle visible mais **sans textures** (brillant, envmap seul) | textures résolues contre le remap du mauvais niveau | ajouter / corriger `:<HOME.DGO>` — prendre le niveau retail qui porte le `tpage-*.go` du modèle |
| `merc failed to find texture: 0x… Should be in tpage N` dans le log d'extraction | cette tpage n'a pas été traitée, ou le remap ne pointe nulle part | s'assurer que `<HOME.DGO>` (ou le DGO qui contient `tpage-N`) est dans `inputs.jsonc` `dgo_names` |
| modèle visible seulement dans une partie de la ville | un seul de `lwidea/lwideb/lwidec` a été cuit | cuire dans les trois |
| `extra_art_groups_by_dgo: '<x>' not found in the object DB` | le DGO source du `-ag` n'est pas une entrée du décompilateur | ajouter son DGO à `inputs.jsonc` `dgo_names` |
| `task extract` tourne mais le `.fr3` est inchangé | **tu as lancé un décompilateur périmé** — voir §8 | le recompiler dans le chemin que le Taskfile utilise |

## 8. Piège de build — layout de sortie Ninja vs Visual Studio

Le Taskfile (`task extract`, `task build-release`, …) attend le preset **Ninja**
(`Release-windows-clang`), qui met les binaires à plat dans `out/build/Release/bin/`. Si
ton `out/build/Release` a été configuré avec le générateur **Visual Studio** (VS, ou le
défaut de CMake Tools de VS Code sur Windows), les binaires vont dans
`out/build/Release/bin/Release/` et le `bin/` à plat garde le vieux build qui s'y
trouvait.

`task extract` lance `out/build/Release/bin/decompiler.exe` + `bin/decomp.dll`. S'ils
sont périmés, tes changements de config décompilateur ne font rien, silencieusement.

- **Correctif ponctuel :** `cp out/build/Release/bin/Release/{decomp,common,compiler}.dll`
  et `decompiler.exe` → `out/build/Release/bin/` après avoir buildé. (La DLL est celle
  qui compte ; elle contient le code du décompilateur.)
- **Correctif permanent :** `rm -rf out/build/Release && task gen-cmake-release && task
  build-release` — reconfigure avec le preset Ninja pour que chaque `task` utilise les
  mêmes binaires à jour.
- **Vérif :** `grep -ac extra_art_groups_by_dgo out/build/Release/bin/decomp.dll` doit
  être non nul.

## 9. Limites et alternatives

- **Coût hors-ligne.** Quiconque build le mod doit lancer `task extract` (nécessite un
  ISO légalement extrait). Les mods 100 % source (`(mi)` et c'est bon) non. C'est le
  prix du Circuit 2.
- **Taille des `.fr3`.** Chaque modèle injecté ajoute ses sommets + textures
  (typiquement quelques centaines de Ko) à chaque `.fr3` cible. Ne pas injecter tout le
  catalogue du jeu dans `GAME.fr3`.
- **Affichable ≠ entité placée.** Ça rend un modèle *dessinable* et permet de le
  spawner depuis le code. Le placer à la main comme `entity-actor` dans un niveau
  nécessite encore l'édition du niveau/bsp (outils de niveaux custom).
- **Collision, nav-mesh, distances de LOD** viennent toutes du Circuit 1 (`-ag` + le
  `.gc` du modèle) et se comportent normalement dès que les deux circuits sont là.
- **Alternatives :**
  - `custom_assets/jak2/merc_replacements/<ctrl>.glb` — *remplacer* un merc existant.
  - `custom_assets/jak2/models/<niveau|common>/<nom>.glb` — *ajouter* un merc depuis un
    GLB (scan de dossier automatique, sans config ; nécessite le GLB, qui perd un peu
    de fidélité de matériaux). `extra_art_groups_by_dgo` est la variante sans
    aller-retour GLB pour les modèles natifs du jeu.
  - un **borrow** runtime du niveau d'origine du modèle — pas de re-extraction, mais
    ça consomme un des deux slots de borrow de `ctywide` pour la durée du borrow.
