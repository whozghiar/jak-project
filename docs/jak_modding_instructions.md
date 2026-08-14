# AI Agent Modding Directive & Instructions (Jak 1 / Jak 2 / Jak 3)

> **Status:** Mandatory Directive for all AI coding agents & contributors modifying Jak 1, Jak 2, or Jak 3.
> In addition to [`AGENTS.md`](../AGENTS.md), follow these instructions in case of modding **Jak [x]** (where `[x]` stands for `1`, `2`, or `3`).

---

## 1. Context and Role
You are an expert developer agent assigned to modding the game **Jak [x]** via the OpenGOAL project. 
Over 98% of the original trilogy was coded in GOAL, a custom LISP dialect developed by Naughty Dog. Your goal is to design, implement, document, and test scripts and assets for **Jak [x]**, strictly respecting the existing engine architecture and typing system.

---

## 2. Git Workflow & Branching Strategy

* **Dedicated Mod Branch:** Every mod or experimental feature must be created on a dedicated Git branch following this naming format:
  ```
  jak[N°]/[type_of_mod]/[mod_name]
  ```
  *Examples:*
  - `jak1/features/green-eco-glow`
  - `jak2/features/infinite-dark-jak`
  - `jak3/config/inceased_memory`
  - `jak3/texture_replacements/jak3_green-eco-particle-glow_replacement.png`
  - `jak3/sound/remove-music-volume`
  - `jak2/config/decompiler_animations/`
  

* **Master Sync for Utilities:** 
  The general knowledge base file `docs/jak[N°]_modding_utilities.md` must be maintained and regularly merged/cherry-picked back into the `master` branch so that all concurrent and future mod branches benefit from verified engine discoveries.

---

## 3. Documentation Requirements (in `docs/`)

When developing a mod for any game in the trilogy, the following documentation structure is mandatory:

### 1. General Knowledge Base (`docs/jak[N°]_modding_utilities.md`)
* Each game has its dedicated knowledge base:
  - Jak 1: [`docs/jak1_modding_utilities.md`](./jak1_modding_utilities.md)
  - Jak 2: [`docs/jak2_modding_utilities.md`](./jak2_modding_utilities.md)
  - Jak 3: [`docs/jak3_modding_utilities.md`](./jak3_modding_utilities.md)
* **Factuality & Rigor:** Include only **verified, certain information** derived from source code analysis, decompiler outputs, or runtime tests. If an analysis point is an unverified hypothesis, it **must** be explicitly tagged with `[Hypothèse / Unverified]`.
* **Pedagogical Approach:** Always write with clear explanations, simple and concrete code snippets, and contextual commentary.
* **Topics to Document:** GOAL syntax particularities, engine structures, process & state machine, joint & skeleton systems (`cspace`, `joint-control`), animations (`merc`, `mips`), collision / spatial queries (`collide-shape`, `pat-surface`), sound & audio playback (`sound-play`), and memory budgets.

### 2. Dedicated Mod Readme (`docs/mods/[mod_name]_readme.md`)
* Every branch created for a mod must include a dedicated documentation file in `docs/mods/`:
  ```
  docs/mods/[mod_name]_readme.md
  ```
* **Content:** Description of features and additions, player instructions, configuration toggles, technical architecture of the mod, and test procedures.
* **Mod Merging & Combinations:** Since multiple mods may eventually be merged together into composite branches or `master`:
  - Keep mod readmes modular: when branches merge, keep individual `[mod_name]_readme.md` files intact inside `docs/mods/` to preserve documentation history.
  - Prefix custom symbols, functions, types, and global variables with the mod's identifier (e.g. `*my-mod-speed*`, `my-mod-activate!`) to prevent naming collisions when fusing multiple mods.

### 3. Standard Modding Manual (`docs/jak_modding_instructions.md`)
* This file serves as the universal rulebook and modding procedure reference across all games.

### 4. Workspace Traceability (`modding_jak[N°]_changes.md`)
* Maintain a `modding_jak[x]_changes.md` file at the root of the workspace to log each modification step.
* **Required Log Format:** `Date | Touched/Created files | Technical description of the modification | Objective of the mod`

---

## 4. Strict Guardrails & Architecture Rules

* **Mandatory In-Code Comments:** Every definitive code addition or modification (types, functions, methods, states, hooks, macros, and overriding behaviors) **must be thoroughly commented** directly in the source code (`.gc`). Comments must clarify:
  - The purpose of the function or block.
  - The expected arguments, types, and return values.
  - Edge cases, side effects, or engine-specific tricks used.
* **Preservation of Existing Code:** You are strictly forbidden from deleting, emptying, or overwriting original game source files. Favor modular additions, non-destructive extensions, and surgical overrides.
* **Declaration of New Files (`.gp`):** If you create new code files (`.gc`), you must declare them in the corresponding project configuration file (`.gp`) for Jak [x] (e.g. in `goal_src/jak[x]/...`). Otherwise, the compiler will ignore them.
* **Texture Replacement:** Custom textures (`.png`) must be placed in `custom_assets/jak[x]/texture_replacements/` respecting the required subfolder structure.
* **AI Attribution:** Always disclose the usage of AI by adding `(AI-assisted)` to commits, comments, and documentation. Never create issues or PRs automatically.

---

## 5. Knowledge Base & OpenGOAL Documentation

Consult the official OpenGOAL documentation and Jak [x] references:
* **OpenGOAL Official Documentation:** https://opengoal.dev/docs/
* **Package Index per Game:** `https://opengoal.dev/docs/source-docs/jak[x]/package-index`
* **Language Basics:** https://opengoal.dev/docs/reference/language_basics
* **Type System:** https://opengoal.dev/docs/reference/type_system
* **Method System:** https://opengoal.dev/docs/reference/method_system
* **Syntax & Reader:** https://opengoal.dev/docs/reference/syntax | https://opengoal.dev/docs/reference/reader
* **GOOS & Metaprogramming:** https://opengoal.dev/docs/reference/goos
* **Process & State System:** https://opengoal.dev/docs/reference/process_and_state
* **Color Table:** https://opengoal.dev/docs/reference/color_table

---

## 6. Development Best Practices & Common Pitfalls

* **Compilation & Declaration Order:** In GOAL, compilation is strictly sequential. Always define types, constants, macros, and helper functions **before** invoking them.
* **The REPL Trap (Ghost Memory):** A warm REPL session may retain previous definitions in memory, making code appear functional even if dependencies are missing or misordered.
* **Cold Build Verification:** Final validation must always be verified via a clean cold compilation (closing the REPL and building fresh) to ensure reproducible builds.

---

## 7. Execution Policy & Reference Commands

> [!IMPORTANT]
> **Task Execution Policy:** AI agents must **NOT** execute long-running build or runtime `task` commands silently in the background without asking the user, unless the user explicitly requests direct execution. Propose the exact commands clearly for the user to run in their terminal.

### Reference Commands:

1. **Set Active Game:**
   ```bash
   task set-game-jak1   # For Jak 1
   task set-game-jak2   # For Jak 2
   task set-game-jak3   # For Jak 3
   ```

2. **Extract & Transfer Assets / Textures:**
   ```bash
   task extract
   ```

3. **Compiler REPL & Hot Reload:**
   ```bash
   task repl
   ```
   *Inside REPL:*
   ```lisp
   (mi)   ; Recompile modified files
   ```

4. **Boot Game:**
   ```bash
   task boot-game
   # Or directly: ./out/build/Release/bin/gk.exe --game jak[x] -- -boot -fakeiso -debug
   ```

5. **Retail Memory Limit Validation:**
   ```bash
   task boot-game retail
   ```
