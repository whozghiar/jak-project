# Guard Vehicle Riders & Civilian Alert Suppression / Conducteurs de Véhicules Gardes & Suppression des Alertes Civiles

> - **Origin / Provenance:** `jak2/features/crimson-blueguard/peaceful`
> - **Last Updated / Dernière modification:** `jak2/features/crimson-blueguard/peaceful`

---

# 🇬🇧 English Version

## 1. Context & Core Concepts
In Jak 2's Haven City traffic system:
1. **Guard Vehicles (`vehicle-guard`):** Patrol cruisers spawn an attached rider process (`vehicle-rider`) initialized as `crimson-guard-rider`. The rider uses custom joint masks to sit in the cockpit and plays riding animations (stance 35 for bikes, 36 for cars). If hijacked or shot, the rider gets knocked off, increments the police alert level by 2, and spawns a foot guard to pursue the player.
2. **Civilian Casualties & City Alerts:** When a civilian (`civilian` / `citizen-norm`, `citizen-fat`, etc.) is struck or killed, two alert pathways execute:
   - Immediate Hit: `citizen::general-event-handler` receives `'hit` / `'hit-knocked` and invokes `(trigger-alert this 1 attacker)` -> calls `increase-alert-level`.
   - Lethal Knockdown: `civilian::cleanup-for-death` emits a `traffic-danger` of type `tdt7` with a 30m notification radius. Nearby Crimson Guards receive `'panic` or `'clear-path` with `tdt7`, causing them to immediately trigger a police alert against Jak.

To allow City Peaceful mode to operate with peaceful blue-guard patrols without unwanted alert escalation, this modular utility implements:
- A custom `crimson-blue-guard-rider` entity spawned on `vehicle-guard` cruisers via the modular hook `*mod-city-guard-rider-type-hook*`.
- Clean civilian alert suppression via `*mod-city-citizen-alert-blocked-hook*`, preventing both direct `trigger-alert` calls and `tdt7` danger broadcasts from civilian casualties while preserving normal red-guard alert responses.

---

## 2. Technical Implementation

### Hook Architecture (`traffic-h.gc` & `mod-city-hooks.gc`)
The shared traffic engine files remain agnostic through two forward-declared hooks:
```lisp
;; In engine/ai/traffic-h.gc
(define-extern *mod-city-guard-rider-type-hook* (function type))
(define-extern *mod-city-citizen-alert-blocked-hook* (function citizen symbol))
```

In `mod-city-hooks.gc`:
- Default:
  - `mod-city-hook-guard-rider-type` returns stock `crimson-guard-rider`.
  - `mod-city-hook-citizen-alert-blocked?` returns `#f`.
- City Peaceful:
  - `mod-city-pea-guard-rider-type` returns `crimson-blue-guard-rider` when `*mod-city-peaceful?*` is true.
  - `mod-city-pea-citizen-alert-blocked?` returns `#t` only for non-guards `(and *mod-city-peaceful?* (not (type? this crimson-guard)))`.

### Blue Guard Vehicle Rider (`crimson-blue-guard.gc`)
The `crimson-blue-guard-rider` is defined as a subtype of `crimson-guard-rider`:
- Uses `skel-crimson-blue-guard-rider` referencing `crimson-blue-guard-lod0-jg` and `crimson-blue-guard-lod0-mg`.
- Overrides `active` state event handling: when `'knocked-off` occurs, it sets `id` to 1 (parity selects `crimson-blue-guard`) and omits `increase-alert-level`, allowing the pilot to seamlessly recover on foot without triggering sirens.

### Guard Vehicle Pilot Assignment (`vehicle-guard.gc`)
In `vehicle-guard::vehicle-method-137`:
```lisp
(defmethod vehicle-method-137 ((this vehicle-guard) (arg0 traffic-object-spawn-params))
  (vehicle-rider-spawn this (*mod-city-guard-rider-type-hook*) arg0)
  0
  (none)
  )
```

### Civilian Alert Blocking (`citizen.gc` & `civilian.gc`)
- In `citizen::trigger-alert`: calls to `increase-alert-level` are wrapped with `(when (not (*mod-city-citizen-alert-blocked-hook* this)) ...)`.
- In `civilian::cleanup-for-death`: the `tdt7` traffic danger broadcast is wrapped with `(when (not (*mod-city-citizen-alert-blocked-hook* this)) ...)`.

