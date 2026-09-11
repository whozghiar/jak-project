# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-11 13:29:24 UTC`  
> **Branche source :** `master-dev` (`19d3c3f99`)  
> **Statut global :** 0/15 synchronisées (15 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ⚠️ Conflit | `2d2b11e3a - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/config/enhanced_spawnrates && git merge origin/master-dev` |
| `jak2/config/start_menu_wheel` | ⚠️ Conflit | `50a05cef4 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/config/start_menu_wheel && git merge origin/master-dev` |
| `jak2/features/crimson-blueguard/city-insurrection` | ⚠️ Conflit | `2d2dddaa5 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/crimson-blueguard/city-insurrection && git merge origin/master-dev` |
| `jak2/features/crimson-blueguard/peaceful` | ⚠️ Conflit | `104874cfd - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/crimson-blueguard/peaceful && git merge origin/master-dev` |
| `jak2/features/dark_jak_enhanced` | ⚠️ Conflit | `2001b0711 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/dark_jak_enhanced && git merge origin/master-dev` |
| `jak2/features/jak3-jetBoard` | ⚠️ Conflit | `64a15539d - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/jak3-jetBoard && git merge origin/master-dev` |
| `jak2/features/paddywagon/traffic` | ⚠️ Conflit | `e04301b97 - feat(paddywagon): both traffic lanes + Jak keeps his gun while driving (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/paddywagon/traffic && git merge origin/master-dev` |
| `jak2/features/transport-ag/alert` | ⚠️ Conflit | `c6b130a3b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/transport-ag/alert && git merge origin/master-dev` |
| `jak2/features/transport-ag/traffic` | ⚠️ Conflit | `4b3915712 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/transport-ag/traffic && git merge origin/master-dev` |
| `jak2/features/yakow_killable` | ⚠️ Conflit | `417e7a71b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak2/features/yakow_killable && git merge origin/master-dev` |
| `jak3/config/memory_increase` | ⚠️ Conflit | `d60c2ebae - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak3/config/memory_increase && git merge origin/master-dev` |
| `jak3/features/city-behavior` | ⚠️ Conflit | `3842eaae6 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak3/features/city-behavior && git merge origin/master-dev` |
| `jak3/features/jak2_skin_secret` | ⚠️ Conflit | `be88206cf - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak3/features/jak2_skin_secret && git merge origin/master-dev` |
| `jak3/features/mega_dark_jak` | ⚠️ Conflit | `cd6220d59 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak3/features/mega_dark_jak && git merge origin/master-dev` |
| `jak3/features/redguard-entity` | ⚠️ Conflit | `ae5334c70 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | • `README.md`<br>• `docs/modding/branch_audit.md` | `git checkout jak3/features/redguard-entity && git merge origin/master-dev` |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
