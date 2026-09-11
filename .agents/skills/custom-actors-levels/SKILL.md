---
name: custom-actors-levels
description: Comprehensive guide to custom entities, 3D asset pipelines, Blender glTF/GLB exports, armatures, joint channels, custom sound banks (SBK), Merc .FR3 injection, and custom levels.
---

# Custom Actors, Entities, 3D Assets & Levels — Engineering Reference

OpenGOAL allows importing custom 3D models, skeletal meshes, custom animations, dedicated sound effect banks (SBK), and entire custom levels into Jak 1, Jak 2, and Jak 3. This skill synthesizes the 4-layer entity pipeline, the two-circuit rendering model, Blender glTF/GLB export rules, audio bank packaging, and level creation.

> **Full Engineering Case Study:** See [`docs/modding/custom_entity_workflow.md`](../../../docs/modding/custom_entity_workflow.md) for the complete walkthrough of importing models, animations, and sounds (with `og-j1-board` as reference).

---

## 1. The 4-Layer Entity Ingestion Model

Every external asset must traverse four architectural layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ ① C++ Tooling (goalc, decompiler, common)                             │
│   • build-actor: Converts glTF (.glb) → engine art-group (.go)         │
│   • build-sbk: Converts WAV audio files → sound bank (.SBK)            │
│   • decompiler: Extracts retail game models & sounds into glTF/WAV     │
├────────────────────────────────────────────────────────────────────────┤
│ ② Asset Pipeline (GOOS / game.gp)                                      │
│   • (build-actor ...) describes 3D models, bones, and animation maps   │
│   • (build-sbk ...) compiles custom sound banks                        │
│   • Asset locations: custom_assets/jak[x]/models/ and sounds/sfx/      │
├────────────────────────────────────────────────────────────────────────┤
│ ③ Container Packaging (DGO / CGO / ISO)                                │
│   • game.gd / <level>.gd: Packs art-groups (.go) into GAME.CGO/DGO     │
│   • *all-sbk*: Injected into the "iso" group in game.gp for Overlord   │
├────────────────────────────────────────────────────────────────────────┤
│ ④ GOAL Code (goal_src/jak[x]/...)                                      │
│   • deftype & defstate: State machine, physics, and behavior hooks     │
│   • ja-no-eval / ja :group!: Plays skeletal animations                │
│   • sound-play: Triggers bank SFX via the Overlord sound driver        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 2-Circuit Architecture for Skeletal Actors

