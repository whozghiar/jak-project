# Mod Readme — Start Menu Wheel Fast Navigation (Jak 2) / Navigation Rapide du Menu Circulaire (Jak 2)

> **Bilingual Mod Readme / Readme de Mod Bilingue**
>
> - **Game / Jeu:** Jak 2
> - **Branch / Branche:** `jak2/config/start_menu_wheel`
> - **Target Subsystem / Sous-système ciblé:** UI progress & in-game pause menu (`goal_src/jak2/engine/ui/progress/` & `goal_src/jak2/pc/progress/`)
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Description & Features

This quality-of-life (QoL) mod modernizes the in-game Start / Pause menu wheel navigation in Jak 2 to match the fluidity and responsiveness of Jak 3:

- **Doubled Ring Rotation Speed:** In original Jak 2, the menu ring rotation animation was capped at half the speed of Jak 3, locking new user inputs until the animation completed. The seek speed is doubled to provide instant feedback.
- **Hold-to-Repeat Navigation:** Holding down directional inputs (D-Pad / analog sticks Up/Down and Left/Right) now automatically cycles through options smoothly with a 0.175s throttle window, eliminating the need to repeatedly mash the direction buttons.

## 2. Technical Architecture & Tooling

- **Modified Files:**
  - `goal_src/jak2/engine/ui/progress/progress-h.gc`: added timer fields for input-repeat throttling in `progress-control`.
  - `goal_src/jak2/engine/ui/progress/progress.gc`: updated `respond-to-cpad` and the ring rotation seek rate to match Jak 3 speeds.
  - `goal_src/jak2/pc/progress/progress-generic-pc.gc`: enhanced PC option-menu navigation handling.
  - `goal_src/jak2/pc/progress/progress-pc.gc`: initialized the repeat timer variables.
- **Reused Engine Systems (no new engine code):**
  - The existing `progress-control` state machine and `cpad` input polling — the mod only re-tunes timing constants and adds throttle timers, it introduces no new UI state.

## 3. How to Test & Play

1. Set the active game to Jak 2:
   ```bash
   task set-game-jak2
   ```
2. Hot-recompile in the REPL:
   ```lisp
   (mi)
   ```
3. Boot the game:
   ```bash
   task boot-game
   ```
4. Press `Start` / `Escape` to enter the Pause Menu.
5. Use the D-Pad or Left Stick (or hold up/down/left/right) to navigate the options ring and observe the snappy, continuous scrolling — it should feel identical to Jak 3.

## 4. Current Status & Investigations

- **Stable / working as intended:** doubled ring seek rate and hold-to-repeat both behave as designed, on controller and keyboard, in every progress sub-menu.
- **Config-only mod:** no assets, no new types, no new states — purely timing constants and two throttle timers. Low collision risk when merged with other mods.
- **Not yet investigated:** whether the 0.175s repeat throttle should be exposed as a PC setting rather than hard-coded, and whether the faster seek rate needs a matching tweak to the ring's audio cue cadence.

## 5. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
|------|-----------------------|-----------------------|-----------|
| 2026-08-13 | `goal_src/jak2/engine/ui/progress/progress-h.gc`<br>`goal_src/jak2/engine/ui/progress/progress.gc`<br>`goal_src/jak2/pc/progress/progress-generic-pc.gc`<br>`goal_src/jak2/pc/progress/progress-pc.gc` | Doubled the ring seek rotation rate to match Jak 3. Implemented hold-to-repeat input logic with a 0.175s repeat throttle for Up/Down and Left/Right progress navigation. | Make Start menu wheel navigation responsive and fluid like Jak 3. |
| 2026-08-30 | `docs/modding/current_mod/start_menu_wheel_readme.md` (relocated from `docs/mods/`)<br>removed stale `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` | Relocated this readme to the mandated `docs/modding/current_mod/` path, made it fully bilingual, added the "Current Status & Investigations" section, and cleared the pre-migration flat `docs/` tree left over on this branch. | Bring the mod documentation into compliance with the modding directive. |

---

# 🇫🇷 Version Française

## 1. Description & Fonctionnalités

Ce mod de confort (QoL) modernise la navigation du menu circulaire Start / Pause en jeu dans Jak 2 pour retrouver la fluidité et la réactivité de Jak 3 :

