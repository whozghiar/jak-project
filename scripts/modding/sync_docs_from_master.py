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

SYNCED_PATHS = [".agents", "docs/README.md", "AGENTS.md", "CLAUDE.md"]


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


def get_current_branch():
    res = run_cmd("git rev-parse --abbrev-ref HEAD", check=False)
    return res.stdout.strip() if res.returncode == 0 else ""


def main():
    parser = argparse.ArgumentParser(description="Synchronize modding documentation from master-dev.")
    parser.add_argument("--commit", action="store_true", help="Automatically commit the synced documentation.")
    parser.add_argument("--rebase", action="store_true", help="Rebase the whole branch on origin/master-dev instead.")
    parser.add_argument("--source", default="origin/master-dev", help="Source ref to sync from (default: origin/master-dev).")
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch.")
    args = parser.parse_args()

    source_ref = args.source
    if not args.no_fetch and source_ref.startswith("origin/"):
        print(f"Fetching latest changes from origin for {source_ref.replace('origin/', '')}...")
        run_cmd(f"git fetch origin {source_ref.replace('origin/', '')}", check=False)

    # Fallback to local master-dev if origin ref does not exist
    verify = run_cmd(f"git rev-parse --verify --quiet {source_ref}", check=False)
    if verify.returncode != 0:
        if source_ref == "origin/master-dev":
            source_ref = "master-dev"
            print(f"Falling back to local '{source_ref}'...")
        else:
            print(f"Error: Ref '{source_ref}' not found.", file=sys.stderr)
            sys.exit(1)

    if args.rebase:
        print(f"Rebasing current branch on {source_ref}...")
        run_cmd(f"git rebase {source_ref}")
        print(f"Successfully rebased current branch on {source_ref}.")
        return

    current_branch = get_current_branch()

    # 1. Pull master-dev's version of root paths into the working tree
    print(f"Updating {', '.join(SYNCED_PATHS)} from {source_ref}...")
    run_cmd(f"git checkout {source_ref} -- {' '.join(SYNCED_PATHS)}")

    # 2. Synchronize docs/modding files selectively:
    #    Protect current_mod/ so mod-specific readmes and images are never overwritten
    #    or deleted, and do not copy other mods' readmes over.
    master_modding_files = tracked_files(source_ref, "docs/modding")
    files_to_checkout = []
    for f in master_modding_files:
        if f.startswith("docs/modding/current_mod/"):
            # Only sync the general directory README.md guide, unless on the specific branch
            if f == "docs/modding/current_mod/README.md":
                files_to_checkout.append(f)
            elif current_branch == "jak2/config/custom_animation_and_sound" and f.endswith("custom_animation_and_sound_readme.md"):
                files_to_checkout.append(f)
        else:
            files_to_checkout.append(f)

    if files_to_checkout:
        print(f"Updating {len(files_to_checkout)} docs/modding file(s) from {source_ref}...")
        run_cmd(f"git checkout {source_ref} -- " + " ".join(f'"{f}"' for f in files_to_checkout))

    # 3. Prune: anything under docs/modding/ that master-dev no longer tracks,
    #    BUT NEVER prune anything inside docs/modding/current_mod/!
    here = tracked_files("HEAD", "docs/modding")
    stale = sorted(f for f in (here - master_modding_files) if not f.startswith("docs/modding/current_mod/"))
    if stale:
        print(f"Pruning {len(stale)} obsolete file(s) removed on {source_ref}:")
        for f in stale:
            print(f"  - {f}")
        run_cmd("git rm -q -- " + " ".join(f'"{f}"' for f in stale))

    status_res = run_cmd("git status --porcelain .agents docs AGENTS.md CLAUDE.md", check=False)
    if not status_res.stdout.strip():
        print(f"Documentation is already fully up-to-date with {source_ref}. No changes made.")
        return

    if args.commit:
        run_cmd("git add .agents docs AGENTS.md CLAUDE.md")
        run_cmd('git commit -m "docs: sync modding documentation from master-dev (AI-assisted)"')
        print("Successfully committed the synced documentation.")
    else:
        print("Documentation files updated in your working tree.")
        print("Review, then commit when ready:")
        print("    git add .agents docs AGENTS.md CLAUDE.md")
        print('    git commit -m "docs: sync modding documentation from master-dev (AI-assisted)"')


if __name__ == "__main__":
    main()
