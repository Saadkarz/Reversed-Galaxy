#pragma once

#include "Game/NameObj/NameObj.hpp"

class LayoutActor : public NameObj {
public:
    LayoutActor(const char*, bool);
    virtual ~LayoutActor();

    virtual void movement();
    virtual void draw() const;
    virtual void calcAnim();
    virtual void appear();
    virtual void kill();
    virtual void control();

    /* 0x0C */ void* mLayoutManager;
    /* 0x10 */ void* mSpine;
    /* 0x14 */ void* mEffectKeeper;
    /* 0x18 */ void* mPointingTarget;
    /* 0x1C */ u32 mFlag;
};
