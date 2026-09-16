# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-16 14:44:45 UTC`  
> **Branche source :** `master-dev` (`a52cdb10e`)  
> **Statut global :** 11/15 synchronisées (4 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ⚠️ Conflit | `0669ed967 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/config/enhanced_spawnrates && git merge origin/master-dev` |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `2d95a80cb - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/city-insurrection` | 🔄 Synchronisée | `68b8b15e0 - chore(sync): align jak2/features/crimson-blueguard/city-insurrection with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | 🔄 Synchronisée | `de28025c0 - chore(sync): align jak2/features/crimson-blueguard/crimson-redguard-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/peaceful` | 🔄 Synchronisée | `312f9f0ae - chore(sync): align jak2/features/crimson-blueguard/peaceful with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `1c42f6f0d - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | 🔄 Synchronisée | `6f217bfb6 - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `abb95129b - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | ⚠️ Conflit | `3d9ac6359 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/paddywagon/traffic && git merge origin/master-dev` |
| `jak2/features/transport-ag/alert` | ⚠️ Conflit | `63ade46e9 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/transport-ag/alert && git merge origin/master-dev` |
| `jak2/features/transport-ag/traffic` | ⚠️ Conflit | `df087efa3 - fix(ci): strictly manual workflow_dispatch and valid release workflow syntax` | • `goal_src/jak2/dgos/game.gd` | `git checkout jak2/features/transport-ag/traffic && git merge origin/master-dev` |
| `jak2/features/yakow_killable` | 🔄 Synchronisée | `4804bcd79 - chore(sync): align jak2/features/yakow_killable with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `0384d0295 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `c71e41a07 - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `ac7c24bae - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
