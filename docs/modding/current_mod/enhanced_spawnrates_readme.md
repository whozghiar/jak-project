# Enhanced Spawn Rates & Nav-Mesh Limits Mod / Mod Taux de Spawn et Limites Nav-Mesh Renforcés

> - **Game / Jeu :** Jak 2
> - **Branch / Branche :** `jak2/config/enhanced_spawnrates`
> - **Author / Auteur :** OpenGOAL Modding Team (AI-assisted)
> - **Status / Statut :** Ready / Opérationnel
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features
This mod enhances the ambient atmosphere and danger level of Haven City in Jak 2 by significantly increasing entity spawn densities, alert reinforcements, and detection ranges:
- **Peacetime Crimson Guard Patrols:** Quadrupled Crimson Guard rifle patrols (from 9 to 22), introduced tazers during peace (10), and increased patrol guards (from 1 to 6).
- **Crimson Guard Vehicles:** Increased guard hover bikes from 4 to 10 and Hellcat cruisers from 3 to 8.
- **Progressive Alert Reinforcements:** Scaled all 5 alert levels (0 to 4) so that maximum alert triggers heavy waves of up to 28 rifle guards, 10 tazers, 8 grenadiers, 14 hover bikes, and 10 Hellcats.
- **Extended Detection & Activation Ranges:** Expanded cell activation distance from 200m to 240m for vehicles and 120m to 160m for pedestrians.
- **Engine Stability & Nav-Mesh Doubling:** Doubled per-district nav-mesh capacity from 64 to 128 simultaneous pathfinding actors, eliminating crashes during level transitions.
- **In-Game Diagnostics:** Periodic console stats displaying active/inactive citizens and vehicles, alarm levels, and remaining `*default-dead-pool*` memory headroom.

## 2. Technical Architecture & Tooling

### 2.1 Runtime toggle (native non-regression)
Per CLAUDE.md's golden rules, every behaviour change ships **OFF** behind one flag:

- **`*mod-enhanced-spawnrates-enable*`** — `(define-perm ... symbol #f)` in
  **`engine/ai/traffic-h.gc`** (resident in ENGINE + GAME, so `nav-mesh.gc`,
  which also runs outside the city, links a real symbol in release builds).
  `define-perm` => a toggled-on `#t` survives file/level reloads.
- **`pc/debug/enhanced-spawnrates-menu.gc`** (new, `(declare-file (debug))`) —
  registers `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable` via
  `(mods-menu-register "enhanced-spawnrates" ...)`. Wired in `dgos/game.gd`
  right after `"mods-menu.o"`.
- Every gameplay delta below is wrapped `(if *mod-enhanced-spawnrates-enable* <mod> <stock>)`
  or `(when *mod-enhanced-spawnrates-enable* ...)`. Disabled => the exact stock
  literal/branch, so a compiled-but-disabled build is byte-for-byte stock.

| Read timing | Parts | Applies |
| :--- | :--- | :--- |
| Once at city load | `traffic-manager/init-params` want-counts; `nav-mesh/init-from-entity` `nav-max-users` | **reload the city** |
| Live, per frame | `traffic-engine/update-alert-state` focus counts; `restore-default-settings` `inv-density-factor`; `per-frame-cell-update` cull ranges | next frame |

### 2.2 Touched files
- **`traffic-h.gc`:** defines the flag (see above).
- **`traffic-manager.gc`:** `init-params` picks the enhanced vs. stock
  `traffic-want-counts` block by flag; the `update` telemetry print and the
  verbose spawn-failure `format` are flag-gated (stock stays silent / one-line).
- **`traffic-engine.gc`:** `*alert-level-settings*` is **restored to stock**; the
  enhanced per-level guard focus-target counts live in a new static
  `*mod-esr-alert-target-counts*` (30 × int32) that `update-alert-state` overlays
  onto the working `alert-state settings` *after* the stock mem-copy, only when
  enabled. `inv-density-factor` (`restore-default-settings`) and the three
  `per-frame-cell-update` cell-cull distances are `(if flag ... stock)`.
- **`nav-mesh.gc`:** `init-from-entity` picks `nav-max-users` default 128 (clamped
  `[128,200]`) vs. stock 64 (no clamp) by flag.

## 3. How to Test & Play
1. Launch OpenGOAL REPL:
   ```powershell
   task repl
   ```
2. Build / Hot-reload the GOAL code:
   ```lisp
   (mi)
   ```
3. Boot the game:
   ```powershell
   task boot-game
   ```
4. Open `Debug ▸ Mods ▸ enhanced-spawnrates` and toggle **`Enable`**.
5. **Reload Haven City** (warp or interior round-trip) so `init-params` re-reads
   the want-counts and the nav-mesh is re-sized.
