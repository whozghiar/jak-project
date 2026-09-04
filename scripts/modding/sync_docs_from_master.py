#!/usr/bin/env python3
"""
Utility script to synchronize modding documentation and guidelines
from origin/master-dev into the current working branch.

Usage:
    python scripts/modding/sync_docs_from_master.py           # Sync docs into working tree (unstaged/staged)
    python scripts/modding/sync_docs_from_master.py --commit  # Sync docs and commit immediately
    python scripts/modding/sync_docs_from_master.py --rebase  # Rebase current branch on origin/master-dev
"""

import argparse
import subprocess
import sys

def run_cmd(cmd, check=True):
    print(f">> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res

def main():
    parser = argparse.ArgumentParser(description="Synchronize modding documentation from master-dev.")
    parser.add_argument("--commit", action="store_true", help="Automatically commit updated documentation.")
    parser.add_argument("--rebase", action="store_true", help="Rebase entire branch on origin/master-dev.")
    args = parser.parse_args()

    print("Fetching latest changes from origin/master-dev...")
    run_cmd("git fetch origin master-dev")

    if args.rebase:
        print("Rebasing current branch on origin/master-dev...")
        run_cmd("git rebase origin/master-dev")
        print("Successfully rebased current branch on origin/master-dev.")
        return

    print("Updating docs/modding, AGENTS.md, and CLAUDE.md from origin/master-dev...")
    run_cmd("git checkout origin/master-dev -- docs/modding AGENTS.md CLAUDE.md")

    status_res = run_cmd("git status --porcelain docs/modding AGENTS.md CLAUDE.md", check=False)
    if not status_res.stdout.strip():
        print("Documentation is already fully up-to-date with origin/master-dev. No changes made.")
        return

    if args.commit:
        run_cmd("git add docs/modding AGENTS.md CLAUDE.md")
        run_cmd('git commit -m "docs: sync modding documentation from master-dev (AI-assisted)"')
        print("Successfully committed updated documentation.")
    else:
        print("Documentation files updated in your working tree.")
        print("You can review changes and commit them whenever you are ready:")
        print("    git add docs/modding AGENTS.md CLAUDE.md")
        print('    git commit -m "docs: sync modding documentation (AI-assisted)"')

if __name__ == "__main__":
    main()
