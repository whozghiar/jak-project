# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-13 14:11:58 UTC`  
> **Branche source :** `master-dev` (`ef4392e68`)  
> **Statut global :** 15/17 synchronisées (2 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🔄 Synchronisée | `d1aebca00 - chore: sync jak2/config/enhanced_spawnrates with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/config/start_menu_wheel` | 🔄 Synchronisée | `f53fa6cf1 - chore: sync jak2/config/start_menu_wheel with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/city-insurrection` | 🔄 Synchronisée | `1ceab7c7a - chore: sync jak2/features/crimson-blueguard/city-insurrection with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/crimson-blueguard/crimson-redguard-behavior` | ⚠️ Conflit | `c67191dbe - feat(jak2/crimson-blueguard): blue minimap dot for guard vehicles (AI-assisted)` | • `.agents/skills/engine-internals/discoveries.md`<br>• `AGENTS.md` | `git checkout jak2/features/crimson-blueguard/crimson-redguard-behavior && git merge origin/master-dev` |
| `jak2/features/crimson-blueguard/peaceful` | 🔄 Synchronisée | `a95733307 - chore: sync jak2/features/crimson-blueguard/peaceful with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/dark_jak_enhanced` | 🔄 Synchronisée | `be1c5e590 - chore: sync jak2/features/dark_jak_enhanced with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/haven-city-chaos` | ⚠️ Conflit | `f75162eec - feat(jak2/chaos): 10/50/40 ground faction ratio, plus three Rapid gunner fixes (AI-assisted)` | • `.agents/skills/engine-internals/discoveries.md` | `git checkout jak2/features/haven-city-chaos && git merge origin/master-dev` |
| `jak2/features/jak3-jetBoard` | 🔄 Synchronisée | `b283ae6a3 - chore: sync jak2/features/jak3-jetBoard with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/paddywagon/traffic` | 🔄 Synchronisée | `1aa0e9566 - chore: sync jak2/features/paddywagon/traffic with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/alert` | 🔄 Synchronisée | `105f40c8b - chore: sync jak2/features/transport-ag/alert with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/transport-ag/traffic` | 🔄 Synchronisée | `c607375b0 - chore: sync jak2/features/transport-ag/traffic with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak2/features/yakow_killable` | 🔄 Synchronisée | `4c2108dab - chore: sync jak2/features/yakow_killable with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/config/memory_increase` | 🔄 Synchronisée | `df1c7757e - chore: sync jak3/config/memory_increase with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/city-behavior` | 🔄 Synchronisée | `b58a47d35 - chore: sync jak3/features/city-behavior with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/jak2_skin_secret` | 🔄 Synchronisée | `164b2f428 - chore: sync jak3/features/jak2_skin_secret with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/mega_dark_jak` | 🔄 Synchronisée | `981f13af4 - chore: sync jak3/features/mega_dark_jak with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |
| `jak3/features/redguard-entity` | 🔄 Synchronisée | `0afefe618 - chore: sync jak3/features/redguard-entity with latest origin/master-dev (AI-assisted)` | Fusionnée et poussée avec succès | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
