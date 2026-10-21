#pragma once

#include <revolution/gx/GXStruct.h>
#include <revolution/types.h>

namespace MR {
    const GXRenderModeObj* getSuitableRenderMode();
    bool isAspectRatioFlag16Per9();
    u32 getRequiredExternalFrameBufferSize();
};  // namespace MR

class RenderModeObj {
public:
    static u32 getViWidthMax();
};
