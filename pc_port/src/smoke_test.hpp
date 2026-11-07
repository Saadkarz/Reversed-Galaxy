#pragma once

#include "memory.hpp"

#include <string>
#include <vector>

namespace g2c {

struct SmokeResult {
    std::string name;
    bool pass = false;
    std::string detail;
};

// Runs lifted retail MSL routines (strlen, memset, memcpy) against guest memory.
std::vector<SmokeResult> run_smoke_tests(WiiMemory& mem);

}  // namespace g2c
