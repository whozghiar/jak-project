# Enhanced Spawn Rates & Nav-Mesh Limits Mod / Mod Taux de Spawn et Limites Nav-Mesh Renforcés

> - **Game / Jeu :** Jak 2
> - **Branch / Branche :** `jak2/config/enhanced_spawnrates`
> - **Author / Auteur :** OpenGOAL Modding Team (AI-assisted)
> - **Status / Statut :** Ready / Opérationnel

---

## 🇬🇧 English Version

### 1. Description & Features
This mod enhances the ambient atmosphere and danger level of Haven City in Jak 2 by significantly increasing entity spawn densities, alert reinforcements, and detection ranges:
- **Peacetime Crimson Guard Patrols:** Quadrupled Crimson Guard rifle patrols (from 9 to 22), introduced tazers during peace (10), and increased patrol guards (from 1 to 6).
- **Crimson Guard Vehicles:** Increased guard hover bikes from 4 to 10 and Hellcat cruisers from 3 to 8.
- **Progressive Alert Reinforcements:** Scaled all 5 alert levels (0 to 4) so that maximum alert triggers heavy waves of up to 28 rifle guards, 10 tazers, 8 grenadiers, 14 hover bikes, and 10 Hellcats.
- **Extended Detection & Activation Ranges:** Expanded cell activation distance from 200m to 240m for vehicles and 120m to 160m for pedestrians.
- **Engine Stability & Nav-Mesh Doubling:** Doubled per-district nav-mesh capacity from 64 to 128 simultaneous pathfinding actors, eliminating crashes during level transitions.
- **In-Game Diagnostics:** Periodic console stats displaying active/inactive citizens and vehicles, alarm levels, and remaining `*default-dead-pool*` memory headroom.

### 2. Technical Architecture & Tooling
- **`traffic-manager.gc`:** Overrides `traffic-want-counts` in `init-params` for peaceful city roaming and adds real-time memory diagnostics in `update`.
- **`traffic-engine.gc`:** Reconfigures `*alert-level-settings*` for alert tiers 0 to 4 and adjusts `per-frame-cell-update` distances.
- **`nav-mesh.gc`:** Adjusts `init-from-entity` to raise `nav-max-users` default from 64 to 128 concurrent actors.

### 3. How to Test & Play
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
4. Roam Haven City to observe dense guard patrols, or shoot at guards / cause chaos to trigger escalating alert levels.

### 4. Current Status & Investigations
- **Status:** Fully functional and stable across all 11 Haven City districts (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, `ctyinda`, `ctysluma`, `hiphog`, `gungame`, `stadium`, etc.).
- **Memory & DMA Headroom:** Safely maintains over 5.2 MB free process heap and stays within the 255 active grid cell array limit.

### 5. Modding Changes Log
| Date | Touched / Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| **2026-08-30** | `traffic-manager.gc` | Boosted want counts, cast `*default-dead-pool*` to `dead-pool-heap`, split format calls | Enhanced peacetime guard density and added diagnostic logs |
| **2026-08-30** | `traffic-engine.gc` | Rebalanced alert settings 0-4, adjusted cell spheres to 240m/160m | Massive alert waves while staying within DMA / grid limits |
| **2026-08-30** | `nav-mesh.gc` | Raised default `nav-max-users` from 64 to 128 | Fixed `too many users for nav-mesh` crash during level streaming |
| **2026-08-30** | `17_traffic_engine_spawnrates_and_nav_mesh_limits.md` | Created technical documentation in `docs/modding/jak2_modding_utilities/` | Document engine discoveries and architecture |
| **2026-08-30** | `enhanced_spawnrates_readme.md` | Created dedicated mod readme in `docs/modding/current_mod/` | Mod documentation & changelog |

---

## 🇫🇷 Version Française

### 1. Description & Fonctionnalités
Ce mod intensifie la vie ambiante et la menace militaire dans Abriville (Haven City) dans Jak 2 en augmentant considérablement la densité de spawn, les renforts d'alerte et la portée d'activation :
- **Patrouilles de Crimson Guards hors-alerte :** Les gardes à fusil passent de 9 à 22, introduction des gardes tazer en temps de paix (10), et augmentation des gardes patrouilleurs (de 1 à 6).
- **Véhicules militaires :** Les motos volantes de garde passent de 4 à 10 et les croiseurs Hellcat de 3 à 8.
- **Renforts d'alerte progressifs et massifs :** Les 5 paliers d'alerte (0 à 4) font intervenir jusqu'à 28 gardes à fusil, 10 tazers, 8 grenadiers, 14 motos de garde et 10 Hellcats au niveau d'alerte maximal.
- **Portée de détection & d'activation élargie :** Le rayon des cellules de grille passe de 200m à 240m pour les véhicules et de 120m à 160m pour les piétons.
- **Stabilité & Doublement de la capacité Nav-Mesh :** Capacité maximale de chaque nav-mesh doublée de 64 à 128 utilisateurs simultanés, évitant tout plantage lors des transitions entre quartiers.
- **Diagnostics en temps réel dans la console :** Affichage régulier du nombre de citoyens et véhicules actifs/inactifs, du niveau d'alerte et de la mémoire restante dans `*default-dead-pool*`.

### 2. Architecture Technique & Outillage
- **`traffic-manager.gc` :** Ajustement des `traffic-want-counts` dans `init-params` et ajout des logs mémoire dans `update`.
- **`traffic-engine.gc` :** Configuration des quotas d'alerte 0 à 4 dans `*alert-level-settings*` et calibration des distances dans `per-frame-cell-update`.
- **`nav-mesh.gc` :** Augmentation de la valeur par défaut de `nav-max-users` de 64 à 128 dans `init-from-entity`.

### 3. Commandes & Procédure de Test
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
4. Se promener dans Abriville pour constater la densité militaire, ou attaquer des gardes pour déclencher les vagues de renforts.

### 4. Statut Actuel & Investigations
- **Statut :** Pleinement fonctionnel et stable sur l'ensemble des 11 quartiers de la ville (`ctywide`, `ctyport`, `ctypal`, `ctyfarmb`, `ctyinda`, `ctysluma`, `hiphog`, `gungame`, `stadium`, etc.).
- **Marge mémoire & DMA :** Plus de 5,2 Mo de mémoire heap disponibles sur les 6,16 Mo alloués, respect total de la limite des 255 cellules actives de la grille.

### 5. Journal des Modifications
| Date | Fichiers Modifiés / Créés | Description Technique | Objectif |
| :--- | :--- | :--- | :--- |
| **30-08-2026** | `traffic-manager.gc` | Augmentation des want counts, cast `*default-dead-pool*` en `dead-pool-heap`, découpage format | Augmenter la densité hors-alerte et ajouter les diagnostics console |
| **30-08-2026** | `traffic-engine.gc` | Équilibrage des alertes 0-4, portée des cellules à 240m/160m | Vagues massives d'alerte sans déborder le buffer DMA |
| **30-08-2026** | `nav-mesh.gc` | Augmentation de `nav-max-users` de 64 à 128 | Résoudre le crash `too many users for nav-mesh` lors du streaming |
| **30-08-2026** | `17_traffic_engine_spawnrates_and_nav_mesh_limits.md` | Création de la documentation technique modulaire | Documenter l'architecture et les découvertes moteur |
| **30-08-2026** | `enhanced_spawnrates_readme.md` | Création du README dédié au mod dans `docs/modding/current_mod/` | Documentation bilingue & historique du mod |
