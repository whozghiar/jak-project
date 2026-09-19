# 🤖 GitHub Actions Workflows Guide / Guide des Workflows GitHub Actions

> **Bilingual OpenGOAL Reference Manual / Manuel de Référence Bilingue**
>
> - **Applies to / Concerne :** Jak 1 / Jak 2 / Jak 3 — Modding Infrastructure & CI/CD
> - **Origin / Provenance :** `master-dev`
> - **Scope / Portée :** Automated Upstream Synchronization, Branch Health, Multi-Platform Releases & Issue Triage

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. CI/CD Architecture & Mental Model](#1-cicd-architecture--mental-model) · [2. Upstream & Dev Synchronization (`sync-upstream.yaml`)](#2-upstream--dev-synchronization-sync-upstreamyaml) · [3. Per-Branch Health Check (`branch-sync-check.yaml`)](#3-per-branch-health-check-branch-sync-checkyaml) · [4. Automated Release & Packaging (`release.yml`)](#4-automated-release--packaging-releaseyml) · [5. Bug Report Sync (`mod-bug-report-sync.yml`)](#5-bug-report-sync-mod-bug-report-syncyml) · [6. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)](#6-bug-triage--auto-labeling-mod-bug-triageyml) · [7. Master Mod Catalog Sync (`sync-global-catalog.yml`)](#7-master-mod-catalog-sync-sync-global-catalogyml) · [8. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)](#8-mod-suggestion-auto-triage-mod-suggestion-triageyml) · [9. Quick Reference Matrix](#9-quick-reference-matrix)
> - 🇫🇷 **Français :** [1. Modèle Mental & Architecture CI/CD](#1-modèle-mental--architecture-cicd) · [2. Synchronisation Amont & Dev (`sync-upstream.yaml`)](#2-synchronisation-amont--dev-sync-upstreamyaml) · [3. Vérification de Santé par Branche (`branch-sync-check.yaml`)](#3-vérification-de-santé-par-branche-branch-sync-checkyaml) · [4. Construction & Distribution des Releases (`release.yml`)](#4-construction--distribution-des-releases-releaseyml) · [5. Synchronisation des Rapports de Bugs (`mod-bug-report-sync.yml`)](#5-synchronisation-des-rapports-de-bugs-mod-bug-report-syncyml) · [6. Triage Automatique des Bugs (`mod-bug-triage.yml`)](#6-triage-automatique-des-bugs-mod-bug-triageyml) · [7. Synchronisation du Catalogue Global (`sync-global-catalog.yml`)](#7-synchronisation-du-catalogue-global-sync-global-catalogyml) · [8. Triage Automatique des Suggestions de Mods (`mod-suggestion-triage.yml`)](#8-triage-automatique-des-suggestions-de-mods-mod-suggestion-triageyml) · [9. Matrice Récapitulative](#9-matrice-récapitulative)

---

# 🇬🇧 English Version

## 1. CI/CD Architecture & Mental Model

In this repository, GitHub Actions workflows are engineered to solve two fundamental challenges of OpenGOAL modding:
1. **Parallel Mod Development Without Upstream Divergence:** Retain perfect alignment with official OpenGOAL (`open-goal/jak-project:master`) while simultaneously maintaining 15+ independent mod branches without manual merge overhead.
2. **Player-Grade Distribution:** Deliver fully compiled, statically linked, zero-dependency release archives installable in one click via the official OpenGOAL Launcher.

```text
[Upstream: open-goal/jak-project] (master)
               │
               ▼  (Daily cron at 10:00 UTC: sync-upstream.yaml)
  [origin/master] (Clean Upstream Mirror)
               │
               ▼  (Fast-forward / Merge)
[origin/master-dev] (Modding Core Base: scripts, tools, verified docs)
   │           │
   │           ├── Auto-merge clean branches ──► [origin/jak2/features/my-mod]
   │           │                                         │
   │           │                                         ├── (on: push: branch-sync-check.yaml)
   │           │                                         │     Status Badge: GREEN
   │           │                                         │
   │           │                                         └── Standalone Texture Packs:
   │           │                                             docs/modding/current_mod/texture_packs/*.zip
   │           │                                               │
   │           └── Summary report in GitHub Actions Step Summary│
   │                                                           │
   ▼ (Manual trigger: release.yml) ◄───────────────────────────┘
[GitHub Releases: windows-v*.zip, linux-v*.zip, texture-pack-v*.zip]
   │
   ├── (on: release: mod-bug-report-sync.yml)
   │     Update Mod Concerned dropdown in mod-bug-report.yml
   │
   └── (workflow_call: sync-global-catalog.yml)
         Update root index.json on master-dev (mods + texture packs)
```

---

## 2. Upstream & Dev Synchronization (`sync-upstream.yaml`)

- **File:** [`.github/workflows/sync-upstream.yaml`](../../../.github/workflows/sync-upstream.yaml)
- **When is it called?**
  - **Scheduled Cron:** Daily at `10:00 UTC` (`12:00` Paris summer time).
  - **Manual Trigger:** Any maintainer can trigger it via `workflow_dispatch` from the GitHub Actions tab.
- **Why does it exist?**
  - Prevents our fork from drifting away from upstream bug fixes, compiler enhancements, and engine optimizations.
  - Automates the tedious task of testing and merging `master-dev` into all clean active mod branches (`jak[1-3]/**`).
  - Reports the fleet mergeability summary directly to terminal output and GitHub Actions Step Summary.

### Detailed Execution Trace:
1. **Upstream Fast-Forward:** Fetches `https://github.com/open-goal/jak-project.git:master` and performs a fast-forward merge into our local `master`.
2. **Master-Dev Merge & Workflow Sanitization:** Merges `master` into `master-dev`. Because upstream contains numerous CI workflows that are irrelevant or problematic for mod branches, the step explicitly prunes all workflows except `sync-upstream.yaml`, `release.yml`, `branch-sync-check.yaml`, `mod-bug-report-sync.yml`, and `mod-bug-triage.yml`.
3. **Mod Branch Synchronization:** Runs `python scripts/modding/sync_branches_with_master.py --push`.
   - Tests every active mod branch for mergeability against `origin/master-dev`.
   - If clean (no conflicts), automatically merges `master-dev` and pushes the branch.
   - If conflicts exist, leaves the branch untouched, identifies conflicting files, and generates a concrete resolution command.
   - Generates the summary report in GitHub Actions without polluting the git tree with markdown churn.

---

## 3. Per-Branch Health Check (`branch-sync-check.yaml`)

- **File:** [`.github/workflows/branch-sync-check.yaml`](../../../.github/workflows/branch-sync-check.yaml)
- **When is it called?**
  - **On Push:** Triggered on any push to branches matching `jak[1-3]/**`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - GitHub Actions only runs scheduled cron jobs on the **default repository branch** (`master-dev`); it cannot evaluate a separate cron across 15+ mod branches.
  - This workflow provides an ultra-lightweight, 5-second check that powers each mod branch's native GitHub status badge (`?branch=jak2/features/...`).
  - It validates ancestry: `git merge-base --is-ancestor origin/master-dev HEAD`.
  - If a developer pushes commits to a mod branch without syncing with `master-dev` first, the badge immediately turns red, signaling that a sync (`task modding-sync-branch`) is needed.

---

## 4. Automated Release & Packaging (`release.yml`)

- **File:** [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
- **When is it called?**
  - **Manual Trigger Only (`workflow_dispatch`):** Maintainers trigger it from GitHub Actions with required inputs:
    - `mod_name`: Display name (e.g. `Jak 3 JetBoard in Jak 1`).
    - `mod_description`: Short summary included in `index.json`.
    - `tag_name`: Version tag (e.g. `v1.0.0`).
    - `prerelease`: Boolean flag.
- **Why does it exist?**
  - Eliminates "works on my machine" issues by building both **Windows** (Ninja + Clang) and **Linux** executables from clean source in isolated runners.
  - Bakes static libraries (`Release-windows-clang-static`, `Release-linux-clang-static`) so players do not need Visual C++ redistributables or missing shared libraries.
  - Automatically packages the required runtime structure (`gk`, `goalc`, `extractor`, `data/`).
  - **Standalone Texture Pack Packaging:** Automatically scans `docs/modding/current_mod/texture_packs/` for any packaged texture pack `.zip` files, computes their checksums, attaches them as release assets, and registers them under `"texturePacks"` in `index.json`.
  - Computes SHA256 checksums across all assets (`SHA256SUMS.txt`) and updates the mod's `index.json` catalog file, committing it directly back to the branch so the OpenGOAL Launcher immediately detects the update.
  - **Automated Catalog Synchronization:** Automatically invokes `sync-global-catalog.yml` via `workflow_call` at the conclusion of the job, ensuring the unified catalog on `master-dev` is regenerated immediately.

---

## 5. Bug Report Sync (`mod-bug-report-sync.yml`)

- **File:** [`.github/workflows/mod-bug-report-sync.yml`](../../../.github/workflows/mod-bug-report-sync.yml)
- **When is it called?**
  - **On Release:** Triggered whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - In our GitHub Issue form (`mod-bug-report.yml`), players choose which mod their issue concerns from a dropdown list.
  - A branch may have an `index.json` committed during local testing without having an actual published release.
  - This workflow runs `scripts/modding/sync_bug_report_options.py`, querying the GitHub Releases API to populate the dropdown *strictly* with mods that players can actually download.

---

## 6. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)

- **File:** [`.github/workflows/mod-bug-triage.yml`](../../../.github/workflows/mod-bug-triage.yml)
- **When is it called?**
  - **On Issue:** Triggered when an issue is `opened` or `edited` with the `mod-bug` label.
- **Why does it exist?**
  - Categorizes bug reports automatically without human maintainer intervention.
  - Uses `actions/github-script` to parse the form fields (`Game`, `Mod Concerned`).
  - Automatically applies labels such as `jak2` and `mod:peaceful-haven-city`.
  - Allows developers to filter open bugs by mod: `is:issue is:open label:mod:<slug>`.
  - When fixing the bug on the mod branch, referencing `Fixes #123` in the commit auto-closes the issue upon merging.

---

## 7. Master Mod Catalog Sync (`sync-global-catalog.yml`)

- **File:** [`.github/workflows/sync-global-catalog.yml`](../../../.github/workflows/sync-global-catalog.yml)
- **When is it called?**
  - **On Release:** Triggered automatically whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Workflow Call:** Called directly at the end of the release pipeline (`release.yml`) to ensure instant catalog updates.
  - **Manual Trigger:** via `workflow_dispatch` on `master-dev`.
- **Why does it exist?**
  - Rather than requiring players to manually find and add 15+ individual mod URLs in their OpenGOAL Launcher, the repository provides a single, consolidated master catalog ([`index.json`](../../../index.json) at the root of `master-dev`).
  - This workflow automates catalog maintenance by running `scripts/modding/sync_global_catalog.py`:
    1. Fetches all releases published across the repository via the GitHub REST API.
    2. Downloads and parses individual release assets and catalogs.
    3. Normalizes branch slugs and dedupes versions.
    4. Aggregates all download URLs (Windows and Linux ZIPs, and standalone texture packs), SHA256 checksums, and cover artwork into a single OpenGOAL Launcher v1 compliant schema.
    5. Commits and pushes the updated `index.json` directly to `master-dev`.

---

## 8. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)

- **File:** [`.github/workflows/mod-suggestion-triage.yml`](../../../.github/workflows/mod-suggestion-triage.yml)
- **When is it called?**
  - **On Issue:** Triggered whenever a community idea or feature suggestion is `opened` or `edited` using the "💡 Mod Suggestion" form (`mod-suggestion.yml`).
- **Why does it exist?**
  - Enables players and developers to suggest new mod ideas directly on the fork.
  - Parses the form's targeted game and category to auto-apply labels:
    - Game labels: `jak1`, `jak2`, `jak3`, `jakx`
    - Category labels: `type:gameplay`, `type:entities`, `type:textures`, `type:audio`, `type:levels`, `type:qol`
    - Status labels: `enhancement`, `mod-suggestion`, `needs-triage`
  - Facilitates community triage and allows mod authors to filter concepts when starting new branches (`task modding-new-branch`).

---

## 9. Quick Reference Matrix

| Workflow | Trigger | Permissions | Target Branch | Primary Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `sync-upstream.yaml` | Schedule (daily 10:00 UTC) / dispatch | `contents: write` | `master`, `master-dev`, all clean `jak*/**` | Mirrors upstream, auto-merges clean branches, updates dashboard. |
| `branch-sync-check.yaml` | Push on `jak[1-3]/**` / dispatch | `contents: read` | Current mod branch | Verifies ancestry with `master-dev`; drives GitHub status badge. |
| `release.yml` | Manual `workflow_dispatch` | `contents: write` | Triggered mod branch | Builds Win/Linux binaries, packages texture packs, creates GitHub Release, updates `index.json`. |
| `sync-global-catalog.yml` | Release events / workflow call / dispatch | `contents: write` | `master-dev` | Consolidates all released mods and texture packs into root `index.json` catalog. |
| `mod-bug-report-sync.yml`| Release events / dispatch | `contents: write` | `master-dev` | Refreshes mod dropdown in bug report issue template. |
| `mod-bug-triage.yml` | Issues (`opened`, `edited`) | `issues: write` | N/A (Repository issues) | Labels bug issues by game (`jak1|2|3`) and mod (`mod:<slug>`). |
| `mod-suggestion-triage.yml` | Issues (`opened`, `edited` with `mod-suggestion`) | `issues: write` | N/A (Repository issues) | Labels mod suggestions by game and category (`type:*`). |

---

# 🇫🇷 Version Française

## 1. Modèle Mental & Architecture CI/CD

Dans ce dépôt, les workflows GitHub Actions sont conçus pour répondre à deux défis majeurs du modding OpenGOAL :
1. **Développement de Mods en Parallèle Sans Divergence Amont :** Rester en parfaite synchronisation avec le dépôt officiel OpenGOAL (`open-goal/jak-project:master`) tout en maintenant plus de 15 branches de mods indépendantes sans surcharge manuelle de fusion.
2. **Distribution Qualité Joueur :** Fournir des archives de release entièrement compilées, liées statiquement, sans dépendances externes, installables en un clic via l'OpenGOAL Launcher officiel.

```text
[Dépôt Amont: open-goal/jak-project] (master)
               │
               ▼  (Cron quotidien à 10:00 UTC: sync-upstream.yaml)
  [origin/master] (Miroir Amont Propre)
               │
               ▼  (Fast-forward / Fusion)
[origin/master-dev] (Base Principale du Modding: scripts, outils, docs vérifiées)
   │           │
   │           ├── Auto-fusion des branches propres ──► [origin/jak2/features/mon-mod]
   │           │                                               │
   │           │                                               ├── (on: push: branch-sync-check.yaml)
   │           │                                               │     Badge d'état : VERT
   │           │                                               │
   │           │                                               └── Packs de textures autonomes :
   │           │                                                   docs/modding/current_mod/texture_packs/*.zip
   │           │                                                     │
   │           └── Rapport de synthèse dans GitHub Actions Step Summary│
   │                                                                 │
   ▼ (Déclenchement manuel : release.yml) ◄──────────────────────────┘
[GitHub Releases : windows-v*.zip, linux-v*.zip, texture-pack-v*.zip]
   │
   ├── (on: release: mod-bug-report-sync.yml)
   │     Mise à jour du menu déroulant dans mod-bug-report.yml
   │
   └── (workflow_call: sync-global-catalog.yml)
         Mise à jour d'index.json sur master-dev (mods + packs textures)
```

---

## 2. Synchronisation Amont & Dev (`sync-upstream.yaml`)

- **Fichier :** [`.github/workflows/sync-upstream.yaml`](../../../.github/workflows/sync-upstream.yaml)
- **Quand est-il appelé ?**
  - **Planification Cron :** Tous les jours à `10:00 UTC` (`12:00` heure de Paris en été).
  - **Déclenchement Manuel :** Tout mainteneur peut le lancer via `workflow_dispatch` depuis l'onglet Actions.
- **Pourquoi existe-t-il ?**
  - Évite que notre fork ne dérive par rapport aux correctifs, améliorations du compilateur et optimisations du moteur officiel.
  - Automatise la tâche fastidieuse de tester et fusionner `master-dev` dans toutes les branches de mods actives et saines (`jak[1-3]/**`).
  - Publie le rapport de fusionnabilité de toutes les branches directement dans la console et dans le GitHub Actions Step Summary.

### Déroulement Détaillé Étape par Étape :
1. **Avance Rapide Amont (Fast-Forward) :** Récupère `https://github.com/open-goal/jak-project.git:master` et avance la branche locale `master` sans créer de commit de merge.
2. **Fusion dans Master-Dev & Nettoyage des Workflows :** Fusionne `master` dans `master-dev`. Comme l'amont comprend de nombreux workflows de CI superflus pour nos mods, cette étape supprime systématiquement tous les workflows à l'exception de nos cinq outils essentiels.
3. **Synchronisation des Branches de Mods :** Exécute `python scripts/modding/sync_branches_with_master.py --push`.
   - Teste l'intégrabilité de chaque branche de mod avec `origin/master-dev`.
   - Si aucun conflit n'est détecté, fusionne automatiquement `master-dev` et pousse la branche.
   - En cas de conflit, laisse la branche intacte, liste les fichiers conflictuels et fournit la commande exacte de résolution.
   - Génère le rapport de synthèse dans GitHub Actions sans polluer l'arbre Git avec des fichiers d'historique.

---

## 3. Vérification de Santé par Branche (`branch-sync-check.yaml`)

- **Fichier :** [`.github/workflows/branch-sync-check.yaml`](../../../.github/workflows/branch-sync-check.yaml)
- **Quand est-il appelé ?**
  - **À chaque Push :** Déclenché lors de tout commit poussé sur une branche `jak[1-3]/**`.
  - **Déclenchement Manuel :** via `workflow_dispatch`.
- **Pourquoi existe-t-il ?**
  - GitHub Actions n'évalue les crons récurrents que sur la **branche par défaut** (`master-dev`) ; impossible d'avoir un cron par branche sur 15 branches de mods.
  - Ce workflow ultra-rapide (5 secondes) alimente le badge d'état GitHub Actions natif visible dans le `README.md` de chaque mod (`?branch=jak2/features/...`).
  - Il vérifie la filiation : `git merge-base --is-ancestor origin/master-dev HEAD`.
  - Si un développeur pousse du code sans avoir préalablement synchronisé sa branche avec `master-dev`, le badge passe au rouge, signalant qu'une synchronisation locale (`task modding-sync-branch`) est requise.

---

## 4. Construction & Distribution des Releases (`release.yml`)

- **Fichier :** [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
- **Quand est-il appelé ?**
  - **Exclusivement sur Déclenchement Manuel (`workflow_dispatch`) :** Le mainteneur lance la release avec les paramètres requis :
    - `mod_name` : Nom affiché (ex : `Jak 3 JetBoard in Jak 1`).
    - `mod_description` : Résumé court inclus dans `index.json`.
    - `tag_name` : Tag de version (ex : `v1.0.0`).
    - `prerelease` : Booléen pour version préliminaire.
- **Pourquoi existe-t-il ?**
  - Évite le problème du « ça marche sur ma machine » en recompilant les binaires **Windows** (Ninja + Clang) et **Linux** sur des runners isolés et propres.
  - Construit des binaires entièrement statiques (`Release-windows-clang-static`, `Release-linux-clang-static`) ne nécessitant aucun runtime Visual C++ ou bibliothèque système manquante chez le joueur.
  - Package automatiquement l'arborescence requise (`gk`, `goalc`, `extractor`, `data/`).
  - **Packaging Automatisé des Packs de Textures :** Scanne automatiquement `docs/modding/current_mod/texture_packs/` à la recherche d'archives `.zip` de texture, calcule leurs empreintes, les attache comme assets de release et les référence sous `"texturePacks"` dans `index.json`.
  - Calcule les empreintes SHA256 de tous les assets (`SHA256SUMS.txt`) et met à jour le fichier catalogue `index.json`, puis le commite sur la branche afin que l'OpenGOAL Launcher détecte immédiatement la mise à jour.
  - **Synchronisation Automatisée du Catalogue :** Déclenche automatiquement `sync-global-catalog.yml` via `workflow_call` dès la fin du packaging, garantissant la régénération immédiate du catalogue unifié sur `master-dev`.

---

## 5. Synchronisation des Rapports de Bugs (`mod-bug-report-sync.yml`)

- **Fichier :** [`.github/workflows/mod-bug-report-sync.yml`](../../../.github/workflows/mod-bug-report-sync.yml)
- **Quand est-il appelé ?**
  - **Lors d'une Release :** Déclenché lorsqu'une release GitHub est publiée, dépubliée, modifiée ou supprimée.
  - **Déclenchement Manuel :** via `workflow_dispatch`.
- **Pourquoi existe-t-il ?**
  - Dans le formulaire de signalement de bugs (`mod-bug-report.yml`), le joueur choisit le mod concerné dans un menu déroulant.
  - Une branche peut contenir un fichier `index.json` commité lors de tests locaux sans qu'une vraie release ne soit publiée.
  - Ce workflow exécute `scripts/modding/sync_bug_report_options.py` pour interroger l'API Releases et restreindre le menu *strictement* aux mods téléchargeables par les joueurs.

---

## 6. Triage Automatique des Bugs (`mod-bug-triage.yml`)

- **Fichier :** [`.github/workflows/mod-bug-triage.yml`](../../../.github/workflows/mod-bug-triage.yml)
- **Quand est-il appelé ?**
  - **Sur Ticket (Issue) :** Déclenché à l'ouverture ou modification d'une issue portant le label `mod-bug`.
- **Pourquoi existe-t-il ?**
  - Catégorise automatiquement les tickets sans intervention humaine.
  - Utilise `actions/github-script` pour extraire le Jeu (`jak1|jak2|jak3`) et le nom du mod afin d'appliquer les labels correspondants (`jak2`, `mod:<slug>`).
  - Permet aux développeurs de filtrer les bugs de leur mod : `is:issue is:open label:mod:<slug>`.
  - Lors de la correction sur la branche de mod, la mention `Fixes #123` dans le commit fermera automatiquement le ticket dès sa fusion.

---

## 7. Synchronisation du Catalogue Global (`sync-global-catalog.yml`)

- **Fichier :** [`.github/workflows/sync-global-catalog.yml`](../../../.github/workflows/sync-global-catalog.yml)
- **Quand est-il appelé ?**
  - **Lors d'une Release :** Déclenché automatiquement dès qu'une release GitHub est publiée, dépubliée, modifiée ou supprimée.
  - **Appel de Workflow (`workflow_call`) :** Invoqué directement à la fin du pipeline de release (`release.yml`) pour une prise en compte immédiate.
  - **Déclenchement Manuel :** via `workflow_dispatch` sur `master-dev`.
- **Pourquoi existe-t-il ?**
  - Plutôt que d'obliger les joueurs à chercher et renseigner 15+ URLs individuelles dans l'OpenGOAL Launcher, le dépôt propose un catalogue maître unifié ([`index.json`](../../../index.json) à la racine de `master-dev`).
  - Ce workflow automatise la maintenance du catalogue en exécutant `scripts/modding/sync_global_catalog.py` :
    1. Interroge l'API REST GitHub pour inventorier toutes les releases publiées du dépôt.
    2. Télécharge et analyse les assets et catalogues individuels.
    3. Normalise les identifiants de branches (slugs) et déduplique les versions.
    4. Regroupe l'ensemble des liens de téléchargement (archives ZIP Windows, Linux et packs de textures), empreintes SHA256 et jaquettes dans un schéma v1 conforme pour l'OpenGOAL Launcher.
    5. Commite et pousse le fichier `index.json` actualisé directement sur `master-dev`.

---

## 8. Triage Automatique des Suggestions de Mods (`mod-suggestion-triage.yml`)

- **Fichier :** [`.github/workflows/mod-suggestion-triage.yml`](../../../.github/workflows/mod-suggestion-triage.yml)
- **Quand est-il appelé ?**
  - **Sur Ticket (Issue) :** Déclenché à l'ouverture ou modification d'une issue provenant du formulaire « 💡 Mod Suggestion » (`mod-suggestion.yml`).
- **Pourquoi existe-t-il ?**
  - Permet aux joueurs et moddeurs de proposer de nouvelles idées de mods directement sur le fork.
  - Analyse le jeu ciblé et la catégorie du formulaire pour appliquer automatiquement les labels :
    - Labels de jeu : `jak1`, `jak2`, `jak3`, `jakx`
    - Labels de catégorie : `type:gameplay`, `type:entities`, `type:textures`, `type:audio`, `type:levels`, `type:qol`
    - Labels d'état : `enhancement`, `mod-suggestion`, `needs-triage`
  - Facilite le triage communautaire et permet aux moddeurs d'explorer des concepts lorsqu'ils créent une nouvelle branche (`task modding-new-branch`).

---

## 9. Matrice Récapitulative

| Workflow | Déclencheur | Permissions | Branche Cible | Résultat Principal |
| :--- | :--- | :--- | :--- | :--- |
| `sync-upstream.yaml` | Cron (quotidien 10:00 UTC) / dispatch | `contents: write` | `master`, `master-dev`, branches `jak*/**` | Miroir amont, fusion automatique des branches propres, tableau de bord. |
| `branch-sync-check.yaml` | Push sur `jak[1-3]/**` / dispatch | `contents: read` | Branche courante du mod | Vérifie la filiation avec `master-dev` ; pilote le badge GitHub. |
| `release.yml` | Manuel `workflow_dispatch` | `contents: write` | Branche du mod ciblée | Compile les binaires Win/Linux, package les packs de textures, publie la Release GitHub, met à jour `index.json`. |
| `sync-global-catalog.yml` | Événements Release / workflow call / dispatch | `contents: write` | `master-dev` | Consolide tous les mods et packs de textures publiés dans le catalogue `index.json` racine. |
| `mod-bug-report-sync.yml`| Événements de Release / dispatch | `contents: write` | `master-dev` | Rafraîchit le menu déroulant des mods dans le template d'issue. |
| `mod-bug-triage.yml` | Issues (`opened`, `edited`) | `issues: write` | N/A (Issues du dépôt) | Applique les labels de jeu (`jak1|2|3`) et de mod (`mod:<slug>`). |
| `mod-suggestion-triage.yml` | Issues (`opened`, `edited` avec `mod-suggestion`) | `issues: write` | N/A (Issues du dépôt) | Applique les labels de jeu et de catégorie (`type:*`) aux suggestions. |
