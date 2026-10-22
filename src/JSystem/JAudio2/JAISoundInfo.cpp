#include "JSystem/JAudio2/JAISoundInfo.hpp"

JAISoundInfo::JAISoundInfo(bool set) : JASGlobalInstance< JAISoundInfo >(set) {
}

template <>
JASGlobalInstance< JAISoundInfo >::~JASGlobalInstance() {
    if (sInstance == (JAISoundInfo*)this) {
        sInstance = nullptr;
    }
}

JAISoundInfo::~JAISoundInfo() {
}
