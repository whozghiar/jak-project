---
name: custom-actors-levels
description: "Comprehensive guide to custom entities, 3D asset pipelines, adapting/backporting Blender 3D models between Jak games (Jak 1, 2, 3), Blender glTF/GLB exports, armatures, joint channels, non-destructive texture injection, custom sound banks (SBK), Merc .FR3 injection, and custom levels."
tools:
  - mcp:blender
  - View
  - Edit
  - Bash
---

# Custom Actors, Entities, 3D Assets, Rig Adapter & Levels — Engineering Reference

OpenGOAL allows importing custom 3D models, skeletal meshes, custom animations, dedicated sound effect banks (SBK), adapting models across games, and building entire custom levels into Jak 1, Jak 2, and Jak 3. This skill synthesizes the 4-layer entity pipeline, cross-game model adaptation and retargeting, non-destructive texture workflows, the two-circuit rendering model, Blender glTF/GLB export rules, audio bank packaging, and level creation.

> **Full Engineering Case Study:** See [`docs/modding/custom_entity_workflow.md`](../../../docs/modding/custom_entity_workflow.md) for the complete walkthrough of importing models, animations, and sounds (with `og-j1-board` as reference).

---

## 1. Role & Scope: 3D Technical Specialist & Rig Adapter

As a 3D technical specialist and entity engineer for OpenGOAL:
- **Scope:** Adapting character, vehicle, and enemy models between installments of the Jak trilogy (e.g. backporting a model from Jak 3 or Jak 1 to Jak 2), managing articulation skeletons, retargeting armatures, applying non-destructive textures without breaking meshes or vanilla animations, and engineering full custom actors and levels.
- **Tooling & MCP:** Leverage Blender tooling (including `mcp:blender` when active) alongside file inspection tools to inspect joint hierarchies, vertex weights, material slots, and export flags.

---

## 2. Critical Engine Rules & Guardrails

1. **Strict Armature Hierarchy and Joint Channels:**
   - The GOAL engine expects a strict joint hierarchy (joint channels).
   - **NEVER** rename, delete, or add free bones in the main tree without adapting the joint table of the target GOAL actor.
   - Any model adapted from one Jak game to another must be re-parented/retargeted to exactly match the armature expected by the destination `defskelgroup`.
   - Custom `.glb` files for characters **must contain the armature**.
   - **Root Bone (`align` Rule):** Joint 0 MUST be located at `(0, 0, 0)` and **named `align`**. Omitting `align` as joint 0 offsets every bone index by 1, leading to immediate mesh dislocation or engine crashes when applying animations.

2. **Cross-Game Model Adaptation & Retargeting (Jak 1 ↔ Jak 2 ↔ Jak 3):**
   - When porting or backporting a model (e.g., Jak 3 model to Jak 2, or Jak 1 enemy to Jak 2), verify bone counts and joint order against the target game's skeletal definition.
   - Use the `retarget_anim` tool (`cmake --build out/build/Release --target retarget_anim --config Release`) or the GUI Reskin Tool (`docs/modding/tools/open-goal-glb-reskin-tool/`) when adapting joint matrices.
   - Target model location: `.glb` custom files must be placed in:
     ```text
     custom_assets/<target_game>/models/<area_name>/<model_name>.glb
     ```

3. **Non-Destructive Application of Textures & UV Management:**
   - **Vanilla Textures:** Never directly modify the base decompiled archives or retail textures.
   - **Custom Textures:** Always place PNG files in the appropriate directory:
     ```text
     custom_assets/<target_game>/texture_replacements/<texture_folder>/
     ```
   - **UV Coordinates:** When adding a texture or variant, preserve existing UV coordinates or create a new, clean material group without overwriting original UV maps.
   - **Asset Pipeline Compilation:** After modifying an asset or texture, extract and update the game files by running `task extract` so that the asset compiler deploys them to `decompiler_out/` and generates GPU-ready assets (`.fr3`).

4. **Export Format & Transformations:**
   - All meshes and animations must be exported as binary glTF (`.glb`) without data loss.
   - Ensure vertex weights, normals, and UVs are included.
   - Apply all base transformations (Scale `1.0`, Rotation `(0, 0, 0)`) before exporting (`Ctrl+A` -> Apply All Transforms in Blender).

5. **Traceability & Mod Documentation:**
   - Record each modified asset, modified armature, or added texture in the current mod's Technical README file:
     ```text
     docs/modding/current_mod/<mod_slug>_readme.md
     ```

---

## 3. The 4-Layer Entity Ingestion Model

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

## 4. The 2-Circuit Architecture for Skeletal Actors

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

## 5. Merc `.fr3` Injection (No-Borrow Workflow)

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

## 6. Blender Workflow for Custom Models (.glb)

Custom models must be exported from Blender as binary glTF (`.glb`).

