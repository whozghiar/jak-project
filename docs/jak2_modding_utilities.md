# Jak 2 — notes de modding & fonctionnement mémoire

> Document de travail, pensé pour être complété au fil des sessions. Objectif : garder une
> trace pédagogique de comment le moteur OpenGOAL/jak-project fonctionne « sous le capot »,
> avec des exemples concrets tirés du repo, pour qu'une personne qui découvre le projet (ou
> une future session) puisse comprendre rapidement sans tout redécouvrir à chaque fois.
>
> Pour une vue d'ensemble des 4 briques du projet (`goalc`, `decompiler`, `goal_src/`, `game`),
> voir [`docs/project-overview.md`](./project-overview.md). Ce document-ci se concentre sur des
> sujets plus « profonds » découverts en pratique.

## Sommaire

- [1. Le vocabulaire de base](#1-le-vocabulaire-de-base)
- [2. L'architecture mémoire du runtime](#2-larchitecture-mémoire-du-runtime)
- [3. Où sont définies les constantes mémoire](#3-où-sont-définies-les-constantes-mémoire)
- [4. Étude de cas : augmenter la mémoire pour Jak 2](#4-étude-de-cas--augmenter-la-mémoire-pour-jak-2)
- [5. Compiler et valider un changement GOAL](#5-compiler-et-valider-un-changement-goal)
- [6. Lancer le jeu et lire les logs de boot](#6-lancer-le-jeu-et-lire-les-logs-de-boot)
- [7. Outils de diagnostic mémoire *en jeu*](#7-outils-de-diagnostic-mémoire-en-jeu)
- [8. Pièges connus / points de vigilance](#8-pièges-connus--points-de-vigilance)

---

## 1. Le vocabulaire de base

| Terme | Signification |
|---|---|
| **EE** | "Emotion Engine", le CPU principal de la PS2. Le port PC émule sa mémoire principale en la réservant via `mmap` (voir `game/runtime.cpp`). |
| **GOAL** | Le langage (dialecte de Lisp/Scheme) dans lequel *tout* le code du jeu Naughty Dog est écrit (`goal_src/**/*.gc`). Compilé par notre implémentation maison, **OpenGOAL**. |
| **`goalc`** | Le compilateur OpenGOAL. S'utilise en mode REPL (`task repl`) ou en mode batch avec `-c "(commande)"`. |
| **`gk`** | L'exécutable du runtime C++ ("game kernel") qui charge et exécute le code GOAL compilé. C'est littéralement le jeu. |
| **DGO** | "Data Group Object" — un fichier "paquet" qui regroupe plusieurs objets GOAL compilés (code + données) chargés ensemble depuis le disque (équivalent moderne d'un patch/DLC). |
| **Heap** | Une zone de mémoire allouée en bloc, dans laquelle GOAL alloue ensuite ses propres objets. Il y en a plusieurs types, voir section 2. |
| **`valid?`** | Fonction GOAL (dans `gcommon.gc`) qui vérifie qu'un pointeur "a l'air" correct avant de le déréférencer (alignement + plage d'adresses). Sert de garde-fou de debug, pas une vraie protection mémoire. |

## 2. L'architecture mémoire du runtime

Le runtime réserve **un seul gros bloc de mémoire virtuelle contiguë** au démarrage
(`EE_MAIN_MEM_SIZE`, via `mmap` dans `game/runtime.cpp:161-171`), qui simule la RAM de la PS2.
Tout le reste (heaps GOAL, pile, table des symboles, etc.) vit **à l'intérieur** de ce bloc, à
des offsets fixes définis en dur.

```
0x000000 ─────────────────────────────────────────────────────────────────► EE_MAIN_MEM_SIZE
│
├─ 0x000000 – 0x080000  zone protégée (EE_MAIN_MEM_LOW_PROTECT, comme le kernel PS2)
├─ 0x013fd20            HEAP_START — début du "global heap"
│                        (types, process de base, code du kernel, table des symboles…)
├─ 0x12D00000           GLOBAL_HEAP_END (avec BIG_MEMORY, ce qui est le cas sur PC)
│                        └─ le "level heap" est alloué DANS ce qu'il reste du global heap
│                           quand un niveau se charge (voir goal_src/<game>/engine/level/level.gc)
├─ (petit espace libre)
├─ 0x14000000           DEBUG_HEAP_START — heap séparé pour les outils de debug/REPL
└─ 512 Mo (0x20000000)  fin de la mémoire EE réservée
```

Points clés :

- **`GLOBAL_HEAP_END`, `DEBUG_HEAP_START`, `EE_MAIN_MEM_SIZE`** sont définis dans du code
  **C++ partagé entre tous les jeux** (`common/goal_constants.h`,
  `game/kernel/common/memory_layout.h`) — pas de version par-jeu. Un changement ici affecte
  Jak 1, 2, 3 et Jak X en même temps.
- Le **level heap**, lui, n'est *pas* une zone à adresse fixe séparée : c'est un `kmalloc`
  classique fait **depuis le global heap** au moment de charger un niveau. Sa taille max est
  définie **par jeu**, en GOAL, dans `goal_src/<jeu>/engine/level/level.gc`
  (`DEBUG_LEVEL_HEAP_MULT`). C'est pour ça qu'un level heap trop gros peut littéralement ne
  plus tenir dans ce qu'il reste du global heap (voir étude de cas section 4).
- **`valid?`** (dans `gcommon.gc`, par jeu) refuse tout pointeur `>= END_OF_MEMORY`. Si
  `END_OF_MEMORY` est resté à l'ancienne borne PS2 (128 Mo = `0x8000000`) alors que la mémoire
  réelle a été étendue à 512 Mo, **tout objet alloué au-delà de 128 Mo est rejeté** avec
  l'erreur `"... is not a valid object (bad address)"`, même s'il est parfaitement valide.
  C'est un piège classique quand on étend la mémoire : il faut penser à relever cette borne
  aussi.

## 3. Où sont définies les constantes mémoire

| Constante | Fichier | Portée |
|---|---|---|
| `EE_MAIN_MEM_SIZE` | `common/goal_constants.h` | **Partagée** (tous les jeux) |
| `GLOBAL_HEAP_END` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_START` | `game/kernel/common/memory_layout.h` | **Partagée** |
| `DEBUG_HEAP_SIZE` | `game/kernel/common/memory_layout.h` | Par jeu (namespace `jak2`, `jak3`…), mais valeurs identiques aujourd'hui |
| `END_OF_MEMORY` (utilisé par `valid?`) | `goal_src/<jeu>/kernel/gcommon.gc` | **Par jeu** |
| `DEBUG_LEVEL_HEAP_MULT` (taille du level heap) | `goal_src/<jeu>/engine/level/level.gc` | **Par jeu** |

Ce tableau explique pourquoi porter le changement de Jak 3 vers Jak 2 ne demandait de
toucher **que 2 fichiers GOAL** (les lignes "Par jeu") : le reste (partie C++) était déjà
partagé et donc déjà actif pour Jak 2 dès que le commit Jak 3 a été mergé dans `master`.

## 4. Étude de cas : augmenter la mémoire pour Jak 2

Contexte : la branche `jak3/config/memory_increase` (mergée dans `master`, commit `334dcd5c0`)
augmentait la mémoire PC de 128 Mo (budget PS2 d'origine) à 512 Mo, pour laisser de la place
à du contenu custom (acteurs/entités ajoutés par des mods). Objectif : reproduire le même
changement pour Jak 2, sur `jak2/config/memory_increase`.

### Ce qui était déjà fait gratuitement

Comme `EE_MAIN_MEM_SIZE` et `GLOBAL_HEAP_END` sont dans du code C++ **partagé**, Jak 2
bénéficiait déjà des 512 Mo de mémoire réservée et d'un global heap élargi (~300 Mo) dès que
`master` a récupéré le commit Jak 3 — sans rien faire de plus.

### Ce qu'il restait à porter

Seules les 2 constantes **GOAL, par jeu** devaient être copiées :

```diff
--- goal_src/jak2/kernel/gcommon.gc
-(defconstant END_OF_MEMORY #x8000000)
+(defconstant END_OF_MEMORY #x20000000)  ;; 512 Mo, aligné sur EE_MAIN_MEM_SIZE
```

```diff
--- goal_src/jak2/engine/level/level.gc
-(defglobalconstant DEBUG_LEVEL_HEAP_MULT 1.1)
+(defglobalconstant DEBUG_LEVEL_HEAP_MULT 15.0)  ;; valeur copiée telle quelle de jak3
```

### Le piège : copier la valeur de jak3 telle quelle a fait planter le jeu

En **testant réellement** (compilation + boot, voir sections 5 et 6), le second changement
faisait planter le jeu dès le premier chargement de niveau :

```
kmalloc: !alloc mem heap (282562560 bytes) heap 13ad00
dkernel: unable to malloc 10076 bytes for main-segment
... Segmentation fault
```

Explication : `DEBUG_LEVEL_HEAP_MULT = 15.0` demande un level heap de **282 Mo**, alloué
depuis le global heap partagé (~300 Mo au total). Mais au moment de charger le premier
niveau, Jak 2 a déjà consommé environ **35 Mo** de ce global heap pour son code de boot —
il ne restait donc que ~279 Mo de libre, **moins que les 282 Mo demandés**. Jak 3 a
apparemment moins de code chargé à ce stade-là et arrive à faire tenir 282 Mo dans le même
budget de ~300 Mo — d'où le fait que la même valeur "marche" pour un jeu et pas l'autre,
alors que le mécanisme est identique.

**Leçon générale : une constante mémoire qui marche pour un jeu ne se transpose pas
forcément telle quelle à un autre jeu, même si le mécanisme sous-jacent est partagé.** Il
faut valider par un vrai build + boot, pas seulement copier le diff.

### Valeur retenue

`DEBUG_LEVEL_HEAP_MULT = 12.0` → level heap ≈ 215 Mo, ce qui laisse une marge de sécurité
d'environ 60 Mo sous le budget disponible mesuré (~279 Mo), tout en restant une augmentation
d'environ **10×** par rapport à la valeur d'origine (1.1×). Confirmé en testant un vrai boot
jusqu'au chargement du niveau suivant (`forexita`) sans erreur d'allocation.

Si un jour on veut pousser davantage, il faudra soit réduire ce qui est chargé avant le
premier niveau, soit revoir `GLOBAL_HEAP_END` (partagé — attention à l'impact sur les autres
jeux), et re-mesurer le budget libre disponible de la même façon.

## 5. Compiler et valider un changement GOAL

Un changement dans un fichier `.gc` ne vaut rien tant qu'il n'a pas **recompilé sans erreur**.
Le binaire `goalc` peut compiler tout le jeu en mode batch (pas besoin du REPL interactif) :

```sh
# Depuis out/build/Release/bin/
./goalc.exe --game jak2 -c "(mi)"
```

`(mi)` = "make", la commande GOAL qui reconstruit tous les objets/DGO déclarés pour le jeu
sélectionné. Elle affiche la progression fichier par fichier et termine par :

```
Successfully built all 933 targets in 33.156s
```

Code de sortie `0` + ce message = tout compile. Une erreur de syntaxe ou de type dans un
`.gc` fait échouer la commande avec un message d'erreur pointant le fichier/la ligne fautifs.

Équivalent via `task` (si le jeu courant configuré via `task set-game-jak2` correspond) :
`task repl` puis taper `(mi)` dans le REPL interactif.

## 6. Lancer le jeu et lire les logs de boot

```sh
# Depuis out/build/Release/bin/
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```

- `-fakeiso` : utilise les assets déjà extraits dans `iso_data/jak2` / `out/jak2` au lieu
  d'un vrai lecteur DVD.
- `-boot` : lance directement en jeu plutôt que sur l'écran titre.
- `-debug` : active les fonctionnalités de debug (dont les heaps "debug", plus permissifs).
- `-v` : verbeux, affiche aussi les logs `debug` sur la sortie standard (sinon seul le fichier
  de log les contient).

Les logs sont toujours écrits dans `<racine du repo>/log/<jeu>.<horodatage>.log`, même sans
`-v`. C'est l'endroit à regarder après coup pour valider un changement mémoire :

```sh
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<horodatage>.log
```

Lignes utiles à chercher :

| Ligne dans le log | Ce qu'elle confirme |
|---|---|
| `Main memory size 0x20000000 bytes (512.000 MB)` | La mémoire EE réservée est bien de 512 Mo (côté C++, partagé). |
| `kmalloc: !alloc mem heap (N bytes) heap 13ad00` | Échec d'allocation dans le global heap — signe que le level heap (ou autre) demande plus que ce qu'il reste de libre. |
| `... is not a valid object ... (bad address)` | `END_OF_MEMORY` est trop bas par rapport aux adresses réellement utilisées — penser à le relever. |
| `Elapsed time for level = ...s` suivi de `link finish: ...` | Le niveau suivant a bien fini de charger — bon signe que ça tient en mémoire. |

Le dump d'un heap dans les logs (visible en cas d'échec d'allocation) se lit ainsi :

```
[  13ad00] kheap
  base: #x13fd20        <- début du heap
  top-base: #x12d00000  <- fin réservée du heap (GLOBAL_HEAP_END)
  cur: #x22b93c8         <- pointeur d'allocation actuel ("bottom", grossit vers le haut)
  top: #x12d00000        <- pointeur d'allocation "top" (grossit vers le bas, rarement utilisé)
   used bot: 35100328 of 314311392 bytes   <- ce qui est déjà occupé / le total disponible
```

## 7. Outils de diagnostic mémoire *en jeu*

Le jeu embarque son propre profileur de mémoire, dans
`goal_src/<jeu>/engine/debug/memory-usage.gc`. Il calcule, par niveau chargé, combien
d'octets sont utilisés par catégorie (textures, TFRAG, collision, animations…) et affiche un
pourcentage d'occupation du level heap.

Pour l'activer en jeu (avec `-debug`), il faut passer la variable globale GOAL
`*stats-memory*` à `#t`, ce qui affiche l'overlay en continu (voir
`goal_src/<jeu>/engine/draw/drawable.gc:1492-1513`, qui appelle
`(print-mem-usage (compute-memory-usage! niveau #f) niveau *stdcon*)` chaque frame). Cela
s'active normalement depuis le menu de debug PC (`goal_src/<jeu>/pc/debug/`) ou en tapant
directement dans le REPL connecté au jeu en cours d'exécution :

```lisp
(set! *stats-memory* #t)
```

C'est l'outil à privilégier pour vérifier *a posteriori*, en jouant, que le level heap élargi
laisse vraiment de la marge (et pas juste "ne plante pas au boot").

## 8. Pièges connus / points de vigilance

- **`GLOBAL_HEAP_END` et `DEBUG_HEAP_START` sont partagés entre tous les jeux.** Toucher ces
  valeurs pour "aider" un jeu peut changer le comportement des autres (Jak 1, 3, X). À
  reconfirmer par un boot de chaque jeu concerné si on les modifie.
- **Le budget mémoire "libre" au moment du chargement du niveau dépend de combien de code de
  boot est déjà chargé**, qui diffère d'un jeu à l'autre (et peut varier légèrement selon le
  niveau de démarrage utilisé, ex : `-fakeiso -debug` charge un niveau par défaut différent du
  jeu final). Une valeur de multiplicateur validée sur un niveau n'est pas nécessairement
  valide à 100 % sur tous les niveaux — garder une marge de sécurité raisonnable.
- **`game/kernel/jak2/kscheme.cpp` (et l'équivalent jak3) contiennent une borne codée en dur
  `0x8000000` dans `in_valid_memory_for_new_type()`** (vérification utilisée lors de la
  création dynamique de nouveaux types GOAL). Cette borne n'a *pas* été relevée par le commit
  Jak 3 d'origine ni par le portage Jak 2 — elle n'a pas causé de problème observé (la
  création de types se fait tôt, en zone basse de mémoire), mais c'est une incohérence
  latente à garder en tête si un jour un mod crée dynamiquement des types à haute adresse.
- **Ne jamais valider un changement de constante mémoire uniquement "à la lecture".** Comme
  démontré section 4, une valeur qui compile très bien peut quand même faire planter le jeu au
  runtime. Le triptyque **compiler (`(mi)`) → booter (`gk -v -- -boot -fakeiso -debug`) →
  grep le log** est le minimum pour valider ce genre de changement.
