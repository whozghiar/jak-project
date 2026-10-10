# indus-test for Jak 3

Exported by the OpenGOAL Level Editor from custom-level: 4676 meshes (173480 triangles), 0 collision triangles of the game, 224 actors, 0 art groups, 5 nav meshes.

> `indus-test.glb` (the level's geometry and textures, read from your own copy of Jak 3) is not
> in the repository: make it with the OpenGOAL Level Editor,
> `python tools/build_indus_test.py --export <jak-project>/custom_assets/jak3/levels`.

## Adding it to the game

1. Copy this folder to `custom_assets/jak3/levels/indus-test/` in the jak-project checkout.
2. In `goal_src/jak3/game.gp`, next to the lines of the test-zone:

   ```
   (build-custom-level "indus-test")
   (custom-level-cgo "IXT.DGO" "indus-test/indus-test.gd")
   ```

3. In `goal_src/jak3/engine/level/level-info.gc`, add the definition of `level-info.gc`
   (next to this file) and give it an `:index` no other level has. The player starts at
   (0.0, 9.5, -70.0) m.
4. Build the game (`(mi)` in the REPL), then go there:
   `(start 'play (get-continue-by-name *game-info* "indus-test-start"))`.
   (`bg` loads it next to the levels already there: from the city, no memory is left.)

## What the export changed

- 4676 elements collide by their shape (the builder makes it, with automatic walls): the ones placed, and the levels without the game's collision.

## Good to know

- The collision of the levels' own decor is the game's: a piece of it moved or deleted keeps its
  collision where the game had it. Export with the collision made from the decor to change that.
- The code of the game's objects that live in a level's own files is in `indus-test.gd`, with
  the files before it in that level's DGO (`goal_src/jak3/dgos/`).
- The paths of the actors move with them; the other positions inside their data (targets) are
  the game's.
- The scripts of the game's objects (their `on-...` data) are left out: OpenGOAL's level
  builder cannot write them. What an object does is its behavior (here, the game's own).
- The nav meshes are in `indus-test-nav.json` (`nav_data` of the level): OpenGOAL's level builder
  for Jak 3 writes them in the level only when it reads `nav_data` (see the editor's README).
