#!/usr/bin/env python3
"""
Automated synchronization script for Jak modding branches.
Tests mergeability against a source branch (default: origin/master) using in-memory `git merge-tree`,
optionally merges clean branches, and generates a live markdown dashboard of branch sync statuses.

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

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DASHBOARD_FILE = os.path.join(REPO_ROOT, "docs", "modding", "branch_sync_status.md")

def run_cmd(cmd, check=False):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=REPO_ROOT)
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

def test_merge_tree(source_ref, branch_ref):
    """
    Test merge in memory with git merge-tree --write-tree.
    Returns (clean: bool, conflicting_files: list, raw_output: str)
    """
    res = run_cmd(f"git merge-tree --write-tree {source_ref} {branch_ref}")
    if res.returncode == 0:
        return True, [], res.stdout
    
    # Extract conflicting files
    conflicts = []
    for line in (res.stdout + "\n" + res.stderr).splitlines():
        match = re.search(r"CONFLICT \(.*?\): Merge conflict in (.*)", line)
        if match:
            conflicts.append(match.group(1).strip())
    
    if not conflicts:
        for line in (res.stdout + "\n" + res.stderr).splitlines():
            if "CONFLICT" in line:
                conflicts.append(line.strip())
                
    return False, list(dict.fromkeys(conflicts)), res.stdout

def merge_and_push_branch(branch, source_ref):
    """Perform actual merge on a temporary ref and push to remote."""
    temp_branch = f"temp-sync-{branch.replace('/', '-')}"
    try:
        checkout_res = run_cmd(f"git checkout -B {temp_branch} origin/{branch}")
        if checkout_res.returncode != 0:
            err = (checkout_res.stderr or checkout_res.stdout).strip()
            return False, f"Échec checkout: {err[:120]}"

        merge_res = run_cmd(f'git merge {source_ref} -m "chore: sync {branch} with latest {source_ref} (AI-assisted)"')
        if merge_res.returncode != 0:
            run_cmd("git merge --abort")
            return False, "Échec lors de la fusion locale"
        
        push_res = run_cmd(f"git push origin {temp_branch}:{branch}")
        if push_res.returncode != 0:
            err = (push_res.stderr or push_res.stdout).strip()
            return False, f"Échec git push: {err[:120]}"
        return True, "Fusionnée et poussée avec succès"
    finally:
        run_cmd("git checkout master-dev")
        run_cmd(f"git branch -D {temp_branch}")

def generate_dashboard(results, source_ref, source_sha, updated_at):
    """Generate Markdown dashboard file."""
    total = len(results)
    synced_count = sum(1 for r in results if "À jour" in r["status"] or "Synchronisée" in r["status"])
    conflict_count = sum(1 for r in results if "Conflit" in r["status"])

    md = []
    md.append("# 📊 État de Synchronisation des Branches de Mods")
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

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

def main():
    parser = argparse.ArgumentParser(description="Synchronize modding branches with master and detect conflicts.")
    parser.add_argument("--source", default="master", help="Source branch to sync from (default: master).")
    parser.add_argument("--push", action="store_true", help="Perform merge and push for clean branches.")
    parser.add_argument("--output-only", action="store_true", help="Only generate markdown without merging.")
    args = parser.parse_args()

    source_branch = args.source
    source_ref = f"origin/{source_branch}"

    print(f"=== Modding Branches Sync Manager ===")
    print(f"Source: {source_ref}")
    print(f"Mode: {'Push Clean Merges' if args.push else 'Inspection / Dry-Run'}")

    # Ensure on master-dev
    run_cmd("git checkout master-dev")
    run_cmd(f"git fetch origin {source_branch}")

    source_sha_res = run_cmd(f"git rev-parse --short {source_ref}")
    source_sha = source_sha_res.stdout.strip()

    branches = get_remote_branches()
    print(f"Found {len(branches)} mod branches to inspect.")

    results = []
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    for branch in branches:
        branch_ref = f"origin/{branch}"
        last_commit = get_commit_info(branch_ref)
        print(f"\n--- Checking: {branch} ---")

        # Check if already ancestor
        if check_ancestor(source_ref, branch_ref):
            print(f"  -> Already up to date.")
            results.append({
                "branch": branch,
                "status": "✅ À jour",
                "last_commit": last_commit,
                "conflicts": [],
                "details": "Déjà à jour"
            })
            continue

        # In-memory merge test
        clean, conflicts, raw_out = test_merge_tree(source_ref, branch_ref)
        if clean:
            print("  -> Clean merge possible (0 conflicts).")
            if args.push:
                print(f"  -> Merging and pushing to {branch}...")
                success, msg = merge_and_push_branch(branch, source_ref)
                status_text = "🔄 Synchronisée" if success else "⚠️ Erreur push"
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
                    "details": "Aucun conflit détecté"
                })
        else:
            print(f"  -> Conflicts detected in {len(conflicts)} file(s): {', '.join(conflicts)}")
            results.append({
                "branch": branch,
                "status": "⚠️ Conflit",
                "last_commit": last_commit,
                "conflicts": conflicts,
                "details": f"{len(conflicts)} fichier(s) en conflit"
            })

    print(f"\nGenerating dashboard at {DASHBOARD_FILE}...")
    generate_dashboard(results, source_branch, source_sha, now_str)
    print("Dashboard generated successfully.")

if __name__ == "__main__":
    main()