---

## 3. Concrete Annotated Code Examples

### Pilot Ejection Override (`crimson-blue-guard.gc`)
```lisp
(defbehavior crimson-blue-guard-rider-event-handler crimson-blue-guard-rider ((arg0 process) (arg1 int) (arg2 symbol) (arg3 event-message-block))
  (case arg2
    (('knocked-off)
     (let ((gp-0 (new 'stack 'traffic-object-spawn-params)))
       (let ((v1-1 (find-nearest-nav-mesh (-> self root trans) (the-as float #x7f800000))))
         (set! (-> gp-0 object-type) (traffic-type crimson-guard-1))
         (set! (-> gp-0 behavior) (the-as uint 11))
         (set! (-> gp-0 id) (the-as uint 1)) ;; odd id selects crimson-blue-guard
         (set! (-> gp-0 nav-mesh) v1-1)
         )
       (set! (-> gp-0 nav-branch) #f)
       (set! (-> gp-0 proc) #f)
       (set! (-> gp-0 handle) (process->handle (-> self parent 0)))
       (set! (-> gp-0 user-data) (-> self draw seg-mask))
       (set! (-> gp-0 flags) (traffic-spawn-flags))
       (set! (-> gp-0 guard-type) (the-as uint 7))
       (vector-reset! (-> gp-0 velocity))
       (set! (-> gp-0 position quad) (-> self root trans quad))
       (quaternion-copy! (-> gp-0 rotation) (-> self root quat))
       ;; Blue guard knocked off: do NOT send increase-alert-level, spawn blue guard on foot
       (send-event *traffic-manager* 'activate-object gp-0)
       )
     (logand! (-> self flags) -3)
     (vehicle-rider-method-35 self)
     )
    (else
      (vehicle-rider-event-handler arg0 arg1 arg2 arg3)
      )
    )
  )
```

---

## 4. Known Pitfalls & Edge Cases
- **Guard vs. Civilian Inheritance:** `crimson-guard` inherits from `citizen`. Any hook checking `this` in `citizen.gc` must discriminate between civilians and guards `(not (type? this crimson-guard))`, otherwise red guards would lose their ability to sound the alarm when attacking Jak.
- **`tdt7` Dual Pathway:** Suppressing `trigger-alert` alone is insufficient if a civilian dies; `civilian::cleanup-for-death` broadcasts a `tdt7` danger event which prompts red guards within 30m to raise the alarm themselves. Both sites must be guarded.

---

## 5. Verification Steps
1. Boot Jak 2 with City Peaceful enabled (`Debug ▸ Mods ▸ City Peaceful`).
2. Observe Crimson Guard Zoomers (`vehicle-guard`): pilots must render with blue armor.
3. Hijack or crash a Zoomer: rider must eject as a blue guard on foot without triggering level 2 alert.
4. Kill or run over civilians: alarm must not sound, alert level remains 0.
5. Attack a red guard: alarm must sound normally.

---

# 🇫🇷 Version Française

## 1. Contexte & Concepts Clés
Dans le système de trafic d'Haven City dans Jak 2 :
1. **Véhicules de la garde (`vehicle-guard`) :** Les cruisers de patrouille créent un processus passager (`vehicle-rider`) sous la forme d'un `crimson-guard-rider`. Ce passager configure les masques d'articulation pour s'asseoir dans le cockpit et joue les animations de pilotage (35 pour moto, 36 pour voiture). En cas d'éjection ou de détournement, le niveau d'alerte augmente de 2 et un garde à pied est déployé pour poursuivre Jak.
2. **Victimes civiles & Alertes :** Quand un civil (`civilian` / `citizen-norm`, `citizen-fat`, etc.) est frappé ou tué, deux canaux d'alerte s'activent :
   - Coup direct : `citizen::general-event-handler` reçoit `'hit` / `'hit-knocked` et invoque `(trigger-alert this 1 target)` -> appelle `increase-alert-level`.
   - Mort / Knockdown fatal : `civilian::cleanup-for-death` diffuse un `traffic-danger` de type `tdt7` dans un rayon de 30 m. Les gardes rouges aux alentours reçoivent `'panic` ou `'clear-path` et déclenchent immédiatement l'alerte générale.

