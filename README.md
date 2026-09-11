# Crimson Blue Guard — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fcity--peaceful-green.svg" alt="Branch">
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
- **Active Branch:** `jak2/features/city-peaceful` — base blue-guard traffic + the **City Peaceful**
  mode: ambient blue guards patrol as neutral 2-3 member squads.

### Branch family
| Branch | Adds |
|---|---|
| `jak2/features/blueguard-traffic` | base: `crimson-blue-guard` entity, faithful combat AI, ambient city-traffic spawning, modular hook layer |
| **`jak2/features/city-peaceful`** *(this one)* | neutral blue patrol **squads** — formation nav, adaptive follower speed, leader re-election, mutual defense, faction friendly-fire immunity |
| `jak2/features/city-insurrection` | three-front **territorial civil war** — district zoning, autonomous inter-faction combat, alert-free zones, debug-menu war-zone picker |
| `jak2/features/blueguard` | both modes together (mutually exclusive at runtime) |

**The mod ships OFF.** It is enabled from `Debug ▸ Mods ▸ crimson-blueguard-peaceful ▸ Enable`.
With it **off, Haven City is byte-for-byte stock Jak 2** — no blue guards spawn, ambient
guard-vehicle counts are the retail values, alerts and civilians behave normally. Turning it
**on** enables the whole package at once: blue ambient guards **and** the neutral patrol-squad
behaviour. The choice re-rolls the ambient guards on the spot and persists across level reloads.

## ✨ Key Features
- **New standalone entity:** `crimson-blue-guard` is a real GOAL type (subtype of
  `crimson-guard`), not a global texture swap — regular red guards keep spawning too.
- **Identical to the stock guard in every other respect:** animations, sounds, death (including native purple particle dissolution and ground knockdown death), collision,
  weapon loadout — all inherited unchanged (same slot indices, see the technical doc); only the
  mesh/skeleton-group and the one behavior difference below are different.
- **Its own faction behavior:** unlike the stock guard, it is passive toward Jak by default and
  never joins a general city alert against him. If Jak personally attacks it, it fights back
  without raising the city-wide alarm. Enhanced resilience: 8 HP (double standard guard health)
  ensures durable tactical squad combat.
- **Manual "fight the other guards" trigger:** `crimson-blue-guard-attack-guards`, a small function
  that makes it go hostile toward the nearest red `crimson-guard` — never automatic, called
  explicitly (REPL or code).
- **Mixed into ambient city traffic:** the traffic manager spawns the blue variant for a
  configurable fraction of ambient guard spawns (`*crimson-blue-guard-ratio*`, default 1-in-2 of
  the id-parity pool), right alongside the stock guard.
- **Faithful Crimson Guard Combat AI:** rifle and grenade launcher guards maintain tactical standoff distance (engaging targets up to 50m away), fire reactive bursts or parabolic grenades, and execute evasive combat rolls (`roll-left` / `roll-right`). Melee rifle-butt strikes are strictly an emergency close-quarters counter (< 2.5m), followed immediately by an evasive roll to resume shooting. Taser guards charge and shock with high-voltage electric arcs.
- **City Peaceful mode** (`mod-city-peaceful.gc`, toggled from the Mods debug tab): when on, a
  freshly-activated ambient blue guard becomes a **squad leader** and pulls 1-2 followers behind
  it — tight formation navigation with adaptive follower speed, automatic leader re-election on
  death, distinct weapon loadouts across the squad, and mutual retaliatory defense (hit one, the
  whole squad turns on the attacker) — all without ever sounding the city alarm. Blue guards are
  completely immune to friendly fire from each other.
- **Blue Guard Vehicle Drivers (Peaceful mode):** Krimson Guard patrol cruisers (`vehicle-guard`)
  are piloted by blue guards (`crimson-blue-guard-rider`). If knocked off their vehicle, they
  deploy onto the street as blue guards on foot without triggering police alerts.
- **Civilian Protection / Alert Suppression (Peaceful mode):** attacking or killing civilian
  pedestrians in the street no longer triggers police alarms or raises the city alert level.
  Stock red guards still trigger alerts normally if directly engaged.
