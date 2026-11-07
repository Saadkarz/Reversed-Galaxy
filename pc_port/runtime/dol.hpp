#pragma once

// Parser/loader for the Nintendo DOL executable format.

#include "memory.hpp"

#include <string>
#include <vector>

namespace g2c {

struct DolSection {
    bool isText = false;
    u32 fileOffset = 0;
    u32 address = 0;
    u32 size = 0;
};

struct DolImage {
    std::vector<DolSection> sections;  // non-empty sections only
    u32 bssAddress = 0;
    u32 bssSize = 0;
    u32 entryPoint = 0;
    std::vector<u8> bytes;
};

// Reads and validates the header; returns false and sets err on failure.
bool parse_dol(const std::vector<u8>& bytes, DolImage& out, std::string& err);

// Clears BSS and copies every section into guest memory.
void load_dol(const DolImage& dol, WiiMemory& mem);

bool read_file(const std::string& path, std::vector<u8>& out);

}  // namespace g2c
