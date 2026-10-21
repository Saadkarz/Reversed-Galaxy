#pragma once

#include "Game/System/NerveExecutor.hpp"

class GameSystemStationedArchiveLoader : public NerveExecutor {
public:
    GameSystemStationedArchiveLoader();

    void update();
    bool isDone() const;
    void requestChangeArchivePlayer(bool);
    void fn_804BBA00();
    void fn_804BBB50();
};
