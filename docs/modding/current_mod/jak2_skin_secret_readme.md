# Mod Readme — Jak II Outfit Secret (Jak 3) / Secret « Vêtements de Jak II » (Jak 3)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 3
> - **Branch / Branche:** `jak3/features/jak2_skin_secret`
> - **Target Subsystem / Sous-système ciblé:** Secrets menu (`goal_src/jak3/engine/common-obs/secrets-menu.gc`), PC progress rendering (`goal_src/jak3/pc/progress/progress-draw-pc.gc`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

This mod exposes the dormant **`jak-is-jak2`** game secret through the in-game **Secrets** menu, letting the player switch Jak's model to his Jak II appearance at will.

- A new, **free** (`:cost 0`) entry appears in the Secrets menu, available after `city-start-introduction`.
- Selecting it toggles the `(game-secrets jak-is-jak2)` flag, which the Jak 3 engine already reads to render the Jak II model.
- The `jak-is-jak2` secret flag itself is **stock Jak 3** (declared in `settings-h.gc`) — Naughty Dog wired the model swap but never gave it a menu entry. This mod adds only the entry and its label.
- Because there is no text-database string for the option, its label (`"Vetements de Jak II"`) is resolved dynamically during Secrets-menu rendering.

## 2. Technical Architecture & Tooling

- `goal_src/jak3/engine/common-obs/secrets-menu.gc`:
  - added one `(new 'static 'secret-item-option ...)` to `*menu-secrets-array*`:
    - `:name (text-id progress-title-jak2-mdl-viewer)`
    - `:cost 0`
    - `:secret (game-secrets jak-is-jak2)`
    - `:avail-after (game-task-node city-start-introduction)`
    - `:flags (secret-item-option-flags sf1)`
- `goal_src/jak3/pc/progress/progress-draw-pc.gc`:
  - added a label case in the Secrets-menu draw path: `((game-secrets jak-is-jak2)) → "Vetements de Jak II"`, so the option shows a readable name despite having no localized string.
  - (the commit also reflows large portions of this file; the only behavioral change is the label case.)
- **Reused engine systems (no new assets):** the `jak-is-jak2` secret, the `secret-item-option` menu framework, the `game-secrets` bitfield, and the Jak II model itself are all stock Jak 3.

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
4. Progress past `city-start-introduction` (or load a save that has), open the **Secrets** menu.
5. Confirm the **"Vetements de Jak II"** entry is present, costs 0, and toggles on/off.
6. Enable it and confirm Jak renders in his Jak II outfit in-game and in cutscenes.

## 4. Current Status & Investigations

- **Stable / working as intended:** the entry appears, toggles the `jak-is-jak2` flag, and the model swap takes effect. `:cost 0` makes it a pure toggle.
- **No localized string:** the label is hard-coded (`"Vetements de Jak II"`, unaccented to match the surrounding menu code). A proper `text-id` in the text database would be the clean follow-up, at which point the `progress-draw-pc.gc` label case can be removed.
- **Not yet investigated:** whether `:avail-after (game-task-node city-start-introduction)` is the desired unlock point (vs. available from the start, or after finishing the game), and whether the swap should also affect Dark/Light Jak overlays.

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-22 | `goal_src/jak3/engine/common-obs/secrets-menu.gc`<br>`goal_src/jak3/pc/progress/progress-draw-pc.gc`<br>`docs/modding/jak3_modding_utilities/10_secrets_menu_architecture.md` | Added a free `secret-item-option` for `(game-secrets jak-is-jak2)` to `*menu-secrets-array*` (available after `city-start-introduction`); added the dynamic `"Vetements de Jak II"` label case in the Secrets-menu draw path; documented the `game-secrets` bitfield, the `secret-item-option` structure and the PC label-resolution path as a knowledge-base tip. | Expose the stock but unreachable `jak-is-jak2` model-swap secret through the Secrets menu. |
| 2026-08-30 | `docs/modding/current_mod/jak2_skin_secret_readme.md` | Created this dedicated bilingual mod readme (was previously missing on the branch). | Bring the mod documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Ce mod expose le secret de jeu dormant **`jak-is-jak2`** via le menu **Secrets** en jeu, permettant au joueur de basculer le modèle de Jak sur son apparence de Jak II à volonté.

- Une nouvelle entrée **gratuite** (`:cost 0`) apparaît dans le menu Secrets, disponible après `city-start-introduction`.
- La sélectionner bascule le drapeau `(game-secrets jak-is-jak2)`, que le moteur de Jak 3 lit déjà pour afficher le modèle de Jak II.
- Le drapeau de secret `jak-is-jak2` lui-même est **d'origine dans Jak 3** (déclaré dans `settings-h.gc`) — Naughty Dog a câblé l'échange de modèle mais ne lui a jamais donné d'entrée de menu. Ce mod n'ajoute que l'entrée et son libellé.
- Comme il n'existe aucune chaîne dans la base de textes pour cette option, son libellé (`"Vetements de Jak II"`) est résolu dynamiquement lors du rendu du menu Secrets.

## 2. Architecture Technique & Outillage

- `goal_src/jak3/engine/common-obs/secrets-menu.gc` :
  - ajout d'un `(new 'static 'secret-item-option ...)` à `*menu-secrets-array*` :
    - `:name (text-id progress-title-jak2-mdl-viewer)`
    - `:cost 0`
    - `:secret (game-secrets jak-is-jak2)`
    - `:avail-after (game-task-node city-start-introduction)`
    - `:flags (secret-item-option-flags sf1)`
- `goal_src/jak3/pc/progress/progress-draw-pc.gc` :
  - ajout d'un cas de libellé dans le chemin de dessin du menu Secrets : `((game-secrets jak-is-jak2)) → "Vetements de Jak II"`, pour que l'option affiche un nom lisible malgré l'absence de chaîne localisée.
  - (le commit reformate aussi de larges portions de ce fichier ; le seul changement de comportement est ce cas de libellé.)
- **Systèmes moteur réutilisés (aucun nouvel asset) :** le secret `jak-is-jak2`, le cadre de menu `secret-item-option`, le champ de bits `game-secrets` et le modèle de Jak II lui-même sont tous d'origine dans Jak 3.

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
4. Progresser au-delà de `city-start-introduction` (ou charger une sauvegarde qui l'a), ouvrir le menu **Secrets**.
5. Vérifier que l'entrée **« Vetements de Jak II »** est présente, coûte 0 et se bascule on/off.
6. L'activer et vérifier que Jak s'affiche dans sa tenue de Jak II en jeu et dans les cinématiques.

## 4. Statut Actuel & Investigations

- **Stable / fonctionne comme prévu :** l'entrée apparaît, bascule le drapeau `jak-is-jak2` et l'échange de modèle prend effet. `:cost 0` en fait un simple interrupteur.
- **Aucune chaîne localisée :** le libellé est codé en dur (`"Vetements de Jak II"`, sans accents pour correspondre au code de menu environnant). Un vrai `text-id` dans la base de textes serait le suivi propre, après quoi le cas de libellé dans `progress-draw-pc.gc` pourra être retiré.
- **Non encore investigué :** si `:avail-after (game-task-node city-start-introduction)` est le point de déblocage souhaité (vs. disponible dès le début, ou après la fin du jeu), et si l'échange devrait aussi affecter les surcouches Dark/Light Jak.

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2026-08-22 | `goal_src/jak3/engine/common-obs/secrets-menu.gc`<br>`goal_src/jak3/pc/progress/progress-draw-pc.gc`<br>`docs/modding/jak3_modding_utilities/10_secrets_menu_architecture.md` | Ajout d'un `secret-item-option` gratuit pour `(game-secrets jak-is-jak2)` à `*menu-secrets-array*` (disponible après `city-start-introduction`) ; ajout du cas de libellé dynamique `"Vetements de Jak II"` dans le chemin de dessin du menu Secrets ; documentation du champ de bits `game-secrets`, de la structure `secret-item-option` et du chemin de résolution des libellés PC sous forme de tip. | Exposer via le menu Secrets le secret d'échange de modèle `jak-is-jak2`, présent mais inaccessible. |
| 2026-08-30 | `docs/modding/current_mod/jak2_skin_secret_readme.md` | Création de ce readme de mod bilingue dédié (auparavant absent de la branche). | Mettre la documentation du mod en conformité avec la directive de modding. |
