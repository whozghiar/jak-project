# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-12 13:28:21 UTC`  
> **Branche source :** `master-dev` (`5dde898bc`)  
> **Statut global :** 15/16 synchronisées (1 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🔄 Synchronisée | `3542c71f3 - chore: sync jak2/config/enhanced_spawnrates with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `8e35b9e2b - chore: sync jak2/config/start_menu_wheel with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/city-insurrection` | 🔄 Synchronisée | `f59799a85 - chore: sync jak2/features/crimson-blueguard/city-insurrection with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | ⚠️ Conflit | `c67191dbe - feat(jak2/crimson-blueguard): blue minimap dot for guard vehicles (AI-assisted)` | • `.agents/skills/engine-internals/discoveries.md` | `git checkout jak2/features/crimson-blueguard/crimson-redguard-behavior && git merge origin/master-dev` |
| `jak2/features/crimson-blueguard/peaceful` | ✅ À jour | `a0fbab6f3 - chore: sync jak2/features/crimson-blueguard/peaceful with latest master-dev (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `e9165452a - chore: sync jak2/features/dark_jak_enhanced with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `90b8bf24e - chore: sync jak2/features/jak3-jetBoard with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | 🔄 Synchronisée | `6cfd70d66 - chore: sync jak2/features/paddywagon/traffic with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/alert` | 🔄 Synchronisée | `671c16020 - chore: sync jak2/features/transport-ag/alert with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/traffic` | 🔄 Synchronisée | `071165e33 - chore: sync jak2/features/transport-ag/traffic with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/yakow_killable` | 🔄 Synchronisée | `90d7b2b51 - chore: sync jak2/features/yakow_killable with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/config/memory_increase` | 🔄 Synchronisée | `b07728535 - chore: sync jak3/config/memory_increase with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `9c11dc555 - chore: sync jak3/features/city-behavior with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `3e585944d - chore: sync jak3/features/jak2_skin_secret with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `51200c2e1 - chore: sync jak3/features/mega_dark_jak with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/redguard-entity` | 🔄 Synchronisée | `4a0eb2269 - chore: sync jak3/features/redguard-entity with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
