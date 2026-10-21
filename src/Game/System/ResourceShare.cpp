#include "Game/System/ResourceShare.hpp"

namespace {
    char sResourceShareName[] = "資源共有機構";
}

ResourceShare::ResourceShare() : NameObj(sResourceShareName) {
    mBuffer1 = new u8[0x80];
    mBuffer2 = new u8[0x80];
    mUnk = 0;
}

ResourceShare::~ResourceShare() {
}
