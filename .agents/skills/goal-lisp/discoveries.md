# GOAL Lisp & Syntax — Long-Term Discoveries & Fixes Log

This file records verified, hard-won insights, syntax traps, and fixes identified during OpenGOAL mod development.

> **Feeding Rule:**
> Whenever you identify an undocumented behavior, a syntax trap in GOAL, or the resolution of an engine crash during mod development, append a concise entry (under 10 lines) with a code snippet into this file before concluding the task.

| Date | Branch | Author/Agent | Discovery / Fix | Code Sample |
|---|---|---|---|---|
| 2026-09-11 | master-dev | Agent | Avoid `(= f1 f2)` on floats; use epsilon or bounding comparisons to prevent state lockups. | `(< (abs (- (-> self speed) target-speed)) (meters 0.01))` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | `defstate` accepts NO docstring (unlike `defun`/`defmethod`): its `&rest body` docstring branch needs `(> (length body) 1)` and runs after the keywords, so a string before `:virtual` breaks keyword parsing. Put the prose in `;;` comments above the form. | `;; what this state does` / `(defstate hostile (my-type) :virtual #t ...)` |
| 2026-09-12 | jak2/features/haven-city-chaos | Agent | In `defstate`, an omitted handler is left UNSET (`#f`), never inherited from the parent virtual state: the `*no-state*` sentinel only tells the compiler to skip the field write, and `enter-state` then does `(set! (-> pp post-hook) (-> new-state post))`. So a partial override silently drops the parent's trans/post -- e.g. `citizen-enemy::active` declares only `:code` and therefore has no post at all. Re-declare every handler you still need. | `(let ((t9 (-> (method-of-type nav-enemy hostile) enter))) (if t9 (t9)))` |
