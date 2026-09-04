#!/usr/bin/env python3
"""
Synchronize a mod branch with master-dev.

By default, this script uses `git merge` (safe, non-destructive, preserves commit SHAs
for published branches). It also offers an explicit `--rebase` option for developers
who prefer a linear commit history on unshared/local branches.

Usage:
    python scripts/modding/sync_branch_with_master_dev.py                # Merge master-dev into current branch
    python scripts/modding/sync_branch_with_master_dev.py --rebase       # Rebase current branch onto master-dev
    python scripts/modding/sync_branch_with_master_dev.py --push         # Merge and push to origin
    python scripts/modding/sync_branch_with_master_dev.py --branch jak2/features/foo  # Target specific branch
"""

import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def run_cmd(cmd, check=True, capture=True):
    print(f">> Running: {cmd}")
    res = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=capture,
        cwd=REPO_ROOT,
        encoding="utf-8",
        errors="replace"
    )
    if res.stdout and capture:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res

def get_current_branch():
    res = run_cmd("git rev-parse --abbrev-ref HEAD", check=False)
    if res.returncode == 0:
        return res.stdout.strip()
    return None

def is_working_tree_clean():
    res = run_cmd("git status --porcelain", check=False)
    return len(res.stdout.strip()) == 0

def is_ancestor(ancestor_ref, target_ref):
    res = run_cmd(f"git merge-base --is-ancestor {ancestor_ref} {target_ref}", check=False)
    return res.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description="Synchronize the current (or specified) branch with origin/master-dev."
    )
    parser.add_argument(
        "--branch",
        help="Target branch to synchronize (defaults to currently active branch)."
    )
    parser.add_argument(
        "--rebase",
        action="store_true",
        help="Use 'git rebase' instead of 'git merge' (rewrites commit history, use with caution on published branches)."
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Automatically push the synchronized branch to origin after success."
    )
    parser.add_argument(
        "--source",
        default="master-dev",
        help="Source base branch to synchronize from (default: master-dev)."
    )
    args = parser.parse_args()

    # Determine target branch
    target_branch = args.branch.strip() if args.branch else get_current_branch()
    if not target_branch or target_branch == "HEAD":
        print("Error: Could not determine current branch. Please specify with --branch <name>.", file=sys.stderr)
        sys.exit(1)

    source_branch = args.source.strip()
    source_ref = f"origin/{source_branch}"

    if target_branch == source_branch:
        print(f"Error: Target branch cannot be the source base branch '{source_branch}'.", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== Synchronizing Branch with {source_branch} ===")
    print(f"Target Branch: {target_branch}")
    print(f"Source Base  : {source_ref}")
    print(f"Strategy     : {'REBASE (linear history)' if args.rebase else 'MERGE (safe, preserves SHAs)'}")

    # Check cleanliness
    if not is_working_tree_clean():
        print("\nError: Working tree has uncommitted modifications.", file=sys.stderr)
        print("Please commit or stash your changes before synchronizing:", file=sys.stderr)
        print("    git stash", file=sys.stderr)
        sys.exit(1)

    # Fetch source
    print(f"\nFetching latest {source_ref}...")
    run_cmd(f"git fetch origin {source_branch}")

    # Switch to target branch if not already on it
    current_branch = get_current_branch()
    if current_branch != target_branch:
        print(f"\nChecking out {target_branch}...")
        run_cmd(f"git checkout {target_branch}")

    # Check if already up to date
    if is_ancestor(source_ref, "HEAD"):
        print(f"\n[OK] Branch '{target_branch}' is already fully up-to-date with {source_ref}!")
        return

    if args.rebase:
        print(f"\nRebasing {target_branch} onto {source_ref}...")
        rebase_res = run_cmd(f"git rebase {source_ref}", check=False)
        if rebase_res.returncode != 0:
            print("\n⚠️ Conflict encountered during rebase!", file=sys.stderr)
            print("To resolve conflicts:", file=sys.stderr)
            print("  1. Resolve conflicted files in your editor.")
            print("  2. git add <resolved_files>")
            print("  3. git rebase --continue")
            print("Or abort with: git rebase --abort")
            sys.exit(rebase_res.returncode)
        print(f"\n[OK] Successfully rebased {target_branch} onto {source_ref}!")
        if args.push:
            print(f"\nPushing (force-with-lease) {target_branch} to origin...")
            run_cmd(f"git push --force-with-lease origin {target_branch}")
            print(f"[OK] Pushed to origin/{target_branch} successfully.")
    else:
        print(f"\nMerging {source_ref} into {target_branch}...")
        commit_msg = f"chore: sync {target_branch} with latest {source_branch} (AI-assisted)"
        merge_res = run_cmd(f'git merge {source_ref} -m "{commit_msg}"', check=False)
        if merge_res.returncode != 0:
            print("\n⚠️ Conflict encountered during merge!", file=sys.stderr)
            print("To resolve conflicts:", file=sys.stderr)
            print("  1. Resolve conflicted files in your editor.")
            print("  2. git commit -m \"fix: resolve merge conflicts with master-dev (AI-assisted)\"")
            print("Or abort with: git merge --abort")
            sys.exit(merge_res.returncode)
        print(f"\n[OK] Successfully merged {source_ref} into {target_branch}!")
        if args.push:
            print(f"\nPusshing {target_branch} to origin...")
            run_cmd(f"git push origin {target_branch}")
            print(f"[OK] Pushed to origin/{target_branch} successfully.")

    print(f"\nSynchronization completed successfully!")

if __name__ == "__main__":
    main()
