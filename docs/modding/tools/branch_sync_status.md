# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-15 14:45:32 UTC`  
> **Branche source :** `master-dev` (`63c4eb713`)  
> **Statut global :** 11/15 synchronisées (4 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ⚠️ Conflit | `0669ed967 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/config/enhanced_spawnrates && git merge origin/master-dev` |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `3230e1703 - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/city-insurrection` | ✅ À jour | `687d96328 - feat(mods-menu): migrate crimson-blueguard-insurrection menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | ✅ À jour | `74cc4d237 - feat(mods-menu): migrate crimson-blueguard menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak2/features/crimson-blueguard/peaceful` | ✅ À jour | `a4f0c4419 - feat(mods-menu): migrate crimson-blueguard-peaceful menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `8faefdc3a - feat(mods-menu): migrate dark-jak-enhanced menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak2/features/haven-city-chaos` | ✅ À jour | `d6a0a3d42 - fix(jak2/chaos): update haven-city-chaos-menu path to pc/features in game.gp (AI-assisted)` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `45a858187 - feat(mods-menu): migrate jak3-jetboard menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak2/features/paddywagon/traffic` | ⚠️ Conflit | `3d9ac6359 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/paddywagon/traffic && git merge origin/master-dev` |
| `jak2/features/transport-ag/alert` | ⚠️ Conflit | `63ade46e9 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/transport-ag/alert && git merge origin/master-dev` |
| `jak2/features/transport-ag/traffic` | ⚠️ Conflit | `df087efa3 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/transport-ag/traffic && git merge origin/master-dev` |
| `jak2/features/yakow_killable` | ✅ À jour | `86aa125c8 - feat(mods-menu): migrate yakow-killable menu to retail popup-menu registry (AI-assisted)` | Déjà à jour | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `2dafe1b36 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `8becf0413 - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `592177b0a - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
