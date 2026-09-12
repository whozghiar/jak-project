("LWIDEB.DGO"
 ("tpage-2972.go"
  "grunt-ag.go"
  "citizen-norm-ag.go"
  "crimson-guard-ag.go"
  "predator-ag.go"
  "flitter-ag.go"
  "cara-ag.go"
  "citizen-norm-rider-ag.go"
  "crimson-bike-ag.go"
  "bikea-ag.go"
  ;; MOD haven-city-chaos -- extra metal-head species injected into the invasion city.
  ;; Circuit 1 (skeletons + animations) is these .go files; circuit 2 (merc geometry +
  ;; textures) is baked into lwideb.fr3 by `extra_art_groups_by_dgo` in
  ;; decompiler/config/jak2/jak2_config.jsonc. Both are required -- with only circuit 1 the
  ;; models run and make noise but never draw.
  ;; Texture pages come from each art group's home level so the texture ids resolve:
  ;;   tpage-1607 = atollext-vis-pris  -> juicer, spyder   (home ATE.DGO)
  ;;   tpage-1721 = mtnext-vis-pris    -> centurion, hopper (home MTX.DGO)
  "tpage-1607.go"
  "tpage-1721.go"
  "juicer-ag.go"
  "spyder-ag.go"
  "centurion-ag.go"
  "hopper-ag.go"
  ;; MOD jetpack-crimsonguard -- flying Krimzon Guard art. Added to all three ambient-population
  ;; levels so a district transition never leaves a dispatched guard without a skeleton.
  ;; tpage-3192 = forresca-vis-pris, the hover guard's home texture page (FRA.DGO).
  "tpage-3192.go"
  "crimson-guard-hover-ag.go"
  "lwideb.go"
 ))
