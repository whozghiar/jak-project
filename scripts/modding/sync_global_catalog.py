#!/usr/bin/env python3
"""
Aggregates all published mod releases into a unified global catalog (index.json)
at the repository root on master-dev.
Compliant with OpenGOAL Launcher Mod Source Schema v1:
https://github.com/open-goal/launcher/tree/main/schemas/mod-source/v1

This enables players to add a SINGLE catalog URL in the OpenGOAL Launcher:
    https://raw.githubusercontent.com/<user>/<repo>/master-dev/index.json
to see and install ALL published mods from this repository.

Usage:
    python scripts/modding/sync_global_catalog.py
    python scripts/modding/sync_global_catalog.py --repo whozghiar/jak-project
    python scripts/modding/sync_global_catalog.py --offline
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_NAME = "Whozghiar OpenGOAL Mods Hub"


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


def get_default_repo() -> str:
  url = run_cmd("git config --get remote.origin.url")
  match = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", url)
  if match:
    return match.group(1)
  return "whozghiar/jak-project"


def get_token() -> str:
  return (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()


def fetch_json(url: str, token: str):
  req = urllib.request.Request(
      url,
      headers={
          "Accept": "application/vnd.github+json",
          "User-Agent": "OpenGOAL-GlobalCatalogSync",
          **({"Authorization": f"Bearer {token}"} if token else {}),
      },
  )
  with urllib.request.urlopen(req, timeout=20) as resp:
    return json.loads(resp.read().decode("utf-8"))


def fetch_all_releases(repo: str, token: str):
  releases = []
  page = 1
  while True:
    url = f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}"
    try:
      batch = fetch_json(url, token)
    except urllib.error.HTTPError as err:
      print(f"Warning: HTTP {err.code} fetching releases (page {page}): {err}", file=sys.stderr)
      break
    except Exception as err:
      print(f"Warning: Failed to fetch releases: {err}", file=sys.stderr)
      break
    if not batch:
      break
    releases.extend(batch)
    if len(batch) < 100:
      break
    page += 1
  return releases


TITLE_RE = re.compile(r"^##\s*\S+\s*(.+?)\s*—\s*\S+\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/(jak([123])/.+?)/docs/")


def load_catalog_from_release_asset(rel, token: str):
  """Attempts to load index.json attached as an asset of the release."""
  for asset in rel.get("assets", []):
    if asset.get("name") == "index.json":
      url = asset.get("browser_download_url")
      if url:
        try:
          return fetch_json(url, token)
        except Exception as e:
          print(f"  Warning: failed to download index.json asset from {rel.get('tag_name')}: {e}", file=sys.stderr)
  return None


def collect_mods_from_releases(repo: str, token: str):
  """Collects published mods by inspecting GitHub Releases and their index.json assets."""
  print(f"Fetching published releases for {repo}...")
  releases = fetch_all_releases(repo, token)
  print(f"Found {len(releases)} release(s). Processing catalogs...")

  aggregated_mods = {}

  for rel in sorted(releases, key=lambda r: r.get("published_at") or ""):
    if rel.get("draft"):
      continue

    tag = rel.get("tag_name", "")
    body = rel.get("body") or ""
    branch_match = BRANCH_RE.search(body)
    canonical_slug = None
    if branch_match:
      branch_path = branch_match.group(1)
      m = re.match(r"^jak[123]/(?:features|config)/(.+)$", branch_path)
      if m:
        canonical_slug = m.group(1).replace("/", "-").replace("_", "-")
      else:
        canonical_slug = branch_path.split("/")[-1].replace("_", "-")

    data = load_catalog_from_release_asset(rel, token)

    if data and "mods" in data:
      for mod_key, mod_info in data["mods"].items():
        # Use canonical slug from current branch if available to prevent obsolete key divergence
        target_key = canonical_slug or mod_key

        if target_key not in aggregated_mods:
          aggregated_mods[target_key] = mod_info
        else:
          # Merge metadata with newest release, and combine versions
          existing_versions = {v.get("version"): v for v in aggregated_mods[target_key].get("versions", [])}
          for v in mod_info.get("versions", []):
            ver_num = v.get("version")
            if ver_num and ver_num not in existing_versions:
              aggregated_mods[target_key].setdefault("versions", []).append(v)
          # Update metadata if newer
          for attr in ["displayName", "description", "coverArtUrl", "thumbnailArtUrl", "websiteUrl"]:
            if mod_info.get(attr):
              aggregated_mods[target_key][attr] = mod_info[attr]

      print(f"  ✓ {tag}: loaded via release asset")
    else:
      print(f"  - {tag}: no index.json asset found, skipping")

  return aggregated_mods


def collect_mods_from_branches():
  """Offline fallback: collects index.json from all origin/jak* mod branches."""
  print("Collecting index.json from local/remote mod branches (offline mode)...")
  branches_output = run_cmd("git branch -r")
  branches = [
      b.strip()
      for b in branches_output.splitlines()
      if "origin/jak" in b and "HEAD" not in b
  ]

  aggregated_mods = {}
  for b in sorted(branches):
    cat_res = run_cmd(f"git show {b}:index.json")
    if cat_res.strip():
      try:
        data = json.loads(cat_res)
        for mod_key, mod_info in data.get("mods", {}).items():
          if mod_info.get("versions"):
            if mod_key not in aggregated_mods:
              aggregated_mods[mod_key] = mod_info
            else:
              existing_versions = {v.get("version"): v for v in aggregated_mods[mod_key].get("versions", [])}
              for v in mod_info.get("versions", []):
                ver_num = v.get("version")
                if ver_num and ver_num not in existing_versions:
                  aggregated_mods[mod_key].setdefault("versions", []).append(v)
      except Exception as e:
        print(f"Warning: could not parse index.json on {b}: {e}", file=sys.stderr)

  return aggregated_mods


def generate_global_catalog(mods, source_name: str):
  """Builds the final OpenGOAL Launcher Mod Source Schema v1 document."""
  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
  
  # Sort mods alphabetically by displayName
  sorted_mods = {}
  for k in sorted(mods.keys(), key=lambda x: (mods[x].get("displayName") or x).lower()):
    mod_info = dict(mods[k])
    # Sort versions newest to oldest
    if "versions" in mod_info and isinstance(mod_info["versions"], list):
      mod_info["versions"] = sorted(
          mod_info["versions"],
          key=lambda v: v.get("publishedDate") or "",
          reverse=True
      )
    sorted_mods[k] = mod_info

  return {
      "schemaVersion": "1.0.0",
      "sourceName": source_name,
      "lastUpdated": now_iso,
      "mods": sorted_mods,
      "texturePacks": {}
  }


def main():
  parser = argparse.ArgumentParser(
      description="Generate or sync the master-dev global index.json catalog for OpenGOAL Launcher."
  )
  parser.add_argument(
      "--repo",
      default=get_default_repo(),
      help="GitHub repository in 'owner/repo' format (default: auto-detect)",
  )
  parser.add_argument(
      "--output",
      type=Path,
      default=REPO_ROOT / "index.json",
      help="Path to write index.json (default: <repo_root>/index.json)",
  )
  parser.add_argument(
      "--source-name",
      default=DEFAULT_SOURCE_NAME,
      help=f"Display sourceName in Launcher (default: '{DEFAULT_SOURCE_NAME}')",
  )
  parser.add_argument(
      "--offline",
      action="store_true",
      help="Force collecting only from branch index.json without GitHub API calls",
  )
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Print summary without modifying index.json file",
  )

  args = parser.parse_args()
  token = get_token()

  mods = {}
  if not args.offline:
    try:
      mods = collect_mods_from_releases(args.repo, token)
    except Exception as e:
      print(f"Error connecting to GitHub API: {e}. Falling back to branch inspection.", file=sys.stderr)
      mods = {}

  if not mods:
    print("Falling back to scanning git mod branches...")
    mods = collect_mods_from_branches()

  print(f"\nTotal distinct published mods found: {len(mods)}")
  for k, v in mods.items():
    v_count = len(v.get("versions", []))
    name = v.get("displayName", k)
    game = (v.get("supportedGames") or ["?"])[0]
    print(f"  • [{game}] {name} ({k}) — {v_count} version(s)")

  catalog = generate_global_catalog(mods, args.source_name)
  catalog_json = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"

  if args.dry_run:
    print("\n[Dry Run] Generated index.json preview:")
    print(catalog_json[:600] + "...\n")
    return

  args.output.parent.mkdir(parents=True, exist_ok=True)
  with open(args.output, "w", encoding="utf-8") as f:
    f.write(catalog_json)

  print(f"\n[OK] Successfully wrote global catalog to {args.output}")


if __name__ == "__main__":
  main()
