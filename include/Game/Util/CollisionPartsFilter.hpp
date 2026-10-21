#pragma once

#include "Game/LiveActor/LiveActor.hpp"
#include "Game/Map/CollisionParts.hpp"

class CollisionPartsFilterBase {
public:
    virtual bool isInvalidParts(const CollisionParts*) const = 0;
};

typedef bool (*CollisionPartsFunc)(const CollisionParts*);

class CollisionPartsFilterDelegator : public CollisionPartsFilterBase {
public:
    inline CollisionPartsFilterDelegator(CollisionPartsFunc func) : mFunc(func) {}
    virtual bool isInvalidParts(const CollisionParts* pParts) const;

    /* 0x04 */ CollisionPartsFunc mFunc;
};

class CollisionPartsFilterSensor : public CollisionPartsFilterBase {
public:
    inline CollisionPartsFilterSensor(const HitSensor* pSensor) : mSensor(pSensor) {}
    virtual bool isInvalidParts(const CollisionParts* pParts) const;

    /* 0x04 */ const HitSensor* mSensor;
};

class CollisionPartsFilterSensorType : public CollisionPartsFilterBase {
public:
    inline CollisionPartsFilterSensorType(u32 type) : mSensorType(type) {}
    virtual bool isInvalidParts(const CollisionParts* pParts) const;

    /* 0x04 */ u32 mSensorType;
};

class CollisionPartsFilterActor : public CollisionPartsFilterBase {
public:
    inline CollisionPartsFilterActor(const LiveActor* pActor) : mActor(pActor) {}
    virtual bool isInvalidParts(const CollisionParts* pParts) const;

    /* 0x04 */ const LiveActor* mActor;
};

namespace MR {
    CollisionPartsFilterDelegator* createCollisionPartsFilterDelegator(CollisionPartsFunc);
};
