#include "Game/Util/CollisionPartsFilter.hpp"
#include "Game/LiveActor/HitSensor.hpp"

namespace MR {
    CollisionPartsFilterDelegator* createCollisionPartsFilterDelegator(CollisionPartsFunc func) {
        return new CollisionPartsFilterDelegator(func);
    }
}

bool CollisionPartsFilterSensor::isInvalidParts(const CollisionParts* pParts) const {
    return pParts->mHitSensor == mSensor;
}

bool CollisionPartsFilterSensorType::isInvalidParts(const CollisionParts* pParts) const {
    return pParts->mHitSensor->isType(mSensorType);
}

bool CollisionPartsFilterActor::isInvalidParts(const CollisionParts* pParts) const {
    return pParts->mHitSensor->mHost == mActor;
}

bool CollisionPartsFilterDelegator::isInvalidParts(const CollisionParts* pParts) const {
    return mFunc(pParts);
}
