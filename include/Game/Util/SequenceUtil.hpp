#pragma once

#include <revolution/types.h>

namespace MR {
    bool isExecScenarioStarter();
    bool isStageStateScenarioOpeningCamera();
    bool isStageStatePowerStarAppeared();
    void requestPowerStarGetDemo();
    void requestGrandStarGetDemo();
    void requestStartGameOverDemo();
    void requestEndGameOverDemo();
    void requestEndMissDemo();
    void executeOnWelcomeAndRetry();
};  // namespace MR
