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

extern "C" {
    bool hasPowerStar__16GameDataFunctionFPCcl(const char*, s32);
    void makeGalaxyStatusAccessor__2MRFPCc(const char*);
    bool isGreenStar__20GalaxyStatusAccessorCFl(void*, s32);
    bool isPowerStarBronze__2MRFPCcl(const char*, s32);
    s32 fn_804D3D10__16GameDataFunctionFPCcl(const char*, s32);
    void _savegpr_27();
    void _restgpr_27();
}

asm void PlayResultInStageHolder::fn_804C8ED0() {
    nofralloc
    stwu r1, -0x30(r1)
    mflr r0
    stw r0, 0x34(r1)
    addi r11, r1, 0x30
    bl _savegpr_27
    lwz r28, 0x48(r3)
    li r30, 1
    stb r30, 0x42(r3)
    addi r29, r3, 0x12
    mr r27, r3
    mr r4, r28
    mr r3, r29
    bl hasPowerStar__16GameDataFunctionFPCcl
    cntlzw r0, r3
    srwi. r0, r0, 5
    stb r0, 0x43(r27)
    beq loc_else
    lbz r0, 0x88(r27)
    li r30, 0
    cmpwi r0, 0
    bne loc_set_44_1
    mr r3, r29
    bl makeGalaxyStatusAccessor__2MRFPCc
    stw r3, 0x8(r1)
    mr r4, r28
    addi r3, r1, 0x8
    bl isGreenStar__20GalaxyStatusAccessorCFl
    cmpwi r3, 0
    bne loc_set_44_1
    li r30, 1
loc_set_44_1:
    stb r30, 0x44(r27)
    b loc_after_44
loc_else:
    lbz r0, 0x88(r27)
    li r31, 0
    cmpwi r0, 0
    bne loc_set_44_2
    mr r3, r29
    mr r4, r28
    bl isPowerStarBronze__2MRFPCcl
    cmpwi r3, 0
    beq loc_set_44_2
    mr r31, r30
loc_set_44_2:
    stb r31, 0x44(r27)
loc_after_44:
    lwz r4, 0x64(r27)
    cmpwi r4, 0
    beq loc_zero_64
    lis r3, 0x3
    addi r0, r3, 0x4bc0
    cmplw r4, r0
    bge loc_zero_64
    lbz r0, 0x88(r27)
    cmpwi r0, 0
    bne loc_zero_64
    mr r3, r29
    mr r4, r28
    bl fn_804D3D10__16GameDataFunctionFPCcl
    cmpwi r3, 0
    li r4, 0
    beq loc_set_68
    lwz r0, 0x64(r27)
    cmplw r0, r3
    bge loc_set_68
    li r4, 1
loc_set_68:
    stb r4, 0x68(r27)
    b loc_exit
loc_zero_64:
    li r0, 0
    stw r0, 0x64(r27)
loc_exit:
    addi r11, r1, 0x30
    bl _restgpr_27
    lwz r0, 0x34(r1)
    mtlr r0
    addi r1, r1, 0x30
    blr
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

