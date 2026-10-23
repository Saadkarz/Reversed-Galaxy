#include "JSystem/JAudio2/JAISoundParams.hpp"

void JAISoundParamsMove::moveVolume(f32 newValue, u32 maxSteps) {
    if (maxSteps == 0) {
        mParams.mVolume = newValue;
        mTransition.mVolume.mRemainingSteps = 0;
    } else {
        mTransition.mVolume.set(newValue, mParams.mVolume, maxSteps);
    }
}

void JAISoundParamsTransition::TTransition::set(f32 newValue, f32 currentValue, u32 maxSteps) {
    mRemainingSteps = maxSteps;
    mStep = (newValue - currentValue) / mRemainingSteps;
    mTargetValue = newValue;
}

void JAISoundParamsMove::movePitch(f32 newValue, u32 maxSteps) {
    if (maxSteps == 0) {
        mParams.mPitch = newValue;
        mTransition.mPitch.mRemainingSteps = 0;
    } else {
        mTransition.mPitch.set(newValue, mParams.mPitch, maxSteps);
    }
}

void JAISoundParamsMove::moveFxMix(f32 newValue, u32 maxSteps) {
    if (maxSteps == 0) {
        mParams.mFxMix = newValue;
        mTransition.mFxMix.mRemainingSteps = 0;
    } else {
        mTransition.mFxMix.set(newValue, mParams.mFxMix, maxSteps);
    }
}
