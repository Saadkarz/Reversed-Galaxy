#include "Game/Ride/TubeSliderJumpStep.hpp"

#include "Game/LiveActor/Nerve.hpp"
#include "Game/Util/ActorAnimUtil.hpp"
#include "Game/Util/ActorInitUtil.hpp"
#include "Game/Util/ActorMovementUtil.hpp"
#include "Game/Util/ActorSensorUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"

namespace NrvTubeSliderJumpStep {
    NEW_NERVE(TubeSliderJumpStepNrvWait, TubeSliderJumpStep, Wait);
    NEW_NERVE(TubeSliderJumpStepNrvJump, TubeSliderJumpStep, Jump);
}  // namespace NrvTubeSliderJumpStep

TubeSliderJumpStep::TubeSliderJumpStep(const TVec3f& rFront) : LiveActor("ジャンプ台（チューブスライダー用）") {
    mFront = rFront;
}

void TubeSliderJumpStep::init(const JMapInfoIter& rIter) {
    MR::setScale(this, 1.5f);
    MR::initActor(this, rIter, "TubeSliderJumpStep", false);
    initNerve(GET_NERVE(TubeSliderJumpStep, TubeSliderJumpStepNrvWait), 0);
    makeActorAppeared();
}

void TubeSliderJumpStep::calcAndSetBaseMtx() {
    MR::calcAndSetBaseTRMtxFromGravityAndZAxis(this, mFront);
}

void TubeSliderJumpStep::exeWait() {
    if (MR::isFirstStep(this)) {
        MR::startAction(this, "Wait");
    }
}

void TubeSliderJumpStep::exeJump() {
    if (MR::isFirstStep(this)) {
        MR::startAction(this, "Jump");
    }

    if (MR::isActionEnd(this)) {
        setNerve(GET_NERVE(TubeSliderJumpStep, TubeSliderJumpStepNrvWait));
    }
}

void TubeSliderJumpStep::attackSensor(HitSensor* pSender, HitSensor* pReceiver) {
    if (isNerve(GET_NERVE(TubeSliderJumpStep, TubeSliderJumpStepNrvWait)) && MR::isSensorRide(pReceiver) && MR::sendMsgJump(pReceiver, pSender)) {
        setNerve(GET_NERVE(TubeSliderJumpStep, TubeSliderJumpStepNrvJump));
    }
}
