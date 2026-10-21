#pragma once

class LiveActor;
class J3DModel;
class J3DModelData;
class J3DMaterial;
class ResourceHolder;

#include <JSystem/JGeometry/TBox.hpp>
#include <JSystem/JGeometry/TMatrix.hpp>

namespace MR {
    void syncJointAnimation(LiveActor*, const LiveActor*);
    void copyJointAnimation(LiveActor*, const LiveActor*);

    void syncMaterialAnimation(LiveActor*, const LiveActor*);
    void calcModelBoundingBox(TBox3f*, const LiveActor*);

    J3DModelData* getJ3DModelData(const char*);
    J3DModel* getJ3DModel(const LiveActor*);
    void calcJ3DModel(LiveActor*);
    ResourceHolder* getModelResourceHolder(const LiveActor*);

    int findPosNrmMtxIndexFromModel(J3DModelData*, u16);
    J3DMaterial* getMaterial(J3DModelData*, const char*);
    bool isUseTex(J3DMaterial*, u16);
    bool isUseTexMtx(J3DMaterial*, u32);
    const TPos3f& getMirrorModelTexMtx();

    void initEnvelopeAndEnvMapOrProjMapModelData(J3DModelData*);
    bool isUseFur(const J3DModelData*);
    void downFracVtx(J3DModelData*);
};  // namespace MR
