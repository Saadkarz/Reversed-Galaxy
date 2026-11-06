#include "Game/System/PlayResultInStageHolder.hpp"
#include "Game/System/GalaxyStatusAccessor.hpp"
#include "Game/System/GameDataFunction.hpp"
#include "Game/System/ScenarioDataParser.hpp"
#include "Game/Util/MemoryUtil.hpp"
#include "Game/Util/SceneUtil.hpp"
#include "Game/Util/StringUtil.hpp"

namespace MR {
    s32 clamp(s32, s32, s32);
};

PlayResultInStageHolder::PlayResultInStageHolder()
    : NameObj("プレイ結果保持[ステージ中]"),
      _42(false),
      _43(false),
      _44(false),
      mClearedPowerStarNum(-1),
      mStarPieceNum(0),
      _50(0),
      mCoinNum(0),
      _58(0),
      mPurpleCoinNum(0),
      _60(false),
      _61(false),
      _62(false),
      _64(0),
      _68(false),
      mStartIdInfo(nullptr),
      _70(0),
      _74(true),
      _75(false),
      _76(false),
      mPlayerHealth(3),
      _7C(0),
      _80(false),
      mPadMode(0),
      _88(false),
      mList1(),
      mList2() {
    MR::zeroMemory(mStageName, sizeof(mStageName));
    mStartIdInfo = new JMapIdInfo();
    mList1.mRecords = new PlayResultRecord[64];
    mList1.mCapacity = 64;
    mList2.mRecords = new PlayResultRecord[64];
    mList2.mCapacity = 64;
}

PlayResultRecord::PlayResultRecord() : _0(0), _4(0) {
}

PlayResultRecordList::PlayResultRecordList()
    : mRecords(nullptr), mCapacity(0), mCount(0) {
}

void PlayResultInStageHolder::reset() {
    MR::zeroMemory(mStageName, sizeof(mStageName));
    _42 = false;
    _43 = false;
    _44 = false;
    mClearedPowerStarNum = -1;
    mStarPieceNum = 0;
    _50 = 0;
    mCoinNum = 0;
    _58 = 0;
    mPurpleCoinNum = 0;
    _60 = false;
    _61 = false;
    _62 = false;
    _64 = 0;
    _68 = false;
    *mStartIdInfo = *MR::getInitializeStartIdInfo();
    _70 = 0;
    _74 = true;
    _75 = false;
    _76 = GameDataFunction::isOnGameEventFlag("でしゃばりルイージ出現中");
    mPlayerHealth = 3;
    _7C = 0;
    _80 = false;
    mPadMode = 0;
    _88 = false;
    mList1.mCount = 0;
    mList2.mCount = 0;

    for (ScenarioDataIter iter = MR::makeBeginScenarioDataIter(); !iter.isEnd(); iter.goNext()) {
        const char* name = iter.makeAccessor().getName();
        mList1.add(PlayResultRecord((s32)name, MR::fn_80024F60(name)));
    }
}

void PlayResultInStageHolder::fn_804C8E90() {
    _42 = false;
    mClearedPowerStarNum = -1;
    mPurpleCoinNum = 0;
    _75 = false;
}

void PlayResultInStageHolder::setStageName(const char* name) {
    MR::copyString(mStageName, name, sizeof(mStageName));
}

const char* PlayResultInStageHolder::getStageName() const {
    return mStageName;
}

void PlayResultInStageHolder::fn_804C8ED0() {
    s32 starNum = mClearedPowerStarNum;
    const char* pStageName = getStageName();

    _42 = true;
    _43 = !GameDataFunction::hasPowerStar(pStageName, starNum);

    if (_43) {
        _44 = !_88 && !MR::makeGalaxyStatusAccessor(pStageName).isGreenStar(starNum);
    } else {
        _44 = !_88 && MR::isPowerStarBronze(pStageName, starNum);
    }

    if (_64 != 0 && _64 < 216000 && !_88) {
        u32 bestTime = GameDataFunction::fn_804D3D10(pStageName, starNum);
        _68 = bestTime != 0 && _64 < bestTime;
    } else {
        _64 = 0;
    }
}

void PlayResultInStageHolder::setClearedPowerStarNum(s32 num) {
    mClearedPowerStarNum = num;
}

s32 PlayResultInStageHolder::getClearedPowerStarNum() const {
    return mClearedPowerStarNum;
}

bool PlayResultInStageHolder::addStarPieceNum(s32 count) {
    mStarPieceNum = MR::clamp(mStarPieceNum + count, 0, 999);
    s32 next = _50 + 100;
    bool ret = false;
    if (next <= mStarPieceNum) {
        ret = true;
        _50 = next;
    }
    return ret;
}

