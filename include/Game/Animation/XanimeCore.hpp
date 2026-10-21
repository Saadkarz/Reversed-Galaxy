#pragma once

#include "Game/Animation/XjointTransform.hpp"

class XanimeCore {
public:
    /* 0x00 */ u8 _0[0x14];
    /* 0x14 */ XjointTransform* mTransformList;
};
