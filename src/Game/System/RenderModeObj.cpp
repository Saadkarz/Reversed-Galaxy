#include "Game/System/RenderMode.hpp"
#include <revolution/vi.h>

u32 RenderModeObj::getViWidthMax() {
    switch (VIGetTvFormat()) {
    case VI_PAL:
        return VI_MAX_WIDTH_PAL;
    case VI_MPAL:
        return VI_MAX_WIDTH_MPAL;
    case VI_EURGB60:
        return VI_MAX_WIDTH_EURGB60;
    case VI_NTSC:
    default:
        return VI_MAX_WIDTH_NTSC;
    }
}
