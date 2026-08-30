# Mod Readme — City Behavior (Jak 3) / Comportement de la Ville (Jak 3)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 3
> - **Branch / Branche:** `jak3/features/city-behavior`
> - **Target Subsystems / Sous-systèmes ciblés:** Haven City faction system (`goal_src/jak3/levels/wascity/cty-faction.gc`), traffic & guard AI (`goal_src/jak3/levels/city/traffic/citizen/`), PC debug menu (`goal_src/jak3/pc/debug/default-menu-pc.gc`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

The **City Behavior** mod revamps Haven City's faction AI, traffic spawner systems, and guard combat logic in Jak 3. It introduces dynamic city operating modes switchable at any moment via the in-game PC Debug Menu:

1. **Mode Default (post-game canon — default):**
   - Restores post-game faction balance (`city-power-game-resolution`).
   - Freedom Faction (FF) guards patrol Haven City. In calm zones, attacking a guard triggers local squad defense while others remain neutral. In active warzones (Industrial, Slums), FF guards fight KG and Metalheads. Ambient city music plays continuously without interruption.
2. **Mode Jak 2 (peaceful patrols & collective chase):**
   - Recreates the iconic Jak 2 city dynamic: FF guards patrol peaceful streets without enemy monsters.
   - Attacking any guard triggers an immediate city-wide alert: combat music (`cityfi`) fires up, and all surrounding FF guards draw weapons to engage Jak.
   - Fast alert cooldown (~3 seconds) once Jak breaks line of sight and hides.
3. **Mode Chaos (all-out urban war):**
   - Transforms the entirety of Haven City into an active warzone.
   - Continuous battles between Freedom Faction guards, Krimzon Guards, and Metalhead predators across every district.
4. **City-Wide Polish & Hijack Fixes:**
   - Ejection and vertical ground search improved to 40m in `civilian.gc` / `citizen.gc` to prevent vehicle-hijacking pilot ejection glitches.
   - Guaranteed RAM retention for `ctypepa.DGO`.

## 2. Technical Architecture & Tooling

- `goal_src/jak3/levels/wascity/cty-faction.gc`: core dynamic city mode implementation (`*city-mode*`, `set-city-mode!`) and faction table assignments.
- `goal_src/jak3/levels/city/traffic/citizen/guard.gc`: collective alert triggers, hostile state transitions, and combat music management (`cityfi`).
- `goal_src/jak3/levels/city/common/ff-squad-control.gc`: Freedom Faction squad alert synchronization across sectors.
- `goal_src/jak3/levels/city/traffic/citizen/citizen.gc` & `civilian.gc`: hijacking pilot search radius fix.
- `goal_src/jak3/pc/debug/default-menu-pc.gc`: adds the `"City Mods"` menu with a visual checkbox `[X]` for live mode toggling.

## 3. How to Test & Play

1. Set the active game to Jak 3:
   ```bash
   task set-game-jak3
   ```
2. Hot-recompile in the REPL:
   ```lisp
   (mi)
   ```
3. Boot the game:
   ```bash
   task boot-game
   ```
4. Open the **PC Debug Menu** (`R3` or the debug hotkey).
5. Navigate to **`City Mods`** and select between:
   - `Mode Default (Fin du Jeu - Canon)`
   - `Mode Jak 2 (Gardes Neutres & Chasse)`
   - `Mode Chaos (Guerre Totale)`
6. Travel across Haven City sectors to test patrols, combat alerts, or urban warfare.

## 4. Current Status & Investigations

- **Stable / working as intended:** all three city modes switch live from the Debug Menu, the Jak 2-mode collective alert and `cityfi` music trigger reliably, and the 40m ground-search fix removes the carjack pilot-ejection glitch.
- **Consumed by `jak3/features/redguard-entity`:** that mod adds a red guard variant that only spawns while City Mode is `"Jak 2"`; the two branches are expected to merge together.
- **Not yet investigated:** whether the `~3s` alert cooldown should scale with the number of guards that saw Jak, and whether Chaos mode needs a spawn-budget cap in the densest districts to stay within the traffic cell/nav-mesh limits (see `jak3_modding_utilities` #02).

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) integrated directly into the OpenGOAL PC Debug Menu under "City Mods" (Jak 2 Mode vs Chaos Mode). | Implement "[Mod] City Behavior": Jak 2-style guard hostility & dynamic City War / Jak 2 mode switcher via the Debug Menu. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Added a third City Mode `'default` representing the post-game state (`city-power-game-resolution` faction strengths and default traffic/spawner quotas). Integrated the option in the PC Debug Menu under "City Mods". | Provide a full end-game spawn behavior option alongside Jak 2 mode and Chaos mode. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extended the move-to-ground vertical search radius to 40m in `citizen.gc` and `civilian.gc`, and appended `'ctypepa` to `*territory-list*` in `cty-faction.gc` for Jak 2 and Chaos modes. | Fix vehicle-hijack pilot ejection on carjacking across Haven City and guarantee `ctypepa.DGO` RAM retention. |
| 2026-08-30 | `docs/modding/current_mod/city-behavior_readme.md` (relocated from `docs/mods/`)<br>removed stale `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` | Relocated this readme to the mandated `docs/modding/current_mod/` path, made it fully bilingual, added the "Current Status & Investigations" section, and cleared the pre-migration flat `docs/` tree left over on this branch. | Bring the mod documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Le mod **City Behavior** refond l'IA des factions de Haven City, les systèmes de spawn du trafic et la logique de combat des gardes sur Jak 3. Il introduit des modes de fonctionnement de la ville dynamiques, commutables à tout moment via le menu Debug PC en jeu :

1. **Mode Default (canon post-jeu — par défaut) :**
   - Restaure l'équilibre des factions de fin de jeu (`city-power-game-resolution`).
   - Les gardes de la Freedom Faction (FF) patrouillent Haven City. En zone calme, attaquer un garde déclenche la défense de son escouade locale tandis que les autres restent neutres. Dans les zones de guerre actives (Industriel, Bidonvilles), les gardes FF combattent les KG et les Métatêtes. La musique d'ambiance de la ville joue en continu sans interruption.
2. **Mode Jak 2 (patrouilles paisibles & poursuite collective) :**
   - Recrée la dynamique urbaine emblématique de Jak 2 : les gardes FF patrouillent des rues paisibles sans monstres ennemis.
   - Attaquer n'importe quel garde déclenche une alerte immédiate à l'échelle de la ville : la musique de combat (`cityfi`) démarre, et tous les gardes FF alentour dégainent pour engager Jak.
   - Refroidissement d'alerte rapide (~3 secondes) une fois que Jak brise la ligne de vue et se cache.
3. **Mode Chaos (guerre urbaine totale) :**
   - Transforme l'intégralité de Haven City en zone de guerre active.
   - Combats continus entre les gardes de la Freedom Faction, les Krimzon Guards et les prédateurs Métatêtes dans tous les quartiers.
4. **Peaufinage à l'échelle de la ville & correctifs de détournement :**
   - Éjection et recherche verticale du sol portées à 40m dans `civilian.gc` / `citizen.gc` pour éviter les bugs d'éjection du pilote lors du détournement de véhicule.
   - Rétention RAM garantie pour `ctypepa.DGO`.

## 2. Architecture Technique & Outillage

- `goal_src/jak3/levels/wascity/cty-faction.gc` : implémentation centrale des modes de ville dynamiques (`*city-mode*`, `set-city-mode!`) et affectation des tables de factions.
- `goal_src/jak3/levels/city/traffic/citizen/guard.gc` : déclencheurs d'alerte collective, transitions vers l'état hostile et gestion de la musique de combat (`cityfi`).
- `goal_src/jak3/levels/city/common/ff-squad-control.gc` : synchronisation de l'alerte des escouades Freedom Faction entre secteurs.
- `goal_src/jak3/levels/city/traffic/citizen/citizen.gc` & `civilian.gc` : correctif du rayon de recherche du pilote lors du détournement.
- `goal_src/jak3/pc/debug/default-menu-pc.gc` : ajoute le menu `"City Mods"` avec une case à cocher visuelle `[X]` pour basculer les modes à chaud.

## 3. Commandes & Procédure de Test

1. Sélectionner Jak 3 comme jeu actif :
   ```bash
   task set-game-jak3
   ```
2. Recompiler à chaud dans le REPL :
   ```lisp
   (mi)
   ```
3. Lancer le jeu :
   ```bash
   task boot-game
   ```
4. Ouvrir le **menu Debug PC** (`R3` ou le raccourci debug).
5. Naviguer jusqu'à **`City Mods`** et choisir parmi :
   - `Mode Default (Fin du Jeu - Canon)`
   - `Mode Jak 2 (Gardes Neutres & Chasse)`
   - `Mode Chaos (Guerre Totale)`
6. Parcourir les secteurs de Haven City pour tester les patrouilles, les alertes de combat ou la guerre urbaine.

## 4. Statut Actuel & Investigations

- **Stable / fonctionne comme prévu :** les trois modes de ville se commutent à chaud depuis le menu Debug, l'alerte collective du mode Jak 2 et la musique `cityfi` se déclenchent de façon fiable, et le correctif de recherche du sol à 40m supprime le bug d'éjection du pilote lors du carjacking.
- **Consommé par `jak3/features/redguard-entity` :** ce mod ajoute une variante de garde rouge qui n'apparaît qu'en City Mode `"Jak 2"` ; la fusion des deux branches est attendue.
- **Non encore investigué :** si le refroidissement d'alerte de `~3s` devrait varier selon le nombre de gardes ayant vu Jak, et si le mode Chaos nécessite un plafond de budget de spawn dans les quartiers les plus denses pour rester dans les limites de cellules de trafic / nav-mesh (voir `jak3_modding_utilities` #02).

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Refonte du comportement des gardes Freedom Faction (neutres par défaut, agressivité collective à l'attaque, décroissance d'alerte rapide, musique de combat `cityfi`) et implémentation des City Modes dynamiques (`*city-mode*`, `set-city-mode!`) intégrés directement au menu Debug PC OpenGOAL sous « City Mods » (mode Jak 2 vs mode Chaos). | Implémenter « [Mod] City Behavior » : hostilité des gardes façon Jak 2 & guerre urbaine dynamique / commutateur de mode Jak 2 via le menu Debug. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Ajout d'un troisième City Mode `'default` représentant l'état post-jeu (forces de factions `city-power-game-resolution` et quotas de trafic/spawner par défaut). Option intégrée au menu Debug PC sous « City Mods ». | Fournir une option de comportement de spawn de fin de jeu complète aux côtés du mode Jak 2 et du mode Chaos. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extension du rayon de recherche vertical de mise au sol à 40m dans `citizen.gc` et `civilian.gc`, et ajout de `'ctypepa` à `*territory-list*` dans `cty-faction.gc` pour les modes Jak 2 et Chaos. | Corriger l'éjection du pilote lors du carjacking dans Haven City et garantir la rétention RAM de `ctypepa.DGO`. |
| 2026-08-30 | `docs/modding/current_mod/city-behavior_readme.md` (relocalisé depuis `docs/mods/`)<br>suppression des `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` obsolètes | Relocalisation de ce readme vers le chemin mandaté `docs/modding/current_mod/`, passage en bilingue complet, ajout de la section « Statut Actuel & Investigations », et nettoyage de l'ancien arbre `docs/` plat resté sur cette branche. | Mettre la documentation du mod en conformité avec la directive de modding. |
