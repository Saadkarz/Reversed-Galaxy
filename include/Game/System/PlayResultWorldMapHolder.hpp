#pragma once

#include "Game/NameObj/NameObj.hpp"

struct WorldMapResultData {
    WorldMapResultData();

    u8 _0[0x400];
    u32 _400;
};

class PlayResultWorldMapHolder : public NameObj {
public:
    PlayResultWorldMapHolder();
    virtual ~PlayResultWorldMapHolder();

    void reset();

    /* 0x12 */ u8 _12[2];
    /* 0x14 */ s32 _14;
    /* 0x18 */ s32 _18;
    /* 0x1C */ s32 _1C;
    /* 0x20 */ u8 mArray[8][64];
    /* 0x220 */ WorldMapResultData* mData;
    /* 0x224 */ bool _224;
    /* 0x225 */ bool _225;
    /* 0x228 */ s32 _228;
    /* 0x22C */ bool _22C;
    /* 0x22D */ bool _22D;
};

extern "C" {
    void fn_804C96B0(PlayResultWorldMapHolder*, s32);
    void fn_804C96C0(PlayResultWorldMapHolder*, s32);
    void fn_804C96D0(PlayResultWorldMapHolder*, s32, s32);
    u8 fn_804C96F0(const PlayResultWorldMapHolder*, s32, s32);
    void fn_804C9710(PlayResultWorldMapHolder*);
    void fn_804C9750(PlayResultWorldMapHolder*, const WorldMapResultData*);
    void fn_804C9760(WorldMapResultData*, const WorldMapResultData*);
    void fn_804C9790(const PlayResultWorldMapHolder*, WorldMapResultData*);
    void fn_804C97A0(PlayResultWorldMapHolder*);
}
