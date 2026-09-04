/*!
 * @file mp_session.cpp
 * jak2/features/multiplayer (AI-assisted)
 * See mp_session.h for design notes.
 */

#include "mp_session.h"

#include <chrono>
#include <cstdlib>
#include <sstream>

#include "common/cross_sockets/XSocket.h"
#include "common/log/log.h"

#ifdef _WIN32
#include <WS2tcpip.h>
#else
#include <arpa/inet.h>
#include <fcntl.h>
#endif

namespace mp_net {

namespace {

double now_seconds() {
  using namespace std::chrono;
  return duration<double>(steady_clock::now().time_since_epoch()).count();
}

// Puts a socket into non-blocking mode. Required because game/kernel FFI calls into this session
// must never stall a frame waiting on network I/O - unlike set_socket_timeout (which still blocks
// up to the timeout), this makes send/recv return immediately if no data is available.
void set_non_blocking(int sock) {
#ifdef OS_POSIX
  int flags = fcntl(sock, F_GETFL, 0);
  fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#elif _WIN32
  u_long mode = 1;
  ioctlsocket(sock, FIONBIO, &mode);
#endif
}

// Parses "MP_PEERS=127.0.0.1:8114,192.168.1.5:8114" into resolved peer addresses. Malformed
// entries are logged and skipped rather than aborting the whole list - one typo shouldn't prevent
// connecting to the rest of the peers.
std::vector<sockaddr_in> parse_peer_list(const std::string& peers_env, u16 default_port) {
  std::vector<sockaddr_in> result;
  std::stringstream ss(peers_env);
  std::string entry;
  while (std::getline(ss, entry, ',')) {
    if (entry.empty()) {
      continue;
    }
    auto colon_pos = entry.find(':');
    std::string ip = entry;
    u16 port = default_port;
    if (colon_pos != std::string::npos) {
      ip = entry.substr(0, colon_pos);
      port = static_cast<u16>(std::atoi(entry.substr(colon_pos + 1).c_str()));
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &addr.sin_addr) != 1) {
      lg::error("[multiplayer] Failed to parse peer address '{}', skipping", entry);
      continue;
    }
    result.push_back(addr);
  }
  return result;
}

}  // namespace

bool MpSession::init() {
  const char* peers_env = std::getenv("MP_PEERS");
  if (!peers_env || std::string(peers_env).empty()) {
    // No peer configuration - multiplayer is simply inactive. Solo play must be unaffected.
    lg::info("[multiplayer] MP_PEERS not set, multiplayer session inactive");
    return false;
  }

  const char* player_id_env = std::getenv("MP_LOCAL_PLAYER_ID");
  const char* local_port_env = std::getenv("MP_LOCAL_PORT");
  m_local_player_id = player_id_env ? static_cast<u8>(std::atoi(player_id_env)) : 0;
  u16 local_port = local_port_env ? static_cast<u16>(std::atoi(local_port_env)) : MP_DEFAULT_PORT;

  if (m_local_player_id >= MP_MAX_PLAYERS) {
    lg::error("[multiplayer] MP_LOCAL_PLAYER_ID {} out of range (max {}), disabling multiplayer",
              m_local_player_id, MP_MAX_PLAYERS - 1);
    return false;
  }

  m_peer_addrs = parse_peer_list(peers_env, MP_DEFAULT_PORT);
  if (m_peer_addrs.empty()) {
    lg::error("[multiplayer] MP_PEERS set but no valid peers parsed, disabling multiplayer");
    return false;
  }

  m_socket = open_socket(AF_INET, SOCK_DGRAM, 0);
  if (m_socket < 0) {
    lg::error("[multiplayer] Failed to open UDP socket");
    m_socket = -1;
    return false;
  }

  sockaddr_in bind_addr{};
  bind_addr.sin_family = AF_INET;
  bind_addr.sin_port = htons(local_port);
  bind_addr.sin_addr.s_addr = INADDR_ANY;
  if (bind_socket(m_socket, (sockaddr*)&bind_addr, sizeof(bind_addr)) < 0) {
    lg::error("[multiplayer] Failed to bind UDP socket to port {}", local_port);
    close_socket(m_socket);
    m_socket = -1;
    return false;
  }

  set_non_blocking(m_socket);

  lg::info("[multiplayer] session active: player_id={} local_port={} peers={}", m_local_player_id,
            local_port, m_peer_addrs.size());
  return true;
}

void MpSession::shutdown() {
  if (m_socket >= 0) {
    close_socket(m_socket);
    m_socket = -1;
  }
}

void MpSession::send_local_state(const MpPlayerStatePacket& packet) {
  if (m_socket < 0) {
    return;
  }
  for (const auto& peer_addr : m_peer_addrs) {
    send_to_socket(m_socket, (const char*)&packet, sizeof(packet), peer_addr);
  }
}

u32 MpSession::poll_recv() {
  if (m_socket < 0) {
    return 0;
  }

  for (int i = 0; i < kMaxPacketsPerPoll; ++i) {
    MpPlayerStatePacket packet;
    sockaddr_in from_addr{};
    int bytes = recv_from_socket(m_socket, (char*)&packet, sizeof(packet), &from_addr);
    if (bytes != (int)sizeof(packet)) {
      // Either no more data queued (non-blocking recv returned -1) or a malformed/partial
      // datagram - either way, nothing more to process this call.
      break;
    }
    if (packet.protocol_version != MP_PROTOCOL_VERSION) {
      continue;
    }
    if (packet.player_id >= MP_MAX_PLAYERS || packet.player_id == m_local_player_id) {
      // Ignore out-of-range ids and echoes of our own state (can happen if a peer entry
      // accidentally points back at ourselves).
      continue;
    }

    PeerState& peer = m_peers[packet.player_id];
    if (peer.active && packet.sequence <= peer.last_sequence_seen) {
      // Stale/out-of-order packet - drop it, keep the newer state we already have.
      continue;
    }

    peer.active = true;
    peer.last_packet = packet;
    peer.last_sequence_seen = packet.sequence;
    peer.last_recv_time_seconds = now_seconds();
  }

  double now = now_seconds();
  u32 live_count = 0;
  for (auto& peer : m_peers) {
    if (peer.active && (now - peer.last_recv_time_seconds) > kPeerTimeoutSeconds) {
      peer.active = false;
    }
    if (peer.active) {
      ++live_count;
    }
  }
  return live_count;
}

MpSession& get_session() {
  static MpSession session;
  return session;
}

}  // namespace mp_net
