# Mod Readme — Mega Dark Jak / Dark Giant (Jak 3) / Méga Dark Jak / Dark Giant (Jak 3)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 3
> - **Branch / Branche:** `jak3/features/mega_dark_jak`
> - **Target Subsystem / Sous-système ciblé:** Dark Jak transformation (`goal_src/jak3/engine/target/`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

The **Mega Dark Jak** mod rehabilitates the **Dark Giant** transformation in Jak 3, re-using the giant animation, scaling and interpolation assets that Naughty Dog left dormant in the Jak 3 engine after the Jak 2 Dark Giant boss set-piece (see [`jak3_modding_utilities` #09](../jak3_modding_utilities/09_darkjak_architecture.md)).

- **Hold `L1` while Dark Jak** to grow into the **Dark Giant** (`darkjak-giant-interp` → `2.0`, roughly 2× scale).
- The transformation runs a **headroom collision probe** (a sphere `+12697.6` above Jak, radius `11878.4`): if the ceiling is too low, Jak stays at normal scale so he never clips into geometry.
- While giant, the camera springs back and rises (`string-min-length`, `string-max-length`, spline move/accel settings) to keep the colossus framed.
- Uses the native `"djak-transform"` sound and the `*darkjak-trans-mods*` movement surface.
- Releasing the transform (or leaving room) restores `darkjak-giant-interp` to `1.0` and clears the `giant` stage flag.
- `L1` is intercepted **before** `want-to-powerjak?` so holding `L1` as Dark Jak reliably triggers the giant instead of a Light Jak power.

## 2. Technical Architecture & Tooling

- `goal_src/jak3/engine/target/target-h.gc`:
  - added `(giant)` to the `darkjak-stage` bitfield enum.
  - declared the new virtual state `target-darkjak-giant` in the `target` state list.
- `goal_src/jak3/engine/target/target-darkjak.gc`:
  - new `defstate target-darkjak-giant` — `:code` runs the headroom sphere probe via `fill-and-probe-using-spheres` against `*collide-cache*`, sets `control unknown-word04` to `2.0` (room) or `1.0` (no room), applies the camera `set-setting!` block, plays `"djak-transform"`, and sets `darkjak stage`/`want-stage` to include `giant`.
  - `:exit` restores `darkjak-interp` / `darkjak-giant-interp` and clears the `giant` flag when scale returns to `1.0`.
- `goal_src/jak3/engine/target/target-lightjak.gc`:
  - `want-to-powerjak?` now returns `#f` when Jak is Dark, holding `L1`, and already `giant`, so the giant state owns the `L1` hold.
  - the Dark/Light `L1` handler adds a branch: Dark + `L1` + not `giant` → `(go target-darkjak-giant)`.
- **Reused engine systems (no new assets):** the giant scale interpolation (`darkjak-giant-interp`), the `jakb-darkjak-get-on-fast-ja` animation data, `*darkjak-trans-mods*`, and the `djak-transform` sound are all pre-existing Jak 3 engine leftovers — the mod only wires them back up.

## 3. How to Test & Play

1. Set the active game to Jak 3:
   ```bash
   task set-game-jak3
   ```
2. Hot-recompile in the REPL:
   ```lisp
   (mi)
   ```
3. Boot the game:
   ```bash
   task boot-game
   ```
4. Unlock Dark Jak (or enable it via the debug menu / a save with dark powers), press `L2` to go Dark.
5. **Hold `L1`.** In an open area Jak grows to ~2× (Dark Giant); under a low ceiling he stays normal-sized (headroom probe). Release to shrink back.
6. Confirm the camera pulls back and up while giant, and that `L1` never triggers a Light Jak power while Dark.

## 4. Current Status & Investigations

- **Stable / working as intended:** the `L1` giant trigger, headroom probe, camera spring, transform sound, and clean revert all work in-game.
- **Scope:** this is the Jak 2-style *scale* giant (2.0×), not the full Jak 2 Dark Giant boss move-set — super attacks and the higher `mega-giant` tier are out of scope here (that lives in the Jak 2 `jak2/features/dark_jak_enhanced` mod).
- **Not yet investigated:** whether the `11878.4` probe radius is generous enough for every Haven City interior, and whether the giant should be blocked (rather than silently staying small) with a UI cue when there is no headroom.

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-22 | `goal_src/jak3/engine/target/target-h.gc`<br>`goal_src/jak3/engine/target/target-darkjak.gc`<br>`goal_src/jak3/engine/target/target-lightjak.gc`<br>`docs/modding/jak3_modding_utilities/09_darkjak_architecture.md` | Added the `(giant)` `darkjak-stage` flag and the `target-darkjak-giant` virtual state; implemented the headroom sphere probe, 2.0× `darkjak-giant-interp` scaling, panoramic camera `set-setting!` block and `"djak-transform"` sound; gated `want-to-powerjak?` and added the Dark + `L1` → giant branch; documented the Dark Jak stage architecture and the dormant Jak 2 giant assets as a knowledge-base tip. | Rehabilitate the Jak 2 Dark Giant transformation in Jak 3 on an `L1` hold. |
| 2026-08-30 | `docs/modding/current_mod/mega_dark_jak_readme.md` | Created this dedicated bilingual mod readme (was previously missing on the branch). | Bring the mod documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Le mod **Méga Dark Jak** réhabilite la transformation **Dark Giant** dans Jak 3, en réutilisant les assets d'animation, de mise à l'échelle et d'interpolation « géant » que Naughty Dog a laissés en sommeil dans le moteur de Jak 3 après la séquence du Dark Giant de Jak 2 (voir [`jak3_modding_utilities` #09](../jak3_modding_utilities/09_darkjak_architecture.md)).

- **Maintenir `L1` en Dark Jak** pour se transformer en **Dark Giant** (`darkjak-giant-interp` → `2.0`, échelle ~2×).
- La transformation exécute une **sonde de collision de dégagement** (une sphère à `+12697.6` au-dessus de Jak, rayon `11878.4`) : si le plafond est trop bas, Jak reste à l'échelle normale et ne traverse jamais la géométrie.
- En mode géant, la caméra recule et s'élève (réglages `string-min-length`, `string-max-length`, déplacement / accélération de spline) pour garder le colosse cadré.
- Utilise le son natif `"djak-transform"` et la surface de déplacement `*darkjak-trans-mods*`.
- Relâcher la transformation (ou retrouver de la place) restaure `darkjak-giant-interp` à `1.0` et efface le drapeau de stade `giant`.
- `L1` est intercepté **avant** `want-to-powerjak?` pour que le maintien de `L1` en Dark Jak déclenche de façon fiable le géant plutôt qu'un pouvoir de Light Jak.

## 2. Architecture Technique & Outillage

- `goal_src/jak3/engine/target/target-h.gc` :
  - ajout de `(giant)` au champ de bits `darkjak-stage`.
  - déclaration du nouvel état virtuel `target-darkjak-giant` dans la liste d'états de `target`.
- `goal_src/jak3/engine/target/target-darkjak.gc` :
  - nouveau `defstate target-darkjak-giant` — le `:code` exécute la sonde de dégagement via `fill-and-probe-using-spheres` sur `*collide-cache*`, fixe `control unknown-word04` à `2.0` (place libre) ou `1.0` (pas de place), applique le bloc `set-setting!` de caméra, joue `"djak-transform"` et ajoute `giant` à `darkjak stage`/`want-stage`.
  - le `:exit` restaure `darkjak-interp` / `darkjak-giant-interp` et efface le drapeau `giant` lorsque l'échelle revient à `1.0`.
- `goal_src/jak3/engine/target/target-lightjak.gc` :
  - `want-to-powerjak?` renvoie désormais `#f` quand Jak est Dark, maintient `L1` et est déjà `giant`, afin que l'état géant s'approprie le maintien de `L1`.
  - le gestionnaire `L1` Dark/Light ajoute une branche : Dark + `L1` + pas `giant` → `(go target-darkjak-giant)`.
- **Systèmes moteur réutilisés (aucun nouvel asset) :** l'interpolation d'échelle géante (`darkjak-giant-interp`), les données d'animation `jakb-darkjak-get-on-fast-ja`, `*darkjak-trans-mods*` et le son `djak-transform` sont tous des reliquats préexistants du moteur de Jak 3 — le mod ne fait que les rebrancher.

## 3. Commandes & Procédure de Test

1. Sélectionner Jak 3 comme jeu actif :
   ```bash
   task set-game-jak3
   ```
2. Recompiler à chaud dans le REPL :
   ```lisp
   (mi)
   ```
3. Lancer le jeu :
   ```bash
   task boot-game
   ```
4. Débloquer Dark Jak (ou l'activer via le menu debug / une sauvegarde avec les pouvoirs sombres), appuyer sur `L2` pour passer Dark.
5. **Maintenir `L1`.** En zone ouverte, Jak grandit à ~2× (Dark Giant) ; sous un plafond bas, il reste de taille normale (sonde de dégagement). Relâcher pour rétrécir.
6. Vérifier que la caméra recule et s'élève en mode géant, et que `L1` ne déclenche jamais un pouvoir de Light Jak en Dark.

## 4. Statut Actuel & Investigations

- **Stable / fonctionne comme prévu :** le déclenchement du géant sur `L1`, la sonde de dégagement, le recul de caméra, le son de transformation et le retour propre fonctionnent tous en jeu.
- **Périmètre :** il s'agit du géant *d'échelle* façon Jak 2 (2.0×), pas de l'ensemble complet des attaques du boss Dark Giant de Jak 2 — les super-attaques et le palier supérieur `mega-giant` sont hors périmètre ici (cela vit dans le mod Jak 2 `jak2/features/dark_jak_enhanced`).
- **Non encore investigué :** si le rayon de sonde `11878.4` est assez généreux pour tous les intérieurs de Haven City, et si le géant devrait être bloqué (plutôt que rester silencieusement petit) avec un indice visuel en l'absence de dégagement.

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2026-08-22 | `goal_src/jak3/engine/target/target-h.gc`<br>`goal_src/jak3/engine/target/target-darkjak.gc`<br>`goal_src/jak3/engine/target/target-lightjak.gc`<br>`docs/modding/jak3_modding_utilities/09_darkjak_architecture.md` | Ajout du drapeau `(giant)` de `darkjak-stage` et de l'état virtuel `target-darkjak-giant` ; implémentation de la sonde de dégagement, de la mise à l'échelle `darkjak-giant-interp` à 2.0×, du bloc `set-setting!` de caméra panoramique et du son `"djak-transform"` ; verrouillage de `want-to-powerjak?` et ajout de la branche Dark + `L1` → géant ; documentation de l'architecture des stades de Dark Jak et des assets géants dormants de Jak 2 sous forme de tip. | Réhabiliter la transformation Dark Giant de Jak 2 dans Jak 3 sur un maintien de `L1`. |
| 2026-08-30 | `docs/modding/current_mod/mega_dark_jak_readme.md` | Création de ce readme de mod bilingue dédié (auparavant absent de la branche). | Mettre la documentation du mod en conformité avec la directive de modding. |
