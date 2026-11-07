#include "smoke_test.hpp"

#include "dispatch.hpp"

#include <cstring>

namespace g2c {

namespace {

// Scratch areas high in MEM1, well above main.dol's sections and BSS.
constexpr u32 kStackTop = 0x81700000;
constexpr u32 kBufA = 0x81200000;
constexpr u32 kBufB = 0x81210000;

u32 find_symbol(const char* name) {
    for (std::size_t i = 0; i < g2c_symbol_count; i++) {
        if (std::strcmp(g2c_symbols[i].name, name) == 0) {
            return g2c_symbols[i].addr;
        }
    }
    return 0;
}

bool call(WiiMemory& mem, const char* name, u32 r3, u32 r4, u32 r5, u32& ret, std::string& why) {
    const u32 addr = find_symbol(name);
    if (addr == 0 || lookup_func(addr) == nullptr) {
        why = "not lifted in this build";
        return false;
    }
    CpuContext c(mem);
    c.gpr[1] = kStackTop;
    c.gpr[3] = r3;
    c.gpr[4] = r4;
    c.gpr[5] = r5;
    c.lr = 0;
    lookup_func(addr)(c);
    ret = c.gpr[3];
    return true;
}

}  // namespace

std::vector<SmokeResult> run_smoke_tests(WiiMemory& mem) {
    std::vector<SmokeResult> out;
    u32 ret = 0;

    {
        SmokeResult r{"strlen(\"Galaxy2Coop\")"};
        const char* s = "Galaxy2Coop";
        mem.copy_in(kBufA, s, static_cast<u32>(std::strlen(s) + 1));
        if (call(mem, "strlen", kBufA, 0, 0, ret, r.detail)) {
            r.pass = ret == std::strlen(s);
            r.detail = "returned " + std::to_string(ret);
        }
        out.push_back(r);
    }
    {
        SmokeResult r{"memset(buf, 0xA5, 300)"};
        mem.fill(kBufA, 0, 512);
        if (call(mem, "memset", kBufA, 0xA5, 300, ret, r.detail)) {
            bool ok = ret == kBufA;
            for (u32 i = 0; i < 512 && ok; i++) {
                ok = mem.read8(kBufA + i) == (i < 300 ? 0xA5 : 0x00);
            }
            r.pass = ok;
            r.detail = ok ? "300 bytes set, guard bytes intact" : "buffer contents wrong";
        }
        out.push_back(r);
    }
    {
        SmokeResult r{"memcpy(dst, src, 1000)"};
        for (u32 i = 0; i < 1024; i++) {
            mem.write8(kBufA + i, static_cast<u8>(i * 7 + 3));
            mem.write8(kBufB + i, 0xEE);
        }
        if (call(mem, "memcpy", kBufB, kBufA + 1, 1000, ret, r.detail)) {
            bool ok = ret == kBufB;
            for (u32 i = 0; i < 1024 && ok; i++) {
                const u8 want = i < 1000 ? static_cast<u8>((i + 1) * 7 + 3) : 0xEE;
                ok = mem.read8(kBufB + i) == want;
            }
            r.pass = ok;
            r.detail = ok ? "1000 unaligned bytes copied, tail intact" : "buffer contents wrong";
        }
        out.push_back(r);
    }
    return out;
}

}  // namespace g2c
