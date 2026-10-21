#include "Game/LiveActor/ModelObj.hpp"
#include "Game/Scene/SceneFunction.hpp"
#include "Game/Util.hpp"
#include "Game/Util/ActorInitUtil.hpp"

ModelObj::ModelObj(const char* pName, const char* pModelName, MtxPtr pMtx, int drawBufferType, int movementType, int calcAnimType, bool a7)
    : LiveActor(pName) {
    mMtx = pMtx;
    if (pMtx != nullptr) {
        mPosition.set< f32 >(pMtx[0][3], pMtx[1][3], pMtx[2][3]);
    }

    if (!MR::initActor(this, pModelName, a7) && mModelManager != nullptr) {
        if (drawBufferType < MR::DrawBufferType_None) {
            drawBufferType = MR::DrawBufferType_MapObjWeakLight;
        }
        if (movementType < MR::MovementType_None) {
            movementType = MR::MovementType_MapObj;
        }
        if (calcAnimType < MR::CalcAnimType_None) {
            calcAnimType = MR::CalcAnimType_MapObjDecoration;
        }

        MR::connectToScene(this, movementType, calcAnimType, drawBufferType, -1);
        initSound(4, nullptr, nullptr, TVec3f(0.0f));
        initEffectKeeper(8, nullptr, false);
    }
}

void ModelObj::init(const JMapInfoIter& rIter) {
    makeActorAppeared();
}

void ModelObj::calcAndSetBaseMtx() {
    if (mMtx != nullptr) {
        mPosition.set< f32 >(mMtx[0][3], mMtx[1][3], mMtx[2][3]);
        MR::setBaseTRMtx(this, mMtx);
    } else {
        LiveActor::calcAndSetBaseMtx();
    }
}
