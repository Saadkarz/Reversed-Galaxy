#pragma once

#include <revolution.h>

class LiveActor;

class ActorActionKeeper {
public:
    void initFlagCtrl();
    void updateAnimKeeper();
    void update();

    static ActorActionKeeper* tryCreate(LiveActor*, const char*);
};
