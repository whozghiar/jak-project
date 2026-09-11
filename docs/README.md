# OpenGOAL Documentation Hub / Centre de Documentation OpenGOAL

Welcome to the documentation tree for the OpenGOAL project and modding framework (`jak-project`).

---

## 📂 Structure Overview / Organisation des Dossiers

```text
docs/
├── modding/                # Complete modding documentation, verified references & guides
├── setup/                  # Environment, toolchain & IDE setup (VSCode, VS, Linux, Windows, macOS)
├── progress-notes/         # Upstream decompilation logs, assembly notes & reverse-engineering records
├── scratch/                # Upstream developer scratchpad and temporary notes
└── project-overview.md     # Architecture overview of OpenGOAL compiler, runtime & decompiler
```

---

## 🧭 Key Entry Points / Points d'Accès Principaux

### 1. Modding & Development
- 🛠️ **[Modding Hub (`docs/modding/`)](modding/README.md)**: Verified Lisp instructions (`jak[1|2|3]_lisp_instructions.md`), generic engine primer (`engine_generic_concepts.md`), entity workflow, and mod tools.
- 🤖 **[AI Agent & Developer Guide (`AGENTS.md`)](../AGENTS.md)**: Central rules, Taskfile command reference, REPL hot-reload cycle, ghost memory verification, and git branching standards.
- 🧠 **[Modular Skills (`.agents/skills/`)](../.agents/skills/)**: High-density engineering skills loaded on demand:
  - [`goal-lisp`](../.agents/skills/goal-lisp/SKILL.md): GOAL syntax, state machines, types & macros.
  - [`engine-internals`](../.agents/skills/engine-internals/SKILL.md): C++ runtime, heaps & REPL workflow.
  - [`custom-actors-levels`](../.agents/skills/custom-actors-levels/SKILL.md): 3D models, Blender `.glb` exports, armatures & levels.
  - [`texture-modding`](../.agents/skills/texture-modding/SKILL.md): Custom texture injection & replacement.

### 2. Environment & Toolchain Setup
- 💻 **[Setup Guides (`docs/setup/`)](setup/)**:
  - **Operating Systems:** [Windows](setup/system/windows.md) · [Linux](setup/system/linux.md) · [macOS](setup/system/macos.md) · [Docker](setup/system/docker.md)
  - **IDEs & Editors:** [VSCode](setup/dev/vscode.md) · [Visual Studio](setup/dev/vs.md) · [Zed](setup/dev/zed.md)

### 3. Engine Architecture & Historical Notes
- 📖 **[Project Overview (`docs/project-overview.md`)](project-overview.md)**: Upstream architecture and component roles.
- 🔬 **[Progress Notes (`docs/progress-notes/`)](progress-notes/)**: Decompilation notes, bone systems, joint decompression, and VU assembly documentation.
