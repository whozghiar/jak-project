# Texture Modding — Long-Term Discoveries & Fixes Log

This file records verified insights, texture dimensions quirks, and extraction gotchas for custom textures.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Use `_all/` inside `texture_replacements/` to replace a shared texture across every level tpage without duplicating files. | `custom_assets/jak2/texture_replacements/_all/my_tex.png` |
| 2026-09-19 | jak2/features/blue-krimzon-guard | Agent | Launcher texture pack `.zip` requires root `metadata.json` (with `author`/`authors`, `releaseDate`/`publishedDate`), optional `cover.png`, and `custom_assets/<game>/texture_replacements/`. | `{"schemaVersion": "1.0.0", "version": "1.0.0", "name": "...", "author": "..."}` |
| 2026-09-19 | master-dev | Agent | 38%+ of game textures are shared across multiple levels. Use `decompiler/config/<game>/ntsc_v1/tex-info.min.json` + `open-goal-texture-pack-generator` to detect sharing conflicts before packaging. | `suffixes = ['-vis-tfrag', '-vis-pris', ...] ; lvl = tpage.rsplit('-', 1)[0]` |
| 2026-09-19 | master-dev | Agent | Launcher ModSourceSchema v1 texture packs affiliation: texture packs in catalog index.json must include the releasing mod slug in `tags` and target the mod branch in `websiteUrl` to ensure proper affiliation. | `"tags": ["jak2", "retexture", "hd", "blue-krimzon-guard"]` |

