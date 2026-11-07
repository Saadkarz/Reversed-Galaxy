#pragma once

// Minimal self-contained SHA-1 (FIPS 180-1), used to verify the user's main.dol.

#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace g2c {

inline std::string sha1_hex(const std::uint8_t* data, std::size_t len) {
    std::uint32_t h[5] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0};
    auto rol = [](std::uint32_t x, int n) { return (x << n) | (x >> (32 - n)); };

    std::vector<std::uint8_t> msg(data, data + len);
    const std::uint64_t bitLen = static_cast<std::uint64_t>(len) * 8;
    msg.push_back(0x80);
    while (msg.size() % 64 != 56) {
        msg.push_back(0);
    }
    for (int i = 7; i >= 0; i--) {
        msg.push_back(static_cast<std::uint8_t>(bitLen >> (i * 8)));
    }

    for (std::size_t chunk = 0; chunk < msg.size(); chunk += 64) {
        std::uint32_t w[80];
        for (int i = 0; i < 16; i++) {
            const std::uint8_t* p = &msg[chunk + i * 4];
            w[i] = (std::uint32_t(p[0]) << 24) | (std::uint32_t(p[1]) << 16) | (std::uint32_t(p[2]) << 8) | p[3];
        }
        for (int i = 16; i < 80; i++) {
            w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
        }
        std::uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4];
        for (int i = 0; i < 80; i++) {
            std::uint32_t f;
            std::uint32_t k;
            if (i < 20) {
                f = (b & c) | (~b & d);
                k = 0x5A827999;
            } else if (i < 40) {
                f = b ^ c ^ d;
                k = 0x6ED9EBA1;
            } else if (i < 60) {
                f = (b & c) | (b & d) | (c & d);
                k = 0x8F1BBCDC;
            } else {
                f = b ^ c ^ d;
                k = 0xCA62C1D6;
            }
            const std::uint32_t t = rol(a, 5) + f + e + k + w[i];
            e = d;
            d = c;
            c = rol(b, 30);
            b = a;
            a = t;
        }
        h[0] += a;
        h[1] += b;
        h[2] += c;
        h[3] += d;
        h[4] += e;
    }

    char out[41];
    for (int i = 0; i < 5; i++) {
        std::snprintf(out + i * 8, 9, "%08x", h[i]);
    }
    return std::string(out, 40);
}

}  // namespace g2c
