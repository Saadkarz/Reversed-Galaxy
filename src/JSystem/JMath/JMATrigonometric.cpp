#include "JSystem/JMath/JMATrigonometric.hpp"

namespace JMath {
    template < >
    f32 TAtanTable< 1024, f32 >::atan2_(f32 y, f32 x) const {
        (void)0.0f;
        (void)1.5707964f;
        (void)0.5f;
        (void)1024.0f;
        (void)-1.5707964f;
        (void)3.1415927f;
        (void)-3.1415927f;
        (void)0.7853982f;

        if (y >= 0.0f) {
            if (x >= 0.0f) {
                if (x >= y) {
                    return get_(y, x);
                }
                return TAngleConstant_< f32 >::RADIAN_DEG090() - get_(x, y);
            }
            x = -x;
            if (x < y) {
                return TAngleConstant_< f32 >::RADIAN_DEG090() + get_(x, y);
            }
            return TAngleConstant_< f32 >::RADIAN_DEG180() - get_(y, x);
        }
        f32 negY = -y;
        if (x < 0.0f) {
            x = -x;
            if (x >= negY) {
                return -TAngleConstant_< f32 >::RADIAN_DEG180() + get_(negY, x);
            }
            return -TAngleConstant_< f32 >::RADIAN_DEG090() - get_(x, negY);
        }
        if (x < negY) {
            return -TAngleConstant_< f32 >::RADIAN_DEG090() + get_(x, negY);
        }
        return -get_(negY, x);
    }

    template < >
    f32 TAtanTable< 1024, f32 >::get_(f32 y, f32 x) const {
        if (x == 0.0f) {
            return 0.0f;
        }
        return mTable[static_cast< s32 >(0.5f + 1024.0f * y / x)];
    }

    TSinCosTable< 14, f32 > sSinCosTable;
    TAtanTable< 1024, f32 > sAtanTable ATTRIBUTE_ALIGN(32);
    TAsinAcosTable< 1024, f32 > sAsinAcosTable ATTRIBUTE_ALIGN(32);
}