Pour permettre au mode City Peaceful de maintenir une ambiance pacifique sans escalade intempestive de la police, cette utilité modulaire implémente :
- Une entité `crimson-blue-guard-rider` pour les véhicules `vehicle-guard`, instanciée via le hook modulaire `*mod-city-guard-rider-type-hook*`.
- La suppression complète des alertes civiles via `*mod-city-citizen-alert-blocked-hook*`, bloquant à la fois `trigger-alert` et l'émission du danger `tdt7`, tout en conservant les alertes normales des gardes rouges.

---

## 2. Implémentation Technique

### Architecture des Hooks (`traffic-h.gc` & `mod-city-hooks.gc`)
Les fichiers moteur restent neutres grâce à deux hooks déclarés en avant :
```lisp
;; Dans engine/ai/traffic-h.gc
(define-extern *mod-city-guard-rider-type-hook* (function type))
(define-extern *mod-city-citizen-alert-blocked-hook* (function citizen symbol))
```

Dans `mod-city-hooks.gc` :
- Par défaut :
  - `mod-city-hook-guard-rider-type` renvoie le type d'origine `crimson-guard-rider`.
  - `mod-city-hook-citizen-alert-blocked?` renvoie `#f`.
- Mode City Peaceful :
  - `mod-city-pea-guard-rider-type` renvoie `crimson-blue-guard-rider` quand `*mod-city-peaceful?*` est actif.
  - `mod-city-pea-citizen-alert-blocked?` renvoie `#t` uniquement pour les civils non-gardes `(and *mod-city-peaceful?* (not (type? this crimson-guard)))`.

### Pilote de Véhicule Garde Bleu (`crimson-blue-guard.gc`)
`crimson-blue-guard-rider` est un sous-type de `crimson-guard-rider` :
- Utilise `skel-crimson-blue-guard-rider` avec les géométries `crimson-blue-guard-lod0-jg` et `crimson-blue-guard-lod0-mg`.
- Surcharge l'événement `'knocked-off'` : attribue un `id` impair (parité sélectionnant `crimson-blue-guard`) et supprime l'appel à `increase-alert-level`.

### Assignation du Pilote dans le Cruiser (`vehicle-guard.gc`)
Dans `vehicle-guard::vehicle-method-137` :
```lisp
(defmethod vehicle-method-137 ((this vehicle-guard) (arg0 traffic-object-spawn-params))
  (vehicle-rider-spawn this (*mod-city-guard-rider-type-hook*) arg0)
  0
  (none)
  )
```

### Neutralisation de l'Alerte Civile (`citizen.gc` & `civilian.gc`)
- Dans `citizen::trigger-alert` : l'appel à `increase-alert-level` est conditionné par `(when (not (*mod-city-citizen-alert-blocked-hook* this)) ...)`.
- Dans `civilian::cleanup-for-death` : l'émission du danger `tdt7` est conditionnée par `(when (not (*mod-city-citizen-alert-blocked-hook* this)) ...)`.

---

## 3. Pièges Connus & Cas Particuliers
- **Héritage Gardes / Citoyens :** `crimson-guard` hérite de `citizen`. Tout hook filtrant dans `citizen.gc` doit impérativement distinguer civils et gardes `(not (type? this crimson-guard))`, sous peine de rendre les gardes rouges incapables de sonner l'alarme contre Jak.
- **Double Déclenchement de l'Alerte :** Bloquer `trigger-alert` ne suffit pas lors de la mort d'un civil, car `civilian::cleanup-for-death` émet un événement `tdt7` qui fait réagir les gardes rouges à 30 m à la ronde. Les deux points doivent être verrouillés ensemble.

---

## 4. Étapes de Vérification
1. Démarrer Jak 2 avec City Peaceful activé (`Debug ▸ Mods ▸ City Peaceful`).
2. Observer les patrouilles en Zoomer (`vehicle-guard`) : les pilotes doivent porter l'armure bleue.
3. Éjecter un pilote en percutant ou volant le véhicule : le pilote réapparaît à pied en garde bleu sans alerte.
4. Tuer ou écraser des civils : aucune alarme ne retentit, le niveau d'alerte reste à 0.
5. Attaquer un garde rouge : l'alarme retentit normalement.
