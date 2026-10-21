#pragma once

#include <revolution.h>

class NameObjHolder;
class ScenarioDataParser;
class Scene;

class GameSystemSceneController {
public:
    void prepareReset();
    bool isPreparedReset();
    void restartGameAfterResetting();
    void resetCurrentScenarioNo();

    /* 0x000 */ u8 _0[0x124];
    /* 0x124 */ ScenarioDataParser* mScenarioDataParser;
    /* 0x128 */ NameObjHolder* mObjHolder;
    /* 0x12C */ Scene* mScene;
};
