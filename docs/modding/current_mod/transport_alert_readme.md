# Crimson Guard Alert Drop-Ship — Mod Readme / Transport de Troupes d'Alerte — Readme de Mod

> - **Branch / Branche :** `jak2/features/transport_alert`
> - **Game / Jeu :** Jak II (OpenGOAL)
> - **Status / Statut :** Working — scripted troop transport tied to the city alert level, ~1 per minute / Fonctionnel — transport de troupes scripté lié au niveau d'alerte, ~1 par minute
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

## 🇬🇧 English Version

### 1. Overview & Objective

While Haven City is on **alert (level ≥ 1)**, a **Crimson Guard Troop Transport** (`transport-ag`, the retail drop-ship) descends near the player roughly **once per minute**, deploys a squad of Crimson Guards, and leaves. It is a *scripted* actor — you cannot board it, and it is not part of the ambient traffic pool.

This is the sibling branch of `jak2/features/transport_traffic` (the drivable, traffic-integrated gunship). They share only the `.fr3` merc-geometry injection that makes the transport hull renderable in free-roam.

### 2. How it works

| Piece | File | What it does |
|---|---|---|
| `update-alert-transport` | `traffic-manager.gc` | New `traffic-manager` method, called every frame from `active:post`. Polls the alert level; when it's ≥ 1 and the 1-per-minute cooldown has elapsed and no transport is currently alive, it `process-spawn`s a `transport` at a random point 10–18 m from the player. |
| `alert-transport` / `alert-transport-next-check` | `traffic-manager.gc` | New fields: a handle to the live drop-ship and the earliest `current-time` the next one may spawn. Initialised in `reset-and-init` and `traffic-manager-init-by-other`. |
| scripted `transport` | `transport.gc` (retail) | Unmodified retail drop-ship logic — `come-down` → `idle` (hatch open, `transport-method-33` guard drops, `max-guard` 8) → `leave`. One line added: `(ctywide-entity-hack)` in `transport-init-by-other` so the runtime-spawned transport (which has no `entity-actor`) can still resolve its skeleton art. |
| `.fr3` merc injection | `jak2_config.jsonc`, `lwide{a,b,c}.gd` | `extra_art_groups_by_dgo` bakes `transport-ag`'s merc geometry (textures resolved via `LPROTECT`'s remap table) into the always-resident `lwidea/lwideb/lwidec.fr3`. Without this the PC merc renderer silently skips the hull (`num_missing_models++`). See [utility #18](../jak2_modding_utilities/18_merc_geometry_fr3_residency.md). |

**Cooldown / rate:** the `alert-transport-next-check` timer is set to `current-time + 60 s` at the moment a transport spawns, and case 1 of the `cond` blocks any new spawn while one is still alive — so the effective rate never exceeds **one drop-ship per minute**.

### 3. Rendering — the merc geometry `.fr3` injection

`transport-ag`'s hull geometry only ever shipped in `lprotect/ctykora/forestb/nest`, none of which are resident while free-roaming Haven City. The fix (in `decompiler/config/jak2/jak2_config.jsonc`):

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEA.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEB.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEC.DGO": ["transport-ag:LPROTECT.DGO"]
}
```

This bakes the geometry into `lwidea.fr3 / lwideb.fr3 / lwidec.fr3` (always borrowed into `ctywide` slot 1 in free-roam). The matching `transport-ag.go` + `tpage-2869.go` entries are added to `lwidea.gd / lwideb.gd / lwidec.gd`. No runtime level-borrow.

> **Requires a re-extraction** (`task extract`) so the three `.fr3` are rebuilt with the injected geometry.

### 4. How to Test

1. **Extract (once):** `task extract` — rebuilds `lwide*.fr3` with `transport-ag`.
2. **Rebuild:** `task repl` then `(mi)` (the `traffic-manager` deftype changed — restart the REPL if `(mi)` complains).
3. **Launch:** `task boot-game`, enter Haven City free-roam.
4. **Trigger:** aggro a Crimson Guard to raise the alert level.
5. **Observe:** within a few seconds a transport descends 10–18 m from you, its hatch opens, ~8 guards drop out, and it flies off. The console prints `AT: transport drop spawned ...`.
6. **Rate:** stay on alert — the next transport should not appear until ~60 s after the previous one spawned.

**Key source files:**

- `goal_src/jak2/levels/city/traffic/traffic-manager.gc` — `update-alert-transport` + fields + call site.
- `goal_src/jak2/levels/city/traffic/vehicle/transport.gc` — `(ctywide-entity-hack)` line.
- `decompiler/config/jak2/jak2_config.jsonc`, `goal_src/jak2/dgos/lwide{a,b,c}.gd` — `.fr3` merc injection.

### 5. Current State & Known Tradeoffs

- **Working:** spawn / descent / guard drop / departure / 1-per-minute rate.
- **Not interactive:** the drop-ship cannot be boarded or shot down like a real vehicle — it is the retail scripted actor. For a drivable transport, use `jak2/features/transport_traffic`.
- **Hull invisible until re-extract:** if `lwide*.fr3` have not been rebuilt with the injection, the transport still spawns and drops guards but has no hull mesh (its `vehicle-turret` chin gun still shows). Not a crash.
- **`jak2_config.jsonc`** also carries a local `rip_levels: true` and a whitespace reformat inherited from the combined branch — harmless, not part of this feature.

---

### 6. Modding Changes Log

| Date | Touched/Created Files | Technical Description | Objective |
| :--- | :--- | :--- | :--- |
| 2026-08-29 → 09-01 | `traffic-manager.gc`<br>`transport.gc`<br>`jak2_config.jsonc`<br>`lwide{a,b,c}.gd` | Ported from the combined `jak2/features/transport_v2` branch: `update-alert-transport` + `alert-transport`/`alert-transport-next-check` fields tie the retail `transport` drop-ship to the city alert level; `(ctywide-entity-hack)` added to `transport-init-by-other`; `transport-ag` merc geometry baked into `lwide*.fr3` via `extra_art_groups_by_dgo`. | Scripted troop transport during alerts, no runtime level borrow. |
| 2026-09-02 | `traffic-manager.gc`<br>`docs/modding/current_mod/transport_alert_readme.md` | **Branch split.** Isolated the alert drop-ship onto its own branch (the drivable traffic gunship moved to `jak2/features/transport_traffic`). Post-spawn cooldown `(seconds 15)` → `(seconds 60)` so the rate is strictly one drop-ship per minute. Removed the `transport-v` traffic-type spawn wiring (`traffic-object-spawn` / `type-from-vehicle-type` cases, `want-count[20]` back to 0). New scoped readme. | One clean feature per branch; enforce the requested 1/minute rate. |

---

## 🇫🇷 Version Française

### 1. Présentation & Objectif

Tant qu'Abriville est en **alerte (niveau ≥ 1)**, un **Transport de Troupes des Gardes Grenat** (`transport-ag`, le drop-ship retail) descend près du joueur environ **une fois par minute**, dépose une escouade de Gardes Grenat, puis repart. C'est un acteur *scripté* — on ne peut pas monter à bord, et il ne fait pas partie du pool de trafic ambiant.

C'est la branche sœur de `jak2/features/transport_traffic` (la canonnière pilotable intégrée au trafic). Elles ne partagent que l'injection de géométrie merc `.fr3` qui rend la carlingue du transport affichable en exploration libre.

### 2. Fonctionnement

| Élément | Fichier | Rôle |
|---|---|---|
| `update-alert-transport` | `traffic-manager.gc` | Nouvelle méthode de `traffic-manager`, appelée chaque frame depuis `active:post`. Sonde le niveau d'alerte ; quand il est ≥ 1, que le cooldown de 1/minute est écoulé et qu'aucun transport n'est vivant, elle `process-spawn` un `transport` à un point aléatoire 10–18 m du joueur. |
| `alert-transport` / `alert-transport-next-check` | `traffic-manager.gc` | Nouveaux champs : un handle vers le drop-ship vivant et le `current-time` le plus tôt où le prochain peut apparaître. Initialisés dans `reset-and-init` et `traffic-manager-init-by-other`. |
| `transport` scripté | `transport.gc` (retail) | Logique du drop-ship retail inchangée — `come-down` → `idle` (porte ouverte, dépose via `transport-method-33`, `max-guard` 8) → `leave`. Une ligne ajoutée : `(ctywide-entity-hack)` dans `transport-init-by-other` pour que le transport lancé au runtime (sans `entity-actor`) résolve quand même son art squelettique. |
| Injection merc `.fr3` | `jak2_config.jsonc`, `lwide{a,b,c}.gd` | `extra_art_groups_by_dgo` cuit la géométrie merc de `transport-ag` (textures résolues via la table de remap de `LPROTECT`) dans `lwidea/lwideb/lwidec.fr3` toujours résidents. Sans ça le renderer merc PC saute silencieusement la carlingue. Voir la [fiche #18](../jak2_modding_utilities/18_merc_geometry_fr3_residency.md). |

**Cooldown / cadence :** le timer `alert-transport-next-check` est fixé à `current-time + 60 s` au moment où un transport apparaît, et le cas 1 du `cond` bloque toute nouvelle apparition tant qu'un transport est vivant — donc la cadence ne dépasse jamais **un drop-ship par minute**.

### 3. Rendu — l'injection de géométrie merc `.fr3`

La géométrie de coque de `transport-ag` n'a jamais été livrée que dans `lprotect/ctykora/forestb/nest`, aucun résident en exploration libre d'Abriville. Le correctif (dans `decompiler/config/jak2/jak2_config.jsonc`) :

```jsonc
"extra_art_groups_by_dgo": {
  "LWIDEA.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEB.DGO": ["transport-ag:LPROTECT.DGO"],
  "LWIDEC.DGO": ["transport-ag:LPROTECT.DGO"]
}
```

Cela cuit la géométrie dans `lwidea.fr3 / lwideb.fr3 / lwidec.fr3` (toujours empruntés dans le slot 1 de `ctywide` en exploration libre). Les entrées `transport-ag.go` + `tpage-2869.go` correspondantes sont ajoutées aux `lwidea.gd / lwideb.gd / lwidec.gd`. Aucun emprunt de niveau runtime.

> **Impose une re-extraction** (`task extract`) pour que les trois `.fr3` soient reconstruits avec la géométrie injectée.

### 4. Procédure de Test

1. **Extraire (une fois) :** `task extract` — reconstruit `lwide*.fr3` avec `transport-ag`.
2. **Recompiler :** `task repl` puis `(mi)` (le deftype `traffic-manager` a changé — relancer le REPL si `(mi)` proteste).
3. **Lancer :** `task boot-game`, exploration libre d'Abriville.
4. **Déclencher :** agresser un Garde Grenat pour lever le niveau d'alerte.
5. **Observer :** en quelques secondes un transport descend 10–18 m du joueur, sa porte s'ouvre, ~8 gardes en sortent, et il repart. La console affiche `AT: transport drop spawned ...`.
6. **Cadence :** rester en alerte — le prochain transport ne doit pas apparaître avant ~60 s après l'apparition du précédent.

**Fichiers sources clés :**

- `goal_src/jak2/levels/city/traffic/traffic-manager.gc` — `update-alert-transport` + champs + point d'appel.
- `goal_src/jak2/levels/city/traffic/vehicle/transport.gc` — ligne `(ctywide-entity-hack)`.
- `decompiler/config/jak2/jak2_config.jsonc`, `goal_src/jak2/dgos/lwide{a,b,c}.gd` — injection merc `.fr3`.

### 5. État Actuel & Compromis Connus

- **Fonctionnel :** apparition / descente / dépose des gardes / départ / cadence 1 par minute.
- **Non interactif :** le drop-ship ne peut pas être piloté ni abattu comme un vrai véhicule — c'est l'acteur scripté retail. Pour un transport pilotable, voir `jak2/features/transport_traffic`.
- **Coque invisible avant re-extraction :** si les `lwide*.fr3` n'ont pas été reconstruits avec l'injection, le transport apparaît et dépose quand même les gardes mais n'a pas de maillage de coque (sa tourelle-menton `vehicle-turret` reste visible). Pas de crash.
- **`jak2_config.jsonc`** porte aussi un `rip_levels: true` local et un reformatage d'espaces hérités de la branche combinée — sans conséquence, hors périmètre de cette fonctionnalité.

---

### 6. Journal des Modifications

| Date | Fichiers touchés/créés | Description technique | Objectif |
| :--- | :--- | :--- | :--- |
| 2026-08-29 → 09-01 | `traffic-manager.gc`<br>`transport.gc`<br>`jak2_config.jsonc`<br>`lwide{a,b,c}.gd` | Porté depuis la branche combinée `jak2/features/transport_v2` : `update-alert-transport` + champs `alert-transport`/`alert-transport-next-check` lient le drop-ship `transport` retail au niveau d'alerte ; `(ctywide-entity-hack)` ajouté à `transport-init-by-other` ; géométrie merc de `transport-ag` cuite dans `lwide*.fr3` via `extra_art_groups_by_dgo`. | Transport de troupes scripté pendant les alertes, sans emprunt de niveau runtime. |
| 2026-09-02 | `traffic-manager.gc`<br>`docs/modding/current_mod/transport_alert_readme.md` | **Séparation de branche.** Isolé le drop-ship d'alerte sur sa propre branche (la canonnière pilotable est passée sur `jak2/features/transport_traffic`). Cooldown post-apparition `(seconds 15)` → `(seconds 60)` pour une cadence stricte d'un drop-ship par minute. Retiré le câblage de spawn du type de trafic `transport-v` (cas `traffic-object-spawn` / `type-from-vehicle-type`, `want-count[20]` remis à 0). Nouveau readme dédié. | Une fonctionnalité propre par branche ; imposer la cadence 1/minute demandée. |
