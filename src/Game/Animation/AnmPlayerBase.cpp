#include "Game/Animation/AnmPlayerBase.hpp"
#include "Game/System/ResourceInfo.hpp"
#include "Game/Util/StringUtil.hpp"

AnmPlayerBase::AnmPlayerBase(const ResTable* pResTable) : mResTable(pResTable), mAnmRes(nullptr), mFrameCtrl(), mWaitFirstFrame(false) {
}

void AnmPlayerBase::update() {
    if (mAnmRes != nullptr && !mWaitFirstFrame) {
        mFrameCtrl.update();
    }
}

void AnmPlayerBase::reflectFrame() {
    if (mAnmRes != nullptr) {
        mAnmRes->mFrame = mFrameCtrl.mFrame;
    }
}

extern "C" void fn_80069340(AnmPlayerBase* pPlayer) {
    pPlayer->mWaitFirstFrame = false;
}

void AnmPlayerBase::start(const char* pResName) {
    (void)1.0f;
    (void)0.0f;
    J3DAnmBase* pAnmRes = reinterpret_cast< J3DAnmBase* >(mResTable->getRes(pResName));

    if (pAnmRes != mAnmRes) {
        changeAnimation(pAnmRes);
        mAnmRes = pAnmRes;
    }

    mFrameCtrl.init(mAnmRes->mFrameMax);
    mFrameCtrl.setAttribute(mAnmRes->mAttribute);
    mFrameCtrl.setFrame(0.0f);
    mFrameCtrl.setRate(1.0f);
    mWaitFirstFrame = true;
}

void AnmPlayerBase::changeAnimation(J3DAnmBase*) {
}

void AnmPlayerBase::stop() {
    stopAnimation();
    mFrameCtrl.setRate(0.0f);
}

void AnmPlayerBase::stopAnimation() {
}

extern "C" void fn_80069450(AnmPlayerBase* pPlayer) {
    pPlayer->mFrameCtrl.setRate(1.0f);
}

bool AnmPlayerBase::isPlaying(const char* pAnimName) const {
    if (mAnmRes != nullptr) {
        if (MR::isEqualStringCase(pAnimName, mResTable->getResName(mAnmRes))) {
            return true;
        }
    }

    return false;
}

MaterialAnmPlayerBase::MaterialAnmPlayerBase(const ResTable* pResTable, J3DModelData* pModelData) : AnmPlayerBase(pResTable), mModelData(pModelData) {
}

void MaterialAnmPlayerBase::beginDiff() {
    if (mAnmRes != nullptr) {
        reflectFrame();
        attach(mAnmRes, mModelData);
    }
}

void MaterialAnmPlayerBase::endDiff() {
    if (mAnmRes != nullptr) {
        detach(mAnmRes, mModelData);
    }
}
