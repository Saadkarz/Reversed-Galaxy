#pragma once

#include <revolution/types.h>

class SpkSystem {
public:
    static void connect(s32);
    static void disconnect(s32);
    static void extensionProcess(s32, s32);
};
