#include "Game/Util/Color8.hpp"

Color8::Color8(_GXColor color) {
    _GXColor c = color;
    mR = c.r;
    mG = c.g;
    mB = c.b;
    mA = c.a;
}
