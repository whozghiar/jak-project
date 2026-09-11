---
name: goal-lisp
description: Comprehensive guide to OpenGOAL LISP syntax, typing system, processes, behaviors, virtual states, macros, and common language traps.
---

# GOAL Lisp & Syntax — Engineering Reference

OpenGOAL is an x86-64 native port and extension of GOAL (Game Oriented Assembly Lisp), the proprietary compiled LISP dialect created by Naughty Dog for the Jak & Daxter series. This skill provides the syntax, type system, process model, state machine semantics, and common traps required to author robust `.gc` code.

---

## 1. Syntax Basics & Lexical Conventions

- **Comments:** Single-line comments start with semicolons (`;;`). Block comments use `#| ... |#`.
- **Booleans:** `#t` (true) and `#f` (false). Note: In GOAL, anything other than `#f` evaluates as truthy.
- **Symbols & Keywords:**
  - Symbols: `'my-symbol` or unquoted identifier `my-symbol`.
  - Keywords: Colon-prefixed tokens `:enter`, `:event`, `:inline`, `:virtual`.
- **Numeric Units & Literals:**
  - Floating point literals must have decimal points (e.g. `1.0`, `0.0`).
  - Distance unit: `(meters 4.0)` converts meters to PS2 internal world units (1 meter = 4096.0 internal units).
  - Angle unit: `(degrees 90.0)` converts degrees to binary angles/rotations.
  - Time unit: `(seconds 2.5)` converts game seconds to TICKS (typically based on 60 FPS / 300 ticks/sec).

```lisp
;; Example unit conversions
(let ((dist (meters 5.0))
      (angle (degrees 180.0))
      (duration (seconds 1.0)))
  (format #t "Dist: ~M, Angle: ~R, Ticks: ~D~%" dist angle duration))
```

---

## 2. Type System & Struct Alignment

GOAL has a strongly typed, object-oriented system with single inheritance.

### Type Hierarchy
- `object`: Root of all types.
  - `structure`: Unboxed by default. When stored in another struct without `:inline #t`, it is stored as a 4-byte pointer. With `:inline #t`, it is embedded directly.
    - `basic`: Boxed object. Always has a runtime `type` tag at offset -4 (or 0). Can be checked dynamically via `type-type?`.
      - `process`: Base class for concurrent kernel threads/actors.
        - `process-drawable`: Base class for any 3D entity with a position, skeleton, bounding box, and drawing components.

### Defining Types (`deftype`)

```lisp
(deftype my-actor (process-drawable)
  ((speed              meters)
   (turn-rate          degrees)
   (charge-timer       time-frame)
   (active?            symbol)
   (target-pos         vector :inline)     ;; Embedded 16-byte vector directly inside my-actor
   (custom-substruct   my-struct :inline)  ;; Inline structure
   (other-actor        my-actor)           ;; Reference/pointer to another actor (not inline)
   )
  (:methods
    (my-actor-method-1 (_type_ int) symbol)
    (my-actor-method-2 (_type_ vector) none)
    )
  (:states
    my-actor-idle
    (my-actor-move meters)
    my-actor-die
    )
  )
```

### Alignment & Sizing Rules
- Vectors (`vector`, `matrix`) are 128-bit (16-byte) aligned.
- Structures containing `:inline` vectors or 128-bit fields will be padded to 16 bytes.
- Misaligned fields can cause memory corruption or CPU exceptions. Check decompiled definitions in `goal_src/jak[x]/` for field layout references.

---

## 3. Processes, Behaviors & `self`

### Behaviors (`defbehavior`)
A behavior is a function that runs in the execution context of a specific process type. Inside a behavior, `self` is statically typed to that process:

```lisp
(defbehavior my-actor-init-by-other my-actor ((init-pos vector))
  ;; self is known to be of type 'my-actor' here
  (set! (-> self root) (new 'process 'trsqv))
  (vector-copy! (-> self root trans) init-pos)
  (set! (-> self speed) (meters 2.0))
  (go-virtual my-actor-idle)
  )
```

