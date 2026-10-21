#include "Game/LiveActor/ChangeObj.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Scene/SceneObjHolder.hpp"
#include "Game/Util.hpp"
#include "Game/Util/ActorMovementUtil.hpp"

void ChangeObj::changeTRSVGFromOther(const ChangeObj* pOther) {
#ifdef __MWERKS__
    register LiveActor* otherActor;
    asm {
        lwz otherActor, 0x4(r4)
    }
    MR::setRotation(mActor, otherActor->mRotation);
#else
    MR::setRotation(mActor, pOther->mActor->mRotation);
#endif
    MR::setScale(mActor, pOther->mActor->mScale);
    mActor->mVelocity.set<f32>(pOther->mActor->mVelocity);
    mActor->mGravity.set<f32>(pOther->mActor->mGravity);
    MR::setPosition(mActor, pOther->mActor->mPosition);
    MR::resetPosition(mActor);
}

class ChangeObjTag {
public:
    bool registerObj(ChangeObj* pObj, s32 zoneId, s32 linkId);

    u8 _0[0x14];
    s32 mZoneId;      // 0x14
    s32 mLinkIdA;     // 0x18
    s32 mLinkIdB;     // 0x1C
    ChangeObj* mObjA; // 0x20
    ChangeObj* mObjB; // 0x24
};

bool ChangeObjTag::registerObj(ChangeObj* pObj, s32 zoneId, s32 linkId) {
    if (mZoneId != zoneId) {
        return false;
    }

    if (linkId == mLinkIdA) {
        mObjA = pObj;
        return true;
    }

    if (linkId == mLinkIdB) {
        mObjB = pObj;
        return true;
    }

    return false;
}

ChangeObjHolder::ChangeObjHolder(const char* pName) : NameObj(pName), mGroups() {
    mGroups.init(0x40);
}

void ChangeObjHolder::init(const JMapInfoIter& rIter) {
}

void ChangeObjHolder::registerObj(ChangeObj* pObj, const JMapInfoIter& rIter) {
    s32 count = mGroups.size();
    s32 zoneId = MR::getPlacedZoneId(rIter);
    s32 linkId;
    MR::getJMapInfoLinkID(rIter, &linkId);

    for (s32 i = 0; i < count; i++) {
        if (mGroups[i]->registerObj(pObj, zoneId, linkId)) {
            break;
        }
    }
}

namespace MR {
    void registerChangeObj(ChangeObj* pObj, const JMapInfoIter& rIter) {
        if (MR::isExistSceneObj(SceneObj_ChangeObjHolder)) {
            MR::getSceneObj<ChangeObjHolder*>(SceneObj_ChangeObjHolder)->registerObj(pObj, rIter);
        }
    }
};

template <>
MR::AssignableArray<ChangeObjTag*>::~AssignableArray() {
    if (mArr != nullptr) {
        delete[] mArr;
    }
}

ChangeObjHolder::~ChangeObjHolder() {
}


