#pragma once

#include "Game/LiveActor/LiveActor.hpp"

class TubeSlider;

class TubeSliderEnemy : public LiveActor {
public:
    TubeSliderEnemy(TubeSlider* pSlider);

    virtual void init(const JMapInfoIter& rIter);
    virtual void initAfterPlacement();
    virtual void control();

    /* 0x90 */ TubeSlider* mSlider;
    /* 0x94 */ TVec3f _94;
    /* 0xA0 */ TVec3f _A0;
    /* 0xAC */ s32 _AC;
    /* 0xB0 */ s32 _B0;
    /* 0xB4 */ bool _B4;
    /* 0xB8 */ f32 _B8;
};
