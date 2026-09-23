("WWD.DGO"
 ("target-ladder.o"
  "ladder.o"
  "jak-ladder+0-ag.go"
  "flut-part.o"
  "flut.o"
  "target-flut.o"
  "jak-flut+0-ag.go"
  "nav-graph-h.o"
  "cty-borrow-manager-h.o"
  "cty-faction-h.o"
  "traffic-engine-h.o"
  "height-map-h.o"
  "vehicle-control.o"
  "nav-graph.o"
  "mission-squad-control-h.o"
  "citizen-h.o"
  "squad-control-city-h.o"
  "squad-control-city.o"
  "kg-squad-control-h.o"
  "ff-squad-control-h.o"
  "mh-squad-control-h.o"
  "cty-faction.o"
  "formations.o"
  "formation-object.o"
  "ctywide-obs-h.o"
  "mission-squad-control.o"
  "cty-attack-controller.o"
  "flee-info.o"
  "citizen.o"
  "civilian.o"
  "guard-h.o"
  "traffic-util.o"
  "traffic-engine.o"
  "traffic-manager.o"
  ;; [MOD: Spargus Invasion] behaviour code of the Haven City units the mod brings into Spargus,
  ;; normally CWI-only (metalhead-grunt/-predator normally ship in CTYPESB). Order mirrors cwi.gd /
  ;; ctypesb.gd so the runtime link order stays identical.
  "cty-guard-projectile.o"
  "citizen-enemy.o"
  "mh-squad-member-h.o"
  "guard.o"
  "guard-grenade.o"
  "guard-tazer.o"
  "guard-rifle.o"
  "guard-states.o"
  "citizen-norm.o"
  "citizen-fat.o"
  "citizen-chick.o"
  "mh-squad-member.o"
  "metalhead-flitter.o"
  "metalhead-grunt.o"
  "metalhead-predator.o"
  "ff-squad-control.o"
  "mh-squad-control.o"
  "ctymark-obs-h.o"
  "ctymark-obs.o"
  "wasteland-scenes.o"
  "wlander-h.o"
  "wlander-male.o"
  "wlander-female.o"
  ;; [MOD: Spargus Invasion] must follow every unit above and precede waswide-init.o, which calls it.
  "mod-spargus-invasion.o"
  "waswide-init.o"
  "waswide-part.o"
  "waswide-obs.o"
  "wascity-ocean.o"
  "tizard.o"
  "dogat.o"
  "tpage-873.go"
  "tpage-874.go"
  "tpage-1956.go"
  "tpage-1075.go"
  "tpage-666.go"
  "tpage-1254.go"
  ;; [MOD: Spargus Invasion] unit texture pages: ctypesa-pris (FL guard), ctypesb-pris (grunt,
  ;; flitter), ctypepa-pris (civilians), ctypepb-pris (predator).
  "tpage-957.go"
  "tpage-1758.go"
  "tpage-956.go"
  "tpage-958.go"
  ;; [MOD: Spargus Invasion] ART-GROUP ORDER IS LOAD-BEARING -- keep this block sorted by
  ;; decreasing object size. After the first art group logs in (joint.gc, art-group::relocate) the
  ;; level switches to 'tiny-edge load buffers, and `load-buffer-resize` shrinks each of the two DGO
  ;; buffers to (size of the object it just held + 2 KB). The object loaded two slots later lands in
  ;; that shrunken buffer, so any art group bigger than the one two positions before it overflows
  ;; into the next object's header ("dgo file header ... has overrun heap", then a klink
  ;; 'version == 5' assert). That is why the DGO load buffer size never mattered. Retail WWD is
  ;; sorted this way; sizes below are from the built WWD.DGO.
  ;; The unit merc geometry is baked into waswide.fr3 by "extra_art_groups_by_dgo" in
  ;; decompiler/config/jak3/jak3_config.jsonc -- `task extract` is REQUIRED, (mi) will not
  ;; regenerate a .fr3.
  "crimson-guard-ag.go"          ;; 288976  [MOD] FL guard (home ctypesa)
  "citizen-fat-ag.go"            ;; 245568  [MOD] Haven civilian (home ctypepa)
  "citizen-norm-ag.go"           ;; 236544  [MOD] Haven civilian (home ctypepa)
  "wlander-male-ag.go"           ;; 227712
  "wlander-female-ag.go"         ;; 221504
  "citizen-chick-ag.go"          ;; 198400  [MOD] Haven civilian (home ctypepa)
  "predator-ag.go"               ;; 188160  [MOD] Metal Head predator (home ctypepb)
  "city-grunt-ag.go"             ;; 124816  [MOD] Metal Head grunt (home ctypesb)
  "city-flitter-ag.go"           ;; 106112  [MOD] Metal Head flitter (home ctypesb)
  "flut-saddle-ag.go"            ;;  65728
  "wascity-cactus-ag.go"         ;;  42752
  "des-burning-bush-ag.go"       ;;  16592
  "wascity-windmill-ag.go"       ;;  10592
  "wascity-flag-b-ag.go"         ;;  10096
  "wascity-flag-d-ag.go"         ;;   9904
  "wascity-awning-a-ag.go"       ;;   8880
  "wascity-burning-bush-ag.go"   ;;   8000
  "wascity-flag-c-ag.go"         ;;   7872
  "wascity-flag-a-ag.go"         ;;   7808
  "wascity-wind-fan-ag.go"       ;;   5488
  "waswide-vis.go"
 ))
