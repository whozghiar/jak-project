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
- [13. Custom Animation & Sound Import Pipeline (End-to-End)](#13-custom-animation-sound-import-pipeline-end-to-end)
- [14. 14_dark_jak_scaling_and_super_attacks.md](#14-14-dark-jak-scaling-and-super-attacksmd)

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

### 13. Custom Animation & Sound Import Pipeline (End-to-End)

> **Origin / Provenance:** `jak2/features/jak3-jetBoard` | **Last Updated:** `jak2/features/jak3-jetBoard`

This is the generalized, end-to-end procedure for two recurring modding needs, distilled from
porting the Jak 3 jetboard's animations and sounds into Jak 2 (`jak2/features/jak3-jetBoard`):

- **Part A** — importing a custom animation onto an existing in-game skeleton, including cross-game
  retargeting (e.g. Jak 3 source animation → Jak 2 skeleton).
- **Part B** — adding a new custom sound that plays reliably at runtime, including one that needs
  continuous per-frame updates (looping / ramping volume).
- **Part C** — the rebuild/iteration mechanisms that make both of the above fast to debug, instead
  of paying for a full engine rebuild + game boot on every attempt.

This complements two existing, narrower tips in this folder: [10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md)
(the `align`/`prejoint` off-by-one pitfall) and [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md)
(the `link-art!` hook). Read this file first for the full pipeline, then those two for the specific
pitfalls they document.

---

## Part A — Importing a Custom Animation

### A1. Gather your source and base assets
- **Base skeleton+mesh**: use the project's own decompiled, already-correct GLB for the target
  character, e.g. `decompiler_out/jak2/levels/common/jakb-lod0.glb`. This guarantees the output
  skin/joint order exactly matches the native `jakb-ag`'s expectations — never hand-build or
  hand-edit a GLTF/GLB from scratch, that was the source of an earlier, much harder-to-diagnose
  boot crash in this same mod.
- **Source animation data**: if porting from another game in this repo (Jak 1/2/3 share the same
  decompiler pipeline), check whether the target character's own decompiled GLB **already contains**
  the animation you want — e.g. `decompiler_out/jak3/levels/common/jakb-lod0.glb` had all ~280+
  native Jak 3 animations already baked in, fully decompressed, with no extra `.go`-decompression
  step required. Always check this first; it saves an entire decompiler pass.
- Confirm the animation's compiled name via the target game's `art-elts.gc` (e.g.
  `goal_src/jak3/engine/data/art-elts.gc`) so you retarget the exact clip you think you are.

### A2. Use (or extend) the retargeting tool
A dedicated, standalone CLI tool — `goalc/retarget_anim/` — exists for this. It:
1. Loads the base GLB (`-b/--base`) as the skeleton + mesh to keep unchanged.
2. Loads the source GLB (`-s/--source`) and pulls out one or more named animations
   (`-a/--anim`, repeatable).
3. Maps joints by **name** between the two skeletons.
4. Writes a new, structurally valid `.glb` (`-o/--output`) via the project's existing `tiny_gltf`
   dependency — never hand-patch GLTF JSON/binary directly.

Flags worth knowing: `--root-joints` (default `align main`) and `--neutral-scale-joints` (default
`board`) — see A3 for why these exist. `--force-180-yaw-anim` exists but should stay unused unless
the gameplay code does **not** already drive the rotation itself (double-check first — forcing it
when gameplay code also rotates will double-rotate the result).

### A3. The retargeting rules (why they matter)
Ground-truthed against real native data before trusting them — do not skip this kind of check when
adapting this tool to a new character/animation pair:
- **Root joints (`align`, `main`)**: copy full translation + rotation (+ scale if present) from the
  source. This is real root motion and must carry over exactly.
- **Every other joint**: copy **rotation only**, retargeted as a delta from the *source's own bind
  pose* (`delta = source_animated * inverse(source_bind)`, then `result = delta * target_bind`) —
  not a raw copy of the source's absolute rotation. Keep the *target's own* bind-pose translation and
  scale. Reason: translation encodes bone length, which differs between skeletons (even
  structurally similar ones across games); copying it directly stretches/dislocates the mesh. The
  delta-from-bind-pose formula degrades to a raw copy when both skeletons happen to share identical
  bind rotations for a joint — verify this by direct comparison rather than assuming either way.
- **Explicitly neutral-scale joints** (e.g. `board`, a joint that must never visually stretch):
  force `(1,1,1)` scale at every keyframe rather than trusting either skeleton's source data.

### A4. Verify the output structurally — before compiling anything
Write a small, throwaway Python script that parses the GLB directly (12-byte header + JSON chunk +
BIN chunk — parseable with just the standard-library `json` and `struct` modules; **no `numpy` is
installed in this environment**, so do not depend on it). Check, per regenerated file:
- Skin joint count and names match the native base exactly.
- Both requested animations are present with the expected channels.
- Root joints have translation channels; forced-neutral joints have constant `(1,1,1)` scale across
  all keyframes.
- If in doubt about visual correctness, implement a minimal forward-kinematics (FK) check in the
  same script (compose per-joint local TRS down the parent chain into world matrices) rather than
  guessing — this is cheap in Python and catches joint-order mistakes immediately, without ever
  touching the compiler or the game.

This step exists specifically to avoid the "compile → boot → crash → guess → repeat" loop; nearly
every real bug in this mod's animation pipeline was actually visible in the raw GLB data once
someone looked with the right check.

### A5. Register the GLB with `build-actor`
In the target game's project file (`goal_src/jak2/game.gp`), a `build-actor` declaration with
`:master-art-group` and `:master-ag-map` bakes target slot indices into the compiled art-group at
compile time. If you're replacing an existing custom import's `.glb` file in place (same declared
name/slots), **no `.gp` changes are needed at all** — only the binary GLB input changes.

Also be aware of `goalc/build_actor/common/build_actor.cpp`'s `kGltfToGameJointOffset` constant
(currently `1`): in-game joint index = GLTF skin joint index + 1, **except** when the GLB's joint 0
is already named `align` (true for our decompiled bases), in which case the tool uses direct
0-indexed mapping instead — see [10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md)
for the full pitfall this caused historically. When identifying "what is joint N", always resolve it
via this rule (or via the `joint-node-index`/`joint-node` compile-time macros in `art-h.gc`, which
resolve by **name** against `*jg-info*`) — never hand-count a raw GLB joint array. Hand-counting
produced at least one confidently-wrong finding in this mod before the offset rule was applied
correctly.

### A6. Link the animations at runtime
`build-actor` output with a skeleton has a `joint-geo` in slot 0, so the engine's own `needs-link?`
check (`joint.gc`) — which only returns true if slot 0 is an `art-joint-anim` — will never trigger
automatically for it. You must special-case your custom art-group's name where `link-art!` is
called. The correct, and only safe, hook is `art-group::relocate` in
`goal_src/jak2/engine/anim/joint.gc` — **never** call `link-art!` from gameplay code (e.g. an
actor's `-init` function): level art-group array state is not guaranteed consistent there, and this
risks a memory crash. See [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) for
the exact hook code.

### A7. Compile and test
Once the GLB structurally checks out, pulling it into the running game is a **pure GOAL-side**
change (no C++ was touched) — `(mi)` is sufficient, see Part C for why a full engine rebuild is not
needed here.

---

## Part B — Adding a Custom Sound

### B1. Place the raw sound and add it to the bank
New sounds are appended into a game `.SBK` bank via `goalc/build_sbk/build_sbk.cpp`'s
`append_sbk_from_dir` (or the equivalent bank-build step for your target bank). Verify the target
bank's on-disk layout preconditions the tool expects (e.g. terminator format) hold, ideally by
parsing the real `.SBK` by hand in Python the same way you'd verify a GLB — the append logic is easy
to get subtly wrong against a real, non-trivial binary layout.

### B2. Make sure the bank can actually be *allocated* at runtime
This is the step that is easy to skip and hardest to diagnose from GOAL code alone, because the
failure surfaces as a generic "out of slots" from C++ code far from where the sound was triggered.
`game/overlord/common/sbank.cpp` (shared by Jak 1 and Jak 2 — **not** Jak 3, which has its own,
structurally different `game/overlord/jak3/sbank.cpp`) has a fixed `N_BANKS` array: a handful of
**dedicated, name-reserved slots** (`common`, `gun`, `board` for Jak 2) plus a small **rotating pool**
of level banks. `AllocateBankName` must explicitly special-case any dedicated bank name you rely on
— a name that isn't special-cased falls through to the rotating-pool loop, which is normally always
full during real gameplay (a level keeps its own rotation occupied), so allocation silently fails
with "out of slots" even though a perfectly good dedicated slot sits unused. If you add sounds to an
existing dedicated bank (like `board`), double-check `AllocateBankName` already special-cases that
exact name — do not assume it does just because the slot exists in `InitBanks`.

### B3. Initialize a persistent sound-id for anything that needs per-frame updates
`sound-play-by-name` (`goal_src/jak2/engine/sound/gsound.gc`) does **not** generate a sound id — it
always returns whatever id (`arg1`) it was given. For a one-shot sound this doesn't matter. For a
sound that needs to be *updated* every frame while it plays (a ramping-volume charge sound, an
engine loop, etc.), the caller must pre-initialize a real, unique id via `(new-sound-id)` **once**,
typically in the owning object's `-init` function, so the audio engine can recognize repeated calls
as updates to the *same* live instance rather than unrelated new requests. If you add a new
per-frame sound trigger, grep the equivalent native code (if it exists in another game version) for
where it initializes its own id — this exact omission (forgetting the `new-sound-id` call when
porting a new sound-id struct field) silently broke a charge-up sound in this mod while every other
sound worked fine, because the failure looks identical to "the sound never triggers" rather than
"the sound triggers but is never recognized as continuing."

### B4. Trigger the sound from GOAL
Standard `(sound-play-by-name (static-sound-name "your-sound") id volume pitch bend (sound-group)
position)` call, same as any native sound trigger. `static-sound-name` packs the literal string at
compile time — nothing dynamic to worry about there.

---

## Part C — Fast, Targeted Rebuild Mechanisms

These are what actually kept iteration fast on this mod — use them in this order of preference:

### C1. Build only the standalone tool, not the whole engine
`retarget_anim` (and similarly `build_sbk`, `build_actor`) are standalone CLI targets, not part of
the game runtime. Build just the one target you're iterating on:
```bash
cmake --build out/build/Release --target retarget_anim --config Release
```
This compiles in seconds, versus a full `gk`/engine rebuild. Only fall back to a full build when
you've actually changed game-runtime C++ (e.g. `game/overlord/**`).

### C2. Iterate offline, with no game boot at all
Run the built tool's `.exe` directly against your GLB inputs to regenerate output — this whole loop
(edit tool code → rebuild tool target → rerun → re-verify structurally per A4) never needs to touch
GOAL or boot the game. Only move to a game boot once the structural verification script is clean.

### C3. Structural verification before compiling GOAL or booting
As in A4: a throwaway Python script against the raw GLB/SBK bytes catches the large majority of
mistakes (wrong joint mapping, wrong scale, malformed bank layout) instantly and for free. Treat a
compile-and-boot cycle as the *expensive* last check, not the first one.

### C4. Know whether you need `(mi)` or a full C++ rebuild
- Changed only `.gc`/GOAL code, or swapped in a new `.glb`/asset with no `.gp`/C++ changes? `(mi)`
  (incremental compile in the REPL, or `./goalc.exe --game jak2 -c "(mi)"` in batch mode) is
  sufficient — see [05_compilation_validation_workflow.md](05_compilation_validation_workflow.md).
- Changed C++ under `game/` (e.g. a `sbank.cpp`/`srpc.cpp` fix)? You need an actual engine rebuild
  (`task build-release` / `task build-debug`) before `(mi)` or a boot will reflect the change —
  `(mi)` alone will not pick up C++ changes.
- Don't guess which one applies — check `git status`/`git diff` for what you actually touched before
  proposing a rebuild command to the user, so you propose the cheapest one that's actually correct.

### C5. Scoped debug logging + targeted log grepping
When a bug can only be diagnosed from real runtime behavior (as both the turn-around and the sound
bugs in this mod ultimately were — static analysis alone was not enough), add temporary,
distinctively-prefixed log lines (e.g. `[board-sound-debug]`) at the specific decision points you
suspect, guarded by a one-time-print flag if the code runs every frame (to avoid drowning the log in
spam). Then grep the resulting `log/jak2.<timestamp>.log` for that exact prefix instead of reading
the whole log. Remove or gate these prefixes once the bug is confirmed fixed.

---

---

### 14. 14_dark_jak_scaling_and_super_attacks.md

> **Origin / Provenance:** `jak2/features/dark_jak_enhanced` | **Last Updated:** `jak2/features/dark_jak_enhanced`

In Jak 2, Dark Jak's physical transformation is governed by an engine interpolation variable `darkjak-giant-interp` (ranging from `1.0` to `2.0` in retail code) and the `darkjak-stage` bitfield enum in [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

Because OpenGOAL couples character scaling across physics velocities (`ctrl-xz-vel`), animation bone scales, collision spheres, and damage penetration, understanding how to extend this pipeline unlocks seamless multi-tier transformations, acrobatic restoration, manual cancel controls, and robust super abilities.

---

## 2. Multi-Tier Progressive Scaling Architecture

### A. Stage Enumeration & Unlocked State Transitions
The `darkjak-stage` bitfield enum can be safely extended with new evolutionary tiers (such as `mega-giant`):

```lisp
(defenum darkjak-stage
  :bitfield #t
  :type uint32
  (force-on)
  (active)
  (bomb0)
  (bomb1)
  (invinc)
  (giant)
  (no-anim)
  (disable-force-on)
  (mega-giant)
  )
```

In `target-darkjak.gc`, `want-to-darkjak?` allows progressive evolution across all tiers:
```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

### B. Headroom Collision Queries & Progressive Camera Offsets
When expanding to a colossal scale (e.g. `3.5x`), collision probe spheres and camera spring settings scale proportionally:

```lisp
(let* ((already-giant? (logtest? (-> self darkjak stage) (darkjak-stage giant)))
       (target-scale (if already-giant? 3.5 2.0))
       (start-scale (if already-giant? (-> self darkjak-giant-interp) 1.0))
       )
  (+! (-> s5-1 0 y) (if already-giant? 22000.0 12697.6))
  (set! (-> s5-1 0 r) (if already-giant? 18000.0 11878.4))
  )
```

---

## 3. Manual Cancel Control & Eco Consumption

### A. Universal Manual Revert (`R2`)
In `target-darkjak-post`, checking `(cpad-pressed? (-> self control cpad number) r2)` allows Jak to exit Dark Jak smoothly at any moment:

```lisp
(if (and (cpad-pressed? (-> self control cpad number) r2)
         (not (focus-test? self dead dangerous hit grabbed))
         (not (and (-> self next-state) (= (-> self next-state name) 'target-darkjak-get-off)))
         (not (logtest? (-> self darkjak stage) (darkjak-stage force-on)))
         )
    (go target-darkjak-get-off)
    )
```

### B. Full Eco Consumption on Exit
When Dark Jak ends (via `R2`, timeout, Dark Bomb, Dark Blast, or death), all remaining dark eco is consumed:
```lisp
(set! (-> self game eco-pill-dark) 0.0)
```

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
- [13. Pipeline Complet d'Import d'Animations et de Sons Custom](#13-pipeline-complet-dimport-danimations-et-de-sons-custom)
- [14. 14_dark_jak_scaling_and_super_attacks.md](#14-14-dark-jak-scaling-and-super-attacksmd)

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

### 13. Pipeline Complet d'Import d'Animations et de Sons Custom

> **Origin / Provenance :** `jak2/features/jak3-jetBoard` | **Dernière modification :** `jak2/features/jak3-jetBoard`

Voici la procédure généralisée et complète pour deux besoins de modding récurrents, tirée de
l'import des animations et des sons du jetboard de Jak 3 vers Jak 2
(`jak2/features/jak3-jetBoard`) :

- **Partie A** — importer une animation custom sur un squelette existant en jeu, y compris le
  reciblage inter-jeux (ex : animation source Jak 3 → squelette Jak 2).
- **Partie B** — ajouter un nouveau son custom qui joue de façon fiable en jeu, y compris un son
  nécessitant des mises à jour continues par frame (boucle / volume progressif).
- **Partie C** — les mécanismes de rebuild/itération qui rendent le débogage des deux points
  ci-dessus rapide, plutôt que de payer un rebuild complet du moteur + boot du jeu à chaque essai.

Ce document complète deux fiches existantes plus ciblées dans ce dossier :
[10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md) (le piège du décalage
`align`/`prejoint`) et [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) (le hook
`link-art!`). Lisez d'abord ce fichier pour le pipeline complet, puis ces deux fiches pour les pièges
spécifiques qu'elles documentent.

---

## Partie A — Importer une Animation Custom

### A1. Rassembler les assets source et de base
- **Squelette+mesh de base** : utilisez le GLB déjà décompilé et correct du projet pour le
  personnage cible, ex : `decompiler_out/jak2/levels/common/jakb-lod0.glb`. Cela garantit que
  l'ordre du skin/des joints en sortie correspond exactement à ce qu'attend le `jakb-ag` natif — ne
  jamais construire ou éditer un GLTF/GLB à la main, c'est la source d'un crash au boot bien plus
  difficile à diagnostiquer plus tôt dans ce même mod.
- **Données d'animation source** : si vous portez depuis un autre jeu de ce dépôt (Jak 1/2/3
  partagent le même pipeline de décompilation), vérifiez d'abord si le GLB déjà décompilé du
  personnage cible **contient déjà** l'animation voulue — ex :
  `decompiler_out/jak3/levels/common/jakb-lod0.glb` contenait déjà les ~280+ animations natives de
  Jak 3, entièrement décompressées, sans étape supplémentaire de décompression du `.go`. Vérifiez
  toujours cela en premier ; cela évite une passe complète de décompilation.
- Confirmez le nom compilé de l'animation via `art-elts.gc` du jeu cible (ex :
  `goal_src/jak3/engine/data/art-elts.gc`) pour être sûr de recibler exactement le clip visé.

### A2. Utiliser (ou étendre) l'outil de reciblage
Un outil CLI autonome dédié — `goalc/retarget_anim/` — existe pour cela. Il :
1. Charge le GLB de base (`-b/--base`) comme squelette + mesh à conserver inchangé.
2. Charge le GLB source (`-s/--source`) et en extrait une ou plusieurs animations nommées
   (`-a/--anim`, répétable).
3. Mappe les joints par **nom** entre les deux squelettes.
4. Écrit un nouveau `.glb` structurellement valide (`-o/--output`) via `tiny_gltf`, déjà une
   dépendance du projet — ne jamais patcher un GLTF JSON/binaire à la main.

Options utiles : `--root-joints` (défaut `align main`) et `--neutral-scale-joints` (défaut `board`)
— voir A3 pour leur raison d'être. `--force-180-yaw-anim` existe mais doit rester inutilisée sauf si
le code de gameplay ne pilote **pas** déjà la rotation lui-même (vérifiez d'abord — la forcer alors
que le code de gameplay tourne aussi le résultat provoque une double rotation).

### A3. Les règles de reciblage (et pourquoi elles comptent)
Vérifiées contre de vraies données natives avant d'être appliquées en confiance — ne sautez jamais ce
type de vérification en adaptant l'outil à une nouvelle paire personnage/animation :
- **Joints racines (`align`, `main`)** : copier translation + rotation complètes (+ scale si
  présent) depuis la source. C'est le mouvement racine réel, il doit être conservé tel quel.
- **Tous les autres joints** : copier **uniquement la rotation**, reciblée comme un delta par
  rapport à la *bind pose propre à la source* (`delta = animée_source * inverse(bind_source)`, puis
  `résultat = delta * bind_cible`) — pas une copie brute de la rotation absolue de la source.
  Conserver la translation et le scale de bind pose **propres à la cible**. Raison : la translation
  encode la longueur des os, qui diffère entre squelettes (même structurellement proches d'un jeu à
  l'autre) ; la copier directement étire/disloque le maillage. La formule delta-depuis-bind-pose
  dégénère en copie brute quand les deux squelettes partagent la même rotation de bind pose pour un
  joint donné — vérifiez-le par comparaison directe plutôt que de le supposer dans un sens ou
  l'autre.
- **Joints explicitement à scale neutre** (ex : `board`, un joint qui ne doit jamais s'étirer
  visuellement) : forcer un scale `(1,1,1)` à chaque keyframe plutôt que de faire confiance aux
  données source de l'un ou l'autre squelette.

### A4. Vérifier structurellement la sortie — avant toute compilation
Écrivez un petit script Python jetable qui parse le GLB directement (en-tête 12 octets + chunk JSON
+ chunk BIN — analysable avec uniquement les modules standards `json` et `struct` ; **`numpy` n'est
pas installé dans cet environnement**, n'en dépendez donc pas). Vérifiez, pour chaque fichier
régénéré :
- Le nombre et les noms des joints du skin correspondent exactement à la base native.
- Les deux animations demandées sont présentes avec les canaux attendus.
- Les joints racines ont des canaux de translation ; les joints à scale forcé ont un scale constant
  `(1,1,1)` sur toutes les keyframes.
- En cas de doute sur la correction visuelle, implémentez une vérification minimale de cinématique
  directe (FK) dans le même script (composer les TRS locaux de chaque joint le long de la chaîne
  parentale en matrices monde) plutôt que de deviner — c'est peu coûteux en Python et cela détecte
  immédiatement les erreurs d'ordre des joints, sans jamais toucher au compilateur ni au jeu.

Cette étape existe spécifiquement pour éviter la boucle « compiler → booter → crash → deviner →
recommencer » ; presque tous les vrais bugs du pipeline d'animation de ce mod étaient en réalité
visibles dans les données GLB brutes une fois qu'on regardait avec la bonne vérification.

### A5. Enregistrer le GLB auprès de `build-actor`
Dans le fichier projet du jeu cible (`goal_src/jak2/game.gp`), une déclaration `build-actor` avec
`:master-art-group` et `:master-ag-map` inscrit les index de slots cibles dans l'art-group compilé à
la compilation. Si vous remplacez sur place le `.glb` d'un import custom déjà existant (même nom/
slots déclarés), **aucune modification du `.gp` n'est nécessaire** — seul le binaire GLB en entrée
change.

Soyez aussi attentif à la constante `kGltfToGameJointOffset` (actuellement `1`) de
`goalc/build_actor/common/build_actor.cpp` : index de joint en jeu = index de joint du skin GLTF + 1,
**sauf** si le joint 0 du GLB s'appelle déjà `align` (vrai pour nos bases décompilées), auquel cas
l'outil utilise un mapping direct indexé à 0 — voir
[10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md) pour le piège historique
complet que cela a causé. Pour identifier « quel est le joint N », toujours résoudre via cette règle
(ou via les macros de compilation `joint-node-index`/`joint-node` de `art-h.gc`, qui résolvent par
**nom** via `*jg-info*`) — ne jamais compter à la main les joints d'un GLB brut. Compter à la main a
produit au moins une conclusion fausse avec assurance dans ce mod avant l'application correcte de la
règle de décalage.

### A6. Lier les animations à l'exécution
Une sortie `build-actor` avec squelette a un `joint-geo` au slot 0, donc la vérification native
`needs-link?` du moteur (`joint.gc`) — qui ne renvoie vrai que si le slot 0 est un `art-joint-anim` —
ne se déclenchera jamais automatiquement pour elle. Il faut ajouter un cas spécial pour le nom de
votre art-group custom là où `link-art!` est appelé. Le seul emplacement correct et sûr est
`art-group::relocate` dans `goal_src/jak2/engine/anim/joint.gc` — **ne jamais** appeler `link-art!`
depuis du code de gameplay (ex : la fonction `-init` d'un acteur) : l'état des tableaux d'art-groups
du niveau n'y est pas garanti cohérent, ce qui risque un crash mémoire. Voir
[09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) pour le code exact du hook.

### A7. Compiler et tester
Une fois le GLB validé structurellement, l'intégrer au jeu en cours d'exécution est un changement
**purement côté GOAL** (aucun C++ n'a été touché) — `(mi)` suffit, voir la Partie C pour la raison
pour laquelle un rebuild complet du moteur n'est pas nécessaire ici.

---

## Partie B — Ajouter un Son Custom

### B1. Placer le son brut et l'ajouter à la banque
Les nouveaux sons sont ajoutés à une banque `.SBK` du jeu via `append_sbk_from_dir` de
`goalc/build_sbk/build_sbk.cpp` (ou l'étape équivalente pour votre banque cible). Vérifiez que les
préconditions de mise en page sur disque attendues par l'outil pour la banque cible tiennent (ex :
format du terminateur), idéalement en parsant la vraie `.SBK` à la main en Python, de la même façon
que vous vérifieriez un GLB — la logique d'ajout est facile à casser subtilement contre une mise en
page binaire réelle et non triviale.

### B2. S'assurer que la banque peut réellement être *allouée* à l'exécution
C'est l'étape la plus facile à oublier et la plus difficile à diagnostiquer depuis le seul code
GOAL, car l'échec se manifeste comme un « out of slots » générique venant d'un code C++ éloigné du
point de déclenchement du son. `game/overlord/common/sbank.cpp` (partagé par Jak 1 et Jak 2 — **pas**
Jak 3, qui a son propre `game/overlord/jak3/sbank.cpp` structurellement différent) a un tableau
`N_BANKS` fixe : quelques **slots dédiés réservés par nom** (`common`, `gun`, `board` pour Jak 2) plus
un petit **pool tournant** de banques de niveau. `AllocateBankName` doit explicitement traiter comme
cas spécial tout nom de banque dédiée que vous utilisez — un nom non traité comme cas spécial tombe
dans la boucle du pool tournant, normalement toujours pleine en jeu réel (un niveau occupe sa propre
rotation), donc l'allocation échoue silencieusement avec « out of slots » alors qu'un slot dédié
parfaitement valide reste inutilisé. Si vous ajoutez des sons à une banque dédiée existante (comme
`board`), vérifiez que `AllocateBankName` traite déjà ce nom exact comme cas spécial — ne le
supposez pas simplement parce que le slot existe dans `InitBanks`.

### B3. Initialiser un id de son persistant pour tout ce qui nécessite des mises à jour par frame
`sound-play-by-name` (`goal_src/jak2/engine/sound/gsound.gc`) ne génère **pas** d'id de son — il
renvoie toujours l'id (`arg1`) qu'on lui a donné. Pour un son ponctuel, cela n'a pas d'importance.
Pour un son qui doit être *mis à jour* à chaque frame pendant sa lecture (un son de charge à volume
progressif, une boucle moteur, etc.), l'appelant doit pré-initialiser un vrai id unique via
`(new-sound-id)` **une seule fois**, typiquement dans la fonction `-init` de l'objet propriétaire,
afin que le moteur audio puisse reconnaître les appels répétés comme des mises à jour de la *même*
instance vivante plutôt que des requêtes nouvelles et sans rapport. Si vous ajoutez un nouveau
déclenchement de son par frame, cherchez dans le code natif équivalent (s'il existe dans une autre
version du jeu) où il initialise son propre id — cet oubli précis (ne pas appeler `new-sound-id` en
portant un nouveau champ d'id de son) a silencieusement cassé un son de charge dans ce mod alors que
tous les autres sons fonctionnaient, car le symptôme est identique à « le son ne se déclenche
jamais » plutôt qu'à « le son se déclenche mais n'est jamais reconnu comme continu ».

### B4. Déclencher le son depuis GOAL
Appel standard `(sound-play-by-name (static-sound-name "votre-son") id volume pitch bend
(sound-group) position)`, identique à tout déclenchement de son natif. `static-sound-name` empaquette
la chaîne littérale à la compilation — rien de dynamique à surveiller ici.

---

## Partie C — Mécanismes de Rebuild Ciblé et Rapide

Voici ce qui a réellement permis de garder une itération rapide sur ce mod — à utiliser dans cet
ordre de préférence :

### C1. Ne compiler que l'outil autonome, pas tout le moteur
`retarget_anim` (et de même `build_sbk`, `build_actor`) sont des cibles CLI autonomes, pas partie du
runtime du jeu. Ne compilez que la cible sur laquelle vous itérez :
```bash
cmake --build out/build/Release --target retarget_anim --config Release
```
Cela compile en quelques secondes, contre un rebuild complet de `gk`/du moteur. Ne revenez à un
build complet que si vous avez réellement modifié du C++ du runtime du jeu (ex :
`game/overlord/**`).

### C2. Itérer hors-ligne, sans jamais booter le jeu
Lancez directement l'`.exe` de l'outil compilé contre vos GLB en entrée pour régénérer la sortie —
toute cette boucle (modifier le code de l'outil → recompiler la cible → relancer → revérifier
structurellement selon A4) n'a jamais besoin de toucher GOAL ni de booter le jeu. Ne passez à un boot
du jeu qu'une fois le script de vérification structurelle propre.

### C3. Vérification structurelle avant de compiler GOAL ou de booter
Comme en A4 : un script Python jetable contre les octets bruts du GLB/SBK détecte instantanément et
gratuitement la grande majorité des erreurs (mauvais mapping de joint, mauvais scale, mise en page de
banque malformée). Traitez un cycle compile-et-boot comme la vérification *coûteuse* de dernier
recours, pas la première.

### C4. Savoir si `(mi)` suffit ou s'il faut un rebuild C++ complet
- Seul du `.gc`/code GOAL a changé, ou un nouveau `.glb`/asset a été substitué sans changement de
  `.gp`/C++ ? `(mi)` (compilation incrémentale dans le REPL, ou
  `./goalc.exe --game jak2 -c "(mi)"` en mode batch) suffit — voir
  [05_compilation_validation_workflow.md](05_compilation_validation_workflow.md).
- Du C++ sous `game/` a changé (ex : un correctif dans `sbank.cpp`/`srpc.cpp`) ? Un vrai rebuild du
  moteur est nécessaire (`task build-release` / `task build-debug`) avant que `(mi)` ou un boot ne
  reflète le changement — `(mi)` seul ne prendra jamais en compte un changement C++.
- Ne devinez pas lequel s'applique — vérifiez `git status`/`git diff` pour voir ce que vous avez
  réellement modifié avant de proposer une commande de rebuild à l'utilisateur, afin de proposer la
  moins coûteuse qui soit effectivement correcte.

### C5. Logs de debug ciblés + recherche ciblée dans les logs
Quand un bug ne peut être diagnostiqué qu'à partir du comportement réel à l'exécution (comme ce fut
finalement le cas pour le bug du demi-tour et celui du son dans ce mod — l'analyse statique seule ne
suffisait pas), ajoutez des lignes de log temporaires avec un préfixe distinctif (ex :
`[board-sound-debug]`) aux points de décision précis que vous suspectez, protégées par un indicateur
d'affichage unique si le code s'exécute à chaque frame (pour éviter de noyer le log). Cherchez
ensuite ce préfixe exact dans le fichier `log/jak2.<timestamp>.log` généré plutôt que de lire tout le
log. Retirez ou conditionnez ces préfixes une fois le bug confirmé corrigé.

---

### 14. 14_dark_jak_scaling_and_super_attacks.md

> **Origin / Provenance :** `jak2/features/dark_jak_enhanced` | **Dernière modification :** `jak2/features/dark_jak_enhanced`

Dans Jak 2, la métamorphose de Dark Jak est régie par `darkjak-giant-interp` (`1.0` à `2.0` dans le code de base) et l'énumération bitfield `darkjak-stage` dans [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc).

La maîtrise de cette chaîne permet d'implémenter des évolutions multi-stades, l'annulation manuelle avec `R2`, et des super-attaques fiabilisées.

---

## 2. Architecture de Mise à l'Échelle Multi-Stades

### A. Évolution Débloquée
```lisp
(and (focus-test? self dark)
     (nonzero? (-> self darkjak))
     (not (logtest? (-> self darkjak stage) (darkjak-stage mega-giant)))
     )
```

---

## 3. Annulation Manuelle & Consommation d'Éco

### A. Annulation Manuelle (`R2`)
Détection dans `target-darkjak-post` permettant de revenir à l'état normal à tout moment via `R2`.

### B. Consommation Complète de l'Éco
Dès que la transformation s'arrête (quelle que soit la manière), toute l'éco noire accumulée est consommée (`0.0`).

---
