#pragma once

#include <revolution/types.h>

class GameSystemResetAndPowerProcess {
public:
    bool isActive() const;
    void setResetOperationApplicationReset();
    void setResetOperationReturnToMenu();
    void requestReset(bool);
    void requestGoWiiMenu(bool);
    void fn_804B9860(bool);
};
