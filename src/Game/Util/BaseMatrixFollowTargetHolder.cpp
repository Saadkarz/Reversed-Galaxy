#include "Game/Util/BaseMatrixFollowTargetHolder.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Scene/SceneObjHolder.hpp"
#include "Game/Util/DemoUtil.hpp"
#include "Game/Util/JMapLinkInfo.hpp"
#include "Game/Util/JMapUtil.hpp"
#include "Game/Util/ObjUtil.hpp"

namespace {
    BaseMatrixFollowTargetHolder* getBaseMatrixFollowTargetHolder() {
        return MR::getSceneObj< BaseMatrixFollowTargetHolder* >(SceneObj_BaseMatrixFollowTargetHolder);
    }
};

BaseMatrixFollowTargetHolder::BaseMatrixFollowTargetHolder(const char* pName, s32 targetCapacity, s32 followerCapacity) : NameObj(pName) {
    mTargets.init(targetCapacity);
    mFollowers.init(followerCapacity);
    MR::connectToSceneMapObjMovement(this);
    MR::registerDemoSimpleCastAll(this);
}

void BaseMatrixFollowTargetHolder::initAfterPlacement() {
    for (u32 i = 0; i < mFollowers.size(); i++) {
        BaseMatrixFollower* pFollower = mFollowers[i];
        BaseMatrixFollowTarget* pTarget = findFollowTarget(pFollower);
        if (pTarget->mActor) {
            pFollower->setGravityFollowHost(pTarget->mActor);
        }
    }
}

void BaseMatrixFollower::setGravityFollowHost(const NameObj*) {
}

void BaseMatrixFollowTargetHolder::movement() {
    for (u32 i = 0; i < mFollowers.size(); i++) {
        if (mFollowers[i]->isEnableFollow()) {
            mFollowers[i]->update();
        }
    }
}

void BaseMatrixFollower::update() {
}

void BaseMatrixFollowTargetHolder::addFollower(BaseMatrixFollower* pFollower) {
    mFollowers.push_back(pFollower);

    BaseMatrixFollowTarget* pTarget = findFollowTarget(pFollower);
    if (!pTarget) {
        pTarget = new BaseMatrixFollowTarget(pFollower->mLinkInfo);
        mTargets.push_back(pTarget);
    }

    pFollower->mFollowTarget = pTarget;
}

void BaseMatrixFollowTargetHolder::setFollowTargetInfo(LiveActor* pActor, const JMapInfoIter& rIter, const TPos3f* pBaseMtx,
                                                       BaseMatrixFollowValidater* pValidater) {
    JMapLinkInfo linkInfo(rIter, true);
    BaseMatrixFollowTarget* pTarget = findFollowTarget(&linkInfo);
    if (pTarget) {
        TPos3f mtx;
        MR::getJMapInfoMatrixFromRT(rIter, &mtx);
        pTarget->set(pActor, mtx, pBaseMtx, pValidater);
    }
}

BaseMatrixFollowTarget* BaseMatrixFollowTargetHolder::findFollowTarget(const JMapLinkInfo* pLinkInfo) {
    if (!pLinkInfo) {
        return nullptr;
    }

    for (u32 i = 0; i < mTargets.size(); i++) {
        if (*mTargets[i]->mLinkInfo == *pLinkInfo) {
            return mTargets[i];
        }
    }

    return nullptr;
}

BaseMatrixFollowTarget* BaseMatrixFollowTargetHolder::findFollowTarget(const BaseMatrixFollower* pFollower) {
    if (pFollower == nullptr) {
        return nullptr;
    }

    return findFollowTarget(pFollower->mLinkInfo);
}

namespace MR {
    bool isValidFollowID(const JMapInfoIter& rIter) {
        if (!isValidInfo(rIter)) {
            return false;
        }

        JMapLinkInfo linkInfo(rIter, false);
        return linkInfo.isValid();
    }

    void addBaseMatrixFollower(BaseMatrixFollower* pFollower) {
        createSceneObj(SceneObj_BaseMatrixFollowTargetHolder);
        ::getBaseMatrixFollowTargetHolder()->addFollower(pFollower);
    }

    void addBaseMatrixFollowTarget(LiveActor* pActor, const JMapInfoIter& rIter, const TPos3f* pBaseMtx, BaseMatrixFollowValidater* pValidater) {
        if (isValidInfo(rIter) && isExistSceneObj(SceneObj_BaseMatrixFollowTargetHolder)) {
            ::getBaseMatrixFollowTargetHolder()->setFollowTargetInfo(pActor, rIter, pBaseMtx, pValidater);
        }
    }
};

template <>
MR::AssignableArray< BaseMatrixFollowTarget* >::~AssignableArray() {
    if (mArr != nullptr) {
        delete[] mArr;
    }
}

template <>
MR::AssignableArray< BaseMatrixFollower* >::~AssignableArray() {
    if (mArr != nullptr) {
        delete[] mArr;
    }
}

BaseMatrixFollowTargetHolder::~BaseMatrixFollowTargetHolder() {
}