---

## 4. Virtual States & State Machine (`defstate`)

Processes in OpenGOAL execute finite state machines. Each state can implement the following lifecycle hooks:
- `:enter` — Run once when entering the state (before the first `:trans` or `:code`).
- `:trans` — Executed every frame before process physics/collision.
- `:code` — Main coroutine loop. Can call `(suspend)`, `(sleep-code)`, or animation loops.
- `:post` — Executed every frame after physics/collision; usually handles animation evaluation (`ja-post`) or collision transforms (`transform-post`).
- `:event` — Event message handler triggered asynchronously by other processes via `send-event`.
- `:exit` — Executed once upon leaving the state (even if aborted by an external `go`).

### State Definition Example

```lisp
(defstate my-actor-idle (my-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('trigger)
       (format #t "Triggered by ~A!~%" proc)
       (go-virtual my-actor-move (meters 5.0)))
      (('touch 'attack)
       (format #t "Hit!~%")
       #t)
      )
    )
  :enter (behavior ()
    (set-time! (-> self charge-timer))
    (set! (-> self active?) #t)
    )
  :trans (behavior ()
    ;; Runs every frame
    (if (time-elapsed? (-> self charge-timer) (seconds 3.0))
        (go-virtual my-actor-move (meters 1.0)))
    )
  :code (behavior ()
    (loop
      ;; Play an animation loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!))
        )
      )
    )
  :post (behavior ()
    (transform-post)
    )
  )
```

### State Transitions
- `(go my-actor-idle)`: Transition to a static state.
- `(go-virtual my-actor-idle)`: Transition to a virtual state defined on the actor's type hierarchy.
- Passing arguments to states: `(go-virtual my-actor-move (meters 5.0))`. The target state's hooks receive arguments matching its signature.

---

## 5. Coroutine Control: `suspend`, `sleep-code`, `wait-for`

The GOAL kernel provides non-preemptive green threading for processes:
- `(suspend)`: Yield execution until the next frame. Execution resumes at the exact point after `(suspend)` on the next engine cycle.
- `(sleep-code)`: Suspends indefinitely. Useful when an actor is static or driven entirely by `:trans` or `:event`.
- Animation seek loop pattern:
  ```lisp
  (ja-no-eval :group! my-anim-ja :num! (seek!) :frame-num 0.0)
  (until (ja-done? 0)
    (suspend)
    (ja :num! (seek!))
    )
  ```

---

## 6. Macros & Conditionals

- `(when condition ...)`: Executes body if condition is true.
- `(unless condition ...)`: Executes body if condition is false.
- `(cond (c1 e1) (c2 e2) (else e3))`: Multi-branch conditional.
- `(case val ((val1) e1) ((val2 val3) e2) (else e3))`: Equality switch-case.
- `(defmacro name (args...) body...)`: Compile-time macro expansion.

---

## 7. Crucial Traps & Gotchas in GOAL

1. **Floating Point Equality:**
   - **NEVER** compare floats with `(= f1 f2)`. Slight precision inaccuracies will fail equality.
   - Use `(< (abs (- f1 f2)) 0.001)` or integer/unit approximations.
2. **`basic` vs `structure` Allocation:**
   - A `basic` always has a runtime type tag and can be passed generically.
   - A `structure` has **no runtime type tag**. The compiler must know its type at compile time.
3. **Ghost Memory in REPL:**
   - Changing a `deftype` field layout in an active game session without restarting the game will corrupt RAM because existing allocated processes retain the old struct layout. Always test struct changes with a clean cold boot (`task boot-game`).
4. **Virtual Method ID Limits:**
   - Methods must be declared in `:methods` before being defined with `defmethod`. Never reorder or remove methods on existing engine classes as it shifts the vtable indices for the entire engine.
5. **Memory Heap Selection:**
   - Allocating transient actor data on `'global` leaks memory permanently across level loads. Use the process heap (`'process`) or level heap (`'level`) for gameplay instances.
