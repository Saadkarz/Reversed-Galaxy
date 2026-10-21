#include "Game/LiveActor/ActorParam.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/ObjUtil.hpp"
#include "Game/Util/StringUtil.hpp"

namespace {
    static const char* sActorParam = "ActorParam";

    static const ParamMove sDefaultParamMove = {0.0f, 0.0f, 0.0f, 0.0f};
    static const ParamSight sDefaultParamSight = {0.0f, 0.0f, 0.0f};
    static const ParamJump sDefaultParamJump = {0.0f, 0.0f};
}

static const f32 sDefaultF32 = 0.0f;
static const s32 sDefaultS32 = 0;

ActorParam::Param::Param() {
    mName = nullptr;
    mType = -1;
    mValue = nullptr;
}

ActorParam* ActorParam::tryCreate(LiveActor* pActor) {
    const ResourceHolder* rHolder = MR::getResourceHolder(pActor);
    if (rHolder == nullptr) {
        return nullptr;
    }

    if (MR::isExistFileInArc(rHolder, "%s.bcsv", sActorParam)) {
        return new ActorParam(pActor);
    }

    return nullptr;
}

const s32& ActorParam::getS32(const char* pName) const {
    const Param* p = findParam(pName);
    if (p != nullptr) {
        return *(const s32*)&p->mValue;
    }
    return sDefaultS32;
}

const f32& ActorParam::getF32(const char* pName) const {
    const Param* p = findParam(pName);
    if (p != nullptr) {
        return *(const f32*)&p->mValue;
    }
    return sDefaultF32;
}

const ParamMove& ActorParam::getParamMove(const char* pName) const {
    const Param* p = findParam(pName);
    if (p != nullptr) {
        return *(const ParamMove*)p->mValue;
    }
    return sDefaultParamMove;
}

const ParamJump& ActorParam::getParamJump(const char* pName) const {
    const Param* p = findParam(pName);
    if (p != nullptr) {
        return *(const ParamJump*)p->mValue;
    }
    return sDefaultParamJump;
}

const ParamSight& ActorParam::getParamSight(const char* pName) const {
    const Param* p = findParam(pName);
    if (p != nullptr) {
        return *(const ParamSight*)p->mValue;
    }
    return sDefaultParamSight;
}

ActorParam::ActorParam(LiveActor* pActor) {
    mNumParams = 0;
    mParams = nullptr;

    const ResourceHolder* rHolder = MR::getResourceHolder(pActor);
    JMapInfo* parser = MR::tryCreateCsvParser(rHolder, "%s.bcsv", sActorParam);
    s32 numElements = 0;
    if (parser != nullptr) {
        numElements = MR::getCsvDataElementNum(parser);
    }

    mNumParams = numElements;
    mParams = new Param[numElements];

    for (s32 i = 0; i < mNumParams; i++) {
        Param* param = &mParams[i];
        MR::getCsvDataStr(&param->mName, parser, "ParamName", i);
        const char* paramType = nullptr;
        MR::getCsvDataStr(&paramType, parser, "ParamType", i);

        if (MR::isEqualString(paramType, "s32")) {
            param->mType = 0;
            f32 val = 0.0f;
            MR::getCsvDataF32(&val, parser, "Param00", i);
            param->mValue = (void*)(s32)val;
        }
        else if (MR::isEqualString(paramType, "f32")) {
            param->mType = 1;
            MR::getCsvDataF32((f32*)&param->mValue, parser, "Param00", i);
        }
        else if (MR::isEqualString(paramType, "ParamMove")) {
            param->mType = 2;
            ParamMove* move = new ParamMove();
            MR::getCsvDataF32(&move->mParam00, parser, "Param00", i);
            MR::getCsvDataF32(&move->mParam01, parser, "Param01", i);
            MR::getCsvDataF32(&move->mParam02, parser, "Param02", i);
            MR::getCsvDataF32(&move->mParam03, parser, "Param03", i);
            param->mValue = move;
        }
        else if (MR::isEqualString(paramType, "ParamSight")) {
            param->mType = 4;
            ParamSight* sight = new ParamSight();
            MR::getCsvDataF32(&sight->mParam00, parser, "Param00", i);
            MR::getCsvDataF32(&sight->mParam01, parser, "Param01", i);
            MR::getCsvDataF32(&sight->mParam02, parser, "Param02", i);
            param->mValue = sight;
        }
        else if (MR::isEqualString(paramType, "ParamRebound")) {
            param->mType = 5;
            ParamRebound* rebound = new ParamRebound();
            MR::getCsvDataF32(&rebound->mParam00, parser, "Param00", i);
            MR::getCsvDataF32(&rebound->mParam01, parser, "Param01", i);
            MR::getCsvDataF32(&rebound->mParam02, parser, "Param02", i);
            param->mValue = rebound;
        }
        else if (MR::isEqualString(paramType, "ParamJump")) {
            param->mType = 3;
            ParamJump* jump = new ParamJump();
            MR::getCsvDataF32(&jump->mParam00, parser, "Param00", i);
            MR::getCsvDataF32(&jump->mParam01, parser, "Param01", i);
            param->mValue = jump;
        }
    }
}

const ActorParam::Param* ActorParam::findParam(const char* pName) const {
    const Param* p;
    for (s32 i = 0; i < mNumParams; i++) {
        p = &mParams[i];

        if (MR::isEqualString(p->mName, pName)) {
            return p;
        }
    }
    return nullptr;
}

