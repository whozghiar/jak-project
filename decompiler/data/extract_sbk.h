#pragma once

#include <string>
#include <vector>

#include "common/util/FileUtil.h"

namespace decompiler {

// extract all sound banks into wav files under output_dir.
// SBlk (SFX) banks write one wav per named sound.
// SBv2 (music) banks write one wav per instrument tone.
// only_banks: optional case-insensitive list of bank stems (e.g. "MODEGUR1") to restrict the run.
void extract_sbk_files(const fs::path& input_dir,
                       const fs::path& output_dir,
                       const std::vector<std::string>& only_banks = {});

// extract a single .SBK file (errors are logged, never thrown).
void extract_sbk_file(const fs::path& sbk_path, const fs::path& output_dir);

}  // namespace decompiler
