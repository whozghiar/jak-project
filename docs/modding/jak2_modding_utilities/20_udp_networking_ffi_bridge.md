# Jak 2 — A UDP Networking Bridge for GOAL / Un Pont Réseau UDP pour GOAL

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/multiplayer`
> - **Last Updated / Dernière modification:** `jak2/features/multiplayer`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. The problem this solves

GOAL code cannot open a socket on its own — all I/O has to go through the C++ kernel. This
project already has one networking stack: the DECI2 listener behind `task repl`
(`game/system/Deci2Server.cpp`, `game/kernel/common/kdsnetm.cpp`, `game/kernel/jak2/klisten.cpp`).
It is **not** a good fit for a gameplay feature that needs to send a small state update every
frame: it is TCP, command/response shaped, and tightly coupled to the debugger protocol (framed
messages, an event dispatch table). Bending it to carry "player moved to X" every tick would mean
fighting its framing and blocking-`accept`-loop design.

## 2. The pattern — a minimal, separate FFI bridge

Instead, add a small, self-contained C++ module and expose a handful of plain functions to GOAL
via `make_function_symbol_from_c` — the same mechanism every other PC-port extra already uses
(`game/kernel/jak2/kmachine.cpp`'s `InitMachine_PCPort()`, e.g. `pc-discord-rpc-update`).

Three pieces:

1. **A shared wire-format header** (`common/network/multiplayer_protocol.h` in this mod) — one
   fixed-size, naturally-aligned `struct`, no framing. One UDP packet == one `sizeof(...)` read.
   A `static_assert` on its size catches accidental padding changes at compile time.
2. **A session/socket module** (`game/system/multiplayer/mp_session.{h,cpp}`) — owns the actual
   socket, using new UDP-specific primitives added to `common/cross_sockets/XSocket.h/.cpp`
   (`bind_socket`, `send_to_socket`, `recv_from_socket` — the existing file only had TCP-shaped
   `connect`/`accept`/`read`/`write`). Everything here is non-blocking; a game frame must never
   stall on the network.
3. **A GOAL bridge module** (`game/system/multiplayer/mp_goal_bridge.{h,cpp}`) — the actual
   exposed functions. GOAL pointers arrive as `u32`/`u64` offsets; `game/kernel/common/Ptr.h`'s
   `Ptr<T>(offset).c()` converts one to a real `T*` inside the emulated PS2 memory
   (`g_ee_main_mem`). Marshal by defining a matching `deftype (structure)` on the GOAL side with
   the *exact same field order and size* as the C++ struct (see `discord-info` in
   `goal_src/jak2/pc/pckernel-impl.gc` / `DiscordInfo` in `kmachine_extras.h` for the established
   precedent this follows) and passing it by reference: `(new 'stack 'my-struct)` allocates a
   scratch instance on the GOAL stack, and passing it as a function argument implicitly passes its
   pointer.

## 3. Registering the bridge

- Register the FFI functions in `InitMachine_PCPort()` (`game/kernel/jak2/kmachine.cpp`), next to
  the other `pc-*` extras.
- Forward-declare them for GOAL in `goal_src/jak2/kernel-defs.gc` with `define-extern` (see the
  `mp-init`/`mp-send-local-state`/... block there) — this is the same file every other C-backed
  PC-port function is declared in (`pc-discord-rpc-update`, etc.), and `declare-type` lets you
  reference a `structure` type there before its full `deftype` is compiled elsewhere.
- Add the new `.cpp` files to `game/CMakeLists.txt`'s explicit source list (this project does not
  glob sources) and register the new GOAL `.gc` files' `.o` outputs in the relevant DGO's `.gd`
  file (for an always-resident feature, that's `goal_src/jak2/dgos/game.gd` — **not** `game.gp`,
  which only maps `$ISO`/`$DECOMP` paths and does not enumerate individual source files for this
  project).

## 4. Known pitfalls

- **Struct layout drift.** If the C++ struct and the GOAL `deftype` ever get out of sync (a field
  added to one but not the other, or reordered), the FFI silently reads garbage — there is no
  runtime check. Order fields so every one already falls on its natural alignment boundary (put
  all 4-byte fields first, then 2-byte, then 1-byte, with explicit padding fields for anything
  left over) so the layout does not depend on guessing either compiler's padding rules; verify
  with a `static_assert` on the C++ side.
- **Blocking sockets stall the whole game.** Always set new sockets non-blocking
  (`fcntl`/`O_NONBLOCK` on POSIX, `ioctlsocket`/`FIONBIO` on Windows) — `set_socket_timeout`'s
  `SO_RCVTIMEO` is not the same thing and can still block up to its timeout.
- **A GOAL boolean is not a C `bool`.** Returning `1`/`0` from a bridge function typed `symbol` in
  GOAL will not compare correctly against `#t`/`#f`. Encode it as `s7.offset` (false) or
  `s7.offset + true_symbol_offset(g_game_version)` (true) — see `bool_to_symbol` in
  `game/kernel/jak2/kmachine_extras.cpp`, duplicated locally in `mp_goal_bridge.cpp` since it is a
  one-line helper every such bridge file defines for itself.

