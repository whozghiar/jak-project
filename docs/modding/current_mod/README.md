# Mod Technical Deep-Dive Documentation / Documentation Technique Approfondie des Mods (`docs/modding/current_mod/`)

> **Bilingual Architecture Guide / Guide d'Architecture Bilingue**
>
> - **Audience / Public :** AI Coding Agents, Maintainers & Developers
> - **Scope / Portée :** Tier 2 Technical Deep-Dive Documentation Guidelines

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

> ### 📑 Summary / Sommaire
>
> - 🇬🇧 **English:** [1. Purpose & Philosophy](#1-purpose--philosophy) · [2. Naming Convention](#2-naming-convention) · [3. Recommended Structure](#3-recommended-structure-for-mod-technical-readmes) · [4. Texture Packs for Releases](#4-texture-packs-for-releases-texture_packs)
> - 🇫🇷 **Français :** [1. Objectif & Philosophie](#1-objectif--philosophie) · [2. Convention de Nommage](#2-convention-de-nommage) · [3. Structure Recommandée](#3-structure-recommandée-des-readmes-techniques) · [4. Packs de Textures pour les Releases](#4-packs-de-textures-pour-les-releases-texture_packs-1)

---

# 🇬🇧 English Version

This directory is the dedicated space for **Tier 2 Technical Documentation** for active mod features and subsystems.

---

## 1. Purpose & Philosophy

While the mod's **root `README.md`** is player/user-facing (overview, features, how to compile, game controls, video demonstration), files in this directory provide **pedagogical, in-depth engineering documentation** for developers, AI agents, and future maintainers.

---

## 2. Naming Convention

```text
docs/modding/current_mod/<mod_slug>_readme.md
```
*(e.g., `docs/modding/current_mod/custom_animation_and_sound_readme.md`)*

---

## 3. Recommended Structure for Mod Technical Readmes

Each technical mod document should adopt a structured, educational approach featuring:

1. **Architecture & Subsystems Impacted:**
   - Affected layers (C++ runtime, decompiler, compiler, GOAL game code, asset pipelines).
   - Core concepts and design decisions.
2. **Pedagogical Walkthrough & Data Pipelines:**
   - Step-by-step breakdown of how data flows (e.g., glTF ➔ `build-actor` ➔ art-group ➔ Merc2 `.fr3`).
   - Skeletons, joints, animation mapping, or audio bank ingestion.
3. **Concrete Code Samples:**
   - Real, commented OpenGOAL Lisp snippets (`deftype`, `defstate`, `defbehavior`, hooks).
   - Avoid generic pseudo-code; provide verified, syntax-valid GOAL code.
4. **State Machine & Logic Diagrams:**
   - Process states (`:enter`, `:trans`, `:code`, `:post`, `:event`), transition triggers, and conditions.
5. **Memory, Heap & Performance Footprint:**
   - Heap allocation targets (`'global` vs `'level` vs `'process`), alignment requirements, and budget impact.
   - Traceability of memory leak hazards.
6. **Debugging & Troubleshooting Guide:**
   - Common traps, known edge cases, and REPL verification procedures.

---

## 4. Texture Packs for Releases (`texture_packs/`)

Any mod branch that provides a custom texture pack can store its packaged archive(s) inside:
```text
docs/modding/current_mod/texture_packs/<slug>-v<version>.zip
```

### Why this directory?
- **Git Tracked:** Unlike `custom_assets/jak*/texture_replacements/*`, this directory is **not** ignored by `.gitignore`.
- **Branch-Sync Protected:** Classified as `"ours"` in `scripts/modding/sync_common.py`, meaning it is never wiped or overwritten when merging `master-dev`.
- **Automatic Release Asset Upload:** The GitHub Actions release workflow (`.github/workflows/release.yml`) automatically collects all `.zip` archives from this directory, computes their SHA-256 hashes, registers them under `"texturePacks"` in `index.json`, and attaches them to the published GitHub Release assets!

---

# 🇫🇷 Version Française

Ce dossier est l'espace dédié à la **Documentation Technique de Niveau 2** pour les fonctionnalités et sous-systèmes de mods en cours de développement.

---

## 1. Objectif & Philosophie

Tandis que le **`README.md` racine** du mod s'adresse aux joueurs et utilisateurs (présentation, fonctionnalités clés, guide de compilation, contrôles en jeu, vidéo de démonstration), les documents de ce dossier fournissent une **documentation d'ingénierie pédagogique et approfondie** pour les développeurs, agents IA et futurs mainteneurs.

---

## 2. Convention de Nommage

```text
docs/modding/current_mod/<mod_slug>_readme.md
```
*(ex : `docs/modding/current_mod/custom_animation_and_sound_readme.md`)*

---

## 3. Structure Recommandée des Readmes Techniques

Chaque document technique de mod doit adopter une approche structurée et pédagogique comprenant :

1. **Architecture & Sous-Systèmes Impactés :**
   - Couches concernées (runtime C++, décompilateur, compilateur, code de jeu GOAL, pipelines d'assets).
   - Concepts fondamentaux et choix d'architecture.
2. **Cheminement Pédagogique & Pipelines de Données :**
   - Décomposition étape par étape du flux de données (ex : glTF ➔ `build-actor` ➔ art-group ➔ Merc2 `.fr3`).
   - Squelettes, articulations, correspondance des animations ou ingestion de banques audio.
3. **Exemples Concrets de Code :**
   - Extraits OpenGOAL Lisp réels et commentés (`deftype`, `defstate`, `defbehavior`, hooks).
   - Bannir le pseudo-code ; fournir du code GOAL à la syntaxe valide et testée.
4. **Diagrammes de Machines à États & Logique :**
   - États de processus (`:enter`, `:trans`, `:code`, `:post`, `:event`), déclencheurs de transitions et conditions.
5. **Empreinte Mémoire, Heaps & Performances :**
   - Cibles d'allocation sur les tas (`'global` vs `'level` vs `'process`), alignements et respect des budgets mémoire.
   - Traçabilité et prévention des fuites mémoire.
6. **Guide de Débogage & Résolution des Problèmes :**
   - Pièges fréquents, cas limites connus et procédures de validation au REPL.

---

## 4. Packs de Textures pour les Releases (`texture_packs/`)

Toute branche de mod fournissant un pack de textures dédié peut stocker ses archives `.zip` dans :
```text
docs/modding/current_mod/texture_packs/<slug>-v<version>.zip
```

### Pourquoi cet emplacement ?
- **Suivi par Git :** Contrairement à `custom_assets/jak*/texture_replacements/*`, ce dossier **n'est pas** ignoré par `.gitignore`.
- **Protégé lors des fusions :** Classé en `"ours"` dans `scripts/modding/sync_common.py`, il n'est jamais écrasé ni effacé lors des synchronisations avec `master-dev`.
- **Publication automatique en Release :** Le workflow GitHub Actions (`.github/workflows/release.yml`) collecte automatiquement toutes les archives `.zip` de ce répertoire, calcule leurs empreintes SHA-256, les enregistre sous `"texturePacks"` dans `index.json` et les attache aux assets de la release GitHub !
