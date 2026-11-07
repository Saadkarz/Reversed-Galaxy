#pragma once

#include "Game/NameObj/NameObj.hpp"

class TubeSlider;

class TubeSliderObjCreator : public NameObj {
public:
    TubeSliderObjCreator(TubeSlider* pSlider, const char* pName);

    virtual ~TubeSliderObjCreator();
    virtual void init(const JMapInfoIter& rIter);

    /* 0x14 */ TubeSlider* mSlider;
    /* 0x18 */ const char* mObjName;
};
