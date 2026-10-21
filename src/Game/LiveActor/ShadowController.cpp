#include "Game/LiveActor/ShadowController.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ShadowDrawer.hpp"
#include "Game/Map/HitInfo.hpp"
#include "Game/Scene/SceneFunction.hpp"
#include "Game/Util/CameraUtil.hpp"
#include "Game/Util/GravityUtil.hpp"
#include "Game/Util/LiveActorUtil.hpp"
#include "Game/Util/MapUtil.hpp"
#include "Game/Util/MathUtil.hpp"
#include "Game/Util/MtxUtil.hpp"
#include "Game/Util/ObjUtil.hpp"
#include "Game/Util/SceneUtil.hpp"
#include "Game/Util/AreaObjUtil.hpp"
#include "Game/Util/StringUtil.hpp"

namespace {
    const char* sShadowControllerParam = "ShadowControllerParam";
    const s32 sCollisionCountLimit = 1;
    const s32 sGravityCountLimit = 1;
};  // namespace

class ShadowManager {
public:
    void updateFarClipParam();

    u8 _0[0x2C];
    f32 mFarClip;
    f32 _30;
    u8 _34;
    u8 _35;
};

ShadowControllerHolder::ShadowControllerHolder() : NameObj(((void)1.0f, (void)0.0f, (void)-1.0f, (void)7000.0f, (void)50.0f, (void)0.001f, "影管理")), _14(), _20() {
    mFarClip = 7000.0f;
    _30 = 7000.0f;
    _34 = false;
    _35 = false;
    _14.init(0x500);
    _20.init(0x400);
    MR::connectToScene(this, 0x2C, -1, -1, -1);

    JMapInfo* parser = MR::tryCreateStageZoneInfoCsvParser(sShadowControllerParam);
    if (parser) {
        bool farClip = false;
        MR::getCsvDataBool(&farClip, parser, "FarClip", 0);
        _34 = farClip;
        MR::getCsvDataF32(&mFarClip, parser, "FarClipDistance", 0);
        _30 = mFarClip;
        _35 = _34;
    }
}

template MR::Vector< MR::AssignableArray< ShadowController* > >::Vector();


void ShadowControllerHolder::movement() {
    updateController();
}

void ShadowControllerHolder::initAfterPlacement() {
    ShadowController* pController;
    int size = _14.size();
    for (u32 i = 0; i < size; i++) {
        pController = _14[i];
        pController->updateDirection();
        pController->updateProjection();
    }
}

void ShadowManager::updateFarClipParam() {
    AreaObj* area = MR::getAreaObjAtPlayerPos("ShadowFarClipCtrlArea");
    if (area) {
        s32 arg0 = MR::getAreaObjArg(area, 0);
        s32 arg1 = MR::getAreaObjArg(area, 1);
        mFarClip = (arg0 != -1) ? (f32)arg0 : _30;
        _34 = !(arg1 + 1);
    } else {
        _34 = _35;
        mFarClip = _30;
    }

    AreaObj* viewArea = MR::getAreaObjAtPlayerPos("ViewGroupCtrlArea");
    if (viewArea) {
        s32 arg2 = MR::getAreaObjArg(viewArea, 2);
        if (arg2 != -1 && _34) {
            _34 = false;
        }
    }
}

void ShadowControllerHolder::updateController() {
    reinterpret_cast<ShadowManager*>(this)->updateFarClipParam();
    int size = _20.size();
    for (u32 i = 0; i < size; i++) {
        if (_34) {
            _20[i]->updateFarClipping(mFarClip);
        } else {
            _20[i]->_73 = 0;
        }
        _20[i]->update();
    }
    _20.clear();
}

ShadowControllerList::ShadowControllerList(LiveActor* pActor, u32 listCount) : mShadowList(), mHost(pActor) {
    mShadowList.init(listCount);
}

void ShadowControllerList::addController(ShadowController* pController) {
    mShadowList.push_back(pController);
}

u32 ShadowControllerList::getControllerCount() const {
    return mShadowList.size();
}

