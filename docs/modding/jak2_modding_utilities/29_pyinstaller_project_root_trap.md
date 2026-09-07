# PyInstaller `__file__` vs `sys.executable` Trap / Piège `__file__` vs `sys.executable`

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/chore/reskin_deploy_fix`
> - **Last Updated / Dernière modification:** `jak2/chore/reskin_deploy_fix`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

<a name="-english-version"></a>

# 🇬🇧 English Version

## 1. The bug it caused

`open-goal-glb-reskin-tool` (a `bottle` + `pywebview` desktop app shipped as a
PyInstaller `--onefile` `.exe`) resolved the jak-project root like this:

```python
def find_jak_project_root():
    cur = os.path.dirname(os.path.abspath(__file__))   # <-- the trap
    while cur and os.path.dirname(cur) != cur:
        if os.path.exists(os.path.join(cur, "goal_src")) and os.path.exists(os.path.join(cur, "decompiler")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
```

- **From source** (`python glb_reskin_tool.py`): `__file__` is the real path in
  the repo → walks up → finds the root. Works.
- **From the frozen `.exe`**: PyInstaller `--onefile` unpacks to a temp dir and
  sets `__file__` to something like
  `C:\Users\…\AppData\Local\Temp\_MEI123456\glb_reskin_tool.py`. The walk never
  finds `goal_src/`, so it fell through to the last-resort guess — a path deep
  in `Temp`.

The **"🚀 Build & Deploy"** button then did
`os.makedirs(dest, exist_ok=True); open(dest, "wb").write(glb)` on
`<temp>/custom_assets/jak2/models/custom_levels/<name>.glb`, **reported success**,
and the files never appeared in the repo. "Export GLB…" worked the whole time
because it uses a save dialog (absolute path), not the resolved root.

## 2. The fix

| Change | Why |
| --- | --- |
| Anchor on `os.path.dirname(sys.executable)` **when `sys.frozen`** | `sys.executable` is the real on-disk path of the `.exe`, which sits inside `docs/modding/tools/<tool>/`. Walking up from there finds the repo. |
| Also try `os.getcwd()` and `__file__` (de-duplicated) | covers "run from repo dir" and source runs. |
| Accept `--project <path>` / `OPENGOAL_PROJECT_ROOT` | explicit override for odd layouts. |
| `project_root_looks_valid()` = has `goal_src/` **and** `custom_assets/` | `custom_assets/` is what deploy actually writes into; `decompiler/` may be absent in release-only checkouts. |
| A `project_root_ok` flag; deploy **refuses** (clear message) when false; the UI disables the button | never silently write to the wrong place again. |
| Post-write check: file exists and `getsize == len(bytes)` | catch partial writes. |

`get_base_dir()` (for bundled `ui/` assets) legitimately uses `sys._MEIPASS`
when frozen — that is correct and unchanged. Only the *project* root must not.

## 3. Rule of thumb

> In a PyInstaller `--onefile` app, `__file__` and `sys._MEIPASS` point into a
> **throw-away temp dir**. To find anything *next to the executable on disk*
> (config, a sibling repo, user data), anchor on
> `os.path.dirname(sys.executable)` when `getattr(sys, "frozen", False)`.

The repo's other Python tools that walk up to the project root — e.g.
`open-goal-level-builder` — apply the same pattern.

---

<a name="-version-française"></a>

# 🇫🇷 Version Française

## 1. Le bug qu'il provoquait

`open-goal-glb-reskin-tool` (une appli desktop `bottle` + `pywebview` livrée en
`.exe` PyInstaller `--onefile`) résolvait la racine jak-project ainsi :

```python
def find_jak_project_root():
    cur = os.path.dirname(os.path.abspath(__file__))   # <-- le piège
    while cur and os.path.dirname(cur) != cur:
        if os.path.exists(os.path.join(cur, "goal_src")) and os.path.exists(os.path.join(cur, "decompiler")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
```

- **Depuis les sources** (`python glb_reskin_tool.py`) : `__file__` est le vrai
  chemin dans le dépôt → remonte → trouve la racine. OK.
- **Depuis l'`.exe` figé** : PyInstaller `--onefile` décompresse dans un dossier
  temporaire et met `__file__` à un truc comme
  `C:\Users\…\AppData\Local\Temp\_MEI123456\glb_reskin_tool.py`. La remontée ne
  trouve jamais `goal_src/`, donc on tombait sur la supposition de dernier
  recours — un chemin au fond de `Temp`.

Le bouton **« 🚀 Générer & Déployer »** faisait alors
`os.makedirs(dest, exist_ok=True); open(dest, "wb").write(glb)` sur
`<temp>/custom_assets/jak2/models/custom_levels/<nom>.glb`, **annonçait un
succès**, et les fichiers n'apparaissaient jamais dans le dépôt. « Exporter
GLB… » fonctionnait depuis le début car il utilise une boîte de dialogue
(chemin absolu), pas la racine résolue.

## 2. Le correctif

| Changement | Pourquoi |
| --- | --- |
| S'ancrer sur `os.path.dirname(sys.executable)` **si `sys.frozen`** | `sys.executable` est le vrai chemin disque de l'`.exe`, situé dans `docs/modding/tools/<outil>/`. Remonter de là trouve le dépôt. |
| Essayer aussi `os.getcwd()` et `__file__` (dédupliqués) | couvre « lancé depuis le dépôt » et les runs depuis les sources. |
| Accepter `--project <chemin>` / `OPENGOAL_PROJECT_ROOT` | surcharge explicite pour les layouts atypiques. |
| `project_root_looks_valid()` = présence de `goal_src/` **et** `custom_assets/` | `custom_assets/` est ce dans quoi deploy écrit ; `decompiler/` peut manquer sur un checkout release. |
| Un drapeau `project_root_ok` ; deploy **refuse** (message clair) si faux ; l'UI désactive le bouton | ne plus jamais écrire silencieusement au mauvais endroit. |
| Vérification post-écriture : le fichier existe et `getsize == len(octets)` | détecter les écritures partielles. |

`get_base_dir()` (pour les assets `ui/` embarqués) utilise légitimement
`sys._MEIPASS` quand figé — c'est correct et inchangé. Seule la racine *projet*
ne doit pas.

## 3. Règle générale

> Dans une appli PyInstaller `--onefile`, `__file__` et `sys._MEIPASS` pointent
> vers un **dossier temporaire jetable**. Pour trouver quoi que ce soit *à côté
> de l'exécutable sur le disque* (config, dépôt voisin, données utilisateur),
> ancrez-vous sur `os.path.dirname(sys.executable)` quand
> `getattr(sys, "frozen", False)`.

Les autres outils Python du dépôt qui remontent vers la racine — ex.
`open-goal-level-builder` — appliquent le même schéma.
