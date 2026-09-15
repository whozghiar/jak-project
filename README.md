# Interactive & Vulnerable Yakows / Yakows Interactifs et Vulnérables

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fyakow_killable-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
Makes the peaceful Yakow farm animals killable and protected by Krimzon law. Striking a Yakow immediately triggers a Krimzon Guard alert ("Hands off the cow!"), while defeating it drops dark eco pills with authentic death VFX.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/yakow_killable`

## ✨ Key Features
- **Feature:** Yakows are now vulnerable and killable, taking damage from player attacks.
- **Feature:** Striking a Yakow instantly triggers Krimzon Guard Alert Level 1 ("Hands off the cow!").
- **Feature:** Purple dissolution death VFX and drops 6 Dark Eco pills upon defeat.

## 📥 Download & Play via OpenGOAL Launcher (Players)

> [!TIP]
> **No developer environment required!** You can install and play this mod directly using the official OpenGOAL Launcher:

### Option A — Add Custom Mod Source (Recommended)
1. In the **OpenGOAL Launcher**, navigate to **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Paste this catalog URL:
   ```text
   https://raw.githubusercontent.com/whozghiar/jak-project/jak2/features/yakow_killable/index.json
   ```
3. Go to the **Mods** tab, locate **Interactive & Vulnerable Yakows**, and click **Install**.
4. Select your clean PS2 Jak II ISO when prompted. The launcher will automatically extract assets and launch the game!

### Option B — Manual Installation from GitHub Releases
1. Download the pre-built package for your operating system from the [Releases](https://github.com/whozghiar/jak-project/releases) tab (`windows-v*.zip` or `linux-v*.zip`).
2. Extract the archive into your OpenGOAL Launcher features directory:
   - **Windows:** `%APPDATA%\OpenGOAL-Launcher\features\jak2\mods\_local\yakow_killable\`
   - **Linux:** `~/.config/OpenGOAL-Launcher/features/jak2/mods/_local/yakow_killable/`
3. Launch the game from the OpenGOAL Launcher.

---

## 🛠️ Developer Setup & Local Compilation

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Layer 3 (GOAL only) — Not required if standard binaries already exist
- **Details:** Only GOAL scripts are modified. No C++ rebuild needed. For first-time build, use the fast targeted task:
```bash
task build-release-game
```

### 3. Asset Extraction
- **Status:** Standard extraction sufficient (once per setup)
- **Details:** Standard extraction sufficient. Uses native in-game models, animations, and sound effects.
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or iterate fast via the OpenGOAL REPL using `task repl`, then hot-reload with `(mi)` and `(r)`).*

### 5. Enable the Mod (OFF by default)
This mod ships **disabled** — a fresh install leaves the farm Yakows as the stock invulnerable animals. Open the in-game Mods menu with **L3 + SELECT** (operates in retail boot, no debug mode required):
```text
Mods ▸ yakow-killable ▸ Enable
```

## 🎥 Demonstration Video

[![Demonstration Video](https://img.youtube.com/vi/njKxjCuEpcU/maxresdefault.jpg)](https://youtu.be/njKxjCuEpcU)

▶️ **[Watch the demonstration video on YouTube](https://youtu.be/njKxjCuEpcU)**

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
Rend les Yakows pacifiques de la ferme vulnérables et protégés par la loi Krimzon. Frapper un Yakow déclenche immédiatement une alerte des Gardes Krimzon ("Touche pas à la vache !"), tandis que l'éliminer fait apparaître des pilules d'éco noire avec des effets visuels de dissolution violette.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/yakow_killable`

## ✨ Fonctionnalités Clés
- **Fonctionnalité :** Les Yakows sont vulnérables et peuvent être vaincus par les attaques du joueur.
- **Fonctionnalité :** Frapper un Yakow déclenche instantanément l'Alerte Niveau 1 des Krimzon Guards.
- **Fonctionnalité :** Effet visuel de dissolution violette et chute de 6 pilules d'éco noire à leur défaite.

## 📥 Téléchargement & Installation via OpenGOAL Launcher (Joueurs)

> [!TIP]
> **Aucun environnement de compilation requis !** Vous pouvez installer et jouer à ce mod directement depuis l'OpenGOAL Launcher officiel :

### Option A — Ajouter une Source de Mod Personnalisée (Recommandé)
1. Dans l'**OpenGOAL Launcher**, rendez-vous dans **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Collez l'URL suivante pointant vers le catalogue du mod :
   ```text
   https://raw.githubusercontent.com/whozghiar/jak-project/jak2/features/yakow_killable/index.json
   ```
3. Allez dans l'onglet **Mods**, sélectionnez **Interactive & Vulnerable Yakows** et cliquez sur **Install**.
4. Fournissez votre ISO PS2 de Jak II propre lorsque demandé. Le launcher s'occupe de tout !

### Option B — Installation Manuelle depuis les Releases GitHub
1. Téléchargez l'archive correspondant à votre OS dans l'onglet [Releases](https://github.com/whozghiar/jak-project/releases) (`windows-v*.zip` ou `linux-v*.zip`).
2. Décompressez l'archive dans le répertoire des mods de votre OpenGOAL Launcher :
   - **Windows :** `%APPDATA%\OpenGOAL-Launcher\features\jak2\mods\_local\yakow_killable\`
   - **Linux :** `~/.config/OpenGOAL-Launcher/features/jak2/mods/_local/yakow_killable/`
3. Lancez le jeu directement depuis le launcher.

---

## 🛠️ Guide Développeur & Compilation Locale

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Layer 3 (GOAL uniquement) — Non requise si les binaires existent déjà
- **Détails :** Seuls les scripts GOAL sont modifiés. En cas de premier build machine :
```bash
task build-release-game
```

### 3. Extraction des Données (Assets)
- **Statut :** Extraction standard suffisante (une seule fois à l'installation)
```bash
task extract
```

### 4. Lancer le Jeu
```bash
task boot-game
```

### 5. Activer le Mod (DÉSACTIVÉ par défaut)
Ce mod est livré **désactivé** — une installation neuve conserve les Yakows de la ferme invulnérables comme dans le jeu d'origine. Ouvrez le menu Mods en jeu avec **L3 + SELECT** (fonctionne en boot retail, sans mode debug) :
```text
Mods ▸ yakow-killable ▸ Enable
```

## 🎥 Encart Vidéo Démonstrative

[![Vidéo de Démonstration](https://img.youtube.com/vi/njKxjCuEpcU/maxresdefault.jpg)](https://youtu.be/njKxjCuEpcU)

▶️ **[Visionner la vidéo de démonstration sur YouTube](https://youtu.be/njKxjCuEpcU)**

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`docs/modding/current_mod/yakow_killable_readme.md`](docs/modding/current_mod/yakow_killable_readme.md)
