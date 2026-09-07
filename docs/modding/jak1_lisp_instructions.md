# Jak 1 — OpenGOAL Lisp Instructions / Instructions Lisp OpenGOAL

> **Bilingual reference / Référence bilingue** — [🇬🇧 English](#-english) · [🇫🇷 Français](#-français)
>
> **What this file is / Rôle de ce fichier**
>
> 🇬🇧 The **source of truth** for writing OpenGOAL (GOAL) Lisp for *Jak 1 — The
> Precursor Legacy*. Every instruction here is **verified** — compiled and seen
> working. Consult it *before* touching any `.gc` file so you never invent an
> instruction. The GOAL language and most engine systems are shared across the
> trilogy, so the core patterns match Jak 2/3 — the fully worked examples and traps
> live in [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md); this file keeps
> the essentials plus what is specific to Jak 1.
>
> 🇫🇷 La **source de vérité** pour écrire du Lisp OpenGOAL (GOAL) pour *Jak 1 — The
> Precursor Legacy*. Chaque instruction ici est **vérifiée** — compilée et vue
> fonctionner. À consulter *avant* de toucher un fichier `.gc`, pour ne jamais
> inventer une instruction. Le langage GOAL et la plupart des systèmes moteur sont
> communs à la trilogie, donc les patterns de base sont identiques à Jak 2/3 — les
> exemples complets et les pièges vivent dans
> [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) ; ce fichier garde
> l'essentiel plus ce qui est propre à Jak 1.
>
> **Also read / À lire aussi:** [`engine_generic_concepts.md`](engine_generic_concepts.md).
>
> **Zero-hallucination contract / Contrat zéro hallucination**
>
> 🇬🇧 Only 100%-verified instructions. Test in the REPL first. New entries land **on
> `master-dev` only** — see [How to contribute](#how-to-contribute--comment-contribuer).
>
> 🇫🇷 Seules les instructions vérifiées à 100 %. Testez d'abord au REPL. Les nouvelles
> entrées sont intégrées **sur `master-dev` uniquement** — voir
> [Comment contribuer](#how-to-contribute--comment-contribuer).

---

<a name="-english"></a>
<a name="-français"></a>

## A — Vocabulary / Vocabulaire

| Term | 🇬🇧 Meaning | 🇫🇷 Signification |
|---|---|---|
| **GOAL** | Naughty Dog's Lisp dialect, compiled to native x86-64 by OpenGOAL. | Le dialecte Lisp de Naughty Dog, compilé en x86-64 natif par OpenGOAL. |
| **`process-drawable`** | Base type for any world entity with a 3D model + transform (`goal_src/jak1/engine/game/process-drawable.gc`). | Type de base de toute entité du monde avec modèle 3D + transformation. |
| **`target`** | The player process (Jak). Global symbol `*target*`. | Le processus joueur (Jak). Symbole global `*target*`. |
| **state** | State-machine node: `:event` handlers, `:code` loop, `:post` step. | Nœud de machine à états : handlers `:event`, boucle `:code`, étape `:post`. |
| **DGO** | On-disk package of compiled objects (`.o`) streamed together on level load. | Paquet disque d'objets compilés (`.o`) streamés d'un bloc au chargement d'un niveau. |
| **`(mi)`** | REPL command: incremental compile + hot reload. | Commande REPL : compilation incrémentale + hot reload. |

---

## B — Core Lisp patterns (shared across the trilogy) / Patterns Lisp de base (communs à la trilogie)

> 🇬🇧 These are identical to Jak 2/3. See
> [`jak2_lisp_instructions.md` §B](jak2_lisp_instructions.md)
> for the extended explanation and traps of each.
>
> 🇫🇷 Identiques à Jak 2/3. Voir
> [`jak2_lisp_instructions.md` §B](jak2_lisp_instructions.md)
> pour l'explication étendue et les pièges de chacun.

### B1 — Custom actor + state machine / Acteur custom + machine à états

```lisp
;; EN: a custom interactive actor deriving from process-drawable
;; FR: un acteur interactif custom dérivant de process-drawable
(deftype my-custom-actor (process-drawable)
  ((custom-counter int32)
   (custom-timer   time-frame))
  (:state-methods idle active))

;; EN: a state — :event reacts to messages, :code is the loop, :post flushes anim
;; FR: un état — :event réagit aux messages, :code est la boucle, :post applique l'anim
(defstate idle (my-custom-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack) (go-virtual active))))
  :code (behavior ()
    (loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))))
  :post ja-post)
```

### B2 — Animation macros / Macros d'animation

| Macro | 🇬🇧 What it does | 🇫🇷 Ce qu'elle fait |
|---|---|---|
| `(ja-no-eval :group! G :num! (seek!) :frame-num 0.0)` | Start an animation from frame 0 on channel 0. | Lance une animation à la frame 0 sur le canal 0. |
| `(ja :num! (seek!))` | Advance the active animation one frame. | Fait avancer l'animation active d'une frame. |
| `(ja-done? 0)` | `#t` when channel 0 reached the clip end. | `#t` quand le canal 0 a fini son clip. |
| `(suspend)` | Yield to the engine for this frame. | Rendre la main au moteur pour cette frame. |

- 🇬🇧 The joint subsystem is `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).
- 🇫🇷 Le sous-système de joints est `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).

### B3 — Sound / Son

```lisp
;; EN: simple SFX / FR: SFX simple
(sound-play "sound-name")

;; EN: positional / entity-bound SFX
;; FR: SFX spatialisé / lié à une entité
(sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
```

### B4 — Collision / Collision

- 🇬🇧 A process's collision lives in its `root` field (`collide-shape` or `trsqv`).
  Surface materials are defined in `goal_src/jak1/engine/collide/pat-h.gc`
  (`pat-surface`).
- 🇫🇷 La collision d'un processus vit dans son champ `root` (`collide-shape` ou
  `trsqv`). Les matières de surface sont définies dans
  `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

### B5 — Register a new script in the project file (`.gp`) / Enregistrer un nouveau script dans le fichier projet (`.gp`)

```lisp
;; EN: 1. put the file under goal_src/jak1/custom/
;;     2. add this line to goal_src/jak1/jak1-game.gp
;;     3. recompile with (mi) in the REPL
;; FR: 1. placer le fichier sous goal_src/jak1/custom/
;;     2. ajouter cette ligne à goal_src/jak1/jak1-game.gp
;;     3. recompiler avec (mi) dans le REPL
(c "custom/my-script.gc")
```

### B6 — Debug ▸ Mods toggle / Bascule Debug ▸ Mods

- 🇬🇧 **Follow-up:** the unified `mods-menu.gc` registry exists for Jak 2 today
  ([`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md)). The Jak 1
  port is planned. Until it lands, a Jak 1 mod adds its toggle to
  `goal_src/jak1/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc` with a
  **mod-slug-prefixed** submenu, and documents it in the mod README so the port can
  absorb it cleanly.
