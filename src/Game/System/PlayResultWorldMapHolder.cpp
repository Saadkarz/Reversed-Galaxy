#include "Game/System/PlayResultWorldMapHolder.hpp"

PlayResultWorldMapHolder::PlayResultWorldMapHolder()
    : NameObj("プレイ結果保持[ワールドマップ]"),
      mData(nullptr) {
    mData = new WorldMapResultData();
    reset();
}

void PlayResultWorldMapHolder::reset() {
    _14 = 0;
    _18 = -1;
    _1C = 0;
    fn_804C9710(this);
    mData->_400 = 0;
    _224 = false;
    _225 = false;
    _22C = false;
    _22D = false;
    _228 = 5;
}

extern "C" {
    void fn_804C96B0(PlayResultWorldMapHolder* holder, s32 val) {
        holder->_18 = val;
    }

    void fn_804C96C0(PlayResultWorldMapHolder* holder, s32 val) {
        holder->_1C = val;
    }

    void fn_804C96D0(PlayResultWorldMapHolder* holder, s32 a, s32 b) {
        holder->mArray[a - 1][b] = 1;
    }

    u8 fn_804C96F0(const PlayResultWorldMapHolder* holder, s32 a, s32 b) {
        return holder->mArray[a - 1][b];
    }

    void fn_804C9710(PlayResultWorldMapHolder* holder) {
        for (u32 i = 0; i < 8; i++) {
            for (int j = 0; j < 64; j++) {
                holder->mArray[i][j] = 0;
            }
        }
    }

    void fn_804C9750(PlayResultWorldMapHolder* holder, const WorldMapResultData* other) {
        fn_804C9760(holder->mData, other);
    }

    void fn_804C9760(WorldMapResultData* dest, const WorldMapResultData* src) {
        *dest = *src;
    }

    void fn_804C9790(const PlayResultWorldMapHolder* holder, WorldMapResultData* dest) {
        fn_804C9760(dest, holder->mData);
    }

    void fn_804C97A0(PlayResultWorldMapHolder* holder) {
        holder->mData->_400 = 0;
    }
}

PlayResultWorldMapHolder::~PlayResultWorldMapHolder() {
}
