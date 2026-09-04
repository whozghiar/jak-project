# Mod Readme — Yakow Killable & Behaviors (Jak 2) / Yakow Tuable & Comportements (Jak 2)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 2
> - **Branch / Branche:** `jak2/features/yakow_killable`
> - **Target Entity / Entité Cible:** `yakow` (`goal_src/jak2/levels/city/farm/yakow.gc`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

This mod enhances the Yakow animals located at the Hip Hog farm in Jak 2 by bringing back authentic Jak 1-style behaviors and adding a full combat/death loop.

- **Jak 1-Style Behaviors:**
  - **Flee Mechanic (`run-away`):** When approached or attacked by Jak, Yakows turn and flee in the opposite direction.
  - **Graze System (`graze` / `graze-kicked`):** Yakows alternate between idle grazing and active walking, with a dedicated reaction when kicked mid-graze.
  - **Kick Reaction (`kicked`):** Authentic animation selection between the traveling kick (`yakow-kicked-ja`) and the stationary kick (`yakow-kicked-in-place-ja`), depending on the Yakow's movement vector at the moment of impact.
- **Combat & Death Mechanic (`die`):**
  - Yakows now have 4 hit points (`default-hit-points = 4`) instead of being invulnerable, and `damage-amount-from-attack` returns 1 so any registered attack chips away at their health.
  - Upon death, the Yakow drops **6 dark eco pills** dispersed in a ~1.5 m radius around its position.
  - Plays the classic `"yakow-die"` cry (via the base `enemy` `dying` hook), then dissolves using the engine's generic `death-default` effect: **purple particles tracing the mesh/skeleton outline** as it fades out, layered with the `"enemy-fizz"` sound baked into that effect — the exact same system used by civilians and Crimson Guards. See the dedicated engine tip: [`jak2_modding_utilities/12_generic_death_effect_particles.md`](../jak2_modding_utilities/12_generic_death_effect_particles.md).

## 2. Technical Architecture & Tooling

- **Modified Files:**
  - `goal_src/jak2/levels/city/farm/yakow.gc`: Added `run-away`, `graze`, `graze-kicked`, `kicked`, `die` states; new tracking fields (`grazing`, `walk-run-blend`, `walk-turn-blend`, `run-mode`, `home-base`); overrode `damage-amount-from-attack` and `general-event-handler`.
  - `decompiler/config/jak2/ntsc_v1/{joint-node-info.min.json, art-group-info.min.json, type_casts.jsonc}`: Skeleton/joint bindings and type-cast hints for the `yakow` skeleton and its `code`/`method` overrides, required for the decompiler to resolve the animation-driving code cleanly.
  - *No custom external 3D models required:* Uses native in-game Jak 2 models, animations, and sound effects.
- **Reused Engine Systems (no new engine code needed):**
  - `nav-enemy` / `enemy` base states and event dispatch (`goal_src/jak2/engine/nav/nav-enemy.gc`, `goal_src/jak2/engine/ai/enemy.gc`) — hit-point handling, `dying`, death-flag bookkeeping.
  - The generic merc death-dissolve effect (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc`, `goal_src/jak2/engine/game/effect-control.gc`) via `(do-effect (-> self skel effect) 'death-default 0.0 -1)`.
  - `birth-pickup-at-point` for the dark eco pill drops (standard pickup-spawn helper, no custom pickup logic).

## 3. How to Test & Play

1. Set the active game to Jak 2:
   ```bash
   task set-game-jak2
   ```
2. Hot-recompile in the REPL:
   ```lisp
   (mi)
   ```
   Or in batch mode: `./goalc.exe --game jak2 -c "(mi)"` (must report `Successfully built all N targets`).
3. Boot the game and travel to the Hip Hog Farm in Haven City:
   ```bash
   task boot-game
   ```
4. Attack a Yakow with melee punches/spins or weapons to observe:
   - The kick animation and fleeing behavior on non-lethal hits.
   - On the killing blow (4th hit): the `"yakow-die"` cry, the purple mesh-dissolve particle effect with its "fizz" sound, and 6 dark eco pills scattering around the corpse's former position.

## 4. Current Status & Investigations

- **Stable / working as intended:** flee, graze, kick reactions, HP-based death, dark eco pill drops, and the purple death-dissolve VFX + classic cry.
- **Not yet investigated:** whether killed Yakows should respawn on level re-entry/task reset like other farm entities, and whether repeated kills should be capped per play session (no reward-farming guard is currently in place beyond the natural respawn rules inherited from `nav-enemy`/entity persistence).
- **Tip discovered and now documented separately** (previously undocumented in this repo): the generic `death-default` purple particle system is available to *any* skeleton-having `process-drawable` for free via `do-effect` — see [`jak2_modding_utilities/12_generic_death_effect_particles.md`](../jak2_modding_utilities/12_generic_death_effect_particles.md) for the full mechanism, code pattern, and pitfalls (in particular: always `suspend-for` before `cleanup-for-death`, or the particles never get a chance to spawn).

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2025-07-19 | `goal_src/jak2/levels/city/farm/yakow.gc` | Added Jak 1-style states (`run-away`, `graze`, `graze-kicked`, `die`), added tracking fields (`grazing`, `walk-run-blend`, `run-mode`, `home-base`), set `damage-amount-from-attack` to 1. | Recreate Jak 1 Yakow behaviors in Jak 2 with dark eco drop. |
| 2026-08-13 | `goal_src/jak2/levels/city/farm/yakow.gc` | Polished `kicked` state (traveling vs in-place kick based on nav travel), raised HP to 4 hits, drop 6 dark eco pills, replaced particle effect with `group-land-poof-drt`. | Authentic Jak 1 feel, robust death VFX and balanced reward. |
| 2026-08-16 | `goal_src/jak2/levels/city/farm/yakow.gc`, `docs/modding/jak2_modding_utilities/12_generic_death_effect_particles.md`, `docs/modding/current_mod/yakow_killable_readme.md` | Replaced the placeholder dust poof (`group-land-poof-drt` + manual `"enemy-fizz"`) in the `die` state's `:code` with `(do-effect (-> self skel effect) 'death-default 0.0 -1)`, the generic engine death-dissolve effect (purple mesh/skeleton-outline particles), followed by a 1s `suspend-for` so it can play out before cleanup. The classic `"yakow-die"` sound was already playing via `(dying self)` in `:enter` and is unaffected. Documented the underlying generic death-effect engine system as a standalone modding tip (kept isolated, the aggregated `jak2_modding_utilities.md` was intentionally left untouched). Relocated this readme from the legacy `docs/mods/` path to the mandated `docs/modding/current_mod/` path and made it fully bilingual. | Give the Yakow the same authentic death VFX used by other Jak II enemies instead of a generic landing-dust placeholder, and bring the mod's documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Ce mod enrichit les Yakows présents à la ferme du Hip Hog dans Jak 2 en réintroduisant des comportements fidèles à Jak 1 et en ajoutant une boucle complète de combat/mort.

- **Comportements Façon Jak 1 :**
  - **Mécanique de Fuite (`run-away`) :** Quand Jak s'approche ou attaque, le Yakow se retourne et fuit dans la direction opposée.
  - **Système de Pâturage (`graze` / `graze-kicked`) :** Le Yakow alterne entre broutage à l'arrêt et marche active, avec une réaction dédiée s'il est frappé pendant qu'il broute.
  - **Réaction au Coup de Pied (`kicked`) :** Sélection authentique de l'animation entre le coup de pied en mouvement (`yakow-kicked-ja`) et le coup de pied à l'arrêt (`yakow-kicked-in-place-ja`), selon le vecteur de déplacement du Yakow au moment de l'impact.
- **Mécanique de Combat & de Mort (`die`) :**
  - Le Yakow possède désormais 4 points de vie (`default-hit-points = 4`) au lieu d'être invulnérable, et `damage-amount-from-attack` renvoie 1 afin que toute attaque reconnue entame sa santé.
  - À sa mort, le Yakow lâche **6 pilules d'éco sombre** dispersées dans un rayon d'environ 1,5 m autour de sa position.
  - Il émet le cri classique `"yakow-die"` (via le hook `dying` de base d'`enemy`), puis se dissout avec l'effet générique `death-default` du moteur : **des particules violettes traçant le contour du maillage/squelette** pendant qu'il disparaît, superposées au son `"enemy-fizz"` intégré à cet effet — exactement le même système que celui utilisé par les civils et les Crimson Guards. Voir le tip moteur dédié : [`jak2_modding_utilities/12_generic_death_effect_particles.md`](../jak2_modding_utilities/12_generic_death_effect_particles.md).

## 2. Architecture Technique & Outillage

- **Fichiers Modifiés :**
  - `goal_src/jak2/levels/city/farm/yakow.gc` : Ajout des états `run-away`, `graze`, `graze-kicked`, `kicked`, `die` ; nouveaux champs de suivi (`grazing`, `walk-run-blend`, `walk-turn-blend`, `run-mode`, `home-base`) ; surcharge de `damage-amount-from-attack` et `general-event-handler`.
  - `decompiler/config/jak2/ntsc_v1/{joint-node-info.min.json, art-group-info.min.json, type_casts.jsonc}` : Liaisons de squelette/joints et indices de cast de types pour le squelette `yakow` et ses surcharges de `code`/`method`, nécessaires pour que le décompilateur résolve proprement le code pilotant les animations.
  - *Aucun modèle 3D externe requis :* S'appuie entièrement sur les modèles, animations et sons natifs du jeu de base Jak 2.
- **Systèmes Moteur Réutilisés (aucun nouveau code moteur requis) :**
  - Les états et le dispatch d'événements de base `nav-enemy` / `enemy` (`goal_src/jak2/engine/nav/nav-enemy.gc`, `goal_src/jak2/engine/ai/enemy.gc`) — gestion des points de vie, `dying`, suivi des flags de mort.
  - L'effet générique de dissolution de mort merc (`goal_src/jak2/engine/gfx/foreground/merc/merc-death.gc`, `goal_src/jak2/engine/game/effect-control.gc`) via `(do-effect (-> self skel effect) 'death-default 0.0 -1)`.
  - `birth-pickup-at-point` pour le lâcher des pilules d'éco sombre (helper standard de spawn de pickups, sans logique de pickup custom).

## 3. Commandes & Procédure de Test

1. Sélectionner Jak 2 comme jeu actif :
   ```bash
   task set-game-jak2
   ```
2. Recompiler à chaud dans le REPL :
   ```lisp
   (mi)
   ```
   Ou en mode batch : `./goalc.exe --game jak2 -c "(mi)"` (doit afficher `Successfully built all N targets`).
3. Lancer le jeu et se rendre à la ferme du Hip Hog à Haven City :
   ```bash
   task boot-game
   ```
4. Attaquer un Yakow au corps-à-corps (coups de poing/spin) ou aux armes pour observer :
   - L'animation de coup de pied et le comportement de fuite lors des coups non mortels.
   - Au coup fatal (4ᵉ coup) : le cri `"yakow-die"`, l'effet de particules violettes de dissolution du maillage avec son son "fizz", et 6 pilules d'éco sombre se dispersant autour de l'ancienne position du corps.

## 4. Statut Actuel & Investigations

- **Stable / fonctionnant comme prévu :** fuite, pâturage, réactions au coup de pied, mort basée sur les PV, lâcher de pilules d'éco sombre, et VFX de dissolution violette + cri classique.
- **Non encore investigué :** si les Yakows tués doivent réapparaître au rechargement du niveau/reset de tâche comme d'autres entités de la ferme, et si les kills répétés doivent être plafonnés par session de jeu (aucun garde-fou anti-farming n'est en place au-delà des règles naturelles de respawn héritées de `nav-enemy`/de la persistance des entités).
- **Astuce découverte et désormais documentée séparément** (jusqu'ici non documentée dans ce dépôt) : le système générique de particules violettes `death-default` est disponible gratuitement pour **n'importe quel** `process-drawable` possédant un squelette, via `do-effect` — voir [`jak2_modding_utilities/12_generic_death_effect_particles.md`](../jak2_modding_utilities/12_generic_death_effect_particles.md) pour le mécanisme complet, le pattern de code et les pièges (en particulier : toujours faire un `suspend-for` avant `cleanup-for-death`, sinon les particules n'ont jamais l'occasion d'apparaître).

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2025-07-19 | `goal_src/jak2/levels/city/farm/yakow.gc` | Ajout des états façon Jak 1 (`run-away`, `graze`, `graze-kicked`, `die`), ajout des champs de suivi (`grazing`, `walk-run-blend`, `run-mode`, `home-base`), passage de `damage-amount-from-attack` à 1. | Recréer les comportements du Yakow de Jak 1 dans Jak 2 avec lâcher d'éco sombre. |
| 2026-08-13 | `goal_src/jak2/levels/city/farm/yakow.gc` | Peaufinage de l'état `kicked` (coup en mouvement vs à l'arrêt selon le déplacement nav), PV portés à 4 coups, lâcher de 6 pilules d'éco sombre, remplacement de l'effet de particules par `group-land-poof-drt`. | Ressenti Jak 1 authentique, VFX de mort robuste et récompense équilibrée. |
| 2026-08-16 | `goal_src/jak2/levels/city/farm/yakow.gc`, `docs/modding/jak2_modding_utilities/12_generic_death_effect_particles.md`, `docs/modding/current_mod/yakow_killable_readme.md` | Remplacement du poof de poussière placeholder (`group-land-poof-drt` + `"enemy-fizz"` manuel) dans le `:code` de l'état `die` par `(do-effect (-> self skel effect) 'death-default 0.0 -1)`, l'effet générique moteur de dissolution de mort (particules violettes du contour du maillage/squelette), suivi d'un `suspend-for` d'1s pour le laisser se dérouler avant le nettoyage. Le son classique `"yakow-die"` était déjà joué via `(dying self)` dans `:enter` et reste inchangé. Documentation du système générique de mort du moteur en tant que tip de modding autonome et isolé (le fichier agrégé `jak2_modding_utilities.md` a volontairement été laissé intact). Relocalisation de ce readme depuis l'ancien chemin `docs/mods/` vers le chemin mandaté `docs/modding/current_mod/`, et passage en bilingue complet. | Offrir au Yakow le même VFX de mort authentique que les autres ennemis de Jak II au lieu d'un placeholder générique de poussière, et mettre la documentation du mod en conformité avec la directive de modding. |
