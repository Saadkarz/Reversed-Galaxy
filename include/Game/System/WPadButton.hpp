#pragma once

#include <revolution/types.h>

class WPad;

class WPadButton {
public:
    WPadButton(const WPad* pPad);

    void update();

    bool testButtonUp() const;
    bool testButtonDown() const;
    bool testButtonLeft() const;
    bool testButtonRight() const;
    bool testButtonA() const;
    bool testButtonB() const;
    bool testButtonMinus() const;
    bool testButtonPlus() const;
    bool testButton1() const;
    bool testButton2() const;
    bool testButtonC() const;
    bool testButtonZ() const;

    bool testTriggerUp() const;
    bool testTriggerDown() const;
    bool testTriggerLeft() const;
    bool testTriggerRight() const;
    bool testTriggerA() const;
    bool testTriggerB() const;
    bool testTriggerMinus() const;
    bool testTriggerHome() const;
    bool testTriggerPlus() const;
    bool testTrigger1() const;
    bool testTrigger2() const;
    bool testTriggerC() const;
    bool testTriggerZ() const;

    bool isChangeAnyState() const;
    bool testButtonOnlyMinus() const;

    const WPad* mPad;
    u32 mHold;
    u32 mTrigger;
    u32 mRelease;
    u32 mRepeat;
    f32 mDelaySec;
    f32 mPulseSec;
};
