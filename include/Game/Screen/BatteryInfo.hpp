#pragma once

#include "Game/Screen/LayoutActor.hpp"

class BatteryLayout : public LayoutActor {
public:
    BatteryLayout();
    virtual ~BatteryLayout();

    virtual void init(const JMapInfoIter& rIter);
    virtual void appear();
    virtual void control();

    /* 0x20 */ void* mInfo1P;
    /* 0x24 */ void* mInfo2P;
    /* 0x28 */ u32 _28;
};
