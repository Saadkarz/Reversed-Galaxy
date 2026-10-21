#include "JSystem/JAudio2/JASCallback.hpp"
#include <revolution/os/OSInterrupt.h>

bool JASCallbackMgr::regist(JASCallback* pCallback, void* pArgument) {
    BOOL status = OSDisableInterrupts();
    for (s32 i = 0; i < JASCALLBACK_MAX_CALLBACKS; i++) {
        if (mCallbacks[i].mCallback == nullptr) {
            mCallbacks[i].mCallback = pCallback;
            mCallbacks[i].mArg = pArgument;
            OSRestoreInterrupts(status);
            return true;
        }
    }

    OSRestoreInterrupts(status);
    return false;
}

s32 JASCallbackMgr::reject(JASCallback* pCallback, void* pArgument) {
    s32 rejectNum = 0;
    BOOL status = OSDisableInterrupts();
    for (s32 i = 0; i < JASCALLBACK_MAX_CALLBACKS; i++) {
        if (mCallbacks[i].mCallback == pCallback && mCallbacks[i].mArg == pArgument) {
            mCallbacks[i].mCallback = nullptr;
            mCallbacks[i].mArg = nullptr;
            rejectNum++;
        }
    }

    OSRestoreInterrupts(status);
    return rejectNum;
}

void JASCallbackMgr::callback() {
    for (s32 i = 0; i < JASCALLBACK_MAX_CALLBACKS; i++) {
        if (mCallbacks[i].mCallback != nullptr) {
            s32 result = mCallbacks[i].mCallback(mCallbacks[i].mArg);
            if (result < 0) {
                mCallbacks[i].mCallback = nullptr;
                mCallbacks[i].mArg = nullptr;
            }
        }
    }
}
