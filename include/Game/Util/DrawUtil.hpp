#pragma once

#include <JSystem/JGeometry/TVec.hpp>
#include <revolution/gx.h>

class J3DModelData;
class J3DModel;
class J3DMaterial;
class JUTTexture;

namespace MR {
    void drawSimpleModel(J3DModelData*);
    const TVec3f& getMarioShadowVec();
};  // namespace MR
