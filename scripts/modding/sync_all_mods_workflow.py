#!/usr/bin/env python3
"""
Automated synchronization of master-dev into all mod branches
and update of each mod's root README.md according to its build layer (Layer 1, 2, 3).
"""

import os
import re
import subprocess
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BRANCH_LAYERS = {
    # Layer 1 & 2 (C++ + Decomp/Extract)
    "jak2/config/custom_animation_and_sound": "LAYER_1_2",
    "jak2/features/jak3-jetBoard": "LAYER_1_2",

    # Layer 1 (C++ Runtime & Compiler gk/goalc)
    "jak2/config/memory_increase": "LAYER_1",
    "jak2/features/multiplayer": "LAYER_1",
    "jak3/config/memory_increase": "LAYER_1",

    # Layer 2 (Decompiler / Asset extraction / FR3 injection)
    "jak2/features/enhanced_city_traffic_v2": "LAYER_2",
    "jak2/features/merc-fr3-injection-poc": "LAYER_2",
    "jak2/features/paddy_wagon_v2": "LAYER_2",
    "jak2/features/transport_v2": "LAYER_2",

    # Layer 3 (GOAL only)
    "jak2/config/enhanced_spawnrates": "LAYER_3",
    "jak2/config/start_menu_wheel": "LAYER_3",
    "jak2/features/blueguard": "LAYER_3",
    "jak2/features/dark_jak_enhanced": "LAYER_3",
    "jak2/features/transport_alert": "LAYER_3",
    "jak2/features/transport_traffic": "LAYER_3",
    "jak2/features/yakow_killable": "LAYER_3",
    "jak3/features/city-behavior": "LAYER_3",
    "jak3/features/jak2_skin_secret": "LAYER_3",
    "jak3/features/mega_dark_jak": "LAYER_3",
    "jak3/features/redguard-entity": "LAYER_3",
}

TEMPLATE_EN_L1 = """### 2. Binary Compilation
- **Status:** Required (Layer 1 — C++ Runtime & Compiler)
- **Details:** Compiles the modified C++ runtime (`gk`) and compiler (`goalc`) using the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

"""

TEMPLATE_FR_L1 = """### 2. Compilation des Binaires
- **Statut :** Requise (Couche 1 — Runtime C++ & Compilateur)
- **Détails :** Compile le runtime C++ (`gk`) et le compilateur (`goalc`) modifiés grâce à la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

"""

TEMPLATE_EN_L2 = """### 2. Binary Compilation
- **Status:** Required (Layer 1 & Layer 2 — Decompiler & Runtime)
- **Details:** Compiles the runtime, compiler, and decompiler required for asset extraction:
```bash
task build-release-game
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** Custom extraction required (Layer 2)
- **Details:** Re-run extraction to process custom assets and modified decompiler configuration:
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

"""

TEMPLATE_FR_L2 = """### 2. Compilation des Binaires
- **Statut :** Requise (Couche 1 & Couche 2 — Décompilateur & Runtime)
- **Détails :** Compile le runtime, le compilateur et le décompilateur nécessaires à l'extraction des assets :
```bash
task build-release-game
task build-release-decomp
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction personnalisée requise (Couche 2)
- **Détails :** Relancez l'extraction pour intégrer les assets modifiés et la configuration du décompilateur :
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

"""

TEMPLATE_EN_L3 = """### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist
- **Details:** Only GOAL scripts are modified. No C++ rebuild needed. For first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

"""

TEMPLATE_FR_L3 = """### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà
- **Détails :** Seuls les scripts GOAL sont modifiés, aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

"""

def run(cmd, check=False):
    res = subprocess.run(
        cmd,
        shell=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        cwd=REPO_ROOT
    )
    return res

def clean_locks():
    run("git checkout -- third-party/fmt/support/.gradle")

