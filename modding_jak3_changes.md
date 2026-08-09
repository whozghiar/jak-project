# Modding Jak 3 - Change Log

| Date       | Touched/Created Files | Technical Description | Objective |
|------------|-----------------------|-----------------------|-----------|
| 2026-08-07 | `goal_src/jak3/levels/city/traffic/citizen/guard.gc`, `goal_src/jak3/levels/city/common/ff-squad-control.gc`, `goal_src/jak3/levels/wascity/cty-faction.gc`, `goal_src/jak3/pc/debug/default-menu-pc.gc` | Reworked Freedom Faction guard behavior (neutral by default, collective hostile aggro on attack, fast alert decay, combat music `cityfi`) and implemented dynamic City Modes (`*city-mode*`, `set-city-mode!`) integrated directly into the OpenGOAL PC Debug Menu under "City Mods" (Jak 2 Mode vs Chaos Mode). | Implement "[Mod] City Behavior": Jak 2-style guard hostility & dynamic City War / Jak 2 mode switcher via Debug Menu. |
| 2026-08-09 | `goal_src/jak3/levels/wascity/cty-faction.gc`, `goal_src/jak3/pc/debug/default-menu-pc.gc`, `modding_jak3_changes.md` | Added third City Mode `'default` representing post-game state (`city-power-game-resolution` faction strengths and default traffic/spawner quotas). Integrated option in PC Debug Menu under "City Mods". | Provide full end-game spawn behavior option alongside Jak 2 mode and Chaos mode. |

## [Mod] City Behavior

### Description
Le mod **City Behavior** apporte une refonte complète du comportement des gardes et du système de factions dans les secteurs d'Haven City pour Jak 3. Il permet de retrouver l'ambiance urbaine de Jak 2 tout en offrant une bascule dynamique vers un mode de guerre totale en ville ou un retour aux spawns par défaut de fin de jeu.

### Utilité & Fonctionnalités
1. **Comportement des Gardes FF (Style Jak 2)** :
   - Par défaut, les gardes de la Freedom Faction patrouillent pacifiquement en ville et n'attaquent pas Jak à vue.
   - Si Jak attaque un garde, une alerte collective s'enclenche : les gardes dégainent et le prennent immédiatement en chasse.
   - La musique de combat (`cityfi`) retentit pendant toute la durée de l'alerte.
   - Fin d'alerte rapide (~3 secondes) dès que Jak se met à l'abri hors du champ de vision des gardes.

2. **Modes de Ville Dynamiques (`City Mods`)** :
   - **Mode Default (Fin du jeu / 100%)** : Configure le spawner et la répartition des factions comme à la fin du jeu (`city-power-game-resolution`) : réactivation globale des spawners KG et MH, renforts FF (+5) et MH (+5) dans la zone industrielle, invasion KG (+5) dans les Slums, et escarmouches aux frontières du Port (+1 KG / +1 MH).
   - **Mode Jak 2** *(Mode par défaut)* : Spawns d'ennemis (Metalheads et Robots Krimzon Guards) désactivés. Gardes FF pacifiques.
   - **Mode Chaos** : Déclenche la guerre totale en ville. Des patrouilles d'attaque Metalheads, Krimzon Guards et Freedom Faction Guards sont générées en continu et s'affrontent à travers tous les territoires d'Haven City.

### Mode d'Emploi
1. Lancer le jeu OpenGOAL Jak 3.
2. Ouvrir le **Menu Debug** PC (touche `R3` ou raccourci Debug).
3. Naviguer vers la rubrique **`City Mods`**.
4. Sélectionner l'option souhaitée :
   - **`Activer le Mode Default (Fin du Jeu)`** : Pour appliquer le comportement de spawn standard de fin de jeu.
   - **`Activer le Mode Jak 2 (Gardes Neutres)`** : Pour repasser en ville calme avec gardes pacifiques.
   - **`Activer le Mode Chaos (Guerre Totale)`** : Pour basculer instantanément la ville en état de guerre générale.
