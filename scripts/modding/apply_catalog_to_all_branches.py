#!/usr/bin/env python3
"""
Applies updated catalog (index.json) with branch-variable displayName,
README overview description, and v1.0.0 base version across all 17 mod branches,
and pushes the changes to origin.
"""

import os
from pathlib import Path
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]

BRANCHES = [
    'jak2/config/enhanced_spawnrates',
    'jak2/config/start_menu_wheel',
    'jak2/features/crimson-blueguard/city-insurrection',
    'jak2/features/crimson-blueguard/crimson-redguard-behavior',
    'jak2/features/crimson-blueguard/peaceful',
    'jak2/features/dark_jak_enhanced',
    'jak2/features/haven-city-chaos',
    'jak2/features/jak3-jetBoard',
    'jak2/features/paddywagon/traffic',
    'jak2/features/transport-ag/alert',
    'jak2/features/transport-ag/traffic',
    'jak2/features/yakow_killable',
    'jak3/config/memory_increase',
    'jak3/features/city-behavior',
    'jak3/features/jak2_skin_secret',
    'jak3/features/mega_dark_jak',
    'jak3/features/redguard-entity'
]

def run(cmd: str, check: bool = True) -> str:
  print(f">> {cmd}")
  res = subprocess.run(
      cmd,
      shell=True,
      text=True,
      capture_output=True,
      cwd=REPO_ROOT,
      check=False,
  )
  if res.stdout.strip():
    print(res.stdout.strip())
  if res.returncode != 0:
    if res.stderr.strip():
      print(f"ERROR: {res.stderr.strip()}", file=sys.stderr)
    if check:
      sys.exit(res.returncode)
  return res.stdout.strip()

def main():
  print(f"=== Applying index.json to {len(BRANCHES)} Mod Branches ===")
  run("git checkout master-dev")
  run("git pull origin master-dev")

  for i, b in enumerate(BRANCHES, 1):
    print(f"\n[{i}/{len(BRANCHES)}] Processing {b}...")
    run(f"git checkout {b}")
    run(f"git merge origin/master-dev --no-edit", check=False)
    
    # Auto-resolve documentation & release workflows
    unmerged = run("git diff --name-only --diff-filter=U", check=False).splitlines()
    for f in unmerged:
      f = f.strip()
      if not f:
        continue
      if f == "README.md" or f.startswith("docs/modding/current_mod/"):
        run(f'git checkout HEAD -- "{f}"', check=False)
        run(f'git add "{f}"', check=False)
      elif f == ".github/workflows/release.yml" or f == "docs/modding/branch_audit.md" or f.startswith("docs/modding/tools/") or f == "AGENTS.md" or f.startswith(".agents/"):
        run(f'git checkout MERGE_HEAD -- "{f}"', check=False)
        run(f'git add "{f}"', check=False)
      elif f.startswith(".github/workflows/"):
        run(f'git rm -rf "{f}"', check=False)

    # Ensure mod README is preserved
    run('git checkout HEAD -- README.md', check=False)
    run('git add README.md', check=False)

    # Generate clean index.json
    run(f'python scripts/modding/update_mod_catalog.py --branch "{b}" --tag v1.0.0')
    run("git add index.json")

    # Check if anything changed
    diff_check = subprocess.run("git diff --cached --quiet", shell=True, cwd=REPO_ROOT).returncode != 0
    if diff_check:
      commit_msg = (
          f"chore(catalog): configure index.json with branch variable displayName and README overview\n\n"
          f"- Integration of updated release CI workflow (.github/workflows/release.yml)\n"
          f"  with semantic auto-increment (v1.0.0 -> v1.0.1), variable branch display name,\n"
          f"  and automatic README overview extraction.\n"
          f"- Creation of index.json catalog for 1-click install via OpenGOAL Launcher raw.githubusercontent.\n"
          f"- Integration of latest engine fixes and Jak 3 Debug > Mods registry.\n\n"
          f"(AI-assisted)"
      )
      # Escape quotes for shell or write commit message via git commit -F
      msg_file = REPO_ROOT / ".git" / "COMMIT_EDITMSG_TEMP"
      with open(msg_file, "w", encoding="utf-8") as mf:
        mf.write(commit_msg)
      run(f'git commit -F "{msg_file}"')
      if msg_file.exists():
        msg_file.unlink()

      # Push to origin
      run(f"git push origin {b}")
      print(f"[OK] Successfully committed and pushed {b}!")
    else:
      print(f"[OK] Branch {b} is already completely up to date.")

  run("git checkout master-dev")
  print("\n🎉 All 17 branches successfully synchronized and updated with accurate index.json!")

if __name__ == "__main__":
  main()
