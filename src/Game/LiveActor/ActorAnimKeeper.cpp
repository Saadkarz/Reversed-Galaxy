#include "Game/LiveActor/ActorAnimKeeper.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/System/ResourceHolder.hpp"
#include "Game/Util.hpp"
#include "Game/Util/ActorAnimUtil.hpp"
#include <cstdio>

namespace {
    const char* sFileName = "ActorAnimCtrl";
}

ActorAnimKeeper* ActorAnimKeeper::tryCreate(LiveActor* pActor) {
    const ResourceHolder* pResourceHolder = MR::getResourceHolder(pActor);

    if (pResourceHolder->mMotionResTable->mResourceNum == 0 &&
        pResourceHolder->mBtkResTable->mResourceNum == 0 &&
        pResourceHolder->mBrkResTable->mResourceNum == 0 &&
        pResourceHolder->mBpkResTable->mResourceNum == 0 &&
        pResourceHolder->mBtpResTable->mResourceNum == 0 &&
        pResourceHolder->mBvaResTable->mResourceNum == 0) {
        return nullptr;
    }

    if (MR::isExistFileInArc(pResourceHolder, "%s.bcsv", sFileName)) {
        return new ActorAnimKeeper(pActor);
    }

    return nullptr;
}

namespace {
    const char* getAnimName(const ActorAnimKeeperInfo* pKeeperInfo, const ActorAnimDataInfo& rDataInfo) {
        const char* name = rDataInfo.mName;
        if (name == nullptr) {
            name = pKeeperInfo->mName;
        }
        return name;
    }
}

bool ActorAnimKeeper::start(const char* pName) {
    ActorAnimKeeperInfo* info = findAnimInfo(pName);
    mCurrentInfo = info;
    if (mCurrentInfo == nullptr) {
        return false;
    }

    const char* BckName = ::getAnimName(info, info->mBckInfo);
    const char* BtkName = ::getAnimName(info, info->mBtkInfo);
    const char* BrkName = ::getAnimName(info, info->mBrkInfo);
    const char* BpkName = ::getAnimName(info, info->mBpkInfo);
    const char* BtpName = ::getAnimName(info, info->mBtpInfo);
    const char* BvaName = ::getAnimName(info, info->mBvaInfo);

    if (MR::isExistBck(mActor, BckName) && (!info->mBckInfo.mIsKeepAnim || !MR::isBckPlaying(mActor, BckName))) {
        if (MR::isEqualStringCase(BckName, info->mName)) {
            MR::startBck(mActor, BckName, nullptr);
        } else {
            MR::startBck(mActor, BckName, info->mName);
        }
    }

    if (MR::isExistBtk(mActor, BtkName) && (!info->mBtkInfo.mIsKeepAnim || !MR::isBtkPlaying(mActor, BtkName))) {
        MR::startBtk(mActor, BtkName);
    }

    if (MR::isExistBrk(mActor, BrkName) && (!info->mBrkInfo.mIsKeepAnim || !MR::isBrkPlaying(mActor, BrkName))) {
        MR::startBrk(mActor, BrkName);
    }

    if (MR::isExistBpk(mActor, BpkName) && (!info->mBpkInfo.mIsKeepAnim || !MR::isBpkPlaying(mActor, BpkName))) {
        MR::startBpk(mActor, BpkName);
    }

    if (MR::isExistBtp(mActor, BtpName) && (!info->mBtpInfo.mIsKeepAnim || !MR::isBtpPlaying(mActor, BtpName))) {
        MR::startBtp(mActor, BtpName);
    }

    if (MR::isExistBva(mActor, BvaName) && (!info->mBvaInfo.mIsKeepAnim || !MR::isBvaPlaying(mActor, BvaName))) {
        MR::startBva(mActor, BvaName);
    }

    return true;
}

void ActorAnimKeeper::update() {
}

bool ActorAnimKeeper::trySetAllFrame(f32 frame) {
    if (mCurrentInfo == nullptr) {
        return false;
    }

    const char* bck = ::getAnimName(mCurrentInfo, mCurrentInfo->mBckInfo);
    if (MR::isBckPlayingIfExist(mActor, bck)) {
        MR::setBckFrame(mActor, frame);
    }

    const char* btk = ::getAnimName(mCurrentInfo, mCurrentInfo->mBtkInfo);
    if (MR::isBtkPlayingIfExist(mActor, btk)) {
        MR::setBtkFrame(mActor, frame);
    }

    const char* brk = ::getAnimName(mCurrentInfo, mCurrentInfo->mBrkInfo);
    if (MR::isBrkPlayingIfExist(mActor, brk)) {
        MR::setBrkFrame(mActor, frame);
    }

    const char* bpk = ::getAnimName(mCurrentInfo, mCurrentInfo->mBpkInfo);
    if (MR::isBpkPlayingIfExist(mActor, bpk)) {
        MR::setBpkFrame(mActor, frame);
    }

    const char* btp = ::getAnimName(mCurrentInfo, mCurrentInfo->mBtpInfo);
    if (MR::isBtpPlayingIfExist(mActor, btp)) {
        MR::setBtpFrame(mActor, frame);
    }

    const char* bva = ::getAnimName(mCurrentInfo, mCurrentInfo->mBvaInfo);
    if (MR::isBvaPlayingIfExist(mActor, bva)) {
        MR::setBvaFrame(mActor, frame);
    }

    return true;
}

