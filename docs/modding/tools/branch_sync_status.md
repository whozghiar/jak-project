# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-16 22:56:36 UTC`  
> **Branche source :** `master-dev` (`f32bbcc08`)  
> **Statut global :** 15/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `aed4ab5a3 - feat(traffic): instant traffic recycle on mod toggle / régénération immédiate du trafic au toggle (AI-assisted)` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `9f91ed43c - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/city-insurrection` | 🔄 Synchronisée | `899e5270c - chore(sync): align jak2/features/crimson-blueguard/city-insurrection with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | 🔄 Synchronisée | `902854fea - chore(sync): align jak2/features/crimson-blueguard/crimson-redguard-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/peaceful` | 🔄 Synchronisée | `fe15e2450 - chore(sync): align jak2/features/crimson-blueguard/peaceful with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `19789d67d - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | 🔄 Synchronisée | `58d534aeb - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `78be53884 - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | ✅ À jour | `1a6bb3bec - feat(traffic): instant traffic recycle on mod toggle & demo video / régénération immédiate du trafic au toggle et vidéo de démo (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport-ag/alert` | 🔄 Synchronisée | `ee895daf2 - chore(sync): align jak2/features/transport-ag/alert with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/traffic` | ✅ À jour | `dd82b2ab2 - chore(sync): align jak2/features/transport-ag/traffic with latest master-dev` | Déjà à jour | — |
| `jak2/features/yakow_killable` | 🔄 Synchronisée | `8894494f8 - chore(sync): align jak2/features/yakow_killable with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `3a7bf9018 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `84e8fe24e - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `29ee91124 - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
