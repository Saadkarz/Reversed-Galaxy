#include "Game/LiveActor/ShadowVolumeOvalPole.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/MathUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include <revolution/gx.h>

ShadowVolumeOvalPole::ShadowVolumeOvalPole() : ShadowVolumeModel("影描画[ボリューム楕円柱]") {
    mSize.x = 100.0f;
    mSize.y = 100.0f;
    mSize.z = 200.0f;
    initVolumeModel("ShadowVolumeCylinder");
}

void ShadowVolumeOvalPole::loadModelDrawMtx() const {
    ShadowController* controller = getController();
    TPos3f scaledMtx;
    TPos3f inverseMtx;
    TPos3f mtx;
    TVec3f position;
    calcBaseDropPosition(&position);
    TVec3f direction;
    controller->getDropDir(&direction);
    f32 modelScale = 100.0f;
    direction.negate();
    TVec3f size((const Vec&)mSize);
    size.scale(1.0f / modelScale);

    if (size.x <= 0.01f) {
        size.x = 0.01f;
    }
    if (size.y <= 0.01f) {
        size.y = 0.01f;
    }
    if (size.z <= 0.01f) {
        size.z = 0.01f;
    }

    if (controller->isFollowHostScale()) {
        size *= controller->getHost()->mScale;
    }

    controller->getBaseMtx(scaledMtx.toMtxPtr());
    scaledMtx.setTrans(TVec3f(0.0f, 0.0f, 0.0f));
    MR::preScaleMtx(scaledMtx.toMtxPtr(), size);
    inverseMtx.invert(scaledMtx);
    TVec3f localDirection;
    inverseMtx.mult(direction, localDirection);
    mtx.identity();
    MR::makeMtxUpNoSupport(&mtx, localDirection);
    mtx.concat(scaledMtx, mtx);
    mtx.setTrans(position);

    TVec3f side;
    TVec3f up;
    TVec3f front;
    mtx.getXDir(side);
    mtx.getYDir(up);
    mtx.getZDir(front);
    if (!MR::normalizeOrZero(&up)) {
        side.orthogonalize(up);
        front.orthogonalize(up);
    }

    up.scale(calcBaseDropLength() / 100.0f);
    mtx.setXDir(side);
    mtx.setYDir(up);
    mtx.setZDir(front);
    PSMTXConcat(MR::getCameraViewMtx(), mtx.toMtxPtr(), mtx.toMtxPtr());
    GXLoadPosMtxImm(mtx.toMtxPtr(), 0);
}

void ShadowVolumeOvalPole::setSize(const TVec3f& rSize) {
    mSize = rSize;
}

ShadowVolumeOvalPole::~ShadowVolumeOvalPole() {
}
