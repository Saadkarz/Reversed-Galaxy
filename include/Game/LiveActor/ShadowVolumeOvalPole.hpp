#pragma once

#include "Game/LiveActor/ShadowVolumeModel.hpp"

class ShadowVolumeOvalPole : public ShadowVolumeModel {
public:
    ShadowVolumeOvalPole();

    virtual ~ShadowVolumeOvalPole();
    virtual void loadModelDrawMtx() const;

    void setSize(const TVec3f&);

    /* 0x24 */ TVec3f mSize;
};

__declspec(weak) void __force_sdata2_order() {
    (void)1.0f;
    (void)0.0f;
    (void)100.0f;
    (void)200.0f;
    (void)0.01f;
}
