#!/usr/bin/env python3
"""
Official Mod README Generator and Deployer for all mod branches.
Deploys bilingual (EN/FR) official READMEs with:
- Navigation header (EN / FR)
- Simple non-technical feature explanation
- Step-by-step setup guide (game select, binary rebuild necessity, asset extraction necessity, launch command)
- Dedicated demonstration video block (docs/modding/current_mod/[feature].mp4)
- Collapsible technical details with link to docs/modding/current_mod/
"""

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def extract_youtube_id(url):
    """Extract 11-character YouTube video ID from various YouTube URL formats."""
    if not url:
        return None
    match = re.search(r"(?:youtu\.be/|youtube\.com/(?:embed/|v/|watch\?v=|watch\?.+&v=))([\w-]{11})", url)
    if match:
        return match.group(1)
    return url.strip()

MODS_CONFIG = {
    "jak2/config/custom_animation_and_sound": {
        "title_en": "Custom Animation & Sound Import Tooling",
        "title_fr": "Outils d'Import d'Animations et de Sons Custom",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Provides dedicated tooling and engine hooks to import custom skeletal 3D animations (from glTF) and custom sound banks (.sbk) directly into Jak 2.",
        "desc_fr": "Fournit des outils dédiés et des passerelles moteur pour importer des animations 3D personnalisées (au format glTF) ainsi que des banques de sons personnalisées (.sbk) directement dans Jak 2.",
        "features_en": [
            "Animation retargeting tool converting modern 3D formats into native OpenGOAL art-groups.",
            "Sound bank compiler utility packaging WAV samples into engine-compatible SBK banks.",
            "Seamless playback integration within existing Jak 2 character rigs."
        ],
        "features_fr": [
            "Outil de retargeting d'animations convertissant les formats 3D modernes en art-groups natifs OpenGOAL.",
            "Utilitaire de compilation de banques sonores empaquetant les fichiers WAV en banques SBK compatibles.",
            "Intégration transparente de la lecture d'animations sur les squelettes existants de Jak 2."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. The mod introduces custom C++ build executables (`build_sbk` and `retarget_anim`) inside `goalc/`.",
        "binaries_reason_fr": "Requise. Le mod introduit de nouveaux exécutables C++ (`build_sbk` et `retarget_anim`) dans `goalc/`.",
        "extract_assets": True,
        "extract_reason_en": "Required if you are rebuilding custom sound banks or baking new animation data into levels.",
        "extract_reason_fr": "Requise si vous compilez de nouvelles banques sonores ou intégrez de nouvelles animations aux niveaux.",
        "video_file": "docs/modding/current_mod/custom_animation_and_sound.mp4",
        "doc_file": "docs/modding/current_mod/custom_animation_and_sound_readme.md",
        "tech_summary_en": "Extends `goalc/CMakeLists.txt` with standalone CLI executables linking `tiny_gltf` and sound builders, interfacing with GOAL `sound-bank` and `art-group` structures.",
        "tech_summary_fr": "Étend `goalc/CMakeLists.txt` avec des exécutables CLI autonomes liés à `tiny_gltf` et des générateurs audio interfaçant les structures GOAL `sound-bank` et `art-group`."
    },
    "jak2/config/enhanced_spawnrates": {
        "title_en": "Enhanced Spawn Rates & Nav-Mesh Limits",
        "title_fr": "Taux de Spawn et Limites Nav-Mesh Renforcés",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Increases civilian density, Crimson Guard patrol frequencies, and vehicle spawn volumes in Haven City while expanding navigation mesh quotas to prevent despawns.",
        "desc_fr": "Augmente la densité des piétons, la fréquence des patrouilles de gardes et le volume des véhicules dans Haven City, tout en augmentant les quotas nav-mesh pour éviter les disparitions.",
        "features_en": [
            "Higher ambient traffic and pedestrian density across all Haven City zones.",
            "Elevated Crimson Guard alert spawns during combat and chases.",
            "Increased nav-mesh and pathfinding table buffers to prevent entity despawning."
        ],
        "features_fr": [
            "Densité accrue de la circulation et des piétons dans l'ensemble des quartiers de Haven City.",
            "Renforts de gardes plus nombreux et plus réactifs lors des phases d'alerte et de combat.",
            "Augmentation des tampons de navigation pour préserver la persistance des entités actives."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. Changes are purely written in high-level GOAL engine scripts.",
        "binaries_reason_fr": "Non requise. Les modifications sont entièrement contenues dans des scripts GOAL de haut niveau.",
        "extract_assets": False,
        "extract_reason_en": "Not required. The mod operates on standard Jak 2 game assets.",
        "extract_reason_fr": "Non requise. Le mod fonctionne avec les assets standards de Jak 2.",
        "video_file": "docs/modding/current_mod/enhanced_spawnrates.mp4",
        "doc_file": "docs/modding/current_mod/enhanced_spawnrates_readme.md",
        "tech_summary_en": "Adjusts spawn controllers in `goal_src/jak2/levels/city/common/` and expands navigation table constants in `traffic-h.gc`.",
        "tech_summary_fr": "Ajuste les contrôleurs de spawn dans `goal_src/jak2/levels/city/common/` et élève les constantes de table de navigation dans `traffic-h.gc`."
    },
    "jak2/config/memory_increase": {
        "title_en": "512 MB Main Memory Heap Expansion",
        "title_fr": "Extension de la Mémoire Vive à 512 Mo",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Expands the OpenGOAL global RAM heap from the original 128 MB to a massive 512 MB, enabling heavy custom geometry, dense traffic, and large asset packs without memory overflows.",
        "desc_fr": "Étend la mémoire vive allouée au moteur OpenGOAL de 128 Mo à 512 Mo, permettant d'accueillir des géométries lourdes, un trafic dense et des packs d'assets conséquents sans saturation mémoire.",
        "features_en": [
            "Quadrupled engine memory headroom (512 MB total).",
            "Eliminates out-of-memory crashes when spawning numerous vehicles or custom actors.",
            "Provides safe memory space for complex future mod additions."
        ],
        "features_fr": [
            "Capacité mémoire quadruplée pour le moteur (512 Mo au total).",
            "Élimine les plantages par manque de mémoire lors de l'apparition de nombreux véhicules ou acteurs custom.",
            "Offre une marge de sécurité idéale pour les futurs ajouts de mods complexes."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. Memory layout constants are defined in C++ headers (`goal_constants.h` and `memory_layout.h`).",
        "binaries_reason_fr": "Requise. Les constantes d'allocation mémoire sont définies dans les en-têtes C++ (`goal_constants.h` et `memory_layout.h`).",
        "extract_assets": False,
        "extract_reason_en": "Not required. The memory expansion works out of the box with standard assets.",
        "extract_reason_fr": "Non requise. L'extension mémoire s'applique directement avec les assets standards.",
        "video_file": "docs/modding/current_mod/memory_increase.mp4",
        "doc_file": "docs/modding/jak2_modding_utilities/02_memory_architecture.md",
        "tech_summary_en": "Reconfigures `GLOBAL_HEAP_END` and `DEBUG_LEVEL_HEAP_MULT` in C++ runtime alongside GOAL kernel heap allocators.",
        "tech_summary_fr": "Reconfigure `GLOBAL_HEAP_END` et `DEBUG_LEVEL_HEAP_MULT` dans le runtime C++ ainsi que les allocateurs de heap du noyau GOAL."
    },
    "jak2/config/start_menu_wheel": {
        "title_en": "Start Menu Radial Navigation Wheel",
        "title_fr": "Menu Pause à Navigation Circulaire",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Implements an intuitive radial wheel navigation system inside the pause and options menu, allowing quick selection using directional inputs or analog sticks.",
        "desc_fr": "Implémente un système de navigation circulaire intuitif dans le menu pause et options, permettant une sélection rapide à l'aide des sticks analogiques ou des touches directionnelles.",
        "features_en": [
            "Modern radial selection interface for menus.",
            "Smooth analog and D-Pad responsiveness.",
            "Seamless compatibility with standard pause menu options."
        ],
        "features_fr": [
            "Interface de sélection circulaire moderne pour les menus.",
            "Réponse fluide au stick analogique et à la croix directionnelle.",
            "Compatibilité totale avec toutes les options classiques du menu pause."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. Implemented purely in GOAL UI scripts.",
        "binaries_reason_fr": "Non requise. Implémenté uniquement dans les scripts d'interface GOAL.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Uses native interface fonts and textures.",
        "extract_reason_fr": "Non requise. Utilise les polices et textures d'interface natives.",
        "video_file": "docs/modding/current_mod/start_menu_wheel.mp4",
        "doc_file": "docs/modding/current_mod/start_menu_wheel_readme.md",
        "tech_summary_en": "Hooks into `goal_src/jak2/engine/ui/progress/progress.gc` menu drawing and input handling routines.",
        "tech_summary_fr": "Se branche sur les routines de rendu et de gestion des entrées dans `goal_src/jak2/engine/ui/progress/progress.gc`."
    },
    "jak2/features/dark_jak_enhanced": {
        "title_en": "Dark Jak Enhanced Combat & Abilities",
        "title_fr": "Dark Jak Amélioré & Nouveaux Combats",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Reworks Dark Jak's moveset, introducing extended combo mechanics, increased attack reach, adjusted eco consumption, and responsive combat transitions.",
        "desc_fr": "Revisite la palette de mouvements de Dark Jak en introduisant des enchaînements de combos prolongés, une allonge d'attaque accrue, un équilibrage de la consommation d'éco et des transitions fluides en combat.",
        "features_en": [
            "Extended combo strings and punch-spin variations for Dark Jak.",
            "Rebalanced Dark Eco drain for longer, more satisfying combat phases.",
            "Dynamic damage scaling and enhanced impact particle effects."
        ],
        "features_fr": [
            "Combos prolongés et variations d'attaques tourniquet pour Dark Jak.",
            "Consommation d'Éco Noire rééquilibrée pour des phases de combat plus intenses et gratifiantes.",
            "Dégâts réajustés et renforcement visuel des impacts."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. Modified entirely in target state machines within GOAL.",
        "binaries_reason_fr": "Non requise. Modifié intégralement dans les machines à états de Jak en GOAL.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Uses standard Dark Jak assets and sounds.",
        "extract_reason_fr": "Non requise. Utilise les assets et bruitages standards de Dark Jak.",
        "video_file": "docs/modding/current_mod/dark_jak_enhanced.mp4",
        "doc_file": "docs/modding/current_mod/dark_jak_enhanced_readme.md",
        "tech_summary_en": "Modifies `target-darkjak.gc` state handlers (`target-darkjak-running`, `target-darkjak-smack`) and eco meter decay logic.",
        "tech_summary_fr": "Modifie les gestionnaires d'états dans `target-darkjak.gc` (`target-darkjak-running`, `target-darkjak-smack`) et la logique d'épuisement de la jauge d'éco."
    },
    "jak2/features/enhanced_city_traffic_v2": {
        "title_en": "Haven City Traffic Overhaul V2",
        "title_fr": "Refonte du Trafic de Haven City V2",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Upgrades Haven City's airspace with enhanced traffic density, diverse zoomer types across districts, and dynamic guard vehicle intercept behaviors.",
        "desc_fr": "Met à niveau l'espace aérien de Haven City avec une circulation plus dense, une variété accrue de zoomers selon les quartiers et des comportements d'interception par les gardes.",
        "features_en": [
            "Denser and more lively civilian vehicle flows.",
            "District-specific zoomer distribution across Haven City sectors.",
            "Improved traffic lane management avoiding vehicle clustering."
        ],
        "features_fr": [
            "Flux de véhicules civils plus denses et vivants.",
            "Distribution thématique des modèles de zoomers selon les quartiers de la ville.",
            "Gestion optimisée des couloirs aériens évitant les embouteillages anormaux."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. The branch inherits the modified decompiler (`decompiler/level_extractor/extract_level.cpp`) used to bake injected merc vehicles into level .fr3 files.",
        "binaries_reason_fr": "Requise. La branche hérite du décompilateur modifié (`extract_level.cpp`) requis pour cuire les véhicules injectés dans les fichiers de niveaux .fr3.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) using the freshly built decompiler so the custom vehicle meshes are baked into the city levels.",
        "extract_reason_fr": "Requise (`task extract`) avec le décompilateur recompilé pour cuire les maillages de véhicules dans les niveaux.",
        "video_file": "docs/modding/current_mod/enhanced_city_traffic_v2.mp4",
        "doc_file": "docs/modding/current_mod/traffic_paddywagon_readme.md",
        "tech_summary_en": "Modifies traffic managers in `goal_src/jak2/engine/ai/traffic.gc` and uses the decompiler's `extra_art_groups_by_dgo` FR3 injection.",
        "tech_summary_fr": "Modifie les gestionnaires de trafic dans `traffic.gc` et s'appuie sur l'injection FR3 `extra_art_groups_by_dgo` du décompilateur."
    },
    "jak2/features/jak3-jetBoard": {
        "title_en": "Jak 3 Jetboard Mechanics Port to Jak 2",
        "title_fr": "Portage du Jetboard de Jak 3 dans Jak 2",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Brings the refined, acrobatic Jetboard mechanics from Jak 3 into Jak 2, including enhanced tricks, improved grind physics, responsive jump curves, and custom audio cues.",
        "desc_fr": "Intègre la physique de Jetboard plus acrobatique et souple de Jak 3 dans Jak 2, avec de nouvelles figures, une physique de grind améliorée et une réactivité accrue.",
        "features_en": [
            "Jak 3 jump physics and air-trick combo system.",
            "Refined rail and edge grinding responsiveness.",
            "Custom sound effects and animation blending."
        ],
        "features_fr": [
            "Physique de saut et système de figures aériennes issus de Jak 3.",
            "Accroche et glisse sur les rails optimisées.",
            "Transitions d'animations et effets sonores adaptés."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. The branch includes custom animation compilation and retargeting tools in `goalc/`.",
        "binaries_reason_fr": "Requise. La branche intègre les outils de compilation et retargeting d'animations dans `goalc/`.",
        "extract_assets": True,
        "extract_reason_en": "Required to process and package the ported board animations and sound banks into Jak 2 levels.",
        "extract_reason_fr": "Requise pour traiter et empaqueter les animations du board et les banques sonores dans les niveaux.",
        "video_file": "docs/modding/current_mod/jak3_jetboard.mp4",
        "doc_file": "docs/modding/current_mod/jak3-jetboard_readme.md",
        "tech_summary_en": "Backports physics state handlers from `goal_src/jak3/engine/target/board/` into Jak 2's target board subsystem, linking custom art-groups.",
        "tech_summary_fr": "Rétro-porte les gestionnaires physiques de `goal_src/jak3/engine/target/board/` vers le sous-système board de Jak 2 en liant des art-groups custom."
    },
    "jak2/features/merc-fr3-injection-poc": {
        "title_en": "Merc-Geometry .fr3 Injection Proof of Concept",
        "title_fr": "Preuve de Concept d'Injection .fr3 Merc-Geometry",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Technical breakthrough enabling skeletal 3D models to be permanently resident across any level by baking their merc-geometry directly into `.fr3` level files offline, completely eliminating level borrowing.",
        "desc_fr": "Avancée technique permettant d'injecter des modèles 3D squelettiques dans n'importe quel niveau en intégrant leur géométrie merc directement dans les fichiers de niveau `.fr3` hors-ligne, sans emprunt de niveau.",
        "features_en": [
            "Demonstrates universal actor visibility in all Haven City sectors.",
            "Bypasses PS2 level-borrowing memory limits.",
            "Validates resident drop-ship (`transport-ag`) geometry rendering anywhere."
        ],
        "features_fr": [
            "Prouve la possibilité d'afficher des acteurs universels dans tous les quartiers de Haven City.",
            "Contourne les restrictions historiques d'emprunt de mémoire de la PS2.",
            "Valide l'affichage permanent du vaisseau de transport (`transport-ag`) dans toute la ville."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. Modifies offline decompiler asset baking tools.",
        "binaries_reason_fr": "Requise. Modifie les outils d'assemblage d'assets du décompilateur hors-ligne.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) to bake the injected merc models into the target level `.fr3` files.",
        "extract_reason_fr": "Requise (`task extract`) pour compiler et cuire les modèles injectés dans les fichiers `.fr3` des niveaux.",
        "video_file": "docs/modding/current_mod/merc_fr3_injection_poc.mp4",
        "doc_file": "docs/modding/current_mod/merc_fr3_injection_poc_readme.md",
        "tech_summary_en": "Implements extra art-group merging in decompiler's `MercDataExtractor` to package foreign skeletal meshes into resident FR3 bundles.",
        "tech_summary_fr": "Implémente la fusion d'art-groups supplémentaires dans le `MercDataExtractor` du décompilateur pour intégrer les maillages squelettiques dans les bundles FR3."
    },
    "jak2/features/paddy_wagon_v2": {
        "title_en": "Drivable Prison Zoomer (Paddywagon V2)",
        "title_fr": "Zoomer Pénitentiaire Pilotable (Paddywagon V2)",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Introduces the heavy armored Prison Zoomer (Paddywagon) into Haven City's live traffic and gives Jak the ability to hijack, drive, and fire its onboard weapons.",
        "desc_fr": "Intègre le zoomer blindé pénitentiaire (Paddywagon) dans la circulation active de Haven City et permet à Jak d'en prendre les commandes, de le piloter et d'utiliser ses systèmes.",
        "features_en": [
            "Paddywagon actively spawns and circulates in ambient Haven City traffic.",
            "Full hijacking and driving controls with heavy vehicle handling physics.",
            "Native FR3 baking ensuring the model is always visible without level borrowing."
        ],
        "features_fr": [
            "Le Paddywagon circule naturellement dans le trafic de Haven City.",
            "Possibilité de détourner et piloter le véhicule avec une physique de conduite lourde et blindée.",
            "Intégration FR3 native garantissant la visibilité permanente du véhicule sans emprunt de niveau."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required (`task build-release`). Modifies the decompiler (`decompiler/level_extractor/extract_level.cpp`) to support baking injected merc vehicles into .fr3 files.",
        "binaries_reason_fr": "Requise (`task build-release`). Modifie le décompilateur (`extract_level.cpp`) pour intégrer la cuisson des modèles merc injectés dans les fichiers .fr3.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) using the freshly built decompiler to bake the Paddywagon art-group into city level files.",
        "extract_reason_fr": "Requise (`task extract`) avec le décompilateur recompilé pour cuire l'art-group du Paddywagon dans les niveaux de la ville.",
        "video_file": "docs/modding/current_mod/paddy_wagon_v2.mp4",
        "doc_file": "docs/modding/current_mod/traffic_paddywagon_readme.md",
        "tech_summary_en": "Defines vehicle type entry in `vehicle-h.gc` and control states in `vehicle-states.gc`, baked via `extra_art_groups_by_dgo`.",
        "tech_summary_fr": "Définit le type de véhicule dans `vehicle-h.gc` et les états de contrôle dans `vehicle-states.gc`, injecté via `extra_art_groups_by_dgo`."
    },
    "jak2/features/transport_v2": {
        "title_en": "Drivable Crimson Guard Transport Ship V2",
        "title_fr": "Vaisseau de Transport des Gardes Pilotable V2",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Turns the iconic Crimson Guard Troop Drop-Ship into a fully functional, pilotable flying gunship with vertical alarm spawning and troop delivery mechanics.",
        "desc_fr": "Transforme le célèbre vaisseau de largage des gardes en une canonnière volante entièrement pilotable, avec apparition dynamique lors des alertes et déploiement de troupes.",
        "features_en": [
            "Drivable multi-engine heavy flight physics with vertical thrust controls.",
            "Integrated into city alarm events: spawns vertically from the sky during Crimson alerts.",
            "Custom weapon targeting and troop deployment actions."
        ],
        "features_fr": [
            "Physique de vol lourd multi-moteurs avec contrôle de poussée verticale.",
            "Intégré aux alertes de la ville : apparaît depuis le ciel lors des alertes rouges.",
            "Actions de tir ciblées et possibilité de larguer des troupes."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required (`task build-release`). Modifies the decompiler (`decompiler/level_extractor/extract_level.cpp`) to bake the transport drop-ship geometry into level .fr3 files.",
        "binaries_reason_fr": "Requise (`task build-release`). Modifie le décompilateur (`extract_level.cpp`) pour cuire la carlingue du transport dans les fichiers .fr3 des niveaux.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) using the freshly built decompiler to bake the transport drop-ship art-group into city DGOs.",
        "extract_reason_fr": "Requise (`task extract`) avec le décompilateur recompilé pour intégrer l'art-group du drop-ship dans les DGOs de la ville.",
        "video_file": "docs/modding/current_mod/transport_v2.mp4",
        "doc_file": "docs/modding/current_mod/traffic_guard_transport_readme.md",
        "tech_summary_en": "Hooks transport flight physics into `goal_src/jak2/levels/city/traffic/transport-v.gc` with native collision hull definitions.",
        "tech_summary_fr": "Intègre la physique de vol dans `goal_src/jak2/levels/city/traffic/transport-v.gc` avec définition de coque de collision native."
    },
    "jak2/features/transport_traffic": {
        "title_en": "Crimson Guard Transport Ship in Ambient Traffic",
        "title_fr": "Vaisseau de Transport des Gardes dans le Trafic Aérien",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Integrates transport-v, an authentic Crimson Guard troop transport gunship into Haven City's ambient high-altitude traffic lanes, pilotable by Jak with a functional turret, chasing during alerts, and hovering to drop squads.",
        "desc_fr": "Intègre transport-v, un véritable vaisseau de transport de troupes de la Garde Grenat dans le trafic aérien ambiant d'Abriville, pilotable par Jak avec tourelle fonctionnelle, poursuites d'alerte et largage de troupes.",
        "features_en": [
            "Ambient High-Altitude Gunship: Dual-hull troop transport navigating city flight lanes with seated pilot and minimap icon.",
            "Player Hijacking & Turret Controls: Leap onto the hull to eject the guard, take the helm, and fire the nose turret (R1).",
            "Alert Pursuits & Troop Drop: Pursues Jak during city alerts, locks altitude in place, opens rear hatch, and drops invulnerable guards.",
            "Persistent Turret & Realistic Crash: Synchronized turret child process with LOD and unlocked tumble physics upon fatal damage."
        ],
        "features_fr": [
            "Canonnière dans le Trafic Aérien : Vaisseau de transport à double coque naviguant dans les voies aériennes avec pilote assis et icône minimap.",
            "Prise en Main & Tourelle Joueur : Sautez sur la carlingue pour éjecter le garde, prendre les commandes et tirer à la tourelle de proue (R1).",
            "Poursuite d'Alerte & Déploiement : Traque Jak en alerte, se fige à altitude constante, ouvre la soute arrière et largue des gardes protégés.",
            "Tourelle Persistante & Destruction Réaliste : Processus tourelle synchronisé au pool avec physique de culbutage naturelle en cas de destruction."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required (standard binaries sufficient). The mod executes purely in high-level OpenGOAL scripts.",
        "binaries_reason_fr": "Non requise (binaires standards suffisants). Le mod s'exécute entièrement dans les scripts de haut niveau OpenGOAL.",
        "extract_assets": True,
        "extract_reason_en": "Required once (`task extract`) to bake level packages with injected transport-ag merc geometry.",
        "extract_reason_fr": "Requise une fois (`task extract`) pour compiler les packages de niveaux avec la géométrie merc injectée de transport-ag.",
        "youtube_url": "https://youtu.be/MnqnybexhSA",
        "doc_file": "docs/modding/current_mod/transport_traffic_readme.md"
    },
    "jak2/features/yakow_killable": {
        "title_en": "Interactive & Vulnerable Yakows",
        "title_fr": "Yakows Interactifs et Vulnérables",
        "game": "Jak 2",
        "game_task": "task set-game-jak2",
        "desc_en": "Makes the peaceful Yakow farm animals responsive to player actions and vulnerable to attacks, featuring custom hit reactions, death states, sound cues, and drops.",
        "desc_fr": "Rend les paisibles Yakows de la ferme réactifs aux actions de Jak et vulnérables aux coups, avec des réactions d'impact, un état de mort, des bruitages et du butin.",
        "features_en": [
            "Yakows now react dynamically to kicks, punches, and weapon gunfire.",
            "Custom death animations and comical sound effects upon defeat.",
            "Health and Eco item drops upon defeat."
        ],
        "features_fr": [
            "Les Yakows réagissent désormais dynamiquement aux coups de pied, poings et tirs d'armes.",
            "Animations de chute personnalisées et bruitages comiques lors de la défaite.",
            "Apparition de packs de vie ou d'éco après élimination."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. GOAL scripts handle the health and combat state transitions.",
        "binaries_reason_fr": "Non requise. Les scripts GOAL gèrent la vie et les transitions d'états de combat.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) to process the custom Yakow 3D GLB model and collision data.",
        "extract_reason_fr": "Requise (`task extract`) pour compiler le modèle 3D GLB et les collisions custom du Yakow.",
        "video_file": "docs/modding/current_mod/yakow_killable.mp4",
        "doc_file": "docs/modding/current_mod/yakow_killable_readme.md",
        "tech_summary_en": "Implements `:event` handlers and `yakow-die` states in `goal_src/jak2/levels/city/farm/yakow.gc` using `custom_assets/` GLB meshes.",
        "tech_summary_fr": "Implémente les gestionnaires d'événements et l'état `yakow-die` dans `goal_src/jak2/levels/city/farm/yakow.gc` en s'appuyant sur les maillages GLB de `custom_assets/`."
    },
    "jak3/config/memory_increase": {
        "title_en": "Jak 3 512 MB Main Memory Heap Expansion",
        "title_fr": "Extension Mémoire Vive à 512 Mo pour Jak 3",
        "game": "Jak 3",
        "game_task": "task set-game-jak3",
        "desc_en": "Expands Jak 3's engine memory heap to 512 MB, allowing expansive custom levels, high vehicle counts in the Wasteland, and complex script modifications without crashing.",
        "desc_fr": "Étend la mémoire vive du moteur pour Jak 3 à 512 Mo, permettant de concevoir de grands niveaux custom, d'augmenter le nombre de véhicules dans les Terres Dévastées et d'éviter les crashs mémoire.",
        "features_en": [
            "512 MB total RAM heap headroom for Jak 3.",
            "Eliminates memory exhaustion when exploring massive Wasteland areas with custom mods.",
            "Future-proof foundation for high-poly 3D models and large custom level chunks."
        ],
        "features_fr": [
            "512 Mo de mémoire vive allouée pour Jak 3.",
            "Élimine les plantages par saturation mémoire lors de l'exploration des Terres Dévastées avec des mods.",
            "Base solide pour accueillir des modèles 3D détaillés et des portions de niveaux custom."
        ],
        "rebuild_binaries": True,
        "binaries_reason_en": "Required. C++ memory layout configurations (`common/goal_constants.h`) must be recompiled.",
        "binaries_reason_fr": "Requise. Les constantes de configuration de la mémoire en C++ (`common/goal_constants.h`) doivent être recompilées.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Operates seamlessly with existing Jak 3 game assets.",
        "extract_reason_fr": "Non requise. Fonctionne immédiatement avec les assets existants de Jak 3.",
        "video_file": "docs/modding/current_mod/memory_increase.mp4",
        "doc_file": "docs/modding/jak3_modding_utilities/02_memory_architecture.md",
        "tech_summary_en": "Updates global memory layout boundaries for the Emotion Engine emulator in `memory_layout.h` and GOAL kernel definitions.",
        "tech_summary_fr": "Met à jour les limites d'allocation de l'émulateur Emotion Engine dans `memory_layout.h` et les définitions du noyau GOAL."
    },
    "jak3/features/city-behavior": {
        "title_en": "City & Wasteland Ambient Pedestrian Behaviors",
        "title_fr": "Comportements Ambiants des Citadins et Gardes",
        "game": "Jak 3",
        "game_task": "task set-game-jak3",
        "desc_en": "Enriches non-player character AI in Spargus and Haven City, introducing diverse ambient animations, improved reaction to nearby combat, and varied pathfinding routes.",
        "desc_fr": "Enrichit l'intelligence artificielle des personnages non-joueurs à Spargus et Haven City, en introduisant de nouvelles animations d'ambiance, des réactions au combat et des trajets variés.",
        "features_en": [
            "Civilians react dynamically to gunfights and Wasteland beast intrusions.",
            "Expanded ambient dialogue and idle animation variations.",
            "Smoother crowd pathfinding preventing NPC logjams in narrow alleys."
        ],
        "features_fr": [
            "Les civils réagissent de manière plus vivante aux tirs et à l'intrusion de créatures.",
            "Variété accrue des lignes de dialogue et des postures d'attente des PNJs.",
            "Navigation de foule plus fluide évitant les blocages dans les ruelles étroites."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. Changes reside within GOAL AI scripts.",
        "binaries_reason_fr": "Non requise. Les modifications se situent dans les scripts d'IA en GOAL.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Uses standard Jak 3 character and audio assets.",
        "extract_reason_fr": "Non requise. Utilise les assets et sons standards de Jak 3.",
        "video_file": "docs/modding/current_mod/city_behavior.mp4",
        "doc_file": "docs/modding/current_mod/city-behavior_readme.md",
        "tech_summary_en": "Adjusts civilian state machines in `goal_src/jak3/levels/city/common/ctywide-init.gc` and nav-mesh behavior controllers.",
        "tech_summary_fr": "Ajuste les machines à états des civils dans `goal_src/jak3/levels/city/common/ctywide-init.gc` et les contrôleurs nav-mesh."
    },
    "jak3/features/jak2_skin_secret": {
        "title_en": "Jak II Outfit Secret Unlock in Jak 3",
        "title_fr": "Déblocage de la Tenue Jak II dans les Secrets de Jak 3",
        "game": "Jak 3",
        "game_task": "task set-game-jak3",
        "desc_en": "Adds Jak's iconic Jak II outfit to the in-game Secrets Menu in Jak 3, allowing players to purchase and toggle his classic Haven City rebel appearance at any time.",
        "desc_fr": "Ajoute la tenue emblématique de Jak II dans le Menu des Secrets de Jak 3, permettant aux joueurs de débloquer et d'équiper son apparence classique de rebelle de Haven City à tout moment.",
        "features_en": [
            "Official integration into Jak 3's pause screen Secrets store.",
            "Equips Jak's full classic Jak II 3D mesh throughout gameplay and cutscenes.",
            "Preserves save-file compatibility and secret completion status."
        ],
        "features_fr": [
            "Intégration propre dans la boutique de Secrets du menu pause de Jak 3.",
            "Permet d'arborer le modèle 3D classique de Jak II en jeu et dans les cinématiques.",
            "Préserve la compatibilité des sauvegardes et le suivi des secrets débloqués."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. GOAL UI and secrets table scripts only.",
        "binaries_reason_fr": "Non requise. Concerne uniquement les scripts GOAL d'interface et de secrets.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Jak II model assets are already included natively within Jak 3 files.",
        "extract_reason_fr": "Non requise. Le modèle de Jak II est déjà présent nativement dans les fichiers de Jak 3.",
        "video_file": "docs/modding/current_mod/jak2_skin_secret.mp4",
        "doc_file": "docs/modding/current_mod/jak2_skin_secret_readme.md",
        "tech_summary_en": "Registers `(game-secrets jak-is-jak2)` into `*menu-secrets-array*` in `secrets-menu.gc` and provides text override in `progress-draw-pc.gc`.",
        "tech_summary_fr": "Enregistre `(game-secrets jak-is-jak2)` dans `*menu-secrets-array*` dans `secrets-menu.gc` et configure l'affichage dans `progress-draw-pc.gc`."
    },
    "jak3/features/mega_dark_jak": {
        "title_en": "Mega Dark Jak Overhaul",
        "title_fr": "Transformation Mega Dark Jak Améliorée",
        "game": "Jak 3",
        "game_task": "task set-game-jak3",
        "desc_en": "Overhauls Jak 3's Dark Jak into a devastating powerhouse, featuring increased melee reach, permanent empowered dark strikes, boosted mobility, and enhanced aura effects.",
        "desc_fr": "Transforme le Dark Jak de Jak 3 en une véritable force destructrice, avec une allonge de frappe accrue, des attaques renforcées permanentes, une meilleure mobilité et une aura ténébreuse intensifiée.",
        "features_en": [
            "Enhanced damage multiplier and expanded hitboxes on all Dark Jak attacks.",
            "Dynamic dark energy shockwaves emitted during heavy ground slams.",
            "Extended transformation duration with optimized Dark Eco consumption."
        ],
        "features_fr": [
            "Multiplicateur de dégâts accru et zones d'impact élargies sur toutes les attaques.",
            "Ondes de choc d'énergie noire lors des écrasements au sol.",
            "Durée de transformation prolongée avec gestion optimisée de l'Éco Noire."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. All gameplay changes are implemented in GOAL combat states.",
        "binaries_reason_fr": "Non requise. Les changements sont codés dans les états de combat en GOAL.",
        "extract_assets": False,
        "extract_reason_en": "Not required. Uses standard Jak 3 Dark Jak animations and particle fx.",
        "extract_reason_fr": "Non requise. Utilise les animations et particules natives de Dark Jak.",
        "video_file": "docs/modding/current_mod/mega_dark_jak.mp4",
        "doc_file": "docs/modding/current_mod/mega_dark_jak_readme.md",
        "tech_summary_en": "Modifies Dark Jak behavior states in `goal_src/jak3/engine/target/target-darkjak.gc` including attack damage and collision sphere dimensions.",
        "tech_summary_fr": "Modifie les états de comportement dans `goal_src/jak3/engine/target/target-darkjak.gc`, notamment les tables de dégâts et les sphères de collision."
    },
    "jak3/features/redguard-entity": {
        "title_en": "Crimson Guard Infiltration in Jak 3",
        "title_fr": "Entités Crimson Guard Hostiles dans Jak 3",
        "game": "Jak 3",
        "game_task": "task set-game-jak3",
        "desc_en": "Brings the menacing Crimson Guards from Jak II into the harsh environments of Jak 3, introducing them as fully functional hostile enemy units with custom textures and combat AI.",
        "desc_fr": "Fait revivre les redoutables Crimson Guards de Jak II dans les environnements de Jak 3, sous forme d'unités ennemies hostiles complètes avec textures rouges personnalisées et IA de combat.",
        "features_en": [
            "Fully animated Crimson Guard enemies active in Jak 3 sectors.",
            "Custom high-resolution red armor textures and weapon shielding.",
            "Complete patrol, pursuit, and gunfight AI behavior states."
        ],
        "features_fr": [
            "Ennemis Crimson Guard pleinement animés et actifs dans les secteurs de Jak 3.",
            "Textures haute résolution de l'armure rouge et du bouclier d'énergie.",
            "IA de combat complète avec patrouille, traque et tirs de riposte."
        ],
        "rebuild_binaries": False,
        "binaries_reason_en": "Not required. Uses existing OpenGOAL game runtime.",
        "binaries_reason_fr": "Non requise. S'exécute sur le runtime OpenGOAL standard.",
        "extract_assets": True,
        "extract_reason_en": "Required (`task extract`) to compile the custom Blender 3D models and textures into Jak 3 level packages.",
        "extract_reason_fr": "Requise (`task extract`) pour compiler les modèles 3D Blender et les textures dans les packages de niveaux.",
        "video_file": "docs/modding/current_mod/redguard_entity.mp4",
        "doc_file": "docs/modding/current_mod/redguard-entity_readme.md",
        "tech_summary_en": "Links custom `.glb` meshes from `custom_assets/blender/` into Jak 3 DGO manifests and registers guard entity state machines in GOAL.",
        "tech_summary_fr": "Lie les maillages `.glb` de `custom_assets/blender/` dans les manifests DGO de Jak 3 et enregistre les machines à états des gardes en GOAL."
    }
}

def generate_mod_readme(branch, cfg):
    """Generate the official bilingual README content for a given mod branch."""
    features_en_md = "\n".join([f"- **{f.split(':')[0] if ':' in f else 'Feature'}:** {f.split(':')[1] if ':' in f else f}" for f in cfg["features_en"]])
    features_fr_md = "\n".join([f"- **{f.split(':')[0] if ':' in f else 'Fonctionnalité'} :** {f.split(':')[1] if ':' in f else f}" for f in cfg["features_fr"]])

    bin_status_en = "Required (`task build-release`)" if cfg["rebuild_binaries"] else "Not required (standard binaries sufficient)"
    bin_status_fr = "Requise (`task build-release`)" if cfg["rebuild_binaries"] else "Non requise (binaires standards suffisants)"

    ext_status_en = "Required (`task extract`)" if cfg["extract_assets"] else "Standard extraction sufficient"
    ext_status_fr = "Requise (`task extract`)" if cfg["extract_assets"] else "Extraction standard suffisante"

    # YouTube Video Embed Block
    yt_url = cfg.get("youtube_url")
    if yt_url:
        yt_id = extract_youtube_id(yt_url)
        video_block_en = f"""[![Demonstration Video](https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg)]({yt_url})

▶️ **[Watch the demonstration video on YouTube]({yt_url})**"""
        video_block_fr = f"""[![Vidéo de Démonstration](https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg)]({yt_url})

▶️ **[Visionner la vidéo de démonstration sur YouTube]({yt_url})**"""
    else:
        video_block_en = """> [!NOTE]
> *Demonstration videos are hosted on YouTube to avoid repository bloat.*  
> ▶️ Demonstration video coming soon on YouTube."""
        video_block_fr = """> [!NOTE]
> *Les vidéos de démonstration sont hébergées sur YouTube pour éviter d'alourdir le dépôt Git.*  
> ▶️ Démonstration vidéo prochainement disponible sur YouTube."""

    content = f"""# {cfg["title_en"]} / {cfg["title_fr"]}

<p align="center">
  <img src="https://img.shields.io/badge/OpenGOAL-Mod-blue.svg" alt="OpenGOAL Mod">
  <img src="https://img.shields.io/badge/Game-{cfg["game"].replace(' ', '%20')}-{game_badge_color}.svg" alt="Game">
  <img src="https://img.shields.io/badge/Branch-{encoded_branch}-green.svg" alt="Branch">
  <img src="https://img.shields.io/badge/AI--assisted-Modding-purple.svg" alt="AI Assisted">
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;•&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a>
</p>

---

# 🇬🇧 English Version

## 📖 Overview
{cfg["desc_en"]}

- **Target Game:** {cfg["game"]}
- **Active Branch:** `{branch}`

## ✨ Key Features
{features_en_md}

## 🚀 Step-by-Step Guide to Run the Mod

### 1. Select the Active Game
Make sure your environment is targeting {cfg["game"]}:
```bash
{cfg["game_task"]}
```

### 2. Binary Compilation
- **Status:** {bin_status_en}
- **Details:** {cfg["binaries_reason_en"]}
```bash
task build-release
```

### 3. Asset Extraction
- **Status:** {ext_status_en}
- **Details:** {cfg["extract_reason_en"]}
```bash
task extract
```

### 4. Launch the Game
Run the game natively:
```bash
task boot-game
```
*(Or launch via the OpenGOAL REPL using `task repl`, then compile and run with `(mi)` and `(r)`).*

## 🎥 Demonstration Video
{video_block_en}

## 📖 Technical Documentation
For the complete technical breakdown, architecture, and developer notes, refer to:
- 📄 [`{cfg["doc_file"]}`]({cfg["doc_file"]})

---

# 🇫🇷 Version Française

## 📖 Présentation du Mod
{cfg["desc_fr"]}

- **Jeu Ciblé :** {cfg["game"]}
- **Branche Active :** `{branch}`

## ✨ Fonctionnalités Clés
{features_fr_md}

## 🚀 Guide Pas à Pas pour Lancer le Mod

### 1. Sélectionner le Jeu Actif
Assurez-vous que l'environnement cible {cfg["game"]} :
```bash
{cfg["game_task"]}
```

### 2. Compilation des Binaires
- **Statut :** {bin_status_fr}
- **Détails :** {cfg["binaries_reason_fr"]}
```bash
task build-release
```

### 3. Extraction des Données (Assets)
- **Statut :** {ext_status_fr}
- **Détails :** {cfg["extract_reason_fr"]}
```bash
task extract
```

### 4. Lancer le Jeu
Lancez le jeu nativement :
```bash
task boot-game
```
*(Ou via le REPL OpenGOAL avec `task repl`, puis `(mi)` et `(r)`).*

## 🎥 Encart Vidéo Démonstrative
{video_block_fr}

## 📖 Documentation Technique
Pour l'audit technique approfondi, l'architecture et les détails d'implémentation, consultez :
- 📄 [`{cfg["doc_file"]}`]({cfg["doc_file"]})

---
*(AI-assisted)*
"""
    return content

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=REPO_ROOT, encoding="utf-8", errors="replace")
    return res

def main():
    print(f"=== Deploying Simplified Mod READMEs to all {len(MODS_CONFIG)} branches ===")
    
    # Ensure working tree clean
    status = run_cmd("git status --porcelain").stdout.strip()
    if status:
        print("Working tree is dirty, please stash or commit first:")
        print(status)
        sys.exit(1)

    for branch, cfg in MODS_CONFIG.items():
        print(f"\n---> Processing branch: {branch}")
        
        # Checkout branch: try local branch if exists, otherwise checkout -B from origin
        local_check = run_cmd(f"git rev-parse --verify {branch}")
        if local_check.returncode == 0:
            res = run_cmd(f"git checkout {branch}")
        else:
            res = run_cmd(f"git checkout -B {branch} origin/{branch}")
        if res.returncode != 0:
            print(f"Error checking out {branch}: {res.stderr}")
            continue

        # Generate README
        readme_path = os.path.join(REPO_ROOT, "README.md")
        content = generate_mod_readme(branch, cfg)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Commit and push
        run_cmd("git add README.md")
        commit_res = run_cmd('git commit -m "docs: simplify technical documentation link in root README (AI-assisted)"')
        if commit_res.returncode == 0:
            print(f"  [OK] Committed new README for {branch}")
            push_res = run_cmd(f"git push origin {branch}")
            if push_res.returncode == 0:
                print(f"  [OK] Pushed {branch} to origin")
            else:
                print(f"  [ERROR] Push failed: {push_res.stderr}")
        else:
            print(f"  [INFO] No changes to commit for {branch}")

    print("\nReturning to master-dev...")
    run_cmd("git checkout master-dev")
    print("All mod branches successfully processed!")

if __name__ == "__main__":
    main()
