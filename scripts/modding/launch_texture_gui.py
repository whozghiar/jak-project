#!/usr/bin/env python3
"""
Launch the OpenGOAL Texture Pack Generator GUI tool (Tauri v2 + Rust + Svelte 5).
If precompiled executable is found, launches it directly.
Otherwise, falls back to npm run tauri dev if node/npm are present.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOL_DIR = REPO_ROOT / "docs" / "modding" / "tools" / "open-goal-texture-pack-generator"


def main() -> int:
    if not TOOL_DIR.exists():
        print(f"Error: Tool directory not found at: {TOOL_DIR}")
        print("Please ensure the git submodule is initialized:")
        print("  git submodule update --init --recursive")
        return 1

    # Check for precompiled binaries
    root_exe = TOOL_DIR / "texture_pack_generator.exe"
    target_exe = TOOL_DIR / "src-tauri" / "target" / "release" / "open-goal-texture-pack-generator.exe"

    exe_path = None
    if root_exe.is_file():
        exe_path = root_exe
    elif target_exe.is_file():
        exe_path = target_exe

    if exe_path:
        print(f"Starting OpenGOAL Texture Pack Generator: {exe_path.name}")
        try:
            if sys.platform == "win32":
                # Detached process so the calling terminal/task returns immediately
                DETACHED_PROCESS = 0x00000008
                subprocess.Popen([str(exe_path)], cwd=str(TOOL_DIR), creationflags=DETACHED_PROCESS)
            else:
                subprocess.Popen([str(exe_path)], cwd=str(TOOL_DIR))
            print("Texture Pack Generator started successfully.")
            return 0
        except Exception as err:
            print(f"Error launching {exe_path}: {err}")
            return 1

    print("No precompiled binary found. Starting Tauri development server (npm run tauri dev)...")
    try:
        return subprocess.run(
            ["npm", "run", "tauri", "dev"],
            cwd=str(TOOL_DIR),
            shell=(sys.platform == "win32"),
        ).returncode
    except Exception as err:
        print(f"Failed to launch development server: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
