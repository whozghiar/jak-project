> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/blueguard`
> - **Last Updated / Dernière modification:** `jak2/features/blueguard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## Reskinning an existing character as a standalone entity, with identical animation indices

If you want a visual variant of an existing native character (e.g. a recolored NPC) as its **own
separate GOAL type** — coexisting with the original, not replacing it globally — and that
character's AI code references its animations by **raw numeric slot index** (common in decompiled
enemy/NPC code: `(-> this draw art-group data 33)`, static tables like `:knocked-anim 8`), you
need your new standalone art-group's slot layout to match the original's exactly, or those
hardcoded indices will silently play the wrong clip.

**The mismatch:** `build-actor` (`goalc/build_actor/<game>/build_actor.cpp`) normally emits a
2-slot header (mesh, one dummy null slot) before animations, and orders animations by their order
in the source `.glb`'s `animations` array — which Blender/glTF exporters sort alphabetically.
Native art-groups instead use a 4-slot header (`jgeo`, `lod0-mg`, `lod2-mg`, `shadow-mg`) with
animations in the *original authoring order* (see
`decompiler/config/jak2/ntsc_v1/art-group-info.min.json` for any given art-group's real slot
layout).

**The fix, two additive pieces (jak2, added on `jak2/features/blueguard`):**

1. `build-actor` gained an opt-in `:native-header #t` flag (threaded through
   `goal_src/jak2/lib/project-lib.gp` → `goalc/make/Tools.cpp::BuildActor2Tool` →
   `jak2::BuildActorParams2::native_anim_header` → `run_build_actor` in
   `goalc/build_actor/jak2/build_actor.cpp`), which emits 2 extra null header slots so animations
   start at slot 4 instead of 2. Default `#f`, zero effect on existing actors.
2. Reorder the source `.glb`'s `animations` JSON array to match the target character's real slot
   order before running `build-actor` — see
   `scripts/modding/reorder_crimson_guard_glb_anims.py` for a worked example (adapt the
   `CANONICAL_SUFFIXES` list to your character, pulled straight from `art-group-info.min.json`).

With both in place, subtype the original GOAL type (`(deftype my-variant (original-type) ())`),
declare its two real header elements with `def-art-elt`, write a `defskelgroup` pointing at the
new art-group, and override only the one method that resolves the skeleton-group by name (usually
`init-enemy!` or `init-from-entity!`) — every other inherited state/method keeps using the same
numeric indices unmodified, since they now point at the same clips.

**Full worked example:** `docs/modding/current_mod/blue_guard_reskin_readme.md` (blue
`crimson-guard` variant, `crimson-blue-guard`).

**Pitfall:** if you skip the reordering step, or your source `.glb` is missing/renames a clip the
original had, indices silently drift — nothing errors at compile time, you only notice it as a
wrong or T-posed animation playing at runtime (worst case: only in a rare code path like a
vehicle-knockout reaction, easy to miss in testing).

---
---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## Reskinner un personnage existant en entité à part, avec des indices d'animation identiques

Si vous voulez une variante visuelle d'un personnage natif existant (ex : un PNJ recoloré) en tant
qu'**entité GOAL séparée à part entière** — coexistant avec l'original, sans le remplacer
globalement — et que le code IA de ce personnage référence ses animations par **indice numérique
de slot brut** (courant dans le code d'ennemi/PNJ décompilé : `(-> this draw art-group data 33)`,
des tables statiques comme `:knocked-anim 8`), il faut que la disposition de slots de votre
nouvel art-group autonome corresponde exactement à celle de l'original, sinon ces indices en dur
joueront silencieusement le mauvais clip.

**Le décalage :** `build-actor` (`goalc/build_actor/<jeu>/build_actor.cpp`) émet normalement un
header à 2 slots (mesh, un slot factice vide) avant les animations, et ordonne les animations
selon leur ordre dans le tableau `animations` du `.glb` source — que les exporteurs Blender/glTF
trient alphabétiquement. Les art-groups natifs utilisent au contraire un header à 4 slots (`jgeo`,
`lod0-mg`, `lod2-mg`, `shadow-mg`) avec les animations dans *l'ordre d'origine* (voir
`decompiler/config/jak2/ntsc_v1/art-group-info.min.json` pour la disposition réelle de n'importe
quel art-group).

**Le correctif, deux pièces additives (jak2, ajoutées sur `jak2/features/blueguard`) :**

1. `build-actor` a reçu un flag optionnel `:native-header #t` (propagé via
   `goal_src/jak2/lib/project-lib.gp` → `goalc/make/Tools.cpp::BuildActor2Tool` →
   `jak2::BuildActorParams2::native_anim_header` → `run_build_actor` dans
   `goalc/build_actor/jak2/build_actor.cpp`), qui émet 2 slots de header factices
   supplémentaires pour que les animations commencent au slot 4 au lieu de 2. Par défaut `#f`,
   aucun effet sur les acteurs existants.
2. Réordonner le tableau JSON `animations` du `.glb` source pour correspondre à l'ordre de slot
   réel du personnage cible avant de lancer `build-actor` — voir
   `scripts/modding/reorder_crimson_guard_glb_anims.py` pour un exemple concret (adaptez la liste
   `CANONICAL_SUFFIXES` à votre personnage, tirée directement de `art-group-info.min.json`).

Avec les deux en place, sous-typez le type GOAL d'origine (`(deftype ma-variante (type-original)
())`), déclarez ses deux vrais éléments de header avec `def-art-elt`, écrivez un `defskelgroup`
pointant vers le nouvel art-group, et ne surchargez que la seule méthode qui résout le
skeleton-group par nom (généralement `init-enemy!` ou `init-from-entity!`) — toutes les autres
méthodes/états hérités continuent d'utiliser les mêmes indices numériques sans modification,
puisqu'ils pointent maintenant vers les mêmes clips.

**Exemple complet :** `docs/modding/current_mod/blue_guard_reskin_readme.md` (variante bleue de
`crimson-guard`, `crimson-blue-guard`).

**Piège :** si vous sautez l'étape de réordonnancement, ou que votre `.glb` source manque un clip
qu'avait l'original (ou le renomme), les indices dérivent silencieusement — rien n'échoue à la
compilation, vous ne le remarquez qu'à l'exécution via une animation fausse ou un mesh en T-pose
(pire cas : uniquement dans un chemin de code rare comme une réaction d'éjection de véhicule,
facile à manquer en test).
