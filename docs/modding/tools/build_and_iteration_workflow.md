# OpenGOAL — Build & Iteration Workflow (Fast Mod Compilation)
# Workflow de Compilation & d'Itération (Compilation Rapide des Mods)

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 / Jak 2 / Jak 3 (OpenGOAL PC Port) — all mod branches
> - **Origin / Provenance :** `master-dev`
> - **Last Updated / Dernière modification :** `master-dev`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Why this exists

A full `task build-release` compiles **~20 executables** — the game runtime (`gk`), the compiler
(`goalc`), the decompiler, the language server, dozens of standalone tools, the unit/offline test
suites, and every bundled third-party library (SDL, curl, draco, zydis, capstone…). On a typical
machine that is **10–20 minutes**. For day-to-day modding you almost never need most of it.

Three changes on `master-dev` make iteration dramatically faster. None of them change *what* is
built — only *how much* and *how fast*.

| Change | What it does | Typical gain |
|---|---|---|
| **`sccache` compiler cache** | Remembers the compiled output of every `.cpp`. After a branch switch or a small revert, unchanged files are served from cache instead of recompiled. | Rebuild after `git switch`: **~1–2 min instead of ~15** |
| **Uncapped `--parallel`** | The build tasks no longer force `--parallel 8`; the generator now uses **every CPU core**. | Clean build **~1.5–1.8× faster** |
| **Targeted `*-game` / `*-decomp` tasks** | Build only the binaries you actually need instead of all 20. | Iteration build **~40–55 % fewer files** |

There is also a correctness fix: the `build*` tasks now always pass `--config Release`/`--config
Debug`. With the project's normal Ninja setup this is a harmless no-op, but if a build directory
was ever configured with the Visual Studio generator, `cmake --build` silently defaults to a
**Debug** build even inside `out/build/Release`. Passing `--config` removes that trap.

## 2. The mental model — three independent layers

Understanding this is the key to never waiting for a build you don't need.

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 1 — C++ runtime & compiler   (gk, goalc)                       │
│   Source: game/  common/  goalc/  + third-party                      │
│   Rebuild with: task build-release-game                              │
│   Needed when: you edit engine C++, renderers, mips2c, the compiler  │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 2 — Decompiler & asset extraction   (decompiler)               │
│   Source: decompiler/  common/                                       │
│   Rebuild with: task build-release-decomp                            │
│   Needed when: you change how assets/types are extracted from the    │
│                original game (config JSON changes, mips2c ports,     │
│                new extraction features, texture/model injection)     │
│   After rebuilding, you must RE-RUN the extraction (see §5)          │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 3 — GOAL game code   (*.gc / *.gd / *.gp)                       │
│   Source: goal_src/jak[x]/                                           │
│   "Rebuild" with: the REPL — task repl  then  (mi)                   │
│   Needed when: you edit gameplay logic, states, types, HUD…          │
│   NO C++ compilation involved. Hot-reloads into a running game.      │
└─────────────────────────────────────────────────────────────────────┘
```

**Most mods only ever touch Layer 3.** For those, you never run a C++ build after the initial
setup — you use the REPL.

## 3. First-time setup (once per machine / after `task clean-cmake`)

```bash
# 1. Optional but strongly recommended — install the compiler cache.
#    Windows:
scoop install sccache
#    Linux (apt):        sudo apt install sccache      (or: cargo install sccache)
#    macOS (brew):       brew install sccache
#    (optionally) raise the cache budget so several branches fit:
#    Windows:  setx SCCACHE_CACHE_SIZE 25G       Linux/macOS: export SCCACHE_CACHE_SIZE=25G

# 2. Generate the build system. This is where sccache gets "baked in":
#    the Taskfile auto-detects sccache on PATH and wires it into CMake here.
task gen-cmake-release

# 3. One full build — needed to get the decompiler for asset extraction.
task build-release

