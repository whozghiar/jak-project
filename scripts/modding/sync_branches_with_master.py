#!/usr/bin/env python3
"""
Automated synchronization script for Jak modding branches.
Tests mergeability against a source branch (default: master-dev) using in-memory `git merge-tree`,
optionally merges clean branches, and displays a summary table in terminal output and GitHub Actions Step Summary.

How sync status is reported:
    - In CLI / terminal: prints a formatted summary table of all branches and conflict commands.
    - In GitHub Actions CI: appends the summary markdown to $GITHUB_STEP_SUMMARY for a clean web report.
    - Each mod branch carries its own native GitHub Actions status badge for
      .github/workflows/branch-sync-check.yaml (?branch=<it>), written once into its
      README.md at creation time (create_mod_branch.py). Pushing a successful merge to a branch
      is what triggers branch-sync-check.yaml and turns the badge green.

Usage:
    python scripts/modding/sync_branches_with_master.py           # Test and display summary without pushing
    python scripts/modding/sync_branches_with_master.py --push    # Merge clean branches and push to origin
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

def get_previous_statuses():
    """Previous status parsing retained for interface compatibility (returns empty dict)."""
    return {}

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

        # Same deal for any workflow master-dev added that isn't in
        # sync_common.ALLOWED_MOD_BRANCH_WORKFLOWS: a clean merge carries it in
        # with no conflict to catch, so it has to be swept out explicitly too
        # (see stray_workflow_files).
        for wf_path in sync_common.stray_workflow_files(REPO_ROOT):
            run_cmd(f'git rm -f -q "{wf_path}"')

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

def generate_dashboard(results, source_ref, source_sha, updated_at, output_file=None):
    """Generate Markdown dashboard and print summary."""
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

    # Print clean summary table to stdout
    print("\n" + "=" * 70)
    print(f"📊 Mod Branches Sync Summary: {synced_count}/{total} synced ({conflict_count} conflicts)")
    print("=" * 70)
    for r in results:
        b = r["branch"]
        st = r["status"]
        if r["conflicts"]:
            print(f"  {st:<22} {b} -> Conflicts: {', '.join(r['conflicts'])}")
        else:
            print(f"  {st:<22} {b}")
    print("=" * 70 + "\n")

    # Output to GitHub Actions Step Summary if running in CI
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        try:
            with open(step_summary, "a", encoding="utf-8") as f:
                f.write(new_content + "\n\n")
            print("Summary successfully appended to GITHUB_STEP_SUMMARY.")
        except Exception as err:
            print(f"Notice: Could not write to GITHUB_STEP_SUMMARY: {err}")

    # Output to file if requested
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Summary markdown written to: {output_file}")
        except Exception as err:
            print(f"Error writing output file {output_file}: {err}")
    # write here: GitHub renders that badge live from the workflow's run history.

def main():
    parser = argparse.ArgumentParser(description="Synchronize modding branches with master-dev and detect conflicts.")
    parser.add_argument("--source", default="master-dev", help="Source branch to sync from (default: master-dev).")
    parser.add_argument("--push", action="store_true", help="Perform merge and push for clean branches.")
    parser.add_argument("--output-only", action="store_true", help="Only check mergeability and display summary without merging.")
    parser.add_argument("--output-file", default=None, help="Optional path to write summary markdown to.")
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
                else:
                    status_text = "⚠️ Erreur push"
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
            results.append({
                "branch": branch,
                "status": "⚠️ Conflit",
                "last_commit": last_commit,
                "conflicts": real_conflicts,
                "details": f"{len(real_conflicts)} fichier(s) de code en conflit"
            })

    generate_dashboard(results, source_branch, source_sha, now_str, output_file=args.output_file)

if __name__ == "__main__":
    main()
