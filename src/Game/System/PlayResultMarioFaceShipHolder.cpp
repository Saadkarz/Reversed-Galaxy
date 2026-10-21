#include "Game/System/PlayResultMarioFaceShipHolder.hpp"

PlayResultMarioFaceShipHolder::PlayResultMarioFaceShipHolder()
    : NameObj("プレイ結果保持[マリオ顔惑星]") {
    reset();
}

void PlayResultMarioFaceShipHolder::reset() {
    _12 = false;
    _13 = false;
    _14 = false;
    _18 = 0;
    _1C = false;
}

PlayResultMarioFaceShipHolder::~PlayResultMarioFaceShipHolder() {
}
