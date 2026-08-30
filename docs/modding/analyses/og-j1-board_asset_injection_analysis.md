# Analyse — Injection du JET-Board dans `og-j1-board` & proposition de généralisation

> **Document d'analyse (AI-assisted)**
>
> - **Projet analysé / Analyzed project:** [`Hat-Kid/og-j1-board`](https://github.com/Hat-Kid/og-j1-board) — *« Jak 1: The JET-Board Legacy »*
> - **Copie locale:** `D:\Developpement\OpenGoal Dev\github_mods\og-j1-board`
> - **But:** comprendre **précisément** comment un modèle GLB inexistant dans Jak 1 (la planche
>   physique + les animations Jak/Daxter en planche) a été injecté, puis proposer une méthode
>   **générique** d'injection de *modèle / son / animation* pour Jak 1, Jak 2 et Jak 3.
> - **Date d'analyse:** 2026-08-30

---

## Sommaire

1. [Partie 1 — Anatomie du mod `og-j1-board`](#partie-1)
   1. [Les commits « infrastructure »](#11-les-commits-infrastructure)
   2. [Les trois natures d'assets injectés](#12-les-trois-natures-dassets-injectés)
   3. [Le pipeline modèle GLB, de bout en bout](#13-le-pipeline-modèle-glb-de-bout-en-bout)
   4. [D'où viennent réellement le modèle et les animations ?](#14-doù-viennent-réellement-le-modèle-et-les-animations)
   5. [Le pipeline son (soundbank custom `BOARD.SBK`)](#15-le-pipeline-son)
   6. [Modifications C++ transverses](#16-modifications-c-transverses)
   7. [Récapitulatif : les 3 voies d'injection de modèle](#17-récapitulatif-les-3-voies-dinjection-de-modèle)
2. [Partie 2 — Ce qui est déjà dans `jak-project` upstream](#partie-2)
3. [Partie 3 — Proposition de généralisation](#partie-3)

---

<a name="partie-1"></a>

# Partie 1 — Anatomie du mod `og-j1-board`

Le mod est un **fork complet de `jak-project`** (pas un simple dossier `custom_assets/`). Il touche
donc à la fois :

- le **décompilateur** (extraction des données sources depuis Jak 2 / Jak 3),
- les **outils de build** `goalc/` (`build-actor`, `build-sbk`),
- le **runtime C++** `game/` (overlord son),
- le **code GOAL** `goal_src/jak1/` (le gameplay du board + hooks de chargement).

<a name="11-les-commits-infrastructure"></a>

## 1.1 Les commits « infrastructure »

Historique pertinent (`git log --oneline`, du plus ancien au plus récent) :

| Commit | Message | Rôle |
|---|---|---|
| `5a817899` | `board sounds and metadata` | 45 `.wav` + `metadata.txt` dans `custom_assets/jak1/sounds/sfx/BOARD/` |
| `ecd89626` | `models` | 6 `.glb` : `board`, `eichar-board+0`, `sidekick-board+0` (× dossiers `common/` **et** `custom_levels/`) |
| `e5f8cd1e` | `custom sbk, extract anims` | **Le commit clé.** Décompilateur : `extract_sbk`, `extract_anim`, export des anims dans `fr3_to_gltf`. Outils : `build-sbk`/`append-sbk`, extension de `build-actor` (`master-art-group`, `master-ag-map`, `framerate`, `joint-channel`) |
| `2213d4d1` | `gltf` | `gltf_util.cpp` : paramètre `joint_offset` (gestion `align`/`prejoint` synthétiques) |
| `55c2a647` | `support reg` | `srpc.cpp` + `gsound-h.gc` + `gsound.gc` : support des **registres de son** (grains `SET_REGISTER`, `RAND_*`) |
| `9a68662e` | `misc changes` | Hooks GOAL : `link-art!` spécial-casé, `update-sound-banks`, `fill-skeleton-cache` réécrit, ~40 fichiers moteur adaptés |
| `13426eab` | `board files` | Le gameplay : `board-h.gc`, `target-board.gc`, `board-states.gc`, `board-part.gc`, `board-util.gc`, `board-overrides.gc` (~8 300 lignes) |
| `55c2a647`…`687b544c` | `makefile`, `menu`, `support reg` | Enregistrement `.gp`, entrée de menu, RPC |

<a name="12-les-trois-natures-dassets-injectés"></a>

## 1.2 Les trois natures d'assets injectés

Il est capital de distinguer **trois choses différentes**, chacune avec son propre pipeline :

### A. Un acteur **entièrement neuf** — la planche physique (`board`)

`custom_assets/jak1/models/custom_levels/board.glb` (~83 Ko).

- Aucun équivalent n'existe dans Jak 1 (ni dans Jak 2/3 sous une forme directement réutilisable comme
  acteur autonome Jak 1).
- Possède un **squelette propre** : joints `main centerTip leftTip leftFin leftTail centerTail
  rightTail rightTip outerScale innerScale centerDome` (+ `align` / `prejoint` synthétiques).
- Devient un **art-group compilé** `board-ag.go` + un `process` GOAL `board` (spawné par `target`,
  cf. `target-board.gc:897` `(process-spawn board :name "board" …)`).
- La planche « flex » en jeu via un `joint-mod` en mode `flex-blend` sur le joint `main`
  (`board-util.gc:148`).

### B. Des **art-groups d'animation** greffés sur des modèles existants (`eichar-board+0`, `sidekick-board+0`)

`custom_assets/jak1/models/custom_levels/eichar-board+0.glb` (~3 Mo) et
`sidekick-board+0.glb` (~2,2 Mo).

- Ce sont les modèles de **Jak** et **Daxter** en posture de planche, portant **~54 nouvelles
  animations** chacun (`jakb-board-*`, `daxter-board-*`).
- Le nom `eichar-board+0` suit la convention Naughty Dog des *art-groups additionnels* : `+0` = variante
  d'art-group rattachée au personnage `eichar` (= Jak).
- Ces animations sont **liées au master art-group existant** (`eichar`, `sidekick`) à des **index de
  slot précis** (180→233 pour Jak, 124→177 pour Daxter) via `:master-ag-map` (voir §1.3).
- Au runtime, le skelgroup du board pointe dessus :
  `board-h.gc` → `(set! (-> *jchar-board-sg* art-group-name) "eichar-board+0")`.

### C. Une **soundbank custom** (`BOARD.SBK`)

`custom_assets/jak1/sounds/sfx/BOARD/` : 45 `.wav` + `metadata.txt` (format lisible décrivant 32 sons
et 123 « grains »).

- Compilée en `BOARD.SBK` (format SBlk / SPU-ADPCM) et posée dans `$OUT/iso/`.
- Chargée dans un **slot de banque dédié** (`gBoardBank`, index 2 de l'overlord — déjà présent dans le
  code overlord commun car Jak 2 a un jetboard).

<a name="13-le-pipeline-modèle-glb-de-bout-en-bout"></a>

## 1.3 Le pipeline modèle GLB, de bout en bout

C'est le cœur de la question. Voici la chaîne complète pour `board.glb` →
planche visible et animée en jeu.

### Étape 1 — Fichier source

```
custom_assets/jak1/models/custom_levels/board.glb        ← lu par build-actor
custom_assets/jak1/models/common/board-lod0.glb          ← lu par le décompilateur (voie merc, cf. §1.7)
```

Le mod fournit **les deux copies** (identiques). Pour l'acteur board, la copie *faisant autorité* est
celle de `custom_levels/` (celle que `build-actor` consomme).

### Étape 2 — La macro `build-actor` dans `goal_src/jak1/game.gp`

```lisp
(defmacro build-actor (name &key (gen-mesh #f) &key (force-run #f) &key (texture-bucket 0)
                            &key (framerate 60.0) &key (master-art-group #f)
                            &key (master-ag-map ()) &key (joint-channel 6))
  (let* ((path (string-append "custom_assets/jak1/models/custom_levels/" name ".glb")))
    `(defstep :in '(,path ,gen-mesh ,force-run ,texture-bucket ,framerate
                    ,master-art-group ,master-ag-map ,joint-channel)
              :tool 'build-actor
              :out '(,(string-append "$OUT/obj/" name "-ag.go")))))
```

Appels concrets (`game.gp` ~1699) :

```lisp
(build-actor "board" :texture-bucket 2 :force-run #t)

(build-actor "eichar-board+0"
             :texture-bucket 2 :force-run #t :framerate 60 :joint-channel 24
             :master-art-group eichar
             :master-ag-map ((jakb-board-air-turn 180) (jakb-board-airwalk 181) … (jakb-board-turn-up 233)))

(build-actor "sidekick-board+0"
             :texture-bucket 2 :force-run #t :framerate 60 :joint-channel 24
             :master-art-group sidekick
             :master-ag-map ((daxter-board-air-turn 124) … (daxter-board-turn-up 177)))
```

`master-ag-map` = liste de paires `(nom-animation index-slot-dans-le-master-ag)`. À la compilation,
chaque `art-joint-anim` généré reçoit `master-art-group-name = "eichar"` et
`master-art-group-index = <slot>`, ce qui permet au code moteur d'aller chercher l'animation via
l'art-group `eichar` **existant** à un index libre.

### Étape 3 — `BuildActorTool` (`goalc/make/Tools.cpp`)

Le commit `e5f8cd1e` fait passer le nombre d'entrées de la step de 4 à 8 et parse les nouveaux
arguments :

```cpp
params.framerate = std::stof(task.input.at(4));
if (task.input.at(5) != "#f") params.master_art_group = task.input.at(5);
auto master_ag_list = m_reader.read_from_string(task.input.at(6));   // ((jakb-board-stance 180) …)
// → params.master_ag_map : std::map<std::string,int>
if (task.input.at(7) != "6") params.joint_channel = std::stoi(task.input.at(7));
return jak1::run_build_actor(task.input.at(0), task.output.at(0), params);
```

(Passage rendu possible par un patch de `MakeSystem::handle_defstep` : `defstep :in` accepte désormais
des **listes GOOS** en plus des chaînes — `o.print()` si `o.type != STRING`.)

### Étape 4 — `jak1::run_build_actor` (`goalc/build_actor/jak1/build_actor.cpp`)

1. `load_gltf_model(path)` (tinygltf).
2. `find_single_skin` → si présent : *« this actor will have a real skeleton »*.
3. **Détection du bone `align`** dans le skin GLTF :
   ```cpp
   const int merc_joint_offset = has_align_in_gltf ? 0 : 2;
   ```
4. `extract("test", extract_data, model, all_nodes, 0,0,0, merc_joint_offset)` → géométrie **merc**
   (draws, matériaux, textures, poids de skinning). C'est `MercExtract` partagé avec `merc_replacement`.
5. `convert_joints(skeleton_joints)` → squelette au format jeu :
   - si le GLTF contient un bone `align` : mapping **direct** (index GLTF == index joint jeu) ;
   - sinon : insertion de **2 joints synthétiques** `align` (0) et `prejoint` (1), puis les joints
     GLTF décalés de 2, avec `prejoint` pour parent des racines GLTF.
6. `process_anim(model, skeleton_joints, params.master_art_group, params.master_ag_map, params.framerate)`
   → pour chaque animation GLTF : `extract_anim_from_gltf` puis `compress_animation`
   (format `art-joint-anim` compressé PS2 : sections data64/32/16, control-bits). Le
   `master_art_group_name` / `_index` de `master_ag_map` est propagé dans le `CompressedAnim`.
7. Sérialisation de l'`ArtGroup` (`ArtJointGeo` slot 0, `ArtJointMesh` slot 1, puis un `ArtJointAnim`
   par animation) → `board-ag.go`.

Points sensibles corrigés dans le mod :

- `gltf_util.cpp` `convert_per_vertex_data(..., int joint_offset)` : les index de joints par-sommet
  doivent être décalés du même offset que le squelette (`+1` ou `+2`).
- `merc_replacement.cpp` : `int joints = get_joint_count(...)` (avant : `3 + count`, source d'un
  décalage).
- `animation_processing.cpp` : `out.joints.resize(std::max(max_joint + 1, 2))` — toujours au moins 2
  slots pour les joints-matrices `align` + `prejoint`.

### Étape 5 — Insertion dans le DGO

`goal_src/jak1/dgos/game.gd` :

```
"board-ag.go"
"eichar-board+0-ag.go"
"sidekick-board+0-ag.go"
```

Les `.go` sont donc embarqués dans **`GAME.CGO`**, chargé en permanence → l'acteur board est
**global** (disponible dans tous les niveaux), pas rattaché à un niveau.

### Étape 6 — Déclaration GOAL de l'acteur : la macro `def-actor`

`goal_src/jak1/engine/data/art-h.gc` fournit `def-actor` (système OpenGOAL moderne, remplace
`defskelgroup` manuel). Dans `board-h.gc` :

```lisp
(def-actor board
  :bounds (0 0 0 3.5)
  :art (board-idle-ja close-ja open-ja)
  :joints (align prejoint main centerTip leftTip leftFin leftTail centerTail
           rightTail rightTip outerScale innerScale centerDome)
  :texture-level 2 :sort 1)

(def-actor jchar-board :bounds (0 0 0 3.5)
  :art (jakb-board-air-turn-ja jakb-board-airwalk-ja … jakb-board-turn-up-ja)
  :texture-level 2 :sort 1)

(set! (-> *jchar-board-sg* art-group-name) "eichar-board+0")
(set! (-> *sidekick-board-sg* art-group-name) "sidekick-board+0")
```

`def-actor` génère automatiquement, à la compilation :

- `def-art-elt <name>-ag <name>-lod0-jg 0` (joint-geo), `<name>-lod0-mg 1` (merc-geo),
- un `def-art-elt` par entrée `:art` (les symboles `…-ja`, index 2, 3, …),
- un `def-joint-node` par entrée `:joints` (résolution de joint **par nom** → index),
- un `defskelgroup *<name>-sg*` complet (bounds, shadow, jgeo/janim/lods).

> **Note :** ni `board` ni les animations `board-*` ne sont écrits en dur dans `art-elts.gc` /
> `joint-nodes.gc` — `def-actor`/`def-art-elt` peuplent la table `*art-info*` à la compilation.

### Étape 7 — Liaison à l'exécution (`link-art!`)

`goal_src/jak1/engine/anim/joint.gc`, méthode `art-group::relocate` (commit `9a68662e`) :

```lisp
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "sidekick-board+0")
          (string= (-> this name) "eichar-board+0"))
      (link-art! this)))
```

**Pourquoi ce hack ?** `needs-link?` (natif) ne renvoie `#t` que si le **slot 0** de l'art-group est
un `art-joint-anim`. Or un art-group produit par `build-actor` **avec squelette** a un `joint-geo` en
slot 0. Les animations ne sont donc jamais liées automatiquement → il faut **spécial-caser le nom**
de l'art-group custom là où `link-art!` est appelé.

> ⚠️ Le tip [`jak2_modding_utilities/09_custom_art_groups_link_art.md`](../jak2_modding_utilities/09_custom_art_groups_link_art.md)
> documente qu'il ne faut **jamais** appeler `link-art!` depuis du code gameplay (`-init` d'acteur) :
> l'état des tableaux d'art-groups du niveau n'y est pas garanti cohérent → risque de crash mémoire.
> Le seul point sûr est `art-group::relocate` / le chemin de login.

### Schéma condensé

```
board.glb ──build-actor──► board-ag.go ──game.gd──► GAME.CGO ──(boot)──► login ──relocate──► link-art!
   │                            ▲                                                               │
   │  squelette + géométrie     │ master-ag-map (slots 180-233)                                 ▼
   └─ animations GLTF ──────────┘                                        *board-sg* / *jchar-board-sg*
                                                                        (def-actor → defskelgroup)
                                                                                 │
                                                            target ──process-spawn 'board──► planche visible + animée
```

<a name="14-doù-viennent-réellement-le-modèle-et-les-animations"></a>

## 1.4 D'où viennent réellement le modèle et les animations ?

### Les animations : décompilées depuis Jak 2 / Jak 3, exportées en GLTF

Le README du mod est explicite : *« the latest breakthrough came in April 2026 when I added support
for exporting animations »*. Mécanisme (commit `e5f8cd1e`) :

1. **`decompiler/level_extractor/extract_anim.cpp`** (nouveau) : parcourt les `art-joint-anim` d'un
   art-group de niveau, lit le format compressé PS2 (header 14 × control-bits, sections
   data64/32/16), **gère la décompression LZO** de Jak 2 / Jak 3 (`lzokay`), et range chaque
   animation sous `<master-art-group-name>-lod0`. Une table de remap gère les rares cas où le nom de
   modèle ≠ nom de master-ag (ex. `collectables-*` en Jak 3).

2. **`decompiler/level_extractor/fr3_to_gltf.cpp`** (`decompress_anim` + `add_animation_to_gltf`,
   nouveaux) : **décompresse** l'`art-joint-anim` en keyframes TRS explicites (quaternions à l'échelle
   `0.000030517578125`, translations `4/4096`, scale `0.000244140625`), **décompose les
   joints-matrices** `align`/`prejoint` (méthode de Shepperd pour matrice→quaternion), et ajoute les
   `channels` / `samplers` GLTF (`translation` / `rotation` / `scale`, interpolation `LINEAR`).

3. Déclencheur : option décompilateur **`rip_levels: true`** →
   `save_level_foreground_as_gltf(...)` écrit un `.glb` par art-group de niveau **dans
   `decompiler_out/<jeu>/levels/<niveau>/`**, contenant géométrie merc + squelette + **toutes** les
   animations natives décompressées.

Le README précise que `decompiler_out/jak3/levels/common/jakb-lod0.glb` contenait déjà **~280
animations Jak 3** prêtes à l'emploi. Le modeleur ouvre ce GLB dans Blender, garde les clips
`jakb-board-*`, et réexporte.

### Le format Blender : plugins fournis

`custom_assets/blender_plugins/` :

- `gltf2_blender_extract.py` — override du patch d'export glTF de Blender.
- `opengoal.py` — add-on OpenGOAL (conventions d'os, `align`, échelle, etc.).

Ils garantissent que le GLB réexporté a l'ordre de skin / la hiérarchie d'os / le bone `align`
attendus par `build-actor`.

### La planche physique `board.glb` : modèle neuf

Aucune extraction : c'est un modèle **modélisé à la main** (petit — 83 Ko), avec son squelette de
« flex » (`main`, `centerTip`, `*Tip`, `*Tail`, `*Fin`, `outerScale`, `innerScale`, `centerDome`).
Les animations `close-ja` / `open-ja` (déploiement des ailerons) et `board-idle-ja` sont authorées
dans le même GLB. Le README le liste d'ailleurs dans les TODO : *« Improve the models (Jak, Daxter,
jetboard) »*.

<a name="15-le-pipeline-son"></a>

## 1.5 Le pipeline son (soundbank custom `BOARD.SBK`)

### Extraction (référence)

`decompiler/data/extract_sbk.cpp` (nouveau, ~850 lignes) + option `rip_sound_banks: true` :
extrait chaque `.SBK` du jeu en `.wav` + `metadata.txt` dans `decompiler_out/<jeu>/audio/sfx/`.
Les banques SFX (`SBlk`) écrivent un `.wav` par son nommé ; les banques musique (`SBv2`) un `.wav`
par tone d'instrument.

### Reconstruction

`goalc/build_sbk/build_sbk.cpp` (nouveau, ~1000 lignes) + `goalc/build_sbk/main.cpp` (CLI autonome).
Deux modes :

- `create_sbk_from_dir(dir, out, opts)` — reconstruit une **nouvelle** banque à partir d'un dossier
  `metadata.txt` + `.wav`.
- `append_sbk_from_dir(base, dir, out)` — **ajoute** des sons à une banque existante (encore
  partiellement stubé dans le commit `e5f8cd1e`).

Encodage : WAV PCM → **SPU-ADPCM** (format PS2).

### Macros `.gp`

```lisp
(defmacro build-sbk (name &key (force-run #f) &key (bank-id 0) &key (manifest ()))
  (let* ((sfx-path (string-append "custom_assets/jak1/sounds/sfx/" name))
         (out-path (string-append "$OUT/iso/" name ".SBK")))
    `(begin
      (defstep :in '(,sfx-path ,force-run ,bank-id #t ,manifest) :tool 'build-sbk :out '(,out-path))
      (set! *all-sbk* (cons ,out-path *all-sbk*)))))
```

`manifest` = liste de paires ; plusieurs entrées dans une paire = **variantes** tirées au hasard par
`sound-play`. Dans le mod, le manifest est laissé commenté → la banque est reconstruite telle quelle
depuis `metadata.txt`.

Tools : `add_tool<BuildSbkTool>()` + `add_tool<AppendSbkTool>()` dans `MakeSystem.cpp`.

### Support des registres de son (`reg`) — commit `55c2a647`

Les grains PS2 (`SET_REGISTER`, `SET_REGISTER_RAND`, `RAND_PB`, `RAND_PLAY`…) utilisés massivement
par la banque BOARD pilotent des **registres** que le runtime OpenGOAL ne transmettait pas. Ajouté :

- `game/overlord/jak1/srpc.cpp` : si `mask & 0x800 / 0x1000 / 0x2000` → `snd_SetSoundReg(handle, 0/1/2, reg[i])`.
- `goal_src/jak1/engine/sound/gsound-h.gc` : champs `reg (uint8 3)` + overlay `group-and-reg (uint32 :overlay-at group)`
  dans `sound-play-parms` et `sound-spec`.
- `goal_src/jak1/engine/sound/gsound.gc` : `(set! (-> cmd parms group-and-reg) (-> spec group-and-reg))`
  au lieu de recopier seulement `group`.

### Chargement runtime — `goal_src/jak1/engine/level/level.gc`

```lisp
(define *board-bank-loaded?* #f)
(defun update-sound-banks ()
  (if (nonzero? (rpc-busy? RPC-SOUND-LOADER)) (return 0))
  (when (not *board-bank-loaded?*)
    (sound-bank-load (static-sound-name "board"))
    (true! *board-bank-loaded?*))
  …)
```

L'overlord commun (`game/overlord/common/sbank.cpp`) possède **déjà** un slot dédié
`gBoardBank` (index 2, pré-nommé `"board"` dans `InitBanks`) — hérité du fait que Jak 2 a un jetboard.
`LookupBank("board")` le retrouve par nom → **pas besoin** de toucher `AllocateBankName` en Jak 1.
(Ce n'est **pas** le cas si on ajoute une banque à un *nom nouveau* : cf.
[`jak2_modding_utilities/13`](../jak2_modding_utilities/13_custom_animation_and_sound_import_pipeline.md) §B2.)

<a name="16-modifications-c-transverses"></a>

## 1.6 Modifications C++ transverses

| Fichier | Changement | Raison |
|---|---|---|
| `common/util/gltf_util.{cpp,h}` | `convert_per_vertex_data` / `extract_and_flatten_joints_and_weights` reçoivent `int joint_offset` | aligner les index de joints par-sommet sur les joints synthétiques `align`/`prejoint` |
| `goalc/build_actor/common/build_actor.{cpp,h}` | `BuildActorParams` : `master_art_group`, `master_ag_map`, `framerate` ; `convert_joints` gère un `align` présent dans le GLTF ou en insère 2 synthétiques ; `process_anim` propage le master-ag | animations custom sur modèle existant + bone `align` |
| `goalc/build_actor/jak{1,2,3}/build_actor.{cpp,h}` | `BuildActorParams` → `BuildActorParams{1,2,3}` ; `ArtJointAnim` lit `master_art_group_{name,index}` du `CompressedAnim` (fallback slot 2) ; détection `has_align_in_gltf` → `merc_joint_offset` | idem, par jeu |
| `goalc/build_actor/common/animation_processing.{cpp,h}` | `extract_anim_from_gltf` / `compress_animation` : champs `master_art_group_*`, `resize(max(n,2))` | idem |
| `goalc/make/Tools.{cpp,h}` | `BuildActor*Tool` : 4 → 8 entrées ; `goos::Reader m_reader` ; `BuildSbkTool` / `AppendSbkTool` | passage de la map + soundbanks |
| `goalc/make/MakeSystem.cpp` | `handle_defstep` accepte des objets GOOS non-string ; enregistre les 2 outils SBK | passer `master-ag-map` en liste |
| `goalc/build_sbk/*` | **nouveau** — reconstruction SBK (SPU-ADPCM) | soundbank custom |
| `decompiler/data/extract_sbk.*` | **nouveau** — extraction SBK → wav + metadata | référence son |
| `decompiler/level_extractor/extract_anim.*` | **nouveau** — lecture `art-joint-anim` compressés (+ LZO Jak2/3) | export anims |
| `decompiler/level_extractor/fr3_to_gltf.cpp` | `decompress_anim`, `add_animation_to_gltf`, accessors d'anim ; envmap `KHR_materials_specular` ; rgba 4 canaux | GLB source avec animations |
| `decompiler/level_extractor/extract_level.cpp` | appelle `extract_animations(...)` par art-group | idem |
| `decompiler/level_extractor/merc_replacement.cpp` | `joints = get_joint_count(...)` (au lieu de `3 + …`) | décalage de joints |
| `decompiler/config.{cpp,h}` + `config/*/*_config.jsonc` | `rip_sound_banks` (défaut `true`) | extraction SBK |
| `game/overlord/jak1/srpc.cpp` | `snd_SetSoundReg` selon `mask` | grains à registres |
| `goal_src/jak1/engine/sound/gsound*.gc` | champs `reg` / `group-and-reg` | idem |

<a name="17-récapitulatif-les-3-voies-dinjection-de-modèle"></a>

## 1.7 Récapitulatif : les 3 voies d'injection de modèle dans OpenGOAL

| Voie | Dossier source | Consommateur | Sortie | Quand l'utiliser |
|---|---|---|---|---|
| **`merc_replacements`** | `custom_assets/jakN/merc_replacements/<ctrl>.glb` | `extract_merc.cpp` (`replace_model`) au moment `task extract` | remplace le merc `<ctrl>` **dans le FR3** du niveau | remplacer un modèle **existant** (skin custom de Jak, d'un ennemi…) |
| **modèle custom de niveau** | `custom_assets/jakN/models/<niveau|common>/<name>.glb` | `extract_merc.cpp` (`add_custom_model_to_level`) | **ajoute** un merc `<name>` au FR3 (niveau, ou `common` = tous) | prop/décor supplémentaire, pas d'acteur GOAL complet |
| **`build-actor` (acteur autonome)** | `custom_assets/jakN/models/custom_levels/<name>.glb` | outil `build-actor` (build-time) | **art-group `.go`** (`<name>-ag.go`) → dans un CGO/DGO | **acteur neuf** avec squelette, animations, `process` GOAL, skelgroup — **c'est la voie du board** |

> Le mod fournit `board-lod0.glb` **aussi** dans `models/common/` : cela déclenche en plus
> `add_custom_model_to_level` (le modèle est injecté comme merc `common`). Pour l'acteur board
> proprement dit, c'est néanmoins la sortie `build-actor` (`board-ag.go` listé dans `game.gd`) qui
> fait foi.

---

<a name="partie-2"></a>

# Partie 2 — Ce qui est déjà dans `jak-project` upstream

État de `D:\Developpement\OpenGoal Dev\jak-project` (branche `master`) au 2026-08-30 :

| Fonctionnalité | Statut upstream | Commit / fichier |
|---|---|---|
| `build-actor` **Jak 1** avec `master-art-group` / `master-ag-map` / `framerate` / `joint-channel` | ✅ présent | `e6260e48a` |
| `extract_anim` / export anims dans `fr3_to_gltf` | ✅ présent | `e6260e48a`, `3422e0525` |
| Export blerc (blend shapes) en GLB | ✅ présent | `0b799821e` |
| `extract_sbk` / `build_sbk` / `build_sbk/main.cpp` (CLI) | ✅ présent | `3678cbcc2` |
| Étape `append-sbk` + intégration `goalc/make` | ✅ présent (Jak 2 : `project-lib.gp`) | `3678cbcc2` |
| **`retarget_anim`** (CLI de reciblage d'anims par nom d'os) | ✅ présent | `3678cbcc2` (ta contribution du 21 août 2026) |
| Fix `AllocateBankName` / `game/overlord/common/sbank.cpp` | ✅ présent | `3678cbcc2` |
| Fix offset de joint `build_actor` (modèles avec `align`) | ✅ partiel | `3678cbcc2` |
| Docs : tips `09` (link-art), `10` (retargeting/offset), `11` (jetboard states), `13` (pipeline anim+son) | ✅ présents (Jak 2) | `docs/modding/jak2_modding_utilities/` |
| `config` `rip_sound_banks` | ✅ présent | `3678cbcc2` |

**Ce qui manque encore upstream (présent seulement dans `og-j1-board`) :**

1. **Support des registres de son (`reg`)** — `srpc.cpp` + `gsound-h.gc` + `gsound.gc`. Sans lui, une
   banque qui s'appuie sur des grains `SET_REGISTER*` / `RAND_*` (fréquent) ne se comportera pas
   correctement. **Non trivial et non spécifique au board.**
2. **`build-actor` Jak 2 / Jak 3** : les macros `project-lib.gp` restent **minimalistes**
   (`gen-mesh`, `force-run`, `texture-bucket` seulement) — pas de `master-art-group` / `master-ag-map`
   / `framerate` / `joint-channel` côté macro, alors que l'outil C++ les supporte.
3. **`gltf_util` `joint_offset` explicite** (voie `common/util/`) — upstream n'a qu'un fix partiel.
4. **Hook `link-art!` générique** : upstream et mod utilisent tous deux un **special-case par nom**
   d'art-group. Aucune liste déclarative.
5. **Convention de dossier + macro pour un acteur custom *global*** (embarqué dans `GAME.CGO`) : dans
   le mod c'est fait **à la main** en éditant `game.gd`. Pas de `(register-custom-actor …)`.
6. `add_custom_model_to_level` / `merc_replacements` : dossiers non uniformisés entre les 3 jeux
   (`custom_assets/jakN/models/` existe partout, mais `custom_levels/` vs `common/` vs
   `merc_replacements/` n'est pas documenté d'un seul endroit).

---

<a name="partie-3"></a>

# Partie 3 — Proposition de généralisation

**Objectif :** un pipeline unique *« injection d'asset »* pour Jak 1 / 2 / 3, couvrant **modèle**,
**animation** et **son**, avec des **conventions de dossiers**, des **macros `.gp` harmonisées** et
des **hooks runtime déclaratifs** — de sorte qu'ajouter un asset ne demande jamais d'éditer un `.gd`
ni de hard-coder un nom dans le moteur.

## 3.1 Arborescence `custom_assets/jakN/` unifiée

```
custom_assets/jakN/
├── models/
│   ├── actors/<name>.glb              # acteur autonome neuf → build-actor → <name>-ag.go
│   ├── merc_replacements/<ctrl>.glb   # remplace un merc existant (dans le FR3)
│   └── level_props/<level|common>/<name>.glb   # merc ajouté au FR3 (prop/décor)
├── anims/
│   └── <target-ag>/<clip>.glb         # clips à recibler sur un skeleton natif (target-ag)
└── sounds/
    └── <BANK>/                        # metadata.txt + *.wav (+ manifest.gd optionnel)
```

- `models/custom_levels/` (nom historique) → **alias déprécié** de `models/actors/` (garder la
  rétro-compat un temps).
- Une seule doc `docs/modding/*/NN_custom_asset_injection.md` décrivant les 3 sous-dossiers `models/`
  (remplace/étend le tableau §1.7 et le tip 13).

## 3.2 Macros `.gp` harmonisées entre les 3 jeux

### `build-actor` — porter la version Jak 1 vers Jak 2 / Jak 3

Aligner `goal_src/jak2/lib/project-lib.gp` et `goal_src/jak3/lib/project-lib.gp` sur la macro Jak 1
(`master-art-group`, `master-ag-map`, `framerate`, `joint-channel`) — l'outil C++ les gère déjà, seule
la macro GOOS bride Jak 2/3.

### `build-anim` — nouveau wrapper de haut niveau

```lisp
;; Recible <clip>.glb sur le squelette natif <target-ag> et lie l'anim au slot <slot>.
(build-anim "eichar"                       ; master art-group cible
  :base "$DECOMP/levels/common/eichar-lod0.glb"
  :source "custom_assets/jak1/anims/eichar/jakb-board-stance.glb"
  :clips ((jakb-board-stance 180) (jakb-board-turn 228) …))
```

Sous le capot : `retarget_anim` (déjà là) → GLB intermédiaire → `build-actor <name>+0`
`:master-art-group <target> :master-ag-map (...)`. Une seule ligne au lieu de la longue liste
`:master-ag-map` recopiée à la main dans `og-j1-board`.

### `build-sbk` / `append-sbk` — porter vers Jak 1 et Jak 3

Aujourd'hui intégrés côté Jak 2 (`project-lib.gp`). Généraliser les macros + `*all-sbk*` pour les 3
jeux (le mod montre la version Jak 1).

### `register-custom-actor` — nouveau

```lisp
(register-custom-actor "board" :dgo 'GAME)   ; ajoute "board-ag.go" à GAME.CGO + à la liste de link
```

Évite l'édition manuelle de `goal_src/jakN/dgos/game.gd`. La macro :
1. `set!` d'une liste `*custom-actor-art-groups*` (nom + DGO cible),
2. génération de l'entrée `.go` dans le `.gd` correspondant (ou un `custom.gd` dédié inclus par les
   CGO concernés),
3. alimentation du hook de link (voir 3.3).

## 3.3 Hook `link-art!` déclaratif (remplacer le special-case par nom)

**Problème actuel** (mod *et* upstream) :

```lisp
(if (or (needs-link? this) (string= (-> this name) "eichar-board+0") …) (link-art! this))
```

**Proposition — deux options, non exclusives :**

- **A (rapide) :** une liste `*custom-art-groups-to-link*` (peuplée par `register-custom-actor` /
  `build-anim`), consultée dans `art-group::relocate` :
  ```lisp
  (if (or (needs-link? this) (member? (-> this name) *custom-art-groups-to-link*)) (link-art! this))
  ```
- **B (propre) :** corriger `needs-link?` (`joint.gc`) pour renvoyer `#t` dès qu'un `art-joint-anim`
  est présent **à n'importe quel slot** (pas seulement le slot 0), en ignorant le `joint-geo` du slot
  0. À valider contre les art-groups natifs pour éviter les faux positifs (cf. avertissement du tip
  10 sur le comptage à la main).

## 3.4 Son — finir le travail

1. **Upstreamer le support `reg`** (`srpc.cpp` + `gsound-h.gc` + `gsound.gc`) pour les 3 jeux —
   c'est une capacité générale du moteur audio PS2, pas un détail board.
   - ⚠️ Jak 3 a un overlord son structurellement différent (`game/overlord/jak3/`) — adaptation
     spécifique.
2. **`AllocateBankName` / banques déclarées** : permettre de déclarer une banque dédiée custom (nom +
   taille SPU) via une petite table lue par `InitBanks`, au lieu d'ajouter un `gXxxBank` en dur.
3. **`task extract-sbk` / `task rip-anims <GAME> <LEVEL>`** : tasks Taskfile dédiées et documentées
   pour produire respectivement les `.wav`+`metadata.txt` et les GLB source d'animations
   (`rip_levels`), plutôt qu'un `--config-override` à retenir.

## 3.5 Plugins Blender

Verser `custom_assets/blender_plugins/` (`gltf2_blender_extract.py`, `opengoal.py`) dans
`jak-project` upstream (ils sont dans le mod, pas upstream) + une page
`docs/modding/*/NN_blender_export_setup.md` : version de Blender, installation de l'add-on, réglages
d'export glTF, convention du bone `align`.

## 3.6 Documentation cible

Un tip unifié **`docs/modding/jak1_modding_utilities/NN_custom_asset_injection.md`** (et miroir
Jak 3), bilingue, structuré :

- **Modèle** — les 3 voies (§1.7), quand choisir laquelle, `build-actor` pas à pas, pièges
  `align`/`prejoint`/`joint_offset`.
- **Animation** — `rip_levels` → GLB source → Blender → `retarget_anim` → `build-anim` → link.
  Renvoie au tip Jak 2 `13` (déjà excellent) plutôt que de le dupliquer.
- **Son** — `extract-sbk` → édition `metadata.txt`/`.wav` → `build-sbk`/`append-sbk` → slot de banque
  → chargement runtime → `reg` → `new-sound-id` pour les sons per-frame.
- **Runtime** — `def-actor`, skelgroup, hook `link-art!`, `register-custom-actor`.

## 3.7 Plan d'intégration incrémental (ordre suggéré)

| # | Lot | Portée | Risque |
|---|---|---|---|
| 1 | Harmoniser la macro `build-actor` Jak 2 / Jak 3 sur Jak 1 | GOOS uniquement | faible |
| 2 | Doc unifiée §1.7 (les 3 voies modèle) + `task` extract dédiées | docs + Taskfile | faible |
| 3 | Macro `build-anim` (wrapper `retarget_anim` + `build-actor`) | GOOS + un peu de C++ glue | moyen |
| 4 | `register-custom-actor` + liste `*custom-art-groups-to-link*` + hook générique | GOOS + `joint.gc` | moyen |
| 5 | Porter `build-sbk`/`append-sbk` vers Jak 1 & Jak 3 | GOOS + `MakeSystem` | moyen |
| 6 | Upstreamer support `reg` (Jak 1/2, puis Jak 3) | C++ runtime `game/overlord/**` | élevé (rebuild moteur, tests audio) |
| 7 | Plugins Blender versionnés + doc export | assets + docs | faible |
| 8 | `needs-link?` corrigé (option B) — si validé contre les art-groups natifs | `joint.gc` | élevé (régression possible sur acteurs natifs) |

---

## Annexe — fichiers clés à lire dans `og-j1-board`

| Sujet | Fichier |
|---|---|
| Déclarations de build | `goal_src/jak1/game.gp` (~228 macros, ~1699 appels board) |
| DGO | `goal_src/jak1/dgos/game.gd` (lignes `board-ag.go` etc.) |
| Outil build-actor | `goalc/make/Tools.cpp`, `goalc/build_actor/{common,jak1}/build_actor.cpp` |
| Joints synthétiques | `common/util/gltf_util.cpp`, `goalc/build_actor/common/build_actor.cpp` (`convert_joints`) |
| Export d'anims | `decompiler/level_extractor/{extract_anim,fr3_to_gltf}.cpp` |
| Soundbank | `goalc/build_sbk/build_sbk.cpp`, `decompiler/data/extract_sbk.cpp` |
| Registres son | `game/overlord/jak1/srpc.cpp`, `goal_src/jak1/engine/sound/gsound-h.gc` |
| Déclaration acteur | `goal_src/jak1/engine/data/art-h.gc` (`def-actor`, `defskelgroup`) |
| Gameplay board | `goal_src/jak1/engine/target/board/board-h.gc` (`def-actor board`, skelgroups) |
| Hook de link | `goal_src/jak1/engine/anim/joint.gc` (`art-group::relocate`) |
| Chargement banque | `goal_src/jak1/engine/level/level.gc` (`update-sound-banks`) |
