# 📊 État de Synchronisation des Branches de Mods

> **Fichier réservé à `master-dev`.** Ce dashboard n'est jamais propagé sur les
> branches de mods (voir `sync_common.MASTER_DEV_ONLY_PATHS`) : chaque branche
> porte seulement son propre badge de synchro dans son `README.md`.

> **Dernière mise à jour :** `2026-09-19 00:58:34 UTC`  
> **Branche source :** `master-dev` (`04a80bf66`)  
> **Statut global :** 15/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🔄 Synchronisée | `4de712b04 - chore(sync): align jak2/config/enhanced_spawnrates with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `ded3af97f - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/blue-krimzon-guard` | 🔄 Synchronisée | `4f3871f93 - chore(sync): align jak2/features/blue-krimzon-guard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `4e4b381b8 - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | 🔄 Synchronisée | `553ed3487 - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-rebellion` | 🔄 Synchronisée | `fb361dba2 - chore(sync): align jak2/features/haven-city-rebellion with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `e8e74245b - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/killable_yakow` | 🔄 Synchronisée | `aeb9ed6f9 - chore(sync): align jak2/features/killable_yakow with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | 🔄 Synchronisée | `0e322a846 - chore(sync): align jak2/features/paddywagon/traffic with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/peaceful-haven-city` | 🔄 Synchronisée | `bd19e0de0 - chore(sync): align jak2/features/peaceful-haven-city with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/alert` | 🔄 Synchronisée | `2bffc3087 - chore(sync): align jak2/features/transport-ag/alert with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/traffic` | 🔄 Synchronisée | `925a1fd71 - chore(sync): align jak2/features/transport-ag/traffic with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `90c385564 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `5d883ea8d - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `4ca5d7dc2 - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
