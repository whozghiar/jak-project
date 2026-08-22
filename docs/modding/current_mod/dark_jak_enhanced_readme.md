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
   - *Note:* Progressive evolution is fully unlocked in standard gameplay without requiring story cheat unlocks.
2. **Instant Manual De-Transformation (`R2`):**
   - Press **`R2`** at any moment in any state to instantly revert back to normal Jak.
   - **100% Dark Eco Consumption:** All collected dark eco is consumed upon transformation, and zeroed out when exiting Dark Jak (regardless of whether by timer, `R2` cancel, Dark Bomb, Dark Blast, or death).
3. **Pristine Original HUD:**
   - The HUD remains 100% authentic and unmodified.
4. **Dynamic Panoramic Camera:**
   - Smoothly adjusts camera distance and height (`string-min-length 3.2`, `string-max-length 2.8`) to comfortably frame the colossus.
5. **Heavy Footsteps & Seismic Trample:**
   - Double screen-shake intensity on heavy footfalls during walking/running.
6. **Instant Dark Bomb Activation:**
   - Allows instant triggering of the Dark Bomb at any moment during jump ascent or descent on Square press, cancelling upward momentum immediately for a fast, responsive plunge.
7. **Robust Dark Blast (No Surface Abort):**
   - Dark Blast barrage no longer prematurely cancels back to normal Jak when in confined spaces, low ceilings, or touching obstacles.
8. **Unlocked Roll & Roll-Flip for Level 1 Dark Jak:**
   - Restored rolling (`L1` while moving) and roll-flip jump (`L1 + X`) exclusively for **Level 1 Dark Jak**, while preserving the heavy brute locomotion (no rolling) for the colossal **Mega Dark Jak (Giant / Mega-Giant)** stages.

---

## 2. Technical Architecture & Modifications

