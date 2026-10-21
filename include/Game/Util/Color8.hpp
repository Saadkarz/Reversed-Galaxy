#pragma once

#include <revolution/gx/GXStruct.h>

class Color8 {
public:
    Color8(_GXColor);

    /* 0x00 */ u8 mR;
    /* 0x01 */ u8 mG;
    /* 0x02 */ u8 mB;
    /* 0x03 */ u8 mA;
};
