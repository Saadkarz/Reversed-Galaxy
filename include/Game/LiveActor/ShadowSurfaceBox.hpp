#pragma once

#include "Game/LiveActor/ShadowSurfaceDrawer.hpp"
#include <JSystem/JGeometry/TVec.hpp>

class ShadowSurfaceBox : public ShadowSurfaceDrawer {
public:
    ShadowSurfaceBox();

    virtual ~ShadowSurfaceBox();

    virtual void draw() const;

    void setSize(const TVec3f&);

    /* 0x14 */ TVec3f mSize;
};