def update_readme_for_branch(branch, layer):
    readme_path = os.path.join(REPO_ROOT, "README.md")
    if not os.path.isfile(readme_path):
        return False

    with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    pattern_en = re.compile(r'### 2\. Binary Compilation.*?((?=## 🎥)|(?=## 📖)|(?=---))', re.DOTALL)
    pattern_fr = re.compile(r'### 2\. Compilation des Binaires.*?((?=## 🎥)|(?=## 📖)|(?=---))', re.DOTALL)

    if not pattern_en.search(content) or not pattern_fr.search(content):
        return False

    if layer in ("LAYER_1_2", "LAYER_2"):
        rep_en = TEMPLATE_EN_L2
        rep_fr = TEMPLATE_FR_L2
    elif layer == "LAYER_1":
        rep_en = TEMPLATE_EN_L1
        rep_fr = TEMPLATE_FR_L1
    else: # LAYER_3
        rep_en = TEMPLATE_EN_L3
        rep_fr = TEMPLATE_FR_L3

    new_content = pattern_en.sub(rep_en, content, count=1)
    new_content = pattern_fr.sub(rep_fr, new_content, count=1)

    if new_content != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def process_branch(branch, layer):
    print(f"\n==========================================")
    print(f"Processing branch: {branch} (Layer: {layer})")
    print(f"==========================================")

    # 1. Checkout
    chk = run(f"git checkout {branch}")
    if chk.returncode != 0:
        chk = run(f"git checkout -b {branch} origin/{branch}")
        if chk.returncode != 0:
            print(f"  [ERROR] Cannot checkout {branch}: {chk.stderr.strip()}")
            return False

    clean_locks()

    # 2. Check if master-dev is already ancestor
    anc = run("git merge-base --is-ancestor master-dev HEAD")
    already_merged = (anc.returncode == 0)

    if already_merged:
        print("  [INFO] master-dev is already merged into this branch.")
        updated = update_readme_for_branch(branch, layer)
        if updated:
            run("git add README.md")
            run('git commit -m "docs: update README build instructions for ' + layer + ' workflow (AI-assisted)"')
            print("  [SUCCESS] README updated and committed.")
        else:
            print("  [INFO] README already up to date.")
        clean_locks()
        return True

    # 3. Merge master-dev
    print("  [INFO] Merging master-dev...")
    m = run('git merge master-dev -m "chore: merge master-dev build tooling and workflow documentation (AI-assisted)"')
    if m.returncode != 0:
        print("  [WARN] Merge conflict detected. Resolving known conflicts...")
        status = run("git status --porcelain").stdout

        # Conflicts in README.md -> keep ours (branch's mod README)
        if "README.md" in status:
            run("git checkout --ours README.md")

        # Conflicts in instructions/docs/config from master-dev -> take theirs
        for path in ["AGENTS.md", "CLAUDE.md", "docs/modding/jak_modding_instructions.md"]:
            if path in status:
                run(f"git checkout --theirs {path}")

        # If any decompiler configs conflict, take ours to preserve mod config
        for path in ["decompiler/config/jak2/jak2_config.jsonc", "decompiler/config/jak3/jak3_config.jsonc"]:
            if path in status:
                run(f"git checkout --ours {path}")

    # 4. Update README with Layer-appropriate instructions
    update_readme_for_branch(branch, layer)

    # 5. Add all resolutions and commit
    clean_locks()
    run("git add -A")
    res_commit = run('git commit -m "chore: merge master-dev build tooling and update README for ' + layer + ' workflow (AI-assisted)"')
    if res_commit.returncode == 0:
        print("  [SUCCESS] Merged master-dev and updated README successfully.")
    else:
        print("  [INFO] " + (res_commit.stdout or res_commit.stderr).strip()[:100])

    clean_locks()
    return True

def main():
    results = {}
    for branch, layer in BRANCH_LAYERS.items():
        success = process_branch(branch, layer)
        results[branch] = success

    # Return to master-dev
    print("\nReturning to master-dev...")
    run("git checkout master-dev")
    clean_locks()

    print("\nSummary of results:")
    for b, s in results.items():
        print(f"  {'[OK]' if s else '[FAIL]'} {b}")

if __name__ == "__main__":
    main()
