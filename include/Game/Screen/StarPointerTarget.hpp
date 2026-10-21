#pragma once

#include <JSystem/JGeometry/TVec.hpp>

class LayoutActor;

class StarPointerTarget {
public:
    StarPointerTarget(f32, const TVec3f*, MtxPtr, TVec3f);

    bool calcScreenPosition(TVec2f*) const;
    bool isPointing(const TVec2f&, f32, f32) const;
    void calcPosition(TVec3f*) const;
    f32 calcRadius2d(f32, f32, f32) const;
    bool calcScreenPositionFromView(TVec2f*, const TVec3f&) const;

    /* 0x00 */ f32 mRadius3d;
    /* 0x04 */ TVec3f mOffset;
    /* 0x10 */ s32 mLastPointedChannel;
    /* 0x14 */ const TVec3f* mPosition;
    /* 0x18 */ MtxPtr mMtx;
};
