#pragma once

#include <string>
#include <vector>

#include "common/common_types.h"
#include "common/util/FileUtil.h"

namespace sbk {

struct BuildOptions {
  u32 bank_id = 0;
  // Prepend a 2048-byte on-disc name table before the FileAttributes header. This layout is
  // specific to Jak 1's sound engine (989snd expects a "CUSTOM" name table there) - Jak 2 and
  // Jak 3 load the FileAttributes header directly with no such prefix, so leave this false for
  // those games.
  bool jak1_format = false;
};

// One logical sound with one or more variant WAV files.
// Each variant becomes a TONE grain; for multiple variants a RAND_PLAY grain is auto-inserted.
struct SoundSpec {
  std::vector<fs::path> variants;
};

// Create a new SBK from a list of sound specs.
void create_sbk(const std::vector<SoundSpec>& sounds,
                const fs::path& output,
                const BuildOptions& opts = {});

// Append sound specs as new sounds to an existing V1 SBlk bank.
void append_sbk(const fs::path& input,
                const std::vector<SoundSpec>& sounds,
                const fs::path& output);

// Create a new SBK from a metadata directory (output of extract_sbk: a metadata.txt plus the WAV
// files it references). If `only_names` is non-empty, only sounds whose name (as written in
// metadata.txt) appears in `only_names` are included - everything else in metadata.txt is
// skipped. This lets a metadata.txt dumped from a large bank be used to pull out a handful of
// named sounds without hand-trimming the file first.
void create_sbk_from_dir(const fs::path& dir,
                         const fs::path& output,
                         const BuildOptions& opts = {},
                         const std::vector<std::string>& only_names = {});

// Append sounds from a metadata directory to an existing V1 SBlk bank. See create_sbk_from_dir
// for the meaning of `only_names`.
void append_sbk_from_dir(const fs::path& input,
                         const fs::path& dir,
                         const fs::path& output,
                         const std::vector<std::string>& only_names = {});

}  // namespace sbk
