#pragma once

#include <revolution.h>

class LiveActor;

struct ParamMove {
    f32 mParam00;
    f32 mParam01;
    f32 mParam02;
    f32 mParam03;
};

struct ParamSight {
    f32 mParam00;
    f32 mParam01;
    f32 mParam02;
};

struct ParamRebound {
    f32 mParam00;
    f32 mParam01;
    f32 mParam02;
};

struct ParamJump {
    f32 mParam00;
    f32 mParam01;
};

class ActorParam {
public:
    struct Param {
        Param();

        const char* mName;
        s32 mType;
        void* mValue;
    };

    ActorParam(LiveActor* pActor);

    static ActorParam* tryCreate(LiveActor* pActor);

    const s32& getS32(const char* pName) const;
    const f32& getF32(const char* pName) const;
    const ParamMove& getParamMove(const char* pName) const;
    const ParamJump& getParamJump(const char* pName) const;
    const ParamSight& getParamSight(const char* pName) const;

    const Param* findParam(const char* pName) const;

    s32 mNumParams;
    Param* mParams;
};
