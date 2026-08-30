# Jak 3 — Secrets Menu System (`game-secrets`) / Système du Menu des Secrets (`game-secrets`)

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak3/features/jak2_skin_secret` (technical investigation: `secrets-menu.gc`, `progress-draw-pc.gc`)
> - **Last Updated / Dernière modification:** `jak3/features/jak2_skin_secret`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Secrets Bitmask Definition (`game-secrets`)
* **Bitfield Enum:** Secrets and cheats in Jak 3 are tracked through the `game-secrets` bitfield declared in `settings-h.gc`.
* **State Persistence:** Active secrets are saved in the game state within `(-> *game-info* secrets)` and can be checked using `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

## 2. Secrets Menu Structure (`secrets-menu.gc`)
* **Menu Entries:** Purchasable and toggleable items are registered inside static arrays such as `*menu-secrets-array*` using `secret-item-option` instances.
* **Key Fields:**
  - `:name`: `text-id` specifying the localization string ID.
  - `:cost`: Orb cost required to unlock (`0` allows free activation).
  - `:secret`: Corresponding bit flag from the `game-secrets` enum.
  - `:avail-after`: `game-task-node` prerequisite determining when the item appears in the menu.
  - `:flags`: Behavior attributes (e.g. `(secret-item-option-flags sf1)`).

## 3. UI Label Resolution (`progress-draw-pc.gc`)
* **Custom & Unlocalized Names:** When adding or overriding secrets that lack dedicated strings in the text database, label strings are mapped dynamically during option rendering in `progress-draw-pc.gc`.

---

# 🇫🇷 Version Française

## 1. Définition du Masque de Secrets (`game-secrets`)
* **Énumération Bitfield :** Les secrets et cheats de Jak 3 sont répertoriés dans le champ de bits `game-secrets` déclaré dans `settings-h.gc`.
* **Persistance d'État :** L'état actif des secrets est conservé dans `(-> *game-info* secrets)` et testé via `(logtest? (game-secrets <flag>) (-> *game-info* secrets))`.

## 2. Structure du Menu des Secrets (`secrets-menu.gc`)
* **Déclaration des Éléments :** Les éléments déblocables et activables sont configurés dans des tableaux statiques comme `*menu-secrets-array*` via des structures `secret-item-option`.
* **Champs Principaux :**
  - `:name` : Identifiant `text-id` de la chaîne de texte localisée.
  - `:cost` : Coût en orbes (`0` pour activation gratuite).
  - `:secret` : Drapeau correspondant dans `game-secrets`.
  - `:avail-after` : Prérequis de progression `game-task-node` pour l'affichage dans le menu.
  - `:flags` : Attributs de comportement (ex. `(secret-item-option-flags sf1)`).

## 3. Résolution des Textes UI (`progress-draw-pc.gc`)
* **Noms Personnalisés ou Non Localisés :** Pour les options de secrets ne disposant pas d'entrée dédiée dans les fichiers de texte, le libellé est géré dynamiquement lors du rendu dans `progress-draw-pc.gc`.
