#pragma once

#include "Game/NameObj/NameObj.hpp"

class PlayResultMarioFaceShipHolder : public NameObj {
public:
    PlayResultMarioFaceShipHolder();
    virtual ~PlayResultMarioFaceShipHolder();

    void reset();

    /* 0x12 */ bool _12;
    /* 0x13 */ bool _13;
    /* 0x14 */ bool _14;
    /* 0x18 */ s32 _18;
    /* 0x1C */ bool _1C;
};
