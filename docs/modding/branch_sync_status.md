# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-03 18:25:29 UTC`  
> **Branche source :** `master` (`65fc564c1`)  
> **Statut global :** 16/16 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/custom_animation_and_sound` | ✅ À jour | `200ef0e4c - fix(merge): resolve CMake conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/enhanced_spawnrates` | ✅ À jour | `d8ad86f1e - chore: sync jak2/config/enhanced_spawnrates with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/memory_increase` | ✅ À jour | `1e7ce1531 - chore: sync jak2/config/memory_increase with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/config/start_menu_wheel` | ✅ À jour | `ba3ae4348 - chore: sync jak2/config/start_menu_wheel with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/dark_jak_enhanced` | ✅ À jour | `6c4fbbef5 - chore: sync jak2/features/dark_jak_enhanced with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/enhanced_city_traffic_v2` | ✅ À jour | `1dcf66491 - chore: sync jak2/features/enhanced_city_traffic_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/jak3-jetBoard` | ✅ À jour | `5d71ff198 - fix(merge): resolve CMake conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/merc-fr3-injection-poc` | ✅ À jour | `5427bdebd - chore: sync jak2/features/merc-fr3-injection-poc with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/paddy_wagon_v2` | ✅ À jour | `fdeb0ecf4 - chore: sync jak2/features/paddy_wagon_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport_v2` | ✅ À jour | `a7ab8c19f - chore: sync jak2/features/transport_v2 with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak2/features/yakow_killable` | ✅ À jour | `07ed1641b - chore: sync jak2/features/yakow_killable with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/config/memory_increase` | ✅ À jour | `93c8570b5 - chore: sync jak3/config/memory_increase with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/city-behavior` | ✅ À jour | `d03da075b - chore: sync jak3/features/city-behavior with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/jak2_skin_secret` | ✅ À jour | `77323bced - fix(merge): resolve progress-draw-pc.gc conflict with upstream master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/mega_dark_jak` | ✅ À jour | `c92710916 - chore: sync jak3/features/mega_dark_jak with latest origin/master (AI-assisted)` | Déjà à jour | — |
| `jak3/features/redguard-entity` | ✅ À jour | `adb1e2741 - chore: sync jak3/features/redguard-entity with latest origin/master (AI-assisted)` | Déjà à jour | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
