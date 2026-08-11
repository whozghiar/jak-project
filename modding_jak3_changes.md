# Modding Jak 3 - Change Log

| Date       | Touched/Created Files | Technical Description | Objective |
|------------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`, `goal_src/jak3/levels/city/common/ff-squad-control.gc`, `goal_src/jak3/levels/wascity/cty-faction.gc`, `goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) integrated directly into the OpenGOAL PC Debug Menu under "City Mods" (Jak 2 Mode vs Chaos Mode). | Implement "[Mod] City Behavior": Jak 2-style guard hostility & dynamic City War / Jak 2 mode switcher via Debug Menu. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`, `goal_src/jak3/pc/debug/default-menu-pc.gc`, `modding_jak3_changes.md` | Added third City Mode `'default` representing post-game state (`city-power-game-resolution` faction strengths and default traffic/spawner quotas). Integrated option in PC Debug Menu under "City Mods". | Provide full end-game spawn behavior option alongside Jak 2 mode and Chaos mode. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`, `goal_src/jak3/levels/city/traffic/citizen/citizen.gc`, `goal_src/jak3/levels/city/traffic/citizen/civilian.gc`, `modding_jak3_changes.md` | Extended move-to-ground vertical search radius to 40m in citizen.gc and civilian.gc, and appended 'ctypepa to *territory-list* in cty-faction.gc for Jak 2 and Chaos modes. | Fix vehicle hijack pilot ejection on carjacking across Haven City and guarantee ctypepa.DGO RAM retention. |
| 2026-08-11 | `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb` (new custom model, real geometry+textures, added to level `ctypesa` via the decompiler's existing `add_custom_model_to_level` mechanism), `custom_assets/jak3/models/custom_levels/crimson-redguard.glb` (new, used only to generate a named skeleton/mgeo placeholder), `goal_src/jak3/game.gp` (added `(build-actor "crimson-redguard")` + `*file-entry-map*` pre-registration so `cgo-file` doesn't try to copy the custom-built `.go` from decompiled assets), `goal_src/jak3/dgos/ctypesa.gd` (added `crimson-redguard-ag.go` alongside `crimson-guard-ag.go`), `goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc` (new `citizen-flag red-guard` bit), `goal_src/jak3/levels/city/traffic/citizen/guard.gc` (`citizen-method-194`: 3-way random roll blue/dark-guard/red-guard gated on `*custom-city-mode*`, red-guard exclusive to `'jak2`; after `crimson-guard-method-267` runs, overrides `(-> this draw mgeo)` to the new "crimson-redguard-lod0" model for red-guard instances, or resets it to crimson-guard's own mgeo otherwise — `(-> this draw art-group)`/`jgeo` stay pointed at the shared, unmodified `skel-crimson-guard` so joints/animations are fully reused, not duplicated). | Add a new "crimson-redguard" entity — a red-recolored Freedom Faction guard with the same skeleton/animations as `crimson-guard` — patrolling alongside the existing blue/yellow guards in Haven City, appearing exclusively in City Mode "Jak 2", without modifying the existing `crimson-guard` entity, textures, or behavior at all. |













## [Mod] City Behavior

### Description
Le mod **City Behavior** apporte une refonte complète du comportement des gardes et du système de factions dans les secteurs d'Haven City pour Jak 3. Il permet de choisir à tout moment entre le comportement d'origine du jeu (mode **Default**), le mode urbain pacifique avec alerte de groupe style Jak 2 (mode **Jak 2**), et un mode de guerre générale (mode **Chaos**).

### Utilité & Fonctionnalités
1. **Comportement des Gardes FF par Mode** :
   - **Mode Default (Fin du jeu - Canon)** *(Mode sélectionné par défaut)* :
     - Les gardes de la Freedom Faction patrouillent en ville. Si Jak attaque un garde en zone calme, seule l'escouade visée riposte (comportement identique à la branche `master`). Les autres gardes restent neutres.
     - Dans les zones de conflit (ex: zone industrielle ou Slums), les gardes FF défendent la ville contre les KG/MH et n'attaquent pas Jak.
     - La musique d'ambiance de la ville reste active (pas d'interruption par la musique de combat `cityfi`).
   - **Mode Jak 2 (Gardes Neutres & Chasse)** :
     - Les gardes patrouillent pacifiquement sans autres ennemis en ville.
     - Dès que Jak attaque un garde, une alerte générale s'enclenche : la musique de combat (`cityfi`) retentit et tous les gardes FF de la zone dégainent pour abattre Jak.
     - Fin d'alerte rapide (~3 secondes) lorsque Jak se met à l'abri hors de vue.
   - **Mode Chaos (Guerre Totale)** :
     - Déclenche la guerre générale dans tous les secteurs. Les patrouilles Metalheads, Krimzon Guards et Freedom Faction Guards s'affrontent en continu. Les gardes FF se concentrent sur la défense contre les KG/MH et n'attaquent pas Jak.

2. **Persistance d'Alerte entre Zones** :
   - Les alertes en cours ne sont pas annulées lors des franchissements de frontières ou des chargements de secteurs d'Abriville.

3. **Menu Debug PC et Indicateur Visuel (`City Mods`)** :
   - Le menu debug PC permet d'identifier immédiatement le mode actif grâce à une coche visuelle `[X]`.

### Mode d'Emploi
1. Lancer le jeu OpenGOAL Jak 3.
2. Ouvrir le **Menu Debug** PC (touche `R3` ou raccourci Debug).
3. Naviguer vers la rubrique **`City Mods`**.
4. Sélectionner le mode souhaité (la coche `[X]` indique le mode en cours) :
   - **`[X] Mode Default (Fin du Jeu - Canon)`** : Spawns de fin de jeu, gardes neutres réagissant uniquement par escouade si attaqués.
   - **`[ ] Mode Jak 2 (Gardes Neutres & Chasse)`** : Gardes neutres avec alerte globale et musique de combat au premier coup.
   - **`[ ] Mode Chaos (Guerre Totale)`** : Guerre généralisée FF vs KG vs MH à travers toute la ville.
