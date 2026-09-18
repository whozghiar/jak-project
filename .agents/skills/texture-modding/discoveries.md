# Texture Modding — Long-Term Discoveries & Fixes Log

This file records verified insights, texture dimensions quirks, and extraction gotchas for custom textures.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Use `_all/` inside `texture_replacements/` to replace a shared texture across every level tpage without duplicating files. | `custom_assets/jak2/texture_replacements/_all/my_tex.png` |
| 2026-09-19 | jak2/features/blue-krimzon-guard | Agent | Launcher texture pack `.zip` requires root `metadata.json` (with `author`/`authors`, `releaseDate`/`publishedDate`), optional `cover.png`, and `custom_assets/<game>/texture_replacements/`. | `{"schemaVersion": "1.0.0", "version": "1.0.0", "name": "...", "author": "..."}` |