- **Modular `*mod-city-*-hook*` layer:** the shared traffic/guard engine files call ~10 named
  function-pointer hooks (declared in `engine/ai/traffic-h.gc`); `mod-city-peaceful.gc` and
  `mod-city-hooks.gc` wire the required behaviors, while the rest stay at their stock defaults.
  The engine files remain byte-identical across the branch family.

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

<<<<<<< HEAD
## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/blue_guard_reskin_readme.md`](docs/modding/current_mod/blue_guard_reskin_readme.md)
=======
## 📂 Directory Overview

| [`AGENTS.md`](AGENTS.md) | Unified AI agent directives and modding rules (branching, golden rules, REPL workflow, task reference). |
| [`.agents/skills/`](.agents/skills/) | Modularized developer and agent skills (GOAL Lisp, engine internals, 3D assets/actors, texture modding). |
| [`docs/modding/`](docs/modding/README.md) | Modding documentation hub (verified Lisp references, engine primer, engineering workflows, tools). |
| [`docs/modding/jak1_lisp_instructions.md`](docs/modding/jak1_lisp_instructions.md) · [`jak2`](docs/modding/jak2_lisp_instructions.md) · [`jak3`](docs/modding/jak3_lisp_instructions.md) | **Verified** OpenGOAL Lisp reference per game — consult before coding. |
| [`docs/modding/engine_generic_concepts.md`](docs/modding/engine_generic_concepts.md) | Shared non-Lisp engine primer (memory, heaps, DGOs, level streaming, process life cycle). |
| [`docs/modding/tools/`](docs/modding/tools/) | Tool & pipeline guides (build workflow, custom assets, [Debug ▸ Mods menu](docs/modding/tools/mods_debug_menu.md)). |
| [`docs/modding/templates/`](docs/modding/templates/) | [`MOD_README.template.md`](docs/modding/templates/MOD_README.template.md), [`mod_debug_menu.template.gc`](docs/modding/templates/mod_debug_menu.template.gc). |
| [`docs/modding/branch_audit.md`](docs/modding/branch_audit.md) | Generated per-branch compliance report (`task modding-audit`). |
| [`scripts/modding/`](scripts/modding/) | Python automation (branch creation, branch/doc sync, doc landing, branch audit). |
| [`goal_src/`](goal_src/) | Decompiled and modified GOAL source code by game (`jak1/`, `jak2/`, `jak3/`). |
| [`goalc/`](goalc/) | OpenGOAL compiler with modding adjustments. |
| [`game/`](game/) | C++ runtime simulating the Emotion Engine memory on PC. |
| [`decompiler/`](decompiler/) | Asset extraction and decompiler tools. |
| [`custom_assets/`](custom_assets/) | Custom texture replacements and models. |
>>>>>>> origin/master-dev

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Ajoute un garde crimson recoloré en bleu comme une entité à part entière — un nouveau type GOAL
(`crimson-blue-guard`) qui réutilise à 100% le comportement, les animations et les sons du garde
crimson d'origine (`crimson-guard`), seul le mesh/la texture change. Il apparaît dans Haven City
mélangé au trafic ambiant normal, aux côtés des gardes rouges classiques.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/city-peaceful` — base blue-guard + le mode **City Peaceful** :
  les gardes bleus ambiants patrouillent en escouades neutres de 2 à 3 membres.

### Famille de branches
| Branche | Ajoute |
|---|---|
| `jak2/features/blueguard-traffic` | base : entité `crimson-blue-guard`, IA de combat fidèle, spawn dans le trafic ambiant, couche de hooks modulaire |
| **`jak2/features/city-peaceful`** *(celle-ci)* | **escouades** de patrouille bleues neutres — nav en formation, vitesse adaptative, réélection du chef, défense mutuelle, immunité aux tirs alliés |
| `jak2/features/city-insurrection` | **guerre civile territoriale** à trois fronts — zonage par quartier, combat inter-factions autonome, zones sans alerte, sélecteur de quartier de guerre |
| `jak2/features/blueguard` | les deux modes ensemble (mutuellement exclusifs au runtime) |

**Le mod est livré DÉSACTIVÉ.** Il s'active depuis `Debug ▸ Mods ▸ crimson-blueguard-peaceful ▸ Enable`.
Désactivé, **Abriville est identique au Jak 2 d'origine** — aucun garde bleu, les effectifs de
véhicules-gardes ambiants sont ceux du jeu d'origine, alertes et civils normaux. L'**activer**
enclenche tout le paquet d'un coup : gardes bleus ambiants **et** comportement d'escouades de
patrouille neutres. Le choix re-tire les gardes ambiants immédiatement et persiste au
rechargement des niveaux.

## ✨ Fonctionnalités Clés
- **Nouvelle entité à part entière :** `crimson-blue-guard` est un vrai type GOAL (sous-type de
  `crimson-guard`), pas un simple remplacement de texture global — les gardes rouges classiques
  continuent d'apparaître normalement.
- **Identique au garde classique en tout le reste :** animations, sons, mort (dissolution en particules violettes et maintien au sol après projection), collision, arsenal —
  tout est hérité sans modification (mêmes indices de slot, voir la doc technique) ; seuls le
  mesh/skeleton-group et la différence de comportement ci-dessous changent.
- **Sa propre logique de faction :** contrairement au garde classique, il est passif envers Jak par
  défaut et ne rejoint jamais une alerte générale de la ville contre lui. Si Jak l'attaque
  personnellement, il riposte sans déclencher l'alarme de la ville. Robustesse accrue : 8 PV
  (le double des gardes classiques) pour des affrontements tactiques prolongés.
- **Déclencheur manuel « combattre les autres gardes » :** `crimson-blue-guard-attack-guards`, une
  petite fonction qui le fait devenir hostile envers le `crimson-guard` rouge le plus proche —
  jamais automatique, appelée explicitement (REPL ou code).
- **Mélangé au trafic ambiant de la ville :** le traffic-manager fait apparaître la variante bleue
  pour une fraction configurable des spawns de gardes ambiants (`*crimson-blue-guard-ratio*`,
  1 sur 2 du pool parité-id par défaut), aux côtés du garde classique.
- **IA de Combat Fidèle aux Crimson Guards :** les gardes armés d'un fusil ou d'un lance-grenades maintiennent une distance d'engagement tactique (jusqu'à 50 m), tirent des rafales/projectiles avec visée réactive et enchaînent des roulades d'esquive latérales (`roll-left` / `roll-right`). Les coups de crosse sont strictement réservés au contact d'urgence (< 2,5 m) et sont immédiatement suivis d'une roulade d'esquive pour reprendre le tir à distance. Les gardes au taser foncent au contact pour électrocuter avec des arcs électriques.
- **Mode City Peaceful** (`mod-city-peaceful.gc`, basculé depuis l'onglet Mods) : quand il est
  actif, un garde bleu ambiant fraîchement activé devient **chef d'escouade** et fait apparaître
  1-2 suiveurs derrière lui — nav en formation serrée avec vitesse de suiveur adaptative,
  réélection automatique du chef à la mort, arsenal distinct par membre, et riposte mutuelle
  (frappe-en un, toute l'escouade se retourne contre l'attaquant) — le tout sans jamais déclencher
  l'alarme de la ville. Les gardes bleus sont totalement immunisés aux tirs alliés entre eux.
- **Conducteurs de véhicules en gardes bleus (mode Peaceful) :** les cruisers de patrouille
  de la garde (`vehicle-guard`) sont conduits par des gardes bleus (`crimson-blue-guard-rider`).
  En cas d'éjection du véhicule, ils atterrissent sur la chaussée en gardes bleus à pied sans
  déclencher d'alerte de police.
- **Protection des civils / Suppression de l'alerte (mode Peaceful) :** attaquer ou tuer des
  piétons civils dans les rues ne déclenche plus l'alarme de police et ne fait plus monter le
  niveau d'alerte de la ville. Les gardes rouges classiques déclenchent toujours l'alerte
  normalement s'ils sont directement provoqués.
- **Couche modulaire `*mod-city-*-hook*` :** les fichiers moteur partagés appellent ~10 hooks
  nommés (déclarés dans `engine/ai/traffic-h.gc`) ; `mod-city-peaceful.gc` et `mod-city-hooks.gc`
  câblent les comportements requis, tandis que le reste conserve les valeurs d'origine. Les
  fichiers moteur restent identiques sur toute la famille de branches.

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
<<<<<<< HEAD
=======

## 🌿 Architecture Git & Workflows

Le dépôt sépare le code amont officiel et les branches de modding :
- **`master`** : Miroir direct d'OpenGOAL amont. Aucun commit custom n'y est fait directement.
- **`master-dev`** : Branche de base pour le modding, l'outillage et la documentation consolidée.
- **Branches de mods (`jak[N]/[type]/[nom]`)** : Dérivées de `master-dev`.

### Workflow Principal :
- [`.github/workflows/sync-upstream.yaml`](.github/workflows/sync-upstream.yaml) : Rapatrie chaque jour les nouveautés officielles sur `master`, met à jour `master-dev`, teste et fusionne les branches de mods prêtes, et actualise le tableau ci-dessous.

> L'ancien workflow d'agrégation `sync-modding-docs.yaml` a été **supprimé**. Les
> deux documents de référence (`docs/modding/jak[x]_lisp_instructions.md`,
> `engine_generic_concepts.md`) ont une seule source de vérité — `master-dev` — et
> sont mis à jour là directement via `task modding-land-doc` (en ajout seul), puis
> rapatriés dans les branches de mods avec `task modding-sync-docs`. C'est ce qui
> évite tout conflit de documentation entre branches de mods développées en
> parallèle.

---

## 📊 Tableau de Bord de Synchronisation des Branches / Branch Sync Dashboard

*L'historique complet des fusions et résolutions est consultable dans [`docs/modding/branch_sync_history.log`](docs/modding/branch_sync_history.log).*

<!-- BRANCH_STATUS_START -->
> **Dernière mise à jour :** `2026-09-11 13:48:24 UTC`  
> **Branche source :** `master-dev` (`cdbb2096b`)  
> **Statut global :** 15/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `90728a041 - chore: sync jak2/config/enhanced_spawnrates with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | ✅ À jour | `08233c0e6 - chore: sync jak2/config/start_menu_wheel with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/city-insurrection` | ✅ À jour | `bb3d007b3 - chore: sync jak2/features/crimson-blueguard/city-insurrection with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/peaceful` | ✅ À jour | `a91eee9c0 - chore: sync jak2/features/crimson-blueguard/peaceful with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `427f19cd8 - chore: sync jak2/features/dark_jak_enhanced with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `62debc00c - chore: sync jak2/features/jak3-jetBoard with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/paddywagon/traffic` | ✅ À jour | `a55f28582 - chore: sync jak2/features/paddywagon/traffic with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport-ag/alert` | ✅ À jour | `1e2d84f6b - chore: sync jak2/features/transport-ag/alert with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport-ag/traffic` | ✅ À jour | `b60c12f8f - chore: sync jak2/features/transport-ag/traffic with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/yakow_killable` | ✅ À jour | `480399e6f - chore: sync jak2/features/yakow_killable with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak3/config/memory_increase` | ✅ À jour | `d1b90c9b4 - chore: sync jak3/config/memory_increase with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak3/features/city-behavior` | ✅ À jour | `d7a1955af - chore: sync jak3/features/city-behavior with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak3/features/jak2_skin_secret` | ✅ À jour | `8123108e9 - chore: sync jak3/features/jak2_skin_secret with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak3/features/mega_dark_jak` | ✅ À jour | `b04b08338 - chore: sync jak3/features/mega_dark_jak with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
| `jak3/features/redguard-entity` | ✅ À jour | `67a4892cf - chore: sync jak3/features/redguard-entity with latest origin/master-dev (AI-assisted)` | Déjà à jour | — |
<!-- BRANCH_STATUS_END -->

---

## 🛠️ Référence des commandes `task` / `task` Command Reference

> Builds & runtime use [Taskfile](https://taskfile.dev/). Pass script arguments after `--`.
> Les builds et l'exécution utilisent [Taskfile](https://taskfile.dev/). Passez les arguments après `--`.

### Jeu actif / Active game
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task set-game-jak1` · `-jak2` · `-jak3` | Persist the target game | Fixe le jeu ciblé |

