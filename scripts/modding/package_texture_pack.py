#!/usr/bin/env python3
"""
Package OpenGOAL Texture Pack into a launcher-compliant .zip archive
and optionally register/update it in index.json under "texturePacks".

Complies strictly with:
- Official OpenGOAL documentation: https://opengoal.dev/docs/developing/texture_packs/
- Official OpenGOAL launcher schema: schemas/texture-packs/v1/texture-pack-schema.v1.json
- Official OpenGOAL launcher backend: src-tauri/src/commands/features/texture_packs.rs

Can be run standalone or via Taskfile:
    task modding-package-texture-pack -- --update-index
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_git(args: list[str]) -> str:
  """Run a git command in REPO_ROOT and return stripped stdout."""
  try:
    res = subprocess.run(
        ["git"] + args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()
  except Exception:
    return ""


def detect_current_branch() -> str:
  return run_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "master-dev"


def detect_github_repo_info() -> tuple[str, str]:
  """Return (owner, repo_name) inferred from origin remote URL."""
  remote_url = run_git(["config", "--get", "remote.origin.url"])
  if not remote_url:
    return ("whozghiar", "jak-project")
  # Handle HTTPS or SSH: https://github.com/owner/repo.git or git@github.com:owner/repo.git
  match = re.search(r"github\.com[/:]([\w-]+)/([\w-]+?)(?:\.git)?$", remote_url)
  if match:
    return (match.group(1), match.group(2))
  return ("whozghiar", "jak-project")


def detect_active_game() -> str:
  """Auto-detect active game from branch, .env, or custom_assets/."""
  branch = detect_current_branch()
  for candidate in ["jak1", "jak2", "jak3", "jakx"]:
    if branch.startswith(f"{candidate}/"):
      return candidate

  # Check .env
  env_file = REPO_ROOT / "scripts" / "tasks" / ".env"
  if env_file.exists():
    try:
      for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("GAME="):
          game_val = line.split("=", 1)[1].strip().strip('"').strip("'")
          if game_val in ["jak1", "jak2", "jak3", "jakx"]:
            return game_val
    except Exception:
      pass

  # Inspect custom_assets
  for candidate in ["jak1", "jak2", "jak3"]:
    tex_dir = REPO_ROOT / "custom_assets" / candidate / "texture_replacements"
    if tex_dir.exists() and list(tex_dir.rglob("*.png")):
      return candidate

  return "jak2"


def detect_author() -> str:
  git_user = run_git(["config", "user.name"])
  if git_user and git_user.strip():
    return git_user.strip()
  owner, _ = detect_github_repo_info()
  return owner or "whozghiar"


def compute_sha256(filepath: Path) -> str:
  hasher = hashlib.sha256()
  with open(filepath, "rb") as f:
    while chunk := f.read(65536):
      hasher.update(chunk)
  return hasher.hexdigest()


def slug_to_display_name(slug: str) -> str:
  clean = slug.replace("-textures", "").replace("_textures", "")
  words = [w.capitalize() for w in re.split(r"[-_]+", clean) if w]
  return " ".join(words) + " Textures"


def package_texture_pack(
    game: str = None,
    slug: str = None,
    display_name: str = None,
    description: str = None,
    author: str = None,
    version: str = "1.0.0",
    tags: list[str] = None,
    cover_path: Path = None,
    output_zip: Path = None,
    update_index: bool = False,
    release_url_base: str = None,
) -> Path:
  if not game:
    game = detect_active_game()

  branch = detect_current_branch()
  owner, repo_name = detect_github_repo_info()

  if not slug:
    leaf = branch.split("/")[-1] if "/" in branch else "custom"
    if not leaf.endswith("-textures"):
      slug = f"{leaf}-textures"
    else:
      slug = leaf

  if not display_name:
    display_name = slug_to_display_name(slug)

  if not author:
    author = detect_author()

  if not description:
    description = f"Texture replacement pack for {display_name} ({game})."

  if tags is None:
    tags = [game, "retexture"]
    # Add slug keywords
    keywords = [k for k in re.split(r"[-_]+", slug) if k not in ["textures", game, "jak"]]
    for k in keywords[:3]:
      if k not in tags:
        tags.append(k)

  src_texture_dir = REPO_ROOT / "custom_assets" / game / "texture_replacements"
  if not src_texture_dir.exists():
    raise FileNotFoundError(f"Texture directory not found: {src_texture_dir}")

  png_files = list(src_texture_dir.rglob("*.png"))
  if not png_files:
    raise ValueError(f"No PNG textures found in {src_texture_dir}")

  print(f"[+] Found {len(png_files)} texture(s) for {game} in {src_texture_dir}")

  if output_zip is None:
    output_dir = REPO_ROOT / "out" / "textures"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_zip = output_dir / f"{slug}-v{version}.zip"
  else:
    output_zip.parent.mkdir(parents=True, exist_ok=True)

  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
  release_date_simple = datetime.now(timezone.utc).strftime("%Y-%m-%d")

  # Construct metadata conforming to both OpenGOAL JSON Schema and Rust Launcher struct
  metadata = {
      "schemaVersion": "1.0.0",
      "version": version,
      "name": display_name,
      "description": description,
      "author": author,
      "authors": author,
      "releaseDate": release_date_simple,
      "publishedDate": now_iso,
      "tags": tags,
      "supportedGames": [game],
  }

  print(f"[+] Creating texture pack archive: {output_zip}")
  with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. metadata.json at root
    metadata_bytes = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
    zf.writestr("metadata.json", metadata_bytes)
    print("  [+] Added metadata.json")

    # 2. cover.png at root (if present)
    cover_file = None
    if cover_path and cover_path.exists():
      cover_file = cover_path
    else:
      candidates = [
          REPO_ROOT / "docs" / "img" / "mod" / "mod_cover.png",
          REPO_ROOT / "docs" / "img" / "mod" / "cover.png",
          REPO_ROOT / "custom_assets" / game / "cover.png",
      ]
      for c in candidates:
        if c.exists():
          cover_file = c
          break

    if cover_file:
      zf.write(cover_file, arcname="cover.png")
      print(f"  [+] Added cover.png from {cover_file}")

    # 3. custom_assets/<game>/texture_replacements/...
    for png in sorted(png_files):
      rel_path = png.relative_to(REPO_ROOT)
      # Cross-platform forward slashes in zip
      arcname = str(rel_path).replace("\\", "/")
      zf.write(png, arcname=arcname)
      print(f"  [+] Added {arcname}")

  checksum = compute_sha256(output_zip)
  print(f"[+] Archive generated: {output_zip}")
  print(f"[+] SHA256: {checksum}")

  if update_index:
    index_path = REPO_ROOT / "index.json"
    if index_path.exists():
      try:
        with open(index_path, "r", encoding="utf-8") as f:
          catalog = json.load(f)

        if "texturePacks" not in catalog or not isinstance(catalog["texturePacks"], dict):
          catalog["texturePacks"] = {}

        if not release_url_base:
          # Derive release tag from base mod branch or slug
          base_slug = slug.replace("-textures", "")
          release_tag = f"{base_slug}-v{version}"
          release_url_base = f"https://github.com/{owner}/{repo_name}/releases/download/{release_tag}"

        zip_download_url = f"{release_url_base.rstrip('/')}/{output_zip.name}"

        cover_art_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/docs/img/mod/mod_cover.png"
        )
        website_url = f"https://github.com/{owner}/{repo_name}/tree/{branch}"

        catalog["texturePacks"][slug] = {
            "displayName": display_name,
            "description": description,
            "authors": [author],
            "tags": tags,
            "supportedGames": [game],
            "websiteUrl": website_url,
            "coverArtUrl": cover_art_url,
            "thumbnailArtUrl": cover_art_url,
            "versions": [
                {
                    "version": version,
                    "publishedDate": now_iso,
                    "supportedGames": [game],
                    "assets": {
                        "windows": zip_download_url,
                        "linux": zip_download_url,
                        game: zip_download_url,
                    },
                }
            ],
        }
        catalog["lastUpdated"] = now_iso

        with open(index_path, "w", encoding="utf-8") as f:
          json.dump(catalog, f, indent=2, ensure_ascii=False)
          f.write("\n")

        print(f"[+] Successfully updated {index_path} with texture pack '{slug}'")
      except Exception as err:
        print(f"[-] Error updating index.json: {err}")

  return output_zip


def main():
  parser = argparse.ArgumentParser(description="Package OpenGOAL Texture Pack")
  parser.add_argument(
      "--game",
      choices=["jak1", "jak2", "jak3", "jakx"],
      default=None,
      help="Game name (auto-detected from branch or .env if omitted)",
  )
  parser.add_argument(
      "--slug",
      default=None,
      help="Unique texture pack slug (auto-detected from branch if omitted)",
  )
  parser.add_argument(
      "--display-name",
      default=None,
      help="Display name in OpenGOAL Launcher (auto-generated from slug if omitted)",
  )
  parser.add_argument(
      "--description",
      default=None,
      help="Texture pack description",
  )
  parser.add_argument(
      "--author",
      default=None,
      help="Author name (auto-detected from git if omitted)",
  )
  parser.add_argument("--version", default="1.0.0", help="Semantic version")
  parser.add_argument(
      "--tags",
      nargs="+",
      default=None,
      help="Tags list (e.g. --tags jak2 retexture hellcat)",
  )
  parser.add_argument(
      "--cover",
      type=Path,
      default=None,
      help="Path to cover.png thumbnail",
  )
  parser.add_argument(
      "--output",
      type=Path,
      default=None,
      help="Destination .zip file path",
  )
  parser.add_argument(
      "--update-index",
      action="store_true",
      help="Automatically register/update this pack in index.json",
  )
  parser.add_argument(
      "--release-url",
      default=None,
      help="GitHub release download base URL (auto-detected from origin remote if omitted)",
  )

  args = parser.parse_args()

  package_texture_pack(
      game=args.game,
      slug=args.slug,
      display_name=args.display_name,
      description=args.description,
      author=args.author,
      version=args.version,
      tags=args.tags,
      cover_path=args.cover,
      output_zip=args.output,
      update_index=args.update_index,
      release_url_base=args.release_url,
  )


if __name__ == "__main__":
  main()
