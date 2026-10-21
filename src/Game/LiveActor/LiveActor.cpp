#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ActorActionKeeper.hpp"
#include "Game/LiveActor/ActorLightCtrl.hpp"
#include "Game/LiveActor/ActorSoundHolder.hpp"
#include "Game/LiveActor/AllLiveActorGroup.hpp"
#include "Game/LiveActor/Binder.hpp"
#include "Game/LiveActor/ClippingDirector.hpp"
#include "Game/LiveActor/EffectKeeper.hpp"
#include "Game/LiveActor/HitSensor.hpp"
#include "Game/LiveActor/HitSensorKeeper.hpp"
#include "Game/LiveActor/ModelManager.hpp"
#include "Game/LiveActor/RailRider.hpp"
#include "Game/LiveActor/ShadowController.hpp"
#include "Game/LiveActor/Spine.hpp"
#include "Game/Map/StageSwitch.hpp"
#include "Game/NameObj/NameObjExecuteHolder.hpp"
#include "Game/Screen/StarPointerTarget.hpp"
#include "Game/Util/ActionSoundUtil.hpp"
#include "Game/Util/ActorMovementUtil.hpp"
#include "Game/Util/ActorSensorUtil.hpp"
#include "Game/Util/ActorShadowUtil.hpp"
#include "Game/Util/ActorSwitchUtil.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/ModelUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include <JSystem/J3DGraphAnimator/J3DModel.hpp>

LiveActor::LiveActor(const char* pName)
    : NameObj(((void)1.0f, (void)0.0f, (void)-1.0f, pName)), mPosition(0.0f, 0.0f, 0.0f), mRotation(0.0f, 0.0f, 0.0f), mScale(1.0f, 1.0f, 1.0f),
      mVelocity(0.0f, 0.0f, 0.0f), mGravity(0.0f, -1.0f, 0.0f), mActionKeeper(nullptr), mModelManager(nullptr),
      mSpine(nullptr), mSensorKeeper(nullptr), mBinder(nullptr), mRailRider(nullptr), mEffectKeeper(nullptr),
      mSoundHolder(nullptr), mFlags(), mShadowList(nullptr), mCollisionParts(nullptr), mSwitchCtrl(nullptr),
      mPointerTarget(nullptr), mLightCtrl(nullptr) {
    MR::getAllLiveActorGroup()->registerActor(this);
    MR::getClippingDirector()->registerActor(this);
}

void LiveActor::init(const JMapInfoIter&) {
}

void LiveActor::appear() {
    makeActorAppeared();
}

void LiveActor::makeActorAppeared() {
    if (mSensorKeeper != nullptr) {
        mSensorKeeper->validateBySystem();
    }

    mFlags.mIsDead = false;

    if (MR::isClipped(this)) {
        endClipped();
    }

    if (mCollisionParts != nullptr) {
        MR::validateCollisionParts(this);
    }

    MR::resetPosition(this);

    if (mLightCtrl != nullptr) {
        mLightCtrl->reset();
    }

    MR::tryUpdateHitSensorsAll(this);
    MR::addToClippingTarget(this);
    MR::connectToSceneTemporarily(this);

    if (!MR::isNoEntryDrawBuffer(this)) {
        MR::connectToDrawTemporarily(this);
    }
}

void LiveActor::kill() {
    makeActorDead();
    if (mSwitchCtrl != nullptr && mSwitchCtrl->isValidSwitchDead() && mSwitchCtrl->_10) {
        MR::onSwitchDead(this);
    }
}

void LiveActor::makeActorDead() {
    mVelocity.zero();

    MR::clearHitSensors(this);

    if (mSensorKeeper != nullptr) {
        mSensorKeeper->invalidateBySystem();
    }

    if (mBinder != nullptr) {
        mBinder->clear();
    }

    if (mEffectKeeper != nullptr) {
        mEffectKeeper->clear();
    }

    if (mCollisionParts != nullptr) {
        MR::invalidateCollisionParts(this);
    }

    mFlags.mIsDead = true;

    MR::removeFromClippingTarget(this);
    MR::disconnectToSceneTemporarily(this);
    MR::disconnectToDrawTemporarily(this);
}

