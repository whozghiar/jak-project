# Unified "Mods" Debug Menu Architecture / Architecture du Menu Debug « Mods » Unifié

> **Bilingual reference / Référence bilingue** — [🇬🇧 English](#-english-version) · [🇫🇷 Version Française](#-version-française)
>
> **Status / Statut**
>
> 🇬🇧 The `mods-menu.gc` registry is **live on `master-dev` for Jak 2**
> (`goal_src/jak2/pc/debug/mods-menu.gc`, wired in `goal_src/jak2/dgos/game.gd`).
> The Jak 1 and Jak 3 ports are a tracked follow-up — until they land, Jak 1/3 mods
> add a mod-slug-prefixed submenu to their `default-menu*.gc` and document it in the
> mod README so the port can absorb it cleanly.
>
> 🇫🇷 Le registre `mods-menu.gc` est **actif sur `master-dev` pour Jak 2**
> (`goal_src/jak2/pc/debug/mods-menu.gc`, câblé dans `goal_src/jak2/dgos/game.gd`).
> Les portages Jak 1 et Jak 3 sont un suivi planifié — en attendant, les mods Jak 1/3
> ajoutent un sous-menu préfixé par leur slug dans leur `default-menu*.gc` et le
> documentent dans le README du mod pour que le portage l'absorbe proprement.

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## 1. Problem

Every mod branch wants a few debug toggles in-game. Historically each branch
edited `goal_src/jak2/engine/debug/default-menu.gc` or
`goal_src/jak2/pc/debug/default-menu-pc.gc` directly. That causes:

- **Symbol collisions** — two branches add a `"Mods"` submenu, or both define a
  pick-func called `dm-toggle`.
- **Permanent merge conflicts** — the shared menu files change on every branch
  whenever they are rebased onto `master-dev`.

## 2. Solution — one tab + a runtime registry

`goal_src/jak2/pc/debug/mods-menu.gc` (registered once in
`goal_src/jak2/dgos/game.gd`, right before `default-menu-pc.o`) installs a single
root tab and a small registry:

```
Debug ▸ Mods ▸ [mod-slug] ▸ [variant / sub-module] ▸ [options & toggles]
```

A mod **never edits `mods-menu.gc`**. It calls, from its own already-compiled
`.gc` file:

```lisp
(mods-menu-register "<mod-slug>" <builder-fn>)
```

The registry:
- de-duplicates by slug (hot-reload safe — re-registering replaces in place);
- sorts entries alphabetically on every rebuild, so **branch merge order never
  changes what the player sees**;
- keeps a permanent `About / how to register` row so the submenu is never empty
  (the framework refuses to open an empty submenu).

### Public API

| Symbol | Signature | Purpose |
| --- | --- | --- |
| `mods-menu-register` | `(function string (function debug-menu-context debug-menu-node) none)` | Register/replace one mod's submenu builder. |
| `mods-menu-rebuild` | `(function none)` | Force a rebuild from the registry (rarely called by hand). |

`mods-menu.gc` is `(declare-file (debug))` — it is stripped from release builds
exactly like the rest of the menu code.

## 3. The standardised template

Full copy-paste file: [`../templates/mod_debug_menu.template.gc`](../templates/mod_debug_menu.template.gc)

```lisp
;;-*-Lisp-*-
(in-package goal)
(declare-file (debug))

;; --- 1. prefixed config state (one symbol per option; `value` slot = the bool) ---
(define *mod-crimson-blueguard-enable*        #f)
(define *mod-crimson-blueguard-city-peaceful* #f)

;; --- 2. pick-function: side effects on `press` only, always return the bool ---
(defun mod-crimson-blueguard-city-peaceful-pick ((arg0 symbol) (arg1 debug-menu-msg))
  (case arg1
    (((debug-menu-msg press))
     (set! (-> arg0 value) (not (-> arg0 value)))
     (when *traffic-manager*
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-0))
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-1))
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-2)))))
  (-> arg0 value))

;; --- 3. builder: cascade slug ▸ variant ▸ options ---
(defun mod-crimson-blueguard-build-menu ((ctx debug-menu-context))
  (debug-menu-make-from-template ctx
    '(menu "crimson-blueguard"
       (flag "Enable" *mod-crimson-blueguard-enable* dm-boolean-toggle-pick-func)
       (menu "city-peaceful"
         (flag "Enable / Disable" *mod-crimson-blueguard-city-peaceful*
               mod-crimson-blueguard-city-peaceful-pick)))))

;; --- 4. register (top-level, runs at file load) ---
(mods-menu-register "crimson-blueguard" mod-crimson-blueguard-build-menu)
```

### Naming rules (what prevents collisions)

| Item | Convention | Example |
| --- | --- | --- |
| config var | `*mod-<slug>-<option>*` | `*mod-crimson-blueguard-city-peaceful*` |
| pick func | `mod-<slug>-<option>-pick` | `mod-crimson-blueguard-city-peaceful-pick` |
| builder | `mod-<slug>-build-menu` | `mod-crimson-blueguard-build-menu` |
| menu label | the bare slug | `"crimson-blueguard"` |

## 4. Wiring the template into a build

Two options:

1. **No new file** — paste steps 1–4 into an existing mod `.gc` that is already
   in a `.gd`.
2. **Dedicated file** — create `goal_src/jak2/.../<slug>-menu.gc` and add
   `"<slug>-menu.o"` to your level or game `.gd` **after `mods-menu.o`** (so
   `mods-menu-register` is already defined at compile time).

Then hot-reload from the REPL:

```lisp
(mi)
```

Open the debug menu in-game and navigate to `Mods ▸ <slug>`.

## 5. Pitfalls

- **Do the work in `press`, not `update`.** The menu sends `update` every few
  frames to refresh the ✓ checkmark. Allocating or spawning there will thrash
  the heap. The pick-func's tail must just `(-> arg0 value)`.
- **Never re-spawn a faction by hand from a toggle.** Send
  `'deactivate-by-type` to `*traffic-manager*` and let the traffic engine
  recycle the existing actor slots. `send-event` uses a stack message block —
  no heap allocation, so nothing is overwritten when the player crosses a
  district boundary mid-toggle.
- **Guard managers that may be absent.** `*traffic-manager*` is `#f` outside the
  city — always `(when *traffic-manager* ...)`.
- **Builders must be pure.** `mod-<slug>-build-menu` is re-run on every rebuild;
  it must only build and return a node.
- **Reloading `mods-menu.gc` itself** resets the registry. Re-run `(mi)` (which
  re-runs every mod's top-level `mods-menu-register`) or reboot. Reloading a mod
  file on its own is always safe.
- **`.o` order in the `.gd`.** Your menu file's `.o` must come after
  `mods-menu.o`.

---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## 1. Problème

Chaque branche de mod veut quelques bascules (toggles) de debug en jeu.
Historiquement chaque branche éditait directement
`goal_src/jak2/engine/debug/default-menu.gc` ou
`goal_src/jak2/pc/debug/default-menu-pc.gc`. Conséquences :

- **Collisions de symboles** — deux branches ajoutent un sous-menu `"Mods"`, ou
  définissent toutes deux une pick-func nommée `dm-toggle`.
- **Conflits de fusion permanents** — les fichiers de menu partagés changent à
  chaque rebase d'une branche sur `master-dev`.

## 2. Solution — un onglet + un registre à l'exécution

`goal_src/jak2/pc/debug/mods-menu.gc` (déclaré une seule fois dans
`goal_src/jak2/dgos/game.gd`, juste avant `default-menu-pc.o`) installe un unique
onglet racine et un petit registre :

```
Debug ▸ Mods ▸ [slug-du-mod] ▸ [variante / sous-module] ▸ [options & bascules]
```

Un mod **n'édite jamais `mods-menu.gc`**. Il appelle, depuis son propre fichier
`.gc` déjà compilé :

```lisp
(mods-menu-register "<slug-du-mod>" <fonction-builder>)
```

Le registre :
- déduplique par slug (compatible hot-reload — un ré-enregistrement remplace sur
  place) ;
- trie les entrées alphabétiquement à chaque reconstruction, donc **l'ordre de
  fusion des branches ne change jamais ce que voit le joueur** ;
- conserve une ligne permanente `About / how to register` pour que le sous-menu
  ne soit jamais vide (le framework refuse d'ouvrir un sous-menu vide).

### API publique

| Symbole | Signature | Rôle |
| --- | --- | --- |
| `mods-menu-register` | `(function string (function debug-menu-context debug-menu-node) none)` | Enregistre/remplace le builder de sous-menu d'un mod. |
| `mods-menu-rebuild` | `(function none)` | Force une reconstruction depuis le registre (rarement appelé à la main). |

`mods-menu.gc` est en `(declare-file (debug))` — il est retiré des builds release
comme le reste du code de menu.

## 3. Le template standardisé

Fichier complet à copier-coller :
[`../templates/mod_debug_menu.template.gc`](../templates/mod_debug_menu.template.gc)

```lisp
;;-*-Lisp-*-
(in-package goal)
(declare-file (debug))

;; --- 1. état de config préfixé (un symbole par option ; slot `value` = le booléen) ---
(define *mod-crimson-blueguard-enable*        #f)
(define *mod-crimson-blueguard-city-peaceful* #f)

;; --- 2. pick-function : effets de bord sur `press` uniquement, toujours renvoyer le booléen ---
(defun mod-crimson-blueguard-city-peaceful-pick ((arg0 symbol) (arg1 debug-menu-msg))
  (case arg1
    (((debug-menu-msg press))
     (set! (-> arg0 value) (not (-> arg0 value)))
     (when *traffic-manager*
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-0))
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-1))
       (send-event *traffic-manager* 'deactivate-by-type (traffic-type crimson-guard-2)))))
  (-> arg0 value))

;; --- 3. builder : cascade slug ▸ variante ▸ options ---
(defun mod-crimson-blueguard-build-menu ((ctx debug-menu-context))
  (debug-menu-make-from-template ctx
    '(menu "crimson-blueguard"
       (flag "Enable" *mod-crimson-blueguard-enable* dm-boolean-toggle-pick-func)
       (menu "city-peaceful"
         (flag "Enable / Disable" *mod-crimson-blueguard-city-peaceful*
               mod-crimson-blueguard-city-peaceful-pick)))))

;; --- 4. enregistrement (au niveau top, exécuté au chargement du fichier) ---
(mods-menu-register "crimson-blueguard" mod-crimson-blueguard-build-menu)
```

### Règles de nommage (ce qui évite les collisions)

| Élément | Convention | Exemple |
| --- | --- | --- |
| var de config | `*mod-<slug>-<option>*` | `*mod-crimson-blueguard-city-peaceful*` |
| pick func | `mod-<slug>-<option>-pick` | `mod-crimson-blueguard-city-peaceful-pick` |
| builder | `mod-<slug>-build-menu` | `mod-crimson-blueguard-build-menu` |
| label du menu | le slug nu | `"crimson-blueguard"` |

## 4. Intégrer le template à un build

Deux options :

1. **Aucun nouveau fichier** — collez les étapes 1 à 4 dans un `.gc` de mod déjà
   présent dans un `.gd`.
2. **Fichier dédié** — créez `goal_src/jak2/.../<slug>-menu.gc` et ajoutez
   `"<slug>-menu.o"` à votre `.gd` de niveau ou de jeu **après `mods-menu.o`**
   (pour que `mods-menu-register` soit déjà défini à la compilation).

Puis hot-reload depuis le REPL :

```lisp
(mi)
```

Ouvrez le menu debug en jeu et allez dans `Mods ▸ <slug>`.

## 5. Pièges

- **Faites le travail dans `press`, pas `update`.** Le menu envoie `update`
  toutes les quelques frames pour rafraîchir la coche ✓. Allouer ou spawn là
  martèlera le tas. La queue de la pick-func doit se limiter à `(-> arg0 value)`.
- **Ne re-spawnez jamais une faction à la main depuis une bascule.** Envoyez
  `'deactivate-by-type` au `*traffic-manager*` et laissez le moteur de trafic
  recycler les slots d'acteurs existants. `send-event` utilise un bloc message
  sur la pile — aucune allocation tas, donc rien n'est écrasé quand le joueur
  franchit une frontière de quartier pendant la bascule.
- **Protégez les managers potentiellement absents.** `*traffic-manager*` vaut
  `#f` hors de la ville — toujours `(when *traffic-manager* ...)`.
- **Les builders doivent être purs.** `mod-<slug>-build-menu` est ré-exécuté à
  chaque reconstruction ; il ne doit que construire et renvoyer un nœud.
- **Recharger `mods-menu.gc` lui-même** réinitialise le registre. Relancez
  `(mi)` (qui ré-exécute le `mods-menu-register` top-level de chaque mod) ou
  redémarrez. Recharger un fichier de mod seul est toujours sûr.
- **Ordre des `.o` dans le `.gd`.** Le `.o` de votre fichier de menu doit venir
  après `mods-menu.o`.
