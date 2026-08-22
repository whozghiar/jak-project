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
The **Dark Jak Enhanced** mod adds a full 3rd evolutionary stage to Dark Jak in Jak 2: the **Mega-Mega Dark Jak (Titan / Colossus)**, alongside critical quality-of-life, acrobatic, HUD, and responsiveness enhancements:

1. **Progressive 3-Tier Transformation (via `L2`):**
   - **1st `L2` Press (Normal Jak):** Transforms into **Classic Dark Jak** (scale x1.05).
   - **2nd `L2` Press (Dark Jak):** Evolves into **Mega Dark Jak / Dark Giant** (scale x2.0).
   - **3rd `L2` Press (Mega Dark Jak):** Evolves into **Mega-Mega Dark Jak / Titan** (scale x3.5).
   - *Note:* Transformation and progressive evolution are fully unlocked in standard gameplay without requiring story cheat unlocks.
2. **Instant Manual De-Transformation (`R2`) with Proportional Eco Retention:**
   - Press **`R2`** at any moment in any state to instantly revert back to normal Jak.
   - **Proportional Eco Retention:** Dark eco is drained in real-time. If you interrupt the transformation early via `R2`, you keep all your remaining dark eco!
   - Super attacks (Dark Bomb, Dark Blast) consume all remaining dark eco upon execution.
