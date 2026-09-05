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
DASHBOARD_FILE = os.path.join(REPO_ROOT, "docs", "modding", "tools", "branch_sync_status.md")
HISTORY_LOG_FILE = os.path.join(REPO_ROOT, "docs", "modding", "tools", "branch_sync_history.md")

def log_event(event_type, branch, details):
    """Append a structured entry to the persistent sync history markdown file."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(HISTORY_LOG_FILE), exist_ok=True)
    if not os.path.isfile(HISTORY_LOG_FILE):
        with open(HISTORY_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📜 Historique des Synchronisations des Branches / Branch Sync History\n\n")
            f.write("| Date (UTC) | Événement | Branche | Détails |\n")
            f.write("| :--- | :---: | :--- | :--- |\n")

    icon_map = {
        "CONFLICT": "⚠️ Conflit",
        "AUTO-MERGE": "🔄 Auto-fusion",
        "RESOLVED": "✅ Conflit Résolu",
        "ERROR": "❌ Erreur"
    }
    event_label = icon_map.get(event_type, event_type)
    line = f"| `{timestamp}` | {event_label} | `{branch}` | {details} |"
    print(f"  [LOG] {event_type} - {branch}: {details}")
    with open(HISTORY_LOG_FILE, "a", encoding="utf-8") as f:
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

    # Also update the dashboard table directly inside root README.md on master-dev
    readme_file = os.path.join(REPO_ROOT, "README.md")
    if os.path.isfile(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            readme_content = f.read()

        table_lines = [
            f"> **Dernière mise à jour :** `{updated_at}`  ",
            f"> **Branche source :** `{source_ref}` (`{source_sha}`)  ",
            f"> **Statut global :** {synced_count}/{total} synchronisées ({conflict_count} conflits)",
            "",
            "| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |",
            "| :--- | :---: | :--- | :--- | :--- |"
        ]
        for r in results:
            branch_code = f"`{r['branch']}`"
            status = r["status"]
            last_commit = f"`{r['last_commit']}`"
            conflicts_fmt = "<br>".join([f"• `{f}`" for f in r["conflicts"]]) if r["conflicts"] else r.get("details", "Aucun")
            res_cmd = f"`git checkout {r['branch']} && git merge origin/{source_ref}`" if "Conflit" in status else "—"
            table_lines.append(f"| {branch_code} | {status} | {last_commit} | {conflicts_fmt} | {res_cmd} |")

        table_block = "\n".join(table_lines)
        pattern = r"<!-- BRANCH_STATUS_START -->.*?<!-- BRANCH_STATUS_END -->"
        replacement = f"<!-- BRANCH_STATUS_START -->\n{table_block}\n<!-- BRANCH_STATUS_END -->"
        if re.search(pattern, readme_content, flags=re.DOTALL):
            new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(new_readme)

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

    # Ensure on master-dev
    run_cmd("git checkout master-dev")
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
        clean, conflicts, raw_out = test_merge_tree(source_ref, branch_ref)
        if clean:
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
                    "details": "Aucun conflit détecté"
                })
        else:
            print(f"  -> Conflicts detected in {len(conflicts)} file(s): {', '.join(conflicts)}")
            confl_fmt = ", ".join([f"`{f}`" for f in conflicts])
            log_event("CONFLICT", branch, f"Conflit détecté lors de la fusion avec {source_ref} dans: {confl_fmt}")
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
