#pragma once

#include <revolution/types.h>

template < typename T >
class JASGlobalInstance {
public:
    static T* sInstance;

    JASGlobalInstance(bool setInstance) {
        if (setInstance) {
            sInstance = (T*)this;
        }
    }

    ~JASGlobalInstance();

    static T* getInstance() {
        return sInstance;
    }
};

template < typename T >
T* JASGlobalInstance< T >::sInstance;

template < typename T >
JASGlobalInstance< T >::~JASGlobalInstance() {
    if (sInstance == (T*)this) {
        sInstance = nullptr;
    }
}
