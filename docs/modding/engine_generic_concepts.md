# Engine Generic Concepts — Jak 1 / Jak 2 / Jak 3 / Concepts Moteur Génériques

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 / Jak 2 / Jak 3 (OpenGOAL PC Port) — all games
> - **Source of Truth / Source de Vérité :** `master-dev`
> - **Scope / Portée :** Memory Heaps, PS2 Memory Simulation, DGOs, Level Streaming & Process Lifecycle

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Simulated PS2 Memory](#1-the-simulated-ps2-memory-block) · [2. The Three Heaps](#2-the-three-heaps) · [3. Memory Constants](#3-memory-constants-where-they-live) · [4. valid? & Memory Expansion](#4-valid-bad-address-and-the-memory-expansion-recipe) · [5. DGOs & Streaming](#5-dgos-and-level-streaming) · [6. Virtual Methods & vtable Trap](#6-virtual-method--state-residency-the-vtable-trap) · [7. Process Lifecycle](#7-process-life-cycle) · [8. Boot Diagnostics Loop](#8-boot-diagnostics--the-compilevalidate-loop) · [9. Architecture Discoveries](#9-extensible-section-future-architecture-discoveries) · [10. How to Contribute](#10-how-to-contribute)
> - 🇫🇷 **Français :** [1. Bloc Mémoire PS2 Simulé](#1-le-bloc-mémoire-ps2-simulé) · [2. Les Trois Heaps](#2-les-trois-tas-heaps) · [3. Constantes Mémoire](#3-constantes-mémoire--où-elles-vivent) · [4. valid? & Extension Mémoire](#4-valid-bad-address-et-la-recette-dextension-mémoire) · [5. DGO & Streaming](#5-dgo-et-streaming-des-niveaux) · [6. Méthodes Virtuelles & Piège vtable](#6-résidence-des-méthodes-et-états-virtuels-le-piège-de-la-vtable) · [7. Cycle de Vie des Processus](#7-cycle-de-vie-dun-processus) · [8. Diagnostic & Validation](#8-diagnostic-au-démarrage--boucle-compilervalider) · [9. Découvertes d'Architecture](#9-section-extensible--découvertes-darchitecture-futures) · [10. Comment Contribuer](#10-comment-contribuer)

---

# 🇬🇧 English Version

## What this file is
The shared, plain-language primer on how the OpenGOAL engine works *below* the Lisp syntax: memory, heaps, level streaming, process life cycle, boot diagnostics. It is **common to all three games**. Read it once before your first mod; come back to it whenever a crash mentions memory or an object "not found".

## Contract
Only verified facts belong here. If you discover a new architectural fact while modding, **do not add it on your mod branch** — record it on `master-dev` (see [How to contribute](#10-how-to-contribute)) so parallel mods never conflict on this file.

---

## 1. The simulated PS2 memory block

The original games ran on the PS2's "Emotion Engine" (EE) CPU with a fixed block of RAM. The PC port keeps that model: at start-up the C++ runtime (`gk`) reserves **one big contiguous virtual memory block** with `mmap` and lets the GOAL code allocate inside it at fixed offsets — exactly as the PS2 kernel did. Nothing in GOAL uses the operating system's `malloc` directly; everything lives inside this one block.

```text
game/runtime.cpp ── mmap( EE_MAIN_MEM_SIZE ) ──► ┌──────────────────────────────┐
                                                  │ simulated PS2 RAM (1 block)  │
                                                  └──────────────────────────────┘
```

- **Why you care:** a mod that allocates too much, or writes past a heap, does not corrupt your PC — it corrupts *this* block and the game crashes with a memory error. The size of the block is `EE_MAIN_MEM_SIZE` (see §3).

---

## 2. The three heaps

A "heap" is just a labelled region *inside* the big block where GOAL allocates objects. There are three you will meet:

| Heap | Holds | Lifetime |
|---|---|---|
| **global heap** | types, the symbol table, kernel code, always-resident processes, `*target*` | whole session |
| **level heap** | everything a level needs: its geometry, textures, actors, art | freed when the level unloads |
| **debug heap** | debug menu, REPL helpers, profiling tools | whole session, but **only in `-debug` builds** |

When you write `(object-new 'global ...)`, `(object-new 'process ...)` or `(object-new 'debug ...)`, the first argument picks which heap. Debug-only code (a debug menu entry, a diagnostic) must allocate on `'debug` so it disappears cleanly from release builds.

```lisp
;; allocate a short-lived actor on the process/level heap (normal case)
(process-spawn my-actor :to *entity-pool*)

;; allocate menu/diagnostic data on the debug heap so release builds drop it
(new 'debug 'debug-menu *debug-menu-context* "My menu")
```

- **Rule of thumb:** never allocate gameplay objects on `'global` "to be safe" — the global heap is small and never frees. Use the level/process heap and let it reclaim your object when the level unloads.

---

## 3. Memory constants: where they live

Some memory limits are set in **shared C++** (one value for *all four* games — Jak 1, 2, 3 and Jak X). Others are set **per game in GOAL**. Changing a shared C++ constant for one mod silently changes it for every game.

| Constant | File | Scope |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | shared (all games) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | shared |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | shared |
| `END_OF_MEMORY` (used by `valid?`) | `goal_src/<game>/kernel/gcommon.gc` | per game |
| `DEBUG_LEVEL_HEAP_MULT` (level-heap size multiplier) | `goal_src/<game>/engine/level/level.gc` | per game |

- A modder who only edits GOAL never touches the first three. The two GOAL constants are the ones you tune for a "more memory" mod (see §4).

---

## 4. `valid?`, "bad address", and the memory-expansion recipe

`valid?` (in `gcommon.gc`) is the engine's pointer sanity check: it rejects any address `>= END_OF_MEMORY`. The PS2 limit was 128 MB (`#x8000000`). The PC port can reserve much more, but if `END_OF_MEMORY` is left at the PS2 value while the block is bigger, every object allocated above 128 MB fails with `bad address` / `not a valid object`.

**Verified recipe (Jak 2, 512 MB):**

```lisp
;; goal_src/jak2/kernel/gcommon.gc
;; raise the ceiling used by valid? to 512 MB
(defconstant END_OF_MEMORY #x20000000)

;; goal_src/jak2/engine/level/level.gc
;; level-heap size = multiplier x base. 15.0 (Jak 3's value) over-allocates on
;; Jak 2 (it loads ~35 MB resident first) and panics at boot. 12.0 is the tested
;; safe value: ~215 MB level heap, ~60 MB spare — a 10x increase over the PS2.
(defconstant DEBUG_LEVEL_HEAP_MULT 12.0)
```

- **Always validate at runtime.** A memory change that compiles can still panic at boot. Follow §8's loop and check the log.

### Where each game stands on `master-dev`:

| Metric | Jak 1 | Jak 2 | Jak 3 |
|---|---|---|---|
| `EE_MAIN_MEM_SIZE` (shared) | 512 MB | 512 MB | 512 MB |
| `GLOBAL_HEAP_END` (shared) | `0x12D00000` (~300 MB) | idem | idem |
| `END_OF_MEMORY` | `#x20000000` | `#x20000000` | `#x20000000` |
| level-heap tuning | `LEVEL_HEAP_SIZE_DEBUG`, still stock | `DEBUG_LEVEL_HEAP_MULT 12.0` | `DEBUG_LEVEL_HEAP_MULT 15.0` |
| debug heap | `jak1::DEBUG_HEAP_SIZE` | `jak2::DEBUG_HEAP_SIZE` | `jak3::DEBUG_HEAP_SIZE` |

- **Jak 3 is already at the ceiling** — 15.0 is the highest tested multiplier of the three.
- **Jak 1 has a different level-heap architecture**: no page/multiplier scheme, just `LEVEL_HEAP_SIZE_DEBUG` allocated from global heap.
- **Trap worth knowing:** raising the *shared* `DEBUG_HEAP_START` broke Jak 1 outright because its `InitMachine` computed the debug heap end from a 128 MB address mask. Always boot all three games with `-debug` when touching shared constants.

---

## 5. DGOs and level streaming

Compiled GOAL code and data are packed into **DGO** files ("Data Group Object"). A DGO is loaded as one unit:
- **Resident DGOs** (e.g. `KERNEL`, `GAME`, `ENGINE`, city hub DGOs) — loaded once at boot and never freed. Code here is *always available*.
- **Level DGOs** — streamed in when entering a level/area and freed when leaving. Code and assets here exist *only while that level is loaded*.

Which `.o` files go into which DGO is declared in the game's `.gd` files (`goal_src/<game>/dgos/*.gd`). New `.gc` source files are also registered in the project file `.gp` (`goal_src/<game>/<game>.gp`).

- **Why you care:** if your code is spawned by an always-running system (traffic, global manager) but *defined* in a level DGO, it will be missing or dangling the moment that level is not loaded.

---

## 6. Virtual method / state residency (the vtable trap)

In GOAL, `defmethod` and `(defstate ... :virtual #t)` fill a slot in the type's **virtual table (vtable)**. That slot is filled **when the object file is linked into memory**, i.e. when its DGO loads — not at compile time.
- Override compiled in a **resident** DGO → slot always filled → works.
- Override compiled in a **level** DGO that is *not loaded* → slot empty → call silently falls back or does nothing.
- Override in a level DGO that was loaded then unloaded → slot **dangling** → crash or undefined behavior.

**Rule:** if a type is instantiated by an always-resident system, define **all** its `:virtual #t` states and virtual methods in an always-resident file.

```lisp
;; BAD — custom traffic actor's active state defined in a mission-only file.
;; GOOD — define it in the resident vehicle/enemy file (e.g. vehicle.gc, car.gc).
(defstate active (my-traffic-actor)
  :virtual #t
  :code (behavior () (loop (ja :num! (seek!)) (suspend))))
```

---

## 7. Process life cycle

Almost every live thing in the game is a **process** (a lightweight cooperative "thread" with its own small stack and heap). A `process-drawable` is a process that also has a 3D model:
1. **spawn** — `process-spawn` allocates the process on a pool's heap and runs its `init` code.
2. **run** — each frame the engine resumes the process's current state; `:code` runs until `(suspend)`. `:post` runs every frame after `:code`.
3. **transition** — `(go some-state)` / `(go-virtual some-state)` switches state.
4. **death** — the process is deactivated; its heap is reclaimed. Children die with their parent.

---

## 8. Boot diagnostics & the compile/validate loop

A GOAL-only change needs **no C++ build**. The loop is:

```bash
# 1. Pick the game once
task set-game-jak2

# 2. Open compiler REPL
task repl
# Inside REPL: (mi)

# 3. Boot and check log
task boot-game
```

```bash
# Scan newest log for memory or object errors:
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

---

## 9. ➕ Extensible section: future architecture discoveries

### 9.1 Overlord sound bank architecture & SPU slot allocation
- **Sound Subsystem (Overlord):** `.SBK` banks are loaded into PS2 SPU RAM by Overlord. Jak 2 & 3 provide fixed dedicated slots for resident banks (`common`, `gun`, `board`) + a 3-slot rotating pool shared dynamically by active level banks.
- **Route A — Append to COMMON (Recommended for global SFX):** `(append-sbk "COMMON" "custom_assets/jak2/sounds/sfx/MY_SFX")` merges sounds directly into resident `COMMON.SBK` with zero runtime management.
- **Route B — Standalone Bank (`build-sbk`):** Places bank into the 3-slot rotating level pool when loaded via `(sound-bank-load ...)`.
- **Looping Sounds:** Allocate sound ID once in the actor's `-init` state via `(new-sound-id)`.

### 9.2 Skeletal Art-Group linking & Master Art-Groups
- In OpenGOAL, custom art-groups grafted onto existing characters require registration: `(register-custom-art-group "<name>")`.
- Links custom art-groups into `*custom-art-groups-to-link*` at level load, preventing missing slot errors.

---

## 10. How to contribute

To keep parallel mod branches conflict-free, this file has **one source of truth: `master-dev`**.
1. Use `task modding-land-doc -- --file docs/modding/engine_generic_concepts.md --message "..." --push`.
2. On your branch: `task modding-sync-docs` to pull the updated file in.
Never edit this file directly on a mod branch.

---

# 🇫🇷 Version Française

## Rôle de ce fichier
L'introduction commune, en langage simple, au fonctionnement du moteur OpenGOAL *en dessous* de la syntaxe Lisp : mémoire, tas (heaps), streaming de niveaux, cycle de vie des processus, diagnostic au démarrage. Ce fichier est **commun aux trois jeux**. À lire une fois avant votre premier mod ; à relire dès qu'un crash parle de mémoire ou d'un objet « introuvable ».

## Contrat
Seuls des faits vérifiés figurent ici. Si vous découvrez un nouveau fait d'architecture en moddant, **ne l'ajoutez pas sur votre branche de mod** — consignez-le sur `master-dev` (voir [Comment contribuer](#10-comment-contribuer)) pour que les mods développés en parallèle n'entrent jamais en conflit sur ce fichier.

---

## 1. Le bloc mémoire PS2 simulé

Les jeux d'origine tournaient sur le processeur « Emotion Engine » (EE) de la PS2 avec une quantité de RAM fixe. Le port PC conserve ce modèle : au démarrage, le runtime C++ (`gk`) réserve **un seul grand bloc de mémoire virtuelle contiguë** via `mmap`, et le code GOAL alloue à l'intérieur à des offsets fixes — exactement comme le faisait le noyau PS2. Rien en GOAL n'utilise le `malloc` du système d'exploitation ; tout vit dans ce bloc unique.

```text
game/runtime.cpp ── mmap( EE_MAIN_MEM_SIZE ) ──► ┌──────────────────────────────┐
                                                  │ RAM PS2 simulée (1 bloc)     │
                                                  └──────────────────────────────┘
```

- **Pourquoi c'est important :** un mod qui alloue trop, ou qui écrit au-delà d'un heap, ne corrompt pas votre PC — il corrompt *ce* bloc et le jeu plante avec une erreur mémoire. La taille du bloc est `EE_MAIN_MEM_SIZE` (voir §3).

---

## 2. Les trois tas (heaps)

Un « heap » (tas) est simplement une région étiquetée *à l'intérieur* du grand bloc, où GOAL alloue ses objets. Vous en rencontrerez trois :

| Heap | Contient | Durée de vie |
|---|---|---|
| **global heap** | les types, la table des symboles, le code kernel, les process toujours résidents, `*target*` | toute la session |
| **level heap** | tout ce qu'un niveau nécessite : géométrie, textures, acteurs, art | libéré au déchargement du niveau |
| **debug heap** | menu debug, aides REPL, outils de profilage | toute la session, mais **uniquement en build `-debug`** |

Quand vous écrivez `(object-new 'global ...)`, `(object-new 'process ...)` ou `(object-new 'debug ...)`, le premier argument choisit le heap. Le code réservé au debug (une entrée de menu debug, un diagnostic) doit allouer sur `'debug'` pour disparaître proprement des builds release.

```lisp
;; allouer un acteur à courte durée de vie sur le heap process/niveau (cas normal)
(process-spawn my-actor :to *entity-pool*)

;; allouer des données de menu/diagnostic sur le debug heap pour que le release les retire
(new 'debug 'debug-menu *debug-menu-context* "My menu")
```

- **Règle simple :** ne jamais allouer d'objets de gameplay sur `'global` « par sécurité » — le global heap est petit et ne libère jamais. Utilisez le heap niveau/process et laissez-le récupérer votre objet au déchargement du niveau.

---

## 3. Constantes mémoire : où elles vivent

Certaines limites mémoire sont définies en **C++ partagé** (une seule valeur pour *les quatre* jeux — Jak 1, 2, 3 et Jak X). D'autres sont définies **par jeu en GOAL**. Modifier une constante C++ partagée pour un mod la modifie silencieusement pour tous les jeux.

| Constante | Fichier | Portée |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | partagée (tous les jeux) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | partagée |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | partagée |
| `END_OF_MEMORY` (utilisé par `valid?`) | `goal_src/<jeu>/kernel/gcommon.gc` | par jeu |
| `DEBUG_LEVEL_HEAP_MULT` (multiplicateur du level-heap) | `goal_src/<jeu>/engine/level/level.gc` | par jeu |

- Un moddeur qui n'édite que du GOAL ne touche jamais aux trois premières. Les deux constantes GOAL sont celles que l'on ajuste pour un mod « plus de mémoire » (voir §4).

---

## 4. `valid?`, « bad address » et la recette d'extension mémoire

`valid?` (dans `gcommon.gc`) est le contrôle de cohérence des pointeurs du moteur : il rejette toute adresse `>= END_OF_MEMORY`. La limite PS2 était de 128 Mo (`#x8000000`). Le port PC peut réserver bien plus, mais si `END_OF_MEMORY` reste à la valeur PS2 alors que le bloc est plus grand, tout objet alloué au-delà de 128 Mo échoue avec `bad address` / `not a valid object`.

**Recette vérifiée (Jak 2, 512 Mo) :**

```lisp
;; goal_src/jak2/kernel/gcommon.gc
;; relever le plafond utilisé par valid? à 512 Mo
(defconstant END_OF_MEMORY #x20000000)

;; goal_src/jak2/engine/level/level.gc
;; taille du level-heap = multiplicateur x base. 12.0 est la valeur sûre testée :
;; ~215 Mo de level heap, ~60 Mo de marge — soit 10x l'original PS2.
(defconstant DEBUG_LEVEL_HEAP_MULT 12.0)
```

- **Toujours valider à l'exécution.** Un changement mémoire qui compile peut quand même paniquer au démarrage. Suivez la boucle du §8 et vérifiez le journal (log).

### État de chaque jeu sur `master-dev` :

| Métrique | Jak 1 | Jak 2 | Jak 3 |
|---|---|---|---|
| `EE_MAIN_MEM_SIZE` (partagé) | 512 Mo | 512 Mo | 512 Mo |
| `GLOBAL_HEAP_END` (partagé) | `0x12D00000` (~300 Mo) | idem | idem |
| `END_OF_MEMORY` | `#x20000000` | `#x20000000` | `#x20000000` |
| Réglage level-heap | `LEVEL_HEAP_SIZE_DEBUG`, d'origine | `DEBUG_LEVEL_HEAP_MULT 12.0` | `DEBUG_LEVEL_HEAP_MULT 15.0` |
| debug heap | `jak1::DEBUG_HEAP_SIZE` | `jak2::DEBUG_HEAP_SIZE` | `jak3::DEBUG_HEAP_SIZE` |

- **Jak 3 est déjà au plafond** — 15.0 est le multiplicateur le plus élevé testé des trois.
- **Jak 1 a une architecture de level-heap différente** : pas de schéma multiplicateur, allocation directe depuis le tas global.
- **Piège à connaître :** modifier une constante partagée impacte tous les jeux. Démarrez toujours les trois jeux avec `-debug` lors d'un ajustement de constante partagée C++.

---

## 5. DGO et streaming des niveaux

Le code et les données GOAL compilés sont empaquetés dans des fichiers **DGO** (« Data Group Object »). Un DGO est chargé d'un bloc :
- **DGO résidents** (ex. `KERNEL`, `GAME`, `ENGINE`, hub urbain) — chargés une fois au démarrage et jamais libérés. Le code ici est *toujours disponible*.
- **DGO de niveau** — streamés à l'entrée d'un niveau/zone et libérés à la sortie. Le code et les assets ici n'existent *que tant que ce niveau est chargé*.

L'affectation des fichiers `.o` dans chaque DGO est déclarée dans les fichiers `.gd` (`goal_src/<jeu>/dgos/*.gd`).

- **Pourquoi c'est important :** si votre code est instancié par un système toujours actif (trafic, gestionnaire global) mais *défini* dans un DGO de niveau, il sera absent ou pendant dès que ce niveau n'est pas chargé.

---

## 6. Résidence des méthodes et états virtuels (le piège de la vtable)

En GOAL, `defmethod` et `(defstate ... :virtual #t)` remplissent une case dans la **table virtuelle (vtable)** du type. Cette case est remplie **quand le fichier objet est lié en mémoire**, c.-à-d. au chargement de son DGO — pas à la compilation.
- Surcharge compilée dans un DGO **résident** → case toujours remplie → fonctionne.
- Surcharge compilée dans un DGO **de niveau** *non chargé* → case vide → l'appel ne fait rien silencieusement.
- Surcharge dans un DGO de niveau *déchargé* → case **pendante** → crash.

**Règle :** si un type est instancié par un système toujours résident, définissez **toutes** ses surcharges d'états `:virtual #t` et de méthodes virtuelles dans un fichier toujours résident.

---

## 7. Cycle de vie d'un processus

Presque tout ce qui est vivant dans le jeu est un **processus** (un thread coopératif léger avec sa propre pile et son heap) :
1. **Création (spawn)** — `process-spawn` alloue le processus sur le heap d'un pool et exécute son code d'`init`.
2. **Exécution (run)** — chaque frame, le moteur reprend l'état courant ; `:code` s'exécute jusqu'à `(suspend)`. `:post` s'exécute chaque frame après `:code`.
3. **Transition** — `(go un-etat)` / `(go-virtual un-etat)` change d'état.
4. **Mort** — le processus est désactivé ; son heap est libéré. Les enfants meurent avec leur parent.

---

## 8. Diagnostic au démarrage & boucle compiler/valider

Un changement GOAL uniquement ne nécessite **aucun build C++**. La boucle est :

```bash
# 1. Sélectionner le jeu
task set-game-jak2

# 2. Ouvrir le REPL
task repl
# Dans le REPL : (mi)

# 3. Démarrer et analyser les logs
task boot-game
```

```bash
# Scruter les erreurs mémoire ou pointeurs invalides :
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

---

## 9. Section extensible : découvertes d'architecture futures

### 9.1 Architecture des banques de sons Overlord & allocation des slots SPU
- **Sous-système Audio (Overlord) :** Les banques `.SBK` sont chargées dans la RAM SPU. Jak 2 et 3 fournissent des slots dédiés fixes pour les banques résidentes (`common`, `gun`, `board`) ainsi qu'un pool tournant de 3 slots pour les banques de niveau.
- **Voie A — Ajout à COMMON (Recommandé) :** `(append-sbk "COMMON" "custom_assets/jak2/sounds/sfx/MES_SFX")` fusionne directement les sons dans `COMMON.SBK`.
- **Voie B — Banque Autonome (`build-sbk`) :** Allouée dans le pool tournant de 3 slots lors du chargement.

### 9.2 Liaison d'Art-Group squelettique & Master Art-Groups
- Dans OpenGOAL, les art-groups personnalisés greffés sur des personnages natifs nécessitent un enregistrement : `(register-custom-art-group "<nom>")`.
- Ceci assure la liaison automatique avec le master art-group au chargement de niveau.

---

## 10. Comment contribuer

Pour garder les branches de mods développées en parallèle sans conflit, ce fichier a **une seule source de vérité : `master-dev`**.
1. Utilisez `task modding-land-doc -- --file docs/modding/engine_generic_concepts.md --message "..." --push`.
2. Sur votre branche : `task modding-sync-docs` pour rapatrier la mise à jour.
Ne jamais éditer ce fichier directement sur une branche de mod.