### Armature & Skeleton Rules
- **Root Bone (`align` Rule):** Joint 0 MUST be located at `(0, 0, 0)` and **named `align`**. Omitting `align` as joint 0 offsets every bone index by 1, leading to immediate mesh dislocation or engine crashes when applying animations.
- **Bone Hierarchy:** Joints must match the bone index expectation of the target game. If replacing or extending an existing actor (e.g., Jak or a Crimson Guard), the bone count, naming, and orientations must strictly match the original skeleton.
- **Joint Channels:** In OpenGOAL, skeletal animations are compressed into joint channels (translation, quaternion rotation, scale). Apply scale and rotation in Blender before exporting (`Ctrl+A` -> Apply All Transforms).
- **Scale:** Ensure Blender units match OpenGOAL world scale (1 Blender meter corresponds to game meters).

### Required Blender Plugins & Standalone Tools
- **Blender Add-ons (`custom_assets/blender_plugins/`):**
  - `opengoal.py`: Mesh tools, surface collision flags (PAT), and vertex-colour bake helpers.
  - `gltf2_blender_extract.py`: Custom exporter drop-in replacement (place inside Blender's `scripts/addons/io_scene_gltf2/blender/exp/`) to ensure proper joint layout and vertex-colour exports for `build-actor`.
- **Standalone Tools Compilation (CMake targets):**
  ```bash
  cmake --build out/build/Release --target retarget_anim --config Release
  cmake --build out/build/Release --target build_actor   --config Release
  cmake --build out/build/Release --target build_sbk     --config Release
  ```

### Export Settings (Blender glTF 2.0 Exporter)
- **Format:** `glTF Binary (.glb)`
- **Include:** Limit to selected objects, Armatures + Meshes. Character `.glb` files must contain the armature.
- **Transform:** `+Y Up` (standard glTF orientation).
- **Geometry:** Apply Modifiers, Include Normals, Include UVs, Include Vertex Colors (if used).
- **Animation:** Enabled if exporting animations. Use NLA strips or Actions.

---

## 7. Animation Mapping & Master Art Groups

When grafting custom animations onto an existing character (e.g. Jak or Daxter):
- Use `build-actor` parameters:
  - `:master-art-group`: Name of the parent art group (e.g. `"eichar-ag"`).
  - `:master-ag-map`: Explicit mapping table from animation name to slot index (`(ja name -> slot)`).
  - `:joint-channel`: Specifies which bones are driven by the animation and which are ignored.
- In `game.gd`, place custom art groups **immediately after** the parent art group so master art group indices stay coherent.

### Linking Hook (`register-custom-art-group`)
Art-groups built with `:master-art-group` contain a `joint-geo` at slot 0, which makes native `needs-link?` return `#f`. Without manual registration, their animations are never linked to the character at level load.
In top-level mod code, register your art-group name (without `-ag`):
```lisp
;; Register custom art-group into *custom-art-groups-to-link* (checked in joint.gc and level.gc)
(register-custom-art-group "mes-anims-jak")
```

---

## 8. Custom Sound Banks (SBK Audio Pipeline)

Adding dedicated sound effects for a custom entity:

### 1. Source Audio Files
Place 16-bit 48kHz PCM WAV audio files + `metadata.txt` under:
```text
custom_assets/jak[x]/sounds/sfx/<BANK_NAME>/
```
*(Tip: generate a valid `metadata.txt` layout by extracting an existing bank via `rip_sound_banks` decompiler override).*

### 2. Delivery Routes
- **Route A — Append to `COMMON` (Recommended for global sounds):**
  1. In `goal_src/jak[x]/game.gp`, remove `"COMMON"` from `copy-sbk-files` (avoids duplicate output build error).
  2. Append your sounds into `COMMON.SBK`:
     ```lisp
     (append-sbk "COMMON" "custom_assets/jak2/sounds/sfx/MY_SFX" :force-run #t)
     ```
  3. Play directly anywhere: `(sound-play "my-sound")`.
- **Route B — Standalone Bank (`build-sbk`):**
  1. Build a new `.SBK`:
     ```lisp
     (build-sbk "MYBANK" "custom_assets/jak2/sounds/sfx/MYBANK" :force-run #t :bank-id #x6d79736e)
     ```
  2. Load before use: `(sound-bank-load (static-sound-name "MYBANK"))`.
  3. ⚠️ Overlord provides 3 dedicated slots (`common`, `gun`, `board`) and a 3-slot rotating level pool. Route B uses the rotating pool and can conflict with level sound banks.

### 3. Looping Sounds
For looped or frame-updated sounds (`sound-play-by-name`), pre-allocate the sound ID **once** in the actor's `-init` state via `(new-sound-id)`, never inside the frame loop.

---

## 9. Custom Level Creation

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
