#pragma once

#include "Game/LiveActor/LiveActor.hpp"

class TubeSlider;

class HanachanRunaway : public LiveActor {
public:
    HanachanRunaway(TubeSlider* pSlider);

    /* 0x90 */ TubeSlider* mSlider;
    /* 0x94 */ s32 _94;
    /* 0x98 */ bool _98;
    /* 0x9C */ s32 _9C;
    /* 0xA0 */ s32 _A0;
    /* 0xA4 */ TVec3f _A4;
    /* 0xB0 */ f32 _B0;
    /* 0xB4 */ f32 _B4;
    /* 0xB8 */ s32 _B8;
    /* 0xBC */ s32 _BC;
    /* 0xC0 */ bool _C0;
    /* 0xC4 */ f32 _C4;
};
