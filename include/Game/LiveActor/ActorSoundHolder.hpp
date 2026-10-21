#pragma once

#include "Game/GameAudio/ActionSoundInfo.hpp"
#include <JSystem/JGeometry/TVec.hpp>
#include <revolution.h>

class LiveActor;

class ActorSoundHolder {
public:
    ActorSoundHolder(LiveActor*, s32, const char*, const TVec3f*, const TVec3f&);

    /* 0x00 */ void* _0;
    /* 0x04 */ ActionSoundInfo* mActionSoundInfo;
    /* 0x08 */ u8 _8[0xC];
};
