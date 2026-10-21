#pragma once

#include "Game/NameObj/NameObj.hpp"
#include "Game/Util/Array.hpp"
#include "Game/Util/JMapIdInfo.hpp"
#include <revolution/types.h>

struct PlayResultRecord {
    inline PlayResultRecord() : _0(0), _4(0) {}
    inline PlayResultRecord(s32 a, u8 b) : _0(a), _4(b) {}

    /* 0x0 */ s32 _0;
    /* 0x4 */ u8 _4;
};

struct PlayResultRecordList {
    PlayResultRecordList();
    ~PlayResultRecordList();
    void add(const PlayResultRecord&);

    /* 0x0 */ PlayResultRecord* mRecords;
    /* 0x4 */ s32 mCapacity;
    /* 0x8 */ s32 mCount;
};

class PlayResultInStageHolder : public NameObj {
public:
    PlayResultInStageHolder();
    virtual ~PlayResultInStageHolder();

    void reset();
    void fn_804C8E90();
    void setStageName(const char*);
    const char* getStageName() const;
    void fn_804C8ED0();
    void setClearedPowerStarNum(s32);
    s32 getClearedPowerStarNum() const;
    bool addStarPieceNum(s32);
    s32 getClearedStarPieceNum() const;
    bool addCoinNum(s32);
    s32 getClearedCoinNum() const;
    bool incPurpleCoinNum();
    s32 getPurpleCoinNum() const;
    void setCollectTicoCoinSaved();
    void fn_804C9170();
    bool fn_804C9200(const char*) const;
    void setRestartMarioNo(const JMapIdInfo&);
    void clearAfterMiss();
    void fn_804C92A0();
    s32 getPlayerHealth() const;
    void fn_804C9320(s32);
    void setPadModeDreamer();
    void setPadModeSuperDreamer();
    void clearPadMode();

    /* 0x12 */ char mStageName[48];
    /* 0x42 */ bool _42;
    /* 0x43 */ bool _43;
    /* 0x44 */ bool _44;
    /* 0x48 */ s32 mClearedPowerStarNum;
    /* 0x4C */ s32 mStarPieceNum;
    /* 0x50 */ s32 _50;
    /* 0x54 */ s32 mCoinNum;
    /* 0x58 */ s32 _58;
    /* 0x5C */ s32 mPurpleCoinNum;
    /* 0x60 */ bool _60;
    /* 0x61 */ bool _61;
    /* 0x62 */ bool _62;
    /* 0x64 */ s32 _64;
    /* 0x68 */ bool _68;
    /* 0x6C */ JMapIdInfo* mStartIdInfo;
    /* 0x70 */ s32 _70;
    /* 0x74 */ bool _74;
    /* 0x75 */ bool _75;
    /* 0x76 */ bool _76;
    /* 0x78 */ s32 mPlayerHealth;
    /* 0x7C */ s32 _7C;
    /* 0x80 */ bool _80;
    /* 0x84 */ s32 mPadMode;
    /* 0x88 */ bool _88;
    /* 0x8C */ PlayResultRecordList mList1;
    /* 0x98 */ PlayResultRecordList mList2;
};
