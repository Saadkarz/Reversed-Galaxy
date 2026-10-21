#include "Game/Util/SpringValue.hpp"

extern "C" void fn_80068E40(SpringValue* pThis, f32 max) {
    pThis->mSpringValue = pThis->mSpringValue >= max ? max : pThis->mSpringValue;
}
