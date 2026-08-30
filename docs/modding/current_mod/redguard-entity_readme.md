# Mod Readme — Crimson Redguard Entity (Jak 3) / Entité Crimson Redguard (Jak 3)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 3
> - **Branch / Branche:** `jak3/features/redguard-entity`
> - **Target Subsystems / Sous-systèmes ciblés:** Traffic Guards (`goal_src/jak3/levels/city/traffic/citizen/guard.gc`), level `ctypesa` DGO, custom model pipeline (`custom_assets/jak3/models/`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

This mod introduces the **Crimson Redguard** custom entity to Haven City in Jak 3:

- **Red Freedom Faction Guard:** A red-armored guard variant inspired by the classic Krimzon Guard aesthetic, patrolling alongside blue Freedom Faction guards and yellow Dark Guards in Haven City.
- **Exclusive City Mode Integration:** Appears dynamically when City Mode is set to `"Jak 2"` (see the `jak3/features/city-behavior` mod) via a 3-way random spawner roll (`blue` / `dark-guard` / `red-guard`).
- **Non-Destructive Mesh Overriding:** Uses a dedicated high-fidelity 3D model (`crimson-redguard-lod0.glb`) while seamlessly reusing the existing `skel-crimson-guard` joint and animation tree without duplicating memory buffers.

## 2. Technical Architecture & Tooling

- **Custom Assets & Models:**
  - `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb`: custom red geometry and textures injected into level `ctypesa`.
  - `goal_src/jak3/dgos/ctypesa.gd`: registers `crimson-redguard-ag.go`.
  - `goal_src/jak3/game.gp`: declares `(build-actor "crimson-redguard")` with file-entry map registration.
- **GOAL Logic:**
  - `goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc`: adds the `citizen-flag red-guard` bit.
  - `goal_src/jak3/levels/city/traffic/citizen/guard.gc`: implements the 3-way random spawner distribution in `citizen-method-194` and dynamic `mgeo` overriding in `crimson-guard-method-267`.
- **Reused Engine Systems (no new engine code):**
  - `skel-crimson-guard` joint/animation tree — the custom model rides the existing skeleton, so no new animation data or joint bindings are needed.
  - The existing Freedom Faction guard AI, alert, and squad logic — the Redguard is a pure visual variant and inherits all behavior.

## 3. How to Test & Play

1. Set the active game to Jak 3:
   ```bash
   task set-game-jak3
   ```
2. Run extraction to compile the custom model assets:
   ```bash
   task extract
   ```
3. Recompile the game in the REPL (`task repl`):
   ```lisp
   (mi)
   ```
4. Boot the game:
   ```bash
   task boot-game
   ```
5. In the PC Debug Menu (`R3`), open **`City Mods`** and select **`Mode Jak 2`**.
6. Travel to Haven City South (`ctypesa`) to encounter patrolling Crimson Redguards mixed in with the blue and Dark Guard variants.

## 4. Current Status & Investigations

- **Stable / working as intended:** custom model builds and links into `ctypesa`, the `red-guard` spawner roll fires at roughly one-in-three among Jak 2 mode guards, and the red mesh renders on the shared `skel-crimson-guard` skeleton with correct animation.
- **Depends on `jak3/features/city-behavior`:** the Redguard only spawns while City Mode is `"Jak 2"`. Outside that mod's `*city-mode*` switch there is no spawn path; merging the two branches is expected.
- **Not yet investigated:** whether the custom art group needs an explicit residency guarantee for districts other than `ctypesa` if the spawner is later extended city-wide, and whether the 3-way roll should be weighted rather than uniform.

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) in the PC Debug Menu. *(shared lineage with `jak3/features/city-behavior`)* | Provide the City Behavior mode switcher this mod hooks into. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Added the `'default` post-game city mode to the Debug Menu. *(shared lineage with `jak3/features/city-behavior`)* | Provide a full end-game spawn behavior option. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extended the move-to-ground vertical search radius to 40m in `citizen.gc` and `civilian.gc`, appended `'ctypepa` to `*territory-list*`. *(shared lineage with `jak3/features/city-behavior`)* | Fix vehicle-hijack pilot ejection and guarantee `ctypepa` RAM retention. |
| 2026-08-11 | `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb`<br>`goal_src/jak3/game.gp`<br>`goal_src/jak3/dgos/ctypesa.gd`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/guard.gc` | Added the custom Crimson Redguard model into `ctypesa`, configured the actor build in `game.gp`, added the `citizen-flag red-guard` bit, and implemented the random 3-way guard roll with mesh override in `guard.gc`. | Add the Crimson Redguard entity variant in City Mode "Jak 2". |
| 2026-08-30 | `docs/modding/current_mod/redguard-entity_readme.md` (relocated from `docs/mods/`)<br>removed stale `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` | Relocated this readme to the mandated `docs/modding/current_mod/` path, made it fully bilingual, added the "Current Status & Investigations" section, and cleared the pre-migration flat `docs/` tree left over on this branch. | Bring the mod documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Ce mod introduit l'entité custom **Crimson Redguard** dans Haven City sur Jak 3 :

- **Garde de la Freedom Faction rouge :** Une variante de garde à l'armure rouge inspirée de l'esthétique classique des Krimzon Guards, patrouillant aux côtés des gardes bleus de la Freedom Faction et des Dark Guards jaunes dans Haven City.
- **Intégration exclusive au City Mode :** Apparaît dynamiquement lorsque le City Mode est réglé sur `"Jak 2"` (voir le mod `jak3/features/city-behavior`), via un tirage aléatoire à 3 issues du spawner (`blue` / `dark-guard` / `red-guard`).
- **Surcharge de maillage non destructive :** Utilise un modèle 3D haute fidélité dédié (`crimson-redguard-lod0.glb`) tout en réutilisant sans heurt l'arbre de joints et d'animations `skel-crimson-guard` existant, sans dupliquer de tampon mémoire.

## 2. Architecture Technique & Outillage

- **Assets & modèles custom :**
  - `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb` : géométrie et textures rouges custom injectées dans le niveau `ctypesa`.
  - `goal_src/jak3/dgos/ctypesa.gd` : enregistre `crimson-redguard-ag.go`.
  - `goal_src/jak3/game.gp` : déclare `(build-actor "crimson-redguard")` avec l'enregistrement dans la file-entry map.
- **Logique GOAL :**
  - `goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc` : ajoute le bit `citizen-flag red-guard`.
  - `goal_src/jak3/levels/city/traffic/citizen/guard.gc` : implémente la distribution du spawner aléatoire à 3 issues dans `citizen-method-194` et la surcharge dynamique de `mgeo` dans `crimson-guard-method-267`.
- **Systèmes moteur réutilisés (aucun nouveau code moteur) :**
  - L'arbre de joints/animations `skel-crimson-guard` — le modèle custom monte sur le squelette existant, donc aucune donnée d'animation ni liaison de joint nouvelle n'est nécessaire.
  - L'IA de garde, l'alerte et la logique d'escouade de la Freedom Faction existantes — le Redguard est une pure variante visuelle et hérite de tout le comportement.

## 3. Commandes & Procédure de Test

1. Sélectionner Jak 3 comme jeu actif :
   ```bash
   task set-game-jak3
   ```
2. Lancer l'extraction pour compiler les assets de modèle custom :
   ```bash
   task extract
   ```
3. Recompiler le jeu dans le REPL (`task repl`) :
   ```lisp
   (mi)
   ```
4. Lancer le jeu :
   ```bash
   task boot-game
   ```
5. Dans le menu Debug PC (`R3`), ouvrir **`City Mods`** et sélectionner **`Mode Jak 2`**.
6. Se rendre au sud de Haven City (`ctypesa`) pour rencontrer des Crimson Redguards en patrouille, mêlés aux variantes bleue et Dark Guard.

## 4. Statut Actuel & Investigations

- **Stable / fonctionne comme prévu :** le modèle custom se compile et se lie dans `ctypesa`, le tirage du spawner `red-guard` se déclenche environ une fois sur trois parmi les gardes du mode Jak 2, et le maillage rouge se rend sur le squelette partagé `skel-crimson-guard` avec l'animation correcte.
- **Dépend de `jak3/features/city-behavior` :** le Redguard n'apparaît que si le City Mode vaut `"Jak 2"`. En dehors du commutateur `*city-mode*` de ce mod, il n'y a aucun chemin d'apparition ; la fusion des deux branches est attendue.
- **Non encore investigué :** si le groupe d'art custom nécessite une garantie de résidence explicite pour des quartiers autres que `ctypesa` au cas où le spawner serait étendu à toute la ville, et si le tirage à 3 issues devrait être pondéré plutôt qu'uniforme.

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`<br>`goal_src/jak3/levels/city/common/ff-squad-control.gc`<br>`goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Refonte du comportement des gardes Freedom Faction (neutres par défaut, agressivité collective à l'attaque, décroissance d'alerte rapide, musique de combat `cityfi`) et implémentation des City Modes dynamiques (`*city-mode*`, `set-city-mode!`) dans le menu Debug PC. *(lignée partagée avec `jak3/features/city-behavior`)* | Fournir le commutateur de mode City Behavior auquel ce mod se raccorde. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/pc/debug/default-menu-pc.gc` | Ajout du mode ville post-jeu `'default` au menu Debug. *(lignée partagée avec `jak3/features/city-behavior`)* | Fournir une option de comportement de spawn de fin de jeu complète. |
| 2026-08-10 | `goal_src/jak3/levels/wascity/cty-faction.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/civilian.gc` | Extension du rayon de recherche vertical de mise au sol à 40m dans `citizen.gc` et `civilian.gc`, ajout de `'ctypepa` à `*territory-list*`. *(lignée partagée avec `jak3/features/city-behavior`)* | Corriger l'éjection du pilote lors du détournement de véhicule et garantir la rétention RAM de `ctypepa`. |
| 2026-08-11 | `custom_assets/jak3/models/ctypesa/crimson-redguard-lod0.glb`<br>`goal_src/jak3/game.gp`<br>`goal_src/jak3/dgos/ctypesa.gd`<br>`goal_src/jak3/levels/city/traffic/citizen/citizen-h.gc`<br>`goal_src/jak3/levels/city/traffic/citizen/guard.gc` | Ajout du modèle Crimson Redguard custom dans `ctypesa`, configuration du build d'acteur dans `game.gp`, ajout du bit `citizen-flag red-guard`, et implémentation du tirage de garde aléatoire à 3 issues avec surcharge de maillage dans `guard.gc`. | Ajouter la variante d'entité Crimson Redguard en City Mode « Jak 2 ». |
| 2026-08-30 | `docs/modding/current_mod/redguard-entity_readme.md` (relocalisé depuis `docs/mods/`)<br>suppression des `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` obsolètes | Relocalisation de ce readme vers le chemin mandaté `docs/modding/current_mod/`, passage en bilingue complet, ajout de la section « Statut Actuel & Investigations », et nettoyage de l'ancien arbre `docs/` plat resté sur cette branche. | Mettre la documentation du mod en conformité avec la directive de modding. |
