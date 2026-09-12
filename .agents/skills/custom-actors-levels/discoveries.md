# Custom Actors & Levels — Long-Term Discoveries & Fixes Log

This file records verified insights, 3D model export caveats, joint channel traps, and level injection discoveries.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Models loaded in GOAL heap without `.fr3` injection are invisible in Merc2 renderer; add entry to `extra_art_groups_by_dgo`. | `"extra_art_groups_by_dgo": { "LWIDEA": ["transport-ag:LPROTECT.DGO"] }` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | Collision pairing happens on CHILD primitives only: a collide-shape's root prim is a `collide-shape-prim-group` (cheap bounding sphere) that never enters a touching entry. Widening only the root's `collide-with` does nothing — OR the bits into every child too. | `(dotimes (i (the int (-> group num-children))) (logior! (-> group child i prim-core collide-with) (collide-spec civilian enemy)))` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | Importing a retail enemy into another level needs BOTH circuits: `<x>-ag.go` + that enemy's home-level **pris** texture page in the target `.gd`, and an `extra_art_groups_by_dgo` entry with `:HOME.DGO` so the remap table resolves its texture ids. Texture names rarely mention the actor, so pick the home level's `*-vis-pris` page. | `"LWIDEB.DGO": ["rapid-gunner-ag:RUI.DGO"]` + `"tpage-853.go"` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | Retail combat states cannot be re-pointed at a subclass of a different parent: they read the original type's fields at fixed offsets. Port the states and redeclare the fields; inheriting the wrong base (e.g. `citizen` for pooling) is the cheaper half to keep. | `(deftype chaos-rapid-gunner (chaos-metalhead) ((target-next-pos vector :inline) ...))` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | Jak2 city faction ratios are bounded by usable traffic types x 20: Krimzon Guard pedestrians have only types 4 and 6 (`lwide-activate` leaves 5 and 7 at level #f), so 40 guards is the hard maximum and only reachable as an even 20+20. A weighted split that mirrors retail (1:9) silently clamps to 4+20. | `(define *mod-chaos-guard-types* (new 'static 'array uint8 2 4 6))` |