## 5. Verification steps

1. Build (`task build-release`) and confirm the new `.cpp` files compile and link.
2. From the REPL (`task repl`), call the exposed function directly, e.g. `(mp-init)`, and confirm
   it returns `#t`/`#f` as expected rather than erroring or hanging.
3. For a struct-marshaling bridge function, build the scratch struct in GOAL, call the function,
   and read back a field you expect to have changed, to confirm the pointer arithmetic lines up on
   both sides.

---

# 🇫🇷 Version Française

## 1. Le problème résolu

Le code GOAL ne peut pas ouvrir de socket seul — toutes les entrées/sorties passent par le noyau
C++. Ce projet dispose déjà d'une pile réseau : le listener DECI2 derrière `task repl`
(`game/system/Deci2Server.cpp`, `game/kernel/common/kdsnetm.cpp`,
`game/kernel/jak2/klisten.cpp`). Elle **ne convient pas** à une fonctionnalité de gameplay qui doit
envoyer une petite mise à jour d'état à chaque frame : c'est un protocole TCP, en
requête/réponse, étroitement couplé au protocole du débogueur (messages encadrés, table de
distribution d'événements). Le détourner pour transporter « joueur déplacé en X » à chaque tick
reviendrait à lutter contre son système de trames et sa boucle `accept` bloquante.

## 2. Le patron — un pont FFI minimal et séparé

À la place, on ajoute un petit module C++ autonome et on expose une poignée de fonctions simples à
GOAL via `make_function_symbol_from_c` — le même mécanisme que tous les autres ajouts PC-port
(`game/kernel/jak2/kmachine.cpp`, fonction `InitMachine_PCPort()`, ex. `pc-discord-rpc-update`).

Trois éléments :

1. **Un en-tête de format d'échange partagé** (`common/network/multiplayer_protocol.h` dans ce
   mod) — une `struct` de taille fixe et naturellement alignée, sans encadrement. Un paquet UDP =
   une lecture `sizeof(...)`. Un `static_assert` sur sa taille détecte tout ajout de padding
   accidentel à la compilation.
2. **Un module de session/socket** (`game/system/multiplayer/mp_session.{h,cpp}`) — possède le
   socket, via de nouvelles primitives UDP ajoutées à `common/cross_sockets/XSocket.h/.cpp`
   (`bind_socket`, `send_to_socket`, `recv_from_socket` — le fichier existant n'avait que des
   fonctions orientées TCP `connect`/`accept`/`read`/`write`). Tout y est non-bloquant ; une frame
   de jeu ne doit jamais attendre le réseau.
