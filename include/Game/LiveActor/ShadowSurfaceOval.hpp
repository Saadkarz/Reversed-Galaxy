#pragma once

#include "Game/LiveActor/ShadowSurfaceDrawer.hpp"
#include "Game/Util/Color.hpp"
#include <JSystem/JGeometry/TVec.hpp>

class J3DModelData;

class ShadowSurfaceOval : public ShadowSurfaceDrawer {
public:
    ShadowSurfaceOval();

    virtual ~ShadowSurfaceOval();

    virtual void draw() const;

    void setSize(const TVec3f&);
    void setColor(Color8);
    void setAlpha(u8);

    /* 0x14 */ J3DModelData* mModelData;
    /* 0x18 */ TVec3f mSize;
    /* 0x24 */ Color8 mColor;
};
