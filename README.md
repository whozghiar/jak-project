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
limits, no console spam. Turn it on at `[L3 + SELECT] ▸ Mods ▸ enhanced-spawnrates ▸ Enable`.
The choice persists across level reloads and **takes effect immediately**
(ambient traffic pools are recycled in real-time via `'kill-all` and `'spawn-all`,
so enhanced density and patrols appear without having to reload the city).
Turn it off to restore vanilla traffic immediately.

## ✨ Key Features
- **Peacetime Crimson Guard Patrols:** Quadrupled Crimson Guard rifle patrols (from 9 to 22), introduced 10 tazer guards during peace, and increased patrol guards (from 1 to 6).
- **Military Vehicles:** Increased guard hover bikes from 4 to 10 and Crimson Guard Hellcat cruisers from 3 to 8.
- **Massive Progressive Alert Waves:** Rebalanced all 5 alert levels (0 to 4) scaling up to 28 rifle guards, 10 tazers, 8 grenadiers, 14 hover bikes, and 10 Hellcats at maximum alert.
- **Extended Detection & Activation Ranges:** Expanded cell activation radius from 200m to 240m for vehicles and 120m to 160m for pedestrians.
- **Doubled Nav-Mesh Capacity:** Raised per-district nav-mesh user quota from 64 to 128 simultaneous pathfinding actors, permanently fixing the `too many users for nav-mesh` crash during district streaming.
- **Real-Time Memory & Population Diagnostics:** Live console logging of active/inactive entities, alarm level, and remaining `*default-dead-pool*` memory headroom.
- **Ships OFF, one runtime switch:** everything above is gated behind a single `*mod-enhanced-spawnrates-enable*` flag, toggled from `[L3 + SELECT] ▸ Mods ▸ enhanced-spawnrates ▸ Enable`. Disabled = stock Jak 2.

## 🎮 Usage & Controls
1. Boot the game normally (no debug mode required!). Press **L3 + SELECT** to open the unified in-game **Mods** menu and select **`enhanced-spawnrates`**.
2. Toggle **`Enable`**.
   The choice persists across level reloads and **takes effect immediately**
   (ambient traffic pools are recycled in real-time via `'kill-all` and `'spawn-all`,
   so enhanced density and patrols appear without having to reload the city).
   Turn it off to restore vanilla traffic immediately.

There are no in-world keybindings; the mod is entirely data/spawn tuning.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist.
- **Details:** Only GOAL scripts are modified (`traffic-h.gc`, `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`, the new `pc/features/enhanced-spawnrates-menu.gc`, and `dgos/game.gd`). No C++ rebuild needed. For a first-time build, use the fast targeted task:
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

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/ojMdc_wdyZc)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Intensifie considérablement la vie ambiante, la présence militaire et le danger au sein d'Abriville (Haven City) en augmentant massivement les patrouilles de Gardes Grenat, les véhicules d'intervention et les vagues d'alerte, tout en doublant la capacité du nav-mesh et en élargissant les portées d'activation pour assurer une parfaite stabilité moteur.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/enhanced_spawnrates`

**Le mod est livré DÉSACTIVÉ.** Une installation neuve compilée-mais-désactivée
joue un Jak 2 identique à l'original — densité de trafic, vagues d'alerte et
limites nav-mesh d'origine, aucun message console. Activez-le dans
`[L3 + SELECT] ▸ Mods ▸ enhanced-spawnrates ▸ Enable`.
Le choix de la bascule persiste au rechargement des niveaux et **prend effet
immédiatement** (les pools de trafic ambiant sont recyclés en temps réel via
`'kill-all` et `'spawn-all`, faisant apparaître la densité accrue sans recharger
la ville). Désactivez-le pour rétablir immédiatement le trafic d'origine.

## ✨ Fonctionnalités Clés
- **Patrouilles de Gardes Grenat Hors-Alerte :** Gardes à fusil plus que doublés (de 9 à 22), ajout de 10 gardes tazer en temps de paix et augmentation des patrouilleurs (de 1 à 6).
- **Véhicules Militaires Accrus :** Flotte de motos de garde augmentée de 4 à 10 et croiseurs Hellcat de 3 à 8.
- **Vagues d'Alerte Massives & Progressifs :** 5 niveaux d'alerte calibrés (0 à 4) déployant jusqu'à 28 gardes à fusil, 10 tazers, 8 grenadiers, 14 motos et 10 Hellcats au palier maximal.
- **Portée de Détection et d'Activation Élargie :** Rayon des cellules de grille porté de 200m à 240m pour les véhicules et de 120m à 160m pour les piétons.
- **Doublement de la Capacité Nav-Mesh :** Quota maximal de chaque nav-mesh doublé de 64 à 128 acteurs simultanés, éliminant définitivement les plantages `too many users for nav-mesh` lors du streaming entre quartiers.
- **Diagnostics Mémoire & Population en Direct :** Suivi périodique en console des entités actives/inactives, de l'alarme et de la marge mémoire restante dans le heap de process (`*default-dead-pool*`).
- **Livré DÉSACTIVÉ, un seul interrupteur :** tout ce qui précède est conditionné à l'unique variable `*mod-enhanced-spawnrates-enable*`, basculée depuis `[L3 + SELECT] ▸ Mods ▸ enhanced-spawnrates ▸ Enable`. Désactivé = Jak 2 d'origine.

## 🎮 Utilisation & Commandes
1. Lancez le jeu normalement (aucun mode debug requis !). Appuyez sur **L3 + SELECT** pour ouvrir le menu unifié **Mods** et sélectionnez **`enhanced-spawnrates`**.
2. Basculez **`Enable`**.
   Le choix persiste au rechargement des niveaux et **prend effet immédiatement**
   (les pools de trafic ambiant sont recyclés en temps réel via `'kill-all` et
   `'spawn-all`, faisant apparaître la densité accrue sans devoir recharger la
   ville). Désactivez-le pour rétablir immédiatement le trafic d'origine.

Aucune touche de jeu dédiée ; le mod n'est que du réglage de données / de spawn.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà.
- **Détails :** Seuls des scripts GOAL sont modifiés (`traffic-h.gc`, `traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`, le nouveau `pc/features/enhanced-spawnrates-menu.gc` et `dgos/game.gd`), aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
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
*(AI-assisted)*
