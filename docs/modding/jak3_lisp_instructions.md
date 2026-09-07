# Jak 3 — OpenGOAL Lisp Instructions / Instructions Lisp OpenGOAL

> **Bilingual reference / Référence bilingue** — [🇬🇧 English](#-english) · [🇫🇷 Français](#-français)
>
> **What this file is / Rôle de ce fichier**
>
> 🇬🇧 The **source of truth** for writing OpenGOAL (GOAL) Lisp for *Jak 3*. Every
> instruction here is **verified** — compiled and seen working. Consult it *before*
> touching any `.gc` file. The GOAL language and most engine systems are shared
> across the trilogy, so the core patterns match Jak 1/2 — the fully worked examples
> and traps live in [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md); this
> file keeps the essentials plus what is specific to Jak 3 (Morph-Gun, Dark/Light
> Jak stages, the secrets menu).
>
> 🇫🇷 La **source de vérité** pour écrire du Lisp OpenGOAL (GOAL) pour *Jak 3*.
> Chaque instruction ici est **vérifiée** — compilée et vue fonctionner. À consulter
> *avant* de toucher un fichier `.gc`. Le langage GOAL et la plupart des systèmes
> moteur sont communs à la trilogie, donc les patterns de base sont identiques à
> Jak 1/2 — les exemples complets et les pièges vivent dans
> [`jak2_lisp_instructions.md`](jak2_lisp_instructions.md) ; ce fichier garde
> l'essentiel plus ce qui est propre à Jak 3 (Morph-Gun, stades Dark/Light Jak, menu
> des secrets).
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
| **`process-focusable`** | Common base for actors the camera/AI can target (Jak 3's default actor base). | Base commune des acteurs ciblables par la caméra/l'IA (base d'acteur par défaut de Jak 3). |
| **`gun-info`** | Structure managing Jak 3's modular arsenal (Morph-Gun + 12 weapon forms). | Structure gérant l'arsenal modulable de Jak 3 (Morph-Gun + 12 formes d'armes). |
| **`vehicle` / `hvehicle`** | Base types for desert off-road vehicles and hovering city craft. | Types de base des véhicules tout-terrain du désert et des véhicules urbains flottants. |
| **`light-jak` / `dark-jak`** | State subsystems governing Jak's eco powers and special forms. | Sous-systèmes d'états gérant les pouvoirs eco et formes spéciales de Jak. |
| **`*target*`** | The player process. | Le processus joueur. |
| **`(mi)`** | REPL command: incremental compile + hot reload. | Commande REPL : compilation incrémentale + hot reload. |

---

## B — Core Lisp patterns (shared across the trilogy) / Patterns Lisp de base (communs à la trilogie)

> 🇬🇧 Identical to Jak 1/2. See
> [`jak2_lisp_instructions.md` §B](jak2_lisp_instructions.md)
> for the extended explanation and traps.
>
> 🇫🇷 Identiques à Jak 1/2. Voir
> [`jak2_lisp_instructions.md` §B](jak2_lisp_instructions.md)
> pour l'explication étendue et les pièges.

### B1 — Custom actor + state machine / Acteur custom + machine à états

```lisp
;; EN: Jak 3 actors usually derive from process-focusable
;; FR: les acteurs Jak 3 dérivent généralement de process-focusable
(deftype my-jak3-actor (process-focusable)
  ((actor-state-flag uint32)
   (energy-level     float))
  (:state-methods idle patrol die))
```

### B2 — Animation macros / Macros d'animation

```lisp
;; EN: advance the current animation, then yield for the frame
;; FR: avancer l'animation courante, puis rendre la main pour la frame
(ja :num! (seek!))
(suspend)
```

- 🇬🇧 Animation pipeline: `merc` / `mips2c` for skinning. Direct joint transforms:
  `(-> self node-list data [index] bone transform)` — indices are skeleton-specific.
- 🇫🇷 Pipeline d'animation : `merc` / `mips2c` pour le skinning. Transformations de
  joints directes : `(-> self node-list data [index] bone transform)` — les indices
  sont propres à un squelette.

### B3 — Weapon system (`gun`) / Système d'armes (`gun`)

```lisp
;; EN: weapon state, ammo and morph are read through the player process
;; FR: l'état de l'arme, les munitions et le morphing s'interrogent via le processus joueur
(when *target*
  (let ((gun (-> *target* gun)))
    ;; EN: access firing modes, ammo counts, morph attachments
    ;; FR: accès aux modes de tir, munitions, pièces de morphing
    ))
```

### B4 — Register a new script (`.gp`) / Enregistrer un nouveau script (`.gp`)

```lisp
;; EN: add to goal_src/jak3/jak3-game.gp, then (mi)
;; FR: ajouter à goal_src/jak3/jak3-game.gp, puis (mi)
(c "custom/my-jak3-mod.gc")
```

### B5 — Debug ▸ Mods toggle / Bascule Debug ▸ Mods

- 🇬🇧 **Follow-up:** the unified `mods-menu.gc` registry exists for Jak 2 today
  ([`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md)). The Jak 3
  port is planned. Until it lands, a Jak 3 mod adds a **mod-slug-prefixed** submenu
  to `goal_src/jak3/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc` and
  documents it in the mod README.
- 🇫🇷 **Suivi :** le registre unifié `mods-menu.gc` existe aujourd'hui pour Jak 2
  ([`docs/modding/tools/mods_debug_menu.md`](tools/mods_debug_menu.md)). Le portage
  Jak 3 est prévu. En attendant, un mod Jak 3 ajoute un sous-menu **préfixé par le
  slug** à `goal_src/jak3/engine/debug/default-menu.gc` / `pc/debug/default-menu-pc.gc`
  et le documente dans le README du mod.

---

## C — Jak 3-specific verified subsystems / Sous-systèmes vérifiés propres à Jak 3

### C1 — Dark Jak stages (`darkjak-stage` bitfield) / Stades de Dark Jak

> 🇬🇧 Dark Jak capabilities are driven by the `darkjak-stage` bitfield enum in
> `target-h.gc`, stored in `(-> self darkjak stage)` and `(-> self darkjak
> want-stage)`.
>
> | Flag | Effect |
> |---|---|
> | `active` | Base Dark Jak form. |
> | `bomb0` / `bomb1` | Dark Bomb / Dark Blast. |
> | `invinc` | Invulnerability. |
> | `invis` | Invisibility (suppresses offensive stages). |
> | `tracking` | Target tracking. |
> | `smack` | Dark Strike. |
> | `giant` | Scaling stage flag. |
>
> 🇫🇷 Les capacités de Dark Jak sont régies par l'énumération de bits `darkjak-stage`
> (`target-h.gc`), stockée dans `(-> self darkjak stage)` et
> `(-> self darkjak want-stage)` (voir table).

- 🇬🇧 Entry validation: `want-to-darkjak?` / `want-to-powerjak?` (in
  `target-darkjak.gc` / `target-lightjak.gc`) check the `(game-feature darkjak)` flag
  in `*setting-control*`, focus tests (no transform while swimming, piloting,
  carrying…), and timing via `(-> self fact darkjak-start-time)`. Transformed
  movement uses the `*darkjak-trans-mods*` surface parameters.
- 🇫🇷 Validation d'entrée : `want-to-darkjak?` / `want-to-powerjak?` (dans
  `target-darkjak.gc` / `target-lightjak.gc`) contrôlent le drapeau
  `(game-feature darkjak)` dans `*setting-control*`, les tests de focus (pas de
  transformation en nageant, en véhicule, en portant un objet…), et la temporisation
  via `(-> self fact darkjak-start-time)`. Le déplacement transformé utilise les
  paramètres de surface `*darkjak-trans-mods*`.
- 🇬🇧 Legacy: the Jak 3 engine still carries the Jak 2 "Dark Giant" animation
  `jakb-darkjak-get-on-fast-ja` and the scale-interp var
  `(-> self darkjak-giant-interp)`, unused by default.
- 🇫🇷 Reliquat : le moteur de Jak 3 embarque encore l'animation « Dark Giant » de
  Jak 2 `jakb-darkjak-get-on-fast-ja` et la variable d'interpolation d'échelle
  `(-> self darkjak-giant-interp)`, inutilisées par défaut.

### C2 — Secrets menu (`game-secrets`) / Menu des secrets

> 🇬🇧 Secrets and cheats are tracked by the `game-secrets` bitfield enum in
> `settings-h.gc`, persisted in `(-> *game-info* secrets)`. Test one with
> `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.
>
> 🇫🇷 Les secrets et cheats sont suivis par l'énumération de bits `game-secrets`
> (`settings-h.gc`), persistée dans `(-> *game-info* secrets)`. Tester un drapeau
> avec `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

- 🇬🇧 Menu entries are `secret-item-option` instances in static arrays like
  `*menu-secrets-array*` (`secrets-menu.gc`). Key fields: `:name` (a `text-id`
  localization string), `:cost` (orb cost, `0` = free), `:secret` (the `game-secrets`
  bit), `:avail-after` (a `game-task-node` prerequisite), `:flags`
  (`secret-item-option-flags`). Custom / unlocalized labels are mapped dynamically
  during option rendering in `progress-draw-pc.gc`.
- 🇫🇷 Les entrées du menu sont des instances `secret-item-option` dans des tableaux
  statiques comme `*menu-secrets-array*` (`secrets-menu.gc`). Champs clés : `:name`
  (chaîne localisée `text-id`), `:cost` (coût en orbes, `0` = gratuit), `:secret`
  (le bit `game-secrets`), `:avail-after` (prérequis `game-task-node`), `:flags`
  (`secret-item-option-flags`). Les libellés custom / non localisés sont gérés
  dynamiquement au rendu de l'option dans `progress-draw-pc.gc`.

### C3 — Powers ⇄ weapons interplay / Interaction pouvoirs ⇄ armes

- 🇬🇧 Modifying `*target*` states can disrupt weapon transitions (`gun-states`) and
  power transitions (`light-jak` / `dark-jak`). Test both after any `target` change.
- 🇫🇷 Modifier les états de `*target*` peut casser les transitions d'armes
  (`gun-states`) et de pouvoirs (`light-jak` / `dark-jak`). Testez les deux après
  tout changement sur `target`.

### C4 — Memory / Mémoire

- 🇬🇧 Kernel entry: `goal_src/jak3/kernel/gcommon.gc`,
  `goal_src/jak3/engine/level/level.gc`. Jak 3 ships the PC memory extension:
  `END_OF_MEMORY = #x20000000` (512 MB); `DEBUG_LEVEL_HEAP_MULT` default `15.0` in
  `level.gc`. Full model: [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).
- 🇫🇷 Entrée kernel : `goal_src/jak3/kernel/gcommon.gc`,
  `goal_src/jak3/engine/level/level.gc`. Jak 3 embarque l'extension mémoire PC :
  `END_OF_MEMORY = #x20000000` (512 Mo) ; `DEBUG_LEVEL_HEAP_MULT` par défaut `15.0`
  dans `level.gc`. Modèle complet : [`engine_generic_concepts.md` §1–4](engine_generic_concepts.md).

---

## D — Lisp-level known pitfalls / Pièges connus au niveau Lisp

- 🇬🇧 **Load order:** parent types before child types in the `.gp`.
- 🇫🇷 **Ordre de chargement :** types parents avant types enfants dans le `.gp`.
- 🇬🇧 **REPL ghost memory:** cold-restart to validate big changes.
- 🇫🇷 **Mémoire fantôme du REPL :** redémarrer à froid pour valider les gros changements.
- 🇬🇧 **A clean compile is not a pass:** boot and read `log/jak3.*.log`.
- 🇫🇷 **Une compilation propre n'est pas une validation :** démarrer et lire `log/jak3.*.log`.
- 🇬🇧 **Native non-regression:** ship changes off by default, behind the mod toggle.
- 🇫🇷 **Non-régression native :** livrer les changements désactivés par défaut, derrière la bascule du mod.

---

## E — ➕ Append new verified entries below / Ajouter les nouvelles entrées vérifiées ci-dessous

> 🇬🇧 One numbered block at a time, same shape as section B/C. **`master-dev` only.**
> 🇫🇷 Un bloc numéroté à la fois, même forme que la section B/C. **`master-dev` uniquement.**

<!-- ➕ APPEND NEW VERIFIED ENTRIES BELOW THIS LINE — master-dev only, one block at a time -->

---

## How to contribute / Comment contribuer

> 🇬🇧 One source of truth: **`master-dev`**. On a mod branch, run
> `task modding-land-doc` then `task modding-sync-docs`. Mod-feature notes go in the
> mod branch's root `README.md`, not here.
>
> 🇫🇷 Une source de vérité : **`master-dev`**. Sur une branche de mod, lancez
> `task modding-land-doc` puis `task modding-sync-docs`. Les notes de fonctionnalité
> de mod vont dans le `README.md` racine de la branche, pas ici.
