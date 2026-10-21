#include "Game/LiveActor/ShadowVolumeQuakeWave.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include <revolution/gx.h>
#include <revolution/mtx.h>

namespace MR {
    f32 cosDegree(f32);
    f32 sinDegree(f32);
}

ShadowVolumeQuakeWave::ShadowVolumeQuakeWave(LiveActor* pHost)
    : ShadowVolumeDrawer(((void)0.0f, "影描画[クッパ地震衝撃波]")),
      mHost(pHost),
      mMtx(0),
      mScale(1000.0f),
      mAngle(0.0f),
      mWidth(2.5f) {
}

void ShadowVolumeQuakeWave::loadModelDrawMtx() const {
    TPos3f mtx;
    mtx.identity();
    if (mMtx) {
        mtx.set(mMtx);
    } else {
        mtx.set(mHost->getBaseMtx());
    }

    MR::preScaleMtx(mtx.toMtxPtr(), TVec3f(mScale));
    PSMTXConcat(MR::getCameraViewMtx(), mtx.toMtxPtr(), mtx.toMtxPtr());
    GXLoadPosMtxImm(mtx.toMtxPtr(), 0);
    GXSetCurrentMtx(0);
    GXClearVtxDesc();
    GXSetVtxDesc(GX_VA_POS, GX_DIRECT);
    GXSetVtxAttrFmt(GX_VTXFMT0, GX_VA_POS, GX_POS_XYZ, GX_F32, 0);
}

void ShadowVolumeQuakeWave::drawShape() const {
    f32 cos1 = MR::cosDegree(mAngle - mWidth);
    f32 cos2 = MR::cosDegree(mAngle + mWidth);
    f32 sin1 = MR::sinDegree(mAngle - mWidth);
    f32 sin2 = MR::sinDegree(mAngle + mWidth);

    for (int i = 0; i < 32; i++) {
        f32 theta1 = (360.0f * (f32)i) / 32.0f;
        f32 theta2 = (360.0f * (f32)(i + 1)) / 32.0f;
        f32 cosTheta1 = MR::cosDegree(theta1);
        f32 sinTheta1 = MR::sinDegree(theta1);
        f32 cosTheta2 = MR::cosDegree(theta2);
        f32 sinTheta2 = MR::sinDegree(theta2);

        GXBegin(GX_TRIANGLESTRIP, GX_VTXFMT0, 6);
        GXPosition3f32(0.0f, 0.0f, 0.0f);
        GXPosition3f32(sin1 * sinTheta2, cos1, sin1 * cosTheta2);
        GXPosition3f32(sin1 * sinTheta1, cos1, sin1 * cosTheta1);
        GXPosition3f32(sin2 * sinTheta2, cos2, sin2 * cosTheta2);
        GXPosition3f32(sin2 * sinTheta1, cos2, sin2 * cosTheta1);
        GXPosition3f32(0.0f, 0.0f, 0.0f);
    }
}

bool ShadowVolumeQuakeWave::isDraw() const {
    return MR::isValidDraw(mHost);
}

ShadowVolumeQuakeWave::~ShadowVolumeQuakeWave() {
}
