# Jak 2 — Jetboard State Handling & Particle Tracking / Gestion des États Jetboard & Particules

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `jak2/features/jak3-jetBoard`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## Jetboard State Handling (`target-board-exit` Whitelist & Heading Inversion)

### ⚠️ The `target-board-exit` Whitelist Pitfall (The Mini-Jetboard Bug)
In Jak 2, the jetboard (`board-lod0`) is a standalone actor process (`board.gc`) anchored to `node-list data 25` with two distinct visual states:
1. **`use` (`board-open-ja`):** Fins, wings, and tips deployed in full snowboard/surfboard shape.
2. **`idle` (`board-close-ja`):** Fully retracted into its center dome (a small round disc for Jak's back).

- The `target-board-exit` function (`target-board.gc:882`) contains a **hardcoded whitelist** of valid board states.
- When creating a new board state (e.g. `target-board-turn-around`), **it MUST be added to the whitelist** in `target-board-exit`, `target-board-pre-move`, and `target-board-real-post`.
- **Symptom if omitted:** Upon entering the new state, the engine assumes Jak is dismounting, clears `(focus-status board)`, and the `board` actor instantly drops to `idle` / `board-close-ja` (the board shrinks into a mini-puck under Jak's boots).

### Autonomous Rotation & Pad Steering Lockout (`turn-lockout-end-time`)
During autonomous animation-driven turns, `target-board-real-post` continuously executes `read-pad` and calls `turn-to-vector` (or `rot->dir-targ!` on neutral stick), which can overwrite `dir-targ` every frame with the player's stick input or reset it to the previous facing quaternion.
- **Fix:** Set `(set! (-> self control turn-lockout-end-time) (+ (current-time) (seconds 1.5)))` in `:enter` (and reset to 0 in `:exit`), ensuring standard stick steering is suppressed until the turnaround completes.
- **Entry Momentum:** Calculate entry velocity using `(fmax (-> self control ctrl-xz-vel) (vector-length (vector-flatten! (new-stack-vector0) (-> self control transv) (-> self control dynam gravity-normal))) 40960.0)` so momentum is preserved even if the player was drifting or gliding without forward stick input.

### Heading Inversion, Boost & Forward Momentum on State Exit
To guarantee a complete autonomous heading change (e.g. 180° turnaround) and reward the player:
1. `(quaternion-copy! (-> self control quat-for-control) (-> self control dir-targ))`: Inverts the control quaternion.
2. `(set-quaternion! (-> self control) (-> self control dir-targ))`: Inverts root-transform orientation.
3. `(vector-z-quaternion! (-> self control transv) (-> self control dir-targ))` & `(vector-float*! (-> self control transv) ... f30-1)`: Re-aligns world velocity in the reversed heading with acceleration boost (`(fmax (+ f30-0 20480.0) 114688.0)`).
4. `(set-forward-vel f30-1)` & `(set! (-> self control ctrl-xz-vel) f30-1)`: Passes scalar forward velocity.
5. `(sound-play "board-boost")`, `(cpad-set-buzz!)`, and `part-tracker-spawn group-board-land-straight`: Plays audio, rumble, and landing dust VFX matching native spin-trick rewards.

### Dynamic Joint Tracking, Particle Ripples & Collision Spheres (`board-zap-track`)
For area-of-effect attacks while riding (e.g. `board-zap`):
- **Dynamic Tracking:** Sparticle callbacks (`(:func 'board-zap-track)`) should query `*target*` directly and copy the board joint translation `(joint-node-index jakb-lod0-jg board)` into `(-> arg2 x/y/z)`. In parallel, `part-tracker-spawn` should pass `:callback part-tracker-track-target`. This ensures all particles and the tracker process follow the moving board in real time at high velocity.
- **Concentric Multi-Ring Ripple:** Replicating Jak 3's `group-board-zap-attack` (`:num 0.25`, `:length (seconds 0.335)`, `:scalevel-x (meters 0.16666667)`) emits 4 to 5 concentric ripples expanding up to $3.0\text{ m}$.
- **Damage Radius Alignment:** Configure the attack collision sphere in `target-util.gc` (`sphere<-vector+r!`) to $12288.0$ ($3.0\text{ m}$) with root bounding sphere $13107.2$ ($3.2\text{ m}$), matching native Jak 3 values exactly.
- **Suppression of Trick FX on Hit:** In `target-board.gc` (`'touched` event handler), guard `(process-spawn part-tracker :init part-tracker-init group-board-spin-attack ...)` with `(if (!= (-> self control danger-mode) 'board-zap) ...)` to prevent native spin-trick flashes during zap attacks.

---

# 🇫🇷 Version Française

## Gestion des États Jetboard (`target-board-exit` Whitelist & Orientation)

### ⚠️ Le Piège de la Whitelist `target-board-exit` (Le Bug du Mini-Jetboard)
Dans Jak 2, le jetboard (`board-lod0`) est un processus acteur autonome (`board.gc`) attaché à `node-list data 25` avec deux états visuels distincts :
1. **`use` (`board-open-ja`) :** Ailerons, pointes et spoilers déployés en grand skate/snowboard.
2. **`idle` (`board-close-ja`) :** Rétracté entièrement dans son dôme central (disque compact fixé au dos de Jak).

- La fonction `target-board-exit` (`target-board.gc:882`) possède une **liste blanche codée en dur** des états de jetboard valides.
- Lors de l'ajout d'un nouvel état de jetboard (ex: `target-board-turn-around`), **il DOIT être ajouté à la liste blanche** de `target-board-exit`, `target-board-pre-move` et `target-board-real-post`.
- **Symptôme si omis :** Dès l'entrée dans le nouvel état, le moteur croit que Jak descend du skate, efface `(focus-status board)`, et l'acteur `board` bascule instantanément en `idle` / `board-close-ja` (la planche se rétracte en mini-rondelle sous les pieds de Jak).

### Rotation Autonome & Verrouillage du Pilotage Stick (`turn-lockout-end-time`)
Lors d'un demi-tour piloté par animation, `target-board-real-post` exécute continuellement `read-pad` et appelle `turn-to-vector` (ou `rot->dir-targ!` si stick neutre), écrasant `dir-targ` à chaque frame avec l'orientation du joystick ou le réinitialisant sur l'ancien cap.
- **Correctif :** Définir `(set! (-> self control turn-lockout-end-time) (+ (current-time) (seconds 1.5)))` dans `:enter` (et remettre à 0 dans `:exit`), supprimant toute interférence du joystick pendant le demi-tour.
- **Conservation de vitesse d'entrée :** Calculer la vitesse initiale via `(fmax (-> self control ctrl-xz-vel) (vector-length (vector-flatten! (new-stack-vector0) (-> self control transv) (-> self control dynam gravity-normal))) 40960.0)` pour conserver l'élan même si Jak glissait ou dérivait sans pousser le stick vers l'avant.

### Inversion de Cap, Boost & Maintien de Vélocité à la Sortie
Pour garantir un changement de cap complet (demi-tour à 180°) et gratifier le joueur :
1. `(quaternion-copy! (-> self control quat-for-control) (-> self control dir-targ))` : Inverse le quaternion de contrôle.
2. `(set-quaternion! (-> self control) (-> self control dir-targ))` : Inverse l'orientation du root-transform.
3. `(vector-z-quaternion! (-> self control transv) (-> self control dir-targ))` & `(vector-float*! (-> self control transv) ... f30-1)` : Aligne la vélocité monde dans la nouvelle direction avec boost d'accélération (`(fmax (+ f30-0 20480.0) 114688.0)`).
4. `(set-forward-vel f30-1)` & `(set! (-> self control ctrl-xz-vel) f30-1)` : Transmet la vitesse scalaire vers l'avant.
5. `(sound-play "board-boost")`, `(cpad-set-buzz!)`, et `part-tracker-spawn group-board-land-straight` : Déclenche le son de boost, la vibration manette et les particules de poussière au sol (identiques aux figures réussies).

### Suivi Dynamique de Joint, Ondes Particulaires & Sphères de Collision (`board-zap-track`)
Pour les attaques de zone en déplacement (ex: `board-zap`) :
- **Suivi Dynamique :** Les callbacks de sparticles (`(:func 'board-zap-track)`) doivent interroger `*target*` directement et recopier la translation du joint du skate `(joint-node-index jakb-lod0-jg board)` dans `(-> arg2 x/y/z)`. En parallèle, `part-tracker-spawn` doit recevoir `:callback part-tracker-track-target`. Les particules et le processus tracker accompagnent ainsi la planche en temps réel même à haute vitesse.
- **Ondes Concentriques Multi-Anneaux :** La réplication de `group-board-zap-attack` de Jak 3 (`:num 0.25`, `:length (seconds 0.335)`, `:scalevel-x (meters 0.16666667)`) émet 4 à 5 anneaux concentriques successifs s'étendant jusqu'à $3.0\text{ m}$.
- **Alignement du Rayon de Dégâts :** Configurer la sphère de collision d'attaque dans `target-util.gc` (`sphere<-vector+r!`) à $12288.0$ ($3.0\text{ m}$) avec une sphère racine englobante de $13107.2$ ($3.2\text{ m}$), calquées à l'identique sur les constantes de Jak 3.
- **Suppression de l'Effet de Spin à l'Impact :** Dans `target-board.gc` (gestionnaire d'événement `'touched`), protéger le spawn de `group-board-spin-attack` avec `(if (!= (-> self control danger-mode) 'board-zap) ...)` pour empêcher le déclenchement de l'effet visuel de figure/spin bleu lors des attaques zap.
