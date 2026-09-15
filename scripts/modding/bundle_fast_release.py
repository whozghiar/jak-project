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
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_upstream_version(base_version: str = None) -> tuple[str, str]:
  """
  Resolves the upstream version tag to use for downloading official binaries.
  Priority order:
    1. Explicit CLI argument (--base-version)
    2. Environment variable OPENGOAL_BASE_VERSION / UPSTREAM_VERSION
    3. .upstream-version file at repository root
    4. Git ancestry: closest v0.* tag from HEAD
    5. Fallback: None (triggers 'latest' release lookup)
  Returns (version_tag, source_reason).
  """
  if base_version and base_version.strip():
    return base_version.strip(), "CLI argument (--base-version)"

  env_ver = os.environ.get("OPENGOAL_BASE_VERSION") or os.environ.get("UPSTREAM_VERSION")
  if env_ver and env_ver.strip():
    return env_ver.strip(), "environment variable (OPENGOAL_BASE_VERSION)"

  ver_file = REPO_ROOT / ".upstream-version"
  if ver_file.exists():
    try:
      content = ver_file.read_text(encoding="utf-8").strip()
      if content:
        return content, ".upstream-version file"
    except Exception:
      pass

  # Auto-resolve from Git ancestry: closest v0.* tag from HEAD
  try:
    res = subprocess.run(
        ["git", "describe", "--tags", "--match=v0.*", "--abbrev=0", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    if res.returncode == 0 and res.stdout.strip():
      return res.stdout.strip(), "git ancestry (closest v0.* tag)"
  except Exception:
    pass

  # Fallback to general closest tag
  try:
    res = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    if res.returncode == 0 and res.stdout.strip():
      tag = res.stdout.strip()
      if tag.startswith("v0."):
        return tag, "git ancestry"
  except Exception:
    pass

  return None, "fallback to latest official release"


def get_official_release(repo="open-goal/jak-project", tag=None):
  """
  Queries GitHub Releases API for the specified tag (or latest if tag is None).
  Falls back to latest if the specified tag release is not found.
  """
  headers = {"User-Agent": "OpenGOAL-Packager"}
  token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
  if token:
    headers["Authorization"] = f"Bearer {token}"

  url = (
      f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
      if tag
      else f"https://api.github.com/repos/{repo}/releases/latest"
  )

  try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
      data = json.loads(resp.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    if tag:
      print(
          f"Warning: Upstream release for tag '{tag}' not found (HTTP {e.code}). Falling back to 'latest' release...",
          file=sys.stderr,
      )
      url = f"https://api.github.com/repos/{repo}/releases/latest"
      req = urllib.request.Request(url, headers=headers)
      with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    else:
      raise

  resolved_tag = data.get("tag_name", tag)
  win_asset = next(
      (
          a["browser_download_url"]
          for a in data.get("assets", [])
          if a["name"].startswith("opengoal-windows")
          and a["name"].endswith(".zip")
      ),
      None,
  )
  lin_asset = next(
      (
          a["browser_download_url"]
          for a in data.get("assets", [])
          if a["name"].startswith("opengoal-linux")
          and (a["name"].endswith(".tar.gz") or a["name"].endswith(".zip"))
      ),
      None,
  )
  return resolved_tag, win_asset, lin_asset


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
  parser.add_argument(
      "--base-version",
      default=None,
      help="Specific upstream release tag to use (e.g. v0.3.6). If omitted, automatically detected from git ancestry, .upstream-version or latest.",
  )
  args = parser.parse_args()

  out_path = Path(args.out_dir)
  if not out_path.is_absolute():
    out_path = REPO_ROOT / out_path
  out_path.mkdir(parents=True, exist_ok=True)

  target_ver, ver_source = resolve_upstream_version(args.base_version)
  print(f"[1/4] Fetching pre-compiled binaries from {args.base_repo}...")
  if target_ver:
    print(f"      Target upstream version: {target_ver} (source: {ver_source})")
  else:
    print(f"      Target upstream version: latest (source: {ver_source})")

  base_tag, win_url, lin_url = get_official_release(args.base_repo, tag=target_ver)
  if not win_url or not lin_url:
    raise RuntimeError(
        f"Could not find release assets in {args.base_repo} {base_tag}"
    )

  print(f"      Matched upstream release: {base_tag}")
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
  is_zip = lin_url.endswith(".zip")
  lin_archive_name = "upstream_linux.zip" if is_zip else "upstream_linux.tar.gz"
  lin_archive = temp_root / lin_archive_name
  urllib.request.urlretrieve(lin_url, lin_archive)

  lin_dest = temp_root / "dist_linux"
  lin_dest.mkdir(parents=True)
  if is_zip:
    with zipfile.ZipFile(lin_archive, "r") as zf:
      zf.extractall(lin_dest)
  else:
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
