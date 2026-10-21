#include "Game/LiveActor/HitSensorInfo.hpp"
#include "Game/LiveActor/HitSensor.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Util.hpp"

void HitSensorInfo::setFollowPos(const TVec3f* pFollowPos) {
    mFollowPos = pFollowPos;
}

void HitSensorInfo::setFollowMtx(MtxPtr followMtx) {
    mFollowMtx = followMtx;
}

HitSensorInfo::HitSensorInfo(const char* pSensorName, HitSensor* pSensor, const TVec3f* pFollowPos, MtxPtr followMtx, const TVec3f& rVec, bool flag)
    : mSensorName(pSensorName), mNameHash(MR::getHashCode(pSensorName)), _C(rVec), mSensor(pSensor), mFollowPos(pFollowPos), mFollowMtx(followMtx) {
    mHasCallback = flag;
}

void HitSensorInfo::update() {
    if (mHasCallback) {
        mSensor->mHostActor->updateHitSensor(mSensor);
        return;
    }

    TVec3f position;

    if (mFollowMtx) {
        position.set< f32 >(mFollowMtx[0][3], mFollowMtx[1][3], mFollowMtx[2][3]);
        position.x += (mFollowMtx[0][0] * _C.x + mFollowMtx[0][1] * _C.y + mFollowMtx[0][2] * _C.z);
        const MtxPtr mtx = mFollowMtx;
        position.y += (mtx[1][0] * _C.x + mtx[1][1] * _C.y + mtx[1][2] * _C.z);
        position.z += (mtx[2][0] * _C.x + mtx[2][1] * _C.y + mtx[2][2] * _C.z);
    } else {
        if (mFollowPos) {
            position.set< f32 >(mFollowPos->x, mFollowPos->y, mFollowPos->z);
        } else {
#ifdef __MWERKS__
            register HitSensor* sensor;
            asm {
                lwz sensor, 0x8(r3)
            }
            position.set(sensor->mHostActor->mPosition);
#else
            position.set(mSensor->mHostActor->mPosition);
#endif
        }

        MtxPtr baseMtx = mSensor->mHostActor->getBaseMtx();
        if (baseMtx) {
            position.x += baseMtx[0][0] * _C.x + baseMtx[0][1] * _C.y + baseMtx[0][2] * _C.z;
            position.y += baseMtx[1][0] * _C.x + baseMtx[1][1] * _C.y + baseMtx[1][2] * _C.z;
            position.z += baseMtx[2][0] * _C.x + baseMtx[2][1] * _C.y + baseMtx[2][2] * _C.z;
        } else {
            position.add(_C);
        }
    }

    mSensor->mPosition.set(position);
}

void HitSensorInfo::doObjCol() {
    for (s32 i = 0; i < mSensor->mSensorCount; i++) {
        if (!MR::isDead(mSensor->mSensors[i]->mHostActor)) {
            mSensor->mHostActor->attackSensor(mSensor, mSensor->mSensors[i]);
        }
    }
}
