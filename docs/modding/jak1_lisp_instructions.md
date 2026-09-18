# Jak 1 — OpenGOAL Lisp Instructions / Instructions Lisp OpenGOAL

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 — The Precursor Legacy (OpenGOAL PC Port)
> - **Source of Truth / Source de Vérité :** `master-dev`
> - **Contract / Contrat :** 100% Verified Lisp instructions — test in REPL before committing.

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [A. Vocabulary](#a--vocabulary) · [B. Core Lisp Patterns](#b--core-lisp-patterns) · [C. Jak 1 Specific Notes](#c--jak-1-specific-verified-notes) · [D. Known Pitfalls](#d--lisp-level-known-pitfalls) · [E. How to Contribute](#how-to-contribute)
> - 🇫🇷 **Français :** [A. Vocabulaire](#a--vocabulaire) · [B. Patterns Lisp de Base](#b--patterns-lisp-de-base) · [C. Notes Propres à Jak 1](#c--notes-spécifiques-à-jak-1) · [D. Pièges Connus](#d--pièges-connus-au-niveau-lisp) · [E. Comment Contribuer](#comment-contribuer)

---

# 🇬🇧 English Version

## What this file is
The **source of truth** for writing OpenGOAL (GOAL) Lisp for *Jak 1 — The Precursor Legacy*. Every instruction here is **verified** — compiled and seen working. Consult it *before* touching any `.gc` file so you never invent an instruction. The GOAL language and most engine systems are shared across the trilogy, so the core patterns match Jak 2/3 — the fully worked examples and traps live in [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md); this file keeps the essentials plus what is specific to Jak 1.

**Also read:** [`engine_generic_concepts.md`](engine_generic_concepts.md).

---

## A — Vocabulary

| Term | Meaning |
|---|---|
| **GOAL** | Naughty Dog's Lisp dialect, compiled to native x86-64 by OpenGOAL. |
| **`process-drawable`** | Base type for any world entity with a 3D model + transform (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | The player process (Jak). Global symbol `*target*`. |
| **state** | State-machine node: `:event` handlers, `:code` loop, `:post` step. |
| **DGO** | On-disk package of compiled objects (`.o`) streamed together on level load. |
| **`(mi)`** | REPL command: incremental compile + hot reload. |

---

## B — Core Lisp patterns

### B1 — Custom actor + state machine

```lisp
;; a custom interactive actor deriving from process-drawable
(deftype my-custom-actor (process-drawable)
  ((custom-counter int32)
   (custom-timer   time-frame))
  (:state-methods idle active))

;; a state — :event reacts to messages, :code is the loop, :post flushes anim
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

### B2 — Animation macros

| Macro | What it does |
|---|---|
| `(ja-no-eval :group! G :num! (seek!) :frame-num 0.0)` | Start an animation from frame 0 on channel 0. |
| `(ja :num! (seek!))` | Advance the active animation one frame. |
| `(ja-done? 0)` | `#t` when channel 0 reached the clip end. |
| `(suspend)` | Yield to the engine for this frame. |

- The joint subsystem is `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).

### B3 — Sound

```lisp
;; simple SFX
(sound-play "sound-name")

;; positional / entity-bound SFX
(sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
```

### B4 — Collision

- A process's collision lives in its `root` field (`collide-shape` or `trsqv`). Surface materials are defined in `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

### B5 — Register a new script in the project file (`.gp`)

```lisp
;; 1. put the file under goal_src/jak1/custom/
;; 2. add this line to goal_src/jak1/jak1-game.gp
;; 3. recompile with (mi) in the REPL
(c "custom/my-script.gc")
```

### B6 — In-game Mods toggle

- The unified `mods-menu.gc` registry is live for **Jak 2 and Jak 3** ([`docs/modding/tools/mods_menu.md`](tools/mods_menu.md)). Jak 1 is **not ported**: it has no `popup-menu` in `pc/util/`, and appending to its debug root menu at link time segfaults the boot. Until a port lands, a Jak 1 mod adds its toggle to `goal_src/jak1/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc` with a **mod-slug-prefixed** submenu, and documents it in the mod README — stating explicitly that the toggle is **debug-only**.

---

## C — Jak 1-specific verified notes

### C1 — Memory
- Kernel entry points: `goal_src/jak1/kernel/gcommon.gc` and `goal_src/jak1/engine/level/level.gc`. `valid?` rejects pointers past `END_OF_MEMORY`. `EE_MAIN_MEM_SIZE` is the shared C++ constant (`common/goal_constants.h`). Full model: [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

### C2 — Compile / validate loop
```bash
task set-game-jak1        # pick Jak 1 once
task repl                 # then (mi) — incremental compile + hot reload
task boot-game            # boot and check the log
```

---

## D — Lisp-level known pitfalls

- **Load order:** parent types before child types in the `.gp` include list.
- **REPL ghost memory:** cold-restart the REPL to validate a large change from scratch.
- **A clean compile is not a pass:** always boot and read `log/jak1.*.log`.
- **Native non-regression:** ship changes off by default, behind the mod toggle.

---

## How to contribute

One source of truth: **`master-dev`**. On a mod branch, run `task modding-land-doc -- --file docs/modding/jak1_lisp_instructions.md --message "..." --push`, then `task modding-sync-docs` back on your branch.

---

# 🇫🇷 Version Française

## Rôle de ce fichier
La **source de vérité** pour écrire du Lisp OpenGOAL (GOAL) pour *Jak 1 — The Precursor Legacy*. Chaque instruction ici est **vérifiée** — compilée et vue fonctionner. À consulter *avant* de toucher un fichier `.gc`, pour ne jamais inventer une instruction. Le langage GOAL et la plupart des systèmes moteur sont communs à la trilogie, donc les patterns de base sont identiques à Jak 2/3 — les exemples complets et les pièges vivent dans [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) ; ce fichier garde l'essentiel plus ce qui est propre à Jak 1.

**À lire aussi :** [`engine_generic_concepts.md`](engine_generic_concepts.md).

---

## A — Vocabulaire

| Terme | Signification |
|---|---|
| **GOAL** | Le dialecte Lisp de Naughty Dog, compilé en x86-64 natif par OpenGOAL. |
| **`process-drawable`** | Type de base de toute entité du monde avec modèle 3D + transformation (`goal_src/jak1/engine/game/process-drawable.gc`). |
| **`target`** | Le processus joueur (Jak). Symbole global `*target*`. |
| **state** | Nœud de machine à états : handlers `:event`, boucle `:code`, étape `:post`. |
| **DGO** | Paquet disque d'objets compilés (`.o`) streamés d'un bloc au chargement d'un niveau. |
| **`(mi)`** | Commande REPL : compilation incrémentale + hot reload. |

---

## B — Patterns Lisp de base

### B1 — Acteur custom + machine à états

```lisp
;; un acteur interactif custom dérivant de process-drawable
(deftype my-custom-actor (process-drawable)
  ((custom-counter int32)
   (custom-timer   time-frame))
  (:state-methods idle active))

;; un état — :event réagit aux messages, :code est la boucle, :post applique l'anim
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

### B2 — Macros d'animation

| Macro | Ce qu'elle fait |
|---|---|
| `(ja-no-eval :group! G :num! (seek!) :frame-num 0.0)` | Lance une animation à la frame 0 sur le canal 0. |
| `(ja :num! (seek!))` | Fait avancer l'animation active d'une frame. |
| `(ja-done? 0)` | `#t` quand le canal 0 a fini son clip. |
| `(suspend)` | Rendre la main au moteur pour cette frame. |

- Le sous-système de joints est `cspace` / `joint-control` (`goal_src/jak1/engine/anim/joint.gc`).

### B3 — Son

```lisp
;; SFX simple
(sound-play "sound-name")

;; SFX spatialisé / lié à une entité
(sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
```

### B4 — Collision

- La collision d'un processus vit dans son champ `root` (`collide-shape` ou `trsqv`). Les matières de surface sont définies dans `goal_src/jak1/engine/collide/pat-h.gc` (`pat-surface`).

### B5 — Enregistrer un nouveau script dans le fichier projet (`.gp`)

```lisp
;; 1. placer le fichier sous goal_src/jak1/custom/
;; 2. ajouter cette ligne à goal_src/jak1/jak1-game.gp
;; 3. recompiler avec (mi) dans le REPL
(c "custom/my-script.gc")
```

### B6 — Bascule Mods en jeu

- Le registre unifié `mods-menu.gc` est actif pour **Jak 2 et Jak 3** ([`docs/modding/tools/mods_menu.md`](tools/mods_menu.md)). Jak 1 n'est **pas porté** : il n'a pas de `popup-menu` dans `pc/util/`, et ajouter une entrée à son menu debug racine au link fait segfaulter le boot. En attendant, un mod Jak 1 ajoute sa bascule dans `goal_src/jak1/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc` avec un sous-menu **préfixé par le slug du mod**, et le documente dans le README du mod — en précisant que la bascule est **debug-only**.

---

## C — Notes spécifiques à Jak 1

### C1 — Mémoire
- Points d'entrée kernel : `goal_src/jak1/kernel/gcommon.gc` et `goal_src/jak1/engine/level/level.gc`. `valid?` rejette les pointeurs au-delà de `END_OF_MEMORY`. `EE_MAIN_MEM_SIZE` est la constante C++ partagée (`common/goal_constants.h`). Modèle complet : [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

### C2 — Boucle compiler / valider
```bash
task set-game-jak1        # choisir Jak 1 une fois
task repl                 # puis (mi) — compilation incrémentale + hot reload
task boot-game            # démarrer et vérifier le log
```

---

## D — Pièges connus au niveau Lisp

- **Ordre de chargement :** types parents avant types enfants dans la liste d'inclusion du `.gp`.
- **Mémoire fantôme du REPL :** redémarrer le REPL à froid pour valider un gros changement depuis zéro.
- **Une compilation propre n'est pas une validation :** toujours démarrer et lire `log/jak1.*.log`.
- **Non-régression native :** livrer les changements désactivés par défaut, derrière la bascule du mod.

---

## Comment contribuer

Une source de vérité : **`master-dev`**. Sur une branche de mod, lancez `task modding-land-doc -- --file docs/modding/jak1_lisp_instructions.md --message "..." --push`, puis `task modding-sync-docs` de retour sur votre branche.
