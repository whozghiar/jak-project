# Jak 1 — Known Pitfalls & Best Practices / Pièges Connus & Bonnes Pratiques

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Common Traps & Points of Vigilance

* **Symbol Loading Order:** Parent types must strictly be declared before child types in `.gp` and file include lists.
* **REPL Ghost Memory:** Always perform a clean cold restart of the REPL to ensure changes compile from scratch without relying on stale runtime state.
* **Git Synchronization:** Regularly merge verified discoveries from this file back to `master`.

---

# 🇫🇷 Version Française

## Pièges Fréquents & Points de Vigilance

* **Ordre de Chargement des Symboles :** Les types parents doivent impérativement être déclarés avant les types enfants dans les fichiers `.gp`.
* **REPL Ghost Memory :** Toujours valider les modifications avec un redémarrage à froid du REPL pour s'assurer d'une compilation complète sans état résiduel.
* **Synchronisation Git :** Synchroniser régulièrement les ajouts validés avec la branche `master`.
