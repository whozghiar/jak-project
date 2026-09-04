#pragma once

/*!
 * @file mp_session.h
 * jak2/features/multiplayer (AI-assisted)
 *
 * Owns the UDP socket, the fixed peer list, and the per-peer state table for the local-network
 * presence-only multiplayer mod. This is a thin, engine-adjacent runtime service (same category as
 * game/system/Deci2Server.cpp), not part of the GOAL kernel proper - the GOAL/FFI marshaling lives
 * separately in mp_goal_bridge.h/.cpp.
 *
 * v1 session model: a fixed peer list read once at boot from environment variables (no
 * broadcast/mDNS discovery - see the mod's implementation plan for why). Every instance sends its
 * own state to every configured peer every tick (full mesh) and listens on its own local port for
 * everyone else's packets. All socket I/O is non-blocking; nothing here should ever stall a game
 * frame waiting on the network.
 */

#include <array>
#include <cstring>
#include <vector>

#include "common/common_types.h"
#include "common/network/multiplayer_protocol.h"

#ifdef _WIN32
#include <WinSock2.h>
#else
#include <netinet/in.h>
#endif

namespace mp_net {

// The most recent snapshot received from one remote peer, plus bookkeeping used to detect
// out-of-order/stale packets and peer disconnects.
struct PeerState {
  bool active = false;
  MpPlayerStatePacket last_packet = {};
  u32 last_sequence_seen = 0;
  double last_recv_time_seconds = 0.0;
};

class MpSession {
 public:
  // Reads MP_PEERS / MP_LOCAL_PLAYER_ID / MP_LOCAL_PORT from the environment, opens a non-blocking
  // UDP socket bound to the local port, and resolves the configured peer addresses.
  // Returns true on success. If no peer configuration is present, multiplayer is simply inactive -
  // this must never prevent normal single-player boot/play.
  bool init();

  // Closes the socket, if open. Safe to call even if init() was never called or failed.
  void shutdown();

  bool is_active() const { return m_socket >= 0; }
  u8 local_player_id() const { return m_local_player_id; }

  // Sends one state snapshot to every configured peer. `sequence` is expected to be
  // caller-managed and monotonically increasing (mp_goal_bridge owns that counter).
  void send_local_state(const MpPlayerStatePacket& packet);

  // Drains all currently-queued incoming packets (bounded per call so a burst can never stall a
  // frame), updates the peer table, and marks any peer that hasn't sent a packet within
  // kPeerTimeoutSeconds as inactive. Returns the number of currently-active remote peers.
  u32 poll_recv();

  // Fixed-size table indexed by player_id. Only entries with `active == true` are live.
  const std::array<PeerState, MP_MAX_PLAYERS>& peers() const { return m_peers; }

 private:
  static constexpr double kPeerTimeoutSeconds = 3.0;
  static constexpr int kMaxPacketsPerPoll = 64;  // bound recv work per frame

  int m_socket = -1;
  u8 m_local_player_id = 0;
  std::vector<sockaddr_in> m_peer_addrs;
  std::array<PeerState, MP_MAX_PLAYERS> m_peers{};
};

// Single shared session instance, analogous to other engine-wide singletons initialized once at
// boot (e.g. the Deci2Server instance owned by the kernel). Owned by mp_goal_bridge.cpp.
MpSession& get_session();

}  // namespace mp_net
