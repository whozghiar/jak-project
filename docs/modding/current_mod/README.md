# Mod Technical Deep-Dive Documentation (`docs/modding/current_mod/`)

This directory is the dedicated space for **Tier 2 Technical Documentation** for active mod features and subsystems.

---

## 🎯 Purpose & Philosophy

While the mod's **root `README.md`** is player/user-facing (overview, features, how to compile, game controls, video demonstration), files in this directory provide **pedagogical, in-depth engineering documentation** for developers, AI agents, and future maintainers.

### Naming Convention
```text
docs/modding/current_mod/<mod_slug>_readme.md
```
*(e.g., `docs/modding/current_mod/custom_animation_and_sound_readme.md`)*

---

## 📐 Recommended Structure for Mod Technical Readmes

Each technical mod document should adopt a structured, educational approach featuring:

1. **Architecture & Subsystems Impacted:**
   - Affected layers (C++ runtime, decompiler, compiler, GOAL game code, asset pipelines).
   - Core concepts and design decisions.
2. **Pedagogical Walkthrough & Data Pipelines:**
   - Step-by-step breakdown of how data flows (e.g., glTF ➔ `build-actor` ➔ art-group ➔ Merc2 `.fr3`).
   - Skeletons, joints, animation mapping, or audio bank ingestion.
3. **Concrete Code Samples:**
   - Real, commented OpenGOAL Lisp snippets (`deftype`, `defstate`, `defbehavior`, hooks).
   - Avoid generic pseudo-code; provide verified, syntax-valid GOAL code.
4. **State Machine & Logic Diagrams:**
   - Process states (`:enter`, `:trans`, `:code`, `:post`, `:event`), transition triggers, and conditions.
5. **Memory, Heap & Performance Footprint:**
   - Heap allocation targets (`'global` vs `'level` vs `'process`), alignment requirements, and budget impact.
6. **Debugging & Troubleshooting Guide:**
   - Common traps, known edge cases, and REPL verification procedures.
