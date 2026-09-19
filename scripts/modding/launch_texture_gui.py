#!/usr/bin/env python3
"""
Launch the OpenGOAL Texture Pack Generator GUI tool (Tauri v2 + Rust + Svelte 5).
Workflow:
1. If precompiled executable exists (texture_pack_generator.exe or target/release/open-goal-texture-pack-generator.exe), run it.
2. If missing, attempt to auto-download the latest release binary from GitHub Releases:
   https://github.com/whozghiar/open-goal-texture-pack-generator/releases/latest/download/texture_pack_generator.exe
3. If download fails or offline, fall back to starting the Tauri dev server (npm run tauri dev).
"""
from __future__ import annotations

import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOL_DIR = REPO_ROOT / "docs" / "modding" / "tools" / "open-goal-texture-pack-generator"
GITHUB_RELEASE_URL = (
    "https://github.com/whozghiar/open-goal-texture-pack-generator/releases/latest/download/texture_pack_generator.exe"
)


def download_binary(dest_path: Path) -> bool:
    print("Precompiled binary not found locally.")
    print("Attempting to download latest release from GitHub...")
    print(f"URL: {GITHUB_RELEASE_URL}")
    try:
        req = urllib.request.Request(
            GITHUB_RELEASE_URL,
            headers={"User-Agent": "OpenGOAL-Launcher-Tool"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536
            temp_dest = dest_path.with_suffix(".tmp")
            with open(temp_dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        print(f"\rDownloading: {pct:.1f}% ({downloaded / (1024*1024):.1f} MB)", end="")
                    else:
                        print(f"\rDownloading: {downloaded / (1024*1024):.1f} MB", end="")
            print("\nDownload complete.")
            temp_dest.replace(dest_path)
            return True
    except Exception as err:
        print(f"\nCould not auto-download binary: {err}")
        return False


def main() -> int:
    if not TOOL_DIR.exists():
        print(f"Error: Tool directory not found at: {TOOL_DIR}")
        print("Please ensure the git submodule is initialized:")
        print("  git submodule update --init --recursive")
        return 1

    # Check for local precompiled binaries
    root_exe = TOOL_DIR / "texture_pack_generator.exe"
    target_exe = TOOL_DIR / "src-tauri" / "target" / "release" / "open-goal-texture-pack-generator.exe"

    exe_path = None
    if root_exe.is_file():
        exe_path = root_exe
    elif target_exe.is_file():
        exe_path = target_exe

    # If binary not found and on Windows, attempt auto-download
    if not exe_path and sys.platform == "win32":
        if download_binary(root_exe):
            exe_path = root_exe

    if exe_path and exe_path.is_file():
        print(f"Starting OpenGOAL Texture Pack Generator: {exe_path.name}")
        try:
            subprocess.Popen([str(exe_path)], cwd=str(TOOL_DIR))
            print("Texture Pack Generator started successfully.")
            return 0
        except Exception as err:
            print(f"Error launching {exe_path}: {err}")
            return 1

    print("Starting Tauri development server (npm run tauri dev)...")
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
