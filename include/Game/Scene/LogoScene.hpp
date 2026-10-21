#pragma once

#include "Game/Scene/Scene.hpp"

class LogoScene : public Scene {
public:
    LogoScene();
    virtual ~LogoScene();

    bool isDisplayStrapRemineder() const;
};
