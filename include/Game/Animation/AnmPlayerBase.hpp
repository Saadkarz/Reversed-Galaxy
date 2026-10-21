#pragma once

#include <JSystem/J3DGraphAnimator/J3DAnimation.hpp>

class J3DAnmBase;
class J3DModelData;
class ResTable;

class AnmPlayerBase {
public:
    AnmPlayerBase(const ResTable*);
    ~AnmPlayerBase();

    virtual void changeAnimation(J3DAnmBase*);
    virtual void stopAnimation();

    void update();
    void reflectFrame();
    void start(const char*);
    void stop();
    bool isPlaying(const char*) const;

    /* 0x4 */ J3DAnmBase* mAnmRes;
    /* 0x8 */ const ResTable* mResTable;
    /* 0xC */ J3DFrameCtrl mFrameCtrl;
    /* 0x20 */ bool mWaitFirstFrame;
};

class MaterialAnmPlayerBase : public AnmPlayerBase {
public:
    MaterialAnmPlayerBase(const ResTable*, J3DModelData*);

    virtual void attach(J3DAnmBase*, J3DModelData*) = 0;
    virtual void detach(J3DAnmBase*, J3DModelData*) = 0;

    void beginDiff();
    void endDiff();

    /* 0x24 */ J3DModelData* mModelData;
};

extern "C" void fn_80069340(AnmPlayerBase* pPlayer);
extern "C" void fn_80069450(AnmPlayerBase* pPlayer);
