#pragma once

#include "Game/LiveActor/LiveActor.hpp"

class ModelObj : public LiveActor {
public:
    ModelObj(const char*, const char*, MtxPtr, int, int, int, bool);

    virtual void init(const JMapInfoIter&);
    virtual void calcAndSetBaseMtx();

    /* 0x8C */ MtxPtr mMtx;
};
