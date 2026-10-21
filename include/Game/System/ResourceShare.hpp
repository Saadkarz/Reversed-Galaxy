#pragma once

#include "Game/NameObj/NameObj.hpp"

class ResourceShare : public NameObj {
public:
    ResourceShare();
    virtual ~ResourceShare();

    void* mBuffer1;
    void* mBuffer2;
    u32 mUnk;
};
