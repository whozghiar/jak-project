# Jak 3 — OpenGOAL Lisp Instructions / Instructions Lisp OpenGOAL

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 3 (OpenGOAL PC Port)
> - **Source of Truth / Source de Vérité :** `master-dev`
> - **Contract / Contrat :** 100% Verified Lisp instructions — test in REPL before committing.

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [A. Vocabulary](#a--vocabulary) · [B. Core Lisp Patterns](#b--core-lisp-patterns) · [C. Jak 3 Subsystems](#c--jak-3-specific-verified-subsystems) · [D. Known Pitfalls](#d--lisp-level-known-pitfalls) · [E. How to Contribute](#how-to-contribute)
> - 🇫🇷 **Français :** [A. Vocabulaire](#a--vocabulaire) · [B. Patterns Lisp de Base](#b--patterns-lisp-de-base) · [C. Sous-Systèmes Jak 3](#c--sous-systèmes-vérifiés-propres-à-jak-3) · [D. Pièges Connus](#d--pièges-connus-au-niveau-lisp) · [E. Comment Contribuer](#comment-contribuer)

---

# 🇬🇧 English Version

## What this file is
The **source of truth** for writing OpenGOAL (GOAL) Lisp for *Jak 3*. Every instruction here is **verified** — compiled and seen working. Consult it *before* touching any `.gc` file. The GOAL language and most engine systems are shared across the trilogy, so the core patterns match Jak 1/2 — the fully worked examples and traps live in [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md); this file keeps the essentials plus what is specific to Jak 3 (Morph-Gun, Dark/Light Jak stages, secrets menu).

**Also read:** [`engine_generic_concepts.md`](engine_generic_concepts.md).

---

## A — Vocabulary

| Term | Meaning |
|---|---|
| **GOAL** | Naughty Dog's Lisp dialect, compiled to native x86-64 by OpenGOAL. |
| **`process-focusable`** | Common base for actors the camera/AI can target (Jak 3's default actor base). |
| **`gun-info`** | Structure managing Jak 3's modular arsenal (Morph-Gun + 12 weapon forms). |
| **`vehicle` / `hvehicle`** | Base types for desert off-road vehicles and hovering city craft. |
| **`light-jak` / `dark-jak`** | State subsystems governing Jak's eco powers and special forms. |
| **`*target*`** | The player process. |
| **`(mi)`** | REPL command: incremental compile + hot reload. |

---

## B — Core Lisp patterns

### B1 — Custom actor + state machine

```lisp
;; Jak 3 actors usually derive from process-focusable
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag uint32)
   (energy-level     float))
  (:state-methods idle patrol die))
```

### B2 — Animation macros

```lisp
;; advance current animation, then yield for the frame
(ja :num! (seek!))
(suspend)
```

- Animation pipeline: `merc` / `mips2c` for skinning. Direct joint transforms: `(-> self node-list data [index] bone transform)` — indices are skeleton-specific.

### B3 — Weapon system (`gun`)

```lisp
;; weapon state, ammo and morph are read through the player process
(when *target*
  (let ((gun (-> *target* gun)))
    ;; access firing modes, ammo counts, morph attachments
    ))
```

### B4 — Register a new script (`.gp`)

```lisp
;; add to goal_src/jak3/jak3-game.gp, then (mi)
(c "custom/my-jak3-mod.gc")
```

### B5 — In-game Mods toggle

- The unified registry is **live for Jak 3** in `goal_src/jak3/pc/features/mods-menu.gc`. Register with `(mods-menu-register "<slug>" builder)` from one of your mod's own `.gc` files; the menu opens in-game with **L3 + SELECT** and works in a retail boot. Never add `(declare-file (debug))` to that file. Full guide: [`docs/modding/tools/mods_menu.md`](tools/mods_menu.md).

---

## C — Jak 3-specific verified subsystems

### C1 — Dark Jak stages (`darkjak-stage` bitfield)

Dark Jak capabilities are driven by the `darkjak-stage` bitfield enum in `target-h.gc`, stored in `(-> self darkjak stage)` and `(-> self darkjak want-stage)`:

| Flag | Effect |
|---|---|
| `active` | Base Dark Jak form. |
| `bomb0` / `bomb1` | Dark Bomb / Dark Blast. |
| `invinc` | Invulnerability. |
| `invis` | Invisibility (suppresses offensive stages). |
| `tracking` | Target tracking. |
| `smack` | Dark Strike. |
| `giant` | Scaling stage flag. |

- Entry validation: `want-to-darkjak?` / `want-to-powerjak?` (in `target-darkjak.gc` / `target-lightjak.gc`) check the `(game-feature darkjak)` flag in `*setting-control*`, focus tests, and timing. Transformed movement uses `*darkjak-trans-mods*` surface parameters.
- Legacy: the Jak 3 engine still carries the Jak 2 "Dark Giant" animation `jakb-darkjak-get-on-fast-ja` and the scale-interp var `(-> self darkjak-giant-interp)`.

### C2 — Secrets menu (`game-secrets`)

Secrets and cheats are tracked by the `game-secrets` bitfield enum in `settings-h.gc`, persisted in `(-> *game-info* secrets)`. Test one with `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

- Menu entries are `secret-item-option` instances in static arrays like `*menu-secrets-array*` (`secrets-menu.gc`). Custom / unlocalized labels are mapped dynamically during option rendering in `progress-draw-pc.gc`.

### C3 — Powers ⇄ weapons interplay

Modifying `*target*` states can disrupt weapon transitions (`gun-states`) and power transitions (`light-jak` / `dark-jak`). Test both after any `target` change.

### C4 — Memory

Kernel entry: `goal_src/jak3/kernel/gcommon.gc`, `goal_src/jak3/engine/level/level.gc`. Jak 3 ships the PC memory extension: `END_OF_MEMORY = #x20000000` (512 MB); `DEBUG_LEVEL_HEAP_MULT` default `15.0` in `level.gc`. Full model: [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

---

## D — Lisp-level known pitfalls

- **Load order:** parent types before child types in the `.gp`.
- **REPL ghost memory:** cold-restart to validate big changes.
- **A clean compile is not a pass:** boot and read `log/jak3.*.log`.
- **Native non-regression:** ship changes off by default, behind the mod toggle.

---

## How to contribute

One source of truth: **`master-dev`**. On a mod branch, run `task modding-land-doc` then `task modding-sync-docs`. Mod-feature notes go in the mod branch's root `README.md`, not here.

---

# 🇫🇷 Version Française

## Rôle de ce fichier
La **source de vérité** pour écrire du Lisp OpenGOAL (GOAL) pour *Jak 3*. Chaque instruction ici est **vérifiée** — compilée et vue fonctionner. À consulter *avant* de toucher un fichier `.gc`. Le langage GOAL et la plupart des systèmes moteur sont communs à la trilogie, donc les patterns de base sont identiques à Jak 1/2 — les exemples complets et les pièges vivent dans [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) ; ce fichier garde l'essentiel plus ce qui est propre à Jak 3 (Morph-Gun, stades Dark/Light Jak, menu des secrets).

**À lire aussi :** [`engine_generic_concepts.md`](engine_generic_concepts.md).

---

## A — Vocabulaire

| Terme | Signification |
|---|---|
| **GOAL** | Le dialecte Lisp de Naughty Dog, compilé en x86-64 natif par OpenGOAL. |
| **`process-focusable`** | Base commune des acteurs ciblables par la caméra/l'IA (base d'acteur par défaut de Jak 3). |
| **`gun-info`** | Structure gérant l'arsenal modulable de Jak 3 (Morph-Gun + 12 formes d'armes). |
| **`vehicle` / `hvehicle`** | Types de base des véhicules tout-terrain du désert et des véhicules urbains flottants. |
| **`light-jak` / `dark-jak`** | Sous-systèmes d'états gérant les pouvoirs eco et formes spéciales de Jak. |
| **`*target*`** | Le processus joueur. |
| **`(mi)`** | Commande REPL : compilation incrémentale + hot reload. |

---

## B — Patterns Lisp de base

### B1 — Acteur custom + machine à états

```lisp
;; les acteurs Jak 3 dérivent généralement de process-focusable
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag uint32)
   (energy-level     float))
  (:state-methods idle patrol die))
```

### B2 — Macros d'animation

```lisp
;; avancer l'animation courante, puis rendre la main pour la frame
(ja :num! (seek!))
(suspend)
```

- Pipeline d'animation : `merc` / `mips2c` pour le skinning. Transformations de joints directes : `(-> self node-list data [index] bone transform)` — les indices sont propres à un squelette.

### B3 — Système d'armes (`gun`)

```lisp
;; l'état de l'arme, les munitions et le morphing s'interrogent via le processus joueur
(when *target*
  (let ((gun (-> *target* gun)))
    ;; accès aux modes de tir, munitions, pièces de morphing
    ))
```

### B4 — Enregistrer un nouveau script (`.gp`)

```lisp
;; ajouter à goal_src/jak3/jak3-game.gp, puis (mi)
(c "custom/my-jak3-mod.gc")
```

### B5 — Bascule Mods en jeu

- Le registre unifié est **actif pour Jak 3** dans `goal_src/jak3/pc/features/mods-menu.gc`. On enregistre avec `(mods-menu-register "<slug>" builder)` depuis un `.gc` du mod ; le menu s'ouvre en jeu avec **L3 + SELECT** et fonctionne en boot retail. N'ajoutez jamais `(declare-file (debug))` à ce fichier. Guide complet : [`docs/modding/tools/mods_menu.md`](tools/mods_menu.md).

---

## C — Sous-systèmes vérifiés propres à Jak 3

### C1 — Stades de Dark Jak (`darkjak-stage` bitfield)

Les capacités de Dark Jak sont régies par l'énumération de bits `darkjak-stage` (`target-h.gc`), stockée dans `(-> self darkjak stage)` et `(-> self darkjak want-stage)` :

| Drapeau | Effet |
|---|---|
| `active` | Forme de base Dark Jak. |
| `bomb0` / `bomb1` | Dark Bomb / Dark Blast. |
| `invinc` | Invulnérabilité. |
| `invis` | Invisibilité (supprime les attaques offensives). |
| `tracking` | Ciblage automatique. |
| `smack` | Dark Strike. |
| `giant` | Drapeau de transformation géante. |

- Validation d'entrée : `want-to-darkjak?` / `want-to-powerjak?` contrôlent le drapeau `(game-feature darkjak)` dans `*setting-control*`, les tests de focus et la temporisation.
- Reliquat : le moteur de Jak 3 embarque encore l'animation « Dark Giant » de Jak 2 `jakb-darkjak-get-on-fast-ja` et la variable `(-> self darkjak-giant-interp)`.

### C2 — Menu des secrets (`game-secrets`)

Les secrets et cheats sont suivis par l'énumération de bits `game-secrets` (`settings-h.gc`), persistée dans `(-> *game-info* secrets)`. Tester un drapeau avec `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

- Les entrées du menu sont des instances `secret-item-option` dans des tableaux statiques comme `*menu-secrets-array*` (`secrets-menu.gc`).

### C3 — Interaction pouvoirs ⇄ armes

Modifier les états de `*target*` peut casser les transitions d'armes (`gun-states`) et de pouvoirs (`light-jak` / `dark-jak`). Testez les deux après tout changement sur `target`.

### C4 — Mémoire

Entrée kernel : `goal_src/jak3/kernel/gcommon.gc`, `goal_src/jak3/engine/level/level.gc`. Jak 3 embarque l'extension mémoire PC : `END_OF_MEMORY = #x20000000` (512 Mo) ; `DEBUG_LEVEL_HEAP_MULT` par défaut `15.0` dans `level.gc`. Modèle complet : [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

---

## D — Pièges connus au niveau Lisp

- **Ordre de chargement :** types parents avant types enfants dans le `.gp`.
- **Mémoire fantôme du REPL :** redémarrer à froid pour valider les gros changements.
- **Une compilation propre n'est pas une validation :** démarrer et lire `log/jak3.*.log`.
- **Non-régression native :** livrer les changements désactivés par défaut, derrière la bascule du mod.

---

## Comment contribuer

Une source de vérité : **`master-dev`**. Sur une branche de mod, lancez `task modding-land-doc` puis `task modding-sync-docs`. Les notes de fonctionnalité de mod vont dans le `README.md` racine de la branche, pas ici.
