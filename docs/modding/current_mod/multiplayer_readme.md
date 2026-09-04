# Multiplayer — Technical Notes / Notes Techniques (AI-assisted)

Branch: `jak2/features/multiplayer`

## 🇬🇧 English

### Architecture

Each player runs a separate `gk.exe` instance. Instances exchange UDP state snapshots directly
with each other (full mesh, no server) over a fixed, environment-configured peer list. See
[`docs/modding/jak2_modding_utilities/20_udp_networking_ffi_bridge.md`](../jak2_modding_utilities/20_udp_networking_ffi_bridge.md)
for the networking bridge design.

- **v1 scope is presence-only**: remote players are visible (position, orientation, coarse
  animation, chosen skin) but not interactive. No combat/damage/item/enemy/level-state
  synchronization. Each instance fully simulates its own game independently.
- **Character selection** is a live re-skin of the existing `target` process (same physics/
  control/collision), not a second moveset - see
  [`docs/modding/jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md`](../jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md).
- **Remote players** are rendered by a lightweight, non-interactive stub process - see
  [`docs/modding/jak2_modding_utilities/22_minimal_networked_stub_process_pattern.md`](../jak2_modding_utilities/22_minimal_networked_stub_process_pattern.md).

### Files changed / added

**New:**
- `common/network/multiplayer_protocol.h` - shared UDP wire format / GOAL-FFI marshaling struct.
- `game/system/multiplayer/mp_session.{h,cpp}` - UDP socket, peer table, send/recv.
- `game/system/multiplayer/mp_goal_bridge.{h,cpp}` - FFI functions exposed to GOAL.
- `goal_src/jak2/pc/multiplayer/mp-h.gc` - shared enums (`mp-anim-state`, `mp-skin-id`) and the
  `mp-player-state` structure mirroring the C++ wire struct.
- `goal_src/jak2/pc/multiplayer/remote-player.gc` - the non-interactive remote-player stub.
- `goal_src/jak2/pc/multiplayer/mp-manager.gc` - the always-resident manager: samples/broadcasts
  the local player each frame, polls incoming state, spawns/despawns/updates `remote-player`
  stubs, and exposes `(mp-toggle-skin!)`.

**Existing files, small additive touches:**
- `common/cross_sockets/XSocket.h/.cpp` - added `bind_socket`/`send_to_socket`/`recv_from_socket`
  (UDP primitives; the file previously only had TCP-shaped functions for the DECI2/REPL listener).
