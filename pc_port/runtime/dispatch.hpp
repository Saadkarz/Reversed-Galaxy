#pragma once

// Address -> native function table for lifted guest code.

#include "cpu.hpp"

#include <cstddef>

namespace g2c {

using GuestFunc = void (*)(CpuContext&);

// Guest code lives in 0x80004000..0x80800000 (.init + .text of main.dol).
constexpr u32 kCodeBase = 0x80004000;
constexpr u32 kCodeEnd = 0x80800000;

void register_func(u32 addr, GuestFunc fn);
GuestFunc lookup_func(u32 addr);
std::size_t registered_func_count();

// Calls the lifted function at addr; aborts with a clear message if none exists.
void call_indirect(CpuContext& c, u32 addr);

// Trap for instructions the lifter does not translate yet.
[[noreturn]] void unimplemented(CpuContext& c, u32 addr, u32 raw);

struct SymbolEntry {
    const char* name;
    u32 addr;
};

}  // namespace g2c

// Emitted by tools/dol2cpp.py (or by recomp_stub.cpp when no DOL is available).
void g2c_register_all();
extern const g2c::SymbolEntry g2c_symbols[];
extern const std::size_t g2c_symbol_count;
extern const char* const g2c_lift_stats;
