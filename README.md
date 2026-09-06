# Crimson Blue Guard — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fblueguard-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Adds a blue-recolored Crimson Guard as its own, standalone entity — a new GOAL type
(`crimson-blue-guard`) that reuses 100% of the stock `crimson-guard`'s behavior, animations and
sounds, only with a re-textured mesh. It appears in Haven City mixed into the normal ambient
guard traffic, alongside the regular red guards.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/blueguard`

## ✨ Key Features
- **New standalone entity:** `crimson-blue-guard` is a real GOAL type (subtype of
  `crimson-guard`), not a global texture swap — regular red guards keep spawning too.
- **Identical to the stock guard in every other respect:** animations, sounds, death (including native purple particle dissolution and ground knockdown death), collision,
  weapon loadout — all inherited unchanged (same slot indices, see the technical doc); only the
  mesh/skeleton-group and the one behavior difference below are different.
- **Its own faction behavior:** unlike the stock guard, it is passive toward Jak by default and
  never joins a general city alert against him. If Jak personally attacks it, it fights back
  without raising the city-wide alarm.
- **Manual "fight the other guards" trigger:** `crimson-blue-guard-attack-guards`, a small function
  that makes it go hostile toward the nearest red `crimson-guard` — never automatic, called
  explicitly (REPL or code).
- **Mixed into ambient city traffic:** the traffic manager now spawns the blue variant for a
  configurable fraction of ambient guard spawns (`*crimson-blue-guard-ratio*`, default 1-in-8),
  right alongside the stock guard.
- **"Mods" debug menu tab (City Peaceful & City Insurrection):** the debug menu includes a dedicated "Mods" tab:
  - `City Peaceful` (**Fully Implemented & Verified**): ambient blue guards spawn in coordinated 2 to 3 member patrol squads with tight formation navigation, adaptive speed modulation, automatic leader re-election, and diverse weapon loadouts (taser, rifle, grenade launcher). Squad members defend each other in mutual retaliatory defense without raising the city alarm, and enjoy complete friendly-fire immunity.
  - `City Insurrection` (**Fully Implemented**): a three-front territorial civil war across Haven City, with districts classified by loaded city-level name (never hardcoded coordinates). The ambient city-guard pool is populated with whichever faction owns the district Jak is in, so districts are strictly territorial with no wasted spawn slots. **Slums** (`ctysluma`/`b`/`c`) — Blue rebel stronghold: strictly 100% lone blue guards with random weapons, and an alert-free safe haven (any wanted level snaps to 0 on entry and cannot rise; hitting a blue guard triggers only its personal self-defense). **Loyalist districts** (everything else) — strictly 100% stock red/yellow guards, with fully vanilla police density and behaviour toward Jak. **War Zone** — a configurable district (`Debug ▸ Mods ▸ Insurrection war zone`: **Industrial** `ctyinda`/`b` by default, or Port / Bazaar / Farmland / Market): ~30 guards at 50/50 blue vs red (two guard pools, all civilians/metalheads/vehicles removed, tighter spawn packing), and the two factions hunt and open fire on each other on sight (bursts, grenades, taser charges) with a ~60m acquisition range — a living background battle that never raises Jak's wanted level (hitting a red guard here raises nothing either; only loyalist districts run the wanted system). Switching modes or the war-zone district re-rolls the city guards immediately; crossing a district border crossfades them over ~1-2 seconds.
- **Faithful Crimson Guard Combat AI:** rifle and grenade launcher guards maintain tactical standoff distance (engaging targets up to 50m away), fire reactive bursts or parabolic grenades, and execute evasive combat rolls (`roll-left` / `roll-right`). Melee rifle-butt strikes are strictly an emergency close-quarters counter (< 2.5m), followed immediately by an evasive roll to resume shooting. Taser guards charge and shock with high-voltage electric arcs.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** `task build-release-game` (or `task build-debug-game`) — required. The
  `build-actor` tool (`goalc/build_actor/jak2/build_actor.cpp`) and the `goalc` data-compiler
  (`goalc/make/Tools.cpp`) both gained a new opt-in `:native-header` flag used to build this
  actor's art-group. See `docs/modding/build_and_iteration_workflow.md`.
- **Details:** engine/compiler C++ was modified (see the "Engine Changes" table in the technical
  doc below).
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Required, once — the guard's actual drawable geometry + textures ("Circuit 2", see
  the technical doc) are baked into `GAME.fr3` by the decompiler, from
  `custom_assets/jak2/models/common/crimson-blue-guard-lod0.glb`. Needs a legally-dumped Jak 2 ISO.
```bash
task extract
```
Check the log for `Adding custom model crimson-blue-guard-lod0 to common` and no
`merc failed to find texture` error for it. This step does **not** need to be repeated after a
pure GOAL-code change (`(mi)` is enough) — only after the `.glb` model itself changes.

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*
Roughly 1 in 8 ambient guard spawns in Haven City will be blue. To see it faster while testing,
set `(set! *crimson-blue-guard-ratio* 1)` at the REPL once booted — every ambient guard spawn
becomes blue until you reset it back to `8` (or any N you like). You can also spawn one right in
front of you regardless of the ratio with `(spawn-crimson-blue-guard-debug 0)` (baton guard) or
`(spawn-crimson-blue-guard-debug 1)` (gun-equipped guard).

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/blue_guard_reskin_readme.md`](docs/modding/current_mod/blue_guard_reskin_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Ajoute un garde crimson recoloré en bleu comme une entité à part entière — un nouveau type GOAL
(`crimson-blue-guard`) qui réutilise à 100% le comportement, les animations et les sons du garde
crimson d'origine (`crimson-guard`), seul le mesh/la texture change. Il apparaît dans Haven City
mélangé au trafic ambiant normal, aux côtés des gardes rouges classiques.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/blueguard`

## ✨ Fonctionnalités Clés
- **Nouvelle entité à part entière :** `crimson-blue-guard` est un vrai type GOAL (sous-type de
  `crimson-guard`), pas un simple remplacement de texture global — les gardes rouges classiques
  continuent d'apparaître normalement.
- **Identique au garde classique en tout le reste :** animations, sons, mort (dissolution en particules violettes et maintien au sol après projection), collision, arsenal —
  tout est hérité sans modification (mêmes indices de slot, voir la doc technique) ; seuls le
  mesh/skeleton-group et la différence de comportement ci-dessous changent.
- **Sa propre logique de faction :** contrairement au garde classique, il est passif envers Jak par
  défaut et ne rejoint jamais une alerte générale de la ville contre lui. Si Jak l'attaque
  personnellement, il riposte sans déclencher l'alarme de la ville.
- **Déclencheur manuel « combattre les autres gardes » :** `crimson-blue-guard-attack-guards`, une
  petite fonction qui le fait devenir hostile envers le `crimson-guard` rouge le plus proche —
  jamais automatique, appelée explicitement (REPL ou code).
- **Mélangé au trafic ambiant de la ville :** le traffic-manager fait maintenant apparaître la
  variante bleue pour une fraction configurable des spawns de gardes ambiants
  (`*crimson-blue-guard-ratio*`, 1 sur 8 par défaut), aux côtés du garde classique.
- **Onglet menu debug « Mods » (City Peaceful & City Insurrection) :** le menu debug comprend un onglet « Mods » :
  - `City Peaceful` (**Entièrement Implémenté & Vérifié**) : les gardes bleus ambiants patrouillent en escouades coordonnées de 2 à 3 membres avec déplacement en formation serrée, modulation adaptative de la vitesse, réélection automatique du leader, et répartition d'armes variées (taser, fusil laser, lance-grenades). Les membres de l'escouade ripostent ensemble en cas d'agression sans déclencher l'alarme de la ville, et bénéficient d'une immunité totale aux tirs alliés.
  - `City Insurrection` (**Entièrement Implémenté**) : une guerre civile territoriale à trois fronts dans Haven City, les quartiers étant classés par le nom du niveau de ville chargé (jamais de coordonnées codées en dur). Le pool de gardes ambiants de la ville est peuplé de la faction qui contrôle le quartier où se trouve Jak, donc les quartiers sont strictement territoriaux sans aucun slot de spawn gaspillé. **Slums** (`ctysluma`/`b`/`c`) — bastion des rebelles bleus : strictement 100% de gardes bleus solitaires à arsenal aléatoire, et zone refuge sans alerte (tout niveau de recherche retombe à 0 à l'entrée et ne peut plus monter ; frapper un garde bleu ne déclenche que son autodéfense personnelle). **Quartiers loyalistes** (tout le reste) — strictement 100% de gardes rouges/jaunes classiques, avec une densité et un comportement de police strictement d'origine envers Jak. **Zone de Guerre** — un quartier configurable (`Debug ▸ Mods ▸ Insurrection war zone` : **Industriel** `ctyinda`/`b` par défaut, ou Port / Bazar / Fermes / Marché) : ~30 gardes en 50/50 bleus vs rouges (deux pools de gardes, tous les civils/têtes-de-métal/véhicules retirés, spawn plus serré), et les deux factions se repèrent et ouvrent le feu mutuellement à vue (rafales, grenades, charges au taser) avec une portée d'acquisition de ~60 m — une bataille de fond vivante qui ne fait jamais monter le niveau de recherche de Jak (frapper un garde rouge ici ne déclenche rien non plus ; seuls les quartiers loyalistes appliquent le système de recherche). Basculer le mode ou le quartier de guerre re-tire les gardes immédiatement ; franchir une frontière de quartier les fait faire un fondu sur ~1-2 secondes.
- **IA de Combat Fidèle aux Crimson Guards :** les gardes armés d'un fusil ou d'un lance-grenades maintiennent une distance d'engagement tactique (jusqu'à 50 m), tirent des rafales/projectiles avec visée réactive et enchaînent des roulades d'esquive latérales (`roll-left` / `roll-right`). Les coups de crosse sont strictement réservés au contact d'urgence (< 2,5 m) et sont immédiatement suivis d'une roulade d'esquive pour reprendre le tir à distance. Les gardes au taser foncent au contact pour électrocuter avec des arcs électriques.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** `task build-release-game` (ou `task build-debug-game`) — requise. L'outil
  `build-actor` (`goalc/build_actor/jak2/build_actor.cpp`) et le compilateur de données `goalc`
  (`goalc/make/Tools.cpp`) ont tous deux reçu un nouveau flag optionnel `:native-header` utilisé
  pour construire l'art-group de cet acteur. Voir `docs/modding/build_and_iteration_workflow.md`.
- **Détails :** du C++ moteur/compilateur a été modifié (voir le tableau « Changements Moteur »
  dans la doc technique ci-dessous).
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise, une fois — la géométrie de rendu + textures réelles du garde
  (« Circuit 2 », voir la doc technique) sont cuites dans `GAME.fr3` par le décompilateur, à partir
  de `custom_assets/jak2/models/common/crimson-blue-guard-lod0.glb`. Nécessite un ISO Jak 2
  légalement dumpé.
```bash
task extract
```
Vérifiez dans le log la ligne `Adding custom model crimson-blue-guard-lod0 to common` et l'absence
d'erreur `merc failed to find texture` pour lui. Cette étape n'est **pas** à refaire après un
simple changement de code GOAL (`(mi)` suffit) — seulement quand le `.glb` lui-même change.

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou via le REPL OpenGOAL avec `task repl`, puis `(mi)` et `(r)`).*
Environ 1 spawn de garde ambiant sur 8 sera bleu dans Haven City. Pour le voir plus vite pendant
les tests, faites `(set! *crimson-blue-guard-ratio* 1)` au REPL une fois le jeu lancé — chaque
garde ambiant spawné devient bleu jusqu'à ce que vous remettiez `8` (ou la valeur de votre choix).
Vous pouvez aussi en faire apparaître un directement devant vous, sans dépendre du ratio, avec
`(spawn-crimson-blue-guard-debug 0)` (garde matraque) ou `(spawn-crimson-blue-guard-debug 1)`
(garde armé d'un fusil).

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/blue_guard_reskin_readme.md`](docs/modding/current_mod/blue_guard_reskin_readme.md)

---
*(AI-assisted)*