ShadowController* ShadowControllerList::getController(u32 idx) const {
    return mShadowList[idx];
}

ShadowController* ShadowControllerList::getController(const char* pName) const {
    if (mShadowList.size() == 1) {
        return mShadowList[0];
    }

    for (u32 i = 0; i < mShadowList.size(); i++) {
        if (MR::isEqualString(pName, mShadowList[i]->mName)) {
            return mShadowList[i];
        }
    }

    return nullptr;
}

void ShadowControllerList::resetCalcCount() {
    for (u32 i = 0; i < mShadowList.size(); i++) {
        ShadowController* controller = mShadowList[i];
        controller->_71 = 0;
        controller->_72 = 0;
    }
}

void ShadowControllerList::requestCalc() {
    for (u32 i = 0; i < mShadowList.size(); i++) {
        mShadowList[i]->requestCalc();
    }
}

ShadowController::ShadowController(LiveActor* pActor, const char* pName)
    : mActor(pActor), mName(pName), mGroupName(""), mDrawer(nullptr), mProjectedSensor(nullptr), mCollisionPartsFilter(nullptr), _18(nullptr), _1C(nullptr), mDropPos(nullptr), mDropDir(nullptr),
      mProjPos(nullptr), mProjNorm(nullptr), _30(0.0f, 0.0f, 0.0f), _3C(0.0f, -1.0f, 0.0f), _48(0.0f, 0.0f, 0.0f), _54(0.0f, 1.0f, 0.0f), mLocalRotate(0.0f, 0.0f, 0.0f),
      _6C(1), _6D(0), _6E(0), _6F(0), _70(0), _71(0), _72(0), _73(0), mStartOffset(50.0f), mDropLength(0.0f), _7C(0), _7D(1), _7E(1) {
    MR::createSceneObj(SceneObj_ShadowControllerHolder);
    MR::addShadowController(this);
}

void ShadowController::requestCalc() {
    if (!_70) {
        _70 = 1;
        appendToHolder();
    }
}

void ShadowController::update() {
    if (isDraw()) {
        updateDirection();
        updateProjection();
    }

    _70 = 0;
}

void ShadowController::updateFarClipping(f32 clip) {
    TVec3f dropPos;
    getDropPos(&dropPos);
    f32 cameraDistZ = MR::calcCameraDistanceZ(dropPos);
    _73 = cameraDistZ >= clip;
}

void ShadowController::updateDirection() {
    if (isCalcGravity()) {
        TVec3f position;
        getDropPos(&position);
        TVec3f previousDirection(_3C);
        if (!isCalcShadowGravity() || !MR::calcDropShadowVectorOrZero(mActor, position, &_3C, nullptr, 0)) {
            if (!MR::calcGravityVectorOrZero(mActor, position, &_3C, nullptr, 0)) {
                _3C.setPS(previousDirection);
            }
        }

        if (_6D == 2 || _6D == 5) {
            _72++;
        }
    }
}

void ShadowController::updateProjection() {
    if (isCalcCollision()) {
        Triangle triangle;
        TVec3f position;
        getDropPos(&position);
        TVec3f direction;
        getDropDir(&direction);
        position -= direction * mStartOffset;

        switch (_6E) {
        case 0:
            _6F = MR::getFirstPolyOnLineToMap(&_48, &triangle, position, direction * (mDropLength + mStartOffset), mCollisionPartsFilter, nullptr);
            break;
        case 1:
            _6F = MR::getFirstPolyOnLineToWaterSurface(&_48, &triangle, position, direction * (mDropLength + mStartOffset), mCollisionPartsFilter, nullptr);
            break;
        }

        if (_6F) {
            mProjectedSensor = triangle.getSensor();
            _54.set(*triangle.getNormal(0));
        } else {
            mProjectedSensor = nullptr;
        }

        if (_6C == 2) {
            _71++;
        }
    }
}

ShadowDrawer* ShadowController::getShadowDrawer() {
    return mDrawer;
}

