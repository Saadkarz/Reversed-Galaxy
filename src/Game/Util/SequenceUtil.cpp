#include "Game/Util/SequenceUtil.hpp"
#include "Game/Scene/GameSceneFunction.hpp"
#include "Game/System/GameSequenceFunction.hpp"
#include "Game/Util/EventUtil.hpp"
#include "Game/Util/ScreenUtil.hpp"

namespace MR {
    bool isExecScenarioStarter() {
        return GameSceneFunction::isExecScenarioStarter();
    }

    bool isStageStateScenarioOpeningCamera() {
        return GameSceneFunction::isExecScenarioOpeningCamera();
    }

    bool isStageStatePowerStarAppeared() {
        return fn_804D7100();
    }

    void requestPowerStarGetDemo() {
        GameSceneFunction::requestPowerStarGetDemo();
    }

    void requestGrandStarGetDemo() {
        GameSceneFunction::requestGrandStarGetDemo();
    }

    void requestStartGameOverDemo() {
        GameSceneFunction::requestStartGameOverDemo();
    }

    void requestEndGameOverDemo() {
        GameSceneFunction::requestEndGameOverDemo();
    }

    void requestEndMissDemo() {
        GameSceneFunction::requestEndMissDemo();
    }

    void executeOnWelcomeAndRetry() {
        startGalaxyCometEvent();
        requestForceAppearHPMeter();
    }
};  // namespace MR
