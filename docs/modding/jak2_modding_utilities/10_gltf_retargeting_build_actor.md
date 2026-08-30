# Jak 2 — GLTF Retargeting & `build-actor` Skeletons / Reciblage GLTF & Squelettes `build-actor`

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/jak3-jetBoard`
> - **Last Updated / Dernière modification:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## GLTF Animation Retargeting & `build-actor` Joint Indexing

### Skeletons in OpenGOAL vs GLTF
In OpenGOAL, character skeletons (like `jakb-lod0-jg`) contain:
1. **2 Matrix joints (indices 0 & 1):** `align` (Matrix 0) and `prejoint` (Matrix 1).
2. **61 TransformQ joints (indices 2 to 62):** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

### ⚠️ The Duplicate `align` Pitfall in `build-actor` (Off-By-One Shift)
- `convert_joints` in `goalc/build_actor/common/build_actor.cpp` historically prepended a synthetic `"align"` joint at index 0 and offset all GLTF skin joints by `+1` (assuming external models lacked an align joint).
- Because decompiled models (`jakb-lod0.glb`) **already include `align` at index 0**, this created 64 joints instead of 63, shifting every TransformQ joint by `+1` during playback (`main` mapped to `waist_prog`, `waist_prog` to `upper_body`, `hips` to `Lthigh`).
- **Symptom:** Animation looks 100% perfect in Blender, but in-game the mesh stretches/dislocates violently whenever the imported animation is evaluated.
- **Rule:** Always detect if `gjoints[0].name == "align"` and use direct 0-indexed mapping (`prefix_count = 0`), producing `num_joints = 61` matching native `jakb-ag`.

---

# 🇫🇷 Version Française

## Reciblage d'Animations GLTF & Indexation de Squelette dans `build-actor`

### Les Squelettes dans OpenGOAL vs GLTF
Dans OpenGOAL, les squelettes de personnages (comme `jakb-lod0-jg`) contiennent :
1. **2 joints Matriciels (index 0 et 1) :** `align` (Matrice 0) et `prejoint` (Matrice 1).
2. **61 joints TransformQ (index 2 à 62) :** `main` (TQ 0), `waist_prog` (TQ 1), ..., `hips` (TQ 23), `Lthigh` (TQ 24), ..., `pantsRthigh` (TQ 60).

### ⚠️ Le Piège du Double `align` dans `build-actor` (Décalage de +1 Os)
- `convert_joints` (`goalc/build_actor/common/build_actor.cpp`) insérait historiquement un os `"align"` synthétique à l'index 0 et décalait tous les os du GLTF de `+1` (en supposant que les modèles externes n'avaient pas d'align).
- Comme les modèles décompilés (`jakb-lod0.glb`) **possèdent déjà `align` à l'index 0**, cela créait 64 joints au lieu de 63, décalant chaque os TransformQ de `+1` (`main` vers `waist_prog`, `waist_prog` vers `upper_body`, `hips` vers `Lthigh`).
- **Symptôme :** L'animation paraît parfaite dans Blender, mais en jeu le maillage se disloque et s'étire violemment à la lecture de l'animation.
- **Règle :** Toujours détecter si `gjoints[0].name == "align"` et utiliser une indexation directe à 0 (`prefix_count = 0`), produisant `num_joints = 61` identique aux animations natives de `jakb-ag`.