LiveActor* ShadowController::getHost() const {
    return mActor;
}

void ShadowController::setShadowDrawer(ShadowDrawer* pDrawer) {
    mDrawer = pDrawer;
    pDrawer->setShadowController(this);
}

void ShadowController::getBaseMtx(MtxPtr pMtx) const {
    if (!MR::isNearZero(mLocalRotate, 0.001f)) {
        reinterpret_cast< TPos3f* >(pMtx)->identity();
        MR::makeMtxRotate(pMtx, mLocalRotate);
    } else {
        reinterpret_cast< TPos3f* >(pMtx)->identity();
    }

    if (_18 != nullptr) {
        PSMTXConcat(_18, pMtx, pMtx);
    } else if (mActor->getBaseMtx() != nullptr) {
        PSMTXConcat(mActor->getBaseMtx(), pMtx, pMtx);
    }
}

void ShadowController::getDropPos(TVec3f* pOut) const {
    if (mDropPos) {
        pOut->set(*mDropPos);
    } else {
        if (_1C) {
            PSMTXMultVec(_1C, (const Vec*)&_30, (Vec*)pOut);
        } else {
            pOut->set(_30);
        }
    }
}

void ShadowController::getDropDir(TVec3f* pOut) const {
    if (mDropDir) {
        pOut->set(*mDropDir);
    } else {
        pOut->set(_3C);
    }
}

f32 ShadowController::getDropLength() const {
    return mDropLength;
}

void ShadowController::getProjectionPos(TVec3f* pOut) const {
    if (mProjPos) {
        pOut->set(*mProjPos);
    } else {
        pOut->set(_48);
    }
}

void ShadowController::getProjectionNormal(TVec3f* pOut) const {
    if (mProjNorm) {
        pOut->set(*mProjNorm);
    } else {
        pOut->set(_54);
    }
}

f32 ShadowController::getProjectionLength() const {
    if (!isProjected()) {
        return -1.0f;
    }

    TVec3f position;
    getDropPos(&position);
    TVec3f direction;
    getDropDir(&direction);
    TVec3f difference(_48);
    difference -= position;
    f32 length = direction.dot(difference);
    if (length < 0.0f) {
        return 0.0f;
    }

    return position.distance(_48);
}

bool ShadowController::isProjected() const {
    return _6F && _7D;
}

bool ShadowController::isDraw() const {
    if (_73) {
        return false;
    }

    if (!_7D) {
        return false;
    }

    if (!_7E) {
        return true;
    }

    return MR::isValidDraw(mActor);
}

bool ShadowController::isCalcCollision() const {
    if (!_6C) {
        return false;
    }

    if (_6C == 2) {
        return _71 < ::sCollisionCountLimit;
    }

    return true;
}

bool ShadowController::isCalcGravity() const {
    if (_6D == 0 || _6D == 3) {
        return false;
    }

    if (_6D == 2 || _6D == 5) {
        return _72 < ::sGravityCountLimit;
    }

    return true;
}

bool ShadowController::isCalcShadowGravity() const {
    const u8 offset = static_cast< u8 >(-4);
    return static_cast< u8 >(_6D + offset) <= 1;
}

void ShadowController::setGroupName(const char* pName) {
    mGroupName = pName;
}

void ShadowController::setDropPosPtr(const TVec3f* pDropPos) {
    mDropPos = pDropPos;
    _1C = 0;
}

void ShadowController::setDropPosMtxPtr(MtxPtr pMtx, const TVec3f& rOffset) {
    _18 = pMtx;
    mDropPos = nullptr;
    _1C = pMtx;
    _30.set(rOffset);
}

void ShadowController::setDropPosFix(const TVec3f& rPos) {
    _30.set(rPos);
    mDropPos = 0;
    _1C = 0;
}

void ShadowController::setDropDirPtr(const TVec3f* pDropDir) {
    mDropDir = pDropDir;
    _6D = 0;
}

