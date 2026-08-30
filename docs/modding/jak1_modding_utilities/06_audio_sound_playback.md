# Jak 1 — Audio & Sound Playback / Audio & Lecture de Sons

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - **Last Updated / Dernière modification:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Sound Triggering Methods

* **Simple SFX Playback:**
  ```lisp
  (sound-play "sound-name")
  ```
* **Positional / Entity-Bound SFX:**
  ```lisp
  (sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
  ```

---

# 🇫🇷 Version Française

## Méthodes de Déclenchement Audio

* **Lecture d'Effet Sonore Simple :**
  ```lisp
  (sound-play "sound-name")
  ```
* **Lecture Spatialisée / Liée à une Entité :**
  ```lisp
  (sound-play-by-name (static-sound-name "sound-name") (new-sound-id) 1024 0 0 (sound-group sfx) #t)
  ```
