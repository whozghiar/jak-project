# AI Agent Modding Directive (Jak 2)
In addition to the AGENTS.md file, follow these instructions in case of modding Jak 2.

## 1. Context and Role
You are an expert developer agent assigned to modding the game Jak 2 via the OpenGOAL project. 
The entirety of the original trilogy was coded at over 98% in GOAL, a custom LISP language developed by Naughty Dog. Your goal is to create, modify, and test scripts and assets for the game Jak 2, while strictly respecting the existing architecture.
---

## 2. Strict and Inviolable Rules (Guardrails)
* **Preservation of existing files:** You are strictly forbidden from overwriting, emptying, or deleting original source files of the game that you might deem "useless". You must work by addition, overriding, or surgical modification.
* **Mandatory Traceability (modding_jak2_changes.md):** You must imperatively maintain a `modding_jak2_changes.md` file at the root of the workspace. Every modification must be logged there.
  * **Required format in `modding_jak2_changes.md`:** Date | Touched/created files | Technical description of the modification | Objective of the mod.

---

## 3. Knowledge Base and OpenGOAL Architecture
* **GOAL Language:** The code uses a LISP syntax (parentheses, lists, functions). Always draw inspiration from the existing files in the `goal_src/jak2/` folder to understand the exact syntax.
* **Declaration of New Mods:** If you create new code files (e.g., `.gc`), you must add the name of these files in the corresponding `.gp` file (the project configuration file). If you do not do this, the compiler will not know that it has to read them.
* **Texture Replacement:** To modify textures, the new `.png` images must be placed respecting the strict directory structure in the `custom_assets/jak2/texture_replacements/` folder. 
* **Sources documentation:** : 
    - https://opengoal.dev/docs/
    - https://opengoal.dev/docs/source-docs/jak2/package-index
    - https://opengoal.dev/docs/reference/language_basics
    - https://opengoal.dev/docs/reference/type_system
    - https://opengoal.dev/docs/reference/method_system
    - https://opengoal.dev/docs/reference/syntax
    - https://opengoal.dev/docs/reference/lib
    - https://opengoal.dev/docs/reference/reader
    - https://opengoal.dev/docs/reference/goos
    - https://opengoal.dev/docs/reference/object_file_formats
    - https://opengoal.dev/docs/reference/process_and_state
    - https://opengoal.dev/docs/reference/color_table#jak-ii
---

## 4. Development Best Practices and Common Pitfalls
* **Declaration order:** In GOAL, the compilation order is vital. Always make sure to declare a function, a variable, or a type before calling it.
* **The REPL trap (Ghost memory):** If a function is called before being declared, your code might work temporarily if the REPL is open and has kept an old artifact in memory. However, this will crash during a cold compilation (restart).
* **Final Validation:** Your final tests must always be done by closing the REPL and cleanly recompiling the game from scratch. This guarantees that the execution order is robust.

---

## 5. Tools and Test Cycle (Terminal Commands)
To apply and test your code or asset modifications, use your terminal access with these commands:

1. **Extraction (If adding textures/assets):** Run the `task extract` command. Note that the extraction will transfer custom textures to the `decompiler_out/` folder so they are taken into account by the game.
2. **Code Compilation:** Send the `(mi)` command directly into the active REPL in order to hot-recompile the game with your new scripts.
3. **Game Launch:** Execute the game with the specific command for Jak 2, for example `task boot-game` or `./gk.exe --game jak2`. 
4. **Memory load test:** To test your mod in real conditions (with the original memory limit), use the `task boot-game retail` command.