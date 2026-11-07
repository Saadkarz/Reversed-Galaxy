#pragma once

#include "Game/Screen/LayoutActor.hpp"

class SubMeterLayout : public LayoutActor {
public:
    SubMeterLayout(const char*, const char*);

    virtual void init(const JMapInfoIter&);
    virtual void control();

    void setLifeRatio(f32);
    void requestDeactivate();
    void requestAppear();
    void requestFrameIn();
    void requestFrameOut();

    /* 0x28 */ u32 _28;
    /* 0x2C */ u8 _2C;
    /* 0x2D */ u8 _2D;
    /* 0x2E */ u16 _2E;
    /* 0x30 */ u16 _30;
    /* 0x32 */ u16 _32;
};
