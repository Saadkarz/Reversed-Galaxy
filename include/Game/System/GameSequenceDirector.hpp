#pragma once

#include <revolution/types.h>

class GameDataHolder;
class SaveDataHandleSequence;

class GameSequenceDirector {
public:
    bool isInitializedGameDataHolder() const;

    /* 0x00 */ void* _0;
    /* 0x04 */ void* _4;
    /* 0x08 */ SaveDataHandleSequence* mSaveDataHandleSequence;
};
