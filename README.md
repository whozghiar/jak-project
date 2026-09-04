# Dark Jak Enhanced (Mega-Mega Dark Jak & Titan Evolution) — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fdark_jak_enhanced-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
The **Dark Jak Enhanced** mod adds a full 3rd evolutionary stage to Dark Jak in Jak 2: the **Mega-Mega Dark Jak (Titan / Colossus)**, alongside critical quality-of-life improvements, restored acrobatics for Level 1 Dark Jak, instantaneous Dark Bomb activation, and enhanced collision resilience.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/dark_jak_enhanced`

## ✨ Key Features
- **Progressive 3-Tier Evolution (via `L2`):**
  - **1st `L2` Press (Normal Jak):** Transforms into **Classic Dark Jak** (scale x1.05).
  - **2nd `L2` Press (Dark Jak):** Evolves into **Mega Dark Jak / Dark Giant** (scale x2.0).
  - **3rd `L2` Press (Mega Dark Jak):** Evolves into **Mega-Mega Dark Jak / Titan** (scale x3.5).
  - *No story unlock required:* works directly during standard gameplay without debug cheats.
- **Manual De-Transformation (`R2`) & 100% Eco Drain:** Press `R2` at any time to immediately revert back to normal Jak. Dark eco reserve is 100% consumed upon transformation exit, regardless of cause (`R2` cancel, timer expiration, Dark Bomb, Dark Blast, or death).
- **Pristine Authentic HUD:** The original HUD is kept 100% authentic and unmodified.
- **Dynamic Panoramic Camera:** Automatic distance and height pull-back (`string-min-length 3.2`, `string-max-length 2.8`) for optimal framing of the colossal titan.
- **Heavy Footsteps & Seismic Screen-Shake:** Doubled screen-shake intensity on footfalls while walking and running as a titan.
- **Instant Dark Bomb Activation:** Pressing Square during any jump ascent or descent immediately cancels upward momentum for an instant, responsive dive plunge.
- **Collision-Resilient Dark Blast:** Dark Blast barrage no longer prematurely aborts when cast in confined interiors, under low ceilings, or touching obstacles.
- **Agile Roll & Roll-Flip for Level 1:** Restores rolling (`L1` in motion) and roll-flip jumps (`L1 + X`) exclusively for Level 1 Dark Jak, while keeping giant stages heavy and grounded.

## 🎮 Controls & Gameplay Summary
- **`L2`:** Transform / Evolve to next Dark Jak tier (Level 1 -> Mega Giant -> Titan).
- **`R2`:** Instant de-transformation back to normal Jak.
- **`L1` (in motion):** Roll (Level 1 Dark Jak only).
- **`L1 + X`:** Roll-flip jump (Level 1 Dark Jak only).
- **Square (in air):** Instant Dark Bomb plunge (cancels upward vertical momentum).
- **`L1 + Square`:** Dark Blast (stable in confined spaces).

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist.
- **Details:** Only GOAL scripts are modified (`target-h.gc`, `target-darkjak.gc`, `target-handler.gc`, `target-util.gc`, `target.gc`). No C++ rebuild needed. For a first-time build, use:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup).
- **Details:** Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
[![Demonstration Video](https://img.youtube.com/vi/eUS1cFZ_clg/maxresdefault.jpg)](https://youtu.be/eUS1cFZ_clg)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/eUS1cFZ_clg)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/dark_jak_enhanced_readme.md`](docs/modding/current_mod/dark_jak_enhanced_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Le mod **Dark Jak Enhanced** ajoute un troisième stade d'évolution complet pour Dark Jak dans Jak 2 : le **Méga-Méga Dark Jak (Titan / Colosse)**, accompagné d'améliorations majeures d'acrobatie, de contrôles instantanés et d'une robustesse accrue face aux collisions.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/dark_jak_enhanced`

## ✨ Fonctionnalités Clés
- **Évolution Progressive en 3 Stades (via `L2`) :**
  - **1ᵉʳ appui sur `L2` (Jak normal) :** Transformation en **Dark Jak classique** (taille x1.05).
  - **2ᵉ appui sur `L2` (Dark Jak) :** Évolution en **Méga Dark Jak / Dark Giant** (taille x2.0).
  - **3ᵉ appui sur `L2` (Méga Dark Jak) :** Évolution ultime en **Méga-Méga Dark Jak / Titan** (taille x3.5).
  - *Sans prérequis de triche :* disponible directement en cours de partie standard sans cheats.
- **Détransformation Manuelle (`R2`) & Consommation Totale de l'Éco :** Appui sur `R2` à tout moment pour revenir immédiatement à Jak normal. La réserve d'éco noire est vidée à 100% dès la sortie de Dark Jak, quelle que soit la cause (`R2`, fin du timer, Dark Bomb, Dark Blast, mort).
- **HUD Authentique et Intact :** Le HUD d'origine du jeu reste strictement intact et sans ajouts superflus.
- **Caméra Panoramique Dynamique :** Recul et élévation automatiques de la caméra (`string-min-length 3.2`, `string-max-length 2.8`) pour un cadrage optimal du colosse.
- **Foulées Lourdes & Secousses Sismiques :** Intensité doublée des secousses d'écran (`screen-shake`) lors des bruits de pas en marche et course en titan.
- **Déclenchement Instantané de la Dark Bomb :** L'appui sur Carré en l'air annule immédiatement la vélocité ascendante pour un plongeon rapide et percutant.
- **Dark Blast Résistant aux Collisions :** La salve d'éclairs ne s'annule plus prématurément dans les espaces confinés, sous des plafonds bas ou près d'obstacles.
- **Roulade & Roulade Sautée pour Dark Jak Niveau 1 :** Réactivation de la roulade (`L1` en mouvement) et de la roulade sautée (`L1 + Croix`) exclusivement pour Dark Jak Niveau 1, tout en maintenant la lourdeur imposante des stades géants.

## 🎮 Contrôles & Résumé Gameplay
- **`L2` :** Transformation / Évolution vers le stade supérieur (Niveau 1 -> Méga Giant -> Titan).
- **`R2` :** Annulation manuelle immédiate et retour à Jak normal.
- **`L1` (en mouvement) :** Roulade (Dark Jak Niveau 1 uniquement).
- **`L1 + Croix` :** Roulade sautée (Dark Jak Niveau 1 uniquement).
- **Carré (en l'air) :** Plongeon instantané en Dark Bomb.
- **`L1 + Carré` :** Dark Blast résistant aux collisions.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Couche 3 (GOAL uniquement) — Non requise si les binaires standards existent déjà.
- **Détails :** Seuls les scripts GOAL sont modifiés (`target-h.gc`, `target-darkjak.gc`, `target-handler.gc`, `target-util.gc`, `target.gc`). Aucune recompilation C++ n'est nécessaire. Pour un premier build :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation).
- **Détails :** Utilise les modèles, animations et bruitages natifs du jeu.
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou itérez rapidement via le REPL OpenGOAL avec `task repl`, puis rechargez à chaud avec `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
[![Vidéo de Démonstration](https://img.youtube.com/vi/eUS1cFZ_clg/maxresdefault.jpg)](https://youtu.be/eUS1cFZ_clg)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/eUS1cFZ_clg)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/dark_jak_enhanced_readme.md`](docs/modding/current_mod/dark_jak_enhanced_readme.md)

---
*(AI-assisted)*