void LiveActor::movement() {
    if (mModelManager != nullptr && !mFlags.mIsNotReleasedAnimFrame) {
        mModelManager->update();

        if (mActionKeeper != nullptr) {
            mActionKeeper->updateAnimKeeper();
        }
    }

    if (MR::isCalcGravity(this)) {
        MR::calcGravity(this);
    }

    if (mSensorKeeper != nullptr) {
        mSensorKeeper->doObjCol();
    }

    if (mFlags.mIsDead) {
        return;
    }

    if (mSpine != nullptr) {
        mSpine->update();
    }

    if (mFlags.mIsDead) {
        return;
    }

    control();

    if (mFlags.mIsDead) {
        return;
    }

    updateBinder();

    if (mActionKeeper != nullptr) {
        mActionKeeper->update();
    }

    if (mEffectKeeper != nullptr) {
        mEffectKeeper->update();
    }

    if (mLightCtrl != nullptr) {
        MR::updateLightCtrl(this);
    }

    MR::tryUpdateHitSensorsAll(this);
    MR::actorSoundMovement(this);
    MR::requestCalcActorShadow(this);
}

void LiveActor::calcAnim() {
    if (mFlags.mIsOnCalcAnim) {
        return;
    }

    calcAnmMtx();

    if (mCollisionParts == nullptr) {
        return;
    }

    MR::setCollisionMtx(this);
}

void LiveActor::calcAnmMtx() {
    if (mModelManager == nullptr) {
        return;
    }

    MR::getJ3DModel(this)->setBaseScale(mScale);
    calcAndSetBaseMtx();
    mModelManager->calcAnim();
}

void J3DModel::setBaseScale(const Vec& scale) {
    mBaseScale.x = scale.x;
    mBaseScale.y = scale.y;
    mBaseScale.z = scale.z;
}

void LiveActor::calcViewAndEntry() {
    if (mFlags.mIsNoCalcView) {
        return;
    }

    if (mModelManager == nullptr) {
        return;
    }

    if (mFlags.mIsNoCalcView) {
        return;
    }

    mModelManager->calcView();
}

bool LiveActor::receiveMessage(u32 msg, HitSensor* pSender, HitSensor* pReceiver) {
    if (msg == 51) {
        return receiveMsgPush(pSender, pReceiver);
    }

    bool isMsgPlayerAttack = msg > 0 && msg < 38;

    if (isMsgPlayerAttack) {
        return receiveMsgPlayerAttack(msg, pSender, pReceiver);
    }

    bool isMsgEnemyAttack = msg > 89 && !(msg >= 117);

    if (isMsgEnemyAttack) {
        return receiveMsgEnemyAttack(msg, pSender, pReceiver);
    }

    return receiveOtherMsg(msg, pSender, pReceiver);
}

void LiveActor::calcAndSetBaseMtx() {
    if (MR::getTaken(this) != nullptr) {
        MR::setBaseTRMtx(this, MR::getTaken(this)->mHost->getTakingMtx());
    } else {
        TPos3f mtx;

        if (mRotation.x == 0.0f && mRotation.z == 0.0f) {
            MR::makeMtxTransRotateY(mtx, this);
        } else {
            MR::makeMtxTR(mtx, this);
        }

        MR::setBaseTRMtx(this, mtx);
    }
}

MtxPtr LiveActor::getTakingMtx() const {
    return getBaseMtx();
}

void LiveActor::setNerve(const Nerve* pNerve) {
    mSpine->setNerve(pNerve);
}

bool LiveActor::isNerve(const Nerve* pNerve) const {
    return mSpine->getCurrentNerve() == pNerve;
}

s32 LiveActor::getNerveStep() const {
    return mSpine->mCurrentStep;
}

HitSensor* LiveActor::getSensor(const char* pSensorName) const {
    if (mSensorKeeper != nullptr) {
        return mSensorKeeper->getSensor(pSensorName);
    }

    return nullptr;
}

MtxPtr LiveActor::getBaseMtx() const {
    if (MR::getJ3DModel(this) != nullptr) {
        return MR::getJ3DModel(this)->mBaseTransformMtx;
    }

    return nullptr;
}

void LiveActor::startClipped() {
    mFlags.mIsClipped = true;

    if (getSensorKeeper() != nullptr) {
        mSensorKeeper->invalidateBySystem();
    }

    if (mEffectKeeper != nullptr) {
        mEffectKeeper->stopEmitterOnClipped();
    }

    MR::disconnectToSceneTemporarily(this);

    if (MR::isNoEntryDrawBuffer(this)) {
        return;
    }

    MR::disconnectToDrawTemporarily(this);
}

