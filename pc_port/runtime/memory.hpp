#pragma once

// Flat host-side model of the Wii's physical RAM as seen through the
// PowerPC's default BAT mappings:
//   MEM1  24 MiB  0x80000000-0x817FFFFF (cached)   0xC0000000-0xC17FFFFF (uncached)
//   MEM2  64 MiB  0x90000000-0x93FFFFFF (cached)   0xD0000000-0xD3FFFFFF (uncached)
// All multi-byte accessors are big-endian, like the guest.

#include <bit>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>

#if defined(_MSC_VER)
#include <stdlib.h>
#endif

namespace g2c {

using u8 = std::uint8_t;
using u16 = std::uint16_t;
using u32 = std::uint32_t;
using u64 = std::uint64_t;
using s8 = std::int8_t;
using s16 = std::int16_t;
using s32 = std::int32_t;
using s64 = std::int64_t;
using f32 = float;
using f64 = double;

inline u16 bswap16(u16 v) {
#if defined(_MSC_VER)
    return _byteswap_ushort(v);
#else
    return __builtin_bswap16(v);
#endif
}

inline u32 bswap32(u32 v) {
#if defined(_MSC_VER)
    return _byteswap_ulong(v);
#else
    return __builtin_bswap32(v);
#endif
}

inline u64 bswap64(u64 v) {
#if defined(_MSC_VER)
    return _byteswap_uint64(v);
#else
    return __builtin_bswap64(v);
#endif
}

class WiiMemory {
public:
    static constexpr u32 MEM1_SIZE = 24u * 1024 * 1024;
    static constexpr u32 MEM2_SIZE = 64u * 1024 * 1024;

    WiiMemory() : mMem1(new u8[MEM1_SIZE]()), mMem2(new u8[MEM2_SIZE]()) {}

    WiiMemory(const WiiMemory&) = delete;
    WiiMemory& operator=(const WiiMemory&) = delete;

    // Returns true if [addr, addr+len) lies inside one mapped region.
    bool isMapped(u32 addr, u32 len = 1) const {
        u32 off;
        u32 size;
        return region(addr, off, size) != nullptr && off + len <= size && off + len >= off;
    }

    // Host pointer for a guest address; faults on unmapped addresses.
    u8* translate(u32 addr) {
        u32 off;
        u32 size;
        u8* base = region(addr, off, size);
        if (base == nullptr) {
            fault(addr);
        }
        return base + off;
    }

    const u8* translate(u32 addr) const { return const_cast<WiiMemory*>(this)->translate(addr); }

    u8 read8(u32 a) const { return *translate(a); }
    u16 read16(u32 a) const { return bswap16(load<u16>(a)); }
    u32 read32(u32 a) const { return bswap32(load<u32>(a)); }
    u64 read64(u32 a) const { return bswap64(load<u64>(a)); }
    f32 read_f32(u32 a) const { return std::bit_cast<f32>(read32(a)); }
    f64 read_f64(u32 a) const { return std::bit_cast<f64>(read64(a)); }

    void write8(u32 a, u8 v) { *translate(a) = v; }
    void write16(u32 a, u16 v) { store<u16>(a, bswap16(v)); }
    void write32(u32 a, u32 v) { store<u32>(a, bswap32(v)); }
    void write64(u32 a, u64 v) { store<u64>(a, bswap64(v)); }
    void write_f32(u32 a, f32 v) { write32(a, std::bit_cast<u32>(v)); }
    void write_f64(u32 a, f64 v) { write64(a, std::bit_cast<u64>(v)); }

    void copy_in(u32 dst, const void* src, u32 len) {
        if (len == 0) {
            return;
        }
        check(dst, len);
        std::memcpy(translate(dst), src, len);
    }

    void copy_out(void* dst, u32 src, u32 len) const {
        if (len == 0) {
            return;
        }
        check(src, len);
        std::memcpy(dst, translate(src), len);
    }

    void fill(u32 dst, u8 value, u32 len) {
        if (len == 0) {
            return;
        }
        check(dst, len);
        std::memset(translate(dst), value, len);
    }

    [[noreturn]] static void fault(u32 addr) {
        std::fprintf(stderr, "[g2c] guest memory fault: unmapped address 0x%08X\n", addr);
        std::abort();
    }

private:
    // Region lookup by the top nibble: 8/C -> MEM1, 9/D -> MEM2.
    u8* region(u32 addr, u32& off, u32& size) const {
        switch (addr >> 28) {
        case 0x8:
        case 0xC:
            off = addr & 0x0FFFFFFF;
            size = MEM1_SIZE;
            return off < MEM1_SIZE ? mMem1.get() : nullptr;
        case 0x9:
        case 0xD:
            off = addr & 0x0FFFFFFF;
            size = MEM2_SIZE;
            return off < MEM2_SIZE ? mMem2.get() : nullptr;
        default:
            return nullptr;
        }
    }

    void check(u32 addr, u32 len) const {
        if (!isMapped(addr, len)) {
            fault(addr);
        }
    }

    template <typename T>
    T load(u32 a) const {
        T v;
        std::memcpy(&v, translate(a), sizeof(T));
        return v;
    }

    template <typename T>
    void store(u32 a, T v) {
        std::memcpy(translate(a), &v, sizeof(T));
    }

    std::unique_ptr<u8[]> mMem1;
    std::unique_ptr<u8[]> mMem2;
};

}  // namespace g2c
