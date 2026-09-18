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
    'jak2/features/blue-krimzon-guard',
    'jak2/features/dark_jak_enhanced',
    'jak2/features/haven-city-chaos',
    'jak2/features/haven-city-rebellion',
    'jak2/features/jak3-jetBoard',
    'jak2/features/killable_yakow',
    'jak2/features/paddywagon/traffic',
    'jak2/features/peaceful-haven-city',
    'jak2/features/transport-ag/alert',
    'jak2/features/transport-ag/traffic',
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

    # If there is an unresolved merge or staged changes, commit
    diff_check = subprocess.run("git diff --cached --quiet", shell=True, cwd=REPO_ROOT).returncode != 0
    if diff_check:
      commit_msg = (
          f"fix(ci): strictly manual workflow_dispatch and valid release workflow syntax\n\n"
          f"- Workflow triggers restricted to workflow_dispatch only (never triggers on push/commit)\n"
          f"- Fixed line 378 YAML indentation syntax error\n"
          f"- Synchronized latest release scripts from master-dev\n\n"
          f"(AI-assisted)"
      )
      msg_file = REPO_ROOT / ".git" / "COMMIT_EDITMSG_TEMP"
      with open(msg_file, "w", encoding="utf-8") as mf:
        mf.write(commit_msg)
      run(f'git commit -F "{msg_file}"')
      if msg_file.exists():
        msg_file.unlink()

    # Check if local branch is ahead of origin
    local_rev = run(f"git rev-parse HEAD", check=False)
    remote_rev = run(f"git rev-parse origin/{b}", check=False)
    if local_rev != remote_rev:
      run(f"git push origin {b}")
      print(f"[OK] Successfully pushed {b} to origin!")
    else:
      print(f"[OK] Branch {b} is already completely up to date on origin.")

  run("git checkout master-dev")
  print("\n🎉 All 17 branches successfully synchronized and updated with accurate index.json!")

if __name__ == "__main__":
  main()
