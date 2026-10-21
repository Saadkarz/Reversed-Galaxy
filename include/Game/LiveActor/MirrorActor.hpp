#pragma once

#include "Game/LiveActor/LiveActor.hpp"

class MirrorActor : public LiveActor {
public:
    MirrorActor(LiveActor*, const char*, const char*);

    virtual void init(const JMapInfoIter&);
    virtual void movement();
    virtual void calcAnim();
    virtual void calcViewAndEntry();
    virtual ~MirrorActor();

    bool isHostInTheOtherSideOfMirror() const;
    TVec3f getHostCenterPos() const;

    /* 0x90 */ LiveActor* mHost;
    /* 0x94 */ TVec3f mCenter;
    /* 0xA0 */ f32 mRadius;
    /* 0xA4 */ bool mIsDisconnected;
};
