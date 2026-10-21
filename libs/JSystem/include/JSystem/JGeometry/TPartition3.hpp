#pragma once

#include "JSystem/JGeometry/TVec.hpp"

namespace JGeometry {
    template < typename T >
    class TPartition3 {
    public:
        void set(const TVec3< T >& rFirst, const TVec3< T >& rSecond, const TVec3< T >& rThird);

        void set(const TVec3< T >& rNormal, const TVec3< T >& rPoint) __attribute__((noinline));

        TVec3< T > mNormal;  // 0x0
        T mDot;              // 0xC
    };

    template < typename T >
    void TPartition3< T >::set(const TVec3< T >& rFirst, const TVec3< T >& rSecond, const TVec3< T >& rThird) {
        TVec3< T > secondEdge;
        TVec3< T > firstEdge;
        firstEdge.sub(rSecond, rFirst);
        secondEdge.sub(rThird, rSecond);
        mNormal.cross(secondEdge, firstEdge);
        mNormal.normalize();
        mDot = mNormal.dot(rFirst);
    }

    template < typename T >
    void TPartition3< T >::set(const TVec3< T >& rNormal, const TVec3< T >& rPoint) {
        mNormal.x = rNormal.x;
        mNormal.y = rNormal.y;
        mNormal.z = rNormal.z;
        mDot = mNormal.dot(rPoint);
    }
};  // namespace JGeometry
