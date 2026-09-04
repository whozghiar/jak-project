#!/usr/bin/env python3
"""
Aggregate individual tip files into a consolidated bilingual knowledge base for each game.
(Jak 1, Jak 2, Jak 3)
"""

import os
import re
import glob

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_MODDING_DIR = os.path.join(REPO_ROOT, "docs", "modding")

GAMES = [
    {"id": "jak1", "name": "Jak 1 (The Precursor Legacy)", "dir": "jak1_modding_utilities"},
    {"id": "jak2", "name": "Jak 2", "dir": "jak2_modding_utilities"},
    {"id": "jak3", "name": "Jak 3", "dir": "jak3_modding_utilities"},
]

def slugify(text):
    """Generate markdown-compatible anchor slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text

def parse_tip_file(filepath):
    """Extract bilingual metadata, titles, and sections from a single tip markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Title (line 1)
    title_match = re.search(r"^#\s+Jak\s+[123]\s+—\s+(.*?)$", content, re.MULTILINE)
    full_title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
    if "/" in full_title:
        en_title, fr_title = [part.strip() for part in full_title.split("/", 1)]
    else:
        en_title, fr_title = full_title, full_title

    # Extract Provenance Metadata
    prov_match = re.search(r">\s*-\s*\*\*Origin / Provenance:\*\*\s*`(.*?)`", content)
    origin_branch = prov_match.group(1).strip() if prov_match else "master"

    updated_match = re.search(r">\s*-\s*\*\*Last Updated / Dernière modification:\*\*\s*`(.*?)`", content)
    updated_branch = updated_match.group(1).strip() if updated_match else None

    # Split EN and FR sections
    en_section = ""
    fr_section = ""

    en_split = content.split("# 🇬🇧 English Version")
    if len(en_split) > 1:
        fr_split = en_split[1].split("# 🇫🇷 Version Française")
        en_section = fr_split[0].strip()
        if len(fr_split) > 1:
            fr_section = fr_split[1].strip()

    # Strip top-level # headers inside sections to maintain hierarchy (downgrade to ## / ###)
    def clean_section(text, title):
        lines = []
        is_first_header = True
        for line in text.splitlines():
            sline = line.strip()
            # If line is a table of contents or duplicate of the section title, skip it
            if sline.startswith("## Table of Contents") or sline.startswith("## Sommaire"):
                continue
            if is_first_header and sline.startswith("## "):
                # If first header matches or is redundant with title, skip it
                is_first_header = False
                continue
            lines.append(line)
        cleaned = "\n".join(lines).strip()
        return cleaned

    return {
        "filename": os.path.basename(filepath),
        "en_title": en_title,
        "fr_title": fr_title,
        "origin": origin_branch,
        "updated": updated_branch,
        "en_content": clean_section(en_section, en_title),
        "fr_content": clean_section(fr_section, fr_title),
    }

def build_aggregated_doc(game_info, tips):
    """Construct unified aggregated markdown for a specific game."""
    game_name = game_info["name"]
    doc = []

    doc.append(f"# {game_name} — Modding Notes & Engine Utilities / Notes de Modding & Utilitaires Moteur\n")
    doc.append("> **Bilingual Knowledge Base / Base de Connaissances Bilingue**")
    doc.append(">")
    doc.append("> - [🇬🇧 English Version](#-english-version)")
    doc.append("> - [🇫🇷 Version Française](#-version-française)\n")
    doc.append("---\n")

    # 🇬🇧 English Section
    doc.append("# 🇬🇧 English Version\n")
    doc.append("## Table of Contents")
    for idx, tip in enumerate(tips, 1):
        anchor = slugify(f"{idx} {tip['en_title']}")
        doc.append(f"- [{idx}. {tip['en_title']}](#{anchor})")
    doc.append("\n---\n")

    for idx, tip in enumerate(tips, 1):
        doc.append(f"### {idx}. {tip['en_title']}\n")
        meta = f"> **Origin / Provenance:** `{tip['origin']}`"
        if tip["updated"]:
            meta += f" | **Last Updated:** `{tip['updated']}`"
        doc.append(f"{meta}\n")
        doc.append(tip["en_content"])
        doc.append("\n---\n")

    # 🇫🇷 French Section
    doc.append("# 🇫🇷 Version Française\n")
    doc.append("## Sommaire")
    for idx, tip in enumerate(tips, 1):
        anchor = slugify(f"{idx} {tip['fr_title']}")
        doc.append(f"- [{idx}. {tip['fr_title']}](#{anchor})")
    doc.append("\n---\n")

    for idx, tip in enumerate(tips, 1):
        doc.append(f"### {idx}. {tip['fr_title']}\n")
        meta = f"> **Origin / Provenance :** `{tip['origin']}`"
        if tip["updated"]:
            meta += f" | **Dernière modification :** `{tip['updated']}`"
        doc.append(f"{meta}\n")
        doc.append(tip["fr_content"])
        doc.append("\n---\n")

    return "\n".join(doc)

def process_game(game_info):
    folder = os.path.join(DOCS_MODDING_DIR, game_info["dir"])
    if not os.path.isdir(folder):
        print(f"Skipping {game_info['id']}: folder not found ({folder})")
        return

    pattern = os.path.join(folder, "[0-9]*_*.md")
    tip_files = sorted(glob.glob(pattern), key=lambda x: os.path.basename(x))

    if not tip_files:
        print(f"No numbered tip files found for {game_info['id']}")
        return

    tips = [parse_tip_file(f) for f in tip_files]
    new_doc_content = build_aggregated_doc(game_info, tips)

    target_file = os.path.join(folder, f"{game_info['id']}_modding_utilities.md")
    
    # Read existing content to check if changed
    existing_content = ""
    if os.path.isfile(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

    if existing_content.strip() != new_doc_content.strip():
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_doc_content)
        print(f"[UPDATED] {os.path.relpath(target_file, REPO_ROOT)} ({len(tips)} tips aggregated)")
    else:
        print(f"[UNCHANGED] {os.path.relpath(target_file, REPO_ROOT)}")

def main():
    print("=== Aggregating Modding Utilities ===")
    for game in GAMES:
        process_game(game)
    print("=== Done ===")

if __name__ == "__main__":
    main()
