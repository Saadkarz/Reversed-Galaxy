#include "Game/LiveActor/PartsModel.hpp"
#include "Game/LiveActor/LodCtrl.hpp"
#include "Game/NameObj/NameObjExecuteHolder.hpp"
#include "Game/Scene/SceneFunction.hpp"
#include "Game/Util/ActorInitUtil.hpp"
#include "Game/Util/ActorSensorUtil.hpp"
#include "Game/Util/FixedPosition.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/ObjUtil.hpp"

PartsModel::PartsModel(LiveActor* pActor, const char* pName, const char* pModelName, MtxPtr pMtx, int drawBufferType, bool a6)
    : LiveActor(pName), mHost(pActor), mFixedPos(nullptr), mMtx(pMtx), mCalcOwnMatrix(true), mCheckHiddenHost(false), mIsDead(false) {
    if (mMtx != nullptr) {
        mPosition.set< f32 >(mMtx[0][3], mMtx[1][3], mMtx[2][3]);
    } else {
        mPosition.set(pActor->mPosition);
    }

    mRotation.set(pActor->mRotation);
    mScale.set(pActor->mScale);

    if (pModelName == nullptr) {
        return;
    }

    if (!MR::initActor(this, pModelName, a6)) {
        if (drawBufferType < 0) {
            drawBufferType = 9;
        }

        u32 movementType = 42;
        u32 calcAnimType = 11;

        if (static_cast<u32>(drawBufferType - 22) <= 2) {
            movementType = 37;
            calcAnimType = 10;
        }

        if (drawBufferType == 17 || drawBufferType == 28) {
            movementType = 39;
            calcAnimType = 6;
        }

        MR::connectToScene(this, movementType, calcAnimType, drawBufferType, MR::DrawType_None);
    }
}

void PartsModel::init(const JMapInfoIter& rIter) {
    if (mEffectKeeper == nullptr) {
        initEffectKeeper(8, nullptr, false);
    }

    if (mSoundHolder == nullptr) {
        initSound(8, nullptr, nullptr, TVec3f(0.0f));
    }

    MR::invalidateClipping(this);
    makeActorAppeared();
}

void PartsModel::makeActorAppeared() {
    LiveActor::makeActorAppeared();

    mIsDead = false;
}

void PartsModel::makeActorDead() {
    LiveActor::makeActorDead();

    mIsDead = true;
}

void PartsModel::movement() {
    if (MR::isDead(this) || MR::isDead(mHost) || MR::isClipped(mHost) || !mCheckHiddenHost && MR::isHiddenModel(mHost)) {
        if (!mIsDead) {
            mIsDead = true;

            MR::invalidateHitSensors(this);

            if (!MR::isHiddenModel(this)) {
                MR::disconnectToDrawTemporarily(this);
            }
        }
    } else {
        if (mIsDead) {
            mIsDead = false;

            MR::validateHitSensors(this);

            if (!MR::isHiddenModel(this)) {
                MR::connectToDrawTemporarily(this);
            }
        }

        LiveActor::movement();
    }
}

void PartsModel::calcAnim() {
    if (mIsDead || MR::isDead(this) || MR::isNoCalcAnim(this) || MR::isClipped(this)) {
        return;
    }

    if (isInitFixedPosition()) {
        mFixedPos->calc();
    }

    LiveActor::calcAnim();
}

void PartsModel::calcViewAndEntry() {
    if (mIsDead) {
        return;
    }

    LiveActor::calcViewAndEntry();
}

void PartsModel::initFixedPosition(const TVec3f& rLocalTrans, const TVec3f& rLocalRotate, const char* pJointName) {
    if (pJointName != nullptr) {
        mFixedPos = new FixedPosition(mHost, pJointName, rLocalTrans, rLocalRotate);
    } else {
        mFixedPos = new FixedPosition(mHost, rLocalTrans, rLocalRotate);
    }

    mMtx = mFixedPos->mMtx;
}

void PartsModel::initFixedPosition(const char* pJointName) {
    initFixedPosition(TVec3f(0.0f, 0.0f, 0.0f), TVec3f(0.0f, 0.0f, 0.0f), pJointName);
}

void PartsModel::initFixedPosition(MtxPtr pMtx, const TVec3f& rLocalTrans, const TVec3f& rLocalRotate) {
    mFixedPos = new FixedPosition(pMtx, rLocalTrans, rLocalRotate);
    mMtx = mFixedPos->mMtx;
}

void PartsModel::loadFixedPosition(const char* pJointName, const LiveActor* pActor) {
    mFixedPos = new FixedPosition(mHost, pJointName, pActor);
    mMtx = mFixedPos->mMtx;
}

void PartsModel::offFixedPosNormalizeScale() {
    mFixedPos->mNormalizeScale = false;
}

void PartsModel::calcAndSetBaseMtx() {
    if (mMtx != nullptr && mCalcOwnMatrix) {
        mPosition.set< f32 >(mMtx[0][3], mMtx[1][3], mMtx[2][3]);
        MR::setBaseTRMtx(this, mMtx);
    } else {
        LiveActor::calcAndSetBaseMtx();
    }
}

PartsModelLodCtrl::PartsModelLodCtrl(LiveActor* pHost, const char* pName, const char* pModelName, MtxPtr pMtx, s32 drawBufferType, bool a6)
    : PartsModel(pHost, pName, pModelName, pMtx, drawBufferType, a6), mLodCtrl(nullptr) {
}

void PartsModelLodCtrl::init(const JMapInfoIter& rIter) {
    PartsModel::init(rIter);
    mLodCtrl = MR::createLodCtrlNPC(this, rIter);
}

void PartsModelLodCtrl::control() {
    mLodCtrl->update();
}

LodCtrl* PartsModelLodCtrl::getLodCtrl() const {
    return mLodCtrl;
}

void PartsModelLodCtrl::initLightCtrl() {
    MR::initLightCtrl(this);
    if (mLodCtrl != nullptr) {
        mLodCtrl->initLightCtrl();
    }
}

void PartsModelLodCtrl::calcAndSetBaseMtx() {
    PartsModel::calcAndSetBaseMtx();
    if (mLodCtrl != nullptr) {
        mLodCtrl->syncJointAnimation();
    }
}

PartsModelLodCtrl::~PartsModelLodCtrl() {
}