| File | Subsystem | Modifications |
| :--- | :--- | :--- |
| [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc) | Type Definitions | Added `(mega-giant)` to `darkjak-stage` bitfield enum. |
| [`goal_src/jak2/engine/target/target-util.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-util.gc) | Target Utilities | In `can-roll?`, allow rolling for Level 1 Dark Jak while disabling it for `giant` and `mega-giant` stages. |
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | Dark Jak States | Unlocked progressive evolution in `want-to-darkjak?`, `R2` manual cancel in `target-darkjak-post`, instant upward momentum cancellation in `target-darkjak-bomb0`, collision-resilient `:trans`/`:exit` in `target-darkjak-bomb1`, and 100% dark eco drain on transformation exit in `target-darkjak-end-mode`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Event Handlers | Doubled camera smush intensity on `effect-control` footsteps in `mega-giant` stage. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Player Locomotion | Scaled jump velocity thresholds, instant Dark Bomb triggers, and support for roll-flip jumps in Level 1 Dark Jak. |

---

## 3. How to Test & Play

1. Start the game via REPL or boot command:
   ```bash
   task boot-game
   ```
2. Collect dark eco pills or enable debug cheat mode in REPL:
   ```lisp
   (set! (-> *setting-control* user-default cheat-mode) 'debug)
   ```
3. Press **`L2`** to transform:
   - **`R2` :** Instantly reverts Jak to his normal form at any moment.
   - **2nd & 3rd `L2` :** Evolve into Mega Dark Jak and Titan (3.5x).
   - **`L1` / `L1 + X` :** Roll and roll-flip in Level 1 Dark Jak.
   - **Square in air (Dark Bomb) :** Instant Dark Bomb plunge.
   - **L1 + Square (Dark Blast) :** Collision-resilient Dark Blast.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-08-22 | `target-h.gc`, `target-darkjak.gc`, `target-handler.gc` | Added `(mega-giant)` enum bitfield and implemented 3.5x progressive scaling, panoramic camera, and amplified footstep shakes. | Implement Stage 3 Colossal Dark Jak. |
| 2026-08-22 | `target.gc` | Scaled vertical jump velocity gates by `darkjak-giant-interp`. | Fix Dark Bomb not triggering in Mega Giant mode. |
| 2026-08-22 | `target-darkjak.gc` | Removed `on-surface` abort in `target-darkjak-bomb1 :trans` and cleaned `:exit`. | Prevent Dark Blast from cancelling prematurely on surface contact. |
| 2026-08-22 | `target.gc`, `target-darkjak.gc` | Allowed instantaneous Square press trigger during jumps and zeroed upward `transv` on `bomb0 :enter`. | Allow responsive instant plunge for Dark Bomb. |
| 2026-08-22 | `target-util.gc`, `target.gc` | Enabled roll only for Level 1 Dark Jak in `can-roll?` and disabled it for `giant` and `mega-giant` stages. | Maintain agile roll for Level 1 Dark Jak while keeping giant stages heavy and grounded. |
| 2026-08-22 | `target-darkjak.gc` | Added `R2` manual de-transformation hook and ensured 100% dark eco consumption when transformation ends. | Provide universal R2 cancel and standard eco consumption without HUD modification. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités
Le mod **Dark Jak Enhanced** ajoute un troisième stade d'évolution complet pour Dark Jak dans Jak 2 : le **Méga-Méga Dark Jak (Titan / Colosse)**, accompagné d'améliorations majeures d'acrobatie, de contrôles et de robustesse :

1. **Évolution Progressive en 3 Stades (via `L2`) :**
   - **1ᵉʳ appui sur `L2` (Jak normal) :** Transformation en **Dark Jak classique** (taille x1.05).
   - **2ᵉ appui sur `L2` (Dark Jak) :** Évolution en **Méga Dark Jak / Dark Giant** (taille x2.0).
   - **3ᵉ appui sur `L2` (Méga Dark Jak) :** Évolution ultime en **Méga-Méga Dark Jak / Titan** (taille x3.5).
   - *Note :* L'évolution progressive fonctionne en gameplay standard sans nécessiter de secret.
2. **Détransformation Manuelle (`R2`) & Consommation Totale de l'Éco :**
   - Appuyez sur **`R2`** à tout moment pour détransformer Jak.
   - **Consommation à 100% :** La réserve d'éco noire est entièrement consommée dès la fin de la transformation, peu importe la façon dont elle se termine (`R2`, fin du timer, Dark Bomb, Dark Blast, mort).
3. **HUD Authentique et Intact :**
   - L'HUD d'origine reste parfaitement intact et inchangé.
4. **Caméra Panoramique Dynamique :**
   - Recul et élévation automatique de la caméra (`string-min-length 3.2`, `string-max-length 2.8`) pour un cadrage optimal du titan.
5. **Foulées Lourdes & Secousses Sismiques :**
   - Intensité doublée des secousses d'écran (`screen-shake`) lors des bruits de pas en marche et course.
6. **Déclenchement Instantané de la Dark Bomb :**
   - Déclenchement immédiat de la Dark Bomb à n'importe quel moment du saut dès l'appui sur Carré, annulant immédiatement la vélocité ascendante pour un plongeon rapide.
7. **Dark Blast Résistant aux Collisions :**
   - Le Dark Blast ne s'annule plus prématurément lorsqu'il est déclenché dans des espaces confinés, sous un plafond bas ou près d'obstacles.
8. **Roulade & Roulade Sautée pour Dark Jak Niveau 1 :**
   - Réactivation de la roulade (`L1` en mouvement) et de la roulade sautée (`L1 + Croix`) exclusivement pour **Dark Jak Niveau 1**, tout en conservant la démarche de colosse lourd (sans roulade) pour les stades géants.

---

## 2. Architecture Technique & Modifications

| Fichier | Sous-système | Modifications |
| :--- | :--- | :--- |
| [`goal_src/jak2/engine/target/target-h.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-h.gc) | Définition de Types | Ajout de `(mega-giant)` dans l'énumération `darkjak-stage`. |
| [`goal_src/jak2/engine/target/target-util.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-util.gc) | Utilitaires Joueur | Dans `can-roll?`, autorisation de la roulade pour le niveau 1 et blocage pour les stades `giant` et `mega-giant`. |
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | États de Dark Jak | Évolution débloquée dans `want-to-darkjak?`, annulation manuelle `R2` dans `target-darkjak-post`, Dark Bomb instantanée, fiabilisation de `target-darkjak-bomb1`, et consommation de 100% de l'éco noire à l'arrêt du mode dans `target-darkjak-end-mode`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Gestionnaires d'Événements | Intensité de secousse d'écran doublée pour les pas en mode `mega-giant`. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Locomotion du Joueur | Ajustement des seuils de vélocité, Dark Bomb instantanée, et support de la roulade sautée en Dark Jak Niveau 1. |

---

## 3. Commandes & Procédure de Test

1. Lancer le jeu :
   ```bash
   task boot-game
   ```
2. Ramasser de l'éco noire ou activer le mode debug dans le REPL :
   ```lisp
   (set! (-> *setting-control* user-default cheat-mode) 'debug)
   ```
3. Appuyer sur **`L2`** pour se transformer :
   - **`R2` :** Annule immédiatement la transformation et revient à Jak normal.
   - **2ᵉ et 3ᵉ appuis sur `L2` :** Évolue en Méga Dark Jak et Titan (3.5x).
   - **`L1` / `L1 + Croix` :** Roulade et roulade sautée en Dark Jak Niveau 1.
   - **Carré en l'air (Dark Bomb) :** Plongeon instantané.
   - **L1 + Carré (Dark Blast) :** Salve complète même en espace restreint.
