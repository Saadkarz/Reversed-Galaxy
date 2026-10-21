#pragma once

#include "Game/AudioLib/AudSystem.hpp"
#include <revolution/types.h>

class AudBgmMgr;
class AudSceneMgr;

class AudClass_8007C890 {
public:
    void fn_80087840();
};

namespace AudWrap {
    AudSystem* getSystem();
    bool hasSystem();
    AudSceneMgr* getSceneMgr();
    AudClass_8007C890* fn_8007C890();
    AudBgmMgr* getBgmMgr();
}
