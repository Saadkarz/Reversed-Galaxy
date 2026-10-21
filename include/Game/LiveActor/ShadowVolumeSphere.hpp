#pragma once

#include "Game/LiveActor/ShadowVolumeModel.hpp"

__declspec(weak) void __force_sdata2_order() {
    (void)0.0f;
}

class ShadowVolumeSphere : public ShadowVolumeModel {
public:
    ShadowVolumeSphere();

    virtual ~ShadowVolumeSphere();
    virtual void loadModelDrawMtx() const;
    virtual bool isDraw() const;

    void setRadius(f32);

    /* 0x20 */ f32 mRadius;
};
