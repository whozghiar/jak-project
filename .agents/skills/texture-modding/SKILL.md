---
name: texture-modding
description: Guide to custom texture replacement, directory layout, PNG format requirements, texture merging, and task extract baking in OpenGOAL.
---

# Texture Modding & Replacement — Engineering Reference

OpenGOAL features native texture replacement and texture merging mechanisms. Custom textures are processed during asset extraction and baked directly into PC-optimized renderer packages (`.fr3` and texture databases).

---

## 1. Texture Replacement Directory Structure

Texture replacements are located under `custom_assets/`:

```text
custom_assets/
└── jak[x]/
    ├── texture_replacements/
    │   ├── <tpage-name>/
    │   │   └── <texture-name>.png      # Replaces texture specifically in that tpage
    │   └── _all/
    │       └── <texture-name>.png      # Global fallback: replaces texture across ALL tpages
    └── texture_merges/
        └── <tpage-name>/
            └── <texture-name>.png      # Merges non-transparent pixels onto original texture
```

### Folder Explanations
1. **Specific TPage Folder (`<tpage-name>/`):**
   - E.g. `custom_assets/jak2/texture_replacements/tpage-1234/guard-armor.png`
   - Only replaces the texture inside the designated texture page.
2. **Global Fallback Folder (`_all/`):**
   - E.g. `custom_assets/jak2/texture_replacements/_all/jak-eyes.png`
   - If a texture is not found in a specific `<tpage-name>` subfolder, the extractor checks `_all/`.
   - Useful for universal textures shared across multiple levels.

---

## 2. Image Specifications

- **Format:** Standard PNG (Portable Network Graphics).
- **Color Channels:** 32-bit RGBA (8 bits per channel: Red, Green, Blue, Alpha).
- **Resolution:** Can match original PS2 dimensions or be higher resolution (HD textures).
- **Dimensions:** Must have valid dimensions. For texture merging (`texture_merges`), the merge PNG dimensions **must strictly match** the source texture dimensions.

---

## 3. Extraction & Baking Workflow

Textures in OpenGOAL are not loaded as loose `.png` files at runtime; they are baked into binary texture pages and `.fr3` level files during offline extraction.

### Step-by-Step Replacement Workflow:
1. Identify the texture name and tpage (e.g. from `decompiler_out/jak[x]/textures/` or level files).
2. Place your edited `.png` in:
   ```text
   custom_assets/jak[x]/texture_replacements/<tpage-name>/<texture-name>.png
   ```
   *(or `_all/<texture-name>.png`)*
3. Run extraction to bake the textures:
   ```bash
   task extract
   ```
4. Boot the game to inspect in-game textures:
   ```bash
   task boot-game
   ```

> [!NOTE]
> Editing or adding a PNG in `custom_assets/` does **not** update the game immediately. You must run `task extract` to bake the changes.

---

## 4. Standalone Texture Pack Distribution & Packaging

To distribute custom textures as an official, 1-click installable Texture Pack for the OpenGOAL Launcher:

### Archive Structure:
The resulting `.zip` must have this exact structure:
```text
metadata.json                                     # Root metadata (author, version, description)
cover.png                                         # Optional thumbnail
custom_assets/jak[x]/texture_replacements/        # Replacement textures
```

### Packaging Command:
Run the automated packaging task:
```bash
task modding-package-texture-pack -- --update-index
```
Options supported:
- `--game jak1|jak2|jak3`: Auto-detected from active branch if omitted.
- `--slug <name-textures>`: Auto-derived from branch name if omitted.
- `--display-name "<Title>"`: Auto-generated from slug if omitted.
- `--version <semver>`: Default `1.0.0`.
- `--author "<name>"`: Auto-detected from git if omitted.
- `--update-index`: Automatically registers or updates the pack in root `index.json` under `"texturePacks"`.

### Standard Storage & Automatic Release Pipeline:
Package your texture pack into:
```text
docs/modding/current_mod/texture_packs/<slug>-v<version>.zip
```
- **Git Tracked & Sync Protected:** Located under `docs/modding/current_mod/`, safely versioned in git without `.gitignore` interference, and immune to upstream branch sync overwrites.
- **Automated GitHub Release:** During `.github/workflows/release.yml`, CI automatically picks up any `.zip` from this directory, computes checksums, registers it in `index.json`, and attaches it to the GitHub Release assets!

