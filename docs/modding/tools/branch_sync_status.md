# 📊 État de Synchronisation des Branches de Mods

> **Fichier réservé à `master-dev`.** Ce dashboard n'est jamais propagé sur les
> branches de mods (voir `sync_common.MASTER_DEV_ONLY_PATHS`) : chaque branche
> porte seulement son propre badge de synchro dans son `README.md`.

> **Dernière mise à jour :** `2026-09-19 00:48:06 UTC`  
> **Branche source :** `master-dev` (`3c300b370`)  
> **Statut global :** 15/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | 🟢 Prête à fusionner | `c758c195d - chore(sync): align jak2/config/enhanced_spawnrates with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/config/start_menu_wheel` | 🟢 Prête à fusionner | `fb97e189a - chore(sync): align jak2/config/start_menu_wheel with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/blue-krimzon-guard` | 🟢 Prête à fusionner | `427b85d7b - chore(sync): align jak2/features/blue-krimzon-guard with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/dark_jak_enhanced` | 🟢 Prête à fusionner | `ddbe0e067 - chore(sync): align jak2/features/dark_jak_enhanced with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/haven-city-chaos` | 🟢 Prête à fusionner | `13e84eda8 - chore(sync): align jak2/features/haven-city-chaos with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/haven-city-rebellion` | 🟢 Prête à fusionner | `92bfb4356 - chore(sync): align jak2/features/haven-city-rebellion with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/jak3-jetBoard` | 🟢 Prête à fusionner | `58bf17935 - chore(sync): align jak2/features/jak3-jetBoard with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/killable_yakow` | 🟢 Prête à fusionner | `196a24ab4 - chore(sync): align jak2/features/killable_yakow with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/paddywagon/traffic` | 🟢 Prête à fusionner | `3384b49bf - chore(sync): align jak2/features/paddywagon/traffic with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/peaceful-haven-city` | 🟢 Prête à fusionner | `8bf9e5ba0 - chore(sync): align jak2/features/peaceful-haven-city with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/transport-ag/alert` | 🟢 Prête à fusionner | `bdd1cdeba - chore(sync): align jak2/features/transport-ag/alert with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak2/features/transport-ag/traffic` | 🟢 Prête à fusionner | `8867877ff - chore(sync): align jak2/features/transport-ag/traffic with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak3/features/city-behavior` | 🟢 Prête à fusionner | `4a8d77941 - chore(sync): align jak3/features/city-behavior with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak3/features/jak2_skin_secret` | 🟢 Prête à fusionner | `a92342b1e - chore(sync): align jak3/features/jak2_skin_secret with latest origin/master-dev` | Aucun conflit de code détecté | — |
| `jak3/features/mega_dark_jak` | 🟢 Prête à fusionner | `46530a262 - chore(sync): align jak3/features/mega_dark_jak with latest origin/master-dev` | Aucun conflit de code détecté | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
