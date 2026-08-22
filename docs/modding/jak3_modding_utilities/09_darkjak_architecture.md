# Jak 3 — Architecture: Dark Jak Stages & Legacy Assets

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** Technical investigation (`goal_src/jak3/engine/target/target-darkjak.gc`, `goal_src/jak3/engine/target/target-lightjak.gc`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Dark Jak State Machine & Abilities (`darkjak-stage`)
* **Bitmask Flags:** Dark Jak capabilities are driven by the `darkjak-stage` bitfield enum in `target-h.gc` and stored in `(-> self darkjak stage)` and `(-> self darkjak want-stage)`:
  - `active`: Base Dark Jak form.
  - `bomb0` / `bomb1`: Dark Bomb and Dark Blast abilities.
  - `invinc`: Invulnerability stage.
  - `invis`: Invisibility modifier (suppresses offensive stages).
  - `tracking`: Target tracking mode.
  - `smack`: Dark Strike attack mode.
  - `giant`: Scaling stage flag.

## 2. Transformation Checks & Mod Surfaces
* **Trigger Conditions:** `want-to-darkjak?` and `want-to-powerjak?` in `target-darkjak.gc` / `target-lightjak.gc` validate:
  - Game features flag `(game-feature darkjak)` in `*setting-control*`.
  - Focus tests (cannot transform while swimming underwater, piloting, carrying, etc.).
  - Timing delays via `(-> self fact darkjak-start-time)`.
* **Surface Modifiers:** Transformed movement is governed by `*darkjak-trans-mods*` surface parameters.

## 3. Legacy Jak 2 Giant State Assets
* **Unused Animation & Scale Hooks:** The Jak 3 engine retains full animation data for `jakb-darkjak-get-on-fast-ja` as well as scaling interpolation variables (`(-> self darkjak-giant-interp)`) originally used for the Jak 2 Dark Giant transformation.

---

# 🇫🇷 Version Française

## 1. Machine à États et Capacités Dark Jak (`darkjak-stage`)
* **Drapeaux Bitmask :** Les capacités de Dark Jak sont régies par l'énumération de bits `darkjak-stage` (`target-h.gc`) et stockées dans `(-> self darkjak stage)` et `(-> self darkjak want-stage)` :
  - `active` : Forme Dark Jak de base.
  - `bomb0` / `bomb1` : Capacités Dark Bomb et Dark Blast.
  - `invinc` : État d'invulnérabilité.
  - `invis` : Modificateur d'invisibilité (neutralise les capacités offensives).
  - `tracking` : Mode de suivi / ciblage.
  - `smack` : Attaque Dark Strike.
  - `giant` : Drapeau d'échelle / transformation géante.

## 2. Conditions de Déclenchement et Surfaces Modificatrices
* **Validation d'Entrée :** `want-to-darkjak?` et `want-to-powerjak?` (`target-darkjak.gc` / `target-lightjak.gc`) contrôlent :
  - L'activation de la feature `(game-feature darkjak)` dans `*setting-control*`.
  - Les tests de focus (interdiction sous l'eau, en véhicule, transport d'objet, etc.).
  - Les temporisations via `(-> self fact darkjak-start-time)`.
* **Modificateurs de Surface :** Les physiques de déplacement transformé utilisent `*darkjak-trans-mods*`.

## 3. Reliquats Moteur du Dark Giant de Jak 2
* **Animations et Variables d'Échelle Résiduelles :** Le moteur de Jak 3 intègre encore les données d'animation `jakb-darkjak-get-on-fast-ja` ainsi que la variable d'interpolation de taille `(-> self darkjak-giant-interp)` héritées du Dark Giant de Jak 2.
