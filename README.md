# Multiplayer — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fmultiplayer-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Local-network, presence-only multiplayer for Jak 2. Each player runs their own game instance;
instances see each other's live position, orientation, coarse animation, and chosen skin (Jak or
a Krimzon Guard) rendered as non-interactive stand-ins. Each instance still fully simulates its
own independent game/combat/enemies - v1 does **not** synchronize gameplay, only presence. See
[`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)
for the full technical breakdown.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/multiplayer`

## ✨ Key Features
- **UDP presence sync:** every instance broadcasts its player's live position/orientation/coarse
  animation/skin to a fixed list of peers over loopback or LAN, up to 4 players, no server needed.
- **Character selection:** play as Jak or a Krimzon Guard - a live re-skin of the existing player
  character (same physics/controls), toggled with a REPL command and visible to every connected
  peer.
- **Zero setup beyond a few environment variables:** no matchmaking, no account, no internet
  connectivity required - just point each instance at the others' IP:port.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Required (Layer 1 — C++ Runtime & Compiler)
- **Details:** Compiles the modified C++ runtime (`gk`) and compiler (`goalc`) using the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

---|---|
| `common/network/multiplayer_protocol.h` (new) | Shared UDP wire format / GOAL-FFI struct |
| `game/system/multiplayer/mp_session.{h,cpp}` (new) | UDP socket + peer table |
| `game/system/multiplayer/mp_goal_bridge.{h,cpp}` (new) | FFI functions exposed to GOAL |
| `common/cross_sockets/XSocket.h/.cpp` | Added UDP primitives (`bind_socket`, `send_to_socket`, `recv_from_socket`) |
| `game/kernel/jak2/kmachine.cpp` | Registered the `mp-*` FFI functions |
| `game/CMakeLists.txt` | Added the two new `.cpp` files to the build |
| `goal_src/jak2/pc/multiplayer/mp-h.gc` (new) | Shared enums + the `mp-player-state` structure |
| `goal_src/jak2/pc/multiplayer/remote-player.gc` (new) | Non-interactive remote-player stub process |
| `goal_src/jak2/pc/multiplayer/mp-manager.gc` (new) | Always-resident manager: broadcast/poll/spawn/despawn, `(mp-toggle-skin!)` |
| `goal_src/jak2/kernel-defs.gc` | `define-extern` forward declarations for the `mp-*` functions |
| `goal_src/jak2/dgos/game.gd` | Registered `mp-h.o`, `remote-player.o`, `mp-manager.o` |
| `goal_src/jak2/engine/target/logic-target.gc` | One added line spawning the manager singleton |

See [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)
for the full rationale, known limitations, and non-goals.

## 🎥 Demonstration Video

[![Demonstration Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Watch the demonstration video on YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `YOUR_VIDEO_ID` with the YouTube video ID (e.g. `MnqnybexhSA`) and `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` with the video URL (e.g. `https://youtu.be/MnqnybexhSA`).*

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Multijoueur en réseau local, présence uniquement, pour Jak 2. Chaque joueur lance sa propre
instance du jeu ; les instances voient la position, l'orientation, l'animation grossière et le
skin choisi (Jak ou un garde Krimzon) des autres joueurs, affichés comme des doublures
non-interactives. Chaque instance simule toujours entièrement son propre jeu/combat/ennemis - la
v1 ne synchronise **pas** le gameplay, uniquement la présence. Voir
[`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)
pour l'analyse technique complète.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/multiplayer`

## ✨ Fonctionnalités Clés
- **Synchronisation de présence en UDP :** chaque instance diffuse la position/orientation/
  animation grossière/skin de son joueur à une liste fixe de pairs, en local ou sur LAN, jusqu'à
  4 joueurs, sans serveur.
- **Sélection de personnage :** jouer en Jak ou en garde Krimzon - un reskin à chaud du personnage
  joueur existant (mêmes physique/contrôles), basculé via une commande REPL et visible par chaque
  pair connecté.
- **Aucune configuration au-delà de quelques variables d'environnement :** pas de matchmaking, pas
  de compte, aucune connectivité Internet requise - il suffit de pointer chaque instance vers
  l'IP:port des autres.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Requise (Couche 1 — Runtime C++ & Compilateur)
- **Détails :** Compile le runtime C++ (`gk`) et le compilateur (`goalc`) modifiés grâce à la tâche ciblée rapide :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
- **Détails :** Extraction standard suffisante. Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

---|---|
| `common/network/multiplayer_protocol.h` (nouveau) | Format d'échange UDP partagé / struct FFI GOAL |
| `game/system/multiplayer/mp_session.{h,cpp}` (nouveau) | Socket UDP + table des pairs |
| `game/system/multiplayer/mp_goal_bridge.{h,cpp}` (nouveau) | Fonctions FFI exposées à GOAL |
| `common/cross_sockets/XSocket.h/.cpp` | Ajout des primitives UDP (`bind_socket`, `send_to_socket`, `recv_from_socket`) |
| `game/kernel/jak2/kmachine.cpp` | Enregistrement des fonctions FFI `mp-*` |
| `game/CMakeLists.txt` | Ajout des deux nouveaux fichiers `.cpp` à la compilation |
| `goal_src/jak2/pc/multiplayer/mp-h.gc` (nouveau) | Énumérations partagées + structure `mp-player-state` |
| `goal_src/jak2/pc/multiplayer/remote-player.gc` (nouveau) | Processus-relais non-interactif pour les joueurs distants |
| `goal_src/jak2/pc/multiplayer/mp-manager.gc` (nouveau) | Gestionnaire toujours résident : diffusion/sondage/création/destruction, `(mp-toggle-skin!)` |
| `goal_src/jak2/kernel-defs.gc` | Déclarations `define-extern` pour les fonctions `mp-*` |
| `goal_src/jak2/dgos/game.gd` | Enregistrement de `mp-h.o`, `remote-player.o`, `mp-manager.o` |
| `goal_src/jak2/engine/target/logic-target.gc` | Une ligne ajoutée pour faire naître le gestionnaire singleton |

Voir [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)
pour le raisonnement complet, les limitations connues et les non-objectifs.

## 🎥 Encart Vidéo Démonstrative

[![Vidéo de Démonstration](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Les vidéos de démonstration doivent être hébergées sur YouTube pour éviter d'alourdir le dépôt Git. Remplacez `YOUR_VIDEO_ID` par l'identifiant de la vidéo YouTube (ex : `MnqnybexhSA`) et `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` par l'URL de la vidéo (ex : `https://youtu.be/MnqnybexhSA`).*

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/multiplayer_readme.md`](docs/modding/current_mod/multiplayer_readme.md)

---
*(AI-assisted)*
