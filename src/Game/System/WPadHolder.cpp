#include "Game/System/WPadHolder.hpp"
#include "Game/System/GameSequenceFunction.hpp"
#include "Game/System/GameSystem.hpp"
#include "Game/System/GameSystemFunction.hpp"
#include "Game/System/GameSystemObjHolder.hpp"
#include "Game/System/WPad.hpp"
#include "Game/System/WPadPointer.hpp"
#include "Game/Util/GamePadUtil.hpp"
#include "Game/Util/MemoryUtil.hpp"
#include "Game/Util/SingletonHolder.hpp"
#include <revolution/wpad.h>

#define KPAD_STATUS_ARRAY_SIZE 120

namespace {
    bool isUpdatePad() {
        if (GameSystemFunction::isHomeButtonMenuActive()) {
            return false;
        }

        return !GameSystemFunction::isOccurredSystemWarning();
    }

    inline bool isUpdateInHomeButton() {
        return GameSequenceFunction::isPadMode() && MR::isPadRecorderReading() && !isUpdatePad();
    }
}  // namespace

WPadReadDataInfo::WPadReadDataInfo() : mStatusArray(nullptr), mValidStatusCount(0) {
    mStatusArray = new KPADStatus[KPAD_STATUS_ARRAY_SIZE];
    MR::zeroMemory(mStatusArray, sizeof(KPADStatus) * KPAD_STATUS_ARRAY_SIZE);
}

KPADStatus* WPadReadDataInfo::getKPadStatus(u32 index) const {
    if (index >= mValidStatusCount) {
        return nullptr;
    }

    return &mStatusArray[index];
}

KPADStatus* WPadReadDataInfo::getReadBuffer() {
    return mStatusArray;
}

u32 WPadReadDataInfo::getValidStatusCount() const {
    return mValidStatusCount;
}

void WPadReadDataInfo::copy(const WPadReadDataInfo& rOther) {
    mValidStatusCount = rOther.mValidStatusCount;

    for (s32 i = 0; i < (s32)mValidStatusCount; i++) {
        mStatusArray[i] = rOther.mStatusArray[i];
    }
}

WPadHolder::WPadHolder()
    : mReadDataInfoArray2(nullptr),
      mKpadWorkBuffer(nullptr),
      mMode(1) {
    WPADRegisterAllocator(MR::allocFromWPadHeap, MR::freeFromWPadHeap);
    mKpadWorkBuffer = new u8[0x7BC0];
    KPADInit(mKpadWorkBuffer, 0x1E0);

    mReadDataInfoArray = new WPadReadDataInfo[WPAD_MAX_CONTROLLERS];
    mReadDataInfoArray2 = new WPadReadDataInfo[WPAD_MAX_CONTROLLERS];

    for (u32 i = 0; i < 2; i++) {
        mPad[i] = new WPad(i);
        mPad[i]->setReadInfo(&mReadDataInfoArray2[i]);
    }

    setConnectCallback();
    initSensorBarPosition();
}

void WPadHolder::updateReadDataOnly() {
    WPadReadDataInfo* pInfo;

    for (s32 chan = WPAD_CHAN0; chan < WPAD_MAX_CONTROLLERS; chan++) {
        pInfo = &mReadDataInfoArray[chan];
        s32 err = 0;
        pInfo->mValidStatusCount = KPADReadEx(chan, pInfo->mStatusArray, KPAD_STATUS_ARRAY_SIZE, &err);
    }

    for (s32 chan = WPAD_CHAN0; chan < WPAD_MAX_CONTROLLERS; chan++) {
        mReadDataInfoArray2[chan].copy(mReadDataInfoArray[chan]);
    }

    readPadData();
}

void WPadHolder::updateProjectPadData() {
    for (u32 i = 0; i < ARRAY_SIZE(mPad); i++) {
        mPad[i]->update();
    }
}

void WPadHolder::updateInHomeButton() {
    for (u32 i = 0; i < ARRAY_SIZE(mPad); i++) {
        mPad[i]->updateInHomeButton();
    }
}

void WPadHolder::updateInGame() {
    for (s32 chan = WPAD_CHAN2; chan < WPAD_MAX_CONTROLLERS; chan++) {
        KPADStatus* pStatus = mReadDataInfoArray2[chan].getKPadStatus(0);

        if (pStatus == nullptr) {
            continue;
        }

        if (pStatus->wpad_err != WPAD_ERR_NONE) {
            continue;
        }

        WPADDisconnect(chan);
    }
}

void WPadHolder::update() {
    updateReadDataOnly();

    if (isUpdateInHomeButton()) {
        updateInHomeButton();
    } else {
        updateProjectPadData();
    }

    if (mMode == 1) {
        updateInGame();
    }
}

void WPadHolder::initSensorBarPosition() {
    u8 sensorBarPosition = WPADGetSensorBarPosition();
    f32 level = 0.0f;

    switch (sensorBarPosition) {
    case WPAD_SENSOR_BAR_POS_TOP:
        level = 0.35f;
        break;
    case WPAD_SENSOR_BAR_POS_BOTTOM:
        level = -0.15f;
        break;
    }

    for (u32 i = 0; i < ARRAY_SIZE(mPad); i++) {
        mPad[i]->mPointer->setSensorBarLevel(level);
    }
}

WPad* WPadHolder::getWPad(s32 chan) {
    if (static_cast<u32>(chan) < 2) {
        return mPad[chan];
    }

    return nullptr;
}

void WPadHolder::setConnectCallback() {
    for (s32 chan = WPAD_CHAN0; chan < WPAD_MAX_CONTROLLERS; chan++) {
        KPADSetConnectCallback(chan, WPad::connectCallback);
        WPADSetExtensionCallback(chan, WPad::extensionCallback);
    }
}

void WPadHolder::readPadData() {
    if (isUpdatePad()) {
        for (s32 chan = WPAD_CHAN0; chan < WPAD_MAX_CONTROLLERS; chan++) {
            MR::readPadData(chan, &mReadDataInfoArray2[chan]);
        }
    }
}

namespace {
    WPadHolder* getWPadHolder() NO_INLINE {
        return SingletonHolder< GameSystem >::get()->mObjHolder->mWPadHolder;
    }
}  // namespace

namespace MR {
    WPad* getWPad(s32 chan) {
        return ::getWPadHolder()->getWPad(chan);
    }

    void setWPadHolderModeHomeButton() {
        WPadHolder* pHolder = ::getWPadHolder();
        pHolder->mMode = 0;
    }

    void setWPadHolderModeGame() {
        WPadHolder* pHolder = ::getWPadHolder();
        pHolder->mMode = 1;
    }

    u32 getHBMKPadData(HBMKPadData* pPadData, s32 chan) {
        u32 type;
        s32 err = WPADProbe(chan, &type);
        KPADStatus* pStatus = ::getWPadHolder()->mReadDataInfoArray[chan].mStatusArray;

        switch (err) {
        case WPAD_ERR_NONE:
        case WPAD_ERR_BUSY:
        case WPAD_ERR_TRANSFER:
            pPadData->kpad = pStatus;
            pPadData->pos = pStatus->pos;
            pPadData->use_devtype = pStatus->dev_type;
            break;
        default:
            pPadData->kpad = nullptr;
            break;
        }

        return type;
    }

    bool testHBMKPadTrigger(s32 chan, u32 mask) {
        return (::getWPadHolder()->mReadDataInfoArray[chan].mStatusArray->trig & mask) != 0;
    }
}  // namespace MR
