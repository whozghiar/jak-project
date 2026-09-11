# Paddy Wagon Traffic — Jak 2

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-Jak%202-orange.svg" alt="Target Game">
  <img src="https://img.shields.io/badge/Branch-jak2%2Ffeatures%2Fpaddywagon%2Ftraffic-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview

The Krimzon Guard **paddy wagon** — the armoured prisoner van you chase during
*Escort Brutter* — now drives Haven City's ordinary street traffic, with a
**civilian prisoner standing arms-crossed in the rear cage** and a **Crimson
Guard at the controls**. It is a real guard vehicle: red dot on the minimap,
joins the hunt during an alert, and **can be boarded and driven** — stealing it
raises the city alarm exactly like stealing a hellcat or a guard bike.

- **Target Game:** Jak 2
- **Active Branch:** `jak2/features/paddywagon/traffic`

## ✨ Key Features

- **A paddy wagon in ordinary traffic.** `paddywagon-v` is a `vehicle-guard`
  woven into the city's ground traffic pool (up to 2 at a time). It uses the
  retail `paddy-wagon` hull and its retail physics constants, so it drives and
  handles exactly like the mission van.
- **A random civilian prisoner in the cage.** Every wagon carries a `norm`,
  `fat` or `chick` citizen standing in the rear compartment, dressed from the
  same random wardrobe as the pedestrians in the street. `norm` and `fat` hold
  the retail *arms-crossed* pose; `chick` stands at ease (retail has no
  arms-crossed animation for that body type).
- **Crimson Guard driver.** The regular red `crimson-guard-rider`, in the same
  pose it uses in a hellcat.
- **Drivable and stealable like any guard ship.** Walk up for the "press
  triangle" prompt, or hang off a flank rail first if it is passing above you,
  then take it. The guard is thrown clear, the city alert jumps and a Crimson
  Guard respawns on the street — all the stock guard-vehicle theft behaviour.
  The prisoner stays locked in his cage and rides along with you.
- **It runs when you shoot it.** A van carrying a prisoner does not stop to
  fight: take a shot at one and it floors the throttle, pushes past traffic and
  takes every turn that leads away from you for the next 12 seconds, never
  turning to give chase.
- **Both traffic lanes, and your gun stays out.** Once you are driving, **R2**
  drops the wagon from the high air lane down to the low one and back up, and
  **R1** fires Jak's own weapon — the wagon handles like a car in that respect,
  not like a hellcat.

## 🎮 Controls & Usage

Only while Jak is piloting the paddy wagon:

| Input | Action |
|---|---|
| **Triangle** (near the wagon) | Board it — or grab a side rail and hang, if it is passing above you |
| **Triangle** (while hanging) | Climb in and take the controls (this is the theft — the alarm goes off) |
| **R2** | Toggle between the **high air lane** (the default) and the **low lane** |
| **R1** | Fire Jak's equipped gun while driving |
| **Triangle** (while driving) | Get out |

Everything else — throttle, steering, brake, boost — is the standard city
vehicle control set.
- **Unarmed.** The `paddy-wagon` skeleton has no gun joint, so the wagon rams
  and pursues but never shoots.
- **OFF by default,** switchable from `Debug ▸ Mods ▸ paddywagon-traffic`.

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting Jak 2:
```bash
task set-game-jak2
```

### 2. Binary Compilation
- **Status:** Not required — no C++ was changed. The stock `gk` / `goalc` /
  `decompiler` binaries are sufficient.
- **Details:** This mod only touches GOAL sources, `.gd` DGO manifests and one
  `decompiler/config` **data** key (`extra_art_groups_by_dgo`), which the
  existing decompiler already understands. If your `out/build` is empty, build
  once with `task build-release`.

### 3. Asset Extraction
- **Status:** **Required — `task extract`.**
- **Details:** The paddy wagon's merc geometry only ever shipped in
  `LMEETBRT.DGO`. `extra_art_groups_by_dgo` bakes it into `lwidea.fr3`,
  `lwideb.fr3` and `lwidec.fr3` so the model is renderable in free roam.
  **Without this step the wagon is completely invisible** (the process still
  runs — sounds, collision and the riders are all there).
```bash
task extract
```

### 4. Launch the Game
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*

### 5. Enable the Mod
The mod ships **OFF**. In game:
`Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable`, then **reload the city** (walk
into an interior and back out, or warp) so the traffic manager re-reads its
want-counts. Drive around Haven City and watch for a boxy armoured van in the
car lanes with a figure standing in the back.

## 🎥 Demonstration Video

