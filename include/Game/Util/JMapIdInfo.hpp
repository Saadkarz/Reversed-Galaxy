#pragma once

#include <revolution.h>

class JMapInfoIter;

class JMapIdInfo {
public:
    inline JMapIdInfo() : _0(-1), mZoneID(-1) {
    }

    

    JMapIdInfo(s32, s32);
    JMapIdInfo(s32, const JMapInfoIter&);

    void initialize(s32, const JMapInfoIter&);

    JMapIdInfo& operator=(const JMapIdInfo& rhs);

    inline bool operator==(const JMapIdInfo& rOther) const {
        bool ret = false;

        if (_0 == rOther._0 && mZoneID == rOther.mZoneID) {
            ret = true;
        }

        return ret;
    }

    int getZoneID() const {
        return mZoneID;
    }

    s32 _0;
    int mZoneID;  // 0x04
};

namespace MR {
    JMapIdInfo createJMapIdInfoFromGroupId(const JMapInfoIter&);
    JMapIdInfo createJMapIdInfoFromClippingGroupId(const JMapInfoIter&);
};  // namespace MR
