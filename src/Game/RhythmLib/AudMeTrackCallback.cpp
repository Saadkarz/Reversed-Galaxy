#include "Game/RhythmLib/AudMeTrackCallback.hpp"
#include <JSystem/JAudio2/JASCriticalSection.hpp>

AudCallback AudMeTrackCallback::sMeTrackCallback;

bool AudMeTrackCallback::regist(AudCallbackFunc pFunc, void* pData) {
    return sMeTrackCallback.regist(pFunc, pData);
}

void AudMeTrackCallback::callback(s32 type, s32 time) {
    sMeTrackCallback.callback(type, time);
}