s32 PlayResultInStageHolder::getClearedStarPieceNum() const {
    return MR::clamp(mStarPieceNum, 0, 999);
}

bool PlayResultInStageHolder::addCoinNum(s32 count) {
    mCoinNum = MR::clamp(mCoinNum + count, 0, 999);
    return false;
}

s32 PlayResultInStageHolder::getClearedCoinNum() const {
    return MR::clamp(mCoinNum, 0, 999);
}

bool PlayResultInStageHolder::incPurpleCoinNum() {
    return ++mPurpleCoinNum == 100;
}

s32 PlayResultInStageHolder::getPurpleCoinNum() const {
    return MR::clamp(mPurpleCoinNum, 0, 999);
}

void PlayResultInStageHolder::setCollectTicoCoinSaved() {
    _61 = true;
    _62 = !GameDataFunction::isOnGalaxyFlagTicoCoin(mStageName);
}

void PlayResultInStageHolder::fn_804C9170() {
    for (s32 i = 0; i < mList1.mCount; i++) {
        const PlayResultRecord& rec = mList1.mRecords[i];
        if (rec._4 == 0) {
            const char* name = (const char*)rec._0;
            if (MR::fn_80024F60(name)) {
                mList2.add(PlayResultRecord((s32)name, 1));
            }
        }
    }
}

bool PlayResultInStageHolder::fn_804C9200(const char* name) const {
    for (s32 i = 0; i < mList2.mCount; i++) {
        if (MR::isEqualString((const char*)mList2.mRecords[i]._0, name)) {
            return true;
        }
    }
    return false;
}

void PlayResultInStageHolder::setRestartMarioNo(const JMapIdInfo& info) {
    *mStartIdInfo = info;
}

void PlayResultInStageHolder::clearAfterMiss() {
    _70++;
    fn_804C92A0();
}

void PlayResultInStageHolder::fn_804C92A0() {
    mCoinNum = 0;
    _58 = 0;
    _74 = false;
    mPlayerHealth = 3;
    _88 = false;
    _60 = false;
    if (mPadMode != 0) {
        mPadMode = 0;
    }
}

s32 PlayResultInStageHolder::getPlayerHealth() const {
    if (MR::isStageMarioFaceShipOrWorldMap()) {
        return 3;
    }
    return mPlayerHealth;
}

void PlayResultInStageHolder::fn_804C9320(s32 health) {
    _7C = health;
}

void PlayResultInStageHolder::setPadModeDreamer() {
    mPadMode = 1;
    _74 = false;
    mPlayerHealth = MR::getPlayerLife();
}

void PlayResultInStageHolder::setPadModeSuperDreamer() {
    mPadMode = 2;
    _88 = true;
    _74 = false;
    mPlayerHealth = (MR::getPlayerLife() > 3) ? 6 : 3;
}

void PlayResultInStageHolder::clearPadMode() {
    mPadMode = 0;
}

void PlayResultRecordList::add(const PlayResultRecord& record) {
    s32 count = mCount;
    mCount = count + 1;
    mRecords[count] = record;
}

PlayResultRecordList::~PlayResultRecordList() {
    if (mRecords != nullptr) {
        delete[] mRecords;
    }
}

extern "C" {
    void __dt__20PlayResultRecordListFv();
    void __dt__7NameObjFv();
    void __dl__FPv();
}

asm PlayResultInStageHolder::~PlayResultInStageHolder() {
    nofralloc
    stwu r1, -0x10(r1)
    mflr r0
    cmpwi r3, 0
    stw r0, 0x14(r1)
    stw r31, 0xc(r1)
    mr r31, r4
    stw r30, 0x8(r1)
    mr r30, r3
    beq loc_70
    addic. r3, r3, 0x98
    beq loc_34
    li r4, -1
    bl __dt__20PlayResultRecordListFv
loc_34:
    addic. r3, r30, 0x8c
    beq loc_48
    li r4, -1
    bl __dt__20PlayResultRecordListFv
loc_48:
    mr r3, r30
    li r4, 0
    bl __dt__7NameObjFv
    cmpwi r31, 0
    ble loc_70
    mr r3, r30
    bl __dl__FPv
loc_70:
    mr r3, r30
    lwz r31, 0xc(r1)
    lwz r30, 0x8(r1)
    lwz r0, 0x14(r1)
    mtlr r0
    addi r1, r1, 0x10
    blr
}

