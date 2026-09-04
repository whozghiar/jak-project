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
- **Status:** Required (`task build-release`)
- **Details:** This mod adds new C++ source files (`game/system/multiplayer/`, plus additions to
  `common/cross_sockets/XSocket.*` and `game/kernel/jak2/kmachine.cpp`) - the runtime binary must
  be rebuilt.
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient
- **Details:** No new/custom 3D models, textures, or sound banks - character selection reuses
  Jak's and the Krimzon Guard's existing in-game art.
```bash
task extract
```

### 4. Configure and launch each instance
Before `task boot-game`, set these environment variables per instance (values below are an example
for two players on the same machine over loopback):

```bash
# Instance A (player 0)
export MP_PEERS=127.0.0.1:8115
export MP_LOCAL_PLAYER_ID=0
export MP_LOCAL_PORT=8114

# Instance B (player 1), in its own terminal/environment
export MP_PEERS=127.0.0.1:8114
export MP_LOCAL_PLAYER_ID=1
export MP_LOCAL_PORT=8115
```

Then, per instance:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*
If `MP_PEERS` is left unset, the mod is simply inactive and the game plays as normal solo.

## 🎮 Usage & Controls
- **Character selection:** from the OpenGOAL REPL (`task repl`), run `(mp-toggle-skin!)` to flip
  the local player between Jak and the Krimzon Guard skin. This applies immediately and is
  broadcast to every connected peer on the next tick. (A pause-menu toggle was planned but needs a
  new localized UI string this project has no pipeline for yet - see the technical notes linked
  above.)
- **Remote players are visual-only in v1:** you will see other connected players moving around
  your world with their chosen skin, but cannot collide with, damage, or otherwise interact with
  them, and their presence has no effect on your own game's enemies/items/progress.
- **Up to 4 simultaneous instances.**

## 📝 Changes Log
| File(s) | Why |
|---|---|
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
- **Statut :** Requise (`task build-release`)
- **Détails :** Ce mod ajoute de nouveaux fichiers source C++ (`game/system/multiplayer/`, ainsi
  que des ajouts à `common/cross_sockets/XSocket.*` et `game/kernel/jak2/kmachine.cpp`) - le
  binaire du moteur doit être recompilé.
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante
- **Détails :** Aucun nouveau modèle 3D, texture ou son personnalisé - la sélection de personnage
  réutilise l'art existant de Jak et du garde Krimzon.
```bash
task extract
```

### 4. Configurer et lancer chaque instance
Avant `task boot-game`, définissez ces variables d'environnement pour chaque instance (exemple
ci-dessous pour deux joueurs sur la même machine via loopback) :

```bash
# Instance A (joueur 0)
export MP_PEERS=127.0.0.1:8115
export MP_LOCAL_PLAYER_ID=0
export MP_LOCAL_PORT=8114

# Instance B (joueur 1), dans son propre terminal/environnement
export MP_PEERS=127.0.0.1:8114
export MP_LOCAL_PLAYER_ID=1
export MP_LOCAL_PORT=8115
```

Puis, pour chaque instance :
```bash
task boot-game
```
*(Ou via le REPL OpenGOAL avec `task repl`, puis `(mi)` et `(r)`).*
Si `MP_PEERS` n'est pas défini, le mod est simplement inactif et le jeu se joue normalement en solo.

## 🎮 Utilisation & Commandes
- **Sélection de personnage :** depuis le REPL OpenGOAL (`task repl`), exécutez
  `(mp-toggle-skin!)` pour basculer le joueur local entre Jak et le skin du garde Krimzon.
  L'effet est immédiat et diffusé à chaque pair connecté au tick suivant. (Une bascule dans le
  menu pause était prévue mais nécessite une nouvelle chaîne d'interface localisée, pour laquelle
  ce projet n'a pas encore de pipeline - voir les notes techniques ci-dessus.)
- **Les joueurs distants sont uniquement visuels en v1 :** vous verrez les autres joueurs connectés
  se déplacer dans votre monde avec leur skin choisi, mais sans pouvoir entrer en collision, leur
  infliger des dégâts, ni interagir avec eux d'aucune façon ; leur présence n'a aucun effet sur les
  ennemis/objets/progression de votre propre partie.
- **Jusqu'à 4 instances simultanées.**

## 📝 Journal des Modifications
| Fichier(s) | Pourquoi |
|---|---|
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
