#pragma once

#include <revolution.h>

class ScenarioData;

class GalaxyStatusAccessor {
public:
    GalaxyStatusAccessor(const ScenarioData*);

    const char* getName() const;
    s32 getPowerStarNum() const;

    s32 getWorldNo() const;
    bool isGreenStar(s32) const;

    const ScenarioData* mScenarioData;  // 0x00
};

namespace MR {
    GalaxyStatusAccessor makeGalaxyStatusAccessor(const char*);
};
