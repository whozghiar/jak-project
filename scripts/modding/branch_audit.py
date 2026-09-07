#!/usr/bin/env python3
"""
Audit every mod branch against the refactored modding standards and write
docs/modding/branch_audit.md.

Read-only: it never checks out or modifies a branch. It inspects `origin/jak*`
refs with `git ls-tree` / `git grep` / `git diff` and produces a report a human
(or an agent, later) can work through branch by branch.

Checks per branch (vs origin/master-dev):
  1. Obsolete docs/modding/jak[x]_modding_utilities/ tree still present?
  2. Directly edits engine/pc debug menu files (default-menu*.gc)? (now an anti-pattern)
  3. Registers a Debug > Mods toggle (`mods-menu-register`)?
  4. Which goal_src/** files it changes (native-regression surface).
  5. Root README.md present and customised (not the raw template)?

Usage:
    python scripts/modding/branch_audit.py
    python scripts/modding/branch_audit.py --no-fetch
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_FILE = os.path.join(REPO_ROOT, "docs", "modding", "branch_audit.md")
BASE = "origin/master-dev"


def run(cmd, check=False):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=REPO_ROOT,
                          encoding="utf-8", errors="replace")


def mod_branches():
    """Union of local and origin jak* branches. Local-only branches (unpushed WIP)
    are audited against their local ref; the rest against origin/."""
    out = set()
    for line in run('git branch -r --list "origin/jak*"').stdout.splitlines():
        b = line.strip()
        if b and not b.endswith("/HEAD") and b.startswith("origin/"):
            out.add(b[len("origin/"):])
    for line in run('git for-each-ref --format=%(refname:short) refs/heads/').stdout.splitlines():
        b = line.strip()
        if re.match(r"jak[123]/", b):
            out.add(b)
    return sorted(out)


def branch_ref(branch):
    """Prefer origin/<branch>; fall back to the local ref for unpushed branches."""
    if run(f"git rev-parse --verify --quiet origin/{branch}").returncode == 0:
        return f"origin/{branch}", False
    return branch, True


def ls_tree(ref, path):
    res = run(f'git ls-tree -r --name-only {ref} -- {path}')
    return [l.strip() for l in res.stdout.splitlines() if l.strip()]


def changed_files(ref, path):
    res = run(f'git diff --name-only {BASE}...{ref} -- {path}')
    return [l.strip() for l in res.stdout.splitlines() if l.strip()]


def grep_ref(ref, pattern, path):
    res = run(f'git grep -l -e "{pattern}" {ref} -- {path}')
    return [l.split(":", 1)[-1].strip() for l in res.stdout.splitlines() if l.strip()]


def audit_branch(branch):
    ref, local_only = branch_ref(branch)
    game = re.match(r"(jak[123])/", branch)
    game = game.group(1) if game else "?"

    old_utils = [f for f in ls_tree(ref, "docs/modding")
                 if re.search(r"jak[123]_modding_utilities/", f)]

    engine_changes = changed_files(ref, "goal_src")
    menu_edits = [f for f in engine_changes
                  if re.search(r"debug/(default-menu|menu)", f) or f.endswith("mods-menu.gc")]
    menu_edits = [f for f in menu_edits if not f.endswith("mods-menu.gc")]

    has_toggle = bool(grep_ref(ref, "mods-menu-register", "goal_src"))

    readme = run(f"git show {ref}:README.md")
    readme_text = readme.stdout or ""
    readme_ok = readme.returncode == 0 and "{MOD_TITLE}" not in readme_text
    readme_state = "customised" if readme_ok else ("raw template" if readme.returncode == 0 else "missing")

    todos = []
    if old_utils:
        todos.append(f"Remove obsolete `jak[x]_modding_utilities/` ({len(old_utils)} files) — "
                     f"`git merge master-dev` then `git rm` any modify/delete conflicts.")
    if menu_edits:
        todos.append("Move debug toggles off shared menu files "
                     f"({', '.join('`'+m+'`' for m in menu_edits)}) into a `mods-menu-register` submenu.")
    if not has_toggle and game == "jak2":
        todos.append("Add a Debug ▸ Mods toggle via `mods-menu-register` (see `docs/modding/tools/mods_debug_menu.md`).")
    if not has_toggle and game in ("jak1", "jak3"):
        todos.append("Add a mod-slug-prefixed debug submenu; port to `mods-menu-register` once the "
                     f"{game} framework lands.")
    if engine_changes:
        todos.append(f"Confirm native non-regression: {len(engine_changes)} `goal_src/**` file(s) changed — "
                     "each behaviour change must be OFF by default, behind the mod toggle.")
    if readme_state != "customised":
        todos.append(f"Root README.md is {readme_state} — fill in from `docs/modding/templates/MOD_README.template.md`.")
    if not todos:
        todos.append("No action — compliant.")

    return {
        "branch": branch,
        "local_only": local_only,
        "game": game,
        "old_utils": len(old_utils),
        "menu_edits": len(menu_edits),
        "toggle": has_toggle,
        "engine_changes": engine_changes,
        "readme": readme_state,
        "todos": todos,
    }


def render(rows):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    md = []
    md.append("# 🔍 Mod Branch Compliance Audit / Audit de Conformité des Branches de Mods\n")
    md.append(f"> **Generated / Généré :** `{now}` · **Base :** `{BASE}`")
    md.append(">")
    md.append("> 🇬🇧 Generated by `scripts/modding/branch_audit.py`. Read-only snapshot. "
              "Work through each branch's TODO list, then re-run.")
    md.append("> 🇫🇷 Généré par `scripts/modding/branch_audit.py`. Instantané en lecture seule. "
              "Traiter la liste TODO de chaque branche, puis relancer.\n")
    md.append("_🟡 = local-only branch (not yet pushed to origin)._\n")
    md.append("| Branch | Game | Old KB files | Direct menu edits | Mods toggle | `goal_src` files changed | README |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for r in rows:
        md.append("| `{branch}`{lo} | {game} | {old} | {menu} | {tog} | {eng} | {rme} |".format(
            branch=r["branch"], lo=" 🟡" if r["local_only"] else "", game=r["game"],
            old=("⚠️ " + str(r["old_utils"])) if r["old_utils"] else "✅ 0",
            menu=("⚠️ " + str(r["menu_edits"])) if r["menu_edits"] else "✅ 0",
            tog="✅" if r["toggle"] else "❌",
            eng=len(r["engine_changes"]),
            rme={"customised": "✅", "raw template": "⚠️", "missing": "❌"}[r["readme"]],
        ))
    md.append("\n---\n")
    md.append("## Per-branch TODOs / TODO par branche\n")
    for r in rows:
        md.append(f"### `{r['branch']}`\n")
        for t in r["todos"]:
            md.append(f"- [ ] {t}")
        if r["engine_changes"]:
            preview = r["engine_changes"][:12]
            md.append("\n<details><summary>changed <code>goal_src</code> files</summary>\n")
            for f in preview:
                md.append(f"- `{f}`")
            if len(r["engine_changes"]) > len(preview):
                md.append(f"- … +{len(r['engine_changes']) - len(preview)} more")
            md.append("\n</details>")
        md.append("")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="Skip `git fetch origin`.")
    args = ap.parse_args()

    if not args.no_fetch:
        print("Fetching origin...")
        run("git fetch origin --prune")

    branches = mod_branches()
    if not branches:
        sys.exit("No origin/jak* branches found.")
    print(f"Auditing {len(branches)} branches...")
    rows = [audit_branch(b) for b in branches]

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(rows))
    print(f"Wrote {os.path.relpath(OUT_FILE, REPO_ROOT)}")


if __name__ == "__main__":
    main()
