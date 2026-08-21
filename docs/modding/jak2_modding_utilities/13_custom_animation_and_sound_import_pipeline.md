# Jak 2 — Custom Animation & Sound Import Pipeline (End-to-End) / Pipeline Complet d'Import d'Animations et de Sons Custom

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/jak3-jetBoard`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Overview

This is the generalized, end-to-end procedure for two recurring modding needs, distilled from
porting the Jak 3 jetboard's animations and sounds into Jak 2 (`jak2/features/jak3-jetBoard`):

- **Part A** — importing a custom animation onto an existing in-game skeleton, including cross-game
  retargeting (e.g. Jak 3 source animation → Jak 2 skeleton).
- **Part B** — adding a new custom sound that plays reliably at runtime, including one that needs
  continuous per-frame updates (looping / ramping volume).
- **Part C** — the rebuild/iteration mechanisms that make both of the above fast to debug, instead
  of paying for a full engine rebuild + game boot on every attempt.

This complements two existing, narrower tips in this folder: [10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md)
(the `align`/`prejoint` off-by-one pitfall) and [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md)
(the `link-art!` hook). Read this file first for the full pipeline, then those two for the specific
pitfalls they document.

---

## Part A — Importing a Custom Animation

### A1. Gather your source and base assets
- **Base skeleton+mesh**: use the project's own decompiled, already-correct GLB for the target
  character, e.g. `decompiler_out/jak2/levels/common/jakb-lod0.glb`. This guarantees the output
  skin/joint order exactly matches the native `jakb-ag`'s expectations — never hand-build or
  hand-edit a GLTF/GLB from scratch, that was the source of an earlier, much harder-to-diagnose
  boot crash in this same mod.
- **Source animation data**: if porting from another game in this repo (Jak 1/2/3 share the same
  decompiler pipeline), check whether the target character's own decompiled GLB **already contains**
  the animation you want — e.g. `decompiler_out/jak3/levels/common/jakb-lod0.glb` had all ~280+
  native Jak 3 animations already baked in, fully decompressed, with no extra `.go`-decompression
  step required. Always check this first; it saves an entire decompiler pass.
- Confirm the animation's compiled name via the target game's `art-elts.gc` (e.g.
  `goal_src/jak3/engine/data/art-elts.gc`) so you retarget the exact clip you think you are.

### A2. Use (or extend) the retargeting tool
A dedicated, standalone CLI tool — `goalc/retarget_anim/` — exists for this. It:
1. Loads the base GLB (`-b/--base`) as the skeleton + mesh to keep unchanged.
2. Loads the source GLB (`-s/--source`) and pulls out one or more named animations
   (`-a/--anim`, repeatable).
3. Maps joints by **name** between the two skeletons.
4. Writes a new, structurally valid `.glb` (`-o/--output`) via the project's existing `tiny_gltf`
   dependency — never hand-patch GLTF JSON/binary directly.

Flags worth knowing: `--root-joints` (default `align main`) and `--neutral-scale-joints` (default
`board`) — see A3 for why these exist. `--force-180-yaw-anim` exists but should stay unused unless
the gameplay code does **not** already drive the rotation itself (double-check first — forcing it
when gameplay code also rotates will double-rotate the result).

### A3. The retargeting rules (why they matter)
Ground-truthed against real native data before trusting them — do not skip this kind of check when
adapting this tool to a new character/animation pair:
- **Root joints (`align`, `main`)**: copy full translation + rotation (+ scale if present) from the
  source. This is real root motion and must carry over exactly.
- **Every other joint**: copy **rotation only**, retargeted as a delta from the *source's own bind
  pose* (`delta = source_animated * inverse(source_bind)`, then `result = delta * target_bind`) —
  not a raw copy of the source's absolute rotation. Keep the *target's own* bind-pose translation and
  scale. Reason: translation encodes bone length, which differs between skeletons (even
  structurally similar ones across games); copying it directly stretches/dislocates the mesh. The
  delta-from-bind-pose formula degrades to a raw copy when both skeletons happen to share identical
  bind rotations for a joint — verify this by direct comparison rather than assuming either way.
- **Explicitly neutral-scale joints** (e.g. `board`, a joint that must never visually stretch):
  force `(1,1,1)` scale at every keyframe rather than trusting either skeleton's source data.

### A4. Verify the output structurally — before compiling anything
Write a small, throwaway Python script that parses the GLB directly (12-byte header + JSON chunk +
BIN chunk — parseable with just the standard-library `json` and `struct` modules; **no `numpy` is
installed in this environment**, so do not depend on it). Check, per regenerated file:
- Skin joint count and names match the native base exactly.
- Both requested animations are present with the expected channels.
- Root joints have translation channels; forced-neutral joints have constant `(1,1,1)` scale across
  all keyframes.
- If in doubt about visual correctness, implement a minimal forward-kinematics (FK) check in the
  same script (compose per-joint local TRS down the parent chain into world matrices) rather than
  guessing — this is cheap in Python and catches joint-order mistakes immediately, without ever
  touching the compiler or the game.

This step exists specifically to avoid the "compile → boot → crash → guess → repeat" loop; nearly
every real bug in this mod's animation pipeline was actually visible in the raw GLB data once
someone looked with the right check.

### A5. Register the GLB with `build-actor`
In the target game's project file (`goal_src/jak2/game.gp`), a `build-actor` declaration with
`:master-art-group` and `:master-ag-map` bakes target slot indices into the compiled art-group at
compile time. If you're replacing an existing custom import's `.glb` file in place (same declared
name/slots), **no `.gp` changes are needed at all** — only the binary GLB input changes.

Also be aware of `goalc/build_actor/common/build_actor.cpp`'s `kGltfToGameJointOffset` constant
(currently `1`): in-game joint index = GLTF skin joint index + 1, **except** when the GLB's joint 0
is already named `align` (true for our decompiled bases), in which case the tool uses direct
0-indexed mapping instead — see [10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md)
for the full pitfall this caused historically. When identifying "what is joint N", always resolve it
via this rule (or via the `joint-node-index`/`joint-node` compile-time macros in `art-h.gc`, which
resolve by **name** against `*jg-info*`) — never hand-count a raw GLB joint array. Hand-counting
produced at least one confidently-wrong finding in this mod before the offset rule was applied
correctly.

### A6. Link the animations at runtime
`build-actor` output with a skeleton has a `joint-geo` in slot 0, so the engine's own `needs-link?`
check (`joint.gc`) — which only returns true if slot 0 is an `art-joint-anim` — will never trigger
automatically for it. You must special-case your custom art-group's name where `link-art!` is
called. The correct, and only safe, hook is `art-group::relocate` in
`goal_src/jak2/engine/anim/joint.gc` — **never** call `link-art!` from gameplay code (e.g. an
actor's `-init` function): level art-group array state is not guaranteed consistent there, and this
risks a memory crash. See [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) for
the exact hook code.

### A7. Compile and test
Once the GLB structurally checks out, pulling it into the running game is a **pure GOAL-side**
change (no C++ was touched) — `(mi)` is sufficient, see Part C for why a full engine rebuild is not
needed here.

---

## Part B — Adding a Custom Sound

### B1. Place the raw sound and add it to the bank
New sounds are appended into a game `.SBK` bank via `goalc/build_sbk/build_sbk.cpp`'s
`append_sbk_from_dir` (or the equivalent bank-build step for your target bank). Verify the target
bank's on-disk layout preconditions the tool expects (e.g. terminator format) hold, ideally by
parsing the real `.SBK` by hand in Python the same way you'd verify a GLB — the append logic is easy
to get subtly wrong against a real, non-trivial binary layout.

### B2. Make sure the bank can actually be *allocated* at runtime
This is the step that is easy to skip and hardest to diagnose from GOAL code alone, because the
failure surfaces as a generic "out of slots" from C++ code far from where the sound was triggered.
`game/overlord/common/sbank.cpp` (shared by Jak 1 and Jak 2 — **not** Jak 3, which has its own,
structurally different `game/overlord/jak3/sbank.cpp`) has a fixed `N_BANKS` array: a handful of
**dedicated, name-reserved slots** (`common`, `gun`, `board` for Jak 2) plus a small **rotating pool**
of level banks. `AllocateBankName` must explicitly special-case any dedicated bank name you rely on
— a name that isn't special-cased falls through to the rotating-pool loop, which is normally always
full during real gameplay (a level keeps its own rotation occupied), so allocation silently fails
with "out of slots" even though a perfectly good dedicated slot sits unused. If you add sounds to an
existing dedicated bank (like `board`), double-check `AllocateBankName` already special-cases that
exact name — do not assume it does just because the slot exists in `InitBanks`.

### B3. Initialize a persistent sound-id for anything that needs per-frame updates
`sound-play-by-name` (`goal_src/jak2/engine/sound/gsound.gc`) does **not** generate a sound id — it
always returns whatever id (`arg1`) it was given. For a one-shot sound this doesn't matter. For a
sound that needs to be *updated* every frame while it plays (a ramping-volume charge sound, an
engine loop, etc.), the caller must pre-initialize a real, unique id via `(new-sound-id)` **once**,
typically in the owning object's `-init` function, so the audio engine can recognize repeated calls
as updates to the *same* live instance rather than unrelated new requests. If you add a new
per-frame sound trigger, grep the equivalent native code (if it exists in another game version) for
where it initializes its own id — this exact omission (forgetting the `new-sound-id` call when
porting a new sound-id struct field) silently broke a charge-up sound in this mod while every other
sound worked fine, because the failure looks identical to "the sound never triggers" rather than
"the sound triggers but is never recognized as continuing."

### B4. Trigger the sound from GOAL
Standard `(sound-play-by-name (static-sound-name "your-sound") id volume pitch bend (sound-group)
position)` call, same as any native sound trigger. `static-sound-name` packs the literal string at
compile time — nothing dynamic to worry about there.

---

## Part C — Fast, Targeted Rebuild Mechanisms

These are what actually kept iteration fast on this mod — use them in this order of preference:

### C1. Build only the standalone tool, not the whole engine
`retarget_anim` (and similarly `build_sbk`, `build_actor`) are standalone CLI targets, not part of
the game runtime. Build just the one target you're iterating on:
```bash
cmake --build out/build/Release --target retarget_anim --config Release
```
This compiles in seconds, versus a full `gk`/engine rebuild. Only fall back to a full build when
you've actually changed game-runtime C++ (e.g. `game/overlord/**`).

### C2. Iterate offline, with no game boot at all
Run the built tool's `.exe` directly against your GLB inputs to regenerate output — this whole loop
(edit tool code → rebuild tool target → rerun → re-verify structurally per A4) never needs to touch
GOAL or boot the game. Only move to a game boot once the structural verification script is clean.

### C3. Structural verification before compiling GOAL or booting
As in A4: a throwaway Python script against the raw GLB/SBK bytes catches the large majority of
mistakes (wrong joint mapping, wrong scale, malformed bank layout) instantly and for free. Treat a
compile-and-boot cycle as the *expensive* last check, not the first one.

### C4. Know whether you need `(mi)` or a full C++ rebuild
- Changed only `.gc`/GOAL code, or swapped in a new `.glb`/asset with no `.gp`/C++ changes? `(mi)`
  (incremental compile in the REPL, or `./goalc.exe --game jak2 -c "(mi)"` in batch mode) is
  sufficient — see [05_compilation_validation_workflow.md](05_compilation_validation_workflow.md).
- Changed C++ under `game/` (e.g. a `sbank.cpp`/`srpc.cpp` fix)? You need an actual engine rebuild
  (`task build-release` / `task build-debug`) before `(mi)` or a boot will reflect the change —
  `(mi)` alone will not pick up C++ changes.
- Don't guess which one applies — check `git status`/`git diff` for what you actually touched before
  proposing a rebuild command to the user, so you propose the cheapest one that's actually correct.

### C5. Scoped debug logging + targeted log grepping
When a bug can only be diagnosed from real runtime behavior (as both the turn-around and the sound
bugs in this mod ultimately were — static analysis alone was not enough), add temporary,
distinctively-prefixed log lines (e.g. `[board-sound-debug]`) at the specific decision points you
suspect, guarded by a one-time-print flag if the code runs every frame (to avoid drowning the log in
spam). Then grep the resulting `log/jak2.<timestamp>.log` for that exact prefix instead of reading
the whole log. Remove or gate these prefixes once the bug is confirmed fixed.

---

# 🇫🇷 Version Française

## Vue d'Ensemble

Voici la procédure généralisée et complète pour deux besoins de modding récurrents, tirée de
l'import des animations et des sons du jetboard de Jak 3 vers Jak 2
(`jak2/features/jak3-jetBoard`) :

- **Partie A** — importer une animation custom sur un squelette existant en jeu, y compris le
  reciblage inter-jeux (ex : animation source Jak 3 → squelette Jak 2).
- **Partie B** — ajouter un nouveau son custom qui joue de façon fiable en jeu, y compris un son
  nécessitant des mises à jour continues par frame (boucle / volume progressif).
- **Partie C** — les mécanismes de rebuild/itération qui rendent le débogage des deux points
  ci-dessus rapide, plutôt que de payer un rebuild complet du moteur + boot du jeu à chaque essai.

Ce document complète deux fiches existantes plus ciblées dans ce dossier :
[10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md) (le piège du décalage
`align`/`prejoint`) et [09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) (le hook
`link-art!`). Lisez d'abord ce fichier pour le pipeline complet, puis ces deux fiches pour les pièges
spécifiques qu'elles documentent.

---

## Partie A — Importer une Animation Custom

### A1. Rassembler les assets source et de base
- **Squelette+mesh de base** : utilisez le GLB déjà décompilé et correct du projet pour le
  personnage cible, ex : `decompiler_out/jak2/levels/common/jakb-lod0.glb`. Cela garantit que
  l'ordre du skin/des joints en sortie correspond exactement à ce qu'attend le `jakb-ag` natif — ne
  jamais construire ou éditer un GLTF/GLB à la main, c'est la source d'un crash au boot bien plus
  difficile à diagnostiquer plus tôt dans ce même mod.
- **Données d'animation source** : si vous portez depuis un autre jeu de ce dépôt (Jak 1/2/3
  partagent le même pipeline de décompilation), vérifiez d'abord si le GLB déjà décompilé du
  personnage cible **contient déjà** l'animation voulue — ex :
  `decompiler_out/jak3/levels/common/jakb-lod0.glb` contenait déjà les ~280+ animations natives de
  Jak 3, entièrement décompressées, sans étape supplémentaire de décompression du `.go`. Vérifiez
  toujours cela en premier ; cela évite une passe complète de décompilation.
- Confirmez le nom compilé de l'animation via `art-elts.gc` du jeu cible (ex :
  `goal_src/jak3/engine/data/art-elts.gc`) pour être sûr de recibler exactement le clip visé.

### A2. Utiliser (ou étendre) l'outil de reciblage
Un outil CLI autonome dédié — `goalc/retarget_anim/` — existe pour cela. Il :
1. Charge le GLB de base (`-b/--base`) comme squelette + mesh à conserver inchangé.
2. Charge le GLB source (`-s/--source`) et en extrait une ou plusieurs animations nommées
   (`-a/--anim`, répétable).
3. Mappe les joints par **nom** entre les deux squelettes.
4. Écrit un nouveau `.glb` structurellement valide (`-o/--output`) via `tiny_gltf`, déjà une
   dépendance du projet — ne jamais patcher un GLTF JSON/binaire à la main.

Options utiles : `--root-joints` (défaut `align main`) et `--neutral-scale-joints` (défaut `board`)
— voir A3 pour leur raison d'être. `--force-180-yaw-anim` existe mais doit rester inutilisée sauf si
le code de gameplay ne pilote **pas** déjà la rotation lui-même (vérifiez d'abord — la forcer alors
que le code de gameplay tourne aussi le résultat provoque une double rotation).

### A3. Les règles de reciblage (et pourquoi elles comptent)
Vérifiées contre de vraies données natives avant d'être appliquées en confiance — ne sautez jamais ce
type de vérification en adaptant l'outil à une nouvelle paire personnage/animation :
- **Joints racines (`align`, `main`)** : copier translation + rotation complètes (+ scale si
  présent) depuis la source. C'est le mouvement racine réel, il doit être conservé tel quel.
- **Tous les autres joints** : copier **uniquement la rotation**, reciblée comme un delta par
  rapport à la *bind pose propre à la source* (`delta = animée_source * inverse(bind_source)`, puis
  `résultat = delta * bind_cible`) — pas une copie brute de la rotation absolue de la source.
  Conserver la translation et le scale de bind pose **propres à la cible**. Raison : la translation
  encode la longueur des os, qui diffère entre squelettes (même structurellement proches d'un jeu à
  l'autre) ; la copier directement étire/disloque le maillage. La formule delta-depuis-bind-pose
  dégénère en copie brute quand les deux squelettes partagent la même rotation de bind pose pour un
  joint donné — vérifiez-le par comparaison directe plutôt que de le supposer dans un sens ou
  l'autre.
- **Joints explicitement à scale neutre** (ex : `board`, un joint qui ne doit jamais s'étirer
  visuellement) : forcer un scale `(1,1,1)` à chaque keyframe plutôt que de faire confiance aux
  données source de l'un ou l'autre squelette.

### A4. Vérifier structurellement la sortie — avant toute compilation
Écrivez un petit script Python jetable qui parse le GLB directement (en-tête 12 octets + chunk JSON
+ chunk BIN — analysable avec uniquement les modules standards `json` et `struct` ; **`numpy` n'est
pas installé dans cet environnement**, n'en dépendez donc pas). Vérifiez, pour chaque fichier
régénéré :
- Le nombre et les noms des joints du skin correspondent exactement à la base native.
- Les deux animations demandées sont présentes avec les canaux attendus.
- Les joints racines ont des canaux de translation ; les joints à scale forcé ont un scale constant
  `(1,1,1)` sur toutes les keyframes.
- En cas de doute sur la correction visuelle, implémentez une vérification minimale de cinématique
  directe (FK) dans le même script (composer les TRS locaux de chaque joint le long de la chaîne
  parentale en matrices monde) plutôt que de deviner — c'est peu coûteux en Python et cela détecte
  immédiatement les erreurs d'ordre des joints, sans jamais toucher au compilateur ni au jeu.

Cette étape existe spécifiquement pour éviter la boucle « compiler → booter → crash → deviner →
recommencer » ; presque tous les vrais bugs du pipeline d'animation de ce mod étaient en réalité
visibles dans les données GLB brutes une fois qu'on regardait avec la bonne vérification.

### A5. Enregistrer le GLB auprès de `build-actor`
Dans le fichier projet du jeu cible (`goal_src/jak2/game.gp`), une déclaration `build-actor` avec
`:master-art-group` et `:master-ag-map` inscrit les index de slots cibles dans l'art-group compilé à
la compilation. Si vous remplacez sur place le `.glb` d'un import custom déjà existant (même nom/
slots déclarés), **aucune modification du `.gp` n'est nécessaire** — seul le binaire GLB en entrée
change.

Soyez aussi attentif à la constante `kGltfToGameJointOffset` (actuellement `1`) de
`goalc/build_actor/common/build_actor.cpp` : index de joint en jeu = index de joint du skin GLTF + 1,
**sauf** si le joint 0 du GLB s'appelle déjà `align` (vrai pour nos bases décompilées), auquel cas
l'outil utilise un mapping direct indexé à 0 — voir
[10_gltf_retargeting_build_actor.md](10_gltf_retargeting_build_actor.md) pour le piège historique
complet que cela a causé. Pour identifier « quel est le joint N », toujours résoudre via cette règle
(ou via les macros de compilation `joint-node-index`/`joint-node` de `art-h.gc`, qui résolvent par
**nom** via `*jg-info*`) — ne jamais compter à la main les joints d'un GLB brut. Compter à la main a
produit au moins une conclusion fausse avec assurance dans ce mod avant l'application correcte de la
règle de décalage.

### A6. Lier les animations à l'exécution
Une sortie `build-actor` avec squelette a un `joint-geo` au slot 0, donc la vérification native
`needs-link?` du moteur (`joint.gc`) — qui ne renvoie vrai que si le slot 0 est un `art-joint-anim` —
ne se déclenchera jamais automatiquement pour elle. Il faut ajouter un cas spécial pour le nom de
votre art-group custom là où `link-art!` est appelé. Le seul emplacement correct et sûr est
`art-group::relocate` dans `goal_src/jak2/engine/anim/joint.gc` — **ne jamais** appeler `link-art!`
depuis du code de gameplay (ex : la fonction `-init` d'un acteur) : l'état des tableaux d'art-groups
du niveau n'y est pas garanti cohérent, ce qui risque un crash mémoire. Voir
[09_custom_art_groups_link_art.md](09_custom_art_groups_link_art.md) pour le code exact du hook.

### A7. Compiler et tester
Une fois le GLB validé structurellement, l'intégrer au jeu en cours d'exécution est un changement
**purement côté GOAL** (aucun C++ n'a été touché) — `(mi)` suffit, voir la Partie C pour la raison
pour laquelle un rebuild complet du moteur n'est pas nécessaire ici.

---

## Partie B — Ajouter un Son Custom

### B1. Placer le son brut et l'ajouter à la banque
Les nouveaux sons sont ajoutés à une banque `.SBK` du jeu via `append_sbk_from_dir` de
`goalc/build_sbk/build_sbk.cpp` (ou l'étape équivalente pour votre banque cible). Vérifiez que les
préconditions de mise en page sur disque attendues par l'outil pour la banque cible tiennent (ex :
format du terminateur), idéalement en parsant la vraie `.SBK` à la main en Python, de la même façon
que vous vérifieriez un GLB — la logique d'ajout est facile à casser subtilement contre une mise en
page binaire réelle et non triviale.

### B2. S'assurer que la banque peut réellement être *allouée* à l'exécution
C'est l'étape la plus facile à oublier et la plus difficile à diagnostiquer depuis le seul code
GOAL, car l'échec se manifeste comme un « out of slots » générique venant d'un code C++ éloigné du
point de déclenchement du son. `game/overlord/common/sbank.cpp` (partagé par Jak 1 et Jak 2 — **pas**
Jak 3, qui a son propre `game/overlord/jak3/sbank.cpp` structurellement différent) a un tableau
`N_BANKS` fixe : quelques **slots dédiés réservés par nom** (`common`, `gun`, `board` pour Jak 2) plus
un petit **pool tournant** de banques de niveau. `AllocateBankName` doit explicitement traiter comme
cas spécial tout nom de banque dédiée que vous utilisez — un nom non traité comme cas spécial tombe
dans la boucle du pool tournant, normalement toujours pleine en jeu réel (un niveau occupe sa propre
rotation), donc l'allocation échoue silencieusement avec « out of slots » alors qu'un slot dédié
parfaitement valide reste inutilisé. Si vous ajoutez des sons à une banque dédiée existante (comme
`board`), vérifiez que `AllocateBankName` traite déjà ce nom exact comme cas spécial — ne le
supposez pas simplement parce que le slot existe dans `InitBanks`.

### B3. Initialiser un id de son persistant pour tout ce qui nécessite des mises à jour par frame
`sound-play-by-name` (`goal_src/jak2/engine/sound/gsound.gc`) ne génère **pas** d'id de son — il
renvoie toujours l'id (`arg1`) qu'on lui a donné. Pour un son ponctuel, cela n'a pas d'importance.
Pour un son qui doit être *mis à jour* à chaque frame pendant sa lecture (un son de charge à volume
progressif, une boucle moteur, etc.), l'appelant doit pré-initialiser un vrai id unique via
`(new-sound-id)` **une seule fois**, typiquement dans la fonction `-init` de l'objet propriétaire,
afin que le moteur audio puisse reconnaître les appels répétés comme des mises à jour de la *même*
instance vivante plutôt que des requêtes nouvelles et sans rapport. Si vous ajoutez un nouveau
déclenchement de son par frame, cherchez dans le code natif équivalent (s'il existe dans une autre
version du jeu) où il initialise son propre id — cet oubli précis (ne pas appeler `new-sound-id` en
portant un nouveau champ d'id de son) a silencieusement cassé un son de charge dans ce mod alors que
tous les autres sons fonctionnaient, car le symptôme est identique à « le son ne se déclenche
jamais » plutôt qu'à « le son se déclenche mais n'est jamais reconnu comme continu ».

### B4. Déclencher le son depuis GOAL
Appel standard `(sound-play-by-name (static-sound-name "votre-son") id volume pitch bend
(sound-group) position)`, identique à tout déclenchement de son natif. `static-sound-name` empaquette
la chaîne littérale à la compilation — rien de dynamique à surveiller ici.

---

## Partie C — Mécanismes de Rebuild Ciblé et Rapide

Voici ce qui a réellement permis de garder une itération rapide sur ce mod — à utiliser dans cet
ordre de préférence :

### C1. Ne compiler que l'outil autonome, pas tout le moteur
`retarget_anim` (et de même `build_sbk`, `build_actor`) sont des cibles CLI autonomes, pas partie du
runtime du jeu. Ne compilez que la cible sur laquelle vous itérez :
```bash
cmake --build out/build/Release --target retarget_anim --config Release
```
Cela compile en quelques secondes, contre un rebuild complet de `gk`/du moteur. Ne revenez à un
build complet que si vous avez réellement modifié du C++ du runtime du jeu (ex :
`game/overlord/**`).

### C2. Itérer hors-ligne, sans jamais booter le jeu
Lancez directement l'`.exe` de l'outil compilé contre vos GLB en entrée pour régénérer la sortie —
toute cette boucle (modifier le code de l'outil → recompiler la cible → relancer → revérifier
structurellement selon A4) n'a jamais besoin de toucher GOAL ni de booter le jeu. Ne passez à un boot
du jeu qu'une fois le script de vérification structurelle propre.

### C3. Vérification structurelle avant de compiler GOAL ou de booter
Comme en A4 : un script Python jetable contre les octets bruts du GLB/SBK détecte instantanément et
gratuitement la grande majorité des erreurs (mauvais mapping de joint, mauvais scale, mise en page de
banque malformée). Traitez un cycle compile-et-boot comme la vérification *coûteuse* de dernier
recours, pas la première.

### C4. Savoir si `(mi)` suffit ou s'il faut un rebuild C++ complet
- Seul du `.gc`/code GOAL a changé, ou un nouveau `.glb`/asset a été substitué sans changement de
  `.gp`/C++ ? `(mi)` (compilation incrémentale dans le REPL, ou
  `./goalc.exe --game jak2 -c "(mi)"` en mode batch) suffit — voir
  [05_compilation_validation_workflow.md](05_compilation_validation_workflow.md).
- Du C++ sous `game/` a changé (ex : un correctif dans `sbank.cpp`/`srpc.cpp`) ? Un vrai rebuild du
  moteur est nécessaire (`task build-release` / `task build-debug`) avant que `(mi)` ou un boot ne
  reflète le changement — `(mi)` seul ne prendra jamais en compte un changement C++.
- Ne devinez pas lequel s'applique — vérifiez `git status`/`git diff` pour voir ce que vous avez
  réellement modifié avant de proposer une commande de rebuild à l'utilisateur, afin de proposer la
  moins coûteuse qui soit effectivement correcte.

### C5. Logs de debug ciblés + recherche ciblée dans les logs
Quand un bug ne peut être diagnostiqué qu'à partir du comportement réel à l'exécution (comme ce fut
finalement le cas pour le bug du demi-tour et celui du son dans ce mod — l'analyse statique seule ne
suffisait pas), ajoutez des lignes de log temporaires avec un préfixe distinctif (ex :
`[board-sound-debug]`) aux points de décision précis que vous suspectez, protégées par un indicateur
d'affichage unique si le code s'exécute à chaque frame (pour éviter de noyer le log). Cherchez
ensuite ce préfixe exact dans le fichier `log/jak2.<timestamp>.log` généré plutôt que de lire tout le
log. Retirez ou conditionnez ces préfixes une fois le bug confirmé corrigé.
