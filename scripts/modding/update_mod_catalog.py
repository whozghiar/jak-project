#!/usr/bin/env python3
"""
Automated catalog generator and updater for OpenGOAL mod distribution.
Compliant with OpenGOAL Launcher Mod Source Schema v1:
https://github.com/open-goal/launcher/tree/main/schemas/mod-source/v1

Usage:
    python scripts/modding/update_mod_catalog.py
    python scripts/modding/update_mod_catalog.py --tag v1.0.0 --repo user/repo
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cmd(cmd: str) -> str:
  try:
    res = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
        check=False,
    )
    return res.stdout.strip()
  except Exception:
    return ""


def get_current_branch() -> str:
  branch = os.environ.get("GITHUB_REF_NAME") or run_cmd(
      "git rev-parse --abbrev-ref HEAD"
  )
  return branch if branch else "master-dev"


def extract_metadata_from_readme(readme_path: Path):
  """Extract display name and overview description from mod's root README.md."""
  display_name = None
  description = None

  if not readme_path.exists():
    return display_name, description

  try:
    with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
      content = f.read()

    # Extract title from first markdown H1, ignoring language headers like '# 🇬🇧 English Version'
    for line in content.splitlines():
      line_str = line.strip()
      if line_str.startswith("# ") and "Version" not in line_str and "OpenGOAL" not in line_str:
        raw_title = line_str.lstrip("# ").strip()
        # Split at '—' or '-' if it contains game name
        if "—" in raw_title:
          display_name = raw_title.split("—")[0].strip()
        elif " - " in raw_title:
          display_name = raw_title.split(" - ")[0].strip()
        else:
          display_name = raw_title
        break

    # Extract overview section if present
    desc_match = re.search(
        r"##\s+(?:📖\s+)?(?:Overview|Présentation du Mod)\s*\n+([^#\n\r][^\n\r]+)",
        content,
        re.MULTILINE,
    )
    if desc_match:
      candidate = desc_match.group(1).strip()
      if not candidate.startswith("-") and not candidate.startswith("*"):
        description = candidate
  except Exception as err:
    print(f"Warning: Failed to parse README.md: {err}", file=sys.stderr)

  return display_name, description


def main():
  parser = argparse.ArgumentParser(
      description="Update or create an OpenGOAL mod-source index.json catalog."
  )
  parser.add_argument(
      "--index-file",
      default=os.environ.get("INDEX_FILE", "index.json"),
      help="Path to index.json output file",
  )
  parser.add_argument(
      "--tag",
      default=os.environ.get("RELEASE_TAG") or os.environ.get("TAG", "v0.1.0"),
      help="Release tag (e.g. v1.0.0)",
  )
  parser.add_argument(
      "--repo",
      default=os.environ.get("GITHUB_REPOSITORY")
      or os.environ.get("REPO", "open-goal/jak-project"),
      help="GitHub repository owner/repo",
  )
  parser.add_argument(
      "--mod-id",
      default=os.environ.get("MOD_ID"),
      help="Mod unique slug identifier",
  )
  parser.add_argument(
      "--display-name",
      default=os.environ.get("DISPLAY_NAME"),
      help="User-friendly display name",
  )
  parser.add_argument(
      "--authors",
      default=os.environ.get("AUTHORS"),
      help="Comma-separated authors list",
  )
  parser.add_argument(
      "--supported-games",
      default=os.environ.get("SUPPORTED_GAMES"),
      help="Comma-separated games: jak1, jak2, jak3",
  )
  parser.add_argument(
      "--win-sha",
      default=os.environ.get("WIN_SHA", ""),
      help="Windows archive SHA-256",
  )
  parser.add_argument(
      "--lin-sha",
      default=os.environ.get("LIN_SHA", ""),
      help="Linux archive SHA-256",
  )
  args = parser.parse_args()

  branch = get_current_branch()
  readme_title, readme_desc = extract_metadata_from_readme(
      REPO_ROOT / "README.md"
  )

  # Determine target game from branch (e.g. jak2/features/foo -> jak2)
  detected_game = "jak2"
  branch_match = re.match(r"^jak([123])/([^/]+)/(.+)$", branch)
  if branch_match:
    game_num = branch_match.group(1)
    detected_game = f"jak{game_num}"
    detected_slug = branch_match.group(3).replace("_", "-")
  else:
    detected_slug = branch.replace("/", "-").replace("_", "-")

  mod_id = args.mod_id or detected_slug
  supported_games = (
      [g.strip() for g in args.supported_games.split(",") if g.strip()]
      if args.supported_games
      else [detected_game]
  )
  authors = (
      [a.strip() for a in args.authors.split(",") if a.strip()]
      if args.authors
      else [args.repo.split("/")[0]]
  )
  display_name = (
      args.display_name
      or readme_title
      or f"{mod_id.replace('-', ' ').title()} ({detected_game.upper()})"
  )
  description = (
      readme_desc
      or f"Mod OpenGOAL {detected_game.upper()} avec modifications C++ et LISP."
  )

  tag = args.tag.strip()
  clean_version = tag.lstrip("v")
  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

  index_path = Path(args.index_file)
  if not index_path.is_absolute():
    index_path = REPO_ROOT / index_path

  catalog = {
      "schemaVersion": "1.0.0",
      "sourceName": f"{display_name} Source",
      "lastUpdated": now_iso,
      "mods": {},
      "texturePacks": {},
  }

  if index_path.exists():
    try:
      with open(index_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
        if isinstance(loaded, dict) and "mods" in loaded:
          catalog = loaded
    except Exception as err:
      print(
          f"Warning: Could not read existing index.json, creating a fresh one: {err}"
      )

  catalog["lastUpdated"] = now_iso

  # Base download URLs from GitHub Releases
  base_url = f"https://github.com/{args.repo}/releases/download/{tag}"
  win_url = f"{base_url}/windows-{tag}.zip"
  lin_url = f"{base_url}/linux-{tag}.zip"

  if mod_id not in catalog["mods"]:
    catalog["mods"][mod_id] = {
        "displayName": display_name,
        "description": description,
        "authors": authors,
        "tags": ["gameplay", "custom-engine"],
        "supportedGames": supported_games,
        "websiteUrl": f"https://github.com/{args.repo}/tree/{branch}",
        "versions": [],
    }

  mod_entry = catalog["mods"][mod_id]
  mod_entry["displayName"] = display_name
  mod_entry["description"] = description
  mod_entry["supportedGames"] = supported_games

  new_version = {
      "version": clean_version,
      "publishedDate": now_iso,
      "supportedGames": supported_games,
      "assets": {
          "windows": win_url,
          "linux": lin_url,
      },
      "checksums": {
          "windows": args.win_sha,
          "linux": args.lin_sha,
      },
  }

  # Remove previous identical version entry if updating
  mod_entry["versions"] = [
      v for v in mod_entry.get("versions", []) if v.get("version") != clean_version
  ]
  mod_entry["versions"].insert(0, new_version)

  index_path.parent.mkdir(parents=True, exist_ok=True)
  with open(index_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)
    f.write("\n")

  print(f"[OK] Successfully wrote mod catalog to {index_path}")
  print(f"     Mod ID      : {mod_id}")
  print(f"     Version     : {clean_version}")
  print(f"     Target Games: {', '.join(supported_games)}")
  print(f"     Windows URL : {win_url}")
  print(f"     Linux URL   : {lin_url}")


if __name__ == "__main__":
  main()
