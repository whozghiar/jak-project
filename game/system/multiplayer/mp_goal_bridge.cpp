/*!
 * @file mp_goal_bridge.cpp
 * jak2/features/multiplayer (AI-assisted)
 * See mp_goal_bridge.h for design notes.
 */

#include "mp_goal_bridge.h"

#include <chrono>

#include "mp_session.h"

#include "common/log/log.h"
#include "common/network/multiplayer_protocol.h"
#include "common/symbols.h"

#include "game/kernel/common/Ptr.h"
#include "game/kernel/common/kscheme.h"

namespace mp_goal_bridge {

using mp_net::MpPlayerStatePacket;
using mp_net::MP_MAX_PLAYERS;
using mp_net::MP_PROTOCOL_VERSION;

namespace {

// Same small helper every other kmachine_extras.cpp defines locally - GOAL booleans are the
// symbol `#t` or `#f`, not a C 0/1, so returning a raw integer here would not behave as a
// GOAL-side (symbol) return value.
inline u64 bool_to_symbol(bool val) {
  return val ? static_cast<u64>(s7.offset) + true_symbol_offset(g_game_version) : s7.offset;
}

u32 next_sequence() {
  static u32 sequence = 0;
  return ++sequence;
}

u32 now_ms() {
  using namespace std::chrono;
  return static_cast<u32>(
      duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count());
}

}  // namespace

u64 mp_init(u64 unused) {
  (void)unused;
  bool ok = mp_net::get_session().init();
  return bool_to_symbol(ok);
}

void mp_shutdown(u64 unused) {
  (void)unused;
  mp_net::get_session().shutdown();
}

void mp_send_local_state(u64 packet_ptr) {
  auto& session = mp_net::get_session();
  if (!session.is_active()) {
    return;
  }

  // GOAL fills skin_id/pos/quat/anim_phase/anim_state into the scratch struct before calling
  // this; we fill in everything the session itself is authoritative over.
  auto* packet = Ptr<MpPlayerStatePacket>((u32)packet_ptr).c();
  if (!packet) {
    return;
  }

  packet->protocol_version = MP_PROTOCOL_VERSION;
  packet->player_id = session.local_player_id();
  packet->sequence = next_sequence();
  packet->timestamp_ms = now_ms();
  packet->valid = 0;  // meaningless on the wire, see multiplayer_protocol.h

  session.send_local_state(*packet);
}

u64 mp_poll_recv(u64 out_array_ptr) {
  auto& session = mp_net::get_session();

  auto* out_array = Ptr<MpPlayerStatePacket>((u32)out_array_ptr).c();
  if (!out_array) {
    return 0;
  }

  if (!session.is_active()) {
    for (u32 i = 0; i < MP_MAX_PLAYERS; ++i) {
      out_array[i] = {};
    }
    return 0;
  }

  u32 live_count = session.poll_recv();

  const auto& peers = session.peers();
  for (u32 i = 0; i < MP_MAX_PLAYERS; ++i) {
    if (peers[i].active) {
      out_array[i] = peers[i].last_packet;
      out_array[i].valid = 1;
    } else {
      out_array[i] = {};
      out_array[i].valid = 0;
    }
  }

  return live_count;
}

u64 mp_get_local_player_id(u64 unused) {
  (void)unused;
  return mp_net::get_session().local_player_id();
}

}  // namespace mp_goal_bridge
