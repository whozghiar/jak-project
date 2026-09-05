> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/blueguard`
> - **Last Updated / Dernière modification:** `jak2/features/blueguard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## Adding a whole new entity based on an existing character's skeleton

This is the end-to-end recipe for turning a re-skinned `.glb` of an existing native character into
a **new, standalone GOAL entity** — coexisting with the original, not replacing it — that keeps the
original's animations/state machine but can have its own combat/faction behavior. Worked example
throughout: `crimson-blue-guard`, a blue `crimson-guard` variant that is passive to Jak and fights
red guards instead (full source: `goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`,
full writeup: `docs/modding/current_mod/blue_guard_reskin_readme.md`).

This tip is the map; two other tips have the deep detail for two of the steps — read them when you
reach that step, not before:

- **Circuit 1 (skeleton + animation slot indices):**
  `20_reskin_existing_character_native_anim_header.md`
- **Circuit 2 (actual drawable geometry + textures):**
  `19_injecting_a_model_into_a_level.md`

## 0. Prerequisites

- A `.glb` of the character: same skeleton/joint names as the original (or close enough that the
  original's animations retarget cleanly), re-skinned/re-textured, in
  `custom_assets/jak2/models/custom_levels/<name>.glb`.
- You've identified the original GOAL type you're subtyping (e.g. `crimson-guard`) and read enough
  of its file to know: which method sets up its skeleton (`init-enemy!` or `init-from-entity!`,
  usually), and roughly how big its state machine is (you will **not** be copying most of it).

## 1. Circuit 1 — build the skeleton + animations art-group

```lisp
(build-actor "my-variant" :force-run #t :native-header #t)
```

`:native-header #t` is required whenever the original character's code references animations by
raw numeric index anywhere (very common) — it makes your new art-group's slot layout match the
original's exactly. See `20_reskin_existing_character_native_anim_header.md` for why, and for the
`.glb` animation-array reordering step that has to go with it. If the original character's code
only ever uses named/overridable animation fields (rare, worth actually checking rather than
assuming), you can skip `:native-header` and reorder.

Register the source file and residency exactly like any other new `.gc` file (see
`jak_modding_instructions.md`): `(goal-src "path/to/my-variant.gc" "<owning-project-group>")` in
`game.gp`, plus `.gd` entries for wherever the art-group and compiled code need to be resident.

## 2. Define the type and point it at its own skeleton

```lisp
(deftype my-variant (original-type) ())

(def-art-elt my-variant-ag my-variant-lod0-jg 0)
(def-art-elt my-variant-ag my-variant-lod0-mg 1)

(defskelgroup skel-my-variant my-variant my-variant-lod0-jg -1
              ((my-variant-lod0-mg (meters 999999)))
              :bounds (static-spherem 0 0 0 5)
              :origin-joint-index 3)

(defmethod init-enemy! ((this my-variant))
  ;; copy the original's init-enemy! verbatim, then change only the
  ;; art-group-get-by-name string to "skel-my-variant"
  ...)
```

`(deftype my-variant (original-type) ())` with an empty field list is normal — you are not adding
state, just getting a distinct type for polymorphic dispatch (`type-type?`, method overrides,
`instance-of?`, minimap icons, whatever else keys off the concrete type). Every state/method you
don't override is inherited and runs completely unmodified against your new type.

`init-enemy!` (or whichever method resolves the skeleton by name) has to be a full copy with one
string changed, because the `art-group-get-by-name` call is baked into the middle of the method
body — there's no separate hook to override just that one line. Everything else in this tip is
about **not** needing more copies like this one.

## 3. Circuit 2 — make it actually visible

Skeleton + animations alone get you a spawnable, animating, but **invisible** process. See
`19_injecting_a_model_into_a_level.md` §9 "Alternatives" — for a from-scratch `.glb`-based actor
like this one, the applicable mechanism is:

```
custom_assets/jak2/models/<level|common>/<name>-lod0.glb
```

Copy (don't move — `build-actor` needs its own copy at the `custom_levels/` path from step 1) the
same `.glb`, renamed to `<art-group-name>-lod0.glb` (this must match the name `build-actor`'s
dummy merc-ctrl was given — `ag.name + "-lod0"` in `build_actor.cpp`'s
`generate_dummy_merc_ctrl`). Drop it in `models/common/` for something that must be visible
everywhere, or `models/<level-name>/` for one specific level's `.fr3`. No config, no C++, no `.gd`
edit — the decompiler auto-scans that folder. Then:

```bash
task extract
```

Check the log for `Adding custom model <name>-lod0 to <level>` and the absence of any
`merc failed to find texture` line mentioning your model. This is the one step in the whole recipe
that isn't a fast `(mi)` iteration — budget for it once you're about to actually look at the model
in-game, not on every code tweak.

## 4. Only now, give it its own behavior

This is the part that's specific to *why* you're adding a new type instead of reusing the original
directly: it needs to act differently. Two idioms make this cheap, and both are visible end-to-end
in `crimson-blue-guard.gc`:

**a) Override one method/state, keep the parent's behavior for everything you don't touch:**

```lisp
(defmethod general-event-handler ((this my-variant) (arg0 process) (arg1 int) (arg2 symbol) (arg3 event-message-block))
  (case arg2
    (('some-event)
     ;; your new behavior for just this one case
     )
    (else
      ((method-of-type original-type general-event-handler) this arg0 arg1 arg2 arg3)
      )
    )
  )
```

`(method-of-type <parent-type> <method-name>)` looks up and returns the **parent's** implementation
of a method as a callable, bypassing your own override (which would otherwise just call itself).
This is the standard idiom all over the Jak 2 source for "handle a couple of cases myself, delegate
the rest" — grep `general-event-handler` in `guard.gc`, `civilian.gc`, `ruf.gc`, etc. for more
examples. The same idiom works for `defstate`'s individual handlers
(`(-> (method-of-type original-type some-state) trans)`, called then extended — see
`crimson-blue-guard`'s `active :trans` override) — you only ever need to write the handler(s) you're
actually changing; every other state/event on the type is inherited and untouched.

**b) Before writing custom AI, check whether the mechanism you need is already generic.** It's
tempting to assume you'll need to touch a large chunk of the original's state machine (aiming,
target tracking, attack selection...) to make a variant behave differently. Read it first — in
`crimson-guard`'s case, the entire combat loop resolves its target through
`(-> this focus handle)` / `traffic-target-status handle` with no hardcoded assumption that the
target is Jak (see `docs/modding/current_mod/blue_guard_reskin_readme.md` §5 for the full trace).
That meant making `crimson-blue-guard` fight *another guard* instead of Jak needed zero changes to
the aiming/attack code — only to *which handle gets put in that field*, and *when*. Look for the
same shape before assuming you need to duplicate a state: what field holds "current target", is it
read generically, and is there an existing generic finder (`find-nearest-attackable`,
`find-closest-to-with-collide-lists`, etc.) you can call instead of writing your own process-tree
walk.

## 5. Checklist

1. `task extract` completed with no missing-texture error for your model (step 3).
2. `(mi)` compiles clean (step 1-2, 4).
3. Spawn one (ambient spawn ratio, a scripted spawn, or a REPL debug helper like
   `spawn-crimson-blue-guard-debug` in `traffic-manager.gc` — cheap to write, invaluable for
   iterating on behavior without waiting on the ambient spawn system).
4. It's visible and textured (Circuit 2 actually landed).
5. Its animations match the original 1:1, **including any rare/hardcoded-index path** (vehicle
   knockout, elemental hit reactions, death) — this is where a missed `:native-header` or `.glb`
   reorder step shows up, often only in one obscure path.
6. Its new/different behavior (whatever you added in step 4) actually triggers, and doesn't leak
   into the original type (spawn both side by side and confirm the original is unaffected).

---
---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## Ajouter une entité entièrement nouvelle basée sur le squelette d'un personnage existant

Voici la recette de bout en bout pour transformer un `.glb` reskinné d'un personnage natif existant
en une **nouvelle entité GOAL à part entière** — coexistant avec l'original, sans le remplacer —
qui garde les animations/la machine à états de l'original mais peut avoir son propre comportement
de combat/faction. Exemple fil rouge : `crimson-blue-guard`, une variante bleue de `crimson-guard`
passive envers Jak qui combat les gardes rouges à la place (source complète :
`goal_src/jak2/levels/city/traffic/citizen/crimson-blue-guard.gc`, article complet :
`docs/modding/current_mod/blue_guard_reskin_readme.md`).

Ce tip est la carte ; deux autres tips ont le détail approfondi de deux des étapes — lisez-les
quand vous y arrivez, pas avant :

- **Circuit 1 (squelette + indices de slot d'animation) :**
  `20_reskin_existing_character_native_anim_header.md`
- **Circuit 2 (géométrie de rendu réelle + textures) :**
  `19_injecting_a_model_into_a_level.md`

## 0. Prérequis

- Un `.glb` du personnage : mêmes noms de squelette/joints que l'original (ou assez proches pour
  que les animations de l'original se retargent proprement), reskinné/retexturé, dans
  `custom_assets/jak2/models/custom_levels/<nom>.glb`.
- Vous avez identifié le type GOAL d'origine que vous sous-typez (ex. `crimson-guard`) et lu assez
  de son fichier pour savoir : quelle méthode initialise son squelette (`init-enemy!` ou
  `init-from-entity!`, en général), et grossièrement la taille de sa machine à états (vous n'allez
  **pas** en copier la majeure partie).

## 1. Circuit 1 — construire l'art-group squelette + animations

```lisp
(build-actor "ma-variante" :force-run #t :native-header #t)
```

`:native-header #t` est nécessaire dès que le code du personnage d'origine référence des animations
par indice numérique brut quelque part (très courant) — ça fait correspondre exactement la
disposition de slots de votre nouvel art-group à celle de l'original. Voir
`20_reskin_existing_character_native_anim_header.md` pour le pourquoi, et pour l'étape de
réordonnancement du tableau d'animations du `.glb` qui va avec. Si le code du personnage d'origine
n'utilise que des champs d'animation nommés/surchargeables (rare, à vérifier plutôt qu'à supposer),
vous pouvez sauter `:native-header` et le réordonnancement.

Enregistrez le fichier source et sa résidence comme n'importe quel nouveau fichier `.gc` (voir
`jak_modding_instructions.md`) : `(goal-src "chemin/vers/ma-variante.gc" "<groupe-projet>")` dans
`game.gp`, plus les entrées `.gd` partout où l'art-group et le code compilé doivent être résidents.

## 2. Définir le type et le faire pointer vers son propre squelette

```lisp
(deftype ma-variante (type-original) ())

(def-art-elt ma-variante-ag ma-variante-lod0-jg 0)
(def-art-elt ma-variante-ag ma-variante-lod0-mg 1)

(defskelgroup skel-ma-variante ma-variante ma-variante-lod0-jg -1
              ((ma-variante-lod0-mg (meters 999999)))
              :bounds (static-spherem 0 0 0 5)
              :origin-joint-index 3)

(defmethod init-enemy! ((this ma-variante))
  ;; copiez init-enemy! de l'original tel quel, puis changez seulement
  ;; la chaîne de art-group-get-by-name en "skel-ma-variante"
  ...)
```

`(deftype ma-variante (type-original) ())` avec une liste de champs vide est normal — vous n'ajoutez
pas d'état, vous obtenez juste un type distinct pour le dispatch polymorphe (`type-type?`,
surcharges de méthode, `instance-of?`, icônes de minimap, ou tout autre système qui se base sur le
type concret). Chaque état/méthode que vous ne surchargez pas est hérité et tourne sans
modification sur votre nouveau type.

`init-enemy!` (ou la méthode qui résout le squelette par nom) doit être une copie complète avec une
seule chaîne changée, car l'appel à `art-group-get-by-name` est codé en dur au milieu du corps de
la méthode — il n'y a pas de hook séparé pour ne surcharger que cette ligne. Tout le reste de ce
tip vise justement à **ne pas** avoir besoin d'autres copies comme celle-ci.

## 3. Circuit 2 — le rendre réellement visible

Squelette + animations seuls vous donnent un process qui apparaît, s'anime, mais est **invisible**.
Voir `19_injecting_a_model_into_a_level.md` §9 « Alternatives » — pour un acteur basé sur un `.glb`
neuf comme celui-ci, le mécanisme applicable est :

```
custom_assets/jak2/models/<niveau|common>/<nom>-lod0.glb
```

Copiez (ne déplacez pas — `build-actor` a besoin de sa propre copie au chemin `custom_levels/` de
l'étape 1) le même `.glb`, renommé en `<nom-art-group>-lod0.glb` (doit correspondre au nom donné au
merc-ctrl factice de `build-actor` — `ag.name + "-lod0"` dans `generate_dummy_merc_ctrl` de
`build_actor.cpp`). Déposez-le dans `models/common/` pour quelque chose qui doit être visible
partout, ou `models/<nom-niveau>/` pour le `.fr3` d'un niveau précis. Pas de config, pas de C++,
pas d'édition de `.gd` — le décompilateur scanne ce dossier automatiquement. Puis :

```bash
task extract
```

Vérifiez dans le log la ligne `Adding custom model <nom>-lod0 to <niveau>` et l'absence de toute
ligne `merc failed to find texture` mentionnant votre modèle. C'est la seule étape de toute la
recette qui n'est pas une itération rapide en `(mi)` — prévoyez-la une fois prêt à regarder
réellement le modèle en jeu, pas à chaque retouche de code.

## 4. Seulement maintenant, donnez-lui son propre comportement

C'est la partie spécifique à *pourquoi* vous ajoutez un nouveau type plutôt que de réutiliser
l'original directement : il doit se comporter différemment. Deux idiomes rendent ça bon marché, et
les deux sont visibles de bout en bout dans `crimson-blue-guard.gc` :

**a) Surchargez une seule méthode/état, gardez le comportement du parent pour tout ce que vous ne
touchez pas :**