3. **Optimized HUD Countdown Meter & Icon Scaling:**
   - In normal timer mode, the circular purple Dark Eco gauge on the HUD progressively depletes from 100% to 0% in real time.
   - The Dark Jak head icon inside the HUD is scaled to fit inside the ring (scale 1.0), keeping the circular purple gauge clearly readable.
   - When the Infinite Dark Jak secret is active, the gauge remains fully charged (100%).
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
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | Dark Jak States | Unlocked progressive evolution in `want-to-darkjak?`, real-time proportional eco drain in `target-darkjak-process`, `R2` manual cancel in `target-darkjak-post`, instant upward momentum cancellation in `target-darkjak-bomb0`, and collision-resilient `:trans`/`:exit` in `target-darkjak-bomb1`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Event Handlers | Doubled camera smush intensity on `effect-control` footsteps in `mega-giant` stage. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Player Locomotion | Scaled jump velocity thresholds, instant Dark Bomb triggers, and support for roll-flip jumps in Level 1 Dark Jak. |
| [`goal_src/jak2/engine/ui/hud-classes.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/ui/hud-classes.gc) | User Interface | Dynamically compute remaining Dark Jak timer percentage into `values 2 target` and scaled head icon to 1.0 in `hud-dark-eco-symbol draw`. |

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
   - **HUD Gauge & Head Icon :** Observe the head icon fitting inside the purple circular meter as it depletes in real-time.
   - **`R2` :** Instantly reverts Jak to his normal form and retains the remaining dark eco!
   - **2nd & 3rd `L2` :** Evolve into Mega Dark Jak and Titan (3.5x) even with unlimited secret OFF.
   - **`L1` / `L1 + X` :** Roll and roll-flip in Level 1 Dark Jak.
   - **Square in air :** Instant Dark Bomb.
   - **L1 + Square :** Collision-resilient Dark Blast.

---

## 4. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-08-22 | `target-h.gc`, `target-darkjak.gc`, `target-handler.gc` | Added `(mega-giant)` enum bitfield and implemented 3.5x progressive scaling, panoramic camera, and amplified footstep shakes. | Implement Stage 3 Colossal Dark Jak. |
| 2026-08-22 | `target.gc` | Scaled vertical jump velocity gates by `darkjak-giant-interp`. | Fix Dark Bomb not triggering in Mega Giant mode. |
| 2026-08-22 | `target-darkjak.gc` | Removed `on-surface` abort in `target-darkjak-bomb1 :trans` and cleaned `:exit`. | Prevent Dark Blast from cancelling prematurely on surface contact. |
| 2026-08-22 | `target.gc`, `target-darkjak.gc` | Allowed instantaneous Square press trigger during jumps and zeroed upward `transv` on `bomb0 :enter`. | Allow responsive instant plunge for Dark Bomb. |
| 2026-08-22 | `target-util.gc`, `target.gc` | Enabled roll only for Level 1 Dark Jak in `can-roll?` and disabled it for `giant` and `mega-giant` stages. | Maintain agile roll for Level 1 Dark Jak while keeping giant stages heavy and grounded. |
| 2026-08-22 | `target-darkjak.gc`, `hud-classes.gc` | Added `R2` manual de-transformation hook in `target-darkjak-post` and piped remaining timer ratio into `hud-health`/`hud-dark-eco-symbol`. | Provide universal R2 cancel and HUD countdown meter. |
| 2026-08-22 | `hud-classes.gc`, `target-darkjak.gc` | Scaled HUD head icon to 1.0, unlocked evolution without cheat in `want-to-darkjak?`, and implemented real-time proportional eco drain. | Optimize HUD gauge visibility, unlock natural giant progression, and retain remaining eco on early cancel. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités
Le mod **Dark Jak Enhanced** ajoute un troisième stade d'évolution complet pour Dark Jak dans Jak 2 : le **Méga-Méga Dark Jak (Titan / Colosse)**, accompagné d'améliorations majeures d'acrobatie, de contrôles, d'HUD et de robustesse :

1. **Évolution Progressive en 3 Stades (via `L2`) :**
   - **1ᵉʳ appui sur `L2` (Jak normal) :** Transformation en **Dark Jak classique** (taille x1.05).
   - **2ᵉ appui sur `L2` (Dark Jak) :** Évolution en **Méga Dark Jak / Dark Giant** (taille x2.0).
   - **3ᵉ appui sur `L2` (Méga Dark Jak) :** Évolution ultime en **Méga-Méga Dark Jak / Titan** (taille x3.5).
   - *Note :* L'évolution progressive fonctionne désormais en gameplay standard sans nécessiter le secret du jeu.
2. **Détransformation Manuelle (`R2`) & Conservation Proportionnelle de l'Éco :**
   - Appuyez sur **`R2`** à tout moment pour détransformer Jak.
   - **Perte proportionnelle :** L'éco noire se vide progressivement en temps réel. Si vous annulez la transformation prématurément avec `R2`, vous conservez toute l'éco noire restante !
   - Les super-attaques (Dark Bomb, Dark Blast) consomment la totalité de l'éco restante lors du déclenchement.
3. **Jauge HUD Optimisée & Icône Ajustée :**
   - La jauge circulaire violette de l'HUD se vide progressivement de 100% à 0% en temps réel.
   - L'icône de tête de Dark Jak est mise à l'échelle 1.0 et parfaitement centrée pour laisser la jauge circulaire violette 100% lisible.
   - Lorsque le secret Dark Jak Infini est actif, la jauge reste pleine à 100%.
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
| [`goal_src/jak2/engine/target/target-darkjak.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-darkjak.gc) | États de Dark Jak | Évolution débloquée dans `want-to-darkjak?`, drain d'éco proportionnel en temps réel dans `target-darkjak-process`, annulation `R2` dans `target-darkjak-post`, Dark Bomb instantanée et fiabilisation de `target-darkjak-bomb1`. |
| [`goal_src/jak2/engine/target/target-handler.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target-handler.gc) | Gestionnaires d'Événements | Intensité de secousse d'écran doublée pour les pas en mode `mega-giant`. |
| [`goal_src/jak2/engine/target/target.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/target/target.gc) | Locomotion du Joueur | Ajustement des seuils de vélocité, Dark Bomb instantanée, et support de la roulade sautée en Dark Jak Niveau 1. |
| [`goal_src/jak2/engine/ui/hud-classes.gc`](file:///c:/Users/theol/Documents/Developpement/jak-project/goal_src/jak2/engine/ui/hud-classes.gc) | Interface Utilisateur | Calcul dynamique du ratio de temps restant sur `values 2 target` et réduction de la taille de l'icône de tête à 1.0 dans `hud-dark-eco-symbol draw`. |

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
   - **Jauge & Icône HUD :** L'icône de tête est parfaitement ajustée et la jauge violette se vide en temps réel.
   - **`R2` :** Annule immédiatement la transformation et préserve l'éco noire restante proportionnellement au temps utilisé !
   - **2ᵉ et 3ᵉ appuis sur `L2` :** Évolue en Méga Dark Jak et Titan (3.5x) même sans secret activé.
   - **`L1` / `L1 + Croix` :** Roulade et roulade sautée en Dark Jak Niveau 1.
   - **Carré en l'air :** Dark Bomb instantanée.
   - **L1 + Carré :** Dark Blast résistant aux collisions.