### Build & CMake
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task gen-cmake-release` | Configure the build (Ninja + clang); auto-wires `sccache` if installed | Configure le build ; câble `sccache` s'il est installé |
| `task build-release` | Build **all** ~20 binaries (slow — first build / full check) | Build **complet** des ~20 binaires (lent) |
| `task build-release-game` | Build only `gk` + `goalc` — fast, for engine/compiler C++ iteration | Build `gk` + `goalc` uniquement — rapide, pour le C++ moteur/compilateur |
| `task build-release-decomp` | Build only the decompiler — after `decompiler/**` changes, then re-`extract` | Build le décompilateur seul — après modif `decompiler/**`, puis re-`extract` |
| `task build-debug` / `-debug-game` / `-debug-decomp` | Debug equivalents | Équivalents debug |
| `task clean-cmake` | Remove CMake artifacts | Supprime les artefacts CMake |

### Extraction & décompilation / Extraction & decompile
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task extract` | Extract assets + run the decompiler (re-run after any `decompiler/config` change) | Extrait les assets + lance le décompilateur |
| `task decomp` / `decomp-file FILE=…` | Decompile all / one object | Décompile tout / un objet |
| `task rip-textures` / `rip-levels` / `rip-collision` / `rip-audio` | Rip specific asset kinds | Extrait un type d'asset précis |

### REPL & exécution / REPL & run
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task repl` → `(mi)` | Open the compiler REPL; `(mi)` = incremental compile + hot reload (**no C++ build for `.gc` edits**) | Ouvre le REPL ; `(mi)` = compilation incrémentale + hot reload |
| `task boot-game` / `boot-game-retail` | Boot the game (debug / retail) without the REPL | Démarre le jeu (debug / retail) sans REPL |
| `task run-game` | Start the runtime, drive it from the REPL | Lance le runtime, piloté depuis le REPL |
| `task format` / `format-gsrc FILE=…` | Format C++ / one GOAL file | Formate le C++ / un fichier GOAL |

### Workflow de modding / Modding workflow
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task modding-new-branch -- jak2/features/x` | New mod branch from `master-dev` + initial README | Nouvelle branche de mod depuis `master-dev` + README initial |
| `task modding-sync-branch` | Safe `git merge` of `master-dev` into the current branch (`-- --rebase` / `-- --push`) | `git merge` sûr de `master-dev` dans la branche courante |
| `task modding-sync-docs` | Pull `docs/modding` + `AGENTS.md` + `CLAUDE.md` from `master-dev` (prunes deleted files) | Rapatrie la doc depuis `master-dev` (purge les fichiers supprimés) |
| `task modding-land-doc -- --file docs/modding/jak2_lisp_instructions.md --message "…" --push` | Land a doc addition on `master-dev` conflict-free, then re-sync your branch | Intègre un ajout de doc sur `master-dev` sans conflit, puis resync |
| `task modding-branch-status` | Test every mod branch's mergeability + refresh the dashboard (`-- --push` auto-merges) | Teste la fusionnabilité de chaque branche + actualise le tableau |
| `task modding-audit` | Regenerate `docs/modding/branch_audit.md` | Régénère `docs/modding/branch_audit.md` |

### Tests
| Commande | 🇬🇧 | 🇫🇷 |
| :--- | :--- | :--- |
| `task offline-tests` / `offline-tests-fast` | Decompiler reference tests | Tests de référence du décompilateur |
| `task unit-tests` / `tests-filtered FILTER=…` | `goalc` unit tests | Tests unitaires `goalc` |

>>>>>>> origin/master-dev
*(AI-assisted)*
