#include "Game/Ride/TubeSliderObjCreator.hpp"

#include "Game/MapObj/TicoCoin.hpp"
#include "Game/Ride/TubeSlider.hpp"
#include "Game/Ride/TubeSliderCrystal.hpp"
#include "Game/Ride/TubeSliderFunction.hpp"
#include "Game/Ride/TubeSliderJumpStep.hpp"
#include "Game/Util/JMapUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/RailUtil.hpp"
#include "Game/Util/StringUtil.hpp"

namespace {
    inline void initPlacedActor(LiveActor* pActor, const TVec3f& rUp, const JMapInfoIter& rIter) {
        TVec3f pos(pActor->mPosition);
        pActor->mGravity.set(rUp);
        MR::setClippingFar300m(pActor);
        pActor->init(rIter);
        pActor->mGravity.set(rUp);
        MR::setPosition(pActor, pos);
    }
}  // namespace

TubeSliderObjCreator::TubeSliderObjCreator(TubeSlider* pSlider, const char* pName) : NameObj("オブジェ生成（チューブスライダー）") {
    mSlider = pSlider;
    mObjName = pName;
}

void TubeSliderObjCreator::init(const JMapInfoIter& rIter) {
    TVec3f trans(0.0f);
    MR::getJMapInfoTrans(rIter, &trans);
    MR::moveCoordToNearestPos(mSlider, trans);
    TubeSliderFunction::updateTubeSliderInfo(mSlider, true);

    f32 floorAngle = -1.0f;
    MR::getJMapInfoArg0NoInit(rIter, &floorAngle);
    f32 height = 0.0f;
    MR::getJMapInfoArg1NoInit(rIter, &height);

    TVec3f up(0.0f, 1.0f, 0.0f);
    if (floorAngle == -1.0f) {
        floorAngle = TubeSliderFunction::getFloorAngle(mSlider);
    }
    TubeSliderFunction::calcTubeVecDegree(floorAngle, &up, mSlider);

    TubeSlider* pSlider = mSlider;
    const char* pName = mObjName;
    const TVec3f& rUp = up;
    f32 negHeight = height;
    LiveActor* pActor = nullptr;
    if (MR::isEqualString(pName, "TubeSliderJumpStep")) {
        pActor = new TubeSliderJumpStep(-MR::getRailDirection(pSlider));
    } else if (MR::isEqualString(pName, "TubeSliderCrystal")) {
        pActor = new TubeSliderCrystal(-MR::getRailDirection(pSlider));
    } else if (MR::isEqualString(pName, "TubeSliderTicoCoin")) {
        pActor = new TicoCoin("チココイン（チューブスライダー）");
    }

    TubeSliderFunction::getUnknown1(&pActor->mPosition, pSlider, rUp, -negHeight);
    initPlacedActor(pActor, rUp, rIter);
}

TubeSliderObjCreator::~TubeSliderObjCreator() {
}
