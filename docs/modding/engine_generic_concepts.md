# Engine Generic Concepts — Jak 1 / Jak 2 / Jak 3 / Concepts Moteur Génériques

> **Bilingual reference / Référence bilingue**
>
> - [🇬🇧 English](#-english) · [🇫🇷 Français](#-français)
>
> **What this file is / Rôle de ce fichier**
>
> 🇬🇧 The shared, plain-language primer on how the OpenGOAL engine works *below* the
> Lisp syntax: memory, heaps, level streaming, process life cycle, boot diagnostics.
> It is **common to all three games**. Read it once before your first mod; come back
> to it whenever a crash mentions memory or an object "not found".
>
> 🇫🇷 L'introduction commune, en langage simple, au fonctionnement du moteur OpenGOAL
> *en dessous* de la syntaxe Lisp : mémoire, tas (heaps), streaming de niveaux, cycle
> de vie des processus, diagnostic au démarrage. Ce fichier est **commun aux trois
> jeux**. À lire une fois avant votre premier mod ; à relire dès qu'un crash parle de
> mémoire ou d'un objet « introuvable ».
>
> **Contract / Contrat**
>
> 🇬🇧 Only verified facts belong here. If you discover a new architectural fact while
> modding, **do not add it on your mod branch** — record it on `master-dev` (see
> [How to contribute](#how-to-contribute--comment-contribuer)) so parallel mods never
> conflict on this file.
>
> 🇫🇷 Seuls des faits vérifiés figurent ici. Si vous découvrez un nouveau fait
> d'architecture en moddant, **ne l'ajoutez pas sur votre branche de mod** —
> consignez-le sur `master-dev` (voir [Comment contribuer](#how-to-contribute--comment-contribuer))
> pour que les mods développés en parallèle n'entrent jamais en conflit sur ce fichier.

---

<a name="-english"></a>
<a name="-français"></a>

## 1 — The simulated PS2 memory block / Le bloc mémoire PS2 simulé

> 🇬🇧 The original games ran on the PS2's "Emotion Engine" (EE) CPU with a fixed
> block of RAM. The PC port keeps that model: at start-up the C++ runtime (`gk`)
> reserves **one big contiguous virtual memory block** with `mmap` and lets the GOAL
> code allocate inside it at fixed offsets — exactly as the PS2 kernel did. Nothing
> in GOAL uses the operating system's `malloc` directly; everything lives inside this
> one block.
>
> 🇫🇷 Les jeux d'origine tournaient sur le processeur « Emotion Engine » (EE) de la
> PS2 avec une quantité de RAM fixe. Le port PC conserve ce modèle : au démarrage, le
> runtime C++ (`gk`) réserve **un seul grand bloc de mémoire virtuelle contiguë** via
> `mmap`, et le code GOAL alloue à l'intérieur à des offsets fixes — exactement comme
> le faisait le noyau PS2. Rien en GOAL n'utilise le `malloc` du système
> d'exploitation ; tout vit dans ce bloc unique.

```
game/runtime.cpp   ── mmap( EE_MAIN_MEM_SIZE ) ──►  ┌──────────────────────────────┐
                                                    │  simulated PS2 RAM (1 block) │
                                                    └──────────────────────────────┘
```

- 🇬🇧 **Why you care:** a mod that allocates too much, or writes past a heap, does
  not corrupt your PC — it corrupts *this* block and the game crashes with a memory
  error. The size of the block is `EE_MAIN_MEM_SIZE` (see §3).
- 🇫🇷 **Pourquoi c'est important :** un mod qui alloue trop, ou qui écrit au-delà
  d'un heap, ne corrompt pas votre PC — il corrompt *ce* bloc et le jeu plante avec
  une erreur mémoire. La taille du bloc est `EE_MAIN_MEM_SIZE` (voir §3).

---

## 2 — The three heaps / Les trois tas (heaps)

> 🇬🇧 A "heap" is just a labelled region *inside* the big block where GOAL allocates
> objects. There are three you will meet:
>
> | Heap | Holds | Lifetime |
> |---|---|---|
> | **global heap** | types, the symbol table, kernel code, always-resident processes, `*target*` | whole session |
> | **level heap** | everything a level needs: its geometry, textures, actors, art | freed when the level unloads |
> | **debug heap** | debug menu, REPL helpers, profiling tools | whole session, but **only in `-debug` builds** |
>
> When you write `(object-new 'global ...)`, `(object-new 'process ...)` or
> `(object-new 'debug ...)`, the first argument picks which heap. Debug-only code
> (a debug menu entry, a diagnostic) must allocate on `'debug` so it disappears
> cleanly from release builds.
>
> 🇫🇷 Un « heap » (tas) est simplement une région étiquetée *à l'intérieur* du grand
> bloc, où GOAL alloue ses objets. Vous en rencontrerez trois :
>
> | Heap | Contient | Durée de vie |
> |---|---|---|
> | **global heap** | les types, la table des symboles, le code kernel, les process toujours résidents, `*target*` | toute la session |
> | **level heap** | tout ce qu'un niveau nécessite : géométrie, textures, acteurs, art | libéré au déchargement du niveau |
> | **debug heap** | menu debug, aides REPL, outils de profilage | toute la session, mais **uniquement en build `-debug`** |
>
> Quand vous écrivez `(object-new 'global ...)`, `(object-new 'process ...)` ou
> `(object-new 'debug ...)`, le premier argument choisit le heap. Le code réservé au
> debug (une entrée de menu debug, un diagnostic) doit allouer sur `'debug` pour
> disparaître proprement des builds release.

```lisp
;; EN: allocate a short-lived actor on the process/level heap (normal case)
;; FR: allouer un acteur à courte durée de vie sur le heap process/niveau (cas normal)
(process-spawn my-actor :to *entity-pool*)

;; EN: allocate menu/diagnostic data on the debug heap so release builds drop it
;; FR: allouer des données de menu/diagnostic sur le debug heap pour que le release les retire
(new 'debug 'debug-menu *debug-menu-context* "My menu")
```

- 🇬🇧 **Rule of thumb:** never allocate gameplay objects on `'global` "to be safe" —
  the global heap is small and never frees. Use the level/process heap and let it
  reclaim your object when the level unloads.
- 🇫🇷 **Règle simple :** ne jamais allouer d'objets de gameplay sur `'global` « par
  sécurité » — le global heap est petit et ne libère jamais. Utilisez le heap
  niveau/process et laissez-le récupérer votre objet au déchargement du niveau.

---

## 3 — Memory constants: where they live / Constantes mémoire : où elles vivent

> 🇬🇧 Some memory limits are set in **shared C++** (one value for *all four* games —
> Jak 1, 2, 3 and Jak X). Others are set **per game in GOAL**. Changing a shared C++
> constant for one mod silently changes it for every game.
>
> 🇫🇷 Certaines limites mémoire sont définies en **C++ partagé** (une seule valeur
> pour *les quatre* jeux — Jak 1, 2, 3 et Jak X). D'autres sont définies **par jeu en
> GOAL**. Modifier une constante C++ partagée pour un mod la modifie silencieusement
> pour tous les jeux.

| Constant | File / Fichier | Scope / Portée |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | 🇬🇧 shared (all games) · 🇫🇷 partagée (tous les jeux) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | 🇬🇧 shared · 🇫🇷 partagée |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | 🇬🇧 shared · 🇫🇷 partagée |
| `END_OF_MEMORY` (used by `valid?`) | `goal_src/<game>/kernel/gcommon.gc` | 🇬🇧 per game · 🇫🇷 par jeu |
| `DEBUG_LEVEL_HEAP_MULT` (level-heap size multiplier) | `goal_src/<game>/engine/level/level.gc` | 🇬🇧 per game · 🇫🇷 par jeu |

- 🇬🇧 A modder who only edits GOAL never touches the first three. The two GOAL
  constants are the ones you tune for a "more memory" mod (see §4).
- 🇫🇷 Un moddeur qui n'édite que du GOAL ne touche jamais aux trois premières. Les
  deux constantes GOAL sont celles que l'on ajuste pour un mod « plus de mémoire »
  (voir §4).

---

## 4 — `valid?`, "bad address", and the memory-expansion recipe / `valid?`, « bad address » et la recette d'extension mémoire

> 🇬🇧 `valid?` (in `gcommon.gc`) is the engine's pointer sanity check: it rejects any
> address `>= END_OF_MEMORY`. The PS2 limit was 128 MB (`#x8000000`). The PC port can
> reserve much more, but if `END_OF_MEMORY` is left at the PS2 value while the block
> is bigger, every object allocated above 128 MB fails with `bad address` /
> `not a valid object`.
>
> 🇫🇷 `valid?` (dans `gcommon.gc`) est le contrôle de cohérence des pointeurs du
> moteur : il rejette toute adresse `>= END_OF_MEMORY`. La limite PS2 était de 128 Mo
> (`#x8000000`). Le port PC peut réserver bien plus, mais si `END_OF_MEMORY` reste à
> la valeur PS2 alors que le bloc est plus grand, tout objet alloué au-delà de 128 Mo
> échoue avec `bad address` / `not a valid object`.

**Verified recipe (Jak 2, 512 MB) / Recette vérifiée (Jak 2, 512 Mo):**

```lisp
;; goal_src/jak2/kernel/gcommon.gc
;; EN: raise the ceiling used by valid? to 512 MB
;; FR: relever le plafond utilisé par valid? à 512 Mo
(defconstant END_OF_MEMORY #x20000000)

;; goal_src/jak2/engine/level/level.gc
;; EN: level-heap size = multiplier x base. 15.0 (Jak 3's value) over-allocates on
;;     Jak 2 (it loads ~35 MB resident first) and panics at boot. 12.0 is the tested
;;     safe value: ~215 MB level heap, ~60 MB spare — a 10x increase over the PS2.
;; FR: taille du level-heap = multiplicateur x base. 15.0 (valeur de Jak 3) sur-alloue
;;     sur Jak 2 (qui charge ~35 Mo résidents d'abord) et fait paniquer au boot. 12.0
;;     est la valeur sûre testée : ~215 Mo de level heap, ~60 Mo de marge — soit 10x
;;     l'original PS2.
(defconstant DEBUG_LEVEL_HEAP_MULT 12.0)
```

- 🇬🇧 **Always validate at runtime.** A memory change that compiles can still panic
  at boot. Follow §8's loop and check the log.
- 🇫🇷 **Toujours valider à l'exécution.** Un changement mémoire qui compile peut
  quand même paniquer au boot. Suivez la boucle du §8 et vérifiez le log.

---

## 5 — DGOs and level streaming / DGO et streaming des niveaux

> 🇬🇧 Compiled GOAL code and data are packed into **DGO** files ("Data Group
> Object"). A DGO is loaded as one unit. There are two kinds you care about:
>
> - **Resident DGOs** (e.g. `KERNEL`, `GAME`, `ENGINE`, city hub DGOs) — loaded once
>   at boot and never freed. Code here is *always available*.
> - **Level DGOs** — streamed in when you enter a level/area and freed when you
>   leave. Code and assets here exist *only while that level is loaded*.
>
> Which `.o` files go in which DGO is declared in the game's `.gd` files
> (`goal_src/<game>/dgos/*.gd`). New `.gc` source files are also registered in the
> project file `.gp` (`goal_src/<game>/<game>.gp` / `<game>-game.gp`).
>
> 🇫🇷 Le code et les données GOAL compilés sont empaquetés dans des fichiers **DGO**
> (« Data Group Object »). Un DGO est chargé d'un bloc. Deux types comptent pour vous :
>
> - **DGO résidents** (ex. `KERNEL`, `GAME`, `ENGINE`, DGO du hub urbain) — chargés
>   une fois au boot et jamais libérés. Le code ici est *toujours disponible*.
> - **DGO de niveau** — streamés à l'entrée d'un niveau/d'une zone et libérés à la
>   sortie. Le code et les assets ici n'existent *que tant que ce niveau est chargé*.
>
> Quel `.o` va dans quel DGO est déclaré dans les fichiers `.gd` du jeu
> (`goal_src/<jeu>/dgos/*.gd`). Les nouveaux fichiers source `.gc` sont aussi
> enregistrés dans le fichier projet `.gp` (`goal_src/<jeu>/<jeu>.gp` / `<jeu>-game.gp`).

- 🇬🇧 **Why you care:** if your code is spawned by an always-running system (traffic,
  a global manager) but *defined* in a level DGO, it will be missing or dangling the
  moment that level is not loaded. See §6.
- 🇫🇷 **Pourquoi c'est important :** si votre code est instancié par un système
  toujours actif (trafic, gestionnaire global) mais *défini* dans un DGO de niveau,
  il sera absent ou pendant dès que ce niveau n'est pas chargé. Voir §6.

---

## 6 — Virtual method / state residency (the vtable trap) / Résidence des méthodes et états virtuels (le piège de la vtable)

> 🇬🇧 In GOAL, `defmethod` and `(defstate ... :virtual #t)` fill a slot in the
> type's **virtual table (vtable)**. That slot is filled **when the object file is
> linked into memory**, i.e. when its DGO loads — not at compile time. So:
>
> - override compiled in a **resident** DGO → slot always filled → works.
> - override compiled in a **level** DGO that is *not loaded* → slot empty → the call
>   silently does nothing / falls back to the parent (no crash, the actor just stays
>   stuck).
> - override in a level DGO that *was* loaded then unloaded → slot **dangling** →
>   crash, or behaviour that differs before/after visiting that level.
>
> **Rule:** if a type is instantiated by an always-resident system, define **all**
> its `:virtual #t` states and virtual methods in an always-resident file.
>
> 🇫🇷 En GOAL, `defmethod` et `(defstate ... :virtual #t)` remplissent une case dans
> la **table virtuelle (vtable)** du type. Cette case est remplie **quand le fichier
> objet est lié en mémoire**, c.-à-d. au chargement de son DGO — pas à la compilation.
> Donc :
>
> - surcharge compilée dans un DGO **résident** → case toujours remplie → fonctionne.
> - surcharge compilée dans un DGO **de niveau** *non chargé* → case vide → l'appel ne
>   fait rien silencieusement / retombe sur le parent (pas de crash, l'acteur reste
>   bloqué).
> - surcharge dans un DGO de niveau *chargé puis déchargé* → case **pendante** →
>   crash, ou comportement différent avant/après avoir visité ce niveau.
>
> **Règle :** si un type est instancié par un système toujours résident, définissez
> **toutes** ses surcharges d'états `:virtual #t` et de méthodes virtuelles dans un
> fichier toujours résident.

```lisp
;; EN: BAD — a custom traffic actor's active state defined in a mission-only file.
;;     Fine during the mission, invisible/stuck in free-roam.
;; FR: MAUVAIS — l'état actif d'un acteur de trafic custom défini dans un fichier de
;;     mission. OK pendant la mission, invisible/bloqué en jeu libre.

;; EN: GOOD — define it in the resident vehicle/enemy file (e.g. vehicle.gc, car.gc).
;; FR: BON — le définir dans le fichier véhicule/ennemi résident (ex. vehicle.gc, car.gc).
(defstate active (my-traffic-actor)
  :virtual #t
  :code (behavior () (loop (ja :num! (seek!)) (suspend))))
```

---

## 7 — Process life cycle / Cycle de vie d'un processus

> 🇬🇧 Almost every live thing in the game is a **process** (a lightweight cooperative
> "thread" with its own small stack and heap). A `process-drawable` is a process that
> also has a 3D model. The cycle:
>
> 1. **spawn** — `process-spawn` / `process-spawn-function` allocates the process on a
>    pool's heap and runs its `init` code.
> 2. **run** — each frame the engine resumes the process's current **state**; the
>    state's `:code` runs until it hits `(suspend)`, which yields back to the engine
>    for that frame. `:post` runs every frame after `:code` (usually to push the
>    animation and collision).
> 3. **transition** — `(go some-state)` / `(go-virtual some-state)` switches state.
> 4. **death** — the process is deactivated; its heap is reclaimed. Children die with
>    their parent.
>
> 🇫🇷 Presque tout ce qui est vivant dans le jeu est un **processus** (un « thread »
> coopératif léger avec sa propre petite pile et son propre heap). Un
> `process-drawable` est un processus qui a en plus un modèle 3D. Le cycle :
>
> 1. **création** — `process-spawn` / `process-spawn-function` alloue le processus sur
>    le heap d'un pool et exécute son code d'`init`.
> 2. **exécution** — chaque frame, le moteur reprend l'**état** courant du processus ;
>    le `:code` de l'état s'exécute jusqu'à `(suspend)`, qui rend la main au moteur
>    pour cette frame. Le `:post` s'exécute chaque frame après le `:code` (en général
>    pour appliquer l'animation et la collision).
> 3. **transition** — `(go un-etat)` / `(go-virtual un-etat)` change d'état.
> 4. **mort** — le processus est désactivé ; son heap est récupéré. Les enfants
>    meurent avec leur parent.

- 🇬🇧 See [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) for the exact
  `deftype` / `defstate` / animation syntax.
- 🇫🇷 Voir [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) pour la syntaxe
  exacte `deftype` / `defstate` / animation.

---

## 8 — Boot diagnostics & the compile/validate loop / Diagnostic au démarrage & boucle compiler/valider

> 🇬🇧 A GOAL-only change needs **no C++ build**. The loop is:
>
> 🇫🇷 Un changement GOAL uniquement ne nécessite **aucun build C++**. La boucle est :

```bash
# 1. EN: pick the game once / FR: choisir le jeu une fois
task set-game-jak2

# 2. EN: open the compiler REPL / FR: ouvrir le REPL du compilateur
task repl
#    then in the REPL / puis dans le REPL:
#    (mi)      ;; EN: incremental compile + hot reload / FR: compilation incrémentale + hot reload

# 3. EN: boot and read the log / FR: démarrer et lire le log
task boot-game
```

```bash
# EN: scan the newest log for memory / object errors
# FR: scruter le log le plus récent pour les erreurs mémoire / objet
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

```lisp
;; EN: live memory overlay, -debug builds only
;; FR: overlay mémoire en temps réel, builds -debug uniquement
(set! *stats-memory* #t)
```

- 🇬🇧 **A clean compile is not a pass.** Always boot and check the log before
  calling a change done.
- 🇫🇷 **Une compilation propre n'est pas une validation.** Toujours démarrer et
  vérifier le log avant de considérer un changement terminé.

---

## 9 — ➕ Extensible section: future architecture discoveries / Section extensible : découvertes d'architecture futures

> 🇬🇧 New verified, mod-independent engine facts go here. Keep the same shape:
> a numbered heading, a short 🇬🇧 then 🇫🇷 explanation, one shared example, a
> "why you care" line. **Add entries on `master-dev` only** (see below) and **append**
> — never reflow the sections above.
>
> 🇫🇷 Les nouveaux faits moteur vérifiés et indépendants d'un mod vont ici. Gardez la
> même forme : un titre numéroté, une courte explication 🇬🇧 puis 🇫🇷, un exemple
> partagé, une ligne « pourquoi c'est important ». **Ajoutez les entrées sur
> `master-dev` uniquement** (voir ci-dessous) et **en fin de section** — ne jamais
> reformater les sections ci-dessus.

<!-- ➕ APPEND NEW VERIFIED CONCEPTS BELOW THIS LINE — master-dev only, one block at a time -->

---

## How to contribute / Comment contribuer

> 🇬🇧 To keep parallel mod branches conflict-free, this file has **one source of
> truth: `master-dev`**. When you discover something while working on a mod branch:
>
> 1. `task modding-land-doc` — it stashes your work, checks out `master-dev`, pulls,
>    lets you append your entry, commits `docs(concepts): … (AI-assisted)`, pushes,
>    returns you to your branch and re-syncs the docs. (Or do those steps by hand.)
> 2. Back on your branch: `task modding-sync-docs` to pull the updated file in.
>
> Never edit this file directly on a mod branch.
>
> 🇫🇷 Pour garder les branches de mods développées en parallèle sans conflit, ce
> fichier a **une seule source de vérité : `master-dev`**. Quand vous découvrez
> quelque chose sur une branche de mod :
>
> 1. `task modding-land-doc` — met votre travail de côté (stash), bascule sur
>    `master-dev`, tire (pull), vous laisse ajouter votre entrée, commit
>    `docs(concepts): … (AI-assisted)`, pousse, vous ramène sur votre branche et
>    resynchronise la doc. (Ou faites ces étapes à la main.)
> 2. De retour sur votre branche : `task modding-sync-docs` pour récupérer le fichier
>    mis à jour.
>
> Ne jamais éditer ce fichier directement sur une branche de mod.
