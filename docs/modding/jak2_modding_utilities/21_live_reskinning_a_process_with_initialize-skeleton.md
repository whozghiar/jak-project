# Jak 2 — Live-Reskinning a Process with `initialize-skeleton` / Reskin à Chaud d'un Processus avec `initialize-skeleton`

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/multiplayer`
> - **Last Updated / Dernière modification:** `jak2/features/multiplayer`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. The mechanism

`initialize-skeleton` (declared on `process-drawable`/`draw-control`,
`goal_src/jak2/engine/game/game-h.gc:151-152`) is what every `process-drawable` calls once, at
init, to bind its mesh/skeleton/animations: `(initialize-skeleton obj skeleton-group pair)`. There
is also `initialize-skeleton-by-name`, which takes a plain string instead of a resolved
`skeleton-group` (skips the `art-group-get-by-name *level* "..."` step):
`(initialize-skeleton-by-name obj "skel-some-name")`.

Nothing about this method restricts it to being called only once, at spawn, on a brand-new object.
Calling it again later, on an **already-live** process, rebinds its `skel`/`node-list`/`draw
art-group` in place — the object keeps its process identity, its position, its event handlers,
everything except its visible mesh and animation set. This codebase already proves it is safe to
do this conditionally at runtime, just not on `target`:

- `goal_src/jak2/levels/tomb/widow-extras.gc:380-467` picks one of 7 `skel-tomb-boss-catwalk-{a..g}`
  skeletons via a `case` inside one init function, on objects that can be reconfigured.
- `goal_src/jak2/levels/nest/boss/metalkor-setup.gc:608-1157` binds different Metal Kor
  sub-objects to different named skeletons (`skel-metalkor-bomb`, `-wings`, `-legs`, ...).

## 2. What it is *not*

It is tempting to assume the game's own jumpsuit → normal-clothes transition early in Jak 2 is an
example of this. It is not: that is a separate, pre-scripted `scene`/`scene-actor` cutscene system
using its own cutscene-only skeletons (e.g. `"skel-jak-highres"` in
`goal_src/jak2/levels/common/warp-gate.gc:1339-1349`) — a different renderable actor swapped into
the cutscene, not a live reskin of the interactive `target` process. Similarly, Dark Jak
(`goal_src/jak2/engine/target/target-darkjak.gc:102-160`) never calls `initialize-skeleton` — it
keeps `skel-jchar` for its entire life and fakes its look purely via `control scale` and joint-mod
trickery. So there was no in-base-game precedent for live-reskinning `target` itself before this
mod added one (`(mp-toggle-skin!)` in `goal_src/jak2/pc/multiplayer/mp-manager.gc`).

## 3. The real risk: joint layout mismatch

`target`'s per-frame cosmetic code sets up several `joint-mod`s against **fixed joint indices** on
`skel-jchar`'s `node-list` — neck look-at, head flex-blend, upper-body gun-look-at, arm/leg IK
(all set up once in `init-target`, `goal_src/jak2/engine/target/logic-target.gc:3133-3190` or so,
right after the `initialize-skeleton` call for `skel-jchar`). If you re-skin `target` to a
different skeleton whose joint hierarchy differs — e.g. `skel-crimson-guard-level`
(`crimson-guard-lod0-jg`, defined
`goal_src/jak2/levels/common/enemy/guards/crimson-guard-level.gc:12-17`) — those joint-mods are
still indexing into the *new* `node-list` by the *old* numbers. Depending on how the new skeleton's
joint count/order compares, this can silently animate the wrong joint, or index out of bounds.

This risk **only applies when re-skinning `target` itself** (which has all those joint-mods). A
process with no joint-mods — like a purpose-built stub process that only calls `ja-no-eval`/
`ja-post` — has nothing to desync, which is one more reason to keep any process that gets
re-skinned as simple as possible (see
[22_minimal_networked_stub_process_pattern.md](22_minimal_networked_stub_process_pattern.md)).

**Mitigation, not yet exhaustively applied:** gate joint-index-dependent cosmetic updates (in
`target`'s per-frame post-processing) behind a check of the currently-applied skin id, rather than
trying to remap indices for a skeleton whose joint layout wasn't designed for them. Before writing
that gating logic for a specific skeleton, dump and compare both skeletons' `node-list` joint
counts from the REPL — do not assume they line up.

## 4. Verification steps

1. From the REPL, with `*target*` alive: `(-> *target* node-list length)` before and after calling
   `(initialize-skeleton-by-name *target* "skel-crimson-guard-level")`, to see whether the joint
   count actually changed.
2. Watch the character in-game immediately after the swap for T-posing, snapped/stretched limbs,
   or a crash — any of these indicate a joint-mod is now reading a joint that does not mean what it
   used to.
3. If re-skinning a non-`target` process with no joint-mods (e.g. `remote-player`), this class of
   bug does not apply — verify visually that the mesh/animation swapped correctly, nothing more.

---

# 🇫🇷 Version Française

## 1. Le mécanisme

`initialize-skeleton` (déclarée sur `process-drawable`/`draw-control`,
`goal_src/jak2/engine/game/game-h.gc:151-152`) est ce que chaque `process-drawable` appelle une
fois, à l'initialisation, pour lier son maillage/squelette/animations : `(initialize-skeleton obj
skeleton-group pair)`. Il existe aussi `initialize-skeleton-by-name`, qui prend une simple chaîne
au lieu d'un `skeleton-group` déjà résolu (évite l'étape `art-group-get-by-name *level* "..."`) :
`(initialize-skeleton-by-name obj "skel-nom")`.

Rien dans cette méthode ne restreint son appel à une seule fois, à la création, sur un objet neuf.
L'appeler à nouveau plus tard, sur un processus **déjà vivant**, relie sur place son
`skel`/`node-list`/`draw art-group` — l'objet conserve son identité de processus, sa position, ses
gestionnaires d'événements, tout sauf son maillage visible et son jeu d'animations. Ce code source
prouve déjà que c'est sûr à faire conditionnellement à l'exécution, simplement pas sur `target` :

- `goal_src/jak2/levels/tomb/widow-extras.gc:380-467` choisit l'un des 7 squelettes
  `skel-tomb-boss-catwalk-{a..g}` via un `case` dans une fonction d'initialisation, sur des objets
  reconfigurables.
- `goal_src/jak2/levels/nest/boss/metalkor-setup.gc:608-1157` relie différents sous-objets de Metal
  Kor à différents squelettes nommés (`skel-metalkor-bomb`, `-wings`, `-legs`, ...).

## 2. Ce que ce n'est *pas*

Il est tentant de penser que le changement de la combinaison de prisonnier vers des vêtements
normaux, au début de Jak 2, en est un exemple. Ce n'en est pas un : c'est un système de cutscene
`scene`/`scene-actor` séparé et pré-scripté, utilisant ses propres squelettes réservés aux
cutscenes (ex. `"skel-jak-highres"` dans
`goal_src/jak2/levels/common/warp-gate.gc:1339-1349`) — un acteur affichable différent substitué
dans la cutscene, pas un reskin à chaud du processus interactif `target`. De même, Dark Jak
(`goal_src/jak2/engine/target/target-darkjak.gc:102-160`) n'appelle jamais `initialize-skeleton` —
il garde `skel-jchar` toute sa vie et simule son apparence uniquement via `control scale` et des
astuces de joint-mod. Il n'existait donc aucun précédent dans le jeu de base pour reskinner
`target` lui-même à chaud avant que ce mod n'en ajoute un (`(mp-toggle-skin!)` dans
`goal_src/jak2/pc/multiplayer/mp-manager.gc`).

## 3. Le vrai risque : incompatibilité de la disposition des joints

Le code cosmétique par frame de `target` configure plusieurs `joint-mod` sur des **indices de
joint fixes** du `node-list` de `skel-jchar` — look-at du cou, flex-blend de la tête,
gun-look-at du haut du corps, IK bras/jambes (tous configurés une fois dans `init-target`,
`goal_src/jak2/engine/target/logic-target.gc:3133-3190` environ, juste après l'appel
`initialize-skeleton` pour `skel-jchar`). Si l'on reskin `target` vers un squelette différent dont
la hiérarchie de joints diffère — ex. `skel-crimson-guard-level` (`crimson-guard-lod0-jg`, défini
`goal_src/jak2/levels/common/enemy/guards/crimson-guard-level.gc:12-17`) — ces joint-mods
continuent d'indexer le *nouveau* `node-list` avec les *anciens* numéros. Selon la façon dont le
nombre/l'ordre de joints du nouveau squelette se compare, cela peut animer silencieusement le
mauvais joint, ou sortir des limites du tableau.

Ce risque **ne s'applique qu'au reskin de `target` lui-même** (qui possède tous ces joint-mods).
Un processus sans joint-mod — comme un processus-relais minimal qui ne fait qu'appeler
`ja-no-eval`/`ja-post` — n'a rien à désynchroniser, ce qui est une raison de plus de garder tout
processus reskinnable aussi simple que possible (voir
[22_minimal_networked_stub_process_pattern.md](22_minimal_networked_stub_process_pattern.md)).

**Mitigation, pas encore appliquée de façon exhaustive :** conditionner les mises à jour
cosmétiques dépendantes des indices de joint (dans le post-traitement par frame de `target`) à une
vérification du skin actuellement appliqué, plutôt que d'essayer de remapper des indices pour un
squelette dont la disposition de joints n'a pas été conçue pour eux. Avant d'écrire cette logique
de conditionnement pour un squelette donné, extraire et comparer depuis le REPL le nombre de
joints des `node-list` des deux squelettes — ne pas supposer qu'ils correspondent.

## 4. Étapes de vérification

1. Depuis le REPL, avec `*target*` vivant : `(-> *target* node-list length)` avant et après
   l'appel à `(initialize-skeleton-by-name *target* "skel-crimson-guard-level")`, pour voir si le
   nombre de joints a réellement changé.
2. Observer le personnage en jeu immédiatement après le changement : T-pose, membres étirés ou
   déformés, ou crash — tout cela indique qu'un joint-mod lit désormais un joint qui ne signifie
   plus ce qu'il signifiait avant.
3. Lors du reskin d'un processus autre que `target`, sans joint-mod (ex. `remote-player`), cette
   catégorie de bug ne s'applique pas — vérifier visuellement que le maillage/l'animation a bien
   changé, rien de plus.
