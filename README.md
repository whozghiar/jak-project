# Enhanced Spawn Rates & Nav-Mesh Limits / Taux de Spawn et Limites Nav-Mesh Renforcés — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Fconfig%2Fenhanced_spawnrates-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Significantly intensifies the ambient atmosphere, military presence, and combat intensity across Haven City by drastically increasing civilian density, Crimson Guard patrols, guard vehicles, and alert wave reinforcements, supported by doubled nav-mesh capacity and expanded detection radii to guarantee engine stability.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/config/enhanced_spawnrates`

**The mod ships OFF.** A fresh compiled-but-disabled install plays byte-for-byte
like stock Jak 2 — stock traffic density, stock alert waves, stock nav-mesh
limits, no console spam. Turn it on at `Debug ▸ Mods ▸ enhanced-spawnrates ▸
Enable`.

> ⚠️ **Reload Haven City after toggling `Enable`.** The ambient want-counts are
> read once when the city loads (`traffic-manager/init-params`) and the nav-mesh
> user quota is sized once per district on load (`nav-mesh/init-from-entity`), so
> the denser traffic only appears **after you reload the city** — warp, step
> through an interior, or reboot. The alert focus-count and cell-activation-range
> parts of the mod are read live and apply on the next frame. The toggle choice
> persists across level reloads.

## ✨ Key Features
- **Peacetime Crimson Guard Patrols:** Quadrupled Crimson Guard rifle patrols (from 9 to 22), introduced 10 tazer guards during peace, and increased patrol guards (from 1 to 6).
- **Military Vehicles:** Increased guard hover bikes from 4 to 10 and Crimson Guard Hellcat cruisers from 3 to 8.
- **Massive Progressive Alert Waves:** Rebalanced all 5 alert levels (0 to 4) scaling up to 28 rifle guards, 10 tazers, 8 grenadiers, 14 hover bikes, and 10 Hellcats at maximum alert.
- **Extended Detection & Activation Ranges:** Expanded cell activation radius from 200m to 240m for vehicles and 120m to 160m for pedestrians.
- **Doubled Nav-Mesh Capacity:** Raised per-district nav-mesh user quota from 64 to 128 simultaneous pathfinding actors, permanently fixing the `too many users for nav-mesh` crash during district streaming.
- **Real-Time Memory & Population Diagnostics:** Live console logging of active/inactive entities, alarm level, and remaining `*default-dead-pool*` memory headroom.
- **Ships OFF, one runtime switch:** everything above is gated behind a single `*mod-enhanced-spawnrates-enable*` flag, toggled from `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable`. Disabled = stock Jak 2.

## 🎮 Usage & Controls
1. Boot the game, open the debug menu (`~` / select+L1 depending on your setup) and go to **`Debug ▸ Mods ▸ enhanced-spawnrates`**.
2. Toggle **`Enable`**.
3. **Reload Haven City** (warp, or enter and leave any interior) so `init-params` re-reads the want-counts and the nav-mesh is re-sized — otherwise you keep stock traffic density.
4. To turn the mod off again: toggle `Enable` off and reload the city once more.

There are no in-world keybindings; the mod is entirely data/spawn tuning.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist.
- **Details:** Only GOAL scripts are modified (`traffic-h.gc`, `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`, the new `pc/debug/enhanced-spawnrates-menu.gc`, and `dgos/game.gd`). No C++ rebuild needed. For a first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup).
- **Details:** Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
[![Demonstration Video](https://img.youtube.com/vi/ojMdc_wdyZc/maxresdefault.jpg)](https://youtu.be/ojMdc_wdyZc)

<<<<<<< HEAD
▶️ **[Watch the demonstration video on YouTube](https://youtu.be/ojMdc_wdyZc)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)
=======
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
Intensifie considérablement la vie ambiante, la présence militaire et le danger au sein d'Abriville (Haven City) en augmentant massivement les patrouilles de Gardes Grenat, les véhicules d'intervention et les vagues d'alerte, tout en doublant la capacité du nav-mesh et en élargissant les portées d'activation pour assurer une parfaite stabilité moteur.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/enhanced_spawnrates`

**Le mod est livré DÉSACTIVÉ.** Une installation neuve compilée-mais-désactivée
joue un Jak 2 identique à l'original — densité de trafic, vagues d'alerte et
limites nav-mesh d'origine, aucun message console. Activez-le dans
`Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable`.

> ⚠️ **Rechargez Abriville après avoir activé `Enable`.** Les want-counts ambiants
> sont lus une seule fois au chargement de la ville (`traffic-manager/init-params`)
> et le quota d'utilisateurs du nav-mesh est dimensionné une fois par quartier au
> chargement (`nav-mesh/init-from-entity`) : le trafic plus dense n'apparaît donc
> **qu'après rechargement de la ville** — warp, passage par un intérieur, ou
> redémarrage. Les parties « nombre de cibles en alerte » et « portée d'activation
> des cellules » sont lues en direct et s'appliquent à la frame suivante. Le choix
> de la bascule persiste au rechargement des niveaux.

## ✨ Fonctionnalités Clés
- **Patrouilles de Gardes Grenat Hors-Alerte :** Gardes à fusil plus que doublés (de 9 à 22), ajout de 10 gardes tazer en temps de paix et augmentation des patrouilleurs (de 1 à 6).
- **Véhicules Militaires Accrus :** Flotte de motos de garde augmentée de 4 à 10 et croiseurs Hellcat de 3 à 8.
- **Vagues d'Alerte Massives & Progressifs :** 5 niveaux d'alerte calibrés (0 à 4) déployant jusqu'à 28 gardes à fusil, 10 tazers, 8 grenadiers, 14 motos et 10 Hellcats au palier maximal.
- **Portée de Détection et d'Activation Élargie :** Rayon des cellules de grille porté de 200m à 240m pour les véhicules et de 120m à 160m pour les piétons.
- **Doublement de la Capacité Nav-Mesh :** Quota maximal de chaque nav-mesh doublé de 64 à 128 acteurs simultanés, éliminant définitivement les plantages `too many users for nav-mesh` lors du streaming entre quartiers.
- **Diagnostics Mémoire & Population en Direct :** Suivi périodique en console des entités actives/inactives, de l'alarme et de la marge mémoire restante dans le heap de process (`*default-dead-pool*`).
- **Livré DÉSACTIVÉ, un seul interrupteur :** tout ce qui précède est conditionné à l'unique variable `*mod-enhanced-spawnrates-enable*`, basculée depuis `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable`. Désactivé = Jak 2 d'origine.

## 🎮 Utilisation & Commandes
1. Lancez le jeu, ouvrez le menu debug et allez dans **`Debug ▸ Mods ▸ enhanced-spawnrates`**.
2. Basculez **`Enable`**.
3. **Rechargez Abriville** (warp, ou entrez puis sortez d'un intérieur) pour que `init-params` relise les want-counts et que le nav-mesh soit redimensionné — sinon la densité de trafic reste celle d'origine.
4. Pour désactiver le mod : rebasculez `Enable` et rechargez la ville une nouvelle fois.

Aucune touche de jeu dédiée ; le mod n'est que du réglage de données / de spawn.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà.
- **Détails :** Seuls des scripts GOAL sont modifiés (`traffic-h.gc`, `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`, le nouveau `pc/debug/enhanced-spawnrates-menu.gc` et `dgos/game.gd`), aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation).
- **Détails :** Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
[![Vidéo de Démonstration](https://img.youtube.com/vi/ojMdc_wdyZc/maxresdefault.jpg)](https://youtu.be/ojMdc_wdyZc)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/ojMdc_wdyZc)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

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
