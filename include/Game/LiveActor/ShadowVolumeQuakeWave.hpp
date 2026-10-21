#pragma once

#include "Game/LiveActor/ShadowVolumeDrawer.hpp"

class LiveActor;

class ShadowVolumeQuakeWave : public ShadowVolumeDrawer {
public:
    ShadowVolumeQuakeWave(LiveActor*);

    virtual ~ShadowVolumeQuakeWave();
    virtual void loadModelDrawMtx() const;
    virtual void drawShape() const;
    virtual bool isDraw() const;

    /* 0x24 */ LiveActor* mHost;
    /* 0x28 */ MtxPtr mMtx;
    /* 0x2C */ f32 mScale;
    /* 0x30 */ f32 mAngle;
    /* 0x34 */ f32 mWidth;
};