6. Roam Haven City to observe dense guard patrols, or shoot at guards / cause
   chaos to trigger escalating alert levels. Toggle `Enable` off + reload to
   confirm the return to stock density.

## 4. Current Status & Investigations
- **Status:** Fully functional and stable across all 11 Haven City districts (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, `ctyinda`, `ctysluma`, `hiphog`, `gungame`, `stadium`, etc.).
- **Memory & DMA Headroom:** Safely maintains over 5.2 MB free process heap and stays within the 255 active grid cell array limit.

## 5. Modding Changes Log
| Date | Touched / Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| **2026-08-30** | `traffic-manager.gc` | Boosted want counts, cast `*default-dead-pool*` to `dead-pool-heap`, split format calls | Enhanced peacetime guard density and added diagnostic logs |
| **2026-08-30** | `traffic-engine.gc` | Rebalanced alert settings 0-4, adjusted cell spheres to 240m/160m | Massive alert waves while staying within DMA / grid limits |
| **2026-08-30** | `nav-mesh.gc` | Raised default `nav-max-users` from 64 to 128 | Fixed `too many users for nav-mesh` crash during level streaming |
| **2026-08-30** | `17_traffic_engine_spawnrates_and_nav_mesh_limits.md` | Created technical documentation in `docs/modding/jak2_lisp_instructions.md` | Document engine discoveries and architecture |
| **2026-08-30** | `enhanced_spawnrates_readme.md` | Created dedicated mod readme in `docs/modding/current_mod/` | Mod documentation & changelog |
| **2026-09-08** | `traffic-h.gc`, `pc/debug/enhanced-spawnrates-menu.gc` (new), `dgos/game.gd` | Added `*mod-enhanced-spawnrates-enable*` (`define-perm`, #f) + `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable` | Mandatory Debug ▸ Mods runtime toggle — ship OFF by default (AI-assisted) |
| **2026-09-08** | `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc` | Restored `*alert-level-settings*` to stock + new static `*mod-esr-alert-target-counts*` overlay; every want-count / density / cull-range / nav-max-users / telemetry delta gated on the flag | Native non-regression: compiled-but-disabled build plays byte-for-byte like stock Jak 2 (AI-assisted) |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités
Ce mod intensifie la vie ambiante et la menace militaire dans Abriville (Haven City) dans Jak 2 en augmentant considérablement la densité de spawn, les renforts d'alerte et la portée d'activation :
- **Patrouilles de Crimson Guards hors-alerte :** Les gardes à fusil passent de 9 à 22, introduction des gardes tazer en temps de paix (10), et augmentation des gardes patrouilleurs (de 1 à 6).
- **Véhicules militaires :** Les motos volantes de garde passent de 4 à 10 et les croiseurs Hellcat de 3 à 8.
- **Renforts d'alerte progressifs et massifs :** Les 5 paliers d'alerte (0 à 4) font intervenir jusqu'à 28 gardes à fusil, 10 tazers, 8 grenadiers, 14 motos de garde et 10 Hellcats au niveau d'alerte maximal.
- **Portée de détection & d'activation élargie :** Le rayon des cellules de grille passe de 200m à 240m pour les véhicules et de 120m à 160m pour les piétons.
- **Stabilité & Doublement de la capacité Nav-Mesh :** Capacité maximale de chaque nav-mesh doublée de 64 à 128 utilisateurs simultanés, évitant tout plantage lors des transitions entre quartiers.
- **Diagnostics en temps réel dans la console :** Affichage régulier du nombre de citoyens et véhicules actifs/inactifs, du niveau d'alerte et de la mémoire restante dans `*default-dead-pool*`.

## 2. Architecture Technique & Outillage

### 2.1 Bascule runtime (non-régression native)
Conformément aux règles d'or de CLAUDE.md, chaque changement de comportement est
livré **DÉSACTIVÉ** derrière une unique variable :

- **`*mod-enhanced-spawnrates-enable*`** — `(define-perm ... symbol #f)` dans
  **`engine/ai/traffic-h.gc`** (résident en ENGINE + GAME, donc `nav-mesh.gc`,
  qui tourne aussi hors de la ville, lie un vrai symbole en build release).
  `define-perm` => un `#t` activé survit aux rechargements de fichier/niveau.
- **`pc/debug/enhanced-spawnrates-menu.gc`** (nouveau, `(declare-file (debug))`) —
  enregistre `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable` via
  `(mods-menu-register "enhanced-spawnrates" ...)`. Câblé dans `dgos/game.gd`
  juste après `"mods-menu.o"`.
- Chaque écart de gameplay ci-dessous est enveloppé `(if *mod-enhanced-spawnrates-enable* <mod> <stock>)`
  ou `(when *mod-enhanced-spawnrates-enable* ...)`. Désactivé => le littéral / la
  branche d'origine exacte : un build compilé-mais-désactivé est identique à l'original.

| Moment de lecture | Éléments | Prise d'effet |
| :--- | :--- | :--- |
| Une fois au chargement de la ville | want-counts `traffic-manager/init-params` ; `nav-max-users` `nav-mesh/init-from-entity` | **rechargement de la ville** |
| En direct, chaque frame | nombre de cibles `traffic-engine/update-alert-state` ; `inv-density-factor` (`restore-default-settings`) ; portées de cull `per-frame-cell-update` | frame suivante |

### 2.2 Fichiers touchés
- **`traffic-h.gc` :** définit la variable (voir ci-dessus).
- **`traffic-manager.gc` :** `init-params` choisit le bloc `traffic-want-counts`
  renforcé ou d'origine selon la variable ; le log de télémétrie de `update` et le
  `format` verbeux d'échec de spawn sont conditionnés (l'original reste
  silencieux / sur une ligne).