- **Vitesse de rotation du cercle doublée :** Dans Jak 2 d'origine, l'animation de rotation du cercle du menu était plafonnée à la moitié de la vitesse de Jak 3, bloquant les nouvelles entrées de l'utilisateur jusqu'à la fin de l'animation. La vitesse de défilement est doublée pour un retour instantané.
- **Navigation « maintenir pour répéter » :** Maintenir une direction (croix directionnelle / sticks analogiques Haut/Bas et Gauche/Droite) fait désormais défiler les options en continu et en douceur avec une fenêtre de throttle de 0,175s, évitant de marteler les boutons de direction.

## 2. Architecture Technique & Outillage

- **Fichiers modifiés :**
  - `goal_src/jak2/engine/ui/progress/progress-h.gc` : ajout de champs de minuterie pour le throttle de répétition des entrées dans `progress-control`.
  - `goal_src/jak2/engine/ui/progress/progress.gc` : mise à jour de `respond-to-cpad` et de la vitesse de défilement de rotation du cercle pour correspondre aux vitesses de Jak 3.
  - `goal_src/jak2/pc/progress/progress-generic-pc.gc` : amélioration de la gestion de la navigation du menu d'options PC.
  - `goal_src/jak2/pc/progress/progress-pc.gc` : initialisation des variables de minuterie de répétition.
- **Systèmes moteur réutilisés (aucun nouveau code moteur) :**
  - La machine à états `progress-control` et la lecture des entrées `cpad` existantes — le mod ne fait que réajuster des constantes de timing et ajouter deux minuteries de throttle, il n'introduit aucun nouvel état d'UI.

## 3. Commandes & Procédure de Test

1. Sélectionner Jak 2 comme jeu actif :
   ```bash
   task set-game-jak2
   ```
2. Recompiler à chaud dans le REPL :
   ```lisp
   (mi)
   ```
3. Lancer le jeu :
   ```bash
   task boot-game
   ```
4. Appuyer sur `Start` / `Échap` pour entrer dans le menu Pause.
5. Utiliser la croix directionnelle ou le stick gauche (ou maintenir haut/bas/gauche/droite) pour naviguer dans le cercle d'options et constater le défilement vif et continu — le ressenti doit être identique à Jak 3.

## 4. Statut Actuel & Investigations

- **Stable / fonctionne comme prévu :** la vitesse de défilement doublée et le « maintenir pour répéter » se comportent comme prévu, à la manette comme au clavier, dans chaque sous-menu de progression.
- **Mod de configuration uniquement :** aucun asset, aucun nouveau type, aucun nouvel état — uniquement des constantes de timing et deux minuteries de throttle. Faible risque de conflit lors d'une fusion avec d'autres mods.
- **Non encore investigué :** si le throttle de répétition de 0,175s devrait être exposé comme réglage PC plutôt que codé en dur, et si la vitesse de défilement accrue nécessite un ajustement correspondant de la cadence du repère sonore du cercle.

## 5. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
|------|-------------------------|------------------------|----------|
| 2026-08-13 | `goal_src/jak2/engine/ui/progress/progress-h.gc`<br>`goal_src/jak2/engine/ui/progress/progress.gc`<br>`goal_src/jak2/pc/progress/progress-generic-pc.gc`<br>`goal_src/jak2/pc/progress/progress-pc.gc` | Doublement de la vitesse de rotation de défilement du cercle pour correspondre à Jak 3. Implémentation de la logique « maintenir pour répéter » avec un throttle de répétition de 0,175s pour la navigation Haut/Bas et Gauche/Droite. | Rendre la navigation du menu circulaire Start réactive et fluide comme dans Jak 3. |
| 2026-08-30 | `docs/modding/current_mod/start_menu_wheel_readme.md` (relocalisé depuis `docs/mods/`)<br>suppression des `docs/jak[123]_modding_utilities.md`, `docs/jak_modding_instructions.md`, `docs/mods/README.md` obsolètes | Relocalisation de ce readme vers le chemin mandaté `docs/modding/current_mod/`, passage en bilingue complet, ajout de la section « Statut Actuel & Investigations », et nettoyage de l'ancien arbre `docs/` plat resté sur cette branche. | Mettre la documentation du mod en conformité avec la directive de modding. |
