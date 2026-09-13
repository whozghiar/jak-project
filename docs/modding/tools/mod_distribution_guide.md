# 🚀 Guide de Distribution & Release de Mods OpenGOAL

Ce document détaille l'architecture et le fonctionnement du pipeline de release et d'empaquetage automatique permettant de distribuer un mod OpenGOAL pour qu'il soit directement installable et jouable par n'importe quel joueur via l'**OpenGOAL Launcher officiel**.

---

## 1. Pourquoi ce pipeline gère les modifications C++ (`goalc`, `extractor`, `gk`)

Contrairement aux mods conventionnels qui ne modifient que des fichiers de script LISP (`goal_src/`), certains mods de ce dépôt altèrent les outils et le moteur natifs en C++ :
- **Décompilateur / Extracteur (`decompiler/`) :** Extraction personnalisée d'assets, injection de modèles 3D glTF/FR3, conversions de collisions.
- **Compilateur (`goalc/`) :** Nouveaux comportements, compilateur d'acteurs custom, optimisations assembleur x86-64.
- **Runtime du jeu (`gk`) :** Moteur graphique OpenGL (shaders), simulation EE/IOP, hooks audio et mémoire étendue.

### ⚙️ Mécanisme d'exécution dans l'OpenGOAL Launcher

Quand un joueur installe un mod depuis le Launcher :
1. Le Launcher télécharge l'archive correspondante (`windows-v*.zip` ou `linux-v*.zip`) et l'extrait dans son dossier interne :
   ```text
   %APPDATA%/OpenGOAL-Launcher/features/<jak1|jak2|jak3>/mods/<nom_source>/<nom_mod>/
   ```
2. **Priorité absolue aux exécutables du mod :** Le Launcher n'exécute **pas** la version vanilla d'OpenGOAL. Il exécute les binaires situés directement à la racine du dossier du mod extrait :
   - `extractor` pour décompresser l'ISO propre du joueur, décompiler les assets nécessaires et lancer la compilation LISP locale avec votre `goalc`.
   - `gk` pour lancer le jeu nativement.
3. **Liaison statique totale :** Grâce aux presets CMake officiels `Release-windows-clang-static` et `Release-linux-clang-static`, tous les runtimes C++ et bibliothèques tierces (`SDL3`, `zlib`, `lzokay`, `OpenSSL`) sont fusionnés dans les binaires. Le joueur n'a besoin d'installer aucun runtime Visual C++ ou bibliothèque système supplémentaire.

---

## 2. Arborescence Obligatoire de l'Archive Mod

Pour que le Launcher ne rencontre aucune erreur d'extraction ou de compilation locale, l'archive ZIP contient très exactement :

```text
├── extractor.exe (ou extractor sur Linux)
├── gk.exe        (ou gk sur Linux)
├── goalc.exe     (ou goalc sur Linux)
└── data/
    ├── launcher/
    │   └── error-code-metadata.json
    ├── decompiler/
    │   └── config/                       # Règles de décompilation pour ISOs NTSC/PAL
    ├── goal_src/                         # Code source LISP complet compilé par goalc
    ├── game/
    │   ├── assets/                       # Métadonnées de textes, polices et sons
    │   └── graphics/
    │       └── opengl_renderer/
    │           └── shaders/              # Shaders OpenGL indispensables au démarrage de gk
    └── custom_assets/                    # Modèles 3D, textures et assets du mod (si présents)
```

> [!CAUTION]
> **Piège des Shaders OpenGL :** Si le dossier `data/game/graphics/opengl_renderer/shaders/` est absent de l'archive, l'extracteur et le compilateur sembleront fonctionner, mais lors du clic sur "Play", le moteur `gk` plantera immédiatement sur une erreur de compilation GLSL.

---

## 3. Déclencher une Release depuis une Branche de Mod

Le workflow `.github/workflows/release.yml` est disponible sur `master-dev` et synchronisé sur toutes les branches de mods.

### Méthode A — Via un Tag Git (Recommandé pour version officielle)

Sur votre branche de mod (ex: `jak2/features/my-mod`) :
```bash
# 1. Créez un tag sémantique
git tag v1.0.0

# 2. Poussez le tag sur GitHub
git push origin v1.0.0
```
Le workflow se déclenche automatiquement, compile pour Windows et Linux, calcule les SHA-256, met à jour `index.json` et crée la Release GitHub avec les archives prêtes au téléchargement.

### Méthode B — Via GitHub Actions (Déclenchement Manuel / Test)

1. Ouvrez votre dépôt sur GitHub et rendez-vous dans l'onglet **Actions**.
2. Dans le menu de gauche, sélectionnez **🚀 Build & Release OpenGOAL Mod Package**.
3. Cliquez sur **Run workflow** :
   - Choisissez votre branche de mod active.
   - Saisissez le tag désiré (ex: `v0.1.0-test`).
   - Cochez facultativement "Marquer comme pré-release".
4. Cliquez sur **Run workflow**.

---

## 4. Intégration dans l'OpenGOAL Launcher (`index.json`)

Le script `scripts/modding/update_mod_catalog.py` génère automatiquement un fichier `index.json` conforme au schéma officiel OpenGOAL Mod Source Schema v1 :

```json
{
  "schemaVersion": "1.0.0",
  "sourceName": "Jak II - Mon Mod Source",
  "lastUpdated": "2026-09-13T15:00:00Z",
  "mods": {
    "my-mod": {
      "displayName": "Jak II - Mon Mod",
      "description": "Description du mod...",
      "authors": ["MonPseudo"],
      "tags": ["gameplay", "custom-engine"],
      "supportedGames": ["jak2"],
      "websiteUrl": "https://github.com/user/repo/tree/jak2/features/my-mod",
      "versions": [
        {
          "version": "1.0.0",
          "publishedDate": "2026-09-13T15:00:00Z",
          "supportedGames": ["jak2"],
          "assets": {
            "windows": "https://github.com/user/repo/releases/download/v1.0.0/windows-v1.0.0.zip",
            "linux": "https://github.com/user/repo/releases/download/v1.0.0/linux-v1.0.0.zip"
          },
          "checksums": {
            "windows": "a1b2c3d4...",
            "linux": "e5f6g7h8..."
          }
        }
      ]
    }
  },
  "texturePacks": {}
}
```

### 🎮 Pour les joueurs :
Dans l'OpenGOAL Launcher :
1. Allez dans **Settings ▸ Mods ▸ Add Custom Mod Source**.
2. Entrez l'URL brute du catalogue :
   ```text
   https://raw.githubusercontent.com/<utilisateur>/<dépôt>/<branche>/index.json
   ```
3. Le mod apparaît immédiatement dans l'onglet **Mods** avec bouton d'installation 1-clic !
