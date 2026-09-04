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

## ✨ Key Features
- **Peacetime Crimson Guard Patrols:** Quadrupled Crimson Guard rifle patrols (from 9 to 22), introduced 10 tazer guards during peace, and increased patrol guards (from 1 to 6).
- **Military Vehicles:** Increased guard hover bikes from 4 to 10 and Crimson Guard Hellcat cruisers from 3 to 8.
- **Massive Progressive Alert Waves:** Rebalanced all 5 alert levels (0 to 4) scaling up to 28 rifle guards, 10 tazers, 8 grenadiers, 14 hover bikes, and 10 Hellcats at maximum alert.
- **Extended Detection & Activation Ranges:** Expanded cell activation radius from 200m to 240m for vehicles and 120m to 160m for pedestrians.
- **Doubled Nav-Mesh Capacity:** Raised per-district nav-mesh user quota from 64 to 128 simultaneous pathfinding actors, permanently fixing the `too many users for nav-mesh` crash during district streaming.
- **Real-Time Memory & Population Diagnostics:** Live console logging of active/inactive entities, alarm level, and remaining `*default-dead-pool*` memory headroom.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist.
- **Details:** Only GOAL scripts are modified (`traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`). No C++ rebuild needed. For a first-time build, use the fast targeted task:
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
[![Demonstration Video](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://youtu.be/VIDEO_ID)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/VIDEO_ID)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Intensifie considérablement la vie ambiante, la présence militaire et le danger au sein d'Abriville (Haven City) en augmentant massivement les patrouilles de Gardes Grenat, les véhicules d'intervention et les vagues d'alerte, tout en doublant la capacité du nav-mesh et en élargissant les portées d'activation pour assurer une parfaite stabilité moteur.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/config/enhanced_spawnrates`

## ✨ Fonctionnalités Clés
- **Patrouilles de Gardes Grenat Hors-Alerte :** Gardes à fusil plus que doublés (de 9 à 22), ajout de 10 gardes tazer en temps de paix et augmentation des patrouilleurs (de 1 à 6).
- **Véhicules Militaires Accrus :** Flotte de motos de garde augmentée de 4 à 10 et croiseurs Hellcat de 3 à 8.
- **Vagues d'Alerte Massives & Progressifs :** 5 niveaux d'alerte calibrés (0 à 4) déployant jusqu'à 28 gardes à fusil, 10 tazers, 8 grenadiers, 14 motos et 10 Hellcats au palier maximal.
- **Portée de Détection et d'Activation Élargie :** Rayon des cellules de grille porté de 200m à 240m pour les véhicules et de 120m à 160m pour les piétons.
- **Doublement de la Capacité Nav-Mesh :** Quota maximal de chaque nav-mesh doublé de 64 à 128 acteurs simultanés, éliminant définitivement les plantages `too many users for nav-mesh` lors du streaming entre quartiers.
- **Diagnostics Mémoire & Population en Direct :** Suivi périodique en console des entités actives/inactives, de l'alarme et de la marge mémoire restante dans le heap de process (`*default-dead-pool*`).

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà.
- **Détails :** Seuls les scripts GOAL sont modifiés (`traffic-manager.gc`, `traffic-engine.gc`, `nav-mesh.gc`), aucune recompilation C++ n'est nécessaire. En cas de premier build machine, utilisez la tâche ciblée rapide :
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
[![Vidéo de Démonstration](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://youtu.be/VIDEO_ID)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/VIDEO_ID)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/enhanced_spawnrates_readme.md`](docs/modding/current_mod/enhanced_spawnrates_readme.md)

---
*(AI-assisted)*
