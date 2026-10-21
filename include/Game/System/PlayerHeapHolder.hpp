#pragma once

#include "Game/System/StationedArchiveLoader.hpp"

class JKRExpHeap;

namespace MR {
    void removeResourceAndFileHolderIfIsEqualHeap(JKRHeap* pHeap);
}

class ConditionIfIsNotStationedPlayer : public StationedArchiveLoader::Condition {
public:
    virtual bool isExecute(const MR::StationedFileInfo*) const;
    virtual JKRHeap* getProperHeap(const MR::StationedFileInfo*) const;
    virtual ~ConditionIfIsNotStationedPlayer();
};

class ConditionIfIsNotPlayer : public StationedArchiveLoader::Condition {
public:
    virtual bool isExecute(const MR::StationedFileInfo*) const;
    virtual JKRHeap* getProperHeap(const MR::StationedFileInfo*) const;
    virtual ~ConditionIfIsNotPlayer();
};

class ConditionUsePlayerHeap : public StationedArchiveLoader::Condition {
public:
    ConditionUsePlayerHeap();
    virtual ~ConditionUsePlayerHeap();

    virtual bool isExecute(const MR::StationedFileInfo*) const;
    virtual JKRHeap* getProperHeap(const MR::StationedFileInfo*) const;

    /* 0x4 */ JKRExpHeap* mNapaHeap;
    /* 0x8 */ JKRExpHeap* mGDDRHeap;
    /* 0xC */ bool mIsDataMario;
};

class PlayerHeapHolder {
public:
    PlayerHeapHolder();

    ConditionUsePlayerHeap* getCondition() const;
    void adjust();
    void dispose();
    void setIsDataMario(bool isDataMario);
    static JKRExpHeap* createHeap(u32 size, JKRHeap* pParent);

    /* 0x0 */ ConditionUsePlayerHeap* mCondition;
    /* 0x4 */ JKRExpHeap* mNapaHeap;
    /* 0x8 */ JKRExpHeap* mGDDRHeap;
    /* 0xC */ bool mIsDataMario;
};
