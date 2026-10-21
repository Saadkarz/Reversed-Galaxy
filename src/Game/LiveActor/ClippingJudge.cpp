#include "Game/LiveActor/ClippingJudge.hpp"
#include "Game/LiveActor/ClippingDirector.hpp"
#include "Game/Util/CameraUtil.hpp"

ClippingJudge::ClippingJudge(const char* pName) : NameObj(pName), mFrustum() {
    (void)0.0f;
    for (s32 i = 0; i < 8; i++) {
        mClipDistances[i] = -1.0f;
    }

    mClipDistances[0] = 0.0f;
    mClipDistances[1] = 60000.0f;
    mClipDistances[2] = 50000.0f;
    mClipDistances[3] = 40000.0f;
    mClipDistances[4] = 30000.0f;
    mClipDistances[5] = 20000.0f;
    mClipDistances[6] = 10000.0f;
    mClipDistances[7] = 5000.0f;
}

template <>
JGeometry::THexahedron3<f32>::THexahedron3() {
}

void ClippingJudge::init(const JMapInfoIter& rIter) {
}

void ClippingJudge::movement() {
    calcViewingVolume(&mFrustum, MR::getFarZ());

    for (u32 i = 1; i < 8; i++) {
        calcViewingVolume(&mClipFrustums[i], mClipDistances[i]);
    }
}

bool ClippingJudge::isJudgedToClipFrustum(const TVec3f& rVec, f32 a2) const {
    return !mFrustum.mayIntersectBall3(rVec, a2);
}

template <>
bool JGeometry::THexahedron3<f32>::mayIntersectBall3(const TVec3f& rVec, f32 a2) const {
    f32 neg = -a2;
    const TPartition3< f32 >* end = mPlanes + 6;
    const TPartition3< f32 >* cur = mPlanes;

    while (cur < end) {
        if (cur->mNormal.dot(rVec) - cur->mDot < neg) {
            return false;
        }

        cur++;
    }

    return true;
}

bool ClippingJudge::isJudgedToClipFrustum(const TVec3f& rVec, f32 a2, s32 index) const {
    return (!index) ? !mFrustum.mayIntersectBall3(rVec, a2) : !mClipFrustums[index].mayIntersectBall3(rVec, a2);
}

extern "C" f32 fn_801117D0();

void ClippingJudge::calcViewingVolume(THex3f* pVolume, f32 farClip) {
    f32 nearClip = 500.0f;
    if (MR::isSubjectiveCameraOnForObjClipping()) {
        nearClip = 100.0f;
    }

    f32 aspect = fn_801117D0();
    f32 fovy = MR::getFovy();
    TPos3f cameraMtx;
    cameraMtx.setPositionFromLookAt(MR::getCameraViewMtx());
    f32 height = nearClip * static_cast< f32 >(tan(fovy * (JGeometry::TUtil< f32 >::PI() / 360.0f)));
    f32 width = aspect * height;

    TVec3f front;
    cameraMtx.getZDir(front);
    TVec3f position;
    TVec3f bottomRight(width, -height, nearClip);
    TVec3f topRight(width, height, nearClip);
    TVec3f topLeft(-width, height, nearClip);
    TVec3f bottomLeft(-width, -height, nearClip);
    cameraMtx.getTrans(position);
    cameraMtx.mult(topRight, topRight);
    cameraMtx.mult(topLeft, topLeft);
    cameraMtx.mult(bottomLeft, bottomLeft);
    cameraMtx.mult(bottomRight, bottomRight);

    pVolume->mPlanes[3].set(position, topLeft, topRight);
    pVolume->mPlanes[1].set(position, topRight, bottomRight);
    pVolume->mPlanes[2].set(position, bottomRight, bottomLeft);
    pVolume->mPlanes[0].set(position, bottomLeft, topLeft);

    TVec3f back;
    back.negate(front);
    TVec3f planePosition;
    planePosition.scaleAdd(farClip, front, position);
    pVolume->mPlanes[5].set(back, planePosition);
    planePosition.scaleAdd(nearClip, front, position);
    pVolume->mPlanes[4].set(front, planePosition);
}

template <>
void JGeometry::TPartition3<f32>::set(const TVec3f& rNormal, const TVec3f& rPoint) {
    mNormal.x = rNormal.x;
    mNormal.y = rNormal.y;
    mNormal.z = rNormal.z;
    mDot = mNormal.dot(rPoint);
}

namespace MR {
    ClippingJudge* getClippingJudge() {
        return getClippingDirector()->mJudge;
    }
};  // namespace MR

ClippingJudge::~ClippingJudge() {
}
