#pragma once

#include <string>
#include <vector>

#include "common/common_types.h"
#include "common/util/FileUtil.h"

namespace retarget_anim {

// See retarget_anim.cpp's file comment for the full rationale. Short version: `root_joints` get
// full translation+rotation(+scale) copied from the source clip (real root motion, e.g. a
// jump's/turn's overall movement through the world). Every other matched joint gets rotation
// only - translation encodes bone length, which differs between the source and base skeletons, so
// copying it verbatim would stretch the mesh; its own (constant) bind-pose translation/scale is
// kept instead.
struct RetargetOptions {
  std::vector<std::string> root_joints = {"align", "main"};
  // Always forced to constant (1,1,1) scale in the output, regardless of bind pose or source data.
  std::vector<std::string> force_neutral_scale_joints = {"board"};
  // For this exact animation name, the `align` joint's net rotation (last frame relative to
  // first) is corrected/synthesized to be a 180 degree yaw - needed for turn-around's root motion
  // to read as a full about-face regardless of what the source clip's own align channel does.
  std::string force_180_yaw_align_anim;
};

// Retarget `anim_names` from `source_glb` onto `base_glb`'s skeleton (matched by joint name), and
// write the result - base mesh/skin/nodes/materials copied through unchanged, plus the retargeted
// animations - to `output_glb`. Every joint in the base skeleton gets an explicit
// translation+rotation+scale channel in the output (never omitted), so a joint with no source
// counterpart can't collapse to the origin via a missing-channel default.
void retarget_glb(const fs::path& base_glb,
                  const fs::path& source_glb,
                  const std::vector<std::string>& anim_names,
                  const fs::path& output_glb,
                  const RetargetOptions& opts = {});

}  // namespace retarget_anim
