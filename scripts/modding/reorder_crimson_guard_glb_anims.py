#!/usr/bin/env python3
"""Reorder the `animations` array of a re-skinned crimson-guard .glb so its index order
matches the native crimson-guard-ag art-group slot layout (see
decompiler/config/jak2/ntsc_v1/art-group-info.min.json, key "crimson-guard-ag").

Used together with (build-actor ... :native-header #t) (see
goal_src/jak2/lib/project-lib.gp) so a reskin's animation slot N lines up with slot N in
the original crimson-guard-ag. See docs/modding/current_mod/blue_guard_reskin_readme.md.

Re-run this any time you re-export the source .glb from Blender (a fresh export re-sorts
the animations array alphabetically again).

Usage: python reorder_crimson_guard_glb_anims.py <in.glb> <out.glb>
"""
import json
import struct
import sys

# canonical order, indices 4..43 in crimson-guard-ag
CANONICAL_SUFFIXES = [
    "idle", "walk", "run", "notice", "knocked", "knocked-land",
    "blue-hit", "blue-hit-land", "blue-hit-land-death",
    "yellow-hit0", "yellow-hit0-land", "yellow-hit1", "yellow-hit1-land",
    "die", "rifle-butt",
    "idle-to-stab-idle", "stab-idle-loop", "stab-idle-to-attack", "stab-attack",
    "stab-attack-to-stab-idle", "stab-idle-to-idle", "stab-shuffle",
    "gun-attack",
    "attack-shoot-knee-start", "attack-shoot-knee-loop", "attack-shoot-knee",
    "attack-shoot-knee-end",
    "knocked-back", "knocked-back-land",
    "get-up-front", "get-up-back",
    "bike-stance", "car-stance",
    "grenade-attack",
    "jump-high", "die-falling", "jump-right", "jump-left",
    "knocked-from-car", "knocked-from-bike",
]


def main():
    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, "rb") as f:
        data = f.read()

    magic, version, _length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF" and version == 2

    off = 12
    json_chunk_len, json_chunk_type = struct.unpack_from("<I4s", data, off)
    assert json_chunk_type == b"JSON"
    json_start = off + 8
    json_bytes = data[json_start:json_start + json_chunk_len]
    off = json_start + json_chunk_len

    bin_chunk = None
    if off < len(data):
        bin_chunk_len, _bin_chunk_type = struct.unpack_from("<I4s", data, off)
        bin_start = off + 8
        bin_chunk = data[off:bin_start + bin_chunk_len]

    j = json.loads(json_bytes)
    by_name = {a["name"]: a for a in j["animations"]}

    # figure out the common name prefix (e.g. "crimson-guard-")
    prefix = None
    for suffix in CANONICAL_SUFFIXES:
        for name in by_name:
            if name.endswith(suffix) and name[: -len(suffix)]:
                prefix = name[: -len(suffix)]
                break
        if prefix:
            break
    assert prefix, "could not determine animation name prefix"

    ordered = []
    missing = []
    for suffix in CANONICAL_SUFFIXES:
        name = prefix + suffix
        if name in by_name:
            ordered.append(by_name.pop(name))
        else:
            missing.append(name)

    if missing:
        raise SystemExit(f"missing expected animations: {missing}")
    if by_name:
        raise SystemExit(f"unexpected leftover animations not in canonical order: {list(by_name)}")

    j["animations"] = ordered
    new_json_bytes = json.dumps(j, separators=(",", ":")).encode("utf-8")
    pad = (-len(new_json_bytes)) % 4
    new_json_bytes += b" " * pad

    out = bytearray()
    out += struct.pack("<4sII", b"glTF", 2, 0)  # length patched below
    out += struct.pack("<I4s", len(new_json_bytes), b"JSON")
    out += new_json_bytes
    if bin_chunk is not None:
        out += bin_chunk
    struct.pack_into("<I", out, 8, len(out))

    with open(out_path, "wb") as f:
        f.write(out)

    print(f"wrote {out_path}: {len(ordered)} animations reordered, prefix={prefix!r}")


if __name__ == "__main__":
    main()
