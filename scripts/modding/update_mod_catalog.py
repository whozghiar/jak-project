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

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def generate_release_notes(
    output_path: Path,
    branch: str,
    tag: str,
    repo: str,
    checksums_path: Path = None,
    display_name: str = None,
    description: str = None,
):
  """Generates formatted markdown release notes for GitHub Releases."""
  readme_desc = extract_metadata_from_readme(REPO_ROOT / "README.md")
  branch_match = re.match(r"^jak([123])/([^/]+)/(.+)$", branch)
  if branch_match:
    variable_part = branch_match.group(3)
  else:
    parts = branch.split("/")
    variable_part = parts[-1] if len(parts) > 1 else branch

  disp_name = display_name or variable_part
  desc = (
      description
      or readme_desc
      or f"Mod OpenGOAL avec modifications de jeu."
  )

  checksums_content = ""
  if checksums_path and checksums_path.exists():
    try:
      with open(checksums_path, "r", encoding="utf-8", errors="replace") as f:
        checksums_content = f.read().strip()
    except Exception:
      checksums_content = ""

  notes_parts = [
      f"## 🎮 {disp_name} — {tag}",
      "",
      desc,
      "",
      "### 📦 Téléchargements Directs",
      f"- **Windows :** [`windows-{tag}.zip`](https://github.com/{repo}/releases/download/{tag}/windows-{tag}.zip)",
      f"- **Linux :** [`linux-{tag}.zip`](https://github.com/{repo}/releases/download/{tag}/linux-{tag}.zip)",
      "",
      "### 📋 Intégration OpenGOAL Launcher (Custom Mod Source)",
      "Ajoutez ce mod directement dans l'OpenGOAL Launcher via l'URL du catalogue :",
      "```text",
      f"https://raw.githubusercontent.com/{repo}/{branch}/index.json",
      "```",
  ]

  if checksums_content:
    notes_parts.extend([
        "",
        "### 🔒 Checksums de Sécurité (SHA-256)",
        "```text",
        checksums_content,
        "```",
    ])

  output_path.parent.mkdir(parents=True, exist_ok=True)
  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(notes_parts) + "\n")

  print(f"[OK] Generated release notes to {output_path}")


def get_next_version(index_path: Path, mod_slug: str = "") -> str:
  """
  Calculates the next version string formatted as [nom-du-mod]-[version]
  (e.g. 'jak3-jetBoard-v1.0.0', 'jak3-jetBoard-v1.0.1').
  1. Reads index.json for latest version.
  2. Increments patch number if previous version was released with checksums.
  3. Checks git tags to ensure tag uniqueness across repository.
  """
  candidate_major = 1
  candidate_minor = 0
  candidate_patch = 0

  if index_path.exists():
    try:
      with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        mods = data.get("mods", {})
        for mod_key, mod_data in mods.items():
          if mod_key.startswith("temp-sync-"):
            continue
          versions = mod_data.get("versions", [])
          if versions:
            latest_v_str = versions[0].get("version", "")
            win_ck = versions[0].get("checksums", {}).get("windows", "")
            m = re.search(r"(\d+)\.(\d+)\.(\d+)", latest_v_str)
            if m:
              candidate_major = int(m.group(1))
              candidate_minor = int(m.group(2))
              if win_ck:
                candidate_patch = int(m.group(3)) + 1
              else:
                candidate_patch = int(m.group(3))
            break
    except Exception:
      pass

  prefix = f"{mod_slug}-" if mod_slug else ""
  candidate_tag = f"{prefix}v{candidate_major}.{candidate_minor}.{candidate_patch}"

  # Verify against existing git tags
  existing_tags_raw = run_cmd("git tag -l")
  existing_tags = set(t.strip() for t in existing_tags_raw.splitlines() if t.strip())

  while candidate_tag in existing_tags:
    candidate_patch += 1
    candidate_tag = f"{prefix}v{candidate_major}.{candidate_minor}.{candidate_patch}"

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
      help="Release tag (e.g. jak3-jetBoard-v1.0.0 or v1.0.0)",
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
      "--branch",
      default=os.environ.get("GITHUB_REF_NAME"),
      help="Target branch name (e.g. jak2/features/jak3-jetBoard)",
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
  parser.add_argument(
      "--generate-release-notes",
      help="Output file path to generate markdown release notes and exit",
  )
  parser.add_argument(
      "--checksums-file",
      default="",
      help="Path to SHA256SUMS.txt file to include in release notes",
  )
  args = parser.parse_args()

  branch = args.branch or get_current_branch()
  index_path = Path(args.index_file)
  if not index_path.is_absolute():
    index_path = REPO_ROOT / index_path

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

  # Determine tag formatted as [nom-du-mod]-[version]
  tag = args.tag.strip() if args.tag else ""
  if not tag:
    tag = get_next_version(index_path, mod_slug=variable_part)
  else:
    if not tag.startswith(f"{variable_part}-"):
      v_match = re.search(r"v?\d+\.\d+\.\d+", tag)
      ver_str = v_match.group(0) if v_match else tag
      if not ver_str.startswith("v"):
        ver_str = f"v{ver_str}"
      tag = f"{variable_part}-{ver_str}"

  if args.next_version:
    print(tag)
    return

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

  if args.generate_release_notes:
    output_path = Path(args.generate_release_notes)
    if not output_path.is_absolute():
      output_path = REPO_ROOT / output_path

    checksums_path = Path(args.checksums_file) if args.checksums_file else None
    if checksums_path and not checksums_path.is_absolute():
      checksums_path = REPO_ROOT / checksums_path

    generate_release_notes(
        output_path=output_path,
        branch=branch,
        tag=tag,
        repo=args.repo,
        checksums_path=checksums_path,
        display_name=display_name,
        description=description,
    )
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

  ver_match = re.search(r"(\d+\.\d+\.\d+)", tag)
  clean_version = ver_match.group(1) if ver_match else tag.lstrip("v")
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
          if isinstance(catalog["mods"], dict):
            catalog["mods"] = {k: v for k, v in catalog["mods"].items() if not k.startswith("temp-sync-")}
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

  # Remove previous identical version entry, and drop unreleased drafts without checksums
  mod_entry["versions"] = [
      v for v in mod_entry.get("versions", [])
      if v.get("version") != clean_version
      and (v.get("checksums", {}).get("windows") or v.get("checksums", {}).get("linux"))
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