void LiveActor::endClipped() {
    mFlags.mIsClipped = false;

    if (getSensorKeeper() != nullptr) {
        mSensorKeeper->validateBySystem();
        MR::updateHitSensorsAll(this);
    }

    if (mEffectKeeper != nullptr) {
        mEffectKeeper->playEmitterOffClipped();
    }

    MR::connectToSceneTemporarily(this);

    if (MR::isNoEntryDrawBuffer(this)) {
        return;
    }

    MR::connectToDrawTemporarily(this);
}

void LiveActor::initModelManagerWithAnm(const char* pModelName, const char* pAnimName, const char* pActionName, bool a4) {
    mModelManager = new ModelManager(MR::getCameraProjectionMtx());
    mModelManager->init(pModelName, pAnimName, a4);

    MR::getJ3DModel(this)->setBaseScale(mScale);
    LiveActor::calcAndSetBaseMtx();
    MR::calcJ3DModel(this);

    mActionKeeper = ActorActionKeeper::tryCreate(this, pActionName);
}

void LiveActor::initNerve(const Nerve* pNerve, s32 numStates) {
    mSpine = new Spine(this, pNerve, numStates);
}

void LiveActor::initHitSensor(s32 numSensors) {
    mSensorKeeper = new HitSensorKeeper(numSensors);
}

void LiveActor::initBinder(f32 radius, f32 offsetY, u32 planeNum) {
    mBinder = new Binder(getBaseMtx(), &mPosition, &mGravity, radius, offsetY, planeNum);

    MR::onBind(this);

    if (mEffectKeeper != nullptr) {
        mEffectKeeper->setBinder(mBinder);
    }
}

void LiveActor::initRailRider(const JMapInfoIter& rIter) {
    mRailRider = new RailRider(rIter);
}

void LiveActor::initEffectKeeper(s32 a1, const char* a2, bool doSort) {
    mEffectKeeper = new EffectKeeper(getName(), MR::getModelResourceHolder(this), a1, a2);

    if (doSort) {
        mEffectKeeper->enableSort();
    }

    mEffectKeeper->init(this);

    if (mBinder != nullptr) {
        mEffectKeeper->setBinder(mBinder);
    }
}

void LiveActor::initSound(s32 a1, const char* a2, const TVec3f* a3, const TVec3f& a4) {
    mSoundHolder = new ActorSoundHolder(this, a1, a2, a3, TVec3f(a4));
}

void LiveActor::initShadowControllerList(u32 shadowNum) {
    mShadowList = new ShadowControllerList(this, shadowNum);
}

void LiveActor::initActorCollisionParts(const char* pParam1, HitSensor* pParam2, ResourceHolder* pParam3, MtxPtr pParam4, bool param5, bool param6) {
    MR::CollisionScaleType scaleType;

    if (param6) {
        scaleType = (MR::CollisionScaleType)1;
    } else {
        scaleType = (MR::CollisionScaleType)2;

        if (param5) {
            scaleType = (MR::CollisionScaleType)0;
        }
    }

    if (pParam3 != nullptr) {
        TPos3f mtx;

        if (pParam4 != nullptr) {
            mtx.set(pParam4);
        } else {
            MR::makeMtxTRS(mtx, this);
        }

        mCollisionParts = MR::createCollisionPartsFromResourceHolder(pParam3, pParam1, pParam2, mtx, pParam4, scaleType);
    } else if (pParam4 == nullptr) {
        mCollisionParts = MR::createCollisionPartsFromLiveActor(this, pParam1, pParam2, scaleType);
    } else {
        mCollisionParts = MR::createCollisionPartsFromLiveActor(this, pParam1, pParam2, pParam4, scaleType);
    }

    MR::invalidateCollisionParts(this);
}

void LiveActor::initStageSwitch(const JMapInfoIter& rIter) {
    mSwitchCtrl = MR::createStageSwitchCtrl(this, rIter);
}

void LiveActor::initActorStarPointerTarget(f32 radius, const TVec3f* pTrans, MtxPtr pMtx, TVec3f offset) {
    mPointerTarget = new StarPointerTarget(radius, pTrans, pMtx, offset);
}

void LiveActor::initActorLightCtrl() {
    mLightCtrl = new ActorLightCtrl(this);
}

void LiveActor::attackSensor(HitSensor* pSender, HitSensor* pReceiver) {
}

void LiveActor::updateBinder() {
    if (mBinder == nullptr) {
        mPosition += mVelocity;
    } else if (mFlags.mIsOnBind) {
        mPosition += mVelocity;
        mBinder->clear();
    } else {
        mPosition += mBinder->bind(mVelocity);
    }
}
