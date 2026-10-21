#pragma once

#include <revolution/types.h>

class SaveDataHandleSequence {
public:
    bool isPermitToReset() const;
    void prepareReset();
    bool isPreparedReset() const;
    void restoreFromReset();
};
