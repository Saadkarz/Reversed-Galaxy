#pragma once

#include "Game/Animation/XanimeCore.hpp"

class XanimePlayer {
public:
    XanimeCore* getCore() const { return mCore; }

    /* 0x00 */ u8 _0[0x6C];
    /* 0x6C */ XanimeCore* mCore;
};
