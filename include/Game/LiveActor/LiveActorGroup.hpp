#pragma once

#include "Game/NameObj/NameObjGroup.hpp"

class LiveActor;

class LiveActorGroup : public NameObjGroup {
public:
    LiveActorGroup(const char*, int);

    inline virtual ~LiveActorGroup() {
    }

    void registerActor(LiveActor*);
    LiveActor* getActor(int) const;
    LiveActor* getDeadActor() const;
    s32 getLivingActorNum() const;
    void killAll();
    void appearAll();
    void makeAllDead();

    bool hasActor(const LiveActor* pActor) const {
        for (int i = 0; i < mObjectCount; i++) {
            if (getActor(i) == pActor) {
                return true;
            }
        }

        return false;
    }
};
