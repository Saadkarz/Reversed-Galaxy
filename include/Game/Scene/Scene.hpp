#pragma once

#include "Game/System/NerveExecutor.hpp"

class Scene : public NerveExecutor {
public:
    Scene(const char*);
    virtual ~Scene();
};
