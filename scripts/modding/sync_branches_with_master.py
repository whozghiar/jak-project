#!/usr/bin/env python3
"""
Automated synchronization script for Jak modding branches.
Tests mergeability against a source branch (default: origin/master) using in-memory `git merge-tree`,
optionally merges clean branches, and generates a live markdown dashboard of branch sync statuses.

Where the sync status actually lives (two different granularities, on purpose):
    - The full, all-branches dashboard (docs/modding/tools/branch_sync_status.md) is
      master-dev-only (see sync_common.MASTER_DEV_ONLY_PATHS): it is never carried onto
      a mod branch, and master-dev's own root README.md only shows GitHub's native
      status badge for THIS workflow, linking here for the branch-by-branch detail.
    - Each mod branch instead carries its own native GitHub Actions status badge for
      .github/workflows/branch-sync-check.yaml (?branch=<it>), written once into its
      README.md at creation time (create_mod_branch.py). This script does not touch
      that badge at all: pushing a successful merge to a branch is exactly what makes
      branch-sync-check.yaml run and go green — GitHub renders the badge live from
      that run history, nothing here needs to keep it in sync.

Usage:
    python scripts/modding/sync_branches_with_master.py           # Test and update dashboard without pushing
    python scripts/modding/sync_branches_with_master.py --push    # Merge clean branches, push, and update dashboard
    python scripts/modding/sync_branches_with_master.py --source master-dev  # Use master-dev as source
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

import sync_common

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DASHBOARD_FILE = os.path.join(REPO_ROOT, "docs", "modding", "tools", "branch_sync_status.md")
HISTORY_LOG_FILE = os.path.join(REPO_ROOT, "docs", "modding", "tools", "branch_sync_history.md")

EVENT_LOGS = []

def log_event(event_type, branch, details):
    """Buffer a structured log entry."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    icon_map = {
        "CONFLICT": "⚠️ Conflit",
        "AUTO-MERGE": "🔄 Auto-fusion",
        "RESOLVED": "✅ Conflit Résolu",
        "ERROR": "❌ Erreur"
    }
    event_label = icon_map.get(event_type, event_type)
    line = f"| `{timestamp}` | {event_label} | `{branch}` | {details} |"
    print(f"  [LOG] {event_type} - {branch}: {details}")
    EVENT_LOGS.append(line)

