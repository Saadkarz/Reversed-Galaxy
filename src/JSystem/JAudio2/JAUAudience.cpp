#include "JSystem/JAudio2/JAUAudience.hpp"
#include "JSystem/JAudio2/JAUAudible.hpp"

void JAUAudience3DSetting::init() {
    mFarDistance = 7000.0f;
    mNearDistance = 800.0f;
    mMinVolume = 0.005f;
    mBehindDolbyZ = 8000.0f;
    mFrontDolbyZ = -4000.0f;
    mMaxFxMix = 0.1f;
    mMinFxMix = 0.0f;
    mMaxDolby = 1.0f;
    mCenterDolby = 0.8f;
    mMinDolby = 0.0f;
    mPanAmplitude = 0.5f;
    mPriorityDownRange = 255;
    mSonicSpeed = 3000.0f;
    mPitchDeltaRatioRange = 1.5f;
}

template class JASMemPool<JAUDopplerAudible<4> >;
template class JASMemPool<JAUDopplerAudible<2> >;
template class JASMemPool<JAUDopplerAudible<1> >;
template class JASMemPool<JAUAudible<4> >;
template class JASMemPool<JAUAudible<2> >;
template class JASMemPool<JAUAudible<1> >;

template JASMemPool<JAUDopplerAudible<4> > JASPoolAllocObject<JAUDopplerAudible<4> >::memPool_;
template JASMemPool<JAUDopplerAudible<2> > JASPoolAllocObject<JAUDopplerAudible<2> >::memPool_;
template JASMemPool<JAUDopplerAudible<1> > JASPoolAllocObject<JAUDopplerAudible<1> >::memPool_;
template JASMemPool<JAUAudible<4> > JASPoolAllocObject<JAUAudible<4> >::memPool_;
template JASMemPool<JAUAudible<2> > JASPoolAllocObject<JAUAudible<2> >::memPool_;
template JASMemPool<JAUAudible<1> > JASPoolAllocObject<JAUAudible<1> >::memPool_;
