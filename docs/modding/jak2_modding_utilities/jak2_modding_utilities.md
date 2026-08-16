# Jak 2 — Modding Notes & Engine Utilities / Notes de Modding & Utilitaires Moteur

> **Bilingual Knowledge Base / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Table of Contents
- [1. Core Vocabulary](#1-core-vocabulary)
- [2. Runtime Memory Architecture](#2-runtime-memory-architecture)
- [3. Memory Constants Definition](#3-memory-constants-definition)
- [4. 512 MB Memory Expansion](#4-512-mb-memory-expansion)
- [5. Compiling & Validating GOAL Changes](#5-compiling-validating-goal-changes)
- [6. Running the Game & Reading Boot Logs](#6-running-the-game-reading-boot-logs)
- [7. In-Game Memory Diagnostics](#7-in-game-memory-diagnostics)
- [8. Known Pitfalls & Best Practices](#8-known-pitfalls-best-practices)
- [9. Custom Art-Groups & Dynamic Animation Linking (`link-art!`)](#9-custom-art-groups-dynamic-animation-linking-link-art)
- [10. GLTF Retargeting & `build-actor` Skeletons](#10-gltf-retargeting-build-actor-skeletons)
- [11. Jetboard State Handling & Particle Tracking](#11-jetboard-state-handling-particle-tracking)
- [12. Generic Enemy Death Effect (Purple Skeleton-Dissolve Particles)](#12-generic-enemy-death-effect-purple-skeleton-dissolve-particles)

---

### 1. Core Vocabulary

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

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

---

### 2. Runtime Memory Architecture

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

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

**Key Principles:**
- `GLOBAL_HEAP_END`, `DEBUG_HEAP_START`, and `EE_MAIN_MEM_SIZE` are defined in **shared C++ code across all games** (`common/goal_constants.h`, `game/kernel/common/memory_layout.h`).
- The **level heap** is allocated via `kmalloc` from the global heap when loading a level. Its maximum size is defined **per game in GOAL** via `DEBUG_LEVEL_HEAP_MULT` in `goal_src/<game>/engine/level/level.gc`.
- `valid?` (in `gcommon.gc`) rejects any pointer `>= END_OF_MEMORY`. If `END_OF_MEMORY` remains at the 128 MB PS2 limit (`0x8000000`) while memory is expanded to 512 MB, objects allocated above 128 MB trigger `"bad address"` errors.

---

---

### 3. Memory Constants Definition

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

| Constant | File | Scope |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | **Shared** (all games) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | **Shared** |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | **Shared** |
| `DEBUG_HEAP_SIZE` | `game/kernel/common/memory_layout.h` | Per-game namespace, identical values |
| `END_OF_MEMORY` (used by `valid?`) | `goal_src/<game>/kernel/gcommon.gc` | **Per-game** |
| `DEBUG_LEVEL_HEAP_MULT` (level heap multiplier) | `goal_src/<game>/engine/level/level.gc` | **Per-game** |

---

---

### 4. 512 MB Memory Expansion

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

When porting the 512 MB memory increase from Jak 3 to Jak 2:
- C++ shared constants (`EE_MAIN_MEM_SIZE`, `GLOBAL_HEAP_END`) were already active on `master`.
- `END_OF_MEMORY` in `goal_src/jak2/kernel/gcommon.gc` was raised to `#x20000000` (512 MB).
- **The Pitfall:** Setting `DEBUG_LEVEL_HEAP_MULT` to `15.0` (Jak 3's value) caused out-of-memory kernel panics at boot because Jak 2 loads ~35 MB of resident code before the first level, leaving ~279 MB free. A multiplier of `15.0` requested 282 MB.
- **The Validated Fix:** Setting `DEBUG_LEVEL_HEAP_MULT = 12.0` allocates ~215 MB, leaving a safe 60 MB buffer while providing a **10× increase** over the PS2 original (1.1×).

---

---

### 5. Compiling & Validating GOAL Changes

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

Compile the entire project in batch mode:
```bash
./goalc.exe --game jak2 -c "(mi)"
```
Or interactively in the OpenGOAL REPL:
```bash
task repl
# Inside REPL:
(mi)
```

---

---

### 6. Running the Game & Reading Boot Logs

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

Boot with debug and verbose logging:
```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Check log files in `log/jak2.<timestamp>.log`:
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

---

---

### 7. In-Game Memory Diagnostics

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

To display the live memory overlay in `-debug` mode:
```lisp
(set! *stats-memory* #t)
```
This prints the real-time breakdown of textures, collision, animations, and level heap usage per loaded sector.

---

---

### 8. Known Pitfalls & Best Practices

> **Origin / Provenance:** `jak2/config/memory_increase` | **Last Updated:** `jak2/features/jak3-jetBoard`

1. **Shared C++ Constants:** Modifying `GLOBAL_HEAP_END` affects Jak 1, 2, 3, and Jak X simultaneously.
2. **Boot Allocation Differences:** Available global heap budget varies per game depending on resident boot code.
3. **Always Validate at Runtime:** A change that compiles cleanly can still crash at runtime; always verify via `(mi)` -> boot -> log check.

---

---

### 9. Custom Art-Groups & Dynamic Animation Linking (`link-art!`)

> **Origin / Provenance:** `jak2/features/jak3-jetBoard`

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

---

### 10. GLTF Retargeting & `build-actor` Skeletons

> **Origin / Provenance:** `jak2/features/jak3-jetBoard`

### Skeletons in OpenGOAL vs GLTF
In OpenGOAL, character skeletons (like `jakb-lod0-jg`) contain:
1. **2 Matrix joints (indices 0 & 1):** `align` (Matrix 0) and `prejoint` (Matrix 1).
2. **61 TransformQ joints (indices 2 to 62):** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

### ⚠️ The Duplicate `align` Pitfall in `build-actor` (Off-By-One Shift)
- `convert_joints` in `goalc/build_actor/common/build_actor.cpp` historically prepended a synthetic `"align"` joint at index 0 and offset all GLTF skin joints by `+1` (assuming external models lacked an align joint).
- Because decompiled models (`jakb-lod0.glb`) **already include `align` at index 0**, this created 64 joints instead of 63, shifting every TransformQ joint by `+1` during playback (`main` mapped to `waist_prog`, `waist_prog` to `upper_body`, `hips` to `Lthigh`).
- **Symptom:** Animation looks 100% perfect in Blender, but in-game the mesh stretches/dislocates violently whenever the imported animation is evaluated.
- **Rule:** Always detect if `gjoints[0].name == "align"` and use direct 0-indexed mapping (`prefix_count = 0`), producing `num_joints = 61` matching native `jakb-ag`.

---

---

### 11. Jetboard State Handling & Particle Tracking

> **Origin / Provenance:** `jak2/features/jak3-jetBoard`

### ⚠️ The `target-board-exit` Whitelist Pitfall (The Mini-Jetboard Bug)
In Jak 2, the jetboard (`board-lod0`) is a standalone actor process (`board.gc`) anchored to `node-list data 25` with two distinct visual states:
1. **`use` (`board-open-ja`):** Fins, wings, and tips deployed in full snowboard/surfboard shape.
2. **`idle` (`board-close-ja`):** Fully retracted into its center dome (a small round disc for Jak's back).

- The `target-board-exit` function (`target-board.gc:882`) contains a **hardcoded whitelist** of valid board states.
- When creating a new board state (e.g. `target-board-turn-around`), **it MUST be added to the whitelist** in `target-board-exit`, `target-board-pre-move`, and `target-board-real-post`.
- **Symptom if omitted:** Upon entering the new state, the engine assumes Jak is dismounting, clears `(focus-status board)`, and the `board` actor instantly drops to `idle` / `board-close-ja` (the board shrinks into a mini-puck under Jak's boots).

### Autonomous Rotation & Pad Steering Lockout (`turn-lockout-end-time`)
During autonomous animation-driven turns, `target-board-real-post` continuously executes `read-pad` and calls `turn-to-vector` (or `rot->dir-targ!` on neutral stick), which can overwrite `dir-targ` every frame with the player's stick input or reset it to the previous facing quaternion.
- **Fix:** Set `(set! (-> self control turn-lockout-end-time) (+ (current-time) (seconds 1.5)))` in `:enter` (and reset to 0 in `:exit`), ensuring standard stick steering is suppressed until the turnaround completes.
- **Entry Momentum:** Calculate entry velocity using `(fmax (-> self control ctrl-xz-vel) (vector-length (vector-flatten! (new-stack-vector0) (-> self control transv) (-> self control dynam gravity-normal))) 40960.0)` so momentum is preserved even if the player was drifting or gliding without forward stick input.

### Heading Inversion, Boost & Forward Momentum on State Exit
To guarantee a complete autonomous heading change (e.g. 180° turnaround) and reward the player:
1. `(quaternion-copy! (-> self control quat-for-control) (-> self control dir-targ))`: Inverts the control quaternion.
2. `(set-quaternion! (-> self control) (-> self control dir-targ))`: Inverts root-transform orientation.
3. `(vector-z-quaternion! (-> self control transv) (-> self control dir-targ))` & `(vector-float*! (-> self control transv) ... f30-1)`: Re-aligns world velocity in the reversed heading with acceleration boost (`(fmax (+ f30-0 20480.0) 114688.0)`).
4. `(set-forward-vel f30-1)` & `(set! (-> self control ctrl-xz-vel) f30-1)`: Passes scalar forward velocity.
5. `(sound-play "board-boost")`, `(cpad-set-buzz!)`, and `part-tracker-spawn group-board-land-straight`: Plays audio, rumble, and landing dust VFX matching native spin-trick rewards.

### Dynamic Joint Tracking, Particle Ripples & Collision Spheres (`board-zap-track`)
For area-of-effect attacks while riding (e.g. `board-zap`):
- **Dynamic Tracking:** Sparticle callbacks (`(:func 'board-zap-track)`) should query `*target*` directly and copy the board joint translation `(joint-node-index jakb-lod0-jg board)` into `(-> arg2 x/y/z)`. In parallel, `part-tracker-spawn` should pass `:callback part-tracker-track-target`. This ensures all particles and the tracker process follow the moving board in real time at high velocity.
- **Concentric Multi-Ring Ripple:** Replicating Jak 3's `group-board-zap-attack` (`:num 0.25`, `:length (seconds 0.335)`, `:scalevel-x (meters 0.16666667)`) emits 4 to 5 concentric ripples expanding up to $3.0\text{ m}$.
- **Damage Radius Alignment:** Configure the attack collision sphere in `target-util.gc` (`sphere<-vector+r!`) to $12288.0$ ($3.0\text{ m}$) with root bounding sphere $13107.2$ ($3.2\text{ m}$), matching native Jak 3 values exactly.
- **Suppression of Trick FX on Hit:** In `target-board.gc` (`'touched` event handler), guard `(process-spawn part-tracker :init part-tracker-init group-board-spin-attack ...)` with `(if (!= (-> self control danger-mode) 'board-zap) ...)` to prevent native spin-trick flashes during zap attacks.

---

---

### 12. Generic Enemy Death Effect (Purple Skeleton-Dissolve Particles)

> **Origin / Provenance:** `jak2/features/yakow_killable`

### Context & Core Concepts
When many Jak II enemies (civilians, Crimson Guards, wasps, etc.) die, their model dissolves into purple/violet particles that appear to trace the outline of the mesh as it fades out, accompanied by a "fizz" sound. This is **not** a per-joint/bone particle emitter — it is a generic, reusable engine system built around a `death-info` data type and a handful of static presets, driven through the existing `effect-control` resource-tag dispatcher (`do-effect`).

- **Type:** `death-info` (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc:12-19`) — `vertex-skip`, `timer`, `overlap`, `effect` (a `sparticle-launcher` id), `sound` (a sound-bank name symbol).
- **Presets:** `death-default` (id `73`, purple, generic kill), `death-seed` (id `72`, orange/yellow, used for life-seed death scenes), `death-warp-in` / `death-warp-out` (id `74`, blue-purple, warp-gate teleport — not a kill).
- These are plain global `(define ...)` symbols, so `(-> 'death-default value)` **is already the `death-info` struct** — no per-actor resource tag needs to be declared to use it.

### Technical Implementation
1. **Trigger:** Call `(do-effect (-> self skel effect) 'death-default 0.0 -1)` from any `process-drawable`'s death code. `self skel effect` is an `effect-control` instance automatically created for every skeleton-having process-drawable inside `initialize-skeleton` (`goal_src/jak2/engine/process-drawable/process-drawable.gc:777`) — so this works for **any** enemy/NPC without extra setup, as long as `initialize-skeleton` was called (true for all `nav-enemy`/`enemy` subclasses).
2. **Dispatch:** `do-effect` (`effect-control.gc:272-585`) resolves `arg0`'s symbol value; when it is a `death-info`, it copies `vertex-skip`/`timer`/`overlap`/`effect` onto the process's `draw-control` (`death-vertex-skip`, `death-timer`, `death-timer-org`, `death-draw-overlap`, `death-effect` — fields declared in `goal_src/jak2/engine/data/art-h.gc:303-307`), plays the preset's `sound` via `play-effect-sound`, and sends the process a `'death-start` event (`effect-control.gc:531-576`).
3. **Per-frame mesh dissolve:** Every frame, `foreground-generic-merc-death` (`foreground.gc:728-752`) advances a randomized vertex stride (`death-vertex-skip`) through the skinned mesh and can start hiding triangles once the "overlap" threshold passes (visual erosion of the model). The actual vertex walk + world-space transform (via the current skinning matrices, so it inherently follows the animated pose) happens in the native `generic-merc-death` function — C++ port at `game/mips2c/jak2_functions/generic_merc.cpp:2470-2536`.
4. **Particle spawn:** For each sampled vertex, `merc-death-spawn` (`merc-death.gc:149-157`) looks up the launcher id (e.g. `73`) in `*part-id-table*` and calls `sp-launch-particles-death` (`sparticle-launcher.gc:486-489`) on `*sp-particle-system-2d*`. Launcher `73` chains into launcher `76` (`sparticle-motion-blur`), producing the drifting/fading trailing wisp look.
5. **Purple color values** (`merc-death.gc:116-132`, preset `death-default`): `:r 96.0-150.0 :g 32.0-64.0 :b 128.0-128.0 :a 128.0` — high/constant blue, low green, moderate red → violet/magenta.

### Concrete Annotated Code Example
The canonical minimal pattern (from `wasp.gc:1015-1033`, state `die-now`):
```lisp
:code (behavior ()
  (dying self)                                          ;; plays enemy-info's sound-die, spawns skull gems
  (let ((v1-3 (-> self root root-prim)))                 ;; clear collision so corpse stops blocking things
    (set! (-> v1-3 prim-core collide-as) (collide-spec))
    (set! (-> v1-3 prim-core collide-with) (collide-spec))
    )
  (set! (-> self hit-points) 0)
  (do-effect (-> self skel effect) 'death-default 0.0 -1) ;; spawn the purple dissolve + "enemy-fizz" sound
  (suspend-for (seconds 1))                               ;; let the ~1.25s vertex-skip timer play out
  (send-event self 'death-end)
  (cleanup-for-death self)
  )
```
Applied identically to `yakow.gc`'s `die` state (`goal_src/jak2/levels/city/farm/yakow.gc`), replacing a placeholder `group-land-poof-drt` dust-poof `part-tracker-spawn`.

### Known Pitfalls / Edge Cases
- **Don't skip the `suspend-for`:** the particle spawning is driven by `foreground-generic-merc-death`, which only runs while the process is still alive and drawing. Calling `cleanup-for-death` immediately after `do-effect` destroys the process before any particle ever spawns — the entity just vanishes silently. `death-default`'s `timer` is `0x4b` (75 game frames ≈ 1.25s @ 60 fps); `(suspend-for (seconds 1))` (as used by `wasp.gc`) is close enough in practice.
- **Requires a skeleton:** `(-> self skel effect)` is only populated for process-drawables that went through `initialize-skeleton`. A process without a skeleton (e.g. a pure collide-shape actor) has no valid target for `do-effect`.
- **Sound is baked into the preset, not chosen per-call:** `death-default` always plays `"enemy-fizz"`. If an enemy needs its own signature death cry *in addition*, play it separately (e.g. via the base `enemy` method `dying`, which already calls `(play-damage-or-death-sound this 1)` = `enemy-info :sound-die`) — both sounds will layer naturally.
- **Joint argument (`-1`) is not the spawn origin:** the last argument to `do-effect` selects an `'effect-joint` resource tag (defaults to joint 0/root when `-1` and no tag is declared) used only for the accompanying sound's 3D position — it has no effect on where the dissolve particles appear, since those are generated from mesh vertices in world space, not from a single joint.
- **`death-seed` looks similar but is a different effect:** it is orange/yellow and semantically tied to the "life seed" death sequence, not a generic kill.

### Verification Steps
1. `./goalc.exe --game jak2 -c "(mi)"` (or `task repl` → `(mi)`) — must build with `Successfully built all N targets`.
2. `task boot-game`, kill an entity using this effect, and confirm: purple dissolving particles tracing the mesh, a trailing wisp, and an audible "fizz" alongside any enemy-specific death sound.

---

---

# 🇫🇷 Version Française

## Sommaire
- [1. Vocabulaire de Base](#1-vocabulaire-de-base)
- [2. Architecture Mémoire du Runtime](#2-architecture-mémoire-du-runtime)
- [3. Définition des Constantes Mémoire](#3-définition-des-constantes-mémoire)
- [4. Étude de Cas : Extension Mémoire à 512 Mo](#4-étude-de-cas-extension-mémoire-à-512-mo)
- [5. Compiler & Valider un Changement GOAL](#5-compiler-valider-un-changement-goal)
- [6. Lancer le Jeu & Lire les Logs](#6-lancer-le-jeu-lire-les-logs)
- [7. Outils de Diagnostic Mémoire en Jeu](#7-outils-de-diagnostic-mémoire-en-jeu)
- [8. Pièges Connus & Bonnes Pratiques](#8-pièges-connus-bonnes-pratiques)
- [9. Art-Groups Custom & Liaison Dynamique](#9-art-groups-custom-liaison-dynamique)
- [10. Reciblage GLTF & Squelettes `build-actor`](#10-reciblage-gltf-squelettes-build-actor)
- [11. Gestion des États Jetboard & Particules](#11-gestion-des-états-jetboard-particules)
- [12. Effet de Mort Générique des Ennemis (Particules Violettes de Dissolution)](#12-effet-de-mort-générique-des-ennemis-particules-violettes-de-dissolution)

---

### 1. Vocabulaire de Base

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

| Terme | Signification & Rôle |
|---|---|
| **EE** | "Emotion Engine", le processeur principal de la PS2. Le port PC émule sa mémoire en réservant un bloc contigu via `mmap` (voir `game/runtime.cpp`). |
| **GOAL** | Le dialecte Lisp/Scheme propriétaire dans lequel tout le code de Naughty Dog est écrit (`goal_src/**/*.gc`). Compilé par **OpenGOAL**. |
| **`goalc`** | Le compilateur OpenGOAL. S'utilise en REPL interactif (`task repl`) ou en mode batch (`-c "(command)"`). |
| **`gk`** | L'exécutable C++ ("game kernel") qui charge et exécute le code GOAL compilé. |
| **DGO** | "Data Group Object" — archive regroupant du code et des assets GOAL compilés, chargés d'un bloc depuis le disque. |
| **Heap** | Un espace mémoire alloué en bloc, dans lequel GOAL alloue dynamiquement ses propres objets. |
| **`valid?`** | Fonction GOAL dans `gcommon.gc` vérifiant l'alignement et les bornes d'un pointeur avant déréférencement. |

---

### 2. Architecture Mémoire du Runtime

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

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

**Points Clés :**
- `GLOBAL_HEAP_END`, `DEBUG_HEAP_START` et `EE_MAIN_MEM_SIZE` sont partagés entre tous les jeux en C++ (`common/goal_constants.h`, `memory_layout.h`).
- Le **level heap** est alloué par `kmalloc` dans le global heap au chargement d'un niveau. Sa taille maximale est définie en GOAL par `DEBUG_LEVEL_HEAP_MULT` dans `goal_src/<jeu>/engine/level/level.gc`.
- `valid?` (`gcommon.gc`) rejette tout pointeur `>= END_OF_MEMORY`. Il faut aligner cette borne sur 512 Mo (`#x20000000`).

---

### 3. Définition des Constantes Mémoire

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

| Constante | Fichier | Portée |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | **Partagée** (tous les jeux) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_SIZE` | `game/kernel/common/memory_layout.h` | Par namespace de jeu |
| `END_OF_MEMORY` (utilisé par `valid?`) | `goal_src/<jeu>/kernel/gcommon.gc` | **Par jeu** |
| `DEBUG_LEVEL_HEAP_MULT` (multiplicateur level heap) | `goal_src/<jeu>/engine/level/level.gc` | **Par jeu** |

---

### 4. Étude de Cas : Extension Mémoire à 512 Mo

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

- `END_OF_MEMORY` dans `goal_src/jak2/kernel/gcommon.gc` a été passé à `#x20000000` (512 Mo).
- **Le Piège :** `DEBUG_LEVEL_HEAP_MULT = 15.0` (valeur de Jak 3) faisait crasher Jak 2 au boot car Jak 2 charge ~35 Mo de code résident avant le premier niveau (laissant ~279 Mo libres, insuffisant pour les 282 Mo demandés par 15.0).
- **La Valeur Retenue :** `DEBUG_LEVEL_HEAP_MULT = 12.0` alloue ~215 Mo, laissant une marge de sécurité de 60 Mo sous le budget disponible tout en augmentant la taille par **10×** par rapport à l'original (1.1×).

---

### 5. Compiler & Valider un Changement GOAL

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

Compiler l'ensemble du projet en mode batch :
```bash
./goalc.exe --game jak2 -c "(mi)"
```
Ou via le REPL interactif :
```bash
task repl
# Dans le REPL :
(mi)
```

---

### 6. Lancer le Jeu & Lire les Logs

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

Lancer le jeu en mode debug verbeux :
```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Vérification des logs d'exécution :
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<horodatage>.log
```

---

### 7. Outils de Diagnostic Mémoire en Jeu

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

Pour afficher l'overlay mémoire en temps réel (mode `-debug`) :
```lisp
(set! *stats-memory* #t)
```
Affiche la répartition exacte des textures, collisions, animations et l'espace restant sur le level heap pour chaque niveau chargé.

---

### 8. Pièges Connus & Bonnes Pratiques

> **Origin / Provenance :** `jak2/config/memory_increase` | **Dernière modification :** `jak2/features/jak3-jetBoard`

1. **Constantes C++ Partagées :** Modifier `GLOBAL_HEAP_END` impacte simultanément Jak 1, 2, 3 et Jak X.
2. **Différences d'Allocation au Boot :** L'espace global heap disponible varie selon la quantité de code résident chargée au boot par chaque jeu.
3. **Validation Runtime Obligatoire :** Un changement qui compile sans erreur peut crasher à l'exécution ; toujours valider avec `(mi)` -> boot -> vérification des logs.

---

### 9. Art-Groups Custom & Liaison Dynamique

> **Origin / Provenance :** `jak2/features/jak3-jetBoard`

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

---

### 10. Reciblage GLTF & Squelettes `build-actor`

> **Origin / Provenance :** `jak2/features/jak3-jetBoard`

### Les Squelettes dans OpenGOAL vs GLTF
Dans OpenGOAL, les squelettes de personnages (comme `jakb-lod0-jg`) contiennent :
1. **2 joints Matriciels (index 0 et 1) :** `align` (Matrice 0) et `prejoint` (Matrice 1).
2. **61 joints TransformQ (index 2 à 62) :** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

### ⚠️ Le Piège du Double `align` dans `build-actor` (Décalage de +1 Os)
- `convert_joints` (`goalc/build_actor/common/build_actor.cpp`) insérait historiquement un os `"align"` synthétique à l'index 0 et décalait tous les os du GLTF de `+1` (en supposant que les modèles externes n'avaient pas d'align).
- Comme les modèles décompilés (`jakb-lod0.glb`) **possèdent déjà `align` à l'index 0**, cela créait 64 joints au lieu de 63, décalant chaque os TransformQ de `+1` (`main` vers `waist_prog`, `waist_prog` vers `upper_body`, `hips` vers `Lthigh`).
- **Symptôme :** L'animation paraît parfaite dans Blender, mais en jeu le maillage se disloque et s'étire violemment à la lecture de l'animation.
- **Règle :** Toujours détecter si `gjoints[0].name == "align"` et utiliser une indexation directe à 0 (`prefix_count = 0`), produisant `num_joints = 61` identique aux animations natives de `jakb-ag`.

---

### 11. Gestion des États Jetboard & Particules

> **Origin / Provenance :** `jak2/features/jak3-jetBoard`

### ⚠️ Le Piège de la Whitelist `target-board-exit` (Le Bug du Mini-Jetboard)
Dans Jak 2, le jetboard (`board-lod0`) est un processus acteur autonome (`board.gc`) attaché à `node-list data 25` avec deux états visuels distincts :
1. **`use` (`board-open-ja`) :** Ailerons, pointes et spoilers déployés en grand skate/snowboard.
2. **`idle` (`board-close-ja`) :** Rétracté entièrement dans son dôme central (disque compact fixé au dos de Jak).

- La fonction `target-board-exit` (`target-board.gc:882`) possède une **liste blanche codée en dur** des états de jetboard valides.
- Lors de l'ajout d'un nouvel état de jetboard (ex: `target-board-turn-around`), **il DOIT être ajouté à la liste blanche** de `target-board-exit`, `target-board-pre-move` et `target-board-real-post`.
- **Symptôme si omis :** Dès l'entrée dans le nouvel état, le moteur croit que Jak descend du skate, efface `(focus-status board)`, et l'acteur `board` bascule instantanément en `idle` / `board-close-ja` (la planche se rétracte en mini-rondelle sous les pieds de Jak).

### Rotation Autonome & Verrouillage du Pilotage Stick (`turn-lockout-end-time`)
Lors d'un demi-tour piloté par animation, `target-board-real-post` exécute continuellement `read-pad` et appelle `turn-to-vector` (ou `rot->dir-targ!` si stick neutre), écrasant `dir-targ` à chaque frame avec l'orientation du joystick ou le réinitialisant sur l'ancien cap.
- **Correctif :** Définir `(set! (-> self control turn-lockout-end-time) (+ (current-time) (seconds 1.5)))` dans `:enter` (et remettre à 0 dans `:exit`), supprimant toute interférence du joystick pendant le demi-tour.
- **Conservation de vitesse d'entrée :** Calculer la vitesse initiale via `(fmax (-> self control ctrl-xz-vel) (vector-length (vector-flatten! (new-stack-vector0) (-> self control transv) (-> self control dynam gravity-normal))) 40960.0)` pour conserver l'élan même si Jak glissait ou dérivait sans pousser le stick vers l'avant.

### Inversion de Cap, Boost & Maintien de Vélocité à la Sortie
Pour garantir un changement de cap complet (demi-tour à 180°) et gratifier le joueur :
1. `(quaternion-copy! (-> self control quat-for-control) (-> self control dir-targ))` : Inverse le quaternion de contrôle.
2. `(set-quaternion! (-> self control) (-> self control dir-targ))` : Inverse l'orientation du root-transform.
3. `(vector-z-quaternion! (-> self control transv) (-> self control dir-targ))` & `(vector-float*! (-> self control transv) ... f30-1)` : Aligne la vélocité monde dans la nouvelle direction avec boost d'accélération (`(fmax (+ f30-0 20480.0) 114688.0)`).
4. `(set-forward-vel f30-1)` & `(set! (-> self control ctrl-xz-vel) f30-1)` : Transmet la vitesse scalaire vers l'avant.
5. `(sound-play "board-boost")`, `(cpad-set-buzz!)`, et `part-tracker-spawn group-board-land-straight` : Déclenche le son de boost, la vibration manette et les particules de poussière au sol (identiques aux figures réussies).

### Suivi Dynamique de Joint, Ondes Particulaires & Sphères de Collision (`board-zap-track`)
Pour les attaques de zone en déplacement (ex: `board-zap`) :
- **Suivi Dynamique :** Les callbacks de sparticles (`(:func 'board-zap-track)`) doivent interroger `*target*` directement et recopier la translation du joint du skate `(joint-node-index jakb-lod0-jg board)` dans `(-> arg2 x/y/z)`. En parallèle, `part-tracker-spawn` doit recevoir `:callback part-tracker-track-target`. Les particules et le processus tracker accompagnent ainsi la planche en temps réel même à haute vitesse.
- **Ondes Concentriques Multi-Anneaux :** La réplication de `group-board-zap-attack` de Jak 3 (`:num 0.25`, `:length (seconds 0.335)`, `:scalevel-x (meters 0.16666667)`) émet 4 à 5 anneaux concentriques successifs s'étendant jusqu'à $3.0\text{ m}$.
- **Alignement du Rayon de Dégâts :** Configurer la sphère de collision d'attaque dans `target-util.gc` (`sphere<-vector+r!`) à $12288.0$ ($3.0\text{ m}$) avec une sphère racine englobante de $13107.2$ ($3.2\text{ m}$), calquées à l'identique sur les constantes de Jak 3.
- **Suppression de l'Effet de Spin à l'Impact :** Dans `target-board.gc` (gestionnaire d'événement `'touched`), protéger le spawn de `group-board-spin-attack` avec `(if (!= (-> self control danger-mode) 'board-zap) ...)` pour empêcher le déclenchement de l'effet visuel de figure/spin bleu lors des attaques zap.

---

### 12. Effet de Mort Générique des Ennemis (Particules Violettes de Dissolution)

> **Origin / Provenance :** `jak2/features/yakow_killable`

### Contexte & Concepts Clés
Quand de nombreux ennemis de Jak II meurent (civils, Crimson Guards, guêpes, etc.), leur modèle se dissout en particules violettes qui semblent tracer le contour du maillage pendant qu'il disparaît, accompagné d'un son de "fizz". Ce n'est **pas** un émetteur de particules par joint/os — c'est un système moteur générique et réutilisable, construit autour d'un type `death-info` et de quelques presets statiques, déclenché via le dispatcher de resource-tags existant `effect-control` (`do-effect`).

- **Type :** `death-info` (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc:12-19`) — `vertex-skip`, `timer`, `overlap`, `effect` (un id de `sparticle-launcher`), `sound` (un symbole de nom de banque sonore).
- **Presets :** `death-default` (id `73`, violet, mort générique), `death-seed` (id `72`, orange/jaune, utilisé pour les scènes de mort avec "life seed"), `death-warp-in` / `death-warp-out` (id `74`, bleu-violet, téléportation par warp-gate — pas une mort).
- Ce sont de simples symboles globaux `(define ...)`, donc `(-> 'death-default value)` **est déjà la structure `death-info`** — aucun resource-tag par acteur n'est nécessaire pour l'utiliser.

### Implémentation Technique
1. **Déclenchement :** Appeler `(do-effect (-> self skel effect) 'death-default 0.0 -1)` depuis le code de mort de n'importe quel `process-drawable`. `self skel effect` est une instance `effect-control` créée automatiquement pour tout process-drawable possédant un squelette, dans `initialize-skeleton` (`goal_src/jak2/engine/process-drawable/process-drawable.gc:777`) — cela fonctionne donc pour **n'importe quel** ennemi/PNJ sans configuration supplémentaire, tant que `initialize-skeleton` a été appelé (vrai pour toutes les sous-classes `nav-enemy`/`enemy`).
2. **Dispatch :** `do-effect` (`effect-control.gc:272-585`) résout la valeur du symbole `arg0` ; quand c'est un `death-info`, elle copie `vertex-skip`/`timer`/`overlap`/`effect` sur le `draw-control` du process (`death-vertex-skip`, `death-timer`, `death-timer-org`, `death-draw-overlap`, `death-effect` — champs déclarés dans `goal_src/jak2/engine/data/art-h.gc:303-307`), joue le son du preset via `play-effect-sound`, et envoie un événement `'death-start` au process (`effect-control.gc:531-576`).
3. **Dissolution du maillage image par image :** Chaque frame, `foreground-generic-merc-death` (`foreground.gc:728-752`) avance un pas aléatoire (`death-vertex-skip`) sur le maillage skinné et peut commencer à cacher des triangles une fois le seuil "overlap" dépassé (érosion visuelle du modèle). Le parcours réel des vertices + la transformation en espace monde (via les matrices de skinning courantes, donc suit naturellement la pose animée) se fait dans la fonction native `generic-merc-death` — portage C++ dans `game/mips2c/jak2_functions/generic_merc.cpp:2470-2536`.
4. **Spawn des particules :** Pour chaque vertex échantillonné, `merc-death-spawn` (`merc-death.gc:149-157`) recherche l'id du launcher (ex : `73`) dans `*part-id-table*` et appelle `sp-launch-particles-death` (`sparticle-launcher.gc:486-489`) sur `*sp-particle-system-2d*`. Le launcher `73` enchaîne sur le launcher `76` (`sparticle-motion-blur`), produisant l'effet de traînée qui dérive et s'estompe.
5. **Valeurs de couleur violette** (`merc-death.gc:116-132`, preset `death-default`) : `:r 96.0-150.0 :g 32.0-64.0 :b 128.0-128.0 :a 128.0` — bleu élevé/constant, vert faible, rouge modéré → violet/magenta.

### Exemple de Code Annoté
Le pattern minimal canonique (issu de `wasp.gc:1015-1033`, état `die-now`) :
```lisp
:code (behavior ()
  (dying self)                                          ;; joue sound-die de enemy-info, spawn les skull gems
  (let ((v1-3 (-> self root root-prim)))                 ;; efface la collision pour que le cadavre ne bloque plus rien
    (set! (-> v1-3 prim-core collide-as) (collide-spec))
    (set! (-> v1-3 prim-core collide-with) (collide-spec))
    )
  (set! (-> self hit-points) 0)
  (do-effect (-> self skel effect) 'death-default 0.0 -1) ;; spawn la dissolution violette + le son "enemy-fizz"
  (suspend-for (seconds 1))                               ;; laisse le timer vertex-skip (~1.25s) se dérouler
  (send-event self 'death-end)
  (cleanup-for-death self)
  )
```
Appliqué à l'identique dans l'état `die` de `yakow.gc` (`goal_src/jak2/levels/city/farm/yakow.gc`), en remplacement d'un `part-tracker-spawn` placeholder de poussière `group-land-poof-drt`.

### Pièges / Cas Particuliers
- **Ne pas sauter le `suspend-for` :** le spawn des particules est piloté par `foreground-generic-merc-death`, qui ne s'exécute que tant que le process est vivant et affiché. Appeler `cleanup-for-death` immédiatement après `do-effect` détruit le process avant qu'aucune particule n'ait pu apparaître — l'entité disparaît silencieusement. Le `timer` de `death-default` est `0x4b` (75 frames jeu ≈ 1.25s @ 60 fps) ; `(suspend-for (seconds 1))` (comme dans `wasp.gc`) est suffisant en pratique.
- **Nécessite un squelette :** `(-> self skel effect)` n'est peuplé que pour les process-drawables passés par `initialize-skeleton`. Un process sans squelette (ex : un simple acteur collide-shape) n'a pas de cible valide pour `do-effect`.
- **Le son est intégré au preset, pas choisi par appel :** `death-default` joue toujours `"enemy-fizz"`. Si un ennemi a besoin de son propre cri de mort *en plus*, le jouer séparément (ex : via la méthode de base `enemy` `dying`, qui appelle déjà `(play-damage-or-death-sound this 1)` = `enemy-info :sound-die`) — les deux sons se superposeront naturellement.
- **L'argument joint (`-1`) n'est pas l'origine du spawn :** le dernier argument de `do-effect` sélectionne un resource-tag `'effect-joint` (par défaut joint 0/racine si `-1` et aucun tag déclaré) utilisé uniquement pour la position 3D du son accompagnant — il n'a aucun effet sur l'endroit où apparaissent les particules de dissolution, car elles sont générées à partir des vertices du maillage en espace monde, pas d'un joint unique.
- **`death-seed` ressemble mais est un effet différent :** il est orange/jaune et lié sémantiquement à la séquence de mort "life seed", pas à une mort générique.

### Procédure de Validation
1. `./goalc.exe --game jak2 -c "(mi)"` (ou `task repl` → `(mi)`) — doit compiler avec `Successfully built all N targets`.
2. `task boot-game`, tuer une entité utilisant cet effet, et vérifier : particules violettes qui se dissolvent en traçant le maillage, traînée qui s'estompe, et un "fizz" audible en plus du son de mort spécifique éventuel de l'ennemi.

---