def flush_event_logs():
    """Write all buffered log entries to persistent history file."""
    if not EVENT_LOGS:
        return
    os.makedirs(os.path.dirname(HISTORY_LOG_FILE), exist_ok=True)
    if not os.path.isfile(HISTORY_LOG_FILE):
        with open(HISTORY_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📜 Historique des Synchronisations des Branches / Branch Sync History\n\n")
            f.write("| Date (UTC) | Événement | Branche | Détails |\n")
            f.write("| :--- | :---: | :--- | :--- |\n")
    with open(HISTORY_LOG_FILE, "a", encoding="utf-8") as f:
        for line in EVENT_LOGS:
            f.write(line + "\n")

def get_previous_statuses():
    """Parse previous branch statuses from existing branch_sync_status.md if available."""
    prev = {}
    if os.path.isfile(DASHBOARD_FILE):
        with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|\s*`([^`]+)`", line)
                if m:
                    prev[m.group(1).strip()] = {
                        "status": m.group(2).strip(),
                        "commit": m.group(3).strip()
                    }
    return prev

def run_cmd(cmd, check=False):
    res = subprocess.run(
        cmd, shell=True, text=True, capture_output=True, cwd=REPO_ROOT, encoding="utf-8", errors="replace"
    )
    return res

def get_remote_branches():
    """Retrieve all remote branches matching origin/jak*"""
    run_cmd("git fetch origin")
    res = run_cmd('git branch -r --list "origin/jak*"')
    branches = []
    for line in res.stdout.splitlines():
        branch = line.strip()
        if branch and not branch.endswith("/HEAD") and branch.startswith("origin/"):
            branches.append(branch.replace("origin/", ""))
    return sorted(branches)

def get_commit_info(ref):
    """Retrieve short SHA and commit message for a ref."""
    res = run_cmd(f'git log -1 --format="%h - %s" {ref}')
    return res.stdout.strip() if res.returncode == 0 else "N/A"

def check_ancestor(ancestor, branch):
    """Check if ancestor is already merged into branch."""
    res = run_cmd(f"git merge-base --is-ancestor {ancestor} {branch}")
    return res.returncode == 0

def is_working_tree_clean():
    """Check if local git working tree has uncommitted modifications."""
    res = run_cmd("git status --porcelain")
    return len(res.stdout.strip()) == 0

def test_merge_tree(source_ref, branch_ref):
    """
    Test merge in memory with git merge-tree --write-tree.
    Returns (clean: bool, real_conflicts: list, all_conflicts: list, raw_output: str)
    """
    res = run_cmd(f"git merge-tree --write-tree {source_ref} {branch_ref}")
    if res.returncode == 0:
        return True, [], [], res.stdout
    
    # Extract conflicting files
    conflicts = []
    for line in (res.stdout + "\n" + res.stderr).splitlines():
        match = re.search(r"CONFLICT \(.*?\): Merge conflict in (.*)", line)
        if match:
            conflicts.append(match.group(1).strip())
    
    if not conflicts:
        for line in (res.stdout + "\n" + res.stderr).splitlines():
            if "CONFLICT" in line:
                m2 = re.search(r"CONFLICT \(.*?\):\s*(.*?)\s+(?:deleted|modified|renamed)", line)
                if m2:
                    conflicts.append(m2.group(1).strip())
                else:
                    conflicts.append(line.strip())
                
    conflicts = list(dict.fromkeys(conflicts))
    real_conflicts = [f for f in conflicts if not sync_common.is_auto_resolvable(f)]
    # Clean if there are no real code conflicts
    clean = (len(real_conflicts) == 0)
    return clean, real_conflicts, conflicts, res.stdout

def merge_and_push_branch(branch, source_ref):
    """Perform actual merge on a temporary ref and push to remote, auto-resolving mod doc conflicts."""
    temp_branch = f"temp-sync-{branch.replace('/', '-')}"
    try:
        checkout_res = run_cmd(f"git checkout -B {temp_branch} origin/{branch}")
        if checkout_res.returncode != 0:
            err = (checkout_res.stderr or checkout_res.stdout).strip()
            return False, f"Échec checkout: {err[:120]}"

        merge_res = run_cmd(f'git merge {source_ref} --no-commit')
        if merge_res.returncode != 0:
            unmerged = [l.strip() for l in run_cmd("git diff --name-only --diff-filter=U").stdout.splitlines() if l.strip()]
            for f in unmerged:
                action = sync_common.classify_conflict_path(f)
                if action == "ours":
                    run_cmd(f'git checkout HEAD -- "{f}"')
                    run_cmd(f'git add "{f}"')
                elif action == "theirs":
                    run_cmd(f'git checkout MERGE_HEAD -- "{f}"')
                    run_cmd(f'git add "{f}"')
                elif action == "drop":
                    run_cmd(f'git rm -rf "{f}"')

            # Verify if any real code conflict remains
            remaining = [l.strip() for l in run_cmd("git diff --name-only --diff-filter=U").stdout.splitlines() if l.strip()]
            if remaining:
                run_cmd("git merge --abort")
                return False, f"Vrais conflits de code: {', '.join(remaining)}"

        # CRITICAL: Always ensure mod's root README.md is strictly preserved from HEAD
        # (prevents Git 3-way merge from silently splicing master-dev's dashboard/hub into mod's README)
        run_cmd('git checkout HEAD -- README.md')

        # master-dev-only files (e.g. the all-branches sync dashboard) ride along on a
        # clean, no-conflict merge too since git has no reason to flag them — strip them
        # back out so they never linger on a mod branch.
        for mdo_path in sync_common.MASTER_DEV_ONLY_PATHS:
            if os.path.isfile(os.path.join(REPO_ROOT, mdo_path)):
                run_cmd(f'git rm -f -q "{mdo_path}"')
        run_cmd('git add README.md')

        # No README badge to stamp here: each mod branch's "synced with master-dev?"
        # badge is a native GitHub Actions status badge (.github/workflows/branch-sync-check.yaml,
        # written once into the README at branch creation by create_mod_branch.py). This
        # very push is what makes that badge go green — GitHub renders it live from the
        # workflow run it triggers, nothing here needs to touch the README to update it.

        # Refresh index.json's display metadata only — a routine sync is not a release,
        # so it must never fabricate a draft versions[] entry (see update_mod_catalog.py's
        # refresh_metadata_only: that used to happen here every single day).
        run_cmd(f'python "{os.path.join(REPO_ROOT, "scripts", "modding", "update_mod_catalog.py")}" --branch "{branch}" --metadata-only')
        run_cmd('git add index.json')

        commit_msg = (
            f"chore(sync): align {branch} with latest {source_ref}\n\n"
            f"- Integration of updated release CI workflow (.github/workflows/release.yml)\n"
            f"  with semantic auto-increment (v1.0.0 -> v1.0.1), variable branch display name,\n"
            f"  and automatic README overview extraction.\n"
            f"- Creation of index.json catalog for 1-click install via OpenGOAL Launcher raw.githubusercontent.\n"
            f"- Integration of latest engine fixes and Jak 3 Debug > Mods registry.\n\n"
            f"(AI-assisted)"
        )
        run_cmd(f'git commit -m "{commit_msg}"')
        
        push_res = run_cmd(f"git push origin {temp_branch}:{branch}")
        if push_res.returncode != 0:
            err = (push_res.stderr or push_res.stdout).strip()
            return False, f"Échec git push: {err[:120]}"

        # Also update local branch pointer if it exists
        local_check = run_cmd(f"git show-ref --verify --quiet refs/heads/{branch}")
        if local_check.returncode == 0:
            run_cmd(f"git branch -f {branch} {temp_branch}")

        return True, "Fusionnée et poussée avec succès"
    finally:
        run_cmd("git checkout master-dev")
        run_cmd(f"git branch -D {temp_branch}")

def generate_dashboard(results, source_ref, source_sha, updated_at):
    """Generate Markdown dashboard file."""
    total = len(results)
    # "Prête à fusionner" (dry-run, no --push) is just as "in sync" as "À jour" or
    # "Synchronisée" (post-push) — only a real, unresolved conflict should count against
    # the summary badge. Counting just the first two under-reported the true number and
    # would have made the new summary badge lie about how healthy the fleet of branches is.
    synced_count = sum(
        1 for r in results
        if "À jour" in r["status"] or "Synchronisée" in r["status"] or "Prête à fusionner" in r["status"]
    )
    conflict_count = sum(1 for r in results if "Conflit" in r["status"])

    md = []
    md.append("# 📊 État de Synchronisation des Branches de Mods")
    md.append("")
    md.append("> **Fichier réservé à `master-dev`.** Ce dashboard n'est jamais propagé sur les")
    md.append("> branches de mods (voir `sync_common.MASTER_DEV_ONLY_PATHS`) : chaque branche")
    md.append("> porte seulement son propre badge de synchro dans son `README.md`.")
    md.append("")
    md.append(f"> **Dernière mise à jour :** `{updated_at}`  ")
    md.append(f"> **Branche source :** `{source_ref}` (`{source_sha}`)  ")
    md.append(f"> **Statut global :** {synced_count}/{total} synchronisées ({conflict_count} conflits)")
    md.append("")
    md.append("| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |")
    md.append("| :--- | :---: | :--- | :--- | :--- |")

    for r in results:
        branch_code = f"`{r['branch']}`"
        status = r["status"]
        last_commit = f"`{r['last_commit']}`"
        
        if r["conflicts"]:
            conflicts_fmt = "<br>".join([f"• `{f}`" for f in r["conflicts"]])
        else:
            conflicts_fmt = r.get("details", "Aucun")

        if "Conflit" in status:
            res_cmd = f"`git checkout {r['branch']} && git merge origin/{source_ref}`"
        else:
            res_cmd = "—"

        md.append(f"| {branch_code} | {status} | {last_commit} | {conflicts_fmt} | {res_cmd} |")

    md.append("")
    md.append("---")
    md.append("### Guide de Résolution des Conflits")
    md.append("Lorsqu'une branche affiche un conflit :")
    md.append("1. Basculez sur la branche en local : `git checkout <branche>`")
    md.append(f"2. Récupérez les modifications de la source : `git merge origin/{source_ref}`")
    md.append("3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.")
    md.append("4. Testez la compilation (`task build-release`).")
    md.append("5. Commitez et poussez votre résolution : `git commit -m \"fix: resolve merge conflicts with master (AI-assisted)\" && git push`")
    md.append("")
    md.append("*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*")
    md.append("")
    new_content = "\n".join(md)

    # The "Dernière mise à jour" timestamp changes on literally every run, even when
    # nothing else did — writing (and thus committing) the file on that basis alone
    # produces a meaningless commit every single day forever. Compare content with
    # that one line stripped out first, and skip the write entirely if nothing else
    # moved, so `git status` (and the cron's commit step) sees no diff to act on.
    def _without_timestamp(text):
        return re.sub(r"^> \*\*Dernière mise à jour :\*\*.*$", "", text, flags=re.MULTILINE)

    previous_content = ""
    if os.path.isfile(DASHBOARD_FILE):
        with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
            previous_content = f.read()

    if _without_timestamp(previous_content) == _without_timestamp(new_content):
        print(f"Dashboard content unchanged besides the timestamp — leaving {DASHBOARD_FILE} as-is.")
    else:
        with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

    # master-dev's own root README no longer embeds the full table (that stayed a
    # master-dev-only file, see the note above) — just GitHub's own status badge for
    # THIS workflow (sync-upstream.yaml), hardcoded once in README.md. Nothing to
    # write here: GitHub renders that badge live from the workflow's run history.

