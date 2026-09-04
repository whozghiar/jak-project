#pragma once

/*!
 * @file multiplayer_protocol.h
 * jak2/features/multiplayer (AI-assisted)
 *
 * Wire format and constants for the local-network, presence-only multiplayer mod.
 *
 * Design intentionally avoids the existing DECI2 listener stack (game/system/Deci2Server.cpp,
 * game/kernel/common/kdsnetm.cpp): that protocol is a TCP, command/response, debugger-oriented
 * protocol. This is a fixed-size, unreliable UDP "latest state" snapshot instead - one packet is
 * always exactly sizeof(MpPlayerStatePacket) bytes, so there is no framing or reassembly.
 *
 * This same struct layout is used both as the raw UDP wire format (both peers run identical
 * x86-64 builds, so no endianness/alignment translation is needed) and as the layout GOAL-side
 * code mirrors with a `deftype` (see goal_src/jak2/pc/multiplayer/mp-h.gc) when marshaling data
 * across the GOAL/C++ FFI boundary. Field order and the explicit padding bytes below are chosen
 * so the struct has no implicit compiler-inserted padding - keep the GOAL deftype's field order
 * and padding fields in sync with this if either side ever changes.
 */

#include "common/common_types.h"

namespace mp_net {

// Next free port after the existing DECI2 listener (8112 jak1 / 8113 jak2, see
// common/listener_common.h) and the nREPL listener (8181, see common/repl/config.h).
constexpr u16 MP_DEFAULT_PORT = 8114;

// v1 hard cap on simultaneous players (see plan's "explicit non-goals" - full mesh UDP,
// no relay/host-authoritative model needed at this scale).
constexpr u32 MP_MAX_PLAYERS = 4;

constexpr u16 MP_PROTOCOL_VERSION = 1;

// Coarse, presence-only animation state. Deliberately NOT target's real state machine - just
// enough to pick a believable looped animation on the remote-player stub.
enum class MpAnimState : u8 {
  Idle = 0,
  Walk = 1,
  Run = 2,
  Jump = 3,
  Fall = 4,
  Duck = 5,
};

// Selectable local-player appearance. Applied via a live `initialize-skeleton` re-skin of
// `*target*` (see docs/modding/jak2_modding_utilities/21_live_reskinning_a_process_with_initialize-skeleton.md).
enum class MpSkinId : u8 {
  Jak = 0,
  KrimzonGuard = 1,
};

// One full state snapshot for one player. Sent every local tick to every configured peer, and
// polled by the receiver every frame. Total size is 48 bytes, verified below with a static_assert
// so accidental padding changes are caught at compile time.
struct MpPlayerStatePacket {
  u32 sequence;       // monotonically increasing per-sender counter, used to reject stale/out-of-order packets
  u32 timestamp_ms;   // sender's local clock at send time, reserved for future interpolation tuning
  float pos_x;
  float pos_y;
  float pos_z;
  float quat_x;
  float quat_y;
  float quat_z;
  float quat_w;
  float anim_phase;   // normalized 0..1 anim time, lets the remote stub roughly line up its `ja` frame
  u16 protocol_version;
  u8 player_id;        // 0..MP_MAX_PLAYERS-1, assigned locally by config (see MP_LOCAL_PLAYER_ID)
  u8 skin_id;           // MpSkinId
  u8 anim_state;         // MpAnimState
  // `valid` is unused on the wire (sender always leaves it 0) - it is repurposed by
  // mp_goal_bridge::mp_poll_recv when writing the fixed MP_MAX_PLAYERS-sized out-array GOAL reads:
  // 1 means "this slot holds a live peer's last packet", 0 means "no peer at this player_id right
  // now". This avoids needing a second parallel array just to say which slots are populated.
  u8 valid;
  u8 _pad[2];  // explicit padding, keeps struct size a multiple of 4 with no implicit gaps
};

static_assert(sizeof(MpPlayerStatePacket) == 48,
              "MpPlayerStatePacket layout changed - update the mirrored GOAL deftype in "
              "goal_src/jak2/pc/multiplayer/mp-h.gc to match, field-for-field, before changing this.");

}  // namespace mp_net
