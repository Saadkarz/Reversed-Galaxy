#include "Game/System/PlayerHeapHolder.hpp"
#include "Game/Util/FileUtil.hpp"
#include "Game/Util/MemoryUtil.hpp"
#include <JSystem/JKernel/JKRExpHeap.hpp>

bool ConditionIfIsNotStationedPlayer::isExecute(const MR::StationedFileInfo* pInfo) const {
    s32 type = pInfo->mLoadType;
    if ((u32)(type - 2) <= 2 || type == 6 || type == 8) {
        return false;
    }
    return true;
}

JKRHeap* ConditionIfIsNotStationedPlayer::getProperHeap(const MR::StationedFileInfo*) const {
    return nullptr;
}

bool ConditionIfIsNotPlayer::isExecute(const MR::StationedFileInfo* pInfo) const {
    s32 type = pInfo->mLoadType;
    if ((u32)(type - 3) <= 2 || (u32)type <= 1 || type == 7) {
        return false;
    }
    return true;
}

JKRHeap* ConditionIfIsNotPlayer::getProperHeap(const MR::StationedFileInfo*) const {
    return nullptr;
}

ConditionUsePlayerHeap::ConditionUsePlayerHeap() : mNapaHeap(nullptr), mGDDRHeap(nullptr), mIsDataMario(true) {
}

bool ConditionUsePlayerHeap::isExecute(const MR::StationedFileInfo* pInfo) const {
    s32 type = 4;
    if (mIsDataMario) {
        type = 3;
    }
    return pInfo->mLoadType == type;
}

JKRHeap* ConditionUsePlayerHeap::getProperHeap(const MR::StationedFileInfo* pInfo) const {
    switch (pInfo->mHeapType) {
    case MR::StationedFileInfo::HEAP_TYPE_NAPA:
        return mNapaHeap;
    case MR::StationedFileInfo::HEAP_TYPE_GDDR:
        return mGDDRHeap;
    case MR::StationedFileInfo::HEAP_TYPE_NONE:
        return nullptr;
    default:
        return nullptr;
    }
}

PlayerHeapHolder::PlayerHeapHolder() : mCondition(nullptr), mNapaHeap(nullptr), mGDDRHeap(nullptr), mIsDataMario(true) {
    ConditionUsePlayerHeap* condition = new ConditionUsePlayerHeap();
    mNapaHeap = PlayerHeapHolder::createHeap(0x200000, MR::getStationedHeapNapa());
    JKRExpHeap* gddr = PlayerHeapHolder::createHeap(0x500000, MR::getStationedHeapGDDR3());
    mGDDRHeap = gddr;
    condition->mNapaHeap = mNapaHeap;
    condition->mGDDRHeap = gddr;
    mCondition = condition;
    condition->mIsDataMario = mIsDataMario;
}

ConditionUsePlayerHeap* PlayerHeapHolder::getCondition() const {
    return mCondition;
}

void PlayerHeapHolder::adjust() {
    JKRExpHeap* napa = mNapaHeap;
    if (!napa->isEmpty()) {
        napa->alloc(0x10000, 0);
    }

    JKRExpHeap* gddr = mGDDRHeap;
    if (!gddr->isEmpty()) {
        gddr->alloc(0x10000, 0);
    }

    MR::adjustHeapSize(mNapaHeap);
    MR::adjustHeapSize(mGDDRHeap);
}

void PlayerHeapHolder::dispose() {
    MR::removeResourceAndFileHolderIfIsEqualHeap(mNapaHeap);
    MR::removeResourceAndFileHolderIfIsEqualHeap(mGDDRHeap);

    if (mNapaHeap->mSize != 0) {
        mNapaHeap->freeAll();
    }

    if (mGDDRHeap->mSize != 0) {
        mGDDRHeap->freeAll();
    }
}

void PlayerHeapHolder::setIsDataMario(bool isDataMario) {
    mIsDataMario = isDataMario;
    mCondition->mIsDataMario = isDataMario;
}

JKRExpHeap* PlayerHeapHolder::createHeap(u32 size, JKRHeap* pParent) {
    if (pParent->getMaxAllocatableSize(0x10) < size) {
        size = -1;
    }

    return JKRExpHeap::create(size, pParent, true);
}

ConditionUsePlayerHeap::~ConditionUsePlayerHeap() {
}
