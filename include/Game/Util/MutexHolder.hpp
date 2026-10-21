#pragma once

#include <revolution/os/OSMutex.h>

class JKRHeap;

namespace MR {
    template < int T >
    class MutexHolder {
    public:
        static OSMutex sMutex;
    };

    template < int T >
    OSMutex MutexHolder< T >::sMutex;

    template <>
    class MutexHolder< 0 > {
    public:
        static OSMutex sMutex;
    };
};  // namespace MR
