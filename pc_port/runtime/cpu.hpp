#pragma once

// Guest PowerPC (Broadway) register state shared by all lifted functions.

#include "memory.hpp"

#include <cmath>

namespace g2c {

struct PairedSingle {
    f64 ps0 = 0.0;  // also the scalar FPR value
    f64 ps1 = 0.0;
};

struct CpuContext {
    explicit CpuContext(WiiMemory& m) : mem(m) {}

    u32 gpr[32] = {};
    PairedSingle fpr[32] = {};
    u32 cr = 0;    // CR0 in bits 31..28 (big-endian bit 0 = MSB)
    u32 lr = 0;
    u32 ctr = 0;
    u32 xer = 0;   // SO = bit 31, OV = bit 30, CA = bit 29
    u32 fpscr = 0;
    u32 gqr[8] = {};
    u32 msr = 0;
    u32 spr[1024] = {};  // other SPRs (HID*, WPAR, DMA, ...), stored without side effects
    WiiMemory& mem;

    // --- CR helpers (field 0 is the most significant nibble) ---
    u32 crBit(u32 bi) const { return (cr >> (31 - bi)) & 1; }
    void setCrBit(u32 bi, u32 v) {
        const u32 m = 1u << (31 - bi);
        cr = v ? (cr | m) : (cr & ~m);
    }
    void setCrField(u32 field, u32 nibble) {
        const u32 sh = 28 - field * 4;
        cr = (cr & ~(0xFu << sh)) | ((nibble & 0xF) << sh);
    }
    u32 so() const { return (xer >> 31) & 1; }
    u32 ca() const { return (xer >> 29) & 1; }
    void setCa(u32 v) { xer = v ? (xer | (1u << 29)) : (xer & ~(1u << 29)); }

    // Signed compare -> LT GT EQ SO nibble.
    void cmpSigned(u32 field, s32 a, s32 b) { setCrField(field, (a < b ? 8 : a > b ? 4 : 2) | so()); }
    void cmpUnsigned(u32 field, u32 a, u32 b) { setCrField(field, (a < b ? 8 : a > b ? 4 : 2) | so()); }
    void recordCr0(u32 result) { cmpSigned(0, static_cast<s32>(result), 0); }

    void cmpFloat(u32 field, f64 a, f64 b) {
        u32 n;
        if (std::isnan(a) || std::isnan(b)) {
            n = 1;
        } else {
            n = a < b ? 8 : a > b ? 4 : 2;
        }
        setCrField(field, n);
    }
};

}  // namespace g2c
