# Modding Jak 2 - Changes Log (AI-assisted)

| Date | Files | Description | Objective |
|------|-------|-------------|-----------|
| 2025-07-19 | `goal_src/jak2/levels/city/farm/yakow.gc` | Rewrote yakow behavior with Jak 1-style states: `run-away` (flee from player), `graze`/`graze-kicked` (dedicated grazing with kick reaction), improved `kicked` (transitions to flee), new `die` state (drops 5 dark eco pills). Added fields: `grazing`, `walk-run-blend`, `walk-turn-blend`, `run-mode`, `home-base`. Changed `damage-amount-from-attack` to return 1 (was 0). Set HP to 3, increased run acceleration. | Make Jak 2 yakow behave like Jak 1 yakow (flee, graze, react to kicks) and drop dark eco on death. |
