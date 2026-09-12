# Engine Internals & REPL — Long-Term Discoveries & Fixes Log

This file records verified insights, runtime crashes, memory management resolutions, and REPL pitfalls.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | `build-release-game` rebuilds only `gk` + `goalc`, skipping decompiler and tests for ~50% faster compile time. | `task build-release-game` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | Jak2 traffic: each `traffic-type` owns a FIXED 20-handle reserve window; `add-reserved-process` silently drops the 21st, so a want-count > 20 leaks one process per frame, each holding a `nav-control` slot until the level dies (ends in `too many users for nav-mesh #f`). Retail's max want-count is 15. Clamp every want-count you write. | `(set! v1-4 (&-> v1-4 20))` / `(when (< a1-2 20) ... (+! (-> v1-2 inactive-count) 1))` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | `*default-nav-mesh*` (nav-mesh.gc) is ONE global static shared by every actor with no entity-backed mesh — all Haven City traffic included, pooled or active. Predicting its usage from want-counts fails; measure free slots instead (`remove-nav-control` only trims the tail, so `nav-control-count` overstates). | `(dotimes (i (the int (-> mesh nav-control-count))) (if (-> mesh nav-control-array i process) (+! used 1)))` |
