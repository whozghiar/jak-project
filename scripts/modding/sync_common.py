#!/usr/bin/env python3
"""
Shared rules used by both branch-sync scripts:
    - sync_branches_with_master.py  (CI fan-out: every mod branch, daily cron)
    - sync_branch_with_master_dev.py (local: one branch, run by a developer)

Why this module exists
-----------------------
Both scripts merge `master-dev` into a mod branch and must resolve the same
handful of paths the same way every time (the mod's own README stays the
mod's, the shared docs/skills come from master-dev, stray workflow files are
dropped). Before this module, that rule table was copy-pasted in both
scripts; a rule change made in one and forgotten in the other would silently
desync CI behaviour from local behaviour. Now there is exactly one place to
edit it.

It also carries a tiny helper for building GitHub's own Actions status badge
markdown (see docs.github.com/actions/how-tos/monitor-workflows/add-a-status-badge).
These badges need no rendering or upkeep from Python: GitHub generates the
SVG live from a workflow's real run history, so the sync scripts only ever
need to write this markdown ONCE, at branch-creation time.
"""

import os
from urllib.parse import quote

# Files that make sense only on master-dev. A plain `git merge master-dev`
# would otherwise happily carry them onto every mod branch (they are not in
# conflict, master-dev just added/changed them) — so both sync scripts
# explicitly `git rm` them back out after merging. Keep this list short: it
# is a statement of "this file does not belong on a mod branch", not a
# general-purpose ignore list.
MASTER_DEV_ONLY_PATHS = [
    "docs/modding/tools/branch_sync_status.md",
]

# The only two workflow files a mod branch is meant to carry (see
# classify_conflict_path's "drop" rule below and AGENTS.md for why this fork
# does not mirror upstream's own CI workflows onto every branch).
ALLOWED_MOD_BRANCH_WORKFLOWS = {
    "release.yml",
    "branch-sync-check.yaml",
}


def stray_workflow_files(repo_root):
    """.github/workflows/* files on disk that don't belong on a mod branch.

    classify_conflict_path's "drop" rule only ever runs on paths git reports as
    CONFLICTED. A workflow that master-dev merely *adds* (not yet present on the
    mod branch, so nothing to conflict with) sails through a clean merge untouched
    — silently violating the same policy. Call this after every merge, conflict or
    not, exactly like MASTER_DEV_ONLY_PATHS, so a brand-new master-dev-only
    workflow can never linger on a mod branch just because it happened not to
    collide with anything.
    """
    workflows_dir = os.path.join(repo_root, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        return []
    return [
        f".github/workflows/{name}"
        for name in sorted(os.listdir(workflows_dir))
        if name not in ALLOWED_MOD_BRANCH_WORKFLOWS
        and os.path.isfile(os.path.join(workflows_dir, name))
    ]


def classify_conflict_path(filepath):
    """
    One rule table, one place. Given a path that conflicted (or would
    conflict) while merging master-dev into a mod branch, returns how to
    resolve it:
        "ours"   - keep the mod branch's own version (its README, its Tier-2 docs)
        "theirs" - take master-dev's version (shared guidelines/skills/tools)
        "drop"   - delete it (any workflow file that isn't release.yml or
                   branch-sync-check.yaml — see AGENTS.md for why this fork
                   does not mirror upstream's own CI workflows)
        None     - not a path this project auto-resolves; a real conflict.
    """
    if filepath == "README.md" or filepath.startswith("docs/modding/current_mod/"):
        return "ours"
    if filepath in MASTER_DEV_ONLY_PATHS:
        # Never actually kept on a mod branch: dropping it here handles the
        # rare case where it shows up as a genuine merge conflict; the
        # common case (no conflict, silently carried over) is handled by
        # each script explicitly `git rm`-ing MASTER_DEV_ONLY_PATHS after
        # every merge, conflict or not.
        return "drop"
    if filepath.startswith(".github/workflows/"):
        return "theirs" if filepath[len(".github/workflows/"):] in ALLOWED_MOD_BRANCH_WORKFLOWS else "drop"
    if (filepath == "docs/modding/branch_audit.md"
            or filepath == "AGENTS.md"
            or filepath.startswith(".agents/")
            or filepath.startswith("docs/modding/tools/")):
        return "theirs"
    return None


def is_auto_resolvable(filepath):
    """True if classify_conflict_path() knows how to resolve this path
    deterministically (used by the CI dry-run to tell a real code conflict
    apart from an expected, always-resolved-the-same-way one)."""
    return classify_conflict_path(filepath) is not None


def github_actions_badge_markdown(repo_path, workflow_file, branch=None, alt="Status"):
    """
    Markdown for a native GitHub Actions status badge — the SVG GitHub itself
    renders from a workflow's real run history, not something we compute or
    ever need to refresh by hand:
    https://docs.github.com/actions/how-tos/monitor-workflows/add-a-status-badge

    `branch`, when given, scopes the badge to that branch's own latest run
    (`?branch=`) — this is what lets each mod branch's README show whether
    *that* branch, specifically, last passed `branch-sync-check.yaml`.
    """
    base = f"https://github.com/{repo_path}/actions/workflows/{workflow_file}"
    badge_url, link_url = f"{base}/badge.svg", base
    if branch:
        encoded = quote(branch, safe="")
        badge_url += f"?branch={encoded}"
        link_url += f"?query=branch%3A{encoded}"
    return f"[![{alt}]({badge_url})]({link_url})"
