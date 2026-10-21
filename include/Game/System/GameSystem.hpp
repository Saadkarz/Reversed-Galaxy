#pragma once

#include "Game/System/NerveExecutor.hpp"
#include <revolution/types.h>

class GameSequenceDirector;
class GameSystemDataHolder;
class GameSystemDimmingWatcher;
class GameSystemErrorWatcher;
class GameSystemFontHolder;
class GameSystemFrameControl;
class GameSystemObjHolder;
class GameSystemSceneController;
class GameSystemStationedArchiveLoader;
class HomeButtonLayout;
class SystemWipeHolder;

class GameSystem : public NerveExecutor {
public:
    void initGX();
    void initAfterStationedResourceLoaded();
    bool isExecuteLoadSystemArchive() const;
    void startToLoadSystemArchive();
    bool isDoneLoadSystemArchive() const;
    void prepareReset();
    bool isPreparedReset() const;

    /* 0x08 */ void* mFifoBase;
    /* 0x0C */ GameSequenceDirector* mSequenceDirector;
    /* 0x10 */ GameSystemDimmingWatcher* mDimmingWatcher;
    /* 0x14 */ GameSystemErrorWatcher* mErrorWatcher;
    /* 0x18 */ GameSystemFontHolder* mFontHolder;
    /* 0x1C */ GameSystemFrameControl* mFrameControl;
    /* 0x20 */ GameSystemObjHolder* mObjHolder;
    /* 0x24 */ GameSystemSceneController* mSceneController;
    /* 0x28 */ GameSystemStationedArchiveLoader* mStationedArchiveLoader;
    /* 0x2C */ HomeButtonLayout* mHomeButtonLayout;
    /* 0x30 */ SystemWipeHolder* mSystemWipeHolder;
    /* 0x34 */ GameSystemDataHolder* mDataHolder;
    /* 0x38 */ bool mIsExecuteLoadSystemArchive;
};
