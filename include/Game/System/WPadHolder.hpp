#pragma once

#include <revolution/hbm.h>
#include <revolution/types.h>

class WPad;
struct KPADStatus;

class WPadReadDataInfo {
public:
    WPadReadDataInfo();

    KPADStatus* getKPadStatus(u32) const;
    KPADStatus* getReadBuffer();
    u32 getValidStatusCount() const;
    void copy(const WPadReadDataInfo&);

    /* 0x00 */ KPADStatus* mStatusArray;
    /* 0x04 */ u32 mValidStatusCount;
};

class WPadHolder {
public:
    WPadHolder();

    virtual void readPadData();

    void updateReadDataOnly();
    void updateProjectPadData();
    void updateInHomeButton();
    void updateInGame();
    void update();
    void initSensorBarPosition();
    WPad* getWPad(s32);
    static void setConnectCallback();

    /* 0x04 */ WPad* mPad[2];
    /* 0x0C */ WPadReadDataInfo* mReadDataInfoArray;
    /* 0x10 */ WPadReadDataInfo* mReadDataInfoArray2;
    /* 0x14 */ void* mKpadWorkBuffer;
    /* 0x18 */ s32 mMode;
};

namespace MR {
    WPad* getWPad(s32);
    void setWPadHolderModeHomeButton();
    void setWPadHolderModeGame();
    u32 getHBMKPadData(HBMKPadData*, s32);
    bool testHBMKPadTrigger(s32, u32);
};  // namespace MR
