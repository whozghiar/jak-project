#!/usr/bin/env python3
"""
Automated script to create a new mod branch branched from master-dev,
and automatically replace the root README.md with a customized mod README template.

Usage:
    python scripts/modding/create_mod_branch.py jak2/features/my-new-mod
    python scripts/modding/create_mod_branch.py jak3/config/enhanced_memory
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.parse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATE_PATH = os.path.join(REPO_ROOT, "docs", "modding", "templates", "MOD_README.template.md")
README_PATH = os.path.join(REPO_ROOT, "README.md")

def run_cmd(cmd, check=True):
    print(f">> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=REPO_ROOT)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res

def format_title(slug):
    """Convert slug-name to Capitalized Words."""
    words = re.split(r"[-_]+", slug)
    return " ".join(w.capitalize() for w in words if w)

def main():
    parser = argparse.ArgumentParser(description="Create a new mod branch with an initialized root README.md.")
    parser.add_argument("branch_name", help="Branch name following jak[123]/[type]/[name] (e.g. jak2/features/hover-board)")
    parser.add_argument("--no-commit", action="store_true", help="Do not create the initial commit automatically.")
    parser.add_argument("--push", action="store_true", help="Push the newly created branch to origin.")
    args = parser.parse_args()

    branch = args.branch_name.strip()

    # Validate branch pattern
    match = re.match(r"^jak([123])/([^/]+)/(.+)$", branch)
    if not match:
        print(f"Error: Invalid branch name format '{branch}'.", file=sys.stderr)
        print("Expected format: jak[1|2|3]/[type_of_mod]/[mod_name]", file=sys.stderr)
        print("Example: jak2/features/air-traffic-v2", file=sys.stderr)
        sys.exit(1)

    game_num = match.group(1)
    mod_type = match.group(2)
    mod_slug = match.group(3)

    game_label = f"Jak {game_num}"
    mod_title = format_title(mod_slug)

    print(f"\n=== Creating Mod Branch: {branch} ===")
    print(f"Target Game: {game_label}")
    print(f"Mod Title  : {mod_title}")

    # Ensure master-dev is fetched and clean
    print("\nEnsuring master-dev is up to date...")
    run_cmd("git fetch origin master-dev")
    run_cmd("git checkout master-dev")

    # Check uncommitted changes
    status_res = run_cmd("git status --porcelain", check=False)
    if status_res.stdout.strip():
        print("Error: You have uncommitted changes in your working tree. Please commit or stash them first.", file=sys.stderr)
        sys.exit(1)

    # Create new branch from master-dev
    print(f"\nCreating branch '{branch}' from master-dev...")
    run_cmd(f"git checkout -b {branch} master-dev")

    # Read template
    if not os.path.isfile(TEMPLATE_PATH):
        print(f"Error: Template not found at '{TEMPLATE_PATH}'.", file=sys.stderr)
        sys.exit(1)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Customize template placeholders
    branch_encoded = urllib.parse.quote(branch, safe="")
    game_encoded = urllib.parse.quote(game_label, safe="")

    custom_readme = template_content.replace("# [Mod Name] — [Jak 1 / Jak 2 / Jak 3]", f"# {mod_title} — {game_label}")
    custom_readme = custom_readme.replace("Game-Jak%202-orange.svg", f"Game-{game_encoded}-orange.svg")
    custom_readme = custom_readme.replace("Branch-jak2%2Ffeatures%2Fyour_mod-green.svg", f"Branch-{branch_encoded}-green.svg")
    custom_readme = custom_readme.replace("task set-game-jak2", f"task set-game-jak{game_num}")

    # Write to root README.md
    print(f"Writing customized mod README to {README_PATH}...")
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(custom_readme)

    if not args.no_commit:
        print("\nCommitting customized mod README...")
        run_cmd("git add README.md")
        run_cmd(f'git commit -m "docs: initialize mod README for {branch} (AI-assisted)"')

    if args.push:
        print(f"\nPushing {branch} to origin...")
        run_cmd(f"git push -u origin {branch}")

    print(f"\n[OK] Mod branch '{branch}' successfully created and initialized!")
    print(f"When browsing this branch on GitHub, your mod README will be displayed automatically on the root page.")

if __name__ == "__main__":
    main()
