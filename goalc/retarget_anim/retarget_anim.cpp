// Cross-skeleton animation retargeter.
//
// Problem this solves: we want 2 Jak3 board animations (jakb-board-jump-high,
// jakb-board-turn-around) playable on Jak2's native jakb-ag skeleton. Jak2 and Jak3 share the same
// joint *names* for the first ~15 joints but diverge in index/order after that, and - more
// importantly for retargeting - the two rigs don't have identical bone lengths. build-actor's
// process_anim() maps an imported GLB's animation channels onto the target art-group purely
// positionally (by the imported GLB's own skin joint order, see
// goalc/build_actor/common/build_actor.cpp), so the *base* skeleton this tool starts from must be
// Jak2's real native one (jakb-lod0.glb / daxter-lod0.glb, as produced by this project's own
// extraction pipeline) - not a hand-built one.
//
// Retargeting rule (ground-truthed against a real native Jak2 board animation before writing this,
// see docs/backport-analysis.md and the planning notes for this branch): every real joint carries
// translation+rotation+scale, but only `root_joints` (align, main) use that translation for actual
// root motion. For every other joint, translation encodes bone length - copying Jak3's translation
// onto Jak2's differently-proportioned rig would stretch it - so only *rotation* (bone-length
// independent) is retargeted; translation/scale come from the base skeleton's own bind pose.
//
// This intentionally reuses only generic, already-proven pieces of this project (tiny_gltf,
// common/util/gltf_util's accessor readers) rather than hand-editing GLTF JSON/binary, which is
// the documented suspected cause of an earlier crash in this exact mod (docs/backport-analysis.md).
#include "retarget_anim.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <optional>

#include "common/log/log.h"
#include "common/util/Assert.h"
#include "common/util/gltf_util.h"

#include "fmt/format.h"
#include "third-party/tiny_gltf/tiny_gltf.h"

