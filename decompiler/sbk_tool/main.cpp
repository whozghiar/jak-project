// Standalone sound-bank extractor.
//
// The decompiler only rips .SBK banks as a side effect of a full run (config key
// "rip_sound_banks"), which first loads every DGO of the game (can take 30+ minutes on a large
// game) - far too slow when all that is wanted is a handful of banks to port into a mod. This
// tool calls the exact same extractor (decompiler/data/extract_sbk.cpp) directly on a folder or
// a single file.
//
// Usage:
//   extract_sbk <in: SBK folder or .SBK file> <out folder> [--banks NAME1,NAME2,...]
//
// Output layout is identical to the decompiler's: <out>/<BANK>/metadata.txt + <BANK>/*.wav,
// directly consumable by goalc's (build-sbk ...) / (append-sbk ...) steps.
#include <string>
#include <vector>

#include "common/log/log.h"
#include "common/util/FileUtil.h"

#include "decompiler/data/extract_sbk.h"
#include "third-party/CLI11.hpp"

int main(int argc, char** argv) {
  lg::set_stdout_level(lg::level::info);
  lg::set_flush_level(lg::level::info);
  lg::initialize();

  std::string in_str;
  std::string out_str;
  std::vector<std::string> banks;

  CLI::App app{"Extract PS2 .SBK sound banks (SFX and music) to WAV + metadata.txt"};
  app.add_option("in", in_str, "Folder containing .SBK files, or a single .SBK file")->required();
  app.add_option("out", out_str, "Output folder (one sub-folder per bank)")->required();
  app.add_option("--banks", banks,
                 "Only extract these bank names (case-insensitive stems, comma or space separated)")
      ->delimiter(',');
  CLI11_PARSE(app, argc, argv);

  fs::path in_path(in_str);
  fs::path out_path(out_str);
  if (!fs::exists(in_path)) {
    lg::error("input path {} does not exist", in_path.string());
    return 1;
  }

  if (fs::is_directory(in_path)) {
    decompiler::extract_sbk_files(in_path, out_path, banks);
  } else {
    decompiler::extract_sbk_file(in_path, out_path);
  }
  return 0;
}
