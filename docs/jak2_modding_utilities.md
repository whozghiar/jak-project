# Jak 2 — Modding Notes & Runtime Memory Architecture / Notes de Modding & Architecture Mémoire

> **Bilingual Knowledge Base / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Table of Contents
- [1. Core Vocabulary](#1-core-vocabulary)
- [2. Runtime Memory Architecture](#2-runtime-memory-architecture)
- [3. Where Memory Constants Are Defined](#3-where-memory-constants-are-defined)
- [4. Case Study: Increasing Memory for Jak 2 (512 MB)](#4-case-study-increasing-memory-for-jak-2-512-mb)
- [5. Compiling and Validating GOAL Changes](#5-compiling-and-validating-goal-changes)
- [6. Running the Game & Reading Boot Logs](#6-running-the-game--reading-boot-logs)
- [7. In-Game Memory Diagnostic Tools](#7-in-game-memory-diagnostic-tools)
- [8. Known Pitfalls & Points of Vigilance](#8-known-pitfalls--points-of-vigilance)
- [9. Custom Art-Groups: Dynamically Linking Imported Animations](#9-custom-art-groups-dynamically-linking-imported-animations)

---

### 1. Core Vocabulary

| Term | Meaning |
|---|---|
| **EE** | "Emotion Engine", the main PS2 CPU. The PC port emulates its main memory by reserving a contiguous block via `mmap` (see `game/runtime.cpp`). |
| **GOAL** | The custom Lisp/Scheme dialect in which all original Naughty Dog game code is written (`goal_src/**/*.gc`). Compiled by **OpenGOAL**. |
| **`goalc`** | The OpenGOAL compiler executable. Runs in interactive REPL mode (`task repl`) or batch mode (`-c "(command)"`). |
| **`gk`** | The C++ runtime executable ("game kernel") that loads and executes compiled GOAL code. |
| **DGO** | "Data Group Object" — a package bundling compiled GOAL objects (code + data) loaded together from disk. |
| **Heap** | A memory arena allocated in bulk, within which GOAL dynamically allocates its own objects. |
| **`valid?`** | GOAL function in `gcommon.gc` checking pointer alignment and address boundaries before dereferencing. |

---

### 2. Runtime Memory Architecture

The runtime reserves **a single large contiguous virtual memory block** at startup (`EE_MAIN_MEM_SIZE`, via `mmap` in `game/runtime.cpp:161-171`), simulating the PS2 RAM. Everything lives inside this block at fixed offsets:

```
0x000000 ─────────────────────────────────────────────────────────────────► EE_MAIN_MEM_SIZE
│
├─ 0x000000 – 0x080000  Low protected area (EE_MAIN_MEM_LOW_PROTECT, like PS2 kernel)
├─ 0x013fd20            HEAP_START — start of the "global heap"
│                        (types, core processes, kernel code, symbol table…)
├─ 0x12D00000           GLOBAL_HEAP_END (with BIG_MEMORY enabled on PC)
│                        └─ "level heap" is allocated INSIDE the remaining global heap
│                           when a level loads (see goal_src/<game>/engine/level/level.gc)
├─ (free space buffer)
├─ 0x14000000           DEBUG_HEAP_START — separate heap for debug/REPL tools
└─ 512 MB (0x20000000)  End of reserved EE memory
```

**Key Points:**
- `GLOBAL_HEAP_END`, `DEBUG_HEAP_START`, and `EE_MAIN_MEM_SIZE` are defined in **shared C++ code across all games** (`common/goal_constants.h`, `game/kernel/common/memory_layout.h`).
- The **level heap** is allocated via `kmalloc` from the global heap when loading a level. Its maximum size is defined **per game in GOAL** via `DEBUG_LEVEL_HEAP_MULT` in `goal_src/<game>/engine/level/level.gc`.
- `valid?` (in `gcommon.gc`) rejects any pointer `>= END_OF_MEMORY`. If `END_OF_MEMORY` remains at the 128 MB PS2 limit (`0x8000000`) while memory is expanded to 512 MB, objects allocated above 128 MB trigger `"bad address"` errors.

---

### 3. Where Memory Constants Are Defined

| Constant | File | Scope |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | **Shared** (all games) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | **Shared** |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | **Shared** |
| `DEBUG_HEAP_SIZE` | `game/kernel/common/memory_layout.h` | Per-game namespace, identical values |
| `END_OF_MEMORY` (used by `valid?`) | `goal_src/<game>/kernel/gcommon.gc` | **Per-game** |
| `DEBUG_LEVEL_HEAP_MULT` (level heap multiplier) | `goal_src/<game>/engine/level/level.gc` | **Per-game** |

---

### 4. Case Study: Increasing Memory for Jak 2 (512 MB)

When porting the 512 MB memory increase from Jak 3 to Jak 2:
- C++ shared constants (`EE_MAIN_MEM_SIZE`, `GLOBAL_HEAP_END`) were already active on `master`.
- `END_OF_MEMORY` in `goal_src/jak2/kernel/gcommon.gc` was raised to `#x20000000` (512 MB).
- **The Pitfall:** Setting `DEBUG_LEVEL_HEAP_MULT` to `15.0` (Jak 3's value) caused out-of-memory kernel panics at boot because Jak 2 loads ~35 MB of resident code before the first level, leaving ~279 MB free. A multiplier of `15.0` requested 282 MB.
- **The Validated Fix:** Setting `DEBUG_LEVEL_HEAP_MULT = 12.0` allocates ~215 MB, leaving a safe 60 MB buffer while providing a **10× increase** over the PS2 original (1.1×).

---

### 5. Compiling and Validating GOAL Changes

Compile the entire project in batch mode:
```bash
./goalc.exe --game jak2 -c "(mi)"
```
Or interactively in REPL:
```bash
task repl
# In REPL:
(mi)
```

---

### 6. Running the Game & Reading Boot Logs

Boot with debug and verbose logging:
```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Check log files in `log/jak2.<timestamp>.log`:
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

---

### 7. In-Game Memory Diagnostic Tools

To display the live memory overlay in `-debug` mode:
```lisp
(set! *stats-memory* #t)
```
This prints the real-time breakdown of textures, collision, animations, and level heap usage per loaded sector.

---

### 8. Known Pitfalls & Points of Vigilance

1. **Shared C++ Constants:** Modifying `GLOBAL_HEAP_END` affects Jak 1, 2, 3, and Jak X simultaneously.
2. **Boot Allocation Differences:** Available global heap budget varies per game depending on resident boot code.
3. **Always Validate at Runtime:** A change that compiles cleanly can still crash at runtime; always verify via `(mi)` -> boot -> log check.

---

### 9. Custom Art-Groups: Dynamically Linking Imported Animations

#### The Requirement
Add custom animations imported from a `.glb` into a resident character art-group (`jakb-ag`, `daxter-ag`) without modifying or recompiling the hundreds of native animations.

#### The Engine Mechanism
1. `build-actor` (in `goal_src/jak2/game.gp`) uses `:master-art-group` and `:master-ag-map` to bake target slot indices into the compiled art-group.
2. `link-art!` (`loader.gc`) iterates through the custom group's entries and attaches pointers to the target slots in the master group.
3. `needs-link?` (`joint.gc`) only returns `#t` if slot 0 is an `art-joint-anim`. In `build-actor` outputs with a skeleton, slot 0 is a `joint-geo`, so `needs-link?` is always `#f`.

#### ⚠️ Where to Hook `link-art!`
- ❌ **NEVER call `link-art!` during gameplay** (e.g. `target-board-init`): level art-group array states may be inconsistent, risking memory crashes.
- ✅ **The Correct Hook is `art-group::relocate`** in `goal_src/jak2/engine/anim/joint.gc`:
```lisp
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "jakb-jak3-board-import"))
      (link-art! this)))
```

### 10. GLTF Animation Retargeting & `build-actor` Joint Indexing

#### Skeletons in OpenGOAL vs GLTF
In OpenGOAL, character skeletons (like `jakb-lod0-jg`) contain:
1. **2 Matrix joints (indices 0 & 1):** `align` (Matrix 0) and `prejoint` (Matrix 1).
2. **61 TransformQ joints (indices 2 to 62):** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

#### ⚠️ The Duplicate `align` Pitfall in `build-actor` (Off-By-One Shift)
- `convert_joints` in `goalc/build_actor/common/build_actor.cpp` historically prepended a synthetic `"align"` joint at index 0 and offset all GLTF skin joints by `+1` (assuming external models lacked an align joint).
- Because decompiled models (`jakb-lod0.glb`) **already include `align` at index 0**, this created 64 joints instead of 63, shifting every TransformQ joint by `+1` during playback (`main` mapped to `waist_prog`, `waist_prog` to `upper_body`, `hips` to `Lthigh`).
- **Symptom:** Animation looks 100% perfect in Blender, but in-game the mesh stretches/dislocates violently whenever the imported animation is evaluated.
- **Rule:** Always detect if `gjoints[0].name == "align"` and use direct 0-indexed mapping (`prefix_count = 0`), producing `num_joints = 61` matching native `jakb-ag`.

---

# 🇫🇷 Version Française

## Sommaire
- [1. Le vocabulaire de base](#1-le-vocabulaire-de-base-1)
- [2. L'architecture mémoire du runtime](#2-larchitecture-mémoire-du-runtime-1)
- [3. Où sont définies les constantes mémoire](#3-où-sont-définies-les-constantes-mémoire-1)
- [4. Étude de cas : augmenter la mémoire pour Jak 2 (512 Mo)](#4-étude-de-cas--augmenter-la-mémoire-pour-jak-2-512-mo)
- [5. Compiler et valider un changement GOAL](#5-compiler-et-valider-un-changement-goal-1)
- [6. Lancer le jeu et lire les logs de boot](#6-lancer-le-jeu-et-lire-les-logs-de-boot-1)
- [7. Outils de diagnostic mémoire en jeu](#7-outils-de-diagnostic-mémoire-en-jeu-1)
- [8. Pièges connus / points de vigilance](#8-pièges-connus--points-de-vigilance-1)
- [9. Art-groups custom : lier des animations importées](#9-art-groups-custom--lier-des-animations-importées)
- [10. Reciblage d'Animations GLTF & Indexation de Squelette dans `build-actor`](#10-reciblage-danimations-gltf--indexation-de-squelette-dans-build-actor)

---

### 1. Le vocabulaire de base

| Terme | Signification |
|---|---|
| **EE** | "Emotion Engine", le processeur principal de la PS2. Le port PC émule sa mémoire en réservant un bloc via `mmap` (`game/runtime.cpp`). |
| **GOAL** | Le dialecte Lisp/Scheme de Naughty Dog dans lequel tout le jeu est programmé (`goal_src/**/*.gc`). Compilé par **OpenGOAL**. |
| **`goalc`** | L'exécutable du compilateur OpenGOAL (mode REPL `task repl` ou mode batch avec `-c`). |
| **`gk`** | L'exécutable du runtime C++ ("game kernel") qui charge et exécute le code GOAL compilé. |
| **DGO** | "Data Group Object" — conteneur regroupant du code et des données GOAL chargés ensemble depuis le disque. |
| **Heap** | Arène de mémoire allouée en bloc, dans laquelle GOAL alloue ses objets. |
| **`valid?`** | Fonction GOAL (`gcommon.gc`) validant l'alignement et les bornes d'un pointeur avant déréférencement. |

---

### 2. L'architecture mémoire du runtime

Le runtime réserve un bloc de mémoire virtuelle contiguë (`EE_MAIN_MEM_SIZE` via `mmap`), simulant la RAM de la PS2 :

```
0x000000 ─────────────────────────────────────────────────────────────────► EE_MAIN_MEM_SIZE
│
├─ 0x000000 – 0x080000  Zone basse protégée (EE_MAIN_MEM_LOW_PROTECT)
├─ 0x013fd20            HEAP_START — début du "global heap"
│                        (types, process de base, code kernel, table des symboles…)
├─ 0x12D00000           GLOBAL_HEAP_END (avec BIG_MEMORY sur PC)
│                        └─ Le "level heap" est alloué DANS l'espace restant du global heap
├─ (espace libre de sécurité)
├─ 0x14000000           DEBUG_HEAP_START — heap séparé pour les outils de debug
└─ 512 Mo (0x20000000)  Fin de la mémoire EE
```

**Points clés :**
- `GLOBAL_HEAP_END`, `DEBUG_HEAP_START` et `EE_MAIN_MEM_SIZE` sont partagés entre tous les jeux en C++ (`common/goal_constants.h`, `memory_layout.h`).
- Le **level heap** est alloué par `kmalloc` dans le global heap au chargement d'un niveau. Sa taille maximale est définie en GOAL par `DEBUG_LEVEL_HEAP_MULT` dans `goal_src/<jeu>/engine/level/level.gc`.
- `valid?` (`gcommon.gc`) rejette tout pointeur `>= END_OF_MEMORY`. Il faut aligner cette borne sur 512 Mo (`#x20000000`).

---

### 3. Où sont définies les constantes mémoire

| Constante | Fichier | Portée |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | **Partagée** (tous les jeux) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_SIZE` | `game/kernel/common/memory_layout.h` | Par namespace de jeu |
| `END_OF_MEMORY` (utilisé par `valid?`) | `goal_src/<jeu>/kernel/gcommon.gc` | **Par jeu** |
| `DEBUG_LEVEL_HEAP_MULT` (multiplicateur level heap) | `goal_src/<jeu>/engine/level/level.gc` | **Par jeu** |

---

### 4. Étude de cas : augmenter la mémoire pour Jak 2 (512 Mo)

- `END_OF_MEMORY` dans `goal_src/jak2/kernel/gcommon.gc` a été passé à `#x20000000` (512 Mo).
- **Le piège :** `DEBUG_LEVEL_HEAP_MULT = 15.0` (valeur de Jak 3) faisait crasher Jak 2 au boot car Jak 2 charge ~35 Mo de code résident avant le premier niveau (laissant ~279 Mo libres, insuffisant pour les 282 Mo demandés par 15.0).
- **La valeur retenue :** `DEBUG_LEVEL_HEAP_MULT = 12.0` alloue ~215 Mo, laissant une marge de sécurité de 60 Mo sous le budget disponible tout en augmentant la taille par **10×** par rapport à l'original (1.1×).

---

### 5. Compiler et valider un changement GOAL

```bash
# Compilation batch
./goalc.exe --game jak2 -c "(mi)"

# Ou via le REPL interactif
task repl
(mi)
```

---

### 6. Lancer le jeu et lire les logs de boot

```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Vérification des logs :
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<horodatage>.log
```

---

### 7. Outils de diagnostic mémoire en jeu

Pour afficher l'overlay mémoire en continu en mode debug :
```lisp
(set! *stats-memory* #t)
```

---

### 8. Pièges connus / points de vigilance

1. **Constantes C++ partagées :** Modifier `GLOBAL_HEAP_END` impacte Jak 1, 2, 3 et Jak X simultanément.
2. **Budgets variables selon le jeu :** La mémoire libre au boot dépend de la quantité de code résident initialement chargé.
3. **Toujours tester en jeu :** Valider systématiquement par la boucle : Compilation `(mi)` -> Boot `gk.exe` -> Vérification des logs.

---

### 9. Art-groups custom : lier des animations importées

#### Le besoin
Ajouter des animations custom depuis un fichier `.glb` sur un art-group résident (`jakb-ag`, `daxter-ag`) sans recompiler ni modifier les centaines d'animations natives.

#### Le mécanisme moteur
1. `build-actor` (`game.gp`) utilise `:master-art-group` et `:master-ag-map` pour injecter les index cibles dans l'art-group compilé.
2. `link-art!` (`loader.gc`) relie les pointeurs des animations custom dans les slots réservés du master art-group.
3. `needs-link?` (`joint.gc`) renvoie toujours `#f` sur un art-group issu de `build-actor` avec squelette car le slot 0 est un `joint-geo`.

#### ⚠️ Emplacement du hook `link-art!`
- ❌ **Ne jamais appeler `link-art!` depuis du code gameplay** (risque de crash d'alignement mémoire).
- ✅ **Le point d'injection propre est `art-group::relocate`** dans `goal_src/jak2/engine/anim/joint.gc` :
```lisp
(when (or (not s5-1) (= (-> s5-1 name) 'default))
  (login this)
  (if (or (needs-link? this)
          (string= (-> this name) "jakb-jak3-board-import"))
      (link-art! this)))
```

---

### 10. Reciblage d'Animations GLTF & Indexation de Squelette dans `build-actor`

#### Structure des Squelettes dans OpenGOAL vs GLTF
Dans OpenGOAL, le squelette d'un personnage principal (`jakb-lod0-jg`) comprend :
1. **2 Matrix joints (index 0 et 1) :** `align` (Matrix 0) et `prejoint` (Matrix 1).
2. **61 TransformQ joints (index 2 à 62) :** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

#### ⚠️ Le Piège de l'os `align` doublon dans `build-actor` (Décalage Off-By-One)
- `convert_joints` dans `goalc/build_actor/common/build_actor.cpp` insérait historiquement un os `"align"` synthétique à l'index 0 et décalait tous les os du GLTF de `+1` (conçu à l'origine pour des modèles externes sans align).
- Comme les modèles décompilés (`jakb-lod0.glb`) **contiennent DÉJÀ `align` à l'index 0**, cela créait 64 joints au lieu de 63, décalant chaque os TransformQ de `+1` à la lecture du clip (`main` prenait `waist_prog`, `waist_prog` prenait `upper_body`, `hips` prenait `Lthigh`).
- **Symptôme :** L'animation paraît 100% parfaite dans Blender, mais en jeu le personnage se disloque/s'étire violemment dès que l'animation importée est jouée.
- **Règle :** Toujours vérifier si `gjoints[0].name == "align"` pour utiliser une indexation directe à 0 (`prefix_count = 0`), produisant `num_joints = 61` conforme au master art-group `jakb-ag`.

---

### 11. Gestion des États Jetboard (`target-board-exit` Whitelist & Orientation)

#### ⚠️ Le Piège de la Liste Blanche `target-board-exit` (Le Bug du Mini-Jetboard)
Dans Jak 2, le jetboard (`board-lod0`) est un processus acteur indépendant (`board.gc`) qui s'ancre sur `node-list data 25` et possède deux états visuels :
1. **`use` (`board-open-ja`) :** Ailerons et pointes déployés en mode snowboard/surf complet.
2. **`idle` (`board-close-ja`) :** Rétracté dans son dôme central (petit disque rond pour le dos de Jak).

- La fonction `target-board-exit` (`target-board.gc:882`) possède une **liste blanche codée en dur** des états de jetboard valides.
- Lors de l'ajout d'un nouvel état de jetboard (ex: `target-board-turn-around`), **il DOIT être ajouté à la liste blanche** de `target-board-exit`, `target-board-pre-move` et `target-board-real-post`.
- **Symptôme si omis :** Dès l'entrée dans le nouvel état, le moteur croit que Jak descend du skate, efface `(focus-status board)`, et l'acteur `board` bascule instantanément en `idle` / `board-close-ja` (la planche se rétracte en mini-rondelle sous les pieds de Jak).

#### Orientation & Maintien de Vélocité à la Sortie d'un État
Pour garantir un changement de cap complet (ex: demi-tour à 180°) sans dépendre du joystick du joueur :
1. `(quaternion-copy! (-> self control quat-for-control) (-> self control dir-targ))` : Inverse le quaternion de contrôle.
2. `(set-quaternion! (-> self control) (-> self control dir-targ))` : Inverse l'orientation du root-transform.
3. `(vector-z-quaternion! (-> self control transv) (-> self control dir-targ))` & `(vector-float*! (-> self control transv) ... f30-0)` : Aligne la vélocité monde.
4. `(set-forward-vel f30-0)` & `(set! (-> self control ctrl-xz-vel) f30-0)` : Transmet la vitesse scalaire vers l'avant.
