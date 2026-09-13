#!/usr/bin/env python3
"""
Fast packaging script for GOAL-only mods (no C++ rebuild needed).
Downloads official pre-compiled OpenGOAL binaries (gk, goalc, extractor)
and injects the mod's GOAL code and custom assets.
Runs in ~30 seconds on any machine (local or GitHub Actions).
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import tarfile
import urllib.request
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]


def get_latest_official_release(repo="open-goal/jak-project"):
  url = f"https://api.github.com/repos/{repo}/releases/latest"
  headers = {"User-Agent": "OpenGOAL-Packager"}
  token = os.environ.get("GITHUB_TOKEN")
  if token:
    headers["Authorization"] = f"Bearer {token}"
  req = urllib.request.Request(url, headers=headers)
  with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    tag = data["tag_name"]
    win_asset = next(
        (
            a["browser_download_url"]
            for a in data["assets"]
            if a["name"].startswith("opengoal-windows")
            and a["name"].endswith(".zip")
        ),
        None,
    )
    lin_asset = next(
        (
            a["browser_download_url"]
            for a in data["assets"]
            if a["name"].startswith("opengoal-linux")
            and (a["name"].endswith(".tar.gz") or a["name"].endswith(".zip"))
        ),
        None,
    )
    return tag, win_asset, lin_asset


def inject_mod_data(dest_dir: Path):
  """Injects local mod assets into the extracted distribution folder."""
  data_dir = dest_dir / "data"
  data_dir.mkdir(parents=True, exist_ok=True)

  # 1. GOAL Source code (mandatory)
  local_gsrc = REPO_ROOT / "goal_src"
  if local_gsrc.exists():
    shutil.copytree(local_gsrc, data_dir / "goal_src", dirs_exist_ok=True)

  # 2. Decompiler configs
  local_decomp = REPO_ROOT / "decompiler" / "config"
  if local_decomp.exists():
    shutil.copytree(
        local_decomp, data_dir / "decompiler" / "config", dirs_exist_ok=True
    )

  # 3. Game assets
  local_assets = REPO_ROOT / "game" / "assets"
  if local_assets.exists():
    shutil.copytree(local_assets, data_dir / "game" / "assets", dirs_exist_ok=True)

  # 4. Shaders (ensure present)
  local_shaders = (
      REPO_ROOT / "game" / "graphics" / "opengl_renderer" / "shaders"
  )
  if local_shaders.exists():
    shutil.copytree(
        local_shaders,
        data_dir / "game" / "graphics" / "opengl_renderer" / "shaders",
        dirs_exist_ok=True,
    )

  # 5. Custom assets (if any)
  local_custom = REPO_ROOT / "custom_assets"
  if local_custom.exists():
    shutil.copytree(
        local_custom, data_dir / "custom_assets", dirs_exist_ok=True
    )


def main():
  parser = argparse.ArgumentParser(
      description="Fast package OpenGOAL mod using official pre-compiled binaries."
  )
  parser.add_argument("--tag", required=True, help="Mod release tag (e.g. v1.0.0)")
  parser.add_argument(
      "--out-dir", default="final-artifacts", help="Output directory for archives"
  )
  parser.add_argument(
      "--base-repo",
      default="open-goal/jak-project",
      help="Upstream repo for pre-compiled binaries",
  )
  args = parser.parse_args()

  out_path = Path(args.out_dir)
  if not out_path.is_absolute():
    out_path = REPO_ROOT / out_path
  out_path.mkdir(parents=True, exist_ok=True)

  print(f"[1/4] Fetching latest pre-compiled binaries from {args.base_repo}...")
  base_tag, win_url, lin_url = get_latest_official_release(args.base_repo)
  if not win_url or not lin_url:
    raise RuntimeError(
        f"Could not find release assets in {args.base_repo} {base_tag}"
    )

  print(f"      Base version: {base_tag}")
  print(f"      Windows asset: {win_url}")
  print(f"      Linux asset  : {lin_url}")

  temp_root = REPO_ROOT / ".temp_mod_bundle"
  if temp_root.exists():
    shutil.rmtree(temp_root)
  temp_root.mkdir(parents=True)

  # -------------------------------------------------------------
  # Windows Packaging
  # -------------------------------------------------------------
  print("\n[2/4] Downloading and bundling Windows package...")
  win_archive = temp_root / "upstream_windows.zip"
  urllib.request.urlretrieve(win_url, win_archive)

  win_dest = temp_root / "dist_windows"
  win_dest.mkdir(parents=True)
  with zipfile.ZipFile(win_archive, "r") as zf:
    zf.extractall(win_dest)
  win_archive.unlink()

  inject_mod_data(win_dest)

  win_out_zip = out_path / f"windows-{args.tag}.zip"
  if win_out_zip.exists():
    win_out_zip.unlink()

  shutil.make_archive(
      str(out_path / f"windows-{args.tag}"), "zip", root_dir=win_dest
  )
  print(f"      Successfully generated: {win_out_zip}")

  # -------------------------------------------------------------
  # Linux Packaging
  # -------------------------------------------------------------
  print("\n[3/4] Downloading and bundling Linux package...")
  lin_archive = temp_root / "upstream_linux.tar.gz"
  urllib.request.urlretrieve(lin_url, lin_archive)

  lin_dest = temp_root / "dist_linux"
  lin_dest.mkdir(parents=True)
  with tarfile.open(lin_archive, "r:gz") as tf:
    tf.extractall(lin_dest)
  lin_archive.unlink()

  inject_mod_data(lin_dest)

  # Ensure executable permissions on Linux binaries
  for b in ["gk", "goalc", "extractor"]:
    bin_path = lin_dest / b
    if bin_path.exists():
      bin_path.chmod(0o755)

  lin_out_zip = out_path / f"linux-{args.tag}.zip"
  if lin_out_zip.exists():
    lin_out_zip.unlink()

  shutil.make_archive(
      str(out_path / f"linux-{args.tag}"), "zip", root_dir=lin_dest
  )
  print(f"      Successfully generated: {lin_out_zip}")

  # Cleanup
  shutil.rmtree(temp_root, ignore_errors=True)
  print("\n[4/4] Fast packaging completed successfully in ~30 seconds!")


if __name__ == "__main__":
  main()
