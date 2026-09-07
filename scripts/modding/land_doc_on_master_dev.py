#!/usr/bin/env python3
"""
Land a modding-doc change on master-dev WITHOUT creating merge conflicts on any
mod branch.

Why this exists
---------------
`docs/modding/*_lisp_instructions.md` and `docs/modding/engine_generic_concepts.md`
have exactly one source of truth: **master-dev**. Editing them on a mod branch and
merging later is what produced constant conflicts. Instead, a discovery made while
modding is "landed" straight onto master-dev as a tiny dedicated commit, then
pulled back into the mod branch with `sync_docs_from_master.py`.

This script does that round-trip for you:

    current branch  ──(carry the doc edit)──►  master-dev  ──commit/push──►
    ──►  back to your branch  ──►  sync_docs_from_master.py

Usage
-----
    # 1. On your mod branch, edit the doc file(s) — append your verified block
    #    below the "APPEND NEW VERIFIED ENTRIES" marker.
    # 2. Run:
    python scripts/modding/land_doc_on_master_dev.py \
        --file docs/modding/jak2_lisp_instructions.md \
        --message "jak2: send-event stack message block" --push

Rules enforced
--------------
- Every --file must live under docs/modding/.
- Your working tree must be clean apart from the --file(s) (commit/stash the rest).
- Your branch's version of each --file must be master-dev's version PLUS a clean
  addition (that is what "append-only" buys you). If the diff does not apply onto
  the latest master-dev, the script aborts and tells you to sync docs first.
"""

import argparse
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def run(cmd, check=True, capture=True):
    print(f">> {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=capture, cwd=REPO_ROOT,
                         encoding="utf-8", errors="replace")
    if capture and res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res


def current_branch():
    return run("git rev-parse --abbrev-ref HEAD", check=False).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description="Land a modding-doc change on master-dev conflict-free.")
    ap.add_argument("--file", action="append", required=True, metavar="PATH",
                    help="Doc file under docs/modding/ to carry over (repeatable).")
    ap.add_argument("--message", required=True, help="Short summary for the commit subject.")
    ap.add_argument("--push", action="store_true", help="Push master-dev after committing.")
    ap.add_argument("--source", default="master-dev", help="Canonical branch (default: master-dev).")
    args = ap.parse_args()

    files = [f.replace("\\", "/").strip() for f in args.file]
    for f in files:
        if not f.startswith("docs/modding/"):
            sys.exit(f"Refusing: {f} is not under docs/modding/.")
        if not os.path.isfile(os.path.join(REPO_ROOT, f)):
            sys.exit(f"Refusing: {f} does not exist.")

    branch = current_branch()
    if not branch or branch in ("HEAD", args.source):
        sys.exit(f"Run this from your mod branch, not '{branch}'.")

    # Working tree must be clean apart from the target files.
    dirty = run("git status --porcelain", check=False).stdout.splitlines()
    dirty_other = [ln for ln in dirty if ln[3:].strip() not in files]
    if dirty_other:
        print("Working tree has changes outside the doc file(s):", file=sys.stderr)
        print("\n".join(dirty_other), file=sys.stderr)
        sys.exit("Commit or stash those first.")

    run(f"git fetch origin {args.source}")

    # Capture the addition as a patch relative to the latest canonical branch.
    patch = run(f'git diff origin/{args.source} -- {" ".join(files)}', check=False).stdout
    if not patch.strip():
        sys.exit("No difference against origin/%s for those files — nothing to land." % args.source)

    fd, patch_path = tempfile.mkstemp(suffix=".patch")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(patch)

    stashed = False
    try:
        if any(ln[3:].strip() in files for ln in dirty):
            run("git stash push -u -m land-doc-autostash -- " + " ".join(f'"{f}"' for f in files))
            stashed = True

        run(f"git checkout {args.source}")
        run(f"git merge --ff-only origin/{args.source}")

        check = run(f'git apply --check "{patch_path}"', check=False)
        if check.returncode != 0:
            run(f"git checkout {branch}")
            if stashed:
                run("git stash pop")
            sys.exit(
                "Your doc edit does not apply cleanly onto the latest %s.\n"
                "Run `python scripts/modding/sync_docs_from_master.py` on your branch,\n"
                "re-append your block, then try again." % args.source
            )
        run(f'git apply "{patch_path}"')
        run("git add " + " ".join(f'"{f}"' for f in files))
        run(f'git commit -m "docs: {args.message} (AI-assisted)"')
        if args.push:
            run(f"git push origin {args.source}")
        else:
            print(f"\nCommitted to local {args.source}. Push it when ready: git push origin {args.source}")
    finally:
        os.unlink(patch_path)
        if current_branch() != branch:
            run(f"git checkout {branch}", check=False)
        if stashed:
            run("git stash pop", check=False)

    print("\nPulling the canonical doc back into your branch...")
    run(f'"{sys.executable}" scripts/modding/sync_docs_from_master.py', check=False)
    print("\nDone. Your branch now carries the master-dev version of the doc.")


if __name__ == "__main__":
    main()
