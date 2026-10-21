#include "Game/LiveActor/ShadowVolumeFlatModel.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ShadowController.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/ModelUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include <JSystem/J3DGraphAnimator/J3DJoint.hpp>
#include <JSystem/J3DGraphAnimator/J3DModelData.hpp>

ShadowVolumeFlatModel::ShadowVolumeFlatModel(const char* pModelName)
    : ShadowVolumeModel("板状シャドウボリューム描画"), mRootDrawMtxIndex(-1), mDropDrawMtxIndex(-1) {
    initVolumeModel(pModelName);
    initJointDrawMtxResister();
}

ShadowVolumeFlatModel::ShadowVolumeFlatModel()
    : ShadowVolumeModel("板状シャドウボリューム描画"), mRootDrawMtxIndex(-1), mDropDrawMtxIndex(-1) {
}

void ShadowVolumeFlatModel::initModel(const char* pModelName) {
    initVolumeModel(pModelName);
    initJointDrawMtxResister();
}

void ShadowVolumeFlatModel::initJointDrawMtxResister() {
    J3DJoint* root = mModelData->getJointTree().getRootNode();
    u16 rootIndex = root->getJntNo();
    u16 dropIndex = root->getChild()->getJntNo();
    mRootDrawMtxIndex = MR::findPosNrmMtxIndexFromModel(mModelData, rootIndex);
    mDropDrawMtxIndex = MR::findPosNrmMtxIndexFromModel(mModelData, dropIndex);
}

void ShadowVolumeFlatModel::draw() const {
    if (getController()->isDraw()) {
        ShadowVolumeDrawer::draw();
    }
}

void ShadowVolumeFlatModel::loadModelDrawMtx() const {
    TPos3f rootMtx;
    TPos3f dropMtx;
    TVec3f displacement;
    TVec3f position;
    TVec3f rootUp;
    TVec3f dropUp;

    ShadowController* controller = getController();
    controller->getDropDir(&displacement);
    displacement.scale(calcBaseDropLength());

    controller->getBaseMtx(rootMtx.toMtxPtr());
    calcBaseDropPosition(&position);
    rootMtx.setTrans(position);

    dropMtx.set(rootMtx);

    rootMtx.getYDir(rootUp);
    if (rootUp.dot(displacement) >= 0.0f) {
        MR::addTransMtx(rootMtx.toMtxPtr(), displacement);
    }
    if (controller->isFollowHostScale()) {
        MR::preScaleMtx(rootMtx.toMtxPtr(), controller->getHost()->mScale);
    }

    PSMTXConcat(MR::getCameraViewMtx(), rootMtx.toMtxPtr(), rootMtx.toMtxPtr());
    GXLoadPosMtxImm(rootMtx.toMtxPtr(), mRootDrawMtxIndex);

    dropMtx.getYDir(dropUp);
    if (dropUp.dot(displacement) < 0.0f) {
        MR::addTransMtx(dropMtx.toMtxPtr(), displacement);
    }
    if (controller->isFollowHostScale()) {
        MR::preScaleMtx(dropMtx.toMtxPtr(), controller->getHost()->mScale);
    }

    PSMTXConcat(MR::getCameraViewMtx(), dropMtx.toMtxPtr(), dropMtx.toMtxPtr());
    GXLoadPosMtxImm(dropMtx.toMtxPtr(), mDropDrawMtxIndex);
}

ShadowVolumeFlatModel::~ShadowVolumeFlatModel() {
}
