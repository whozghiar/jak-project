# 📊 État de Synchronisation des Branches de Mods

> **Fichier réservé à `master-dev`.** Ce dashboard n'est jamais propagé sur les
> branches de mods (voir `sync_common.MASTER_DEV_ONLY_PATHS`) : chaque branche
> porte seulement son propre badge de synchro dans son `README.md`.

> **Dernière mise à jour :** `2026-09-18 15:07:20 UTC`  
> **Branche source :** `master-dev` (`c25c2d3f0`)  
> **Statut global :** 10/15 synchronisées (5 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🔄 Synchronisée | `d1c6f9b4b - chore(sync): align jak2/config/enhanced_spawnrates with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `04402cdf7 - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/blue-krimzon-guard` | 🔄 Synchronisée | `dc3d389b0 - chore(sync): align jak2/features/blue-krimzon-guard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `702d4d540 - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | 🔄 Synchronisée | `82ddd8530 - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-rebellion` | ⚠️ Conflit | `1280fe572 - chore(sync): align jak2/features/haven-city-rebellion with latest origin/master-dev` | • `decompiler/config/jak2/jak2_config.jsonc` | `git checkout jak2/features/haven-city-rebellion && git merge origin/master-dev` |
| `jak2/features/jak3-jetBoard` | ⚠️ Conflit | `6535fa3ec - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | • `decompiler/config/jak3/jak3_config.jsonc` | `git checkout jak2/features/jak3-jetBoard && git merge origin/master-dev` |
| `jak2/features/killable_yakow` | 🔄 Synchronisée | `7fda5c124 - chore(sync): align jak2/features/killable_yakow with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | 🔄 Synchronisée | `9479d9bbe - chore(sync): align jak2/features/paddywagon/traffic with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/peaceful-haven-city` | ⚠️ Conflit | `3fb86c7e5 - chore(sync): align jak2/features/peaceful-haven-city with latest origin/master-dev` | • `decompiler/config/jak2/jak2_config.jsonc` | `git checkout jak2/features/peaceful-haven-city && git merge origin/master-dev` |
| `jak2/features/transport-ag/alert` | ⚠️ Conflit | `a1ffeaaa0 - chore(sync): align jak2/features/transport-ag/alert with latest origin/master-dev` | • `decompiler/config/jak2/jak2_config.jsonc` | `git checkout jak2/features/transport-ag/alert && git merge origin/master-dev` |
| `jak2/features/transport-ag/traffic` | ⚠️ Conflit | `e06d958f2 - chore(sync): align jak2/features/transport-ag/traffic with latest origin/master-dev` | • `decompiler/config/jak2/jak2_config.jsonc` | `git checkout jak2/features/transport-ag/traffic && git merge origin/master-dev` |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `beca4bbf9 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `a3a8140b3 - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `33b6de172 - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
