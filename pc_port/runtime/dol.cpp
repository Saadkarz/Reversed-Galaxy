#include "dol.hpp"

#include <fstream>

namespace g2c {

namespace {

u32 be32(const std::vector<u8>& b, std::size_t off) {
    return (u32(b[off]) << 24) | (u32(b[off + 1]) << 16) | (u32(b[off + 2]) << 8) | u32(b[off + 3]);
}

}  // namespace

bool read_file(const std::string& path, std::vector<u8>& out) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        return false;
    }
    const std::streamsize n = f.tellg();
    f.seekg(0);
    out.resize(static_cast<std::size_t>(n));
    return n == 0 || static_cast<bool>(f.read(reinterpret_cast<char*>(out.data()), n));
}

bool parse_dol(const std::vector<u8>& bytes, DolImage& out, std::string& err) {
    constexpr std::size_t kHeader = 0x100;
    if (bytes.size() < kHeader) {
        err = "file is too small to be a DOL";
        return false;
    }
    out = DolImage{};
    // 7 text + 11 data sections: offsets at 0x00, addresses at 0x48, sizes at 0x90.
    for (int i = 0; i < 18; i++) {
        DolSection s;
        s.isText = i < 7;
        s.fileOffset = be32(bytes, 0x00 + i * 4);
        s.address = be32(bytes, 0x48 + i * 4);
        s.size = be32(bytes, 0x90 + i * 4);
        if (s.size == 0) {
            continue;
        }
        if (std::size_t(s.fileOffset) + s.size > bytes.size()) {
            err = "section " + std::to_string(i) + " runs past the end of the file";
            return false;
        }
        out.sections.push_back(s);
    }
    out.bssAddress = be32(bytes, 0xD8);
    out.bssSize = be32(bytes, 0xDC);
    out.entryPoint = be32(bytes, 0xE0);
    if (out.sections.empty()) {
        err = "DOL has no sections";
        return false;
    }
    out.bytes = bytes;
    return true;
}

void load_dol(const DolImage& dol, WiiMemory& mem) {
    if (dol.bssSize != 0) {
        mem.fill(dol.bssAddress, 0, dol.bssSize);
    }
    for (const DolSection& s : dol.sections) {
        mem.copy_in(s.address, dol.bytes.data() + s.fileOffset, s.size);
    }
}

}  // namespace g2c
