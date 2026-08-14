# Mod Readme — Jak 3 Jetboard Mechanics Port to Jak 2

> **Game / Jeu :** Jak 2  
> **Branch / Branche :** `jak2/features/jak3-jetBoard`  
> **Target Subsystem / Sous-système :** Target Jetboard (`goal_src/jak2/engine/target/board/`) & Sound Bank / Art Group Pipelines

---

## Language Selection / Sélection de la langue
- [English Version](#-english-version)
- [Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

This mod ports three core Jetboard mechanics introduced in Jak 3 into Jak 2's native jetboard system:

1. **Chargeable High Jump:**
   - **Controls:** Hold `L1` (crouch on board) then release `X` / Jump.
   - **Behavior:** Charges dynamic upward kinetic energy and launches Jak much higher than standard board jumps (`jakb-board-jump-high-ja`). Plays dedicated charge & launch audio.
2. **Board Zap Attack (Area-of-Effect & I-Frames):**
   - **Controls:** Press `Circle` while riding the board.
   - **Behavior:** Unleashes a radial electric shockwave dealing damage to nearby enemies with invincibility frames during the discharge. Plays `BOARD_ZAP` and `BOARD_ZAP_HIT`.
3. **180-Degree Quick Turn-Around:**
   - **Controls:** Press `Triangle` while riding the board.
   - **Behavior:** Executes a rapid 180° snap rotation (`jakb-board-turn-around-ja`).

---

## 2. Technical Architecture & Tooling

### A. Animation Retargeting Pipeline (`retarget_anim` & `CMakeLists.txt`)
To cleanly import Jak 3 animations into Jak 2 without manual Blender edits or hex manipulation, a dedicated standalone C++ tool was integrated into the OpenGOAL toolchain:

- **`goalc/CMakeLists.txt` :**
  - Declares executable target `retarget_anim` (`add_executable(retarget_anim retarget_anim/main.cpp retarget_anim/retarget_anim.cpp)`).
  - Links `common`, `fmt`, and `tiny_gltf` to directly read, process, and write binary glTF/GLB containers.
- **`goalc/retarget_anim/main.cpp` :**
  - Provides a CLI interface (via `CLI11`) to configure retargeting:
    - `--base` (`-b`): Base reference GLB carrying Jak 2's native mesh and skeleton (`jakb-lod0.glb` / `daxter-lod0.glb`).
    - `--source` (`-s`): Source GLB containing raw extracted animations from Jak 3.
    - `--anim` (`-a`): Exact animation names to retarget (`board-jump-high`, `board-turn-around`).
    - `--root-joints`: Joints receiving true root motion translation and rotation (`align`, `main`).
    - `--neutral-scale-joints`: Sockets protected from scale drift (`board`).
- **`goalc/retarget_anim/retarget_anim.cpp` :**
  - **Bone-by-name matching:** Maps animation tracks to Jak 2 skeleton joints by semantic name, bypassing joint index discrepancies.
  - **Stretching elimination:** Retains translation only on root bones (`align`/`main`) and forces pure rotation (quaternions) on all child bones to preserve natural limb lengths.
  - **Attachment scale preservation:** Keeps native bind-pose scale on joint 25 `board` (`(0.7143, 0.7143, 0.7143)` canceling `main`'s `1.4` scale).
  - **GLTF spec compliance:** Automatically converts `JOINTS_0` accessor from `UNSIGNED_INT` to `UNSIGNED_BYTE` for `gltf_util` compatibility and purges orphaned buffer data.

### B. Sound Bank Injection (`SBK` Tooling)
- **`decompiler/data/extract_sbk.cpp` & `goalc/build_sbk/` :** C++ tools to extract ADPCM audio from `.SBK` banks and inject new samples via `append-sbk` macro in `project-lib.gp`.
- **`custom_assets/jak2/sounds/sfx/MODEBORD/` :** Provides the 4 Jak 3 audio files (`BOARD_CHARGE`, `BOARD_LAUNCH`, `BOARD_ZAP`, `BOARD_ZAP_HIT`).

### C. Dynamic Art Linking & GOAL Gameplay Logic
- **`goal_src/jak2/engine/anim/joint.gc` :** Hook inside `art-group::relocate` to dynamically link custom art groups at file load time (`link-art!`).
- **`goal_src/jak2/engine/target/board/board-h.gc` :** Extended `board-info` and `target-board-bank` to hold charge timers, zap duration, and sound IDs.
- **`goal_src/jak2/engine/target/board/board-states.gc` & `target-board.gc` :** Implemented high jump, quick turnaround, and zap attack state machines with radial damage collision and i-frames.

---

## 3. How to Test & Play

1. Set the active game to Jak 2:
   ```bash
   task set-game-jak2
   ```
2. Build custom sound assets and recompile:
   ```bash
   task extract
   ```
3. In REPL (`task repl`), hot-recompile code:
   ```lisp
   (mi)
   ```
4. Boot the game:
   ```bash
   task boot-game
   ```
5. Equip Jetboard (`R2`) and test:
   - **Charge Jump:** Hold `L1`, release `X`.
   - **Zap Attack:** Press `Circle`.
   - **Quick Turn:** Press `Triangle`.

---

## 4. Current Status & Investigations

- **Compile & Boot Status:** Full compilation and boot verified on Jak 2 with all 3 mechanics operational.
- **Visual Glitches Fixed at Source:**
  - *Board scale fix:* The generator previously hardcoded `board` scale to `(1,1,1)`. In Jak 2's native bind-pose, `board` has scale `(0.7143,0.7143,0.7143)` as a child of `main` (scale `1.4`), canceling out the parent scaling. Fixed by retaining native bind-pose scale.
  - *Turn-around rotation fix:* Removed forced 180° yaw on `align` in the GLB, as `target-board-turn-around` (`board-states.gc`) already drives the 180° rotation entirely through gameplay code (`quaternion-rotate-y!` and `align!`).
- **Cosmetic Note:** Console output `-debug` prints `no eye anim data for target/sidekick` on new animations because there are no eye blink table entries for custom animation clips (neutral eye pose fallback, harmless).
- **Audio Diagnostics:** Ensure sound names in `metadata.txt` match the lower-case hyphenated identifiers used by `(sound-play ...)` in GOAL.

---

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|---|---|---|---|
| 2026-08-14 | `decompiler/data/extract_sbk.{cpp,h}`<br>`goalc/build_sbk/{build_sbk,main}.{cpp,h}`<br>`goalc/make/Tools.{cpp,h}`<br>`goalc/make/MakeSystem.cpp`<br>`goalc/CMakeLists.txt`<br>`decompiler/config.{cpp,h}`<br>`decompiler/config/jak3/jak3_config.jsonc`<br>`decompiler/decompilation_process.cpp`<br>`goal_src/jak2/lib/project-lib.gp` | Backported `extract_sbk` (SPU-ADPCM extraction from `.SBK`) and `build_sbk` (audio injection into existing SBK with `SFXBlockNames` and V1/V2/V3 `SBlk` support) from `og-j1-board`, exposed via `append-sbk` macro in `project-lib.gp`. | Allow appending custom sounds to Jak 2's native `BOARD.SBK` without replacing the entire bank. |
| 2026-08-14 | `custom_assets/jak2/sounds/sfx/MODEBORD/*.wav`<br>`custom_assets/jak2/sounds/sfx/MODEBORD/metadata.txt` | Extracted `MODEBORD.SBK` from Jak 3, providing 4 new sounds for Jak 2: `BOARD_CHARGE`, `BOARD_LAUNCH` (2 stereo grains), `BOARD_ZAP`, `BOARD_ZAP_HIT`. | Provide audio source data for charged jump and zap attack. |
| 2026-08-14 | `custom_assets/jak2/models/custom_levels/jakb-jak3-board-import.glb`<br>`custom_assets/jak2/models/custom_levels/daxter-jak3-board-import.glb` | Imported 2 Jak 3 animations per character (`board-jump-high`, `board-turn-around`), remapped bone-by-bone onto native Jak 2 skeleton. Uses `jakb-lod0`/`daxter-lod0` mesh (63/48 joints, skin + 2 anims per file). | Provide the 2 missing animations for high jump and 180 turn. |
| 2026-08-14 | `goal_src/jak2/game.gp`<br>`goal_src/jak2/dgos/game.gd`<br>`goal_src/jak2/engine/data/art-elts.gc` | Declared `build-actor` targets for `jakb-jak3-board-import` and `daxter-jak3-board-import` with `:master-art-group`/`:master-ag-map` to free slots in `jakb-ag` (236/237) and `daxter-ag` (459/460); added `.go` packages to `game.gd`; declared `def-art-elt` symbols in `art-elts.gc`. | Compile custom GLBs into separate art-groups and splice into resident `jakb-ag`/`daxter-ag`. |
| 2026-08-14 | `goal_src/jak2/engine/anim/joint.gc` | Added special case in `art-group::relocate` calling `link-art!` on file load once (matching `og-j1-board` pattern for `"eichar-board+0"`). | Ensure correct dynamic link timing at boot without invoking `link-art!` during gameplay. |
| 2026-08-14 | `goal_src/jak2/engine/target/board/board-h.gc` | Extended `board-info` (`charge-sound-id`, `charge-part`, `charge-start-time`, `charge-time`, `charge-progress`, `zap-start-time`) and `target-board-bank` (`charge-jump-time`, `charge-jump-fade-time`, `charge-jump-height`, `zap-duration`, `zap-reset-time`). | Store runtime state for new mechanics in `board-info` pointer struct. |
| 2026-08-14 | `goal_src/jak2/engine/target/board/target-board.gc`<br>`goal_src/jak2/engine/target/board/board-states.gc`<br>`goal_src/jak2/engine/target/target-h.gc`<br>`goal_src/jak2/engine/target/target-handler.gc`<br>`goal_src/jak2/engine/target/target-util.gc` | Implemented gameplay logic: `L1` held charge with looping `board-charge` sound, air release impulse with `board-launch` sound and `jakb-board-jump-high-ja`; `Circle` zap attack with `board-zap`, `target-danger-set!`, i-frames, and `board-zap-hit` impact sound; `Triangle` state `target-board-turn-around` with `jakb-board-turn-around-ja` and 1s timeout guard. | Implement full 3 mechanics using native Jak 2 particle and gameplay architectures. |
| 2026-08-14 | `goalc/retarget_anim/{retarget_anim,main}.{cpp,h}`<br>`goalc/CMakeLists.txt`<br>Regenerated `{jakb,daxter}-jak3-board-import.glb` | Built standalone retargeting tool using `gltf_util` to retarget animations by bone name onto native Jak 2 skeleton (`decompiler_out/jak2/levels/common/{jakb,daxter}-lod0.glb`). Root motion on `align`/`main`, rotation only on child bones, neutral socket scale. Output GLB contains native mesh + only the 2 added animations. | Cleanly regenerate custom GLBs matching `og-j1-board` structure. |
| 2026-08-14 | `goalc/retarget_anim/retarget_anim.cpp` | Handled `JOINTS_0` conversion from `UNSIGNED_INT` to `UNSIGNED_BYTE` for `gltf_util` compatibility; clamped `daxter-lod0.glb` 62-joint skin references to 48 valid joints. | Ensure robust GLTF import without manual file hex patches. |
| 2026-08-15 | `goalc/retarget_anim/retarget_anim.cpp`<br>Regenerated both import GLBs | Fixed board shrink glitch by holding native bind-pose scale `(0.7143, 0.7143, 0.7143)` on joint 25; fixed turn-around visual glitch by removing forced 180° yaw on `align` (since rotation is already driven by `quaternion-rotate-y!` in `board-states.gc`). | Eliminate visual distortions on screen. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Ce mod porte trois mécaniques majeures du Jetboard introduites dans Jak 3 directement dans le système de jetboard natif de Jak 2 :

1. **Saut Haut Chargé (High Jump) :**
   - **Commandes :** Maintenir `L1` (accroupi sur le skate) puis relâcher `X` / Saut.
   - **Comportement :** Charge de l'énergie cinétique ascendante et propulse Jak nettement plus haut qu'un saut standard (`jakb-board-jump-high-ja`). Joue les sons de charge et de propulsion dédiés.
2. **Attaque Zap Circulaire (Dégâts de zone & I-Frames) :**
   - **Commandes :** Appuyer sur `Cercle` en ridant le skate.
   - **Comportement :** Déclenche une onde de choc électrique radiale blessant les ennemis proches avec des frames d'invulnérabilité. Joue `BOARD_ZAP` et `BOARD_ZAP_HIT`.
3. **Demi-Tour Rapide à 180° (Quick Turn-Around) :**
   - **Commandes :** Appuyer sur `Triangle` en ridant le skate.
   - **Comportement :** Exécute un pivotement instantané à 180° (`jakb-board-turn-around-ja`).

---

## 2. Architecture Technique & Outillage

### A. Pipeline de Reciblage d'Animation (`retarget_anim` & `CMakeLists.txt`)
Pour importer proprement les animations de Jak 3 dans Jak 2 sans recourir à des modifications manuelles fragiles dans Blender ou des éditeurs hexadécimaux, un nouvel outil C++ autonome a été intégré directement dans la suite d'outils OpenGOAL :

- **`goalc/CMakeLists.txt` :**
  - Déclare la cible exécutable `retarget_anim` (`add_executable(retarget_anim retarget_anim/main.cpp retarget_anim/retarget_anim.cpp)`).
  - Lie les bibliothèques `common`, `fmt` et `tiny_gltf` pour manipuler et réécrire directement les conteneurs binaires glTF/GLB d'OpenGOAL.
- **`goalc/retarget_anim/main.cpp` :**
  - Fournit une interface en ligne de commande (CLI via `CLI11`) permettant d'automatiser le reciblage :
    - `--base` (`-b`) : Le GLB de référence portant le maillage et le squelette natif de Jak 2 (`jakb-lod0.glb` ou `daxter-lod0.glb`).
    - `--source` (`-s`) : Le GLB source contenant les animations brutes extraites de Jak 3.
    - `--anim` (`-a`) : Les noms exacts des animations à extraire et recibler (`board-jump-high`, `board-turn-around`).
    - `--root-joints` : Les os recevant la translation et rotation réelle de root motion (`align`, `main`).
    - `--neutral-scale-joints` : Les os protégés de toute déformation d'échelle (`board`).
- **`goalc/retarget_anim/retarget_anim.cpp` :**
  - **Remappage par nom d'os :** Fait correspondre chaque piste d'animation au bon os du squelette de Jak 2, indépendamment des différences d'index numérique entre les deux jeux.
  - **Suppression du stretching :** Ne conserve la translation que sur les os racines (`align`/`main`) et force tous les os enfants en rotation pure (quaternions) pour préserver les longueurs de membres d'origine.
  - **Préservation de l'échelle d'attache :** Maintient l'échelle bind-pose native du joint `board` (`(0.7143, 0.7143, 0.7143)` pour annuler le facteur `1.4` de `main`).
  - **Compatibilité glTF :** Convertit automatiquement l'accessor `JOINTS_0` de `UNSIGNED_INT` vers `UNSIGNED_BYTE` exigé par `gltf_util`, et compacte les buffers pour ne générer que les 2 animations utiles sans polluer le package.

### B. Outil d'Injection Sonore (`SBK` Tooling)
- **`decompiler/data/extract_sbk.cpp` & `goalc/build_sbk/` :** Outils C++ permettant d'extraire les sons ADPCM depuis les banques `.SBK` et de les réinjecter via la macro `append-sbk` dans `project-lib.gp`.
- **`custom_assets/jak2/sounds/sfx/MODEBORD/` :** Fournit les 4 sons de Jak 3 (`BOARD_CHARGE`, `BOARD_LAUNCH`, `BOARD_ZAP`, `BOARD_ZAP_HIT`).

### C. Injection Dynamique & Logique GOAL
- **`goal_src/jak2/engine/anim/joint.gc` :** Hook dans `art-group::relocate` pour lier dynamiquement les animations au chargement fichier (`link-art!`).
- **`goal_src/jak2/engine/target/board/board-h.gc` :** Extension de `board-info` et `target-board-bank` pour stocker le temps de charge et les durées d'effets.
- **`goal_src/jak2/engine/target/board/board-states.gc` & `target-board.gc` :** Implémentation des états de saut chargé, demi-tour rapide et attaque zap avec gestion des dégâts radiaux et invulnérabilité.

---

## 3. Commandes & Procédure de Test

1. Définir le jeu actif sur Jak 2 :
   ```bash
   task set-game-jak2
   ```
2. Construire les assets et banques audio :
   ```bash
   task extract
   ```
3. Compiler le code dans le REPL (`task repl`) :
   ```lisp
   (mi)
   ```
4. Lancer le jeu :
   ```bash
   task boot-game
   ```
5. Équiper le Jetboard (`R2`) et tester :
   - **Saut chargé :** Maintenir `L1`, relâcher `X`.
   - **Attaque Zap :** Appuyer sur `Cercle`.
   - **Demi-tour rapide :** Appuyer sur `Triangle`.

---

## 4. Statut Actuel & Investigations

- **Statut de compilation & Boot :** Compilation et boot validés sur Jak 2 avec les 3 mécaniques entièrement fonctionnelles.
- **Corrections visuelles appliquées à la source :**
  - *Correction d'échelle du Board :* Le générateur forçait précédemment l'échelle à `(1,1,1)`. Dans la bind-pose native de Jak 2, `board` a une échelle de `(0.7143, 0.7143, 0.7143)` car c'est un enfant direct de `main` (échelle `1.4`). Corrigé en conservant l'échelle bind-pose native.
  - *Correction visuelle du demi-tour :* Suppression du forçage de lacet à 180° sur `align`, car `target-board-turn-around` (`board-states.gc`) pilote déjà le demi-tour intégralement par le code de gameplay (`quaternion-rotate-y!` et `align!`).
- **Note Cosmétique :** Le log console `-debug` affiche `no eye anim data for target/sidekick` lors de la lecture des nouvelles animations car les animations custom n'ont pas d'entrées dans la table des clignements d'yeux (pose neutre par défaut sans risque de crash).
- **Diagnostic Audio :** Vérifier que les noms de sons dans `metadata.txt` correspondent exactement aux identifiants minuscules avec tirets appelés par `(sound-play ...)` en GOAL.

---

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|---|---|---|---|
| 2026-08-14 | `decompiler/data/extract_sbk.{cpp,h}`<br>`goalc/build_sbk/{build_sbk,main}.{cpp,h}`<br>`goalc/make/Tools.{cpp,h}`<br>`goalc/make/MakeSystem.cpp`<br>`goalc/CMakeLists.txt`<br>`decompiler/config.{cpp,h}`<br>`decompiler/config/jak3/jak3_config.jsonc`<br>`decompiler/decompilation_process.cpp`<br>`goal_src/jak2/lib/project-lib.gp` | Portage de `extract_sbk` et `build_sbk` depuis `og-j1-board`, exposé via la macro `append-sbk` dans `project-lib.gp`. | Permettre l'injection de sons custom dans la banque native `BOARD.SBK` de Jak 2 sans la remplacer. |
| 2026-08-14 | `custom_assets/jak2/sounds/sfx/MODEBORD/*.wav`<br>`custom_assets/jak2/sounds/sfx/MODEBORD/metadata.txt` | Extraction de `MODEBORD.SBK` de Jak 3 fournissant les 4 sons : `BOARD_CHARGE`, `BOARD_LAUNCH`, `BOARD_ZAP`, `BOARD_ZAP_HIT`. | Fournir la source audio pour le saut chargé et le zap. |
| 2026-08-14 | `custom_assets/jak2/models/custom_levels/jakb-jak3-board-import.glb`<br>`custom_assets/jak2/models/custom_levels/daxter-jak3-board-import.glb` | Import de 2 animations Jak 3 par personnage (`board-jump-high`, `board-turn-around`), remappées sur le squelette natif de Jak 2 avec `jakb-lod0`/`daxter-lod0`. | Fournir les 2 animations manquantes pour le saut chargé et le demi-tour. |
| 2026-08-14 | `goal_src/jak2/game.gp`<br>`goal_src/jak2/dgos/game.gd`<br>`goal_src/jak2/engine/data/art-elts.gc` | Déclaration de `build-actor` avec `:master-art-group`/`:master-ag-map` sur des slots libres dans `jakb-ag` (236/237) et `daxter-ag` (459/460) ; ajout des `.go` à `game.gd` ; déclaration des symboles dans `art-elts.gc`. | Compiler les GLB custom et les intégrer aux art-groups résidents. |
| 2026-08-14 | `goal_src/jak2/engine/anim/joint.gc` | Hook dans `art-group::relocate` appelant `link-art!` au chargement du fichier (pattern `og-j1-board`). | Garantir la liaison dynamique au boot sans appel dangereux pendant le gameplay. |
| 2026-08-14 | `goal_src/jak2/engine/target/board/board-h.gc` | Extension de `board-info` et `target-board-bank` pour stocker l'état des nouvelles mécaniques. | Gérer les compteurs et paramètres temporels du Jetboard. |
| 2026-08-14 | `goal_src/jak2/engine/target/board/target-board.gc`<br>`goal_src/jak2/engine/target/board/board-states.gc`<br>`goal_src/jak2/engine/target/target-h.gc`<br>`goal_src/jak2/engine/target/target-handler.gc`<br>`goal_src/jak2/engine/target/target-util.gc` | Logique de gameplay : charge `L1` avec son en boucle, propulsion en l'air avec impulsion et anim `jump-high` ; zap `Cercle` avec dégâts radiaux et i-frames ; demi-tour `Triangle` avec état `turn-around`. | Implémenter les 3 mécaniques complètes de Jak 3 dans Jak 2. |
| 2026-08-14 | `goalc/retarget_anim/{retarget_anim,main}.{cpp,h}`<br>`goalc/CMakeLists.txt`<br>Régénération des GLB | Création de l'outil de reciblage automatique par nom d'os sur squelette natif Jak 2. | Régénérer proprement les GLB custom sans altération manuelle. |
| 2026-08-14 | `goalc/retarget_anim/retarget_anim.cpp` | Conversion automatique de `JOINTS_0` de `uint32` vers `uint8` et clamp de `daxter-lod0.glb` à 48 joints. | Garantir la robustesse de l'import glTF. |
| 2026-08-15 | `goalc/retarget_anim/retarget_anim.cpp`<br>Régénération des GLB | Maintien de l'échelle bind-pose native `(0.7143, 0.7143, 0.7143)` sur le joint 25 ; suppression du forçage de lacet 180° sur `align`. | Éliminer les glitchs visuels de scale et de rotation à l'écran. |