- `game/kernel/jak2/kmachine.cpp` - registered the 5 `mp-*` FFI functions in `InitMachine_PCPort()`.
- `game/CMakeLists.txt` - added the two new `.cpp` files to the (explicit, non-globbed) source list.
- `goal_src/jak2/kernel-defs.gc` - `define-extern` forward declarations for the `mp-*` FFI
  functions and for `mp-manager-start` (GOAL-to-GOAL forward reference, needed because
  `logic-target.gc` compiles before `mp-manager.gc` in `game.gd`'s load order).
- `goal_src/jak2/dgos/game.gd` - registered `mp-h.o`, `remote-player.o`, `mp-manager.o` (in that
  dependency order) in the always-resident `GAME` DGO, next to `logic-target.o`.
- `goal_src/jak2/engine/target/logic-target.gc` - one added line in `start`, calling
  `(mp-manager-start)` (idempotent - see that function's docstring for why it's safe to call on
  every target respawn rather than a single dedicated boot hook).

### Configuration (environment variables, read once at boot)

| Variable | Meaning | Example |
|---|---|---|
| `MP_PEERS` | Comma-separated `ip:port` list of every other instance | `127.0.0.1:8115` |
| `MP_LOCAL_PLAYER_ID` | This instance's id, `0`-`3` | `0` |
| `MP_LOCAL_PORT` | UDP port this instance listens on | `8114` |

If `MP_PEERS` is unset or empty, multiplayer is simply inactive - solo play is unaffected.

### Character selection

Call `(mp-toggle-skin!)` from the REPL to flip between Jak and the Krimzon Guard skin for the
local player; it re-skins `*target*` immediately and is broadcast to peers on the next tick. A
real pause-menu entry was planned but turned out to need a new localized `text-id` string, and
this project has no mechanism (equivalent to `custom_assets/jak2/texture_replacements/` for
textures) for injecting new UI text without the retail text-bank asset pipeline - see the
"Known limitations" section below.

### Known limitations / follow-ups

- **No pause-menu skin toggle yet** (REPL command only) - see above.
- **Joint-layout mismatch when playing as the guard is unverified.** `target`'s per-frame
  joint-mods (head look-at, IK, ...) are indexed for `skel-jchar`'s layout; whether
  `skel-crimson-guard-level`'s layout is compatible enough for them to keep working correctly has
  not been confirmed in-game. See
  [`21_live_reskinning_a_process_with_initialize-skeleton.md`](../jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md#3-the-real-risk-joint-layout-mismatch)
  for the mitigation path if this causes visible glitches.
- Coarse anim-state mapping (`goal_src/jak2/pc/multiplayer/mp-manager.gc`,
  `target-state->mp-anim-state`) only distinguishes idle/walk/run/jump/fall/duck; every other
  `target` state (combat, vehicles, grabs, ...) falls back to idle on remote stubs, by design (see
  non-goals below).
- No broadcast/mDNS discovery - peers must be configured manually via `MP_PEERS`.
- 4-player cap (`MP-MAX-PLAYERS` / `mp_net::MP_MAX_PLAYERS`).

### Non-goals (v1)

No combat/damage/item/enemy/level-state sync · no internet/NAT traversal · no anti-cheat/
encryption (trusted LAN only) · no client-side prediction beyond simple lerp/slerp · no new 3D art.

---

## 🇫🇷 Français

### Architecture

Chaque joueur lance sa propre instance `gk.exe`. Les instances échangent directement des
instantanés d'état UDP entre elles (maillage complet, sans serveur) via une liste de pairs fixe,
configurée par variables d'environnement. Voir
[`docs/modding/jak2_modding_utilities/20_udp_networking_ffi_bridge.md`](../jak2_modding_utilities/20_udp_networking_ffi_bridge.md)
pour la conception du pont réseau.

- **La portée v1 est uniquement la présence** : les joueurs distants sont visibles (position,
  orientation, animation grossière, skin choisi) mais non interactifs. Aucune synchronisation de
  combat/dégâts/objets/ennemis/état de niveau. Chaque instance simule entièrement son propre jeu
  de façon indépendante.
- **La sélection de personnage** est un reskin à chaud du processus `target` existant (même
  physique/contrôle/collision), pas un second moveset - voir
  [`docs/modding/jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md`](../jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md).
- **Les joueurs distants** sont rendus par un processus-relais léger et non-interactif - voir
  [`docs/modding/jak2_modding_utilities/22_minimal_networked_stub_process_pattern.md`](../jak2_modding_utilities/22_minimal_networked_stub_process_pattern.md).

### Fichiers modifiés / ajoutés

**Nouveaux :**
- `common/network/multiplayer_protocol.h` - format d'échange UDP partagé / struct de marshaling FFI GOAL.
- `game/system/multiplayer/mp_session.{h,cpp}` - socket UDP, table des pairs, envoi/réception.
- `game/system/multiplayer/mp_goal_bridge.{h,cpp}` - fonctions FFI exposées à GOAL.
- `goal_src/jak2/pc/multiplayer/mp-h.gc` - énumérations partagées (`mp-anim-state`, `mp-skin-id`)
  et la structure `mp-player-state` reflétant la struct C++.
- `goal_src/jak2/pc/multiplayer/remote-player.gc` - le processus-relais non-interactif.
- `goal_src/jak2/pc/multiplayer/mp-manager.gc` - le gestionnaire toujours résident : échantillonne
  et diffuse le joueur local à chaque frame, sonde l'état entrant, crée/détruit/met à jour les
  relais `remote-player`, et expose `(mp-toggle-skin!)`.

**Fichiers existants, ajouts chirurgicaux :**
- `common/cross_sockets/XSocket.h/.cpp` - ajout de `bind_socket`/`send_to_socket`/
  `recv_from_socket` (primitives UDP ; le fichier n'avait auparavant que des fonctions orientées
  TCP pour le listener DECI2/REPL).
- `game/kernel/jak2/kmachine.cpp` - enregistrement des 5 fonctions FFI `mp-*` dans
  `InitMachine_PCPort()`.
- `game/CMakeLists.txt` - ajout des deux nouveaux fichiers `.cpp` à la liste de sources explicite
  (non générée par glob).
- `goal_src/jak2/kernel-defs.gc` - déclarations `define-extern` pour les fonctions FFI `mp-*` et
  pour `mp-manager-start` (référence anticipée GOAL-vers-GOAL, nécessaire car `logic-target.gc` se
  compile avant `mp-manager.gc` dans l'ordre de chargement de `game.gd`).
- `goal_src/jak2/dgos/game.gd` - enregistrement de `mp-h.o`, `remote-player.o`, `mp-manager.o`
  (dans cet ordre de dépendance) dans le DGO toujours résident `GAME`, à côté de `logic-target.o`.
- `goal_src/jak2/engine/target/logic-target.gc` - une ligne ajoutée dans `start`, appelant
  `(mp-manager-start)` (idempotente - voir le docstring de cette fonction pour comprendre pourquoi
  il est sûr de l'appeler à chaque respawn du joueur plutôt que via un point d'entrée dédié au
  démarrage).

### Configuration (variables d'environnement, lues une fois au démarrage)

| Variable | Signification | Exemple |
|---|---|---|
| `MP_PEERS` | Liste `ip:port` séparée par des virgules de chaque autre instance | `127.0.0.1:8115` |
| `MP_LOCAL_PLAYER_ID` | Identifiant de cette instance, `0`-`3` | `0` |
| `MP_LOCAL_PORT` | Port UDP écouté par cette instance | `8114` |

Si `MP_PEERS` n'est pas défini ou est vide, le multijoueur est simplement inactif - le jeu solo
n'est pas affecté.

### Sélection de personnage

Appeler `(mp-toggle-skin!)` depuis le REPL pour basculer entre Jak et le skin du garde Krimzon
pour le joueur local ; le reskin de `*target*` est immédiat et diffusé aux pairs au tick suivant.
Une véritable entrée de menu pause était prévue, mais nécessiterait un nouveau `text-id` localisé,
et ce projet ne dispose d'aucun mécanisme (équivalent à
`custom_assets/jak2/texture_replacements/` pour les textures) permettant d'injecter du nouveau
texte d'interface sans passer par le pipeline d'assets des banques de texte du jeu original - voir
la section « Limitations connues » ci-dessous.

### Limitations connues / suites possibles

- **Pas encore de bascule de skin dans le menu pause** (commande REPL uniquement) - voir ci-dessus.
- **La compatibilité des joints en jouant en garde n'est pas vérifiée.** Les joint-mods par frame
  de `target` (look-at de la tête, IK, ...) sont indexés pour la disposition de `skel-jchar` ; la
  compatibilité de la disposition de `skel-crimson-guard-level` avec ces indices n'a pas été
  confirmée en jeu. Voir
  [`21_live_reskinning_a_process_with_initialize-skeleton.md`](../jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md#3-le-vrai-risque--incompatibilité-de-la-disposition-des-joints)
  pour la piste de mitigation en cas de problème visuel.
- Le mapping grossier d'état d'animation (`goal_src/jak2/pc/multiplayer/mp-manager.gc`,
  `target-state->mp-anim-state`) ne distingue que idle/walk/run/jump/fall/duck ; tout autre état
  de `target` (combat, véhicules, prises, ...) retombe sur idle chez les relais distants, par
  conception (voir non-objectifs ci-dessous).
- Pas de découverte broadcast/mDNS - les pairs doivent être configurés manuellement via `MP_PEERS`.
- Plafond de 4 joueurs (`MP-MAX-PLAYERS` / `mp_net::MP_MAX_PLAYERS`).

### Non-objectifs (v1)

Aucune synchronisation combat/dégâts/objets/ennemis/état de niveau · pas de jeu par
Internet/traversée NAT · pas d'anti-triche/chiffrement (LAN de confiance uniquement) · pas de
prédiction côté client au-delà d'une simple interpolation lerp/slerp · pas de nouvel art 3D.
