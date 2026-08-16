# Jak 2 — Running the Game & Reading Boot Logs / Lancer le Jeu & Lire les Logs

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Boot Commands & Diagnostic Logs

Boot with debug and verbose logging:
```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Check log files in `log/jak2.<timestamp>.log`:
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<timestamp>.log
```

---

# 🇫🇷 Version Française

## Commandes de Lancement & Analyse des Logs

Lancer le jeu en mode debug verbeux :
```bash
./gk.exe -v --game jak2 -- -boot -fakeiso -debug
```
Vérification des logs d'exécution :
```bash
grep -iE "main memory|bad address|not a valid object|unable to malloc" log/jak2.<horodatage>.log
```
