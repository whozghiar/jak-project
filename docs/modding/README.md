# OpenGOAL Modding Documentation Hub / Centre de Documentation du Modding

This directory centralizes all official reference guides, engineering workflows, tool manuals, and synchronization dashboards for modding Jak 1, Jak 2, and Jak 3 with OpenGOAL.

---

## 📚 1. Core References (Consult Before Coding)

These curated, verified documents are the **single source of truth** hosted on `master-dev`. They prevent hallucinations by providing concrete, tested examples and known traps.

| Reference Document | Scope | Contents |
| :--- | :--- | :--- |
| 📗 [`jak1_lisp_instructions.md`](jak1_lisp_instructions.md) | Jak 1 | Verified OpenGOAL LISP syntax, states, and entity functions for Jak 1. |
| 📗 [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) | Jak 2 | Verified OpenGOAL LISP instructions, combat hooks, and entity methods for Jak 2. |
| 📗 [`jak3_lisp_instructions.md`](jak3_lisp_instructions.md) | Jak 3 | Verified OpenGOAL LISP instructions, vehicle hooks, and weapon types for Jak 3. |
| 📘 [`engine_generic_concepts.md`](engine_generic_concepts.md) | All Games | Memory heaps (`global`, `level`, `debug`, `process`), `mmap` PS2 RAM simulation, DGOs, and process lifecycle. |

> **Anti-Conflict Landing Rule:**
> Never edit reference docs directly on a mod branch. Use:
> ```bash
> task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "..." --push
> task modding-sync-docs
> ```

---

## 🤖 2. Agent Guidelines & Modular Skills

- **[Unified Agent Guide (`AGENTS.md`)](../../AGENTS.md)**: Rules, Taskfile command reference, REPL hot-reload cycle, ghost memory verification, and git branching standards.
- **[Dynamic Skills Library (`.agents/skills/`)](../../.agents/skills/)**:
  - [`goal-lisp`](../../.agents/skills/goal-lisp/SKILL.md) & [`discoveries.md`](../../.agents/skills/goal-lisp/discoveries.md)
  - [`engine-internals`](../../.agents/skills/engine-internals/SKILL.md) & [`repl-workflow.md`](../../.agents/skills/engine-internals/repl-workflow.md)
  - [`custom-actors-levels`](../../.agents/skills/custom-actors-levels/SKILL.md) & [`discoveries.md`](../../.agents/skills/custom-actors-levels/discoveries.md)
  - [`texture-modding`](../../.agents/skills/texture-modding/SKILL.md) & [`discoveries.md`](../../.agents/skills/texture-modding/discoveries.md)

---

## 🛠️ 3. Engineering & Workflow Guides

| Guide | Description |
| :--- | :--- |
| 🚀 [`custom_entity_workflow.md`](custom_entity_workflow.md) | Comprehensive engineering guide on importing custom 3D models, custom animations, and new sound banks (`.SBK`) with `og-j1-board` case study. |
| ⚡ [`tools/build_and_iteration_workflow.md`](tools/build_and_iteration_workflow.md) | Three-layer build model, `sccache` acceleration, and targeted build tasks (`build-release-game`, `build-release-decomp`). |
| 🎨 [`tools/model_and_entity_level_injection_guide.md`](tools/model_and_entity_level_injection_guide.md) | No-borrow Merc `.fr3` injection pipeline (`extra_art_groups_by_dgo`) to inject models into any level. |
| 🎛️ [`tools/mods_debug_menu.md`](tools/mods_debug_menu.md) | How to register mods into the in-game Debug ▸ Mods menu via `(mods-menu-register "<slug>" builder)`. |

---

## 🌿 4. Branch Dashboards & Compliance

- 📊 [`tools/branch_sync_status.md`](tools/branch_sync_status.md): Live mergeability dashboard across all mod branches (`task modding-branch-status`).
- 📜 [`tools/branch_sync_history.md`](tools/branch_sync_history.md): Historical log of automated branch merges and conflict resolutions.
- 📋 [`branch_audit.md`](branch_audit.md): Compliance report tracking active mod branches against project standards (`task modding-audit`).

---

## 📁 5. Templates & Mod Readmes

- 📝 [`templates/MOD_README.template.md`](templates/MOD_README.template.md): Bilingual presentation template for root `README.md` on mod branches.
- ⚙️ [`templates/mod_debug_menu.template.gc`](templates/mod_debug_menu.template.gc): Ready-to-use GOAL template for debug menu registration.
- 📂 [`current_mod/`](current_mod/): Folder storing mod-specific feature readmes (e.g. [`current_mod/custom_animation_and_sound_readme.md`](current_mod/custom_animation_and_sound_readme.md)).

---

## 🧰 6. Standalone Modding Tools

- 🎭 [`tools/open-goal-glb-reskin-tool/`](tools/open-goal-glb-reskin-tool/): GUI application for retargeting and reskinning GLB characters.
- 🗺️ [`tools/open-goal-level-builder/`](tools/open-goal-level-builder/): GUI application for building custom OpenGOAL levels.
