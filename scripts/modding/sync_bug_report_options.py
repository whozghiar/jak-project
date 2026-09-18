#!/usr/bin/env python3
"""
Regenerates the "Mod Concerned" dropdown in .github/ISSUE_TEMPLATE/mod-bug-report.yml
from the repository's actual published GitHub Releases — not from committed index.json
files, which can carry a real-looking checksummed version even when no GitHub Release
was ever actually published (a local/dry run, a release later deleted, ...). A release
is the only place a player can actually download the mod from, so it's the only
trustworthy signal that a mod is "out there" and reportable.

For each release (skipping drafts; pre-releases count — they're still published), the
mod's display name and game are read straight out of its release notes, which
scripts/modding/update_mod_catalog.py --generate-release-notes always writes in the form:

    ## 🎮 <Display Name> — <tag>
    ...
    <img src="https://raw.githubusercontent.com/<repo>/jak<N>/<category>/<branch>/docs/img/mod/mod_cover.png" ...>

Releases whose notes don't match that shape (not produced by this project's release
pipeline) are skipped with a warning rather than guessed at.

Usage:
    python scripts/modding/sync_bug_report_options.py
    python scripts/modding/sync_bug_report_options.py --repo whozghiar/jak-project --dry-run
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATE_FILE = os.path.join(REPO_ROOT, ".github", "ISSUE_TEMPLATE", "mod-bug-report.yml")

BEGIN_MARKER = "# BEGIN GENERATED — scripts/modding/sync_bug_report_options.py (do not edit by hand)"
END_MARKER = "# END GENERATED"

TITLE_RE = re.compile(r"^##\s*\S+\s*(.+?)\s*—\s*\S+\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/(jak([123])/.+?)/docs/")


def get_token() -> str:
  return (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()


def fetch_json(url: str, token: str):
  req = urllib.request.Request(
      url,
      headers={
          "Accept": "application/vnd.github+json",
          "User-Agent": "OpenGOAL-Modding-BugReportSync",
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
      print(f"Error fetching releases (page {page}): {err}", file=sys.stderr)
      break
    if not batch:
      break
    releases.extend(batch)
    if len(batch) < 100:
      break
    page += 1
  return releases


def released_mods(releases):
  """Dedupe by branch, keeping each mod's most recently published release."""
  mods = {}
  skipped = []

  for rel in releases:
    if rel.get("draft"):
      continue

    body = rel.get("body") or ""
    title_match = TITLE_RE.search(body)
    branch_match = BRANCH_RE.search(body)

    if not title_match or not branch_match:
      skipped.append(rel.get("tag_name", "?"))
      continue

    display_name = title_match.group(1).strip()
    branch = branch_match.group(1)
    game = f"jak{branch_match.group(2)}"
    published_at = rel.get("published_at") or ""

    existing = mods.get(branch)
    if existing is None or published_at > existing["published_at"]:
      mods[branch] = {
          "game": game,
          "display_name": display_name,
          "branch": branch,
          "published_at": published_at,
          "tag": rel.get("tag_name", ""),
      }

  return mods, skipped


def render_options(mods):
  game_order = {"jak1": 0, "jak2": 1, "jak3": 2}
  ordered = sorted(
      mods.values(),
      key=lambda m: (game_order.get(m["game"], 9), m["display_name"].lower()),
  )
  lines = []
  for m in ordered:
    tag = m["game"].replace("jak", "Jak ")
    name = m["display_name"].replace('"', '\\"')
    lines.append(f'        - "[{tag}] {name}"')
  return lines


def apply_to_file(path: str, generated_lines, dry_run: bool) -> bool:
  with open(path, "r", encoding="utf-8") as f:
    original_lines = f.readlines()

  begin_idx = end_idx = None
  for i, line in enumerate(original_lines):
    if BEGIN_MARKER in line:
      begin_idx = i
    elif END_MARKER in line and begin_idx is not None:
      end_idx = i
      break

  if begin_idx is None or end_idx is None:
    print(
        f"Error: could not find '{BEGIN_MARKER}' / '{END_MARKER}' markers in {path}",
        file=sys.stderr,
    )
    sys.exit(1)

  new_lines = (
      original_lines[: begin_idx + 1]
      + [line + "\n" for line in generated_lines]
      + original_lines[end_idx:]
  )

  if new_lines == original_lines:
    print("[OK] Dropdown already up to date — no change.")
    return False

  print("--- Generated options ---")
  for line in generated_lines:
    print(line)
  print("-------------------------")

  if dry_run:
    print(f"(dry-run) Would update {path}")
    return True

  with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
  print(f"[OK] Updated {path}")
  return True


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--repo",
      default=os.environ.get("GITHUB_REPOSITORY", "whozghiar/jak-project"),
      help="GitHub repository owner/repo to read releases from",
  )
  parser.add_argument(
      "--file",
      default=TEMPLATE_FILE,
      help="Path to mod-bug-report.yml to regenerate",
  )
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Print what would change without writing the file",
  )
  args = parser.parse_args()

  token = get_token()
  print(f"Fetching published releases for {args.repo}...")
  releases = fetch_all_releases(args.repo, token)
  mods, skipped = released_mods(releases)

  print(f"Found {len(releases)} release(s) total; {len(mods)} distinct released mod(s).")
  if skipped:
    print(f"Skipped {len(skipped)} release(s) with non-standard notes: {', '.join(skipped)}")

  generated_lines = render_options(mods)
  changed = apply_to_file(args.file, generated_lines, args.dry_run)
  sys.exit(2 if (args.dry_run and changed) else 0)


if __name__ == "__main__":
  main()
