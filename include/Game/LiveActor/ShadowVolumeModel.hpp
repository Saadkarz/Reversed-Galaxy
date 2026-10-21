#pragma once

#include "Game/LiveActor/ShadowVolumeDrawer.hpp"

class J3DModelData;

class ShadowVolumeModel : public ShadowVolumeDrawer {
public:
    ShadowVolumeModel(const char*);

    inline virtual ~ShadowVolumeModel();
    virtual void drawShape() const;

    void initVolumeModel(const char*);

    /* 0x1C */ J3DModelData* mModelData;
};

#ifndef SHADOW_VOLUME_CYLINDER_TU
inline ShadowVolumeModel::~ShadowVolumeModel() {}
#endif

