# Custom Actors & Levels — Long-Term Discoveries & Fixes Log

This file records verified insights, 3D model export caveats, joint channel traps, and level injection discoveries.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Models loaded in GOAL heap without `.fr3` injection are invisible in Merc2 renderer; add entry to `extra_art_groups_by_dgo`. | `"extra_art_groups_by_dgo": { "LWIDEA": ["transport-ag:LPROTECT.DGO"] }` |