[![Demonstration Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Watch the demonstration video on YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Demonstration videos must be hosted externally on YouTube to prevent repository bloating. Replace `YOUR_VIDEO_ID` with the YouTube video ID (e.g. `MnqnybexhSA`) and `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` with the video URL (e.g. `https://youtu.be/MnqnybexhSA`).*

## ✅ Compliance Checklist
- [x] **Native non-regression:** with the mod compiled but its toggle OFF, the traffic want-count for slot 20 is 0, so no `paddywagon-v` is ever constructed and no code in `paddywagon-v.gc` runs. The retail `paddywagon` type and the *Escort Brutter* mission are untouched.
- [x] **Debug ▸ Mods toggle:** registered via `(mods-menu-register "paddywagon-traffic" ...)` in [`goal_src/jak2/pc/debug/paddywagon-traffic-menu.gc`](goal_src/jak2/pc/debug/paddywagon-traffic-menu.gc). See [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [x] **No direct `default-menu*.gc` edits.**
- [x] **Symbols prefixed** with the mod slug (`*mod-paddywagon-traffic-enable*`, `mod-paddywagon-traffic-build-menu`, `paddywagon-v*`, `paddywagon-prisoner*`).
- [ ] **Verified Lisp instructions** used by this mod are present in `docs/modding/jak2_lisp_instructions.md` (landed on `master-dev` via `task modding-land-doc`).
- [x] **In-code comments** on every new/overridden type, method, state, macro.

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`docs/modding/current_mod/paddywagon_traffic_readme.md`](docs/modding/current_mod/paddywagon_traffic_readme.md)

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod

Le **fourgon cellulaire** de la Garde Grenat — le véhicule blindé que l'on
poursuit pendant *Escorter Brutter* — circule désormais dans le trafic urbain
ordinaire d'Abriville, avec un **civil prisonnier debout, bras croisés, dans la
cage arrière** et un **Garde Grenat aux commandes**. C'est un véritable véhicule
de garde : point rouge sur la carte, il rejoint la chasse pendant une alerte, et
il **peut être pris en main et conduit** — le voler déclenche l'alarme de la
ville exactement comme voler un hellcat ou une moto de garde.

- **Jeu Ciblé :** Jak 2
- **Branche Active :** `jak2/features/paddywagon/traffic`

## ✨ Fonctionnalités Clés

- **Un fourgon cellulaire dans le trafic ordinaire.** `paddywagon-v` est un
  `vehicle-guard` intégré au pool de trafic terrestre de la ville (2 au maximum
  simultanément). Il utilise la coque `paddy-wagon` d'origine et ses constantes
  physiques d'origine : il se conduit exactement comme le fourgon de mission.
- **Un prisonnier civil aléatoire dans la cage.** Chaque fourgon transporte un
  citoyen `norm`, `fat` ou `chick` debout dans le compartiment arrière, habillé
  dans la même garde-robe aléatoire que les piétons de la rue. `norm` et `fat`
  tiennent la pose *bras croisés* d'origine ; `chick` se tient au repos (le jeu
  d'origine ne possède aucune animation bras croisés pour ce gabarit).
- **Chauffeur Garde Grenat.** Le `crimson-guard-rider` rouge habituel, dans la
  même posture que dans un hellcat.
- **Conductible et volable comme tout vaisseau grenagarde.** Approchez-vous pour
  l'invite « triangle », ou suspendez-vous d'abord à une rambarde latérale s'il
  passe au-dessus de vous, puis emparez-vous-en. Le garde est éjecté, l'alerte
  de la ville monte et un Garde Grenat réapparaît dans la rue — tout le
  comportement standard de vol d'un véhicule de garde. Le prisonnier, lui, reste
  enfermé dans sa cage et vous accompagne.
- **Il fuit quand on lui tire dessus.** Un fourgon qui transporte un prisonnier
  ne s'arrête pas pour combattre : tirez dessus et il accélère à fond, force le
  passage dans le trafic et prend systématiquement les virages qui l'éloignent
  de vous pendant 12 secondes, sans jamais se retourner pour vous poursuivre.
- **Les deux couloirs de circulation, arme au poing.** Une fois aux commandes,
  **R2** fait descendre le fourgon du couloir aérien haut vers le couloir bas et
  inversement, et **R1** tire avec l'arme de Jak — de ce point de vue le fourgon
  se comporte comme une voiture, pas comme un hellcat.

## 🎮 Commandes & Utilisation

Uniquement lorsque Jak pilote le fourgon :

| Touche | Action |
|---|---|
| **Triangle** (près du fourgon) | Monter à bord — ou agripper une rambarde latérale et se suspendre, s'il passe au-dessus de vous |
| **Triangle** (suspendu) | Grimper et prendre les commandes (c'est le vol — l'alarme se déclenche) |
| **R2** | Basculer entre le **couloir aérien haut** (par défaut) et le **couloir bas** |
| **R1** | Tirer avec l'arme équipée de Jak tout en conduisant |
| **Triangle** (en conduisant) | Descendre |

Tout le reste — accélérateur, direction, frein, boost — correspond aux commandes
standard des véhicules urbains.
- **Non armé.** Le squelette `paddy-wagon` ne possède aucun joint d'arme : le
  fourgon percute et poursuit, mais ne tire jamais.
- **Désactivé par défaut,** activable depuis `Debug ▸ Mods ▸ paddywagon-traffic`.

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible Jak 2 :
```bash
task set-game-jak2
```

### 2. Compilation des Binaires
- **Statut :** Non requise — aucun C++ n'a été modifié. Les binaires `gk` /
  `goalc` / `decompiler` standards suffisent.
- **Détails :** Ce mod ne touche que des sources GOAL, des manifestes DGO `.gd`
  et une clé de **données** dans `decompiler/config`
  (`extra_art_groups_by_dgo`), que le décompilateur existant sait déjà lire. Si
  votre `out/build` est vide, compilez une fois avec `task build-release`.

### 3. Extraction des Données (Assets)
- **Statut :** **Requise — `task extract`.**
- **Détails :** La géométrie merc du fourgon n'a jamais existé que dans
  `LMEETBRT.DGO`. `extra_art_groups_by_dgo` la cuit dans `lwidea.fr3`,
  `lwideb.fr3` et `lwidec.fr3` pour que le modèle soit affichable en monde
  ouvert. **Sans cette étape, le fourgon est totalement invisible** (le process
  tourne pourtant : sons, collisions et occupants sont bien là).
```bash
task extract
```

### 4. Lancer le Jeu
```bash
task boot-game
```
*(Ou lancez via le REPL OpenGOAL avec `task repl`, puis compilez et lancez avec `(mi)` et `(r)`).*

### 5. Activer le Mod
Le mod est livré **désactivé**. En jeu :
`Debug ▸ Mods ▸ paddywagon-traffic ▸ Enable`, puis **rechargez la ville**
(entrez dans un intérieur et ressortez, ou téléportez-vous) pour que le
gestionnaire de trafic relise ses quotas. Roulez dans Abriville et guettez un
van blindé anguleux dans les voies de circulation, avec une silhouette debout à
l'arrière.

## 🎥 Vidéo Démonstrative

[![Vidéo Démonstrative](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

▶️ **[Voir la vidéo de démonstration sur YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**

> [!NOTE]
> *Les vidéos de démonstration doivent être hébergées sur YouTube afin d'éviter d'alourdir le dépôt. Remplacez `YOUR_VIDEO_ID` par l'identifiant de la vidéo YouTube (ex. `MnqnybexhSA`) et `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` par l'URL (ex. `https://youtu.be/MnqnybexhSA`).*

## ✅ Checklist de Conformité
- [x] **Non-régression native :** mod compilé mais toggle OFF, le quota de trafic du slot 20 vaut 0 : aucun `paddywagon-v` n'est jamais construit et aucun code de `paddywagon-v.gc` ne s'exécute. Le type `paddywagon` d'origine et la mission *Escorter Brutter* sont intacts.
- [x] **Toggle Debug ▸ Mods :** enregistré via `(mods-menu-register "paddywagon-traffic" ...)` dans [`goal_src/jak2/pc/debug/paddywagon-traffic-menu.gc`](goal_src/jak2/pc/debug/paddywagon-traffic-menu.gc). Voir [`docs/modding/tools/mods_debug_menu.md`](docs/modding/tools/mods_debug_menu.md).
- [x] **Aucune édition directe de `default-menu*.gc`.**
- [x] **Symboles préfixés** par le slug du mod (`*mod-paddywagon-traffic-enable*`, `mod-paddywagon-traffic-build-menu`, `paddywagon-v*`, `paddywagon-prisoner*`).
- [ ] **Instructions Lisp vérifiées** utilisées par ce mod présentes dans `docs/modding/jak2_lisp_instructions.md` (déposées sur `master-dev` via `task modding-land-doc`).
- [x] **Commentaires dans le code** sur chaque type, méthode, état, macro ajouté ou surchargé.

## 📖 Documentation Technique
Pour le détail technique complet, l'architecture et les notes de développement :
- 📄 [`docs/modding/current_mod/paddywagon_traffic_readme.md`](docs/modding/current_mod/paddywagon_traffic_readme.md)
