#!/usr/bin/env python3
"""
Synchronize modding documentation and agent guidance from origin/master-dev into
the current working branch, WITHOUT rebasing or pulling in unrelated changes.

What it syncs:
    - docs/modding/**   (the whole modding docs tree)
    - .agents/**        (modular skills and memory discoveries)
    - AGENTS.md, CLAUDE.md  (agent guidance kept in lockstep with the docs)

It also PRUNES: files that no longer exist under docs/modding/ on master-dev are
removed from the working branch too. This is what lets a docs refactor on
master-dev (e.g. deleting the old jak[x]_modding_utilities/ trees) actually land
on every mod branch instead of lingering forever.

Usage:
    python scripts/modding/sync_docs_from_master.py           # update working tree
    python scripts/modding/sync_docs_from_master.py --commit   # update + commit
    python scripts/modding/sync_docs_from_master.py --rebase    # rebase branch on origin/master-dev instead
"""

import argparse
import subprocess
import sys

SYNCED_PATHS = [".agents", "docs/modding", "AGENTS.md", "CLAUDE.md"]


def run_cmd(cmd, check=True):
    print(f">> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True,
                         encoding="utf-8", errors="replace")
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res


def tracked_files(ref, path):
    """Set of file paths tracked at `ref` under `path`."""
    res = run_cmd(f'git ls-tree -r --name-only {ref} -- {path}', check=False)
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def main():
    parser = argparse.ArgumentParser(description="Synchronize modding documentation from master-dev.")
    parser.add_argument("--commit", action="store_true", help="Automatically commit the synced documentation.")
    parser.add_argument("--rebase", action="store_true", help="Rebase the whole branch on origin/master-dev instead.")
    args = parser.parse_args()

    print("Fetching latest changes from origin/master-dev...")
    run_cmd("git fetch origin master-dev")

    if args.rebase:
        print("Rebasing current branch on origin/master-dev...")
        run_cmd("git rebase origin/master-dev")
        print("Successfully rebased current branch on origin/master-dev.")
        return

    # 1. Pull master-dev's version of every synced path into the working tree.
    print(f"Updating {', '.join(SYNCED_PATHS)} from origin/master-dev...")
    run_cmd(f"git checkout origin/master-dev -- {' '.join(SYNCED_PATHS)}")

    # 2. Prune: anything under docs/modding/ that master-dev no longer tracks.
    here = tracked_files("HEAD", "docs/modding")
    there = tracked_files("origin/master-dev", "docs/modding")
    stale = sorted(here - there)
    if stale:
        print(f"Pruning {len(stale)} file(s) removed on master-dev:")
        for f in stale:
            print(f"  - {f}")
        run_cmd("git rm -q -- " + " ".join(f'"{f}"' for f in stale))

    status_res = run_cmd(f"git status --porcelain {' '.join(SYNCED_PATHS)}", check=False)
    if not status_res.stdout.strip():
        print("Documentation is already fully up-to-date with origin/master-dev. No changes made.")
        return

    if args.commit:
        run_cmd(f"git add {' '.join(SYNCED_PATHS)}")
        run_cmd('git commit -m "docs: sync modding documentation from master-dev (AI-assisted)"')
        print("Successfully committed the synced documentation.")
    else:
        print("Documentation files updated in your working tree.")
        print("Review, then commit when ready:")
        print(f"    git add {' '.join(SYNCED_PATHS)}")
        print('    git commit -m "docs: sync modding documentation from master-dev (AI-assisted)"')


if __name__ == "__main__":
    main()