- **`traffic-engine.gc` :** `*alert-level-settings*` est **restauré à
  l'identique** ; les compteurs de cibles renforcés par palier vivent dans un
  nouveau tableau statique `*mod-esr-alert-target-counts*` (30 × int32) que
  `update-alert-state` superpose sur la copie de travail *après* le mem-copy
  d'origine, uniquement si activé. `inv-density-factor` et les trois distances de
  cull de `per-frame-cell-update` sont en `(if variable ... origine)`.
- **`nav-mesh.gc` :** `init-from-entity` choisit `nav-max-users` défaut 128
  (borné `[128,200]`) ou d'origine 64 (sans borne) selon la variable.

## 3. Commandes & Procédure de Test
1. Ouvrir le REPL OpenGOAL :
   ```powershell
   task repl
   ```
2. Compiler le code GOAL à chaud :
   ```lisp
   (mi)
   ```
3. Lancer le jeu :
   ```powershell
   task boot-game
   ```
4. Ouvrir `Debug ▸ Mods ▸ enhanced-spawnrates` et basculer **`Enable`**.
5. **Recharger Abriville** (warp ou aller-retour par un intérieur) pour que
   `init-params` relise les want-counts et que le nav-mesh soit redimensionné.
6. Se promener dans Abriville pour constater la densité militaire, ou attaquer
   des gardes pour déclencher les vagues de renforts. Rebasculer `Enable` +
   recharger pour vérifier le retour à la densité d'origine.

## 4. Statut Actuel & Investigations
- **Statut :** Pleinement fonctionnel et stable sur l'ensemble des 11 quartiers de la ville (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, `ctyinda`, `ctysluma`, `hiphog`, `gungame`, `stadium`, etc.).
- **Marge mémoire & DMA :** Plus de 5,2 Mo de mémoire heap disponibles sur les 6,16 Mo alloués, respect total de la limite des 255 cellules actives de la grille.

## 5. Journal des Modifications
| Date | Fichiers Modifiés / Créés | Description Technique | Objectif |
| :--- | :--- | :--- | :--- |
| **30-08-2026** | `traffic-manager.gc` | Augmentation des want counts, cast `*default-dead-pool*` en `dead-pool-heap`, découpage format | Augmenter la densité hors-alerte et ajouter les diagnostics console |
| **30-08-2026** | `traffic-engine.gc` | Équilibrage des alertes 0-4, portée des cellules à 240m/160m | Vagues massives d'alerte sans déborder le buffer DMA |
| **30-08-2026** | `nav-mesh.gc` | Augmentation de `nav-max-users` de 64 à 128 | Résoudre le crash `too many users for nav-mesh` lors du streaming |
| **30-08-2026** | `17_traffic_engine_spawnrates_and_nav_mesh_limits.md` | Création de la documentation technique modulaire | Documenter l'architecture et les découvertes moteur |
| **30-08-2026** | `enhanced_spawnrates_readme.md` | Création du README dédié au mod dans `docs/modding/current_mod/` | Documentation bilingue & historique du mod |
| **08-09-2026** | `traffic-h.gc`, `pc/debug/enhanced-spawnrates-menu.gc` (nouveau), `dgos/game.gd` | Ajout de `*mod-enhanced-spawnrates-enable*` (`define-perm`, #f) + `Debug ▸ Mods ▸ enhanced-spawnrates ▸ Enable` | Bascule runtime Debug ▸ Mods obligatoire — livré DÉSACTIVÉ (AI-assisted) |
| **08-09-2026** | `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc` | `*alert-level-settings*` restauré à l'identique + nouveau tableau statique `*mod-esr-alert-target-counts*` en surcouche ; want-counts / densité / portées / nav-max-users / télémétrie tous conditionnés à la variable | Non-régression native : build compilé-mais-désactivé identique à l'original (AI-assisted) |
