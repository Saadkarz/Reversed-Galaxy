#pragma once

#include <JSystem/JGeometry/TVec.hpp>

class XjointTransform {
public:
    XjointTransform();

    /* 0x00 */ u32 _0;
    /* 0x04 */ u16 _4;
    /* 0x08 */ TVec3f mScale;
    /* 0x14 */ TVec3f _14;
};
