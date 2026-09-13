#!/usr/bin/env python3
"""
Automated catalog generator and updater for OpenGOAL mod distribution.
Compliant with OpenGOAL Launcher Mod Source Schema v1:
https://github.com/open-goal/launcher/tree/main/schemas/mod-source/v1

Usage:
    python scripts/modding/update_mod_catalog.py
    python scripts/modding/update_mod_catalog.py --tag v1.0.0 --repo whozghiar/jak-project
    python scripts/modding/update_mod_catalog.py --next-version
    python scripts/modding/update_mod_catalog.py --print-metadata
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
  """Extract overview description from mod's root README.md without AI mentions."""
  description = None

  if not readme_path.exists():
    return description

  try:
    with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
      content = f.read()

    # Extract overview section if present
    desc_match = re.search(
        r"##\s+(?:📖\s+)?(?:Overview|Présentation du Mod)\s*\n+([\s\S]*?)(?=\n\s*(?:- \*\*Target Game|##|---|\Z))",
        content,
        re.MULTILINE,
    )
    if desc_match:
      raw_desc = desc_match.group(1).strip()
      cleaned_lines = []
      for line in raw_desc.splitlines():
        line_s = line.strip()
        if not line_s:
          continue
        if line_s.startswith("-") or line_s.startswith("*") or line_s.startswith("<") or line_s.startswith("!["):
          continue
        cleaned_lines.append(line_s)
      if cleaned_lines:
        candidate = " ".join(cleaned_lines)
        # Strip AI disclosure or badges from description
        candidate = re.sub(r"\s*\(AI-assisted[^)]*\)", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*\(AI--assisted[^)]*\)", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"AI--assisted-Modding-[^.\s]+\.svg", "", candidate)
        description = candidate.strip()
  except Exception as err:
    print(f"Warning: Failed to parse README.md: {err}", file=sys.stderr)

  return description


def get_next_version(index_path: Path) -> str:
  """
  Calculates the next version string (e.g. 'v1.0.0', 'v1.0.1', 'v1.0.2').
  1. Reads index.json for latest version.
  2. Increments patch number.
  3. Checks git tags to ensure tag uniqueness.
  """
  candidate_major = 1
  candidate_minor = 0
  candidate_patch = 0

  if index_path.exists():
    try:
      with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        mods = data.get("mods", {})
        for mod_data in mods.values():
          versions = mod_data.get("versions", [])
          if versions:
            latest_v_str = versions[0].get("version", "")
            m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", latest_v_str)
            if m:
              candidate_major = int(m.group(1))
              candidate_minor = int(m.group(2))
              candidate_patch = int(m.group(3)) + 1
            break
    except Exception:
      pass

  candidate_tag = f"v{candidate_major}.{candidate_minor}.{candidate_patch}"

  # Verify against existing git tags
  existing_tags_raw = run_cmd("git tag -l")
  existing_tags = set(t.strip() for t in existing_tags_raw.splitlines() if t.strip())

  while candidate_tag in existing_tags:
    candidate_patch += 1
    candidate_tag = f"v{candidate_major}.{candidate_minor}.{candidate_patch}"

  return candidate_tag


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
      default=os.environ.get("RELEASE_TAG") or os.environ.get("TAG", ""),
      help="Release tag (e.g. v1.0.0)",
  )
  parser.add_argument(
      "--repo",
      default=os.environ.get("GITHUB_REPOSITORY")
      or os.environ.get("REPO", "whozghiar/jak-project"),
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
      help="User-friendly display name (defaults to variable branch part)",
  )
  parser.add_argument(
      "--description",
      default=os.environ.get("DESCRIPTION"),
      help="Mod description (defaults to Overview in README.md)",
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
  parser.add_argument(
      "--next-version",
      action="store_true",
      help="Print calculated next version tag and exit",
  )
  parser.add_argument(
      "--print-metadata",
      action="store_true",
      help="Print release metadata JSON (tag, display_name, description) and exit",
  )
  args = parser.parse_args()

  branch = get_current_branch()
  index_path = Path(args.index_file)
  if not index_path.is_absolute():
    index_path = REPO_ROOT / index_path

  if args.next_version:
    print(get_next_version(index_path))
    return

  readme_desc = extract_metadata_from_readme(REPO_ROOT / "README.md")

  # Determine target game and variable part of branch
  # Formats: jak[123]/[category]/[variable_part...]
  detected_game = "jak2"
  branch_match = re.match(r"^jak([123])/([^/]+)/(.+)$", branch)
  if branch_match:
    game_num = branch_match.group(1)
    detected_game = f"jak{game_num}"
    variable_part = branch_match.group(3)
    detected_slug = variable_part.replace("/", "-").replace("_", "-")
  else:
    parts = branch.split("/")
    variable_part = parts[-1] if len(parts) > 1 else branch
    detected_slug = branch.replace("/", "-").replace("_", "-")

  # Rule: Display name MUST ALWAYS be the variable part of the branch
  display_name = args.display_name or variable_part

  # Rule: Description MUST be the same as mod's general README Overview
  description = (
      args.description
      or readme_desc
      or f"Mod OpenGOAL {detected_game.upper()} avec modifications C++ et LISP."
  )

  # Determine tag
  tag = args.tag.strip() if args.tag else ""
  if not tag:
    tag = get_next_version(index_path)

  if args.print_metadata:
    meta = {
        "tag": tag,
        "display_name": display_name,
        "description": description,
        "game": detected_game,
        "branch": branch,
    }
    print(json.dumps(meta, ensure_ascii=False))
    return

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

  clean_version = tag.lstrip("v")
  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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

  catalog["sourceName"] = f"{display_name} Source"
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

  print(f"[OK] Successfully wrote catalog to {index_path}")
  print(f"     Display Name: {display_name}")
  print(f"     Description : {description[:80]}...")
  print(f"     Version     : {clean_version} ({tag})")


if __name__ == "__main__":
  main()
