#pragma once

#include "Game/Util/JMapInfo.hpp"
#include <JSystem/JGeometry/TMatrix.hpp>
#include <JSystem/JGeometry/TVec.hpp>

class NameObj;
class GameSystemSceneController;
class JMapIdInfo;

namespace MR {
    s32 getCurrentScenarioNo();
    s32 getCurrentSelectedScenarioNo();
    void setCurrentScenarioNo(s32, s32);
    bool isScenarioDecided();
    GameSystemSceneController* getSceneController();

    const char* getCurrentStageName();
    bool isEqualSceneName(const char*);
    bool isEqualStageName(const char*);
    bool isValidZoneName(const char*);

    bool isPlacementLocalStage();

    TPos3f& getZonePlacementMtx(const JMapInfoIter&);

    void getCameraRailInfo(JMapInfoIter*, const JMapInfo**, s32, s32);

    void getRailInfo(JMapInfoIter*, const JMapInfo**, const JMapInfoIter&);

    bool isInitializeStatePlacementSomething();
    s32 getChildObjNum(const JMapInfoIter&);
    void getChildObjName(const char**, const JMapInfoIter&, int);
    void initChildObj(NameObj*, const JMapInfoIter&, int);
    s32 getPlacedZoneId(const JMapInfoIter&);

    const JMapIdInfo* getInitializeStartIdInfo();
    bool isStageMarioFaceShipOrWorldMap();
    s32 getPlayerLife();
    bool isPowerStarBronze(const char*, s32);
    bool fn_80024F60(const char*);
};  // namespace MR
