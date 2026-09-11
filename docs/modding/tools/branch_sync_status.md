# 📊 État de Synchronisation des Branches de Mods

> **Dernière mise à jour :** `2026-09-11 13:39:20 UTC`  
> **Branche source :** `master-dev` (`e2f7032b7`)  
> **Statut global :** 0/15 synchronisées (0 conflits)

| Branche | Statut | Dernier Commit Branche | Conflits / Détails | Commande de Résolution |
| :--- | :---: | :--- | :--- | :--- |
| `jak2/config/enhanced_spawnrates` | ⚠️ Erreur push | `2d2b11e3a - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/config/start_menu_wheel` | ⚠️ Erreur push | `50a05cef4 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/crimson-blueguard/city-insurrection` | ⚠️ Erreur push | `2d2dddaa5 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/crimson-blueguard/peaceful` | ⚠️ Erreur push | `104874cfd - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/dark_jak_enhanced` | ⚠️ Erreur push | `2001b0711 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/jak3-jetBoard` | ⚠️ Erreur push | `64a15539d - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/paddywagon/traffic` | ⚠️ Erreur push | `e04301b97 - feat(paddywagon): both traffic lanes + Jak keeps his gun while driving (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/transport-ag/alert` | ⚠️ Erreur push | `c6b130a3b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/transport-ag/traffic` | ⚠️ Erreur push | `4b3915712 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak2/features/yakow_killable` | ⚠️ Erreur push | `417e7a71b - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/config/memory_increase` | ⚠️ Erreur push | `d60c2ebae - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/city-behavior` | ⚠️ Erreur push | `3842eaae6 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/jak2_skin_secret` | ⚠️ Erreur push | `be88206cf - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/mega_dark_jak` | ⚠️ Erreur push | `cd6220d59 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |
| `jak3/features/redguard-entity` | ⚠️ Erreur push | `ae5334c70 - docs: sync documentation architecture and agent skills from master-dev (AI-assisted)` | Échec checkout: error: Your local changes to the following files would be overwritten by checkout:
	.github/workflows/sync-upstream.yaml | — |

---
### Guide de Résolution des Conflits
Lorsqu'une branche affiche un conflit :
1. Basculez sur la branche en local : `git checkout <branche>`
2. Récupérez les modifications de la source : `git merge origin/master-dev`
3. Résolvez les fichiers en conflit listés dans le tableau ci-dessus.
4. Testez la compilation (`task build-release`).
5. Commitez et poussez votre résolution : `git commit -m "fix: resolve merge conflicts with master (AI-assisted)" && git push`

*(Ce fichier est mis à jour automatiquement par le workflow `sync-upstream.yaml` ou le script `scripts/modding/sync_branches_with_master.py`)*
