#pragma once

#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/Nerve.hpp"

class BreakModel : public LiveActor {
public:
    BreakModel(LiveActor*, const char*, const char*, MtxPtr, const char*);

    virtual ~BreakModel();
    virtual void init(const JMapInfoIter&);
    virtual void appear();
    virtual void calcAndSetBaseMtx();

    void exeBreak();

    /* 0x90 */ LiveActor* mHost;
    /* 0x94 */ const char* mActionName;
    /* 0x98 */ MtxPtr mMtx;
};

