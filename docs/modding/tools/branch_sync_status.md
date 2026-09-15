# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-14 16:15:17 UTC`  
> **Branche source :** `master-dev` (`cac31f184`)  
> **Statut global :** 17/17 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `0669ed967 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | ✅ À jour | `d38f47aed - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/city-insurrection` | ✅ À jour | `cd12ecad7 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | ✅ À jour | `f7f06f832 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/peaceful` | ✅ À jour | `33d1e9f04 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `7076cd20f - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/haven-city-chaos` | ✅ À jour | `5bf495226 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `73d489ee6 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/paddywagon/traffic` | ✅ À jour | `3d9ac6359 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/transport-ag/alert` | ✅ À jour | `63ade46e9 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/transport-ag/traffic` | ✅ À jour | `df087efa3 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak2/features/yakow_killable` | ✅ À jour | `58421d731 - chore(release): update index.json for yakow_killable-v1.0.1` | Déjà à jour | — |
| `jak3/config/memory_increase` | ✅ À jour | `7887b9b24 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak3/features/city-behavior` | ✅ À jour | `daa7717a8 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak3/features/jak2_skin_secret` | ✅ À jour | `e5fa8644e - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak3/features/mega_dark_jak` | ✅ À jour | `bc31f0b91 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |
| `jak3/features/redguard-entity` | ✅ À jour | `64b0d4209 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | Déjà à jour | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
