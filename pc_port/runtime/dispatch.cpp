#include "dispatch.hpp"

#include <cstdio>
#include <cstdlib>
#include <vector>

namespace g2c {

namespace {

std::vector<GuestFunc>& table() {
    static std::vector<GuestFunc> t((kCodeEnd - kCodeBase) / 4, nullptr);
    return t;
}

std::size_t g_count = 0;

bool inRange(u32 addr) { return addr >= kCodeBase && addr < kCodeEnd && (addr & 3) == 0; }

}  // namespace

void register_func(u32 addr, GuestFunc fn) {
    if (!inRange(addr)) {
        std::fprintf(stderr, "[g2c] register_func: address 0x%08X outside code range\n", addr);
        std::abort();
    }
    GuestFunc& slot = table()[(addr - kCodeBase) / 4];
    if (slot == nullptr) {
        g_count++;
    }
    slot = fn;
}

GuestFunc lookup_func(u32 addr) { return inRange(addr) ? table()[(addr - kCodeBase) / 4] : nullptr; }

std::size_t registered_func_count() { return g_count; }

void call_indirect(CpuContext& c, u32 addr) {
    GuestFunc fn = lookup_func(addr);
    if (fn == nullptr) {
        std::fprintf(stderr, "[g2c] call to unlifted guest address 0x%08X (lr=0x%08X)\n", addr, c.lr);
        std::abort();
    }
    fn(c);
}

void unimplemented(CpuContext& c, u32 addr, u32 raw) {
    std::fprintf(stderr, "[g2c] unimplemented instruction 0x%08X at 0x%08X (lr=0x%08X)\n", raw, addr, c.lr);
    std::abort();
}

}  // namespace g2c
