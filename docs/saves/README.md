# 100% Save Files Guide

> ### Summary
>
> [1. Overview & Contents](#1-overview--contents) · [2. Benefits of 100% Saves](#2-benefits-of-100-saves) · [3. Importing into the Base Game](#3-importing-into-the-base-game) · [4. Importing into OpenGOAL Launcher Mods](#4-importing-into-opengoal-launcher-mods) · [5. Save Slots Structure & Customization](#5-save-slots-structure--customization)

---

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
