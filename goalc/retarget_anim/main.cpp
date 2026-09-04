#include "retarget_anim.h"

#include "common/log/log.h"

#include "third-party/CLI11.hpp"

int main(int argc, char** argv) {
  lg::set_stdout_level(lg::level::info);
  lg::set_flush_level(lg::level::info);
  lg::initialize();

  std::string base_str;
  std::string source_str;
  std::string output_str;
  std::vector<std::string> anim_names;
  std::vector<std::string> root_joints = {"align", "main"};
  std::vector<std::string> neutral_scale_joints = {"board"};
  std::string force_180_yaw_anim;

  CLI::App app{"Retarget animations from one skeleton's GLB onto another's, matching joints by "
              "name. See goalc/retarget_anim/retarget_anim.cpp for the full rationale."};
  app.add_option("-b,--base", base_str,
                 "Base GLB: mesh+skeleton the output keeps (e.g. the native jakb-lod0.glb) - its "
                 "skin joint order is preserved exactly in the output")
      ->required();
  app.add_option("-s,--source", source_str,
                 "Source GLB to pull animation curves from (e.g. Jak3's native jakb-lod0.glb)")
      ->required();
  app.add_option("-o,--output", output_str, "Output GLB path")->required();
  app.add_option("-a,--anim", anim_names, "Animation name(s) to retarget (by name in --source)")
      ->required();
  app.add_option("--root-joints", root_joints,
                 "Joint names that get full translation+rotation(+scale) from the source (real "
                 "root motion); default: align main");
  app.add_option("--neutral-scale-joints", neutral_scale_joints,
                 "Joint names forced to constant (1,1,1) scale in the output; default: board");
  app.add_option("--force-180-yaw-anim", force_180_yaw_anim,
                 "If set, the align joint's net yaw over this specific --anim is corrected/"
                 "synthesized to exactly 180 degrees");
  CLI11_PARSE(app, argc, argv);

  retarget_anim::RetargetOptions opts;
  opts.root_joints = root_joints;
  opts.force_neutral_scale_joints = neutral_scale_joints;
  opts.force_180_yaw_align_anim = force_180_yaw_anim;

  retarget_anim::retarget_glb(fs::path(base_str), fs::path(source_str), anim_names,
                              fs::path(output_str), opts);
  return 0;
}