# 4. Extract the assets from your legal ISO in ./iso_data (once, unless config changes).
task extract
```

> If you skip `sccache`, everything still works — the Taskfile simply omits it. But you lose the
> single biggest speed-up for branch-heavy mod work.

## 4. Everyday iteration loop

### 4a. Editing GOAL code (`.gc`) — the common case, no C++ build

```bash
task repl                 # starts goalc, connects to the game
# in the REPL:
(mi)                      # incrementally compile + hot-reload your changes into the running game
```
Keep the REPL open. Every `(mi)` after an edit takes seconds.

### 4b. Editing C++ engine or compiler code

```bash
task build-release-game   # builds ONLY gk + goalc (+ their libraries)
task boot-game            # or: task run-game
```
`build-release-game` skips: `decompiler`, `lsp`, `extractor`, all `tools/`, the test suites, and
standalone third-party binaries. With `sccache` warm, only the files you actually changed
recompile.

### 4c. Switching between mod branches

```bash
git switch jak2/features/my-other-mod
task build-release-game   # sccache serves the unchanged 95 %+ from cache — fast
```

## 5. What if my mod needs to modify the decompiler?

Some mods legitimately need decompiler changes — for example:

- adding an entry to `extra_art_groups_by_dgo` or another `decompiler/config/jak[x]/*.jsonc` key
  (custom model / `.fr3` injection, extra level extraction),
- porting a new `mips2c` function so a type extracts correctly,
- teaching the decompiler about a new type layout or a new asset format.

`task build-release-game` **will not** rebuild the decompiler — that is the whole point of the
targeted task. The workflow is:

```bash
# 1. Rebuild ONLY the decompiler (sccache still applies — only changed files recompile).
task build-release-decomp

# 2. Re-run the extraction so the decompiled output / assets are regenerated with your new
#    decompiler. Pick the one that matches your change:
task extract                       # full asset + level extraction (config JSON changes,
                                   #   texture/model/collision/level injection)
task decomp                        # re-decompile all GOAL code to reference output
task update-gsrc-file FILE=foo.gc  # re-decompile + fold one file back into goal_src/
task decomp-file FILE=foo          # decompile a single object without touching goal_src/

# 3. Then rebuild the game code as usual (REPL (mi), or task build-release-game if you also
#    changed engine C++).
```

Key point: **a decompiler change is inert until you re-extract.** The decompiler runs *offline*;
its output (in `decompiler_out/`, `goal_src/`, and the extracted asset packs) is what the game
actually loads. Rebuilding the binary without re-running it changes nothing in-game.

If you changed *both* engine C++ and the decompiler, run `task build-release-decomp` **and**
`task build-release-game` (or a single `task build-release` for everything).

Document any decompiler-config change in your mod's root `README.md` "Binary Compilation" step so
other users know they must run `task build-release` + `task extract`, not just the standard
binaries.

## 6. Task reference

| Task | Builds | Use when |
|---|---|---|
| `task gen-cmake-release` | *(configure only)* | first setup, after `task clean-cmake`, or to pick up a newly-installed `sccache` |
| `task build-release` | everything (~20 exes) | first build, CI-like full check, or you changed many layers at once |
| `task build-release-game` | `gk` + `goalc` | iterating on engine / compiler C++ |
| `task build-release-decomp` | `decompiler` | you changed `decompiler/` code or `decompiler/config/**` |
| `task repl` → `(mi)` | *(nothing — hot reload)* | iterating on GOAL `.gc` code |
| `task extract` | *(runs decompiler)* | first setup, or after a decompiler / config change |

`build-debug`, `build-debug-game`, `build-debug-decomp` are the `Debug` equivalents (paired with
`task gen-cmake-debug`).

## 7. Checking that sccache is working

```bash
sccache --show-stats
```
Look at the "Cache hits" vs "Cache misses" ratio. A rebuild after a branch switch should be
almost all hits. `sccache --zero-stats` resets the counters before a test build.

---

# 🇫🇷 Version Française

## 1. Pourquoi ce document

Un `task build-release` complet compile **~20 exécutables** — le runtime du jeu (`gk`), le
compilateur (`goalc`), le décompilateur, le serveur de langage, des dizaines d'outils autonomes,
les suites de tests unitaires/offline, et toutes les bibliothèques tierces embarquées (SDL, curl,
draco, zydis, capstone…). Sur une machine classique cela représente **10 à 20 minutes**. Pour le
modding quotidien, la quasi-totalité de ce travail est inutile.

Trois changements sur `master-dev` accélèrent fortement l'itération. Aucun ne modifie *ce qui* est
construit — seulement *la quantité* et *la vitesse*.

| Changement | Rôle | Gain typique |
|---|---|---|
| **Cache de compilation `sccache`** | Mémorise le résultat compilé de chaque `.cpp`. Après un changement de branche ou un petit revert, les fichiers inchangés sont servis depuis le cache au lieu d'être recompilés. | Rebuild après `git switch` : **~1–2 min au lieu de ~15** |
| **`--parallel` déplafonné** | Les tâches de build ne forcent plus `--parallel 8` ; le générateur utilise désormais **tous les cœurs CPU**. | Build propre **~1,5–1,8× plus rapide** |
| **Tâches ciblées `*-game` / `*-decomp`** | Ne construit que les binaires réellement nécessaires au lieu des 20. | Build d'itération **~40–55 % de fichiers en moins** |

Il y a aussi une correction de fiabilité : les tâches `build*` passent maintenant toujours
`--config Release`/`--config Debug`. Avec la configuration Ninja normale du projet, c'est un
no-op inoffensif ; mais si un dossier de build a été configuré avec le générateur Visual Studio,
`cmake --build` retombe silencieusement sur un build **Debug** même dans `out/build/Release`.
Passer `--config` supprime ce piège.

## 2. Le modèle mental — trois couches indépendantes

Le comprendre est la clé pour ne jamais attendre un build dont vous n'avez pas besoin.

```
┌─────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 — Runtime & compilateur C++   (gk, goalc)                   │
│   Source : game/  common/  goalc/  + third-party                     │
│   Recompiler avec : task build-release-game                          │
│   Nécessaire si : vous modifiez le C++ moteur, les renderers,        │
│                   le mips2c, le compilateur                          │
├─────────────────────────────────────────────────────────────────────┤
│ COUCHE 2 — Décompilateur & extraction d'assets   (decompiler)        │
│   Source : decompiler/  common/                                      │
│   Recompiler avec : task build-release-decomp                        │
│   Nécessaire si : vous changez la façon dont les assets/types sont   │
│                   extraits du jeu d'origine (modif du JSON de        │
│                   config, portage mips2c, nouvelle fonctionnalité    │
│                   d'extraction, injection de textures/modèles)       │
│   Après recompilation, il faut RELANCER l'extraction (voir §5)       │
├─────────────────────────────────────────────────────────────────────┤
│ COUCHE 3 — Code GOAL du jeu   (*.gc / *.gd / *.gp)                    │
│   Source : goal_src/jak[x]/                                          │
│   « Recompiler » avec : le REPL — task repl  puis  (mi)              │
│   Nécessaire si : vous modifiez la logique de jeu, les états,        │
│                   les types, le HUD…                                 │
│   AUCUNE compilation C++. Hot-reload dans un jeu en cours.           │
└─────────────────────────────────────────────────────────────────────┘
```

**La plupart des mods ne touchent que la Couche 3.** Dans ce cas, vous ne lancez jamais de build
C++ après l'installation initiale — vous utilisez le REPL.

## 3. Installation initiale (une fois par machine / après `task clean-cmake`)

```bash
# 1. Optionnel mais fortement recommandé — installer le cache de compilation.
#    Windows :
scoop install sccache
#    Linux (apt) :        sudo apt install sccache      (ou : cargo install sccache)
#    macOS (brew) :       brew install sccache
#    (optionnel) augmenter le budget du cache pour y loger plusieurs branches :
#    Windows :  setx SCCACHE_CACHE_SIZE 25G      Linux/macOS : export SCCACHE_CACHE_SIZE=25G

# 2. Générer le système de build. C'est ici que sccache est « intégré » :
#    le Taskfile détecte automatiquement sccache sur le PATH et le câble dans CMake.
task gen-cmake-release

# 3. Un build complet — nécessaire pour obtenir le décompilateur (extraction d'assets).
task build-release

# 4. Extraire les assets depuis votre ISO légale dans ./iso_data (une fois, sauf modif de config).
task extract
```

> Si vous n'installez pas `sccache`, tout fonctionne quand même — le Taskfile l'omet simplement.
> Mais vous perdez la plus grosse accélération pour un travail de mod à branches multiples.

## 4. Boucle d'itération quotidienne

### 4a. Modifier du code GOAL (`.gc`) — le cas courant, sans build C++

```bash
task repl                 # lance goalc, se connecte au jeu
# dans le REPL :
(mi)                      # compile incrémentalement + hot-reload dans le jeu en cours
```
Gardez le REPL ouvert. Chaque `(mi)` après une modif prend quelques secondes.

### 4b. Modifier du code C++ (moteur ou compilateur)

```bash
task build-release-game   # ne construit QUE gk + goalc (+ leurs bibliothèques)
task boot-game            # ou : task run-game
```
`build-release-game` saute : `decompiler`, `lsp`, `extractor`, tout `tools/`, les suites de
tests, et les binaires tiers autonomes. Avec `sccache` « chaud », seuls les fichiers réellement
modifiés sont recompilés.

### 4c. Basculer entre branches de mod

```bash
git switch jak2/features/mon-autre-mod
task build-release-game   # sccache sert 95 %+ de fichiers inchangés depuis le cache — rapide
```

## 5. Que se passe-t-il si mon mod doit modifier le décompilateur ?

Certains mods ont légitimement besoin de modifier le décompilateur — par exemple :

- ajouter une entrée à `extra_art_groups_by_dgo` ou à une autre clé de
  `decompiler/config/jak[x]/*.jsonc` (injection de modèle custom / `.fr3`, extraction de niveau
  supplémentaire),
- porter une nouvelle fonction `mips2c` pour qu'un type s'extraie correctement,
- apprendre au décompilateur un nouveau layout de type ou un nouveau format d'asset.

`task build-release-game` **ne reconstruira pas** le décompilateur — c'est justement le but de la
tâche ciblée. La marche à suivre est :

```bash
# 1. Recompiler UNIQUEMENT le décompilateur (sccache s'applique — seuls les fichiers
#    modifiés sont recompilés).
task build-release-decomp

# 2. Relancer l'extraction pour que la sortie décompilée / les assets soient régénérés avec
#    votre nouveau décompilateur. Choisissez la commande adaptée à votre changement :
task extract                       # extraction complète assets + niveaux (modif du JSON de
                                   #   config, injection texture/modèle/collision/niveau)
task decomp                        # re-décompile tout le code GOAL vers la sortie de référence
task update-gsrc-file FILE=foo.gc  # re-décompile + réintègre un fichier dans goal_src/
task decomp-file FILE=foo          # décompile un seul objet sans toucher à goal_src/

# 3. Puis recompilez le code du jeu comme d'habitude (REPL (mi), ou task build-release-game si
#    vous avez aussi modifié du C++ moteur).
```

Point essentiel : **une modification du décompilateur est inerte tant que vous n'avez pas
ré-extrait.** Le décompilateur s'exécute *hors-ligne* ; c'est sa sortie (dans `decompiler_out/`,
`goal_src/`, et les packs d'assets extraits) que le jeu charge réellement. Recompiler le binaire
sans le relancer ne change rien en jeu.

Si vous avez modifié *à la fois* le C++ moteur et le décompilateur, lancez
`task build-release-decomp` **et** `task build-release-game` (ou un seul `task build-release` pour
tout).

Documentez toute modification de config du décompilateur dans l'étape « Compilation des Binaires »
du `README.md` racine de votre mod, afin que les autres utilisateurs sachent qu'ils doivent
lancer `task build-release` + `task extract`, et pas seulement utiliser les binaires standards.

## 6. Référence des tâches

| Tâche | Construit | Quand l'utiliser |
|---|---|---|
| `task gen-cmake-release` | *(configuration seule)* | première install, après `task clean-cmake`, ou pour prendre en compte un `sccache` fraîchement installé |
| `task build-release` | tout (~20 exes) | premier build, vérification complète type CI, ou modifications de plusieurs couches à la fois |
| `task build-release-game` | `gk` + `goalc` | itération sur le C++ moteur / compilateur |
| `task build-release-decomp` | `decompiler` | modification de `decompiler/` ou de `decompiler/config/**` |
| `task repl` → `(mi)` | *(rien — hot reload)* | itération sur le code GOAL `.gc` |
| `task extract` | *(exécute le décompilateur)* | première install, ou après un changement décompilateur / config |

`build-debug`, `build-debug-game`, `build-debug-decomp` sont les équivalents `Debug` (à associer à
`task gen-cmake-debug`).

## 7. Vérifier que sccache fonctionne

```bash
sccache --show-stats
```
Regardez le ratio « Cache hits » vs « Cache misses ». Un rebuild après un changement de branche
devrait être quasiment 100 % de hits. `sccache --zero-stats` remet les compteurs à zéro avant un
build de test.
