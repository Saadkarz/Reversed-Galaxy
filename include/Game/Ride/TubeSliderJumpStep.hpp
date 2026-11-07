#pragma once

#include "Game/LiveActor/LiveActor.hpp"

class TubeSliderJumpStep : public LiveActor {
public:
    TubeSliderJumpStep(const TVec3f& rFront);

    virtual void init(const JMapInfoIter& rIter);
    virtual void calcAndSetBaseMtx();
    virtual void attackSensor(HitSensor* pSender, HitSensor* pReceiver);

    void exeWait();
    void exeJump();

    /* 0x90 */ TVec3f mFront;
};
