# Engine Internals & REPL — Long-Term Discoveries & Fixes Log

This file records verified insights, runtime crashes, memory management resolutions, and REPL pitfalls.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | `build-release-game` rebuilds only `gk` + `goalc`, skipping decompiler and tests for ~50% faster compile time. | `task build-release-game` |
| 2026-09-11 | jak2/features/crimson-blueguard/crimson-redguard-behavior | Agent | Traffic pools allocate their processes ONCE then recycle them, so a runtime faction/type swap in `traffic-object-spawn` is invisible to guards that already exist. `'deactivate-by-type` only moves actives back to inactive -- it never re-creates. Send `'kill-all` (destroys active + inactive) then `'spawn-all` (sets `fast-spawn`, re-creates) to make the swap take effect live. | `(send-event *traffic-manager* 'kill-all) (send-event *traffic-manager* 'spawn-all)` |
