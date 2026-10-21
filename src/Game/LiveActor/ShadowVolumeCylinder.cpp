#define SHADOW_VOLUME_CYLINDER_TU
#include "Game/LiveActor/ShadowVolumeCylinder.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ShadowController.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include <revolution/gx.h>

namespace {
    const f32 sModelScale = 100.0f;
};  // namespace

ShadowVolumeCylinder::ShadowVolumeCylinder() : ShadowVolumeModel("影描画[ボリューム円柱]") {
    mRadius = 100.0f;
    initVolumeModel("ShadowVolumeCylinder");
}

inline ShadowVolumeModel::~ShadowVolumeModel() {
}



void ShadowVolumeCylinder::setRadius(f32 radius) {
    mRadius = radius;
}

void ShadowVolumeCylinder::loadModelDrawMtx() const {
    ShadowController* controller = getController();
    TVec3f position;
    calcBaseDropPosition(&position);
    TVec3f direction;
    controller->getDropDir(&direction);
    TVec3f up(-direction);
    TPos3f mtx;
    MR::makeMtxUpNoSupportPos(&mtx, up, position);

    f32 radius = mRadius / ::sModelScale;
    if (controller->isFollowHostScale()) {
        radius *= controller->getHost()->mScale.x;
    }

    TVec3f scale(radius, calcBaseDropLength() / ::sModelScale, radius);
    MR::preScaleMtx(mtx.toMtxPtr(), scale);
    PSMTXConcat(MR::getCameraViewMtx(), mtx.toMtxPtr(), mtx.toMtxPtr());
    GXLoadPosMtxImm(mtx.toMtxPtr(), 0);
}

ShadowVolumeCylinder::~ShadowVolumeCylinder() {
}