namespace retarget_anim {

namespace {

constexpr float kPi = 3.14159265358979323846f;

tinygltf::Model load_glb(const fs::path& path) {
  tinygltf::TinyGLTF loader;
  tinygltf::Model model;
  std::string err, warn;
  bool ok = loader.LoadBinaryFromFile(&model, &err, &warn, path.string());
  if (!warn.empty()) {
    lg::warn("[retarget_anim] {}: {}", path.string(), warn);
  }
  if (!err.empty()) {
    lg::die("[retarget_anim] failed to load {}: {}", path.string(), err);
  }
  ASSERT_MSG(ok, fmt::format("failed to load {}", path.string()).c_str());
  return model;
}

// One skeleton's joints, in skin-joint-index order (this order is exactly what ends up in the
// output's animated joint arrays, and for the base skeleton it must match the master art-group's
// native order - guaranteed by loading the real native GLB rather than building one by hand).
struct SkeletonJoints {
  std::vector<std::string> names;            // joint index -> name
  std::map<std::string, int> name_to_joint;  // name -> joint index
  std::vector<int> node_of_joint;            // joint index -> gltf node index
  std::map<int, int> node_to_joint;          // gltf node index -> joint index
};

SkeletonJoints get_skeleton(const tinygltf::Model& model) {
  auto all_nodes = gltf_util::flatten_nodes_from_all_scenes(model);
  auto skin_idx = gltf_util::find_single_skin(model, all_nodes);
  ASSERT_MSG(skin_idx.has_value(), "model has no skin");
  const auto& skin = model.skins.at(*skin_idx);

  SkeletonJoints result;
  for (size_t i = 0; i < skin.joints.size(); i++) {
    int node_idx = skin.joints[i];
    const auto& name = model.nodes.at(node_idx).name;
    result.names.push_back(name);
    result.name_to_joint[name] = (int)i;
    result.node_of_joint.push_back(node_idx);
    result.node_to_joint[node_idx] = (int)i;
  }
  return result;
}

// Same logic as the file-local helper of the same name in common/util/gltf_util.cpp (not exported
// via gltf_util.h, so reimplemented here rather than modifying a shared header for this tool's
// benefit).
math::Matrix4f matrix_from_node(const tinygltf::Node& node) {
  if (!node.matrix.empty()) {
    math::Matrix4f result;
    for (int i = 0; i < 16; i++) {
      result.data()[i] = (float)node.matrix[i];
    }
    return result;
  }
  math::Vector3f t = node.translation.empty()
                         ? math::Vector3f{0, 0, 0}
                         : math::Vector3f{(float)node.translation[0], (float)node.translation[1],
                                          (float)node.translation[2]};
  math::Vector4f r = node.rotation.empty()
                          ? math::Vector4f{0, 0, 0, 1}
                          : math::Vector4f{(float)node.rotation[0], (float)node.rotation[1],
                                           (float)node.rotation[2], (float)node.rotation[3]};
  math::Vector3f s = node.scale.empty() ? math::Vector3f{1, 1, 1}
                                        : math::Vector3f{(float)node.scale[0],
                                                          (float)node.scale[1],
                                                          (float)node.scale[2]};
  return gltf_util::matrix_from_trs(t, r, s);
}

// Inverse of gltf_util's affine_rot_qxyzw (Shepperd's method) - standard, well-known formula for
// this exact matrix layout (row, col), xyzw quaternion order, translation in column 3.
math::Vector4f quat_from_rotation_matrix(float r00,
                                         float r01,
                                         float r02,
                                         float r10,
                                         float r11,
                                         float r12,
                                         float r20,
                                         float r21,
                                         float r22) {
  float x, y, z, w;
  const float trace = r00 + r11 + r22;
  if (trace > 0.f) {
    float s = 0.5f / std::sqrt(trace + 1.0f);
    w = 0.25f / s;
    x = (r21 - r12) * s;
    y = (r02 - r20) * s;
    z = (r10 - r01) * s;
  } else if (r00 > r11 && r00 > r22) {
    float s = 2.0f * std::sqrt(1.0f + r00 - r11 - r22);
    w = (r21 - r12) / s;
    x = 0.25f * s;
    y = (r01 + r10) / s;
    z = (r02 + r20) / s;
  } else if (r11 > r22) {
    float s = 2.0f * std::sqrt(1.0f + r11 - r00 - r22);
    w = (r02 - r20) / s;
    x = (r01 + r10) / s;
    y = 0.25f * s;
    z = (r12 + r21) / s;
  } else {
    float s = 2.0f * std::sqrt(1.0f + r22 - r00 - r11);
    w = (r10 - r01) / s;
    x = (r02 + r20) / s;
    y = (r12 + r21) / s;
    z = 0.25f * s;
  }
  math::Vector4f q{x, y, z, w};
  return q * (1.0f / std::sqrt(q.dot(q)));
}

void decompose_matrix(const math::Matrix4f& m,
                     math::Vector3f* trans_out,
                     math::Vector4f* quat_out,
                     math::Vector3f* scale_out) {
  *trans_out = math::Vector3f{m(0, 3), m(1, 3), m(2, 3)};

  const float sx = std::sqrt(m(0, 0) * m(0, 0) + m(1, 0) * m(1, 0) + m(2, 0) * m(2, 0));
  const float sy = std::sqrt(m(0, 1) * m(0, 1) + m(1, 1) * m(1, 1) + m(2, 1) * m(2, 1));
  const float sz = std::sqrt(m(0, 2) * m(0, 2) + m(1, 2) * m(1, 2) + m(2, 2) * m(2, 2));
  *scale_out = math::Vector3f{sx, sy, sz};

  const float r00 = m(0, 0) / sx, r10 = m(1, 0) / sx, r20 = m(2, 0) / sx;
  const float r01 = m(0, 1) / sy, r11 = m(1, 1) / sy, r21 = m(2, 1) / sy;
  const float r02 = m(0, 2) / sz, r12 = m(1, 2) / sz, r22 = m(2, 2) / sz;
  *quat_out = quat_from_rotation_matrix(r00, r01, r02, r10, r11, r12, r20, r21, r22);
}

math::Vector4f quat_multiply(const math::Vector4f& a, const math::Vector4f& b) {
  return math::Vector4f{a.w() * b.x() + a.x() * b.w() + a.y() * b.z() - a.z() * b.y(),
                        a.w() * b.y() - a.x() * b.z() + a.y() * b.w() + a.z() * b.x(),
                        a.w() * b.z() + a.x() * b.y() - a.y() * b.x() + a.z() * b.w(),
                        a.w() * b.w() - a.x() * b.x() - a.y() * b.y() - a.z() * b.z()};
}

math::Vector4f quat_conjugate(const math::Vector4f& q) {
  return math::Vector4f{-q.x(), -q.y(), -q.z(), q.w()};
}

math::Vector4f quat_from_y_angle(float radians) {
  return math::Vector4f{0, std::sin(radians * 0.5f), 0, std::cos(radians * 0.5f)};
}

// Approximate signed rotation angle around Y encoded by a quaternion. Exact for a pure Y rotation;
// a reasonable approximation otherwise (board turning is overwhelmingly a Y-axis motion). Matches
// quat_from_y_angle's convention (angle = 2*atan2(y, w)).
float quat_y_angle(const math::Vector4f& q) {
  return 2.0f * std::atan2(q.y(), q.w());
}

// One retargeted channel's raw values, always at `times` (shared per-animation, see
// build_output_animation). is_quat controls whether values are 4-wide (xyzw) or 3-wide (xyz).
struct Curve {
  bool is_quat = false;
  std::vector<float> flat_values;  // times.size() * (is_quat ? 4 : 3) floats
};

Curve constant_curve(size_t num_frames, const math::Vector3f& v) {
  Curve c;
  c.is_quat = false;
  c.flat_values.reserve(num_frames * 3);
  for (size_t i = 0; i < num_frames; i++) {
    c.flat_values.push_back(v.x());
    c.flat_values.push_back(v.y());
    c.flat_values.push_back(v.z());
  }
  return c;
}

Curve constant_curve(size_t num_frames, const math::Vector4f& v) {
  Curve c;
  c.is_quat = true;
  c.flat_values.reserve(num_frames * 4);
  for (size_t i = 0; i < num_frames; i++) {
    c.flat_values.push_back(v.x());
    c.flat_values.push_back(v.y());
    c.flat_values.push_back(v.z());
    c.flat_values.push_back(v.w());
  }
  return c;
}

// A source channel resampled so it has exactly one value per entry of `times` (nearest-previous-
// keyframe hold - the source and target animations run at the same authored framerate in
// practice, see build-actor's :framerate 60 on both the master art-groups and this tool's
// callers, so this is a hold, not a real resample).
Curve resample_to_times(const std::vector<float>& src_times,
                       const std::vector<float>& src_values,
                       int value_dim,
                       const std::vector<float>& times) {
  Curve c;
  c.is_quat = value_dim == 4;
  c.flat_values.reserve(times.size() * value_dim);
  size_t src_i = 0;
  for (float t : times) {
    while (src_i + 1 < src_times.size() && src_times[src_i + 1] <= t) {
      src_i++;
    }
    for (int d = 0; d < value_dim; d++) {
      c.flat_values.push_back(src_values[src_i * value_dim + d]);
    }
  }
  return c;
}

struct SourceAnim {
  std::vector<float> times;  // canonical times for this clip (longest channel found)
  // (joint name, path) -> raw source data, in source's own sample times/count.
  struct Raw {
    std::vector<float> times;
    int value_dim;
    std::vector<float> values;  // times.size() * value_dim
  };
  std::map<std::pair<std::string, std::string>, Raw> by_joint_path;
};

SourceAnim gather_source_anim(const tinygltf::Model& source,
                              const SkeletonJoints& source_skel,
                              const tinygltf::Animation& anim) {
  SourceAnim result;
  size_t best_len = 0;
  for (auto& ch : anim.channels) {
    auto node_it = source_skel.node_to_joint.find(ch.target_node);
    if (node_it == source_skel.node_to_joint.end()) {
      continue;  // not a skeleton joint (e.g. the mesh node itself)
    }
    const std::string& joint_name = source_skel.names[node_it->second];
    const auto& sampler = anim.samplers.at(ch.sampler);
    auto times = gltf_util::extract_floats(source, sampler.input);

    SourceAnim::Raw raw;
    raw.times = times;
    if (ch.target_path == "translation" || ch.target_path == "scale") {
      raw.value_dim = 3;
      auto v = gltf_util::extract_vec<float, 3>(source, sampler.output,
                                                TINYGLTF_COMPONENT_TYPE_FLOAT);
      raw.values.reserve(v.size() * 3);
      for (auto& e : v) {
        raw.values.push_back(e[0]);
        raw.values.push_back(e[1]);
        raw.values.push_back(e[2]);
      }
    } else if (ch.target_path == "rotation") {
      raw.value_dim = 4;
      auto v = gltf_util::extract_vec<float, 4>(source, sampler.output,
                                                TINYGLTF_COMPONENT_TYPE_FLOAT);
      raw.values.reserve(v.size() * 4);
      for (auto& e : v) {
        raw.values.push_back(e[0]);
        raw.values.push_back(e[1]);
        raw.values.push_back(e[2]);
        raw.values.push_back(e[3]);
      }
    } else {
      continue;  // weights/other - not used by this skeleton's joints
    }

    if (times.size() > best_len) {
      best_len = times.size();
      result.times = times;
    }
    result.by_joint_path[{joint_name, ch.target_path}] = std::move(raw);
  }
  ASSERT_MSG(best_len > 0, "source animation has no usable joint channels");
  return result;
}

// Appends `data` to the output model's single buffer and creates a matching bufferView+accessor.
// Returns the new accessor's index. `with_min_max` computes min/max over the flat float data
// (required by the glTF spec for animation sampler "input"/time accessors; harmless-but-unneeded
// elsewhere, so left off for value accessors).
int add_accessor(tinygltf::Model& model,
                 const std::vector<float>& flat_floats,
                 int type,  // TINYGLTF_TYPE_SCALAR / VEC3 / VEC4
                 size_t count,
                 bool with_min_max) {
  if (model.buffers.empty()) {
    model.buffers.emplace_back();
  }
  auto& buf = model.buffers[0].data;
  while (buf.size() % 4 != 0) {
    buf.push_back(0);
  }
  const size_t offset = buf.size();
  const size_t byte_length = flat_floats.size() * sizeof(float);
  const auto* bytes = reinterpret_cast<const u8*>(flat_floats.data());
  buf.insert(buf.end(), bytes, bytes + byte_length);

  tinygltf::BufferView bv;
  bv.buffer = 0;
  bv.byteOffset = offset;
  bv.byteLength = byte_length;
  const int bv_idx = (int)model.bufferViews.size();
  model.bufferViews.push_back(bv);

  tinygltf::Accessor acc;
  acc.bufferView = bv_idx;
  acc.byteOffset = 0;
  acc.componentType = TINYGLTF_COMPONENT_TYPE_FLOAT;
  acc.type = type;
  acc.count = count;
  if (with_min_max) {
    const int dim = type == TINYGLTF_TYPE_SCALAR ? 1 : (type == TINYGLTF_TYPE_VEC3 ? 3 : 4);
    std::vector<double> mn(dim, 1e30), mx(dim, -1e30);
    for (size_t i = 0; i < count; i++) {
      for (int d = 0; d < dim; d++) {
        float v = flat_floats[i * dim + d];
        mn[d] = std::min(mn[d], (double)v);
        mx[d] = std::max(mx[d], (double)v);
      }
    }
    acc.minValues = mn;
    acc.maxValues = mx;
  }
  const int acc_idx = (int)model.accessors.size();
  model.accessors.push_back(acc);
  return acc_idx;
}

void add_channel(tinygltf::Model& model,
                tinygltf::Animation& anim,
                int target_node,
                const std::string& path,
                const std::vector<float>& times,
                const Curve& curve) {
  const int time_acc = add_accessor(model, times, TINYGLTF_TYPE_SCALAR, times.size(), true);
  const int value_acc = add_accessor(model, curve.flat_values,
                                     curve.is_quat ? TINYGLTF_TYPE_VEC4 : TINYGLTF_TYPE_VEC3,
                                     times.size(), false);

  tinygltf::AnimationSampler sampler;
  sampler.input = time_acc;
  sampler.output = value_acc;
  sampler.interpolation = "LINEAR";
  const int sampler_idx = (int)anim.samplers.size();
  anim.samplers.push_back(sampler);

  tinygltf::AnimationChannel channel;
  channel.sampler = sampler_idx;
  channel.target_node = target_node;
  channel.target_path = path;
  anim.channels.push_back(channel);
}

// Strips buffer/bufferView/accessor data down to only what the mesh+skin(+embedded images) still
// reference. Call this right after clearing model.animations and before adding new ones: the goal
// (per og-j1-board's own eichar-board.glb, the model this tool's output is meant to match the
// shape of) is a lean file with the same mesh+skeleton as the game's native model but *only* the
// newly-added animations - not a copy of the base's entire native animation set riding along.
// That matters beyond file size: build-actor's process_anim() processes every animation in the
// GLB, and any animation not named in :master-ag-map gets master_art_group_index -1, which makes
// link-art! fall back to scanning for a free slot in the master art-group and splicing it there -
// so leaving the base's original (already-native, already-correct) animations in this file would
// mean hundreds of chances to silently overwrite unrelated native animation slots.
// glTF allows JOINTS_0 to be UNSIGNED_BYTE or UNSIGNED_SHORT, but this project's mesh importer
// (common/util/gltf_util.cpp's extract_and_flatten_joints_and_weights, used by build-actor) hard-
// requires UNSIGNED_BYTE specifically. The decompiler's own mesh export (this tool's --base input,
// e.g. decompiler_out/jak2/levels/common/jakb-lod0.glb) writes it as UNSIGNED_INT instead - both
// are spec-valid on their own, but only one satisfies the importer. Converts in place by adding a
// corrected accessor and repointing the mesh at it; the old (now-unreferenced) UNSIGNED_INT one is
// cleaned up by compact_model's GC pass same as any other now-dead accessor, so call this before
// compact_model. This is the programmatic equivalent of the manual "JOINTS_0 accessor format" fix
// docs/backport-analysis.md notes was hand-applied to the earlier, hand-edited version of this
// GLB - done here instead so it isn't a one-off hand patch that has to be redone by hand again.
void fixup_joints_accessor_format(tinygltf::Model& model) {
  // Many primitives (one per material, typically) share the same source JOINTS_0 accessor - cache
  // by old accessor index so they all end up pointing at one shared corrected accessor instead of
  // each getting their own redundant copy of the same data.
  std::map<int, int> old_to_new;
  ASSERT_MSG(model.skins.size() == 1, "expected exactly one skin");
  const int n_joints = (int)model.skins[0].joints.size();
  for (auto& mesh : model.meshes) {
    for (auto& prim : mesh.primitives) {
      auto it = prim.attributes.find("JOINTS_0");
      if (it == prim.attributes.end()) {
        continue;
      }
      auto cached = old_to_new.find(it->second);
      if (cached != old_to_new.end()) {
        prim.attributes["JOINTS_0"] = cached->second;
        continue;
      }
      auto& acc = model.accessors.at(it->second);
      if (acc.componentType == TINYGLTF_COMPONENT_TYPE_UNSIGNED_BYTE) {
        continue;  // already correct
      }
      ASSERT_MSG(acc.componentType == TINYGLTF_COMPONENT_TYPE_UNSIGNED_INT,
                "JOINTS_0 fixup only handles UNSIGNED_INT -> UNSIGNED_BYTE (the decompiler mesh "
                "export's actual format) - got an unexpected componentType instead");
      ASSERT_MSG(acc.type == TINYGLTF_TYPE_VEC4, "expected JOINTS_0 to be VEC4");
      auto joints = gltf_util::extract_vec<u32, 4>(model, it->second,
                                                   TINYGLTF_COMPONENT_TYPE_UNSIGNED_INT);
      std::vector<u8> flat_u8;
      flat_u8.reserve(joints.size() * 4);
      int clamped = 0;
      for (auto& j : joints) {
        for (int c = 0; c < 4; c++) {
          u32 v = j[c];
          // Pre-existing in the decompiler's mesh export, not introduced by retargeting: some
          // vertices (observed on Daxter, not Jak) reference joint indices beyond this skin's own
          // joint count, with real (non-zero) skin weight - not a harmless unused slot. Clamp to
          // stay structurally valid (every index a real skin joint) rather than propagate an
          // out-of-bounds index into the compiled output; this only affects mesh data in a file
          // whose actual purpose is carrying animations into the native art-group via
          // :master-art-group, not this file's own (unused) mesh being rendered.
          if ((int)v >= n_joints) {
            v = (u32)(n_joints - 1);
            clamped++;
          }
          ASSERT_MSG(v <= 255, "joint index doesn't fit in a byte");
          flat_u8.push_back((u8)v);
        }
      }
      if (clamped > 0) {
        lg::warn(
            "[retarget_anim] {} of {} JOINTS_0 values referenced a joint beyond this skin's {} "
            "joints - clamped to the last joint",
            clamped, joints.size() * 4, n_joints);
      }

      if (model.buffers.empty()) {
        model.buffers.emplace_back();
      }
      auto& buf = model.buffers[0].data;
      const size_t offset = buf.size();
      buf.insert(buf.end(), flat_u8.begin(), flat_u8.end());

      tinygltf::BufferView bv;
      bv.buffer = 0;
      bv.byteOffset = offset;
      bv.byteLength = flat_u8.size();
      const int bv_idx = (int)model.bufferViews.size();
      model.bufferViews.push_back(bv);

      tinygltf::Accessor new_acc;
      new_acc.bufferView = bv_idx;
      new_acc.componentType = TINYGLTF_COMPONENT_TYPE_UNSIGNED_BYTE;
      new_acc.type = TINYGLTF_TYPE_VEC4;
      new_acc.count = joints.size();
      const int new_acc_idx = (int)model.accessors.size();
      model.accessors.push_back(new_acc);

      lg::info(
          "[retarget_anim] converted JOINTS_0 accessor {} from componentType {} to "
          "UNSIGNED_BYTE (new accessor {})",
          it->second, acc.componentType, new_acc_idx);
      old_to_new[it->second] = new_acc_idx;
      prim.attributes["JOINTS_0"] = new_acc_idx;
    }
  }
}

void compact_model(tinygltf::Model& model) {
  ASSERT_MSG(!model.buffers.empty(), "expected at least one buffer in the base GLB");
  // This file's actual layout (confirmed by inspection, not assumed): buffer 0 is the GLB's
  // embedded binary chunk (no uri) and is where every accessor (mesh/skin data) lives; buffers 1+
  // are per-image base64 data URIs referenced directly by images[].bufferView, never by an
  // accessor. Only buffer 0 needs compacting - the image buffers aren't affected by removing
  // animations at all, so they're left completely untouched (same bytes, same buffer index).

  std::vector<bool> accessor_live(model.accessors.size(), false);
  for (auto& mesh : model.meshes) {
    for (auto& prim : mesh.primitives) {
      for (auto& [name, idx] : prim.attributes) {
        accessor_live.at(idx) = true;
      }
      if (prim.indices >= 0) {
        accessor_live.at(prim.indices) = true;
      }
      for (auto& target : prim.targets) {
        for (auto& [name, idx] : target) {
          accessor_live.at(idx) = true;
        }
      }
    }
  }
  for (auto& skin : model.skins) {
    if (skin.inverseBindMatrices >= 0) {
      accessor_live.at(skin.inverseBindMatrices) = true;
    }
  }

  std::vector<bool> bufferview_live(model.bufferViews.size(), false);
  for (size_t i = 0; i < model.accessors.size(); i++) {
    if (accessor_live[i] && model.accessors[i].bufferView >= 0) {
      bufferview_live.at(model.accessors[i].bufferView) = true;
    }
  }
  for (auto& image : model.images) {
    if (image.bufferView >= 0) {
      bufferview_live.at(image.bufferView) = true;
    }
  }

  const std::vector<u8> old_buf0 = model.buffers[0].data;  // copy: we overwrite buffers[0] below
  std::vector<u8> new_buf0;
  std::vector<int> bufferview_remap(model.bufferViews.size(), -1);
  std::vector<tinygltf::BufferView> new_bufferviews;
  for (size_t i = 0; i < model.bufferViews.size(); i++) {
    if (!bufferview_live[i]) {
      continue;
    }
    tinygltf::BufferView new_bv = model.bufferViews[i];
    if (new_bv.buffer == 0) {
      while (new_buf0.size() % 4 != 0) {
        new_buf0.push_back(0);
      }
      const u8* src = old_buf0.data() + new_bv.byteOffset;
      new_bv.byteOffset = new_buf0.size();
      new_buf0.insert(new_buf0.end(), src, src + new_bv.byteLength);
    }
    // else: references one of the untouched per-image buffers - keep its byteOffset/buffer as-is.
    bufferview_remap[i] = (int)new_bufferviews.size();
    new_bufferviews.push_back(new_bv);
  }

  std::vector<int> accessor_remap(model.accessors.size(), -1);
  std::vector<tinygltf::Accessor> new_accessors;
  for (size_t i = 0; i < model.accessors.size(); i++) {
    if (!accessor_live[i]) {
      continue;
    }
    tinygltf::Accessor acc = model.accessors[i];
    if (acc.bufferView >= 0) {
      acc.bufferView = bufferview_remap.at(acc.bufferView);
    }
    accessor_remap[i] = (int)new_accessors.size();
    new_accessors.push_back(acc);
  }

  for (auto& mesh : model.meshes) {
    for (auto& prim : mesh.primitives) {
      for (auto& [name, idx] : prim.attributes) {
        idx = accessor_remap.at(idx);
      }
      if (prim.indices >= 0) {
        prim.indices = accessor_remap.at(prim.indices);
      }
      for (auto& target : prim.targets) {
        for (auto& [name, idx] : target) {
          idx = accessor_remap.at(idx);
        }
      }
    }
  }
  for (auto& skin : model.skins) {
    if (skin.inverseBindMatrices >= 0) {
      skin.inverseBindMatrices = accessor_remap.at(skin.inverseBindMatrices);
    }
  }
  for (auto& image : model.images) {
    if (image.bufferView >= 0) {
      image.bufferView = bufferview_remap.at(image.bufferView);
    }
  }

  // The top-level buffers[] array itself isn't touched by any of the above - a bufferView that got
  // dropped leaves its *buffer* entry (and, for the per-image ones, its lengthy base64 uri)
  // orphaned but still present and still serialized on write. GC that too: keep buffer 0 (always,
  // since it's where this tool writes mesh/skin/new-animation data) plus whatever buffer index
  // any surviving bufferView still points at; drop and renumber the rest.
  std::vector<bool> buffer_live(model.buffers.size(), false);
  buffer_live.at(0) = true;
  for (auto& bv : new_bufferviews) {
    buffer_live.at(bv.buffer) = true;
  }
  std::vector<int> buffer_remap(model.buffers.size(), -1);
  std::vector<tinygltf::Buffer> new_buffers;
  for (size_t i = 0; i < model.buffers.size(); i++) {
    if (!buffer_live[i]) {
      continue;
    }
    buffer_remap[i] = (int)new_buffers.size();
    new_buffers.push_back(std::move(model.buffers[i]));
  }
  for (auto& bv : new_bufferviews) {
    bv.buffer = buffer_remap.at(bv.buffer);
  }

  const size_t old_accessors = model.accessors.size();
  const size_t old_bufferviews = model.bufferViews.size();
  const size_t old_buffers = model.buffers.size();
  const size_t old_bytes = old_buf0.size();
  model.bufferViews = std::move(new_bufferviews);
  model.accessors = std::move(new_accessors);
  model.buffers = std::move(new_buffers);
  model.buffers[0].data = std::move(new_buf0);
  model.buffers[0].uri.clear();  // must stay the embedded GLB binary chunk, not a stale data uri

  lg::info(
      "[retarget_anim] compacted base model: {} -> {} accessors, {} -> {} bufferViews, {} -> {} "
      "buffers, buffer 0 {} -> {} bytes",
      old_accessors, model.accessors.size(), old_bufferviews, model.bufferViews.size(),
      old_buffers, model.buffers.size(), old_bytes, model.buffers[0].data.size());
}

}  // namespace

void retarget_glb(const fs::path& base_glb,
                  const fs::path& source_glb,
                  const std::vector<std::string>& anim_names,
                  const fs::path& output_glb,
                  const RetargetOptions& opts) {
  tinygltf::Model base = load_glb(base_glb);
  tinygltf::Model source = load_glb(source_glb);

  // Fix the JOINTS_0 accessor format mismatch between the decompiler's mesh export and
  // build-actor's importer (see fixup_joints_accessor_format's comment), then drop the base's own
  // (already-native) animations and the buffer data that was only there to back them - see
  // compact_model's comment for why that matters beyond just file size. Order matters: the fixup
  // must run first so its now-orphaned original JOINTS_0 accessor gets swept up by compact_model's
  // GC pass instead of lingering in the output.
  fixup_joints_accessor_format(base);
  base.animations.clear();
  compact_model(base);

  auto base_skel = get_skeleton(base);
  auto source_skel = get_skeleton(source);
  lg::info("[retarget_anim] base {} joints, source {} joints", base_skel.names.size(),
          source_skel.names.size());

  // Bind-pose local TRS per base joint, decomposed from each joint node's own matrix - kept for
  // every non-root channel (and for root channels the source doesn't animate).
  std::vector<math::Vector3f> bind_trans(base_skel.names.size());
  std::vector<math::Vector4f> bind_quat(base_skel.names.size());
  std::vector<math::Vector3f> bind_scale(base_skel.names.size());
  for (size_t j = 0; j < base_skel.names.size(); j++) {
    auto m = matrix_from_node(base.nodes.at(base_skel.node_of_joint[j]));
    decompose_matrix(m, &bind_trans[j], &bind_quat[j], &bind_scale[j]);
  }

  const auto is_root = [&](const std::string& name) {
    return std::find(opts.root_joints.begin(), opts.root_joints.end(), name) !=
          opts.root_joints.end();
  };
  const auto is_forced_neutral_scale = [&](const std::string& name) {
    return std::find(opts.force_neutral_scale_joints.begin(),
                     opts.force_neutral_scale_joints.end(),
                     name) != opts.force_neutral_scale_joints.end();
  };

  int missing_in_source = 0;
  for (auto& anim_name : anim_names) {
    auto anim_it = std::find_if(source.animations.begin(), source.animations.end(),
                                [&](auto& a) { return a.name == anim_name; });
    ASSERT_MSG(anim_it != source.animations.end(),
              fmt::format("source has no animation named '{}'", anim_name).c_str());
    SourceAnim src = gather_source_anim(source, source_skel, *anim_it);
    const auto& times = src.times;
    const size_t num_frames = times.size();
    lg::info("[retarget_anim] '{}': {} frames, {} source channels", anim_name, num_frames,
            src.by_joint_path.size());

    tinygltf::Animation out_anim;
    out_anim.name = anim_name;

    for (size_t j = 0; j < base_skel.names.size(); j++) {
      const std::string& name = base_skel.names[j];
      const int target_node = base_skel.node_of_joint[j];
      const bool root = is_root(name);
      auto src_has = [&](const char* path) {
        return src.by_joint_path.count({name, path}) != 0;
      };

      // translation: root joints get real root motion from source when present; every other
      // joint (and any root joint the source doesn't animate) keeps its own bind-pose offset so
      // bone lengths stay correct.
      Curve trans_curve;
      if (root && src_has("translation")) {
        auto& raw = src.by_joint_path.at({name, "translation"});
        trans_curve = resample_to_times(raw.times, raw.values, 3, times);
      } else {
        trans_curve = constant_curve(num_frames, bind_trans[j]);
      }

      // rotation: always take the source's articulation when present (bone-length independent,
      // safe to retarget for any joint); otherwise hold the bind pose (no relative motion).
      Curve rot_curve;
      if (src_has("rotation")) {
        auto& raw = src.by_joint_path.at({name, "rotation"});
        rot_curve = resample_to_times(raw.times, raw.values, 4, times);
      } else {
        rot_curve = constant_curve(num_frames, bind_quat[j]);
        if (name != "align" && name != "main" && root == false) {
          // expected for most joints on a source clip that only animates a subset - not an error.
        } else if (!root) {
          missing_in_source++;
        }
      }

      // scale: bind pose, except joints explicitly forced to never drift from it (e.g. the board
      // attachment) and root joints when the source animates scale itself.
      //
      // "Forced neutral" means hold the base's own bind-pose scale, NOT hard-code (1,1,1) - those
      // are only the same thing if the joint's bind pose happens to be unscaled. Ground-truthed
      // against decompiler_out/jak2/levels/common/jakb-lod0.glb: `board` (like `gun` and `extra`,
      // the other attachment joints) has bind-pose scale (0.7143,0.7143,0.7143) - it's a direct
      // child of `main`, whose own bind-pose scale is 1.4, and 0.7143 = 1/1.4 exactly, so the
      // attachment's local scale cancels its parent's out and the held item renders at its
      // natural size regardless of main's. Hard-coding (1,1,1) here broke that cancellation and
      // made the board render at the wrong size throughout both new animations.
      Curve scale_curve;
      if (is_forced_neutral_scale(name)) {
        scale_curve = constant_curve(num_frames, bind_scale[j]);
      } else if (root && src_has("scale")) {
        auto& raw = src.by_joint_path.at({name, "scale"});
        scale_curve = resample_to_times(raw.times, raw.values, 3, times);
      } else {
        scale_curve = constant_curve(num_frames, bind_scale[j]);
      }

      // Force the align joint's net yaw to a specific value for the designated animation
      // (turn-around), regardless of whether/how the source clip itself animates align - the
      // in-game state (target-board-turn-around) drives the logical 180 turn independently in
      // GOAL code, so this only needs to make the *visual* root motion agree with that, not carry
      // gameplay logic itself.
      if (name == "align" && !opts.force_180_yaw_align_anim.empty() &&
          anim_name == opts.force_180_yaw_align_anim) {
        const math::Vector4f q_first{rot_curve.flat_values[0], rot_curve.flat_values[1],
                                     rot_curve.flat_values[2], rot_curve.flat_values[3]};
        const size_t last = num_frames - 1;
        const math::Vector4f q_last{rot_curve.flat_values[last * 4 + 0],
                                    rot_curve.flat_values[last * 4 + 1],
                                    rot_curve.flat_values[last * 4 + 2],
                                    rot_curve.flat_values[last * 4 + 3]};
        const float current_yaw = quat_y_angle(quat_multiply(q_last, quat_conjugate(q_first)));
        const float target_yaw = kPi;  // 180 degrees
        float correction = target_yaw - current_yaw;
        // wrap to (-pi, pi] so we apply the shorter correction
        while (correction > kPi) correction -= 2.0f * kPi;
        while (correction <= -kPi) correction += 2.0f * kPi;
        lg::info(
            "[retarget_anim] '{}': align net yaw before correction = {:.1f} deg, applying {:.1f} "
            "deg ramp to reach 180",
            anim_name, current_yaw * 180.0 / kPi, correction * 180.0 / kPi);
        for (size_t f = 0; f < num_frames; f++) {
          const float ramp = num_frames > 1 ? (float)f / (float)(num_frames - 1) : 1.0f;
          const math::Vector4f extra = quat_from_y_angle(correction * ramp);
          math::Vector4f q{rot_curve.flat_values[f * 4 + 0], rot_curve.flat_values[f * 4 + 1],
                           rot_curve.flat_values[f * 4 + 2], rot_curve.flat_values[f * 4 + 3]};
          q = quat_multiply(extra, q);
          rot_curve.flat_values[f * 4 + 0] = q.x();
          rot_curve.flat_values[f * 4 + 1] = q.y();
          rot_curve.flat_values[f * 4 + 2] = q.z();
          rot_curve.flat_values[f * 4 + 3] = q.w();
        }
      }

      add_channel(base, out_anim, target_node, "translation", times, trans_curve);
      add_channel(base, out_anim, target_node, "rotation", times, rot_curve);
      add_channel(base, out_anim, target_node, "scale", times, scale_curve);
    }

    base.animations.push_back(std::move(out_anim));
  }
  if (missing_in_source > 0) {
    lg::warn(
        "[retarget_anim] {} root-joint/animation combinations had no source rotation channel and "
        "fell back to the bind pose - double check this is expected",
        missing_in_source);
  }

  tinygltf::TinyGLTF writer;
  fs::create_directories(output_glb.parent_path());
  const bool ok =
      writer.WriteGltfSceneToFile(&base, output_glb.string(), true, true, false, true);
  ASSERT_MSG(ok, fmt::format("failed to write {}", output_glb.string()).c_str());
  lg::info("[retarget_anim] wrote {}", output_glb.string());
}

}  // namespace retarget_anim
