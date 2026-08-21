#include "build_sbk.h"

#include "common/log/log.h"
#include "common/util/FileUtil.h"

#include "third-party/CLI11.hpp"

int main(int argc, char** argv) {
  lg::set_stdout_level(lg::level::info);
  lg::set_flush_level(lg::level::info);
  lg::initialize();

  std::string input_str;
  std::string output_str;
  std::string append_str;
  std::vector<std::string> only_names;
  u32 bank_id = 0;
  bool jak1 = false;

  CLI::App app{"OpenGOAL SBK builder — create or append to sound banks"};
  app.add_option("-i,--input", input_str, "Input folder path (metadata.txt + wav files)")
      ->required();
  app.add_option("-o,--output", output_str, "Output .SBK file path")->required();
  app.add_option("-a,--append", append_str,
                 "Path to an existing .SBK; new sounds are appended to it instead of building "
                 "a fresh bank");
  app.add_option("--bank-id", bank_id, "Bank ID to embed in the SBlk header (default 0)");
  app.add_option("--only", only_names,
                 "Sound name(s) from metadata.txt to include; if omitted, every sound in "
                 "metadata.txt is used");
  app.add_flag("--jak1", jak1,
               "Prepend a 2048-byte on-disc name table. Only Jak 1's sound engine expects this - "
               "do not pass this for Jak 2 or Jak 3 banks.");
  CLI11_PARSE(app, argc, argv);

  if (input_str.empty()) {
    lg::error("[build_sbk] need to provide an input folder");
    return 1;
  }

  if (append_str.empty()) {
    sbk::BuildOptions opts;
    opts.bank_id = bank_id;
    opts.jak1_format = jak1;
    sbk::create_sbk_from_dir(fs::path(input_str), fs::path(output_str), opts, only_names);
  } else {
    if (jak1 || bank_id != 0) {
      lg::warn("[build_sbk] --jak1 and --bank-id are ignored in --append mode");
    }
    sbk::append_sbk_from_dir(fs::path(append_str), fs::path(input_str), fs::path(output_str),
                             only_names);
  }

  return 0;
}