def main():
    parser = argparse.ArgumentParser(description="Synchronize modding branches with master-dev and detect conflicts.")
    parser.add_argument("--source", default="master-dev", help="Source branch to sync from (default: master-dev).")
    parser.add_argument("--push", action="store_true", help="Perform merge and push for clean branches.")
    parser.add_argument("--output-only", action="store_true", help="Only generate markdown without merging.")
    args = parser.parse_args()

    source_branch = args.source
    source_ref = f"origin/{source_branch}"

    print(f"=== Modding Branches Sync Manager ===")
    print(f"Source: {source_ref}")
    print(f"Mode: {'Push Clean Merges' if args.push else 'Inspection / Dry-Run'}")

    # Prevent accidental data loss if pushing while working tree has uncommitted modifications
    if args.push and not is_working_tree_clean():
        print("\n❌ Erreur : L'arbre de travail contient des modifications non commitées.", file=sys.stderr)
        print("Pour éviter toute perte accidentelle de vos modifications locales,", file=sys.stderr)
        print("veuillez commiter ou remiser (stash) vos changements avant de lancer la synchronisation :", file=sys.stderr)
        print("    git stash", file=sys.stderr)
        sys.exit(1)

    # Ensure on master-dev
    run_cmd("git checkout master-dev")
    run_cmd("git config merge.ours.driver true")
    run_cmd(f"git fetch origin {source_branch}")

    source_sha_res = run_cmd(f"git rev-parse --short {source_ref}")
    source_sha = source_sha_res.stdout.strip()

    branches = get_remote_branches()
    print(f"Found {len(branches)} mod branches to inspect.")

    prev_statuses = get_previous_statuses()
    results = []
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    for branch in branches:
        branch_ref = f"origin/{branch}"
        last_commit = get_commit_info(branch_ref)
        print(f"\n--- Checking: {branch} ---")

        # Check if already ancestor
        if check_ancestor(source_ref, branch_ref):
            print(f"  -> Already up to date.")
            if branch in prev_statuses and "Conflit" in prev_statuses[branch].get("status", ""):
                log_event("RESOLVED", branch, f"Conflit résolu manuellement. Synchronisée avec {source_ref} (`{last_commit}`)")
            results.append({
                "branch": branch,
                "status": "✅ À jour",
                "last_commit": last_commit,
                "conflicts": [],
                "details": "Déjà à jour"
            })
            continue

        # In-memory merge test
        clean, real_conflicts, all_conflicts, raw_out = test_merge_tree(source_ref, branch_ref)
        if clean:
            if all_conflicts:
                print(f"  -> Clean merge possible (mod docs auto-protected, 0 real code conflicts).")
            else:
                print("  -> Clean merge possible (0 conflicts).")
            if args.push:
                print(f"  -> Merging and pushing to {branch}...")
                success, msg = merge_and_push_branch(branch, source_ref)
                if success:
                    status_text = "🔄 Synchronisée"
                    new_commit = get_commit_info(f"origin/{branch}")
                    log_event("AUTO-MERGE", branch, f"Fusion automatique réussie avec {source_ref} (`{new_commit}`)")
                else:
                    status_text = "⚠️ Erreur push"
                    log_event("ERROR", branch, f"Échec git push: {msg}")
                results.append({
                    "branch": branch,
                    "status": status_text,
                    "last_commit": get_commit_info(f"origin/{branch}"),
                    "conflicts": [],
                    "details": msg
                })
            else:
                results.append({
                    "branch": branch,
                    "status": "🟢 Prête à fusionner",
                    "last_commit": last_commit,
                    "conflicts": [],
                    "details": "Aucun conflit de code détecté"
                })
        else:
            print(f"  -> Real code conflicts detected in {len(real_conflicts)} file(s): {', '.join(real_conflicts)}")
            confl_fmt = ", ".join([f"`{f}`" for f in real_conflicts])
            log_event("CONFLICT", branch, f"Conflit de code détecté lors de la fusion avec {source_ref} dans: {confl_fmt}")
            results.append({
                "branch": branch,
                "status": "⚠️ Conflit",
                "last_commit": last_commit,
                "conflicts": real_conflicts,
                "details": f"{len(real_conflicts)} fichier(s) de code en conflit"
            })

    print(f"\nGenerating dashboard at {DASHBOARD_FILE}...")
    generate_dashboard(results, source_branch, source_sha, now_str)
    flush_event_logs()
    print("Dashboard and history log generated successfully.")

if __name__ == "__main__":
    main()
