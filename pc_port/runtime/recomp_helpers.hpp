#pragma once

// Helpers used by code that tools/dol2cpp.py generates.

#include "dispatch.hpp"

#include <bit>
#include <chrono>
#include <climits>
#include <cmath>

namespace g2c {

inline u32 rotl32(u32 v, u32 n) { return std::rotl(v, static_cast<int>(n & 31)); }

// a + b + carry_in, returning the low word and the carry out.
inline u32 add_carry(CpuContext& c, u32 a, u32 b, u32 cin) {
    const u64 t = static_cast<u64>(a) + b + cin;
    c.setCa(static_cast<u32>(t >> 32));
    return static_cast<u32>(t);
}

inline u32 sraw(CpuContext& c, u32 v, u32 sh) {
    const s32 s = static_cast<s32>(v);
    if (sh & 0x20) {
        c.setCa(s < 0 ? 1 : 0);
        return s < 0 ? 0xFFFFFFFFu : 0;
    }
    sh &= 31;
    const u32 lost = sh ? (v & ((1u << sh) - 1)) : 0;
    c.setCa((s < 0 && lost) ? 1 : 0);
    return static_cast<u32>(s >> sh);
}

inline u32 divw(u32 a, u32 b) {
    const s32 sa = static_cast<s32>(a);
    const s32 sb = static_cast<s32>(b);
    if (sb == 0 || (sa == INT_MIN && sb == -1)) {
        return sa < 0 ? 0xFFFFFFFFu : 0;
    }
    return static_cast<u32>(sa / sb);
}

inline u32 divwu(u32 a, u32 b) { return b == 0 ? 0 : a / b; }

inline u32 mulhw(u32 a, u32 b) {
    return static_cast<u32>((static_cast<s64>(static_cast<s32>(a)) * static_cast<s32>(b)) >> 32);
}

inline u32 mulhwu(u32 a, u32 b) { return static_cast<u32>((static_cast<u64>(a) * b) >> 32); }

inline f64 to_single(f64 v) { return static_cast<f64>(static_cast<f32>(v)); }

// fctiw/fctiwz: saturate to s32 and place the result in the low word of the FPR bits.
inline f64 fctiw(f64 v, bool truncate) {
    s32 r;
    if (std::isnan(v)) {
        r = INT_MIN;
    } else if (v >= 2147483647.0) {
        r = INT_MAX;
    } else if (v <= -2147483648.0) {
        r = INT_MIN;
    } else {
        r = static_cast<s32>(truncate ? std::trunc(v) : std::nearbyint(v));
    }
    return std::bit_cast<f64>(0xFFF8000000000000ull | static_cast<u32>(r));
}

inline u32 fpr_low_word(f64 v) { return static_cast<u32>(std::bit_cast<u64>(v)); }

inline f64 frsqrte(f64 v) { return 1.0 / std::sqrt(v); }
inline f64 fres(f64 v) { return to_single(1.0 / v); }

// --- Paired-single quantized load/store (GQR LD/ST_TYPE: 0=f32 4=u8 5=u16 6=s8 7=s16) ---
inline f64 dequant(u32 raw, u32 type, u32 scale) {
    const f64 s = std::ldexp(1.0, -static_cast<int>(scale & 0x20 ? static_cast<s32>(scale) - 64 : static_cast<s32>(scale)));
    switch (type) {
    case 4: return static_cast<f64>(static_cast<u8>(raw)) * s;
    case 5: return static_cast<f64>(static_cast<u16>(raw)) * s;
    case 6: return static_cast<f64>(static_cast<s8>(raw)) * s;
    case 7: return static_cast<f64>(static_cast<s16>(raw)) * s;
    default: return static_cast<f64>(std::bit_cast<f32>(raw));
    }
}

inline u32 typeSize(u32 type) {
    switch (type) {
    case 4:
    case 6: return 1;
    case 5:
    case 7: return 2;
    default: return 4;
    }
}

inline void psq_load(CpuContext& c, u32 frd, u32 ea, u32 w, u32 i) {
    const u32 gqr = c.gqr[i];
    const u32 type = (gqr >> 16) & 7;
    const u32 scale = (gqr >> 24) & 0x3F;
    const u32 sz = typeSize(type);
    auto rd = [&](u32 a) -> u32 {
        switch (sz) {
        case 1: return c.mem.read8(a);
        case 2: return c.mem.read16(a);
        default: return c.mem.read32(a);
        }
    };
    c.fpr[frd].ps0 = dequant(rd(ea), type, scale);
    c.fpr[frd].ps1 = w ? 1.0 : dequant(rd(ea + sz), type, scale);
}

inline u32 quant(f64 v, u32 type, u32 scale) {
    const f64 s = std::ldexp(1.0, static_cast<int>(scale & 0x20 ? static_cast<s32>(scale) - 64 : static_cast<s32>(scale)));
    auto clampTo = [](f64 x, f64 lo, f64 hi) { return x < lo ? lo : (x > hi ? hi : x); };
    switch (type) {
    case 4: return static_cast<u32>(static_cast<u8>(clampTo(v * s, 0.0, 255.0)));
    case 5: return static_cast<u32>(static_cast<u16>(clampTo(v * s, 0.0, 65535.0)));
    case 6: return static_cast<u32>(static_cast<u8>(static_cast<s8>(clampTo(v * s, -128.0, 127.0))));
    case 7: return static_cast<u32>(static_cast<u16>(static_cast<s16>(clampTo(v * s, -32768.0, 32767.0))));
    default: return std::bit_cast<u32>(static_cast<f32>(v));
    }
}

inline void psq_store(CpuContext& c, u32 frs, u32 ea, u32 w, u32 i) {
    const u32 gqr = c.gqr[i];
    const u32 type = gqr & 7;
    const u32 scale = (gqr >> 8) & 0x3F;
    const u32 sz = typeSize(type);
    auto wr = [&](u32 a, u32 v) {
        switch (sz) {
        case 1: c.mem.write8(a, static_cast<u8>(v)); break;
        case 2: c.mem.write16(a, static_cast<u16>(v)); break;
        default: c.mem.write32(a, v); break;
        }
    };
    wr(ea, quant(c.fpr[frs].ps0, type, scale));
    if (!w) {
        wr(ea + sz, quant(c.fpr[frs].ps1, type, scale));
    }
}

inline u32 timebase(bool upper) {
    // Broadway timebase runs at bus clock / 4 = 60.75 MHz.
    using namespace std::chrono;
    static const auto start = steady_clock::now();
    const u64 ns = static_cast<u64>(duration_cast<nanoseconds>(steady_clock::now() - start).count());
    const u64 ticks = ns * 6075 / 100000;
    return upper ? static_cast<u32>(ticks >> 32) : static_cast<u32>(ticks);
}

inline void dcbz(CpuContext& c, u32 ea) { c.mem.fill(ea & ~31u, 0, 32); }

}  // namespace g2c
