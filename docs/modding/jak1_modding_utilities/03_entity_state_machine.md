# Jak 1 — Entity System, Processes & State Machine / Système d'Entités, Process & États

> **Bilingual Knowledge Item / Base de Connaissances Bilingue**
>
> - **Origin / Provenance:** `master`
> - [🇬🇧 English Version](#-english-version)
> - [🇫🇷 Version Française](#-version-française)

---

# 🇬🇧 English Version

## 1. Process Definition Structure
In GOAL, custom interactive actors derive from `process-drawable`:

```lisp
(deftype my-custom-actor (process-drawable)
  ((custom-counter  int32)
   (custom-timer    time-frame))
  (:state-methods
    idle
    active)
  )
```

## 2. State Machine Implementation
A state is declared with `:virtual #t`, event handlers, code loop, and post function:

```lisp
(defstate idle (my-custom-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack)
       (go-virtual active))))
  :code (behavior ()
    (loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))
      ))
  :post ja-post)
```

---

# 🇫🇷 Version Française

## 1. Structure d'un Nouvel Acteur
En GOAL, les entités interactives dérivent généralement de `process-drawable` :

```lisp
(deftype my-custom-actor (process-drawable)
  ((custom-counter  int32)
   (custom-timer    time-frame))
  (:state-methods
    idle
    active)
  )
```

## 2. Définition d'un État
Un état associe des gestionnaires d'événements, une boucle de code et une méthode de rendu :

```lisp
(defstate idle (my-custom-actor)
  :virtual #t
  :event (behavior ((proc process) (argc int) (message symbol) (block event-message-block))
    (case message
      (('touch 'attack)
       (go-virtual active))))
  :code (behavior ()
    (loop
      (ja-no-eval :group! my-actor-idle-ja :num! (seek!) :frame-num 0.0)
      (until (ja-done? 0)
        (suspend)
        (ja :num! (seek!)))
      ))
  :post ja-post)
```
