#include "Game/LiveActor/ShadowVolumeSphere.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ShadowController.hpp"
#include "Game/Util.hpp"
#include <revolution/gx.h>

ShadowVolumeSphere::ShadowVolumeSphere() : ShadowVolumeModel("影描画[ボリューム球]"), mRadius(100.0f) {
    initVolumeModel("ShadowVolumeSphere");
}

void ShadowVolumeSphere::setRadius(f32 radius) {
    mRadius = radius;
}

bool ShadowVolumeSphere::isDraw() const {
    ShadowController* controller = getController();

    return controller->isProjected() && controller->isDraw();
}

void ShadowVolumeSphere::loadModelDrawMtx() const {
    ShadowController* controller = getController();
    f32 radius = mRadius / 100.0f;
    if (controller->isFollowHostScale()) {
        radius *= controller->getHost()->mScale.x;
    }

    TPos3f mtx;
    mtx.identity();
    mtx.mMtx[0][0] = radius;
    mtx.mMtx[0][1] = 0.0f;
    mtx.mMtx[0][2] = 0.0f;
    mtx.mMtx[1][0] = 0.0f;
    mtx.mMtx[1][1] = radius;
    mtx.mMtx[1][2] = 0.0f;
    mtx.mMtx[2][0] = 0.0f;
    mtx.mMtx[2][1] = 0.0f;
    mtx.mMtx[2][2] = radius;
    TVec3f position;
    controller->getProjectionPos(&position);
    mtx.setTrans(position);

    PSMTXConcat(MR::getCameraViewMtx(), mtx.toMtxPtr(), mtx.toMtxPtr());
    GXLoadPosMtxImm(mtx.toMtxPtr(), 0);
}

ShadowVolumeSphere::~ShadowVolumeSphere() {
}
