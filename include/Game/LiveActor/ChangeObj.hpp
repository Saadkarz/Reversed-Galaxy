#pragma once

#include "Game/NameObj/NameObj.hpp"
#include "Game/Util/Array.hpp"
#include "Game/Util/JMapInfo.hpp"

class LiveActor;

class ChangeObj {
public:
    virtual ~ChangeObj();
    virtual void doChange(ChangeObj*) = 0;

    void changeTRSVGFromOther(const ChangeObj*);

    LiveActor* mActor;
};

class ChangeObjTag;

class ChangeObjHolder : public NameObj {
public:
    ChangeObjHolder(const char*);

    virtual ~ChangeObjHolder();
    virtual void init(const JMapInfoIter&);

    void registerObj(ChangeObj*, const JMapInfoIter&);

    MR::Vector<MR::AssignableArray<ChangeObjTag*> > mGroups;
};

namespace MR {
    void registerChangeObj(ChangeObj*, const JMapInfoIter&);
};