void ShadowController::setProjectionPtr(const TVec3f* pPosition, const TVec3f* pNormal) {
    mProjPos = pPosition;
    mProjNorm = pNormal;
    _6C = 0;
    _6F = 1;
    mProjectedSensor = nullptr;
}

void ShadowController::setDropDirFix(const TVec3f& rDirection) {
    _3C.set(rDirection);
    mDropDir = 0;
    _6D = 0;
}

void ShadowController::setLocalRotate(const TVec3f& rRotate) {
    mLocalRotate.set(rRotate);
}

void ShadowController::setDropLength(f32 len) {
    mDropLength = len;
}

void ShadowController::setDropStartOffset(f32 offs) {
    mStartOffset = offs;
}

void ShadowController::setDropTypeNormal() {
    _6E = 0;
}

void ShadowController::setDropTypeSurface() {
    _6E = 1;
}

void ShadowController::setProjectionFix(const TVec3f& rPosition, const TVec3f& rNormal, bool projected) {
    _48.set(rPosition);
    _54.set(rNormal);
    _6F = projected;
    mProjectedSensor = 0;
}

void ShadowController::onCalcCollision() {
    _6C = 1;
}

void ShadowController::offCalcCollision() {
    _6C = 0;
}

void ShadowController::onCalcCollisionOneTime() {
    _6C = 2;
    _71 = 0;
}

void ShadowController::onCalcDropGravity() {
    TVec3f vec(0.0f, 1.0f, 0.0f);
    _3C.set(vec);
    mDropDir = 0;
    _6D = 1;
}

void ShadowController::onCalcDropGravityOneTime() {
    TVec3f vec(0.0f, 1.0f, 0.0f);
    _3C.set(vec);
    mDropDir = 0;
    _6D = 2;
    _72 = 0;
}

void ShadowController::offCalcDropGravity() {
    _6D = 0;
}

void ShadowController::onCalcDropPrivateGravity() {
    TVec3f vec(0.0f, 1.0f, 0.0f);
    _3C.set(vec);
    mDropDir = 0;
    _6D = 4;
}

void ShadowController::onCalcDropPrivateGravityOneTime() {
    TVec3f vec(0.0f, 1.0f, 0.0f);
    _3C.set(vec);
    mDropDir = 0;
    _6D = 5;
    _72 = 0;
}

void ShadowController::offCalcDropPrivateGravity() {
    _6D = 3;
}

void ShadowController::setCollisionPartsFilter(CollisionPartsFilterBase* pBase) {
    mCollisionPartsFilter = pBase;
}

void ShadowController::onFollowHostScale() {
    _7C = 1;
}

void ShadowController::offFollowHostScale() {
    _7C = 0;
}

bool ShadowController::isFollowHostScale() const {
    return _7C;
}

void ShadowController::onVisibleSyncHost() {
    _7E = 1;
}

void ShadowController::offVisibleSyncHost() {
    _7E = 0;
}

void ShadowController::validate() {
    _7D = 1;
}

void ShadowController::invalidate() {
    _7D = 0;
}

namespace MR {
    void addShadowController(ShadowController* pController) {
        getSceneObj< ShadowControllerHolder* >(SceneObj_ShadowControllerHolder)->_14.push_back(pController);
    }

    void requestCalcActorShadowAppear(LiveActor* pActor) {
        if (!isInitializeStatePlacementSomething()) {
            if (pActor->mShadowList != nullptr) {
                pActor->mShadowList->resetCalcCount();
            }

            if (pActor->mShadowList != nullptr) {
                pActor->mShadowList->requestCalc();
            }
        }
    }

    void requestCalcActorShadow(LiveActor* pActor) {
        if (pActor->mShadowList != nullptr) {
            pActor->mShadowList->requestCalc();
        }
    }
};  // namespace MR

template void MR::Vector< MR::AssignableArray< ShadowController* > >::push_back(ShadowController* const&);
template <>
MR::AssignableArray< ShadowController* >::~AssignableArray() {
    if (mArr != 0) {
        delete[] mArr;
    }
}

ShadowControllerHolder::~ShadowControllerHolder() {
}





