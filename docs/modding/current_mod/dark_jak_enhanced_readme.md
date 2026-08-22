# Dark Jak Enhanced Mod Readme (Jak 2) / Guide du Mod Dark Jak Amélioré

> - **Branch / Branche :** `jak2/features/dark_jak_enhanced`
> - **Game / Jeu :** Jak II
> - **Status / Statut :** Operational / Opérationnel (AI-assisted)

---

- [🇬🇧 English Version](#-english-version)
- [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features
The **Dark Jak Enhanced** mod adds a full 3rd evolutionary stage to Dark Jak in Jak 2: the **Mega-Mega Dark Jak (Titan / Colossus)**, alongside critical quality-of-life, acrobatic, and responsiveness enhancements:

1. **Progressive 3-Tier Transformation (via `L2`):**
   - **1st `L2` Press (Normal Jak):** Transforms into **Classic Dark Jak** (scale x1.05).
   - **2nd `L2` Press (Dark Jak):** Evolves into **Mega Dark Jak / Dark Giant** (scale x2.0).
   - **3rd `L2` Press (Mega Dark Jak):** Evolves into **Mega-Mega Dark Jak / Titan** (scale x3.5).
2. **Dynamic Panoramic Camera:**
   - Smoothly adjusts camera distance and height (`string-min-length 3.2`, `string-max-length 2.8`) to comfortably frame the colossus.
3. **Heavy Footsteps & Seismic Trample:**
   - Double screen-shake intensity on heavy footfalls during walking/running.
4. **Instant Dark Bomb Activation:**
   - Allows instant triggering of the Dark Bomb at any moment during jump ascent or descent on Square press, cancelling upward momentum immediately for a fast, responsive plunge.
5. **Robust Dark Blast (No Surface Abort):**
   - Dark Blast barrage no longer prematurely cancels back to normal Jak when in confined spaces, low ceilings, or touching obstacles.
6. **Unlocked Roll & Roll-Flip for Level 1 Dark Jak:**
   - Restored rolling (`L1` while moving) and roll-flip jump (`L1 + X`) exclusively for **Level 1 Dark Jak**, while preserving the heavy brute locomotion (no rolling) for the colossal **Mega Dark Jak (Giant / Mega-Giant)** stages.

---

## 2. Technical Architecture & Modifications

| File | Subsystem | Modifications |
| :--- | :--- | :--- |
| [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc) | Type Definitions | Added `(mega-giant)` to `darkjak-stage` bitfield enum. |
| [`goal_src/jak2/engine/target/target-util.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-util.gc) | Target Utilities | In `can-roll?`, allow rolling for Level 1 Dark Jak while disabling it for `giant` and `mega-giant` stages. |
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | Dark Jak States | Progressive scaling to 3.5 in `target-darkjak-giant`, instant upward momentum cancellation in `target-darkjak-bomb0`, and collision-resilient `:trans`/`:exit` in `target-darkjak-bomb1`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Event Handlers | Doubled camera smush intensity on `effect-control` footsteps in `mega-giant` stage. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Player Locomotion | Scaled jump velocity thresholds, instant Dark Bomb triggers, and support for roll-flip jumps in Level 1 Dark Jak. |

---

## 3. How to Test & Play

1. Start the game via REPL or boot command:
   ```bash
   task boot-game
   ```
2. Enable debug cheat mode in REPL for unlimited dark eco:
   ```lisp
   (set! (-> *setting-control* user-default cheat-mode) 'debug)
   ```
3. In **Level 1 Dark Jak (1st L2)**: perform rolls (`L1`) and roll-flips (`L1 + X`).
4. In **Mega Dark Jak (2nd L2)** or **Mega-Mega Dark Jak (3rd L2)**: verify that rolling is disabled to preserve heavy brute locomotion.
5. Jump and press **Square** to execute instant Dark Bomb; press **L1 + Square** near walls for Dark Blast.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-08-22 | `target-h.gc`, `target-darkjak.gc`, `target-handler.gc` | Added `(mega-giant)` enum bitfield and implemented 3.5x progressive scaling, panoramic camera, and amplified footstep shakes. | Implement Stage 3 Colossal Dark Jak. |
| 2026-08-22 | `target.gc` | Scaled vertical jump velocity gates by `darkjak-giant-interp`. | Fix Dark Bomb not triggering in Mega Giant mode. |
| 2026-08-22 | `target-darkjak.gc` | Removed `on-surface` abort in `target-darkjak-bomb1 :trans` and cleaned `:exit`. | Prevent Dark Blast from cancelling prematurely on surface contact. |
| 2026-08-22 | `target.gc`, `target-darkjak.gc` | Allowed instantaneous Square press trigger during jumps and zeroed upward `transv` on `bomb0 :enter`. | Allow responsive instant plunge for Dark Bomb. |
| 2026-08-22 | `target-util.gc`, `target.gc` | Enabled roll only for Level 1 Dark Jak in `can-roll?` and disabled it for `giant` and `mega-giant` stages. | Maintain agile roll for Level 1 Dark Jak while keeping giant stages heavy and grounded. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités
Le mod **Dark Jak Enhanced** ajoute un troisième stade d'évolution complet pour Dark Jak dans Jak 2 : le **Méga-Méga Dark Jak (Titan / Colosse)**, accompagné d'améliorations majeures d'acrobatie, de réactivité et de robustesse :

1. **Évolution Progressive en 3 Stades (via `L2`) :**
   - **1ᵉʳ appui sur `L2` (Jak normal) :** Transformation en **Dark Jak classique** (taille x1.05).
   - **2ᵉ appui sur `L2` (Dark Jak) :** Évolution en **Méga Dark Jak / Dark Giant** (taille x2.0).
   - **3ᵉ appui sur `L2` (Méga Dark Jak) :** Évolution ultime en **Méga-Méga Dark Jak / Titan** (taille x3.5).
2. **Caméra Panoramique Dynamique :**
   - Recul et élévation automatique de la caméra (`string-min-length 3.2`, `string-max-length 2.8`) pour un cadrage optimal du titan.
3. **Foulées Lourdes & Secousses Sismiques :**
   - Intensité doublée des secousses d'écran (`screen-shake`) lors des bruits de pas en marche et course.
4. **Déclenchement Instantané de la Dark Bomb :**
   - Déclenchement immédiat de la Dark Bomb à n'importe quel moment du saut dès l'appui sur Carré, annulant immédiatement la vélocité ascendante pour un plongeon rapide.
5. **Dark Blast Résistant aux Collisions :**
   - Le Dark Blast ne s'annule plus prématurément lorsqu'il est déclenché dans des espaces confinés, sous un plafond bas ou près d'obstacles.
6. **Roulade & Roulade Sautée pour Dark Jak Niveau 1 :**
   - Réactivation de la roulade (`L1` en mouvement) et de la roulade sautée (`L1 + Croix`) exclusivement pour **Dark Jak Niveau 1**, tout en conservant la démarche de colosse lourd (sans roulade) pour les stades **Méga Dark Jak** et **Méga-Méga Dark Jak**.

---

## 2. Architecture Technique & Modifications

| Fichier | Sous-système | Modifications |
| :--- | :--- | :--- |
| [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc) | Définition de Types | Ajout de `(mega-giant)` dans l'énumération `darkjak-stage`. |
| [`goal_src/jak2/engine/target/target-util.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-util.gc) | Utilitaires Joueur | Dans `can-roll?`, autorisation de la roulade pour le niveau 1 et blocage pour les stades `giant` et `mega-giant`. |
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | États de Dark Jak | Échelle progressive 3.5 dans `target-darkjak-giant`, annulation de vitesse ascensionnelle dans `target-darkjak-bomb0`, et fiabilisation de `target-darkjak-bomb1`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Gestionnaires d'Événements | Intensité de secousse d'écran doublée pour les pas en mode `mega-giant`. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Locomotion du Joueur | Ajustement des seuils de vélocité, Dark Bomb instantanée, et support de la roulade sautée en Dark Jak Niveau 1. |

---

## 3. Commandes & Procédure de Test

1. Lancer le jeu :
   ```bash
   task boot-game
   ```
2. Activer le mode debug dans le REPL pour obtenir de l'éco noire infinie :
   ```lisp
   (set! (-> *setting-control* user-default cheat-mode) 'debug)
   ```
3. En **Dark Jak Niveau 1 (1ᵉʳ L2)** : effectuer des roulades (`L1`) et roulades sautées (`L1 + Croix`).
4. En **Méga Dark Jak (2ᵉ L2)** ou **Méga-Méga Dark Jak (3ᵉ L2)** : constater que la roulade est désactivée pour préserver l'inertie de titan.
5. Sauter et appuyer sur **Carré** pour déclencher la Dark Bomb instantanée ; appuyer sur **L1 + Carré** près des murs pour tester le Dark Blast.
