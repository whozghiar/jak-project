# Unified In-Game "Mods" Menu / Menu « Mods » Unifié en Jeu

> **Bilingual reference / Référence bilingue** — [🇬🇧 English](#-english-version) · [🇫🇷 Version Française](#-version-française)
>
> **Status / Statut**
>
> 🇬🇧 The `mods-menu.gc` registry is **live on `master-dev` for Jak 2 and Jak 3**,
> with an identical public API in both. Since the retail-boot rework it is **no
> longer part of the debug menu**: it opens in a normal launcher boot with
> **L3 + SELECT**.
>
> | Game | Registry file | Wired in | Opens with |
> | --- | --- | --- | --- |
> | Jak 2 | `goal_src/jak2/pc/features/mods-menu.gc` | `goal_src/jak2/dgos/game.gd` | L3 + SELECT |
> | Jak 3 | `goal_src/jak3/pc/features/mods-menu.gc` | `goal_src/jak3/dgos/game.gd` | L3 + SELECT |
> | Jak 1 | — **not ported**, see §7 | — | — |
>
> 🇫🇷 Le registre `mods-menu.gc` est **actif sur `master-dev` pour Jak 2 et Jak 3**,
> avec une API publique identique dans les deux. Depuis la refonte « boot retail »
> il **ne fait plus partie du menu debug** : il s'ouvre dans un boot normal du
> launcher avec **L3 + SELECT**.
>
> | Jeu | Fichier du registre | Câblé dans | Ouverture |
> | --- | --- | --- | --- |
> | Jak 2 | `goal_src/jak2/pc/features/mods-menu.gc` | `goal_src/jak2/dgos/game.gd` | L3 + SELECT |
> | Jak 3 | `goal_src/jak3/pc/features/mods-menu.gc` | `goal_src/jak3/dgos/game.gd` | L3 + SELECT |
> | Jak 1 | — **non porté**, voir §7 | — | — |

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## 1. Why the debug menu could never work for a shipped mod

The OpenGOAL launcher starts the game with `-boot -fakeiso`. In
`game/kernel/jak2/kmachine.cpp`, `-boot` sets `MasterDebug = 0` **and**
`DebugSegment = 0`. That has three independent consequences, each one fatal:

| Consequence | Where | Effect on a debug-menu mod toggle |
| --- | --- | --- |
| DEBUG segments are not linked | `klink.cpp` skips a segment when `!DebugSegment` | A file marked `(declare-file (debug))` **does not exist at runtime** |
| `kdebugheap` is set to NULL | `kmachine.cpp`, `if (!MasterDebug && !DebugSegment)` | The whole `debug-menu` framework allocates with `(new 'debug ...)` — no heap |
| The open gesture is gated | `main.gc`: `(and *debug-segment* (cpad-hold? 0 l3) (cpad-pressed? 0 select start))` | L3+SELECT does nothing in retail |

So a player who installs a mod from the launcher and starts it normally could
**never** reach a toggle that lived under `Debug ▸ Mods`. Asking them to tick a
"debug mode" box in the launcher is not a fix — it changes how the whole game
boots and is not something a mod can rely on.

The useful side effect of the third row: because `main.gc` makes L3+SELECT inert
in a retail boot, that gesture is **guaranteed free**, which is why the mods menu
claims it.

## 2. Solution — one popup menu + a runtime registry

`goal_src/jak[2|3]/pc/features/mods-menu.gc` (registered in the matching
`goal_src/jak[2|3]/dgos/game.gd`, right after `speedruns.o`) builds on
`popup-menu` (`pc/util/popup-menu.gc`) — plain non-debug code that already ships
in `GAME.CGO` and is used by speedrunner mode. It installs a single menu and a
small registry:

```
[L3 + SELECT] ▸ Mods ▸ [mod-slug] ▸ [variant / sub-module] ▸ [options & toggles]
```

A mod **never edits `mods-menu.gc`**. It calls, from its own already-compiled
`.gc` file:

```lisp
(mods-menu-register "<mod-slug>" <builder-fn>)
```

Entries are sorted alphabetically by slug on every rebuild, so branch merge order
never changes what the player sees.

### Controls

| Button | Action |
| --- | --- |
| L3 + SELECT | open / close |
| UP / DOWN | move by 1 |
| LEFT / RIGHT | move by 5 |
| X | confirm / enter a submenu |
| CIRCLE | back (exits the menu at the root) |
| SELECT | close from anywhere |

The bind is a `pad-buttons` bitfield in `*mods-menu-bind*`. A mod that needs a
different combo sets it at load time, e.g.
`(set! *mods-menu-bind* (pad-buttons l1 r1 triangle))`. Avoid L1+R1+SELECT and
L1+R1+START — those belong to speedrunner mode.

### Public API

```lisp
(mods-menu-register (name string) (builder (function popup-menu-entry)))
```
Register (or, on hot-reload, replace) one mod's submenu. `builder` takes no
argument and returns a `popup-menu-entry` — normally a `popup-menu-submenu`. It
may return `#f` to hide the mod for now (e.g. its level is not loaded).

```lisp
(mods-menu-rebuild)
```
Force a rebuild from the registry. Rarely needed by hand — `mods-menu-register`
calls it, and so does every open.

### Entry types available to a builder

| Type | Use |
| --- | --- |
| `popup-menu-button` | plain action — `:on-confirm` |
| `popup-menu-flag` | toggle with a green check — `:is-toggled?` + `:on-confirm` |
| `popup-menu-submenu` | nested page — `:entries` |
| `popup-menu-dynamic-submenu` | list whose contents are computed at draw time |

Every entry also accepts `:entry-disabled?`, a `(function symbol)` that greys the
row out.

## 3. The standardised template

Copy `docs/modding/templates/mod_menu.template.gc` into one of your mod's own
`.gc` files. It is a working `crimson-blueguard` example covering a master
toggle, a nested variant, a disabled-row condition and an action button.

### Naming rules (what prevents collisions)

| Thing | Pattern |
| --- | --- |
| config var | `*mod-<slug>-<option>*` |
| helper | `mod-<slug>-<option>-<verb>` |
| builder | `mod-<slug>-build-menu` |
| registry label | the mod slug, exactly as the branch name's last segment |

## 4. Wiring the template into a build

1. Put the menu code in a `.gc` file your mod already owns, or add a dedicated
   `<slug>-menu.gc`.
2. Register that `.o` in the right `.gd`, **after `mods-menu.o`**.
3. **Do not** add `(declare-file (debug))` to that file.
4. Rebuild and check it in a *retail* boot, not a debug one:
   `task boot-game-retail` (or `gk -v --game jak2 -- -boot -fakeiso`).

## 5. Pitfalls

These are all real failures hit while building this system — each one compiles
or boots "fine" and then silently does the wrong thing.

- **`(declare-file (debug))` on your mod's menu file.** The file is not linked in
  a retail boot and your registration never runs. No error, no menu row.
- **`(new 'debug ...)` anywhere in code the menu reaches.** `kdebugheap` is NULL
  in retail, so `kmalloc` silently falls back to the **global heap** and never
  frees. A per-frame `(new 'debug ...)` in a draw path is a permanent leak. This
  is exactly the bug that was fixed in `popup-menu.gc` (`'debug` → `'stack`).
- **Spawning a process and sending it an event in the same frame.** `process-spawn`
  does not install the process state until the kernel dispatches it, on the *next*
  frame. `send-event-function` on a stateless process silently does nothing. This
  is why `mods-menu-spawn!` is deliberately separate from `mods-menu-open!` and
  runs at the very end of the per-frame update.
- **Referencing a `define`d symbol from inside a `new 'static` form.** Both the
  `:entries` array of a submenu and the function fields (`:on-confirm`,
  `:is-toggled?`, `:entry-disabled?`) must be written **inline**. A named `defun`
  or a separately-defined array fails to compile with *"could not be evaluated at
  compile time"*. Wrap a named helper in a one-line `lambda`.
- **An empty root menu.** `popup-menu`'s `move-up!` / `move-down!` index the
  entries array without a length guard, so a zero-length menu reads out of
  bounds. `mods-menu-rebuild` always keeps at least one row for this reason.
- **Two popup menus at once.** `*popup-menu-open*` is a single global shared with
  speedrunner mode. `mods-menu-open!` refuses to open while another popup owns
  the screen.
- **Letting the popup close itself without restoring the master mode.** On Jak 2
  the popup's own SELECT / CIRCLE close path does **not** call `set-master-mode`,
  so the game would stay frozen in `'menu`. `mods-menu-update` watches for that
  and hands control back. (Jak 3's handler does it itself — hence the small
  deliberate difference between the two files.)
- **`is-toggled?` doing work.** It runs every frame the menu is on screen. Keep it
  a pure read.

## 6. Jak 2 vs Jak 3 — the one real difference

`popup-menu` is not identical in the two games, so `mods-menu.gc` is not either:

| | Jak 2 | Jak 3 |
| --- | --- | --- |
| Who ticks the menu | nobody — `mods-menu-update` must call `update-menu!` | the popup's own `idle` `:trans` (it clears `menu`/`pause` from its process mask) |
| Who sets the master mode | `mods-menu.gc` | `popup-menu-event-handler` |
| Spawn convention | `process-spawn popup-menu :init popup-menu-init ...` | `process-spawn popup-menu ...` (uses `popup-menu-init-by-other`) |

Everything above the line — the registry, the API, the template, the bind — is
identical.

## 7. Why Jak 1 is not ported

Two independent blockers, unchanged by this rework:

1. **No `popup-menu` in Jak 1.** `goal_src/jak1/pc/util/` has no `popup-menu-h.gc`
   / `popup-menu.gc`; porting them is a real piece of work (font-context, PC
   string encoding and `draw-string-adv` all differ).
2. **The debug root menu is fragile at link time.** Appending to Jak 1's root
   debug menu during `link-and-exec` segfaults the boot reproducibly (see
   `.agents/skills/engine-internals/discoveries.md`), so the old workaround was
   already off-limits there.

Until Jak 1 is ported, Jak 1 mods add a mod-slug-prefixed submenu to their
`default-menu*.gc` and document it in the mod README — with the explicit caveat
that it is **debug-only** and therefore unreachable for a player using the
launcher normally.

## 8. Migrating a branch from the old debug registry

The public function name is unchanged; what changed is the builder's signature
and the node type.

| Before (debug) | After (retail) |
| --- | --- |
| `(declare-file (debug))` | remove it |
| `(defun mod-x-build-menu ((ctx debug-menu-context))` | `(defun mod-x-build-menu ()` |
| returns a `debug-menu-node` via `debug-menu-make-from-template` | returns a `popup-menu-entry`, normally a static `popup-menu-submenu` |
| `'(menu "x" (flag "Enable" *v* pick-fn))` s-expression template | nested `(new 'static 'popup-menu-submenu ... :entries ...)` |
| pick-func `((arg0 symbol) (arg1 debug-menu-msg))` returning the flag | `:is-toggled?` lambda reads the flag, `:on-confirm` lambda flips it |
| `(mods-menu-register "x" mod-x-build-menu)` | unchanged |

---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## 1. Pourquoi le menu debug ne pouvait pas marcher pour un mod distribué

Le launcher OpenGOAL démarre le jeu avec `-boot -fakeiso`. Dans
`game/kernel/jak2/kmachine.cpp`, `-boot` met `MasterDebug = 0` **et**
`DebugSegment = 0`. Trois conséquences indépendantes, chacune fatale :

| Conséquence | Où | Effet sur un toggle de mod dans le menu debug |
| --- | --- | --- |
| Les segments DEBUG ne sont pas linkés | `klink.cpp` saute le segment si `!DebugSegment` | Un fichier marqué `(declare-file (debug))` **n'existe pas à l'exécution** |
| `kdebugheap` est mis à NULL | `kmachine.cpp`, `if (!MasterDebug && !DebugSegment)` | Tout le framework `debug-menu` alloue en `(new 'debug ...)` — plus de tas |
| Le geste d'ouverture est gardé | `main.gc` : `(and *debug-segment* (cpad-hold? 0 l3) (cpad-pressed? 0 select start))` | L3+SELECT ne fait rien en retail |

Un joueur qui installe un mod depuis le launcher et le lance normalement ne
pouvait donc **jamais** atteindre un toggle situé sous `Debug ▸ Mods`. Lui
demander de cocher « mode debug » dans le launcher n'est pas un correctif : ça
change tout le boot du jeu et un mod ne peut pas compter dessus.

Effet de bord utile de la 3ᵉ ligne : puisque `main.gc` rend L3+SELECT inerte en
boot retail, ce geste est **garanti libre**, d'où son usage par le menu Mods.

## 2. Solution — un popup menu + un registre à l'exécution

`goal_src/jak[2|3]/pc/features/mods-menu.gc` (déclaré dans le
`goal_src/jak[2|3]/dgos/game.gd` correspondant, juste après `speedruns.o`)
s'appuie sur `popup-menu` (`pc/util/popup-menu.gc`) — du code non-debug déjà
livré dans `GAME.CGO` et utilisé par le mode speedrun. Il installe un seul menu
et un petit registre :

```
[L3 + SELECT] ▸ Mods ▸ [slug-du-mod] ▸ [variante / sous-module] ▸ [options]
```

Un mod **n'édite jamais `mods-menu.gc`**. Il appelle, depuis un de ses propres
`.gc` déjà compilés :

```lisp
(mods-menu-register "<slug-du-mod>" <fonction-builder>)
```

Les entrées sont triées alphabétiquement par slug à chaque reconstruction :
l'ordre de merge des branches ne change donc jamais ce que voit le joueur.

### Commandes

| Bouton | Action |
| --- | --- |
| L3 + SELECT | ouvrir / fermer |
| HAUT / BAS | déplacement de 1 |
| GAUCHE / DROITE | déplacement de 5 |
| X | valider / entrer dans un sous-menu |
| ROND | retour (quitte le menu à la racine) |
| SELECT | fermer depuis n'importe où |

Le bind est un bitfield `pad-buttons` dans `*mods-menu-bind*`. Un mod qui veut
une autre combinaison la pose au chargement, ex.
`(set! *mods-menu-bind* (pad-buttons l1 r1 triangle))`. Évitez L1+R1+SELECT et
L1+R1+START, réservés au mode speedrun.

### API publique

```lisp
(mods-menu-register (name string) (builder (function popup-menu-entry)))
```
Enregistre (ou remplace, en hot-reload) le sous-menu d'un mod. `builder` ne prend
aucun argument et renvoie un `popup-menu-entry` — normalement un
`popup-menu-submenu`. Il peut renvoyer `#f` pour masquer le mod temporairement
(ex. son niveau n'est pas chargé).

```lisp
(mods-menu-rebuild)
```
Force une reconstruction. Rarement utile à la main — `mods-menu-register`
l'appelle, et chaque ouverture aussi.

### Types d'entrées disponibles

| Type | Usage |
| --- | --- |
| `popup-menu-button` | action simple — `:on-confirm` |
| `popup-menu-flag` | toggle avec coche verte — `:is-toggled?` + `:on-confirm` |
| `popup-menu-submenu` | page imbriquée — `:entries` |
| `popup-menu-dynamic-submenu` | liste calculée au moment du dessin |

Chaque entrée accepte aussi `:entry-disabled?`, une `(function symbol)` qui grise
la ligne.

## 3. Le template standardisé

Copiez `docs/modding/templates/mod_menu.template.gc` dans un `.gc` de votre mod.
C'est un exemple `crimson-blueguard` fonctionnel couvrant un toggle maître, une
variante imbriquée, une condition de grisage et un bouton d'action.

### Règles de nommage (ce qui évite les collisions)

| Élément | Motif |
| --- | --- |
| variable de config | `*mod-<slug>-<option>*` |
| helper | `mod-<slug>-<option>-<verbe>` |
| builder | `mod-<slug>-build-menu` |
| label du registre | le slug du mod, exactement le dernier segment du nom de branche |

## 4. Intégrer le template à un build

1. Mettez le code du menu dans un `.gc` que votre mod possède déjà, ou ajoutez un
   `<slug>-menu.gc` dédié.
2. Déclarez ce `.o` dans le bon `.gd`, **après `mods-menu.o`**.
3. **N'ajoutez pas** `(declare-file (debug))` à ce fichier.
4. Reconstruisez et testez en boot *retail*, pas en debug :
   `task boot-game-retail` (ou `gk -v --game jak2 -- -boot -fakeiso`).

## 5. Pièges

Tous rencontrés réellement en construisant ce système — chacun compile ou boote
« très bien » puis fait silencieusement la mauvaise chose.

- **`(declare-file (debug))` sur le fichier menu de votre mod.** Le fichier n'est
  pas linké en retail et votre enregistrement ne s'exécute jamais. Aucune erreur,
  aucune ligne dans le menu.
- **`(new 'debug ...)` dans du code atteint par le menu.** `kdebugheap` est NULL
  en retail, donc `kmalloc` retombe silencieusement sur le **tas global** et ne
  libère jamais. Un `(new 'debug ...)` par frame dans un chemin de dessin est une
  fuite permanente. C'est exactement le bug corrigé dans `popup-menu.gc`
  (`'debug` → `'stack`).
- **Spawner un process et lui envoyer un event dans la même frame.**
  `process-spawn` n'installe pas l'état du process avant que le kernel ne le
  dispatche, à la frame *suivante*. `send-event-function` sur un process sans
  état ne fait rien, silencieusement. D'où la séparation délibérée entre
  `mods-menu-spawn!` et `mods-menu-open!`, le spawn étant fait tout à la fin de
  la mise à jour par frame.
- **Référencer un symbole `define` depuis un `new 'static`.** Le tableau
  `:entries` d'un sous-menu comme les champs fonction (`:on-confirm`,
  `:is-toggled?`, `:entry-disabled?`) doivent être écrits **inline**. Un `defun`
  nommé ou un tableau défini à part échoue à la compilation avec *« could not be
  evaluated at compile time »*. Enveloppez un helper nommé dans une `lambda`
  d'une ligne.
- **Un menu racine vide.** `move-up!` / `move-down!` de `popup-menu` indexent le
  tableau sans garde de longueur : un menu de longueur zéro lit hors bornes.
  C'est pourquoi `mods-menu-rebuild` garde toujours au moins une ligne.
- **Deux popup menus à la fois.** `*popup-menu-open*` est un global unique partagé
  avec le mode speedrun. `mods-menu-open!` refuse d'ouvrir si un autre popup
  occupe l'écran.
- **Laisser le popup se fermer sans restaurer le master mode.** Sur Jak 2, le
  chemin de fermeture SELECT / ROND du popup n'appelle **pas** `set-master-mode` :
  le jeu resterait figé en `'menu`. `mods-menu-update` surveille ce cas et rend la
  main. (Le handler de Jak 3 le fait lui-même — d'où la petite différence
  délibérée entre les deux fichiers.)
- **`is-toggled?` qui travaille.** Elle tourne à chaque frame où le menu est
  affiché. Gardez-la en lecture pure.

## 6. Jak 2 vs Jak 3 — la seule vraie différence

`popup-menu` n'est pas identique dans les deux jeux, donc `mods-menu.gc` non plus :

| | Jak 2 | Jak 3 |
| --- | --- | --- |
| Qui cadence le menu | personne — `mods-menu-update` doit appeler `update-menu!` | le `:trans` de l'état `idle` du popup (il retire `menu`/`pause` de son masque de process) |
| Qui pose le master mode | `mods-menu.gc` | `popup-menu-event-handler` |
| Convention de spawn | `process-spawn popup-menu :init popup-menu-init ...` | `process-spawn popup-menu ...` (via `popup-menu-init-by-other`) |

Tout le reste — registre, API, template, bind — est identique.

## 7. Pourquoi Jak 1 n'est pas porté

Deux blocages indépendants, inchangés par cette refonte :

1. **Pas de `popup-menu` dans Jak 1.** `goal_src/jak1/pc/util/` n'a ni
   `popup-menu-h.gc` ni `popup-menu.gc` ; les porter est un vrai chantier
   (font-context, encodage de chaînes PC et `draw-string-adv` diffèrent tous).
2. **Le menu debug racine est fragile au link.** Ajouter une entrée au menu debug
   racine de Jak 1 pendant `link-and-exec` fait segfaulter le boot de façon
   reproductible (voir `.agents/skills/engine-internals/discoveries.md`) : l'ancien
   contournement y était déjà interdit.

Tant que Jak 1 n'est pas porté, les mods Jak 1 ajoutent un sous-menu préfixé par
leur slug dans leur `default-menu*.gc` et le documentent dans le README du mod —
avec la réserve explicite que c'est **debug-only** et donc hors de portée d'un
joueur qui utilise le launcher normalement.

## 8. Migrer une branche depuis l'ancien registre debug

Le nom de la fonction publique ne change pas ; ce qui change est la signature du
builder et le type de nœud.

| Avant (debug) | Après (retail) |
| --- | --- |
| `(declare-file (debug))` | le supprimer |
| `(defun mod-x-build-menu ((ctx debug-menu-context))` | `(defun mod-x-build-menu ()` |
| renvoie un `debug-menu-node` via `debug-menu-make-from-template` | renvoie un `popup-menu-entry`, normalement un `popup-menu-submenu` statique |
| template s-expression `'(menu "x" (flag "Enable" *v* pick-fn))` | `(new 'static 'popup-menu-submenu ... :entries ...)` imbriqué |
| pick-func `((arg0 symbol) (arg1 debug-menu-msg))` renvoyant le flag | lambda `:is-toggled?` qui lit le flag, lambda `:on-confirm` qui l'inverse |
| `(mods-menu-register "x" mod-x-build-menu)` | inchangé |
