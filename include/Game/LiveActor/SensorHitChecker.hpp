#pragma once

#include "Game/LiveActor/SensorGroup.hpp"
#include "Game/NameObj/NameObj.hpp"

class HitSensor;

class SensorHitChecker : public NameObj {
public:
    SensorHitChecker(const char*);

    virtual ~SensorHitChecker();

    virtual void init(const JMapInfoIter&);
    virtual void movement();

    void initGroup(HitSensor*);
    void doObjColGroup(SensorGroup*, SensorGroup*) const;
    void doObjColInSameGroup(SensorGroup*) const;

    void checkAttack(HitSensor*, HitSensor*) const;

    /* 0x14 */ SensorGroup* mPlayerGroup;
    /* 0x18 */ SensorGroup* mRideGroup;
    /* 0x1C */ SensorGroup* mEyeGroup;
    /* 0x20 */ SensorGroup* mSimpleGroup;
    /* 0x24 */ SensorGroup* mMapObjGroup;
    /* 0x28 */ SensorGroup* mCharacterGroup;
};

namespace MR {
    void initHitSensorGroup(HitSensor*);
};  // namespace MR
