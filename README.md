# Crimson Guard Air-Traffic Gunship — Jak 2 / Canonnière du Trafic Aérien des Gardes — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Ftransport_traffic-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Introduces `transport-v`, a fully operational Crimson Guard troop transport gunship into Haven City's ambient air traffic. The gunship navigates standard high-altitude traffic lanes, can be boarded and piloted by Jak with a usable chin turret, joins city alert pursuits, and hovers steadily to deploy Crimson Guard squads over solid ground.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/transport_traffic`

## ✨ Key Features
- **Ambient Air-Traffic Gunship:** Twin-hull transport flying the ambient city air lanes with a seated Crimson Guard pilot, minimap icon, and Hellcat-matched wingspan for clean cornering.
- **Player Hijacking & Turret Combat:** Jump onto the hull to hijack the ship, triggering a city-wide alarm. Pilot in seated view with an extended chase camera and hold **R1** to fire the chin turret.
- **Alert Pursuit & Squad Deployment:** On alert, AI transports hunt Jak, hover firmly in place at flight altitude, wait for the rear hatch to open, and drop squads of Crimson Guards (immune to jump damage) before resuming aerial pursuit.
- **Persistent Chin Turret & Natural Destruction:** Custom `transport-v-turret` synchronized with the traffic pool (no phantom cannons in the void) and persistent LOD model (`skel-vehicle-turret-v`). If shot down, the ship unfreezes instantly, tumbling and exploding with realistic physics.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required (standard binaries sufficient)
- **Details:** The mod operates within high-level OpenGOAL scripts.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Required (`task extract`)
- **Details:** Required once to compile the resident `.fr3` level packages (`lwidea/b/c.fr3`) with the injected `transport-ag` merc geometry.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
> [!NOTE]
> **Video Demonstration:** Place or view the demonstration recording for this mod at:  
> 📁 [`docs/modding/current_mod/transport_traffic.mp4`](docs/modding/current_mod/transport_traffic.mp4)  
> *(Drop an MP4 video file in this directory to showcase this mod in action).*

## 🔍 Technical Details & Architecture
<details>
<summary><b>Click to expand technical implementation details</b></summary>

### Architecture Summary
- **Type:** Subtype `transport-v` inheriting from `vehicle-guard` in `car.gc`, cloning `*hellcat-constants*` flight dynamics.
- **Turret Process:** `transport-v-turret` child process with `skel-vehicle-turret-v` (LOD1 extended to 999999m, 12m bounds). Automatically synchronizes with traffic pool (`vehicle-method-127`/`128`/`129`), eliminating floating orphan turrets in the void.
- **Deployment State Machine:** `transport-v-deploy-active?`, `transport-v-hatch-ready?`, and `transport-v-update-hatch` managing rear hatch opening and freezing position/orientation in `vehicle-method-121` without altitude drop.
- **Guard Safety:** Temporary invulnerability granted during jump animations and `rigid-body-object-method-48` collision filter to avoid any damage during drop.
- **Destruction Unfreeze:** Instant vitality check releasing position lock on fatal damage so explosion impulse and tumble physics execute naturally.

### Detailed Documentation
For the complete technical breakdown, memory architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/transport_traffic_readme.md`](docs/modding/current_mod/transport_traffic_readme.md)

</details>

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Intègre `transport-v`, un véritable vaisseau de transport de troupes de la Garde Grenat dans le trafic aérien ambiant d'Abriville. Le vaisseau circule dans les voies aériennes en altitude, peut être abordé et piloté par Jak avec une tourelle de proue fonctionnelle, participe aux poursuites d'alerte, et se stabilise pour larguer des escouades de gardes au-dessus des rues.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/transport_traffic`

## ✨ Fonctionnalités Clés
- **Canonnière dans le Trafic Aérien :** Vaisseau de transport à double coque naviguant dans les voies aériennes avec pilote assis, icône minimap dédiée, et envergure calquée sur le Hellcat pour des virages fluides.
- **Prise en Main & Tourelle Joueur :** Sautez sur la carlingue pour éjecter le garde et prendre les commandes, déclenchant l'alarme de la ville (alerte 2). Vue caméra reculée adaptée et tir manuel à la tourelle de proue (**R1**).
- **Poursuite d'Alerte & Déploiement de Troupes :** En alerte, les transports IA traquent Jak, se figent en vol à altitude constante, attendent l'ouverture complète de la soute arrière et larguent des gardes protégés de tout dégât de saut avant de reprendre la chasse.
- **Tourelle Persistante & Destruction Réaliste :** Processus enfant `transport-v-turret` synchronisé avec le pool de trafic (aucun canon fantôme dans le vide) et modèle LOD persistant (`skel-vehicle-turret-v`). En cas de tir fatal, le vaisseau se défige instantanément pour exploser et culbuter avec la physique complète.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise (binaires standards suffisants)
- **Détails :** Le mod s'exécute entièrement dans les scripts de haut niveau OpenGOAL.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Requise (`task extract`)
- **Détails :** Requise une fois pour compiler les packages de niveau résidents (`lwidea/b/c.fr3`) avec la géométrie merc injectée de `transport-ag`.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou via le REPL OpenGOAL avec `task repl`, puis `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
> [!NOTE]
> **Vidéo de démonstration :** L'enregistrement vidéo de démonstration de ce mod est prévu dans :  
> 📁 [`docs/modding/current_mod/transport_traffic.mp4`](docs/modding/current_mod/transport_traffic.mp4)  
> *(Déposez le fichier MP4 dans ce répertoire pour illustrer visuellement les fonctionnalités du mod).*

## 🔍 Détails Techniques & Documentation
<details>
<summary><b>Cliquez pour dérouler les détails techniques d'implémentation</b></summary>

### Résumé de l'Architecture
- **Type :** Sous-type `transport-v` dérivant de `vehicle-guard` dans `car.gc`, reprenant la dynamique de vol de `*hellcat-constants*`.
- **Processus Tourelle :** Enfant `transport-v-turret` avec squelette `skel-vehicle-turret-v` (LOD1 étendu à 999999m, sphère de 12m). Synchronisé avec le cycle de vie du pool (`vehicle-method-127`/`128`/`129`), éliminant les tourelles flottant dans le vide.
- **Machine à États de Largage :** Fonctions `transport-v-deploy-active?`, `transport-v-hatch-ready?` et `transport-v-update-hatch` gérant l'ouverture de soute et l'immobilisation dans `vehicle-method-121` sans perte d'altitude.
- **Protection des Gardes :** Immunité temporaire pendant le saut et filtre de collision `rigid-body-object-method-48` évitant toute blessure à la sortie.
- **Défigeage à la Mort :** Détection instantanée des dégâts mortels libérant le verrouillage de position pour laisser agir l'impulsion d'explosion et le culbutage naturel de l'épave.

### Documentation Complète
Pour l'audit technique approfondi, les structures mémoire et l'historique complet, consultez :
- 📄 [`docs/modding/current_mod/transport_traffic_readme.md`](docs/modding/current_mod/transport_traffic_readme.md)

</details>

---
*(AI-assisted)*
