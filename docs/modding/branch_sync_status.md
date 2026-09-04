# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-04 00:25:58 UTC`  
> **Branche source :** `master-dev` (`31769a3f9`)  
> **Statut global :** 1/17 synchronisées (16 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/custom_animation_and_sound` | ⚠️ Conflit | `af0a6a969 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/config/custom_animation_and_sound && git merge origin/master-dev` |
| `jak2/config/enhanced_spawnrates` | ⚠️ Conflit | `f360074b6 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/config/enhanced_spawnrates && git merge origin/master-dev` |
| `jak2/config/memory_increase` | ⚠️ Conflit | `46fb2f79c - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak2/config/memory_increase && git merge origin/master-dev` |
| `jak2/config/start_menu_wheel` | ⚠️ Conflit | `21a3c27e3 - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak2/config/start_menu_wheel && git merge origin/master-dev` |
| `jak2/features/dark_jak_enhanced` | ⚠️ Conflit | `362fba536 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/features/dark_jak_enhanced && git merge origin/master-dev` |
| `jak2/features/enhanced_city_traffic_v2` | ⚠️ Conflit | `2019be371 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/features/enhanced_city_traffic_v2 && git merge origin/master-dev` |
| `jak2/features/jak3-jetBoard` | ⚠️ Conflit | `1767295ea - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `decompiler/config/jak3/jak3_config.jsonc`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak2/features/jak3-jetBoard && git merge origin/master-dev` |
| `jak2/features/merc-fr3-injection-poc` | ⚠️ Conflit | `8b50da673 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md`<br>• `decompiler/config/jak2/jak2_config.jsonc` | `git checkout jak2/features/merc-fr3-injection-poc && git merge origin/master-dev` |
| `jak2/features/paddy_wagon_v2` | ⚠️ Conflit | `180228bab - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/features/paddy_wagon_v2 && git merge origin/master-dev` |
| `jak2/features/transport_traffic` | ✅ À jour | `2960ddb8d - docs: simplify technical documentation link in root README (AI-assisted)` | Déjà à jour | — |
| `jak2/features/transport_v2` | ⚠️ Conflit | `2f6468aaf - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/features/transport_v2 && git merge origin/master-dev` |
| `jak2/features/yakow_killable` | ⚠️ Conflit | `3a922fe11 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak2/features/yakow_killable && git merge origin/master-dev` |
| `jak3/config/memory_increase` | ⚠️ Conflit | `756d6aaef - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak3/config/memory_increase && git merge origin/master-dev` |
| `jak3/features/city-behavior` | ⚠️ Conflit | `e7b77da61 - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak3/features/city-behavior && git merge origin/master-dev` |
| `jak3/features/jak2_skin_secret` | ⚠️ Conflit | `fda2e0784 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak3/features/jak2_skin_secret && git merge origin/master-dev` |
| `jak3/features/mega_dark_jak` | ⚠️ Conflit | `ac85d4806 - docs: simplify technical documentation link in root README (AI-assisted)` | • `README.md` | `git checkout jak3/features/mega_dark_jak && git merge origin/master-dev` |
| `jak3/features/redguard-entity` | ⚠️ Conflit | `7ecbf97ab - docs: simplify technical documentation link in root README (AI-assisted)` | • `AGENTS.md`<br>• `CLAUDE.md`<br>• `README.md`<br>• `docs/modding/jak_modding_instructions.md` | `git checkout jak3/features/redguard-entity && git merge origin/master-dev` |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