- 🇫🇷 **Suivi :** le registre unifié `mods-menu.gc` existe aujourd'hui pour Jak 2
  ([`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md)). Le portage
  Jak 1 est prévu. En attendant, un mod Jak 1 ajoute sa bascule dans
  `goal_src/jak1/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc` avec un
  sous-menu **préfixé par le slug du mod**, et le documente dans le README du mod
  pour que le portage l'absorbe proprement.

---

## C — Jak 1-specific verified notes / Notes vérifiées propres à Jak 1

### C1 — Memory / Mémoire

- 🇬🇧 Kernel entry points: `goal_src/jak1/kernel/gcommon.gc` and
  `goal_src/jak1/engine/level/level.gc`. `valid?` (in `gcommon.gc`) rejects pointers
  past `END_OF_MEMORY`. `EE_MAIN_MEM_SIZE` is the shared C++ constant
  (`common/goal_constants.h`). Full model:
  [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).
- 🇫🇷 Points d'entrée kernel : `goal_src/jak1/kernel/gcommon.gc` et
  `goal_src/jak1/engine/level/level.gc`. `valid?` (dans `gcommon.gc`) rejette les
  pointeurs au-delà de `END_OF_MEMORY`. `EE_MAIN_MEM_SIZE` est la constante C++
  partagée (`common/goal_constants.h`). Modèle complet :
  [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

### C2 — Compile / validate loop / Boucle compiler / valider

```bash
task set-game-jak1        # EN: pick Jak 1 once / FR: choisir Jak 1 une fois
task repl                 # then (mi)  — EN: incremental compile + hot reload / FR: compilation incrémentale + hot reload
task boot-game            # EN: boot and check the log / FR: démarrer et vérifier le log
```

---

## D — Lisp-level known pitfalls / Pièges connus au niveau Lisp

- 🇬🇧 **Load order:** parent types before child types in the `.gp` include list.
- 🇫🇷 **Ordre de chargement :** types parents avant types enfants dans la liste
  d'inclusion du `.gp`.
- 🇬🇧 **REPL ghost memory:** cold-restart the REPL to validate a large change from
  scratch.
- 🇫🇷 **Mémoire fantôme du REPL :** redémarrer le REPL à froid pour valider un gros
  changement depuis zéro.
- 🇬🇧 **A clean compile is not a pass:** always boot and read `log/jak1.*.log`.
- 🇫🇷 **Une compilation propre n'est pas une validation :** toujours démarrer et lire
  `log/jak1.*.log`.
- 🇬🇧 **Native non-regression:** ship changes off by default, behind the mod toggle.
- 🇫🇷 **Non-régression native :** livrer les changements désactivés par défaut,
  derrière la bascule du mod.

---

## E — ➕ Append new verified entries below / Ajouter les nouvelles entrées vérifiées ci-dessous

> 🇬🇧 One numbered block at a time, same shape as section B/C. **`master-dev` only.**
> 🇫🇷 Un bloc numéroté à la fois, même forme que la section B/C. **`master-dev` uniquement.**

<!-- ➕ APPEND NEW VERIFIED ENTRIES BELOW THIS LINE — master-dev only, one block at a time -->

---

## How to contribute / Comment contribuer

> 🇬🇧 One source of truth: **`master-dev`**. On a mod branch, run
> `task modding-land-doc` (stash → checkout master-dev → pull → append → commit
> `docs(lisp): <slug> (AI-assisted)` → push → return → re-sync), then
> `task modding-sync-docs` back on your branch. Mod-feature notes go in the mod
> branch's root `README.md`, not here.
>
> 🇫🇷 Une source de vérité : **`master-dev`**. Sur une branche de mod, lancez
> `task modding-land-doc` (stash → checkout master-dev → pull → ajout → commit
> `docs(lisp): <slug> (AI-assisted)` → push → retour → resync), puis
> `task modding-sync-docs` de retour sur votre branche. Les notes de fonctionnalité
> de mod vont dans le `README.md` racine de la branche, pas ici.