3. **Un module de pont GOAL** (`game/system/multiplayer/mp_goal_bridge.{h,cpp}`) — les fonctions
   réellement exposées. Les pointeurs GOAL arrivent comme des offsets `u32`/`u64` ;
   `game/kernel/common/Ptr.h` (`Ptr<T>(offset).c()`) les convertit en vrai `T*` dans la mémoire PS2
   émulée (`g_ee_main_mem`). On effectue le marshaling en définissant côté GOAL un `deftype
   (structure)` avec *exactement le même ordre et la même taille de champs* que la struct C++ (voir
   `discord-info` dans `goal_src/jak2/pc/pckernel-impl.gc` / `DiscordInfo` dans
   `kmachine_extras.h` pour le précédent établi suivi ici), passé par référence : `(new 'stack
   'ma-struct)` alloue une instance temporaire sur la pile GOAL, et la passer en argument de
   fonction transmet implicitement son pointeur.

## 3. Enregistrer le pont

- Enregistrer les fonctions FFI dans `InitMachine_PCPort()`
  (`game/kernel/jak2/kmachine.cpp`), à côté des autres extras `pc-*`.
- Les déclarer côté GOAL avec `define-extern` dans `goal_src/jak2/kernel-defs.gc` (voir le bloc
  `mp-init`/`mp-send-local-state`/... à cet endroit) — c'est le même fichier où sont déclarées
  toutes les autres fonctions PC-port adossées au C (`pc-discord-rpc-update`, etc.), et
  `declare-type` permet d'y référencer un type `structure` avant que son `deftype` complet ne soit
  compilé ailleurs.
- Ajouter les nouveaux fichiers `.cpp` à la liste explicite de sources de `game/CMakeLists.txt`
  (ce projet ne fait pas de glob des sources) et enregistrer les sorties `.o` des nouveaux
  fichiers `.gc` dans le `.gd` du DGO concerné (pour une fonctionnalité toujours résidente, c'est
  `goal_src/jak2/dgos/game.gd` — **pas** `game.gp`, qui ne fait que mapper les chemins
  `$ISO`/`$DECOMP` et n'énumère pas les fichiers source individuels pour ce projet).

## 4. Pièges connus

- **Dérive du layout de la struct.** Si la struct C++ et le `deftype` GOAL se désynchronisent (un
  champ ajouté d'un côté mais pas de l'autre, ou réordonné), le pont FFI lit silencieusement des
  données incohérentes — aucune vérification à l'exécution. Ordonner les champs pour que chacun
  tombe déjà sur sa frontière d'alignement naturelle (tous les champs de 4 octets d'abord, puis 2
  octets, puis 1 octet, avec des champs de padding explicites pour le reste) afin que le layout ne
  dépende pas des règles de padding devinées de l'un ou l'autre compilateur ; vérifier avec un
  `static_assert` côté C++.
- **Un socket bloquant fige tout le jeu.** Toujours rendre les nouveaux sockets non-bloquants
  (`fcntl`/`O_NONBLOCK` sous POSIX, `ioctlsocket`/`FIONBIO` sous Windows) — `SO_RCVTIMEO` via
  `set_socket_timeout` n'est pas équivalent et peut bloquer jusqu'à son délai.
- **Un booléen GOAL n'est pas un `bool` C.** Renvoyer `1`/`0` depuis une fonction de pont typée
  `symbol` côté GOAL ne se comparera pas correctement à `#t`/`#f`. L'encoder comme `s7.offset`
  (faux) ou `s7.offset + true_symbol_offset(g_game_version)` (vrai) — voir `bool_to_symbol` dans
  `game/kernel/jak2/kmachine_extras.cpp`, dupliqué localement dans `mp_goal_bridge.cpp` car c'est
  un utilitaire d'une ligne que chaque fichier de pont redéfinit pour lui-même.

## 5. Étapes de vérification

1. Compiler (`task build-release`) et confirmer que les nouveaux fichiers `.cpp` compilent et sont
   liés correctement.
2. Depuis le REPL (`task repl`), appeler directement la fonction exposée, ex. `(mp-init)`, et
   vérifier qu'elle renvoie `#t`/`#f` comme attendu plutôt que d'échouer ou de bloquer.
3. Pour une fonction de pont avec marshaling de struct, construire la struct temporaire côté GOAL,
   appeler la fonction, puis relire un champ censé avoir changé, afin de confirmer que
   l'arithmétique de pointeurs concorde des deux côtés.
