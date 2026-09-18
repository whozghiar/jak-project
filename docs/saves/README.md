# 💾 100% Save Files Guide / Guide des Sauvegardes 100%

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Audience / Public :** Players & Mod Developers / Joueurs & Développeurs de Mods
> - **Applies to / Concerne :** Jak 1, Jak 2, Jak 3 (Vanilla Game & Mods / Jeu de Base & Mods)
> - **Origin / Provenance :** `master-dev`

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Overview & Contents](#1-overview--contents) · [2. Benefits of 100% Saves](#2-benefits-of-100-saves) · [3. Importing into the Base Game](#3-importing-into-the-base-game) · [4. Importing into OpenGOAL Launcher Mods](#4-importing-into-opengoal-launcher-mods) · [5. Save Slots Structure & Customization](#5-save-slots-structure--customization)
> - 🇫🇷 **Français :** [1. Présentation & Contenu](#1-présentation--contenu) · [2. Avantages des Sauvegardes 100%](#2-avantages-des-sauvegardes-100) · [3. Importer dans le Jeu de Base](#3-importer-dans-le-jeu-de-base) · [4. Importer dans les Mods du Launcher OpenGOAL](#4-importer-dans-les-mods-du-launcher-opengoal) · [5. Structure des Emplacements & Personnalisation](#5-structure-des-emplacements--personnalisation)

---

# 🇬🇧 English Version

## 1. Overview & Contents

This directory contains **100% completion save files** for the OpenGOAL releases of the trilogy:
- **Jak 1: The Precursor Legacy** (`docs/saves/jak1/`)
- **Jak 2: Renegade** (`docs/saves/jak2/`)
- **Jak 3** (`docs/saves/jak3/`)

Each save file has all main story missions completed, all collectibles collected (Power Cells, Precursor Orbs, Scout Flies, Skull Gems), secret features and cheats unlocked, and all weapons/abilities available.

These save files are fully cross-compatible: you can use them in the **vanilla base game** as well as in any **custom mod**.

---

## 2. Benefits of 100% Saves

Using a 100% completion save file provides several key advantages:
- **Instant Mod Access:** Many mods introduce post-game mechanics, end-game areas, weapon variants, or city-wide modifications (such as *Peaceful Haven City*, custom hoverboard physics, or vehicle upgrades). A 100% save lets you jump straight into the mod features without needing to replay the entire campaign from scratch.
- **Full Sandbox Freedom:** All city sectors, level warps, weapons, morph gun attachments, and secrets are instantly accessible.
- **Testing & Playtesting:** Ideal for mod developers and testers who need to quickly verify behaviors in late-game zones or under maximum equipment conditions.

---

## 3. Importing into the Base Game

To import a 100% save into the standalone/vanilla OpenGOAL installation:

### Target Directory Paths

- **Windows:**
  ```text
  %APPDATA%\Roaming\OpenGOAL\jak[x]\saves
  ```
  *(or `%APPDATA%\OpenGOAL\jak[x]\saves` — which expands to `C:\Users\<YourUsername>\AppData\Roaming\OpenGOAL\jak[x]\saves`)*
  - For **Jak 1:** `%APPDATA%\Roaming\OpenGOAL\jak1\saves`
  - For **Jak 2:** `%APPDATA%\Roaming\OpenGOAL\jak2\saves`
  - For **Jak 3:** `%APPDATA%\Roaming\OpenGOAL\jak3\saves`

- **Linux:**
  ```text
  ~/.config/OpenGOAL/jak[x]/saves
  ```

### Step-by-Step Installation

1. **Close the game** completely.
2. Navigate to your base game save folder (e.g. `%APPDATA%\Roaming\OpenGOAL\jak2\saves`).
3. *(Recommended)* Back up your existing saves by copying them to a safe location.
4. Copy the entire contents from `docs/saves/jak[x]/saves/` (the `BASCUS-...` directory containing the `.bin` bank files) directly into your target `saves` directory, overwriting existing files when prompted.
5. Launch the game. OpenGOAL automatically restores **Save Slot 1 (`bank0.bin`)** by default on boot.

---

## 4. Importing into OpenGOAL Launcher Mods

When you install and run a mod via the **OpenGOAL Launcher**, the launcher creates a separate, sandboxed profile directory to store settings and save games independently from the vanilla game.

### Mod Target Directory Path

Each mod creates its own `saves` directory inside the OpenGOAL Launcher installation tree, typically structured as follows:

```text
<OpenGOAL_Launcher_Install_Dir>/features/jak[x]/mods/[mod_name]/_settings/[mod_name]/OpenGoal/jak[x]/saves
```

*Example for a Jak 2 mod named `peaceful-haven-city`:*
```text
OpenGoal/features/jak2/mods/peaceful-haven-city/_settings/peaceful-haven-city/OpenGoal/jak2/saves
```

### Step-by-Step Installation

1. **Close the mod** if it is currently running.
2. Open your file explorer and navigate to the mod's specific save directory:
   `<Launcher_Path>/features/jak[x]/mods/[mod_name]/_settings/[mod_name]/OpenGoal/jak[x]/saves/`
3. *(Recommended)* Create a backup copy of any current saves in that folder.
4. **Replace the contents** of that `saves` folder with the contents from `docs/saves/jak[x]/saves/` (e.g. the `BASCUS-97265AYBABTU!` folder for Jak 2).
5. Launch the mod from the OpenGOAL Launcher: all campaign progress, weapons, and secrets will be 100% unlocked immediately!

---

## 5. Save Slots Structure & Customization

OpenGOAL models PS2 Memory Card directory structures:

```text
saves/
└── BASCUS-97265AYBABTU!/    # Regional Title ID (e.g. Jak 2 NTSC-U)
    ├── bank0.bin            # In-game Save Slot 1 (Auto-loaded on cold boot)
    ├── bank1.bin            # In-game Save Slot 2
    ├── bank2.bin            # In-game Save Slot 3
    ├── bank3.bin            # In-game Save Slot 4
    └── ...
```

> [!TIP]
> - **Preserve your personal save:** If you already have your own playthrough in Slot 1 and do not want to overwrite it, you can rename `bank0.bin` from this guide to `bank1.bin` (Slot 2) or `bank2.bin` (Slot 3) before copying. You can then load it in-game from the Pause Menu > Options > Load Game.
> - **Default Cold Boot:** OpenGOAL always loads `bank0.bin` automatically at launch if present.

---

# 🇫🇷 Version Française

## 1. Présentation & Contenu

Ce répertoire met à disposition des **sauvegardes terminées à 100%** pour les trois volets de la trilogie portés sous OpenGOAL :
- **Jak 1: The Precursor Legacy** (`docs/saves/jak1/`)
- **Jak 2: Hors-la-loi** (`docs/saves/jak2/`)
- **Jak 3** (`docs/saves/jak3/`)

Chaque sauvegarde dispose de l'intégralité des missions principales terminées, de tous les objets à collecter obtenus (Piles d'Énergie, Orbes Précurseurs, Mouches Éclaireuses, Gemmes de Crâne), des secrets et codes de triche débloqués, ainsi que de tout l'arsenal et des capacités au maximum.

Ces sauvegardes sont pleinement compatibles : vous pouvez les utiliser à la fois sur le **jeu original de base** et sur **n'importe quel mod**.

---

## 2. Avantages des Sauvegardes 100%

Utiliser une sauvegarde à 100% apporte plusieurs avantages considérables :
- **Accès Immédiat aux Fonctionnalités des Mods :** Beaucoup de mods s'appuient sur des fonctionnalités de fin de jeu, des zones avancées, des variantes d'armes ou des modifications globales de la ville (*Haven City Pacifiée*, physique modifiée du JetBoard, améliorations de véhicules, etc.). Une sauvegarde 100% vous permet de profiter immédiatement du mod sans devoir recommencer et terminer toute la campagne.
- **Liberté Totale en Mode Bac à Sable (Sandbox) :** Tous les quartiers de la ville, téléporteurs de niveaux, armes, extensions du Morph Gun et secrets sont accessibles instantanément.
- **Idéal pour les Tests et Développeurs de Mods :** Les créateurs et bêta-testeurs peuvent instantanément tester leurs ajouts dans les niveaux finaux ou avec l'équipement complet.

---

## 3. Importer dans le Jeu de Base

Pour importer une sauvegarde à 100% dans votre installation OpenGOAL classique (jeu de base hors mods) :

### Emplacement des Dossiers Cibles

- **Windows :**
  ```text
  %appdata%\Roaming\OpenGOAL\jak[x]\saves
  ```
  *(ou `%APPDATA%\OpenGOAL\jak[x]\saves` — correspondant à `C:\Users\<VotreNomUtilisateur>\AppData\Roaming\OpenGOAL\jak[x]\saves`)*
  - Pour **Jak 1 :** `%appdata%\Roaming\OpenGOAL\jak1\saves`
  - Pour **Jak 2 :** `%appdata%\Roaming\OpenGOAL\jak2\saves`
  - Pour **Jak 3 :** `%appdata%\Roaming\OpenGOAL\jak3\saves`

- **Linux :**
  ```text
  ~/.config/OpenGOAL/jak[x]/saves
  ```

### Procédure d'Installation Étape par Étape

1. **Fermez complètement le jeu.**
2. Rendez-vous dans le dossier de sauvegarde du jeu de base (par exemple : `%appdata%\Roaming\OpenGOAL\jak2\saves`).
3. *(Recommandé)* Faites une copie de sauvegarde préventive de vos sauvegardes actuelles.
4. Copiez l'intégralité du contenu du dossier `docs/saves/jak[x]/saves/` (le répertoire `BASCUS-...` contenant les fichiers `bank*.bin`) directement dans votre dossier `saves` cible en écrasant les fichiers existants.
5. Lancez le jeu. OpenGOAL restaure automatiquement l'**Emplacement 1 (`bank0.bin`)** lors du démarrage.

---

## 4. Importer dans les Mods du Launcher OpenGOAL

Lorsque vous installez et lancez un mod via le **Launcher OpenGOAL officiel**, ce dernier génère un environnement isolé (sandbox) pour chaque mod, séparant les réglages et les sauvegardes du jeu de base.

### Emplacement Cible dans le Launcher

Chaque mod dispose de son propre dossier de sauvegarde situé dans l'arborescence d'installation du Launcher OpenGOAL, généralement sous la forme :

```text
<Dossier_Installation_OpenGOAL>/features/jak[x]/mods/[nom_du_mod]/_settings/[nom_du_mod]/OpenGoal/jak[x]/saves
```

*Exemple pour un mod Jak 2 nommé `peaceful-haven-city` :*
```text
OpenGoal/features/jak2/mods/peaceful-haven-city/_settings/peaceful-haven-city/OpenGoal/jak2/saves
```

### Procédure d'Installation Étape par Étape

1. **Fermez le mod** s'il est en cours d'exécution.
2. Ouvrez l'explorateur de fichiers et naviguez jusqu'au répertoire de sauvegarde spécifique du mod :
   `<Dossier_Launcher>/features/jak[x]/mods/[nom_du_mod]/_settings/[nom_du_mod]/OpenGoal/jak[x]/saves/`
3. *(Recommandé)* Effectuez une copie de sauvegarde de vos données existantes.
4. **Remplacez le contenu** de ce dossier `saves` par le contenu présent dans `docs/saves/jak[x]/saves/` (par exemple le dossier `BASCUS-97265AYBABTU!` pour Jak 2).
5. Lancez le mod depuis le Launcher OpenGOAL : votre progression sera instantanément à 100%, avec toutes les armes et secrets disponibles !

---

## 5. Structure des Emplacements & Personnalisation

OpenGOAL réplique l'arborescence d'une carte mémoire PS2 :

```text
saves/
└── BASCUS-97265AYBABTU!/    # Identifiant Régional (ex: Jak 2 NTSC-U)
    ├── bank0.bin            # Emplacement de sauvegarde 1 (Chargé automatiquement au démarrage)
    ├── bank1.bin            # Emplacement de sauvegarde 2
    ├── bank2.bin            # Emplacement de sauvegarde 3
    ├── bank3.bin            # Emplacement de sauvegarde 4
    └── ...
```

> [!TIP]
> - **Conserver votre propre partie :** Si vous avez déjà une partie personnelle sur l'Emplacement 1 et ne souhaitez pas l'écraser, vous pouvez renommer `bank0.bin` issu de ce guide en `bank1.bin` (Emplacement 2) ou `bank2.bin` (Emplacement 3) avant la copie. Il vous suffira de charger l'emplacement correspondant via le Menu Pause > Options > Charger Partie.
> - **Chargement par défaut au démarrage :** OpenGOAL recharge systématiquement le fichier `bank0.bin` au boot s'il existe.
