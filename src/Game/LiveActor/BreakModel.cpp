#include "Game/LiveActor/BreakModel.hpp"
#include "Game/Util/ActorAnimUtil.hpp"
#include "Game/Util/ActorInitUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"

namespace NrvBreakModel {
    class BreakModelNrvWait : public Nerve {
    public:
        virtual void execute(Spine* pSpine) const {
        }
        static BreakModelNrvWait sInstance;
    };

    class BreakModelNrvBreak : public Nerve {
    public:
        virtual void execute(Spine* pSpine) const {
            reinterpret_cast<BreakModel*>(pSpine->mExecutor)->exeBreak();
        }
        static BreakModelNrvBreak sInstance;
    };

    BreakModelNrvWait BreakModelNrvWait::sInstance;
    BreakModelNrvBreak BreakModelNrvBreak::sInstance;
};

BreakModel::BreakModel(LiveActor* pHost, const char* pModelName, const char* pAnimName, MtxPtr pMtx, const char* pArcName)
    : LiveActor(pModelName), mHost(pHost), mActionName(pArcName), mMtx(pMtx) {
    if (mMtx != nullptr) {
        MR::setPosition(this, mMtx[0][3], mMtx[1][3], mMtx[2][3]);
    } else {
        MR::copyTransRotateScale(mHost, this);
    }

    MR::initActor(this, pAnimName, false);
}

void BreakModel::init(const JMapInfoIter& rIter) {
    MR::invalidateClipping(this);
    initNerve(&NrvBreakModel::BreakModelNrvWait::sInstance, 0);
    makeActorDead();
}

void BreakModel::appear() {
    if (mMtx != nullptr) {
        MR::setPosition(this, mMtx[0][3], mMtx[1][3], mMtx[2][3]);
    } else {
        MR::copyTransRotateScale(mHost, this);
    }

    LiveActor::appear();
    setNerve(&NrvBreakModel::BreakModelNrvBreak::sInstance);
}

void BreakModel::exeBreak() {
    if (MR::isFirstStep(this)) {
        MR::startAction(this, mActionName);
    }

    if (MR::isActionEnd(this)) {
        kill();
    }
}

void BreakModel::calcAndSetBaseMtx() {
    if (mMtx != nullptr) {
        mPosition.set<f32>(mMtx[0][3], mMtx[1][3], mMtx[2][3]);
        MR::setBaseTRMtx(this, mMtx);
    } else {
        LiveActor::calcAndSetBaseMtx();
    }
}

BreakModel::~BreakModel() {
}
