# GOAL Lisp & Syntax — Long-Term Discoveries & Fixes Log

This file records verified, hard-won insights, syntax traps, and fixes identified during OpenGOAL mod development.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Avoid `(= f1 f2)` on floats; use epsilon or bounding comparisons to prevent state lockups. | `(< (abs (- (-> self speed) target-speed)) (meters 0.01))` |