Every rendered actor in OpenGOAL depends on two independent pipelines:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Circuit 1: GOAL Heap (Game Logic & Skeletons)                         │
│   Source: target_level.gd / all_objs.json -> <model>-ag.go             │
│   Loaded into: RAM by GOAL heap loader                                 │
│   Contains: Joint hierarchy (*-jg), animations (*-ja), bone matrices   │
│   Looked up by: art-group-get-by-name & initialize-skeleton            │
│   Failure symptom: Crash with process-drawable-art-error               │
├────────────────────────────────────────────────────────────────────────┤
│ Circuit 2: PC Merc2 Renderer (3D Geometry & Textures)                  │
│   Source: decompiler/config/jak[x]/*.jsonc -> extra_art_groups_by_dgo │
│   Baked into: out/jak[x]/fr3/<level>.fr3 via 'task extract'            │
│   Loaded into: GPU VRAM by PC renderer (Merc2)                         │
│   Contains: 3D mesh vertices (*-mg), UVs, material assignments         │
│   Failure symptom: Model is completely INVISIBLE (silent skip)         │
└────────────────────────────────────────────────────────────────────────┘
```

> **Golden Rule:** Loading an art group (`.ag`) into GOAL memory (Circuit 1) makes the actor logically exist, but it will remain **completely invisible** unless its geometry was baked into the active level's `.fr3` file (Circuit 2) via `extra_art_groups_by_dgo` during `task extract`.

---

## 3. Merc `.fr3` Injection (No-Borrow Workflow)

To inject an existing or custom model into a level without burning scarce level borrow slots:

1. Locate the model's art group name in `goal_src/jak[x]/build/all_objs.json` (e.g. `"transport-ag"`) and its home DGO.
2. Edit `decompiler/config/jak[x]/jak[x]_config.jsonc`:
   ```jsonc
   "extra_art_groups_by_dgo": {
     "LWIDEA": ["transport-ag:LPROTECT.DGO"]
   }
   ```
3. Rebuild decompiler and re-extract:
   ```bash
   task build-release-decomp
   task extract
   ```
4. Add the art group `.go` to the target level's `.gd` list or load it dynamically.

---

## 4. Blender Workflow for Custom Models (.glb)

Custom models must be exported from Blender as binary glTF (`.glb`).

### Armature & Skeleton Rules
- **Root Bone:** The root bone must be located at `(0, 0, 0)`.
- **Bone Hierarchy:** Joints must match the bone index expectation of the target game. If replacing or extending an existing actor (e.g., Jak or a Crimson Guard), the bone count, naming, and orientations must strictly match the original skeleton.
- **Joint Channels:** In OpenGOAL, skeletal animations are compressed into joint channels (translation, quaternion rotation, scale). Apply scale and rotation in Blender before exporting (`Ctrl+A` -> Apply All Transforms).
- **Scale:** Ensure Blender units match OpenGOAL world scale (1 Blender meter corresponds to game meters).

### Export Settings (Blender glTF 2.0 Exporter)
- **Format:** `glTF Binary (.glb)`
- **Include:** Limit to selected objects, Armatures + Meshes.
- **Transform:** `+Y Up` (standard glTF orientation).
- **Geometry:** Apply Modifiers, Include Normals, Include UVs, Include Vertex Colors (if used).
- **Animation:** Enabled if exporting animations. Use NLA strips or Actions.

---

## 5. Animation Mapping & Master Art Groups

When grafting custom animations onto an existing character (e.g. Jak or Daxter):
- Use `build-actor` parameters:
  - `:master-art-group`: Name of the parent art group (e.g. `"eichar-ag"`).
  - `:master-ag-map`: Explicit mapping table from animation name to slot index (`(ja name -> slot)`).
  - `:joint-channel`: Specifies which bones are driven by the animation and which are ignored.
- In `game.gd`, place custom art groups **immediately after** the parent art group so master art group indices stay coherent.

---

## 6. Custom Sound Banks (SBK Audio Pipeline)

Adding dedicated sound effects for a custom entity:

1. Place 16-bit 48kHz WAV audio files under:
   ```text
   custom_assets/jak[x]/sounds/sfx/<BANK_NAME>/
   ```
2. In `goal_src/jak[x]/game.gp`, invoke the `build-sbk` macro:
   ```lisp
   (build-sbk "BOARD" "custom_assets/jak1/sounds/sfx/BOARD")
   ```
3. `build-sbk` registers `BOARD.SBK` into `*all-sbk*`, which is appended to the `iso` group in `game.gp`:
   ```lisp
   (group-list "iso"
     `("$OUT/iso/0COMMON.TXT"
       ...
       ,@(reverse *all-sbk*)
       ...))
   ```
4. Play the sound in GOAL code:
   ```lisp
   (sound-play "board-loop")
   ```

---

## 7. Custom Level Creation

Custom levels are built from `.glb` environment models and configuration files.

### Directory Structure
```text
custom_assets/jak[x]/levels/<level_name>/
├── <level_name>.jsonc       # Level properties, lighting, actor spawns
├── <level_name>.gd          # DGO package descriptor
└── <level_name>.glb         # 3D environment mesh and collision exported from Blender
```

### Level Build Configuration (`game.gp`)
Declare the custom level build targets in `goal_src/jak[x]/jak[x]-game.gp`:
```lisp
(build-custom-level "my-level")
(custom-level-cgo "MYLEVEL.DGO" "my-level/mylevel.gd")
```

### In-Engine Registration (`level-info.gc`)
Add level metadata in `goal_src/jak[x]/engine/level/level-info.gc`:
- Level symbol and name string
- Bounding box and loading conditions
- Music and ambient sound definitions

### Loading and Testing
1. Recompile assets: `task repl` -> `(mi)`
2. Boot game: `task boot-game`
3. In REPL, warp to custom level:
   ```lisp
   (bg-custom 'my-level-vis)
   ```
