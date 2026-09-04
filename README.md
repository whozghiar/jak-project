# Crimson Guard Transport Ship in Ambient Traffic / Vaisseau de Transport des Gardes dans le Trafic Aérien

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Ftransport_traffic-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Integrates transport-v, an authentic Crimson Guard troop transport gunship into Haven City's ambient high-altitude traffic lanes, pilotable by Jak with a functional turret, chasing during alerts, and hovering to drop squads.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/transport_traffic`

## ✨ Key Features
- **Ambient High-Altitude Gunship:**  Dual-hull troop transport navigating city flight lanes with seated pilot and minimap icon.
- **Player Hijacking & Turret Controls:**  Leap onto the hull to eject the guard, take the helm, and fire the nose turret (R1).
- **Alert Pursuits & Troop Drop:**  Pursues Jak during city alerts, locks altitude in place, opens rear hatch, and drops invulnerable guards.
- **Persistent Turret & Realistic Crash:**  Synchronized turret child process with LOD and unlocked tumble physics upon fatal damage.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (Layer 1 & Layer 2 — Decompiler & Runtime)
- **Details:** Compiles the runtime, compiler, and decompiler required for asset extraction:
```bash
task build-release-game
task build-release-decomp
```

### 3. Asset Extraction
- **Status:** Custom extraction required (Layer 2)
- **Details:** Re-run extraction to process custom assets and modified decompiler configuration:
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
[![Demonstration Video](https://img.youtube.com/vi/MnqnybexhSA/maxresdefault.jpg)](https://youtu.be/MnqnybexhSA)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/MnqnybexhSA)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/transport_traffic_readme.md`](docs/modding/current_mod/transport_traffic_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Intègre transport-v, un véritable vaisseau de transport de troupes de la Garde Grenat dans le trafic aérien ambiant d'Abriville, pilotable par Jak avec tourelle fonctionnelle, poursuites d'alerte et largage de troupes.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/transport_traffic`

## ✨ Fonctionnalités Clés
- **Canonnière dans le Trafic Aérien  :**  Vaisseau de transport à double coque naviguant dans les voies aériennes avec pilote assis et icône minimap.
- **Prise en Main & Tourelle Joueur  :**  Sautez sur la carlingue pour éjecter le garde, prendre les commandes et tirer à la tourelle de proue (R1).
- **Poursuite d'Alerte & Déploiement  :**  Traque Jak en alerte, se fige à altitude constante, ouvre la soute arrière et largue des gardes protégés.
- **Tourelle Persistante & Destruction Réaliste  :**  Processus tourelle synchronisé au pool avec physique de culbutage naturelle en cas de destruction.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (Couche 1 & Couche 2 — Décompilateur & Runtime)
- **Détails :** Compile le runtime, le compilateur et le décompilateur nécessaires à l'extraction des assets :
```bash
task build-release-game
task build-release-decomp
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction personnalisée requise (Couche 2)
- **Détails :** Relancez l'extraction pour intégrer les assets modifiés et la configuration du décompilateur :
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
[![Vidéo de Démonstration](https://img.youtube.com/vi/MnqnybexhSA/maxresdefault.jpg)](https://youtu.be/MnqnybexhSA)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/MnqnybexhSA)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/transport_traffic_readme.md`](docs/modding/current_mod/transport_traffic_readme.md)

---
*(AI-assisted)*