```lisp
(defmethod general-event-handler ((this ma-variante) (arg0 process) (arg1 int) (arg2 symbol) (arg3 event-message-block))
  (case arg2
    (('un-evenement)
     ;; votre nouveau comportement pour ce seul cas
     )
    (else
      ((method-of-type type-original general-event-handler) this arg0 arg1 arg2 arg3)
      )
    )
  )
```

`(method-of-type <type-parent> <nom-methode>)` récupère et retourne l'implémentation **du parent**
d'une méthode sous forme d'appelable, en contournant votre propre surcharge (qui sinon s'appellerait
elle-même). C'est l'idiome standard partout dans le code source de Jak 2 pour « gérer moi-même
quelques cas, déléguer le reste » — cherchez `general-event-handler` dans `guard.gc`, `civilian.gc`,
`ruf.gc`, etc. pour d'autres exemples. Le même idiome fonctionne pour les handlers individuels d'un
`defstate` (`(-> (method-of-type type-original un-etat) trans)`, appelé puis étendu — voir la
surcharge du `:trans` de `active` dans `crimson-blue-guard`) — vous n'avez besoin d'écrire que
le(s) handler(s) que vous changez réellement ; tout autre état/événement du type est hérité et
intact.

**b) Avant d'écrire une IA custom, vérifiez si le mécanisme dont vous avez besoin est déjà
générique.** Il est tentant de supposer qu'il faudra toucher une grosse partie de la machine à
états de l'original (visée, suivi de cible, sélection d'attaque...) pour faire se comporter une
variante différemment. Lisez-le d'abord — dans le cas de `crimson-guard`, toute la boucle de combat
résout sa cible via `(-> this focus handle)` / `traffic-target-status handle` sans supposition codée
en dur que la cible est Jak (voir §5 de `docs/modding/current_mod/blue_guard_reskin_readme.md` pour
la trace complète). Ça a permis de faire combattre `crimson-blue-guard` contre *un autre garde* au
lieu de Jak sans aucun changement au code de visée/attaque — seulement à *quel handle est mis dans
ce champ*, et *quand*. Cherchez la même forme avant de supposer qu'il faut dupliquer un état :
quel champ contient « la cible actuelle », est-il lu de façon générique, et existe-t-il déjà un
chercheur générique (`find-nearest-attackable`, `find-closest-to-with-collide-lists`, etc.)
utilisable plutôt que d'écrire votre propre parcours d'arbre de process.

## 5. Checklist

1. `task extract` terminé sans erreur de texture manquante pour votre modèle (étape 3).
2. `(mi)` compile proprement (étapes 1-2, 4).
3. Faites-en apparaître un (ratio de spawn ambiant, spawn scripté, ou un helper de debug REPL comme
   `spawn-crimson-blue-guard-debug` dans `traffic-manager.gc` — bon marché à écrire, précieux pour
   itérer sur le comportement sans attendre le système de spawn ambiant).
4. Il est visible et texturé (le Circuit 2 est bien arrivé).
5. Ses animations correspondent 1:1 à l'original, **y compris tout chemin rare/à indice codé en
   dur** (éjection de véhicule, réactions de coup élémentaire, mort) — c'est là qu'une étape
   `:native-header` ou de réordonnancement du `.glb` manquée se manifeste, souvent seulement dans
   un chemin obscur.
6. Son nouveau comportement / comportement différent (celui ajouté à l'étape 4) se déclenche bien,
   et ne fuite pas vers le type d'origine (faites apparaître les deux côte à côte et vérifiez que
   l'original n'est pas affecté).

---
*(AI-assisted)*