bool ActorAnimKeeper::isExistAnim(const char* pName) {
    if (findAnimInfo(pName) != nullptr) {
        return true;
    }
    return MR::isExistAnim(mActor, pName);
}

bool ActorAnimKeeper::isAnyAnimPlaying(const char* pName) {
    const ActorAnimKeeperInfo* currentInfo = mCurrentInfo;
    if (currentInfo) {
        if (!MR::isEqualStringCase(currentInfo->mName, pName)) {
            return false;
        }

        const char* bck = ::getAnimName(mCurrentInfo, mCurrentInfo->mBckInfo);
        if (MR::isExistBck(mActor, bck)) {
            return MR::isBckPlaying(mActor, bck);
        }

        if (MR::isBtkPlayingIfExist(mActor, ::getAnimName(mCurrentInfo, mCurrentInfo->mBtkInfo)) ||
            MR::isBrkPlayingIfExist(mActor, ::getAnimName(mCurrentInfo, mCurrentInfo->mBrkInfo)) ||
            MR::isBpkPlayingIfExist(mActor, ::getAnimName(mCurrentInfo, mCurrentInfo->mBpkInfo)) ||
            MR::isBtpPlayingIfExist(mActor, ::getAnimName(mCurrentInfo, mCurrentInfo->mBtpInfo)) ||
            MR::isBvaPlayingIfExist(mActor, ::getAnimName(mCurrentInfo, mCurrentInfo->mBvaInfo))) {
            return true;
        }

        return false;
    }

    return MR::isPlayingAnim(mActor, pName);
}

const char* ActorAnimKeeper::getCurrentAnimName() const {
    if (mCurrentInfo != nullptr) {
        return mCurrentInfo->mName;
    }
    return nullptr;
}

namespace {
    void getCsvDataAnimData(ActorAnimDataInfo* pDataInfo, const char* pPrefix, JMapInfo* pParser, s32 index) {
        char buffer[128];
        snprintf(buffer, sizeof(buffer), "%sName", pPrefix);
        MR::getCsvDataStrOrNULL(&pDataInfo->mName, pParser, buffer, index);
        snprintf(buffer, sizeof(buffer), "%sStartFrame", pPrefix);
        MR::getCsvDataF32(&pDataInfo->mStartFrame, pParser, buffer, index);
        snprintf(buffer, sizeof(buffer), "%sIsKeepAnim", pPrefix);
        MR::getCsvDataU8(&pDataInfo->mIsKeepAnim, pParser, buffer, index);
    }
}

ActorAnimKeeper::ActorAnimKeeper(LiveActor* pActor)
    : mActor(pActor), mNumInfo(0), mInfoArray(nullptr), mCurrentInfo(nullptr) {
    MR::getResourceHolder(pActor);
    initAnimData();
}

bool ActorAnimKeeper::initAnimData() {
    const ResourceHolder* pResourceHolder = MR::getResourceHolder(mActor);
    JMapInfo* parser = MR::tryCreateCsvParser(pResourceHolder, "%s.bcsv", sFileName);
    s32 num = 0;
    if (parser != nullptr) {
        num = MR::getCsvDataElementNum(parser);
    }
    mNumInfo = num;
    mInfoArray = new ActorAnimKeeperInfo[mNumInfo];
    for (s32 i = 0; i < mNumInfo; i++) {
        ActorAnimKeeperInfo* current = &mInfoArray[i];
        MR::getCsvDataStr(&current->mName, parser, "ActorAnimName", i);
        getCsvDataAnimData(&current->mBckInfo, "Bck", parser, i);
        getCsvDataAnimData(&current->mBtkInfo, "Btk", parser, i);
        getCsvDataAnimData(&current->mBrkInfo, "Brk", parser, i);
        getCsvDataAnimData(&current->mBpkInfo, "Bpk", parser, i);
        getCsvDataAnimData(&current->mBtpInfo, "Btp", parser, i);
        getCsvDataAnimData(&current->mBvaInfo, "Bva", parser, i);
    }
    return true;
}

ActorAnimKeeperInfo* ActorAnimKeeper::findAnimInfo(const char* pName) const {
    ActorAnimKeeperInfo* current;
    for (s32 i = 0; i < mNumInfo; i++) {
        current = &mInfoArray[i];
        if (MR::isEqualStringCase(current->mName, pName)) {
            return current;
        }
    }
    return nullptr;
}

namespace {
    const char sDataPad[2] = {0, 0};
}
