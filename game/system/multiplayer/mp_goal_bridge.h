#pragma once

/*!
 * @file mp_goal_bridge.h
 * jak2/features/multiplayer (AI-assisted)
 *
 * Thin FFI surface exposed to GOAL via `make_function_symbol_from_c` (registered in
 * game/kernel/jak2/kmachine.cpp's InitMachine_PCPort(), the same idiom used for other PC-port
 * extras like `pc-discord-rpc-update`). Deliberately far simpler than the DECI2 listener's
 * event-driven `GoalProtoHandler` (game/kernel/common/kdsnetm.cpp) - no framing, no dispatch
 * table, just "fill a struct in GOAL memory, call a function, get a struct back."
 *
 * All GOAL-facing functions take/return plain integers (GOAL pointers are passed as u32 offsets
 * from the base of EE memory, per game/kernel/common/Ptr.h) so they marshal cleanly through the
 * GOAL/C ABI boundary that make_function_symbol_from_c expects.
 */

#include "common/common_types.h"

namespace mp_goal_bridge {

// Opens the UDP session (see mp_session.h). Safe to call even with no MP_PEERS configured - in
// that case multiplayer just stays inactive and every other function here becomes a no-op.
// Returns a GOAL boolean symbol offset (#t/#f).
u64 mp_init(u64 unused);

// Closes the UDP session. Call once at game exit.
void mp_shutdown(u64 unused);

// `packet_ptr` is a GOAL pointer to an `mp-player-state` structure (goal_src/jak2/pc/multiplayer/
// mp-h.gc) that the caller has already filled in with skin_id/pos/quat/anim_phase/anim_state.
// This function fills in protocol_version, the local player_id (from session config), a
// monotonically increasing sequence number, and a timestamp, then sends the resulting packet to
// every configured peer. No-op if the session isn't active.
void mp_send_local_state(u64 packet_ptr);

// `out_array_ptr` is a GOAL pointer to a fixed MP_MAX_PLAYERS-sized array of `mp-player-state`
// structures. Every call rewrites the whole array: for each player_id slot with a live peer, the
// peer's last received packet is copied in with `valid` set to 1; every other slot is zeroed with
// `valid` left at 0. Returns the number of currently-live remote peers (0 if the session isn't
// active).
u64 mp_poll_recv(u64 out_array_ptr);

// Returns this instance's configured player id (0 if the session isn't active).
u64 mp_get_local_player_id(u64 unused);

}  // namespace mp_goal_bridge
