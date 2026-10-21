#pragma once

#define SceneObj_SensorHitChecker 0x0
#define SceneObj_ClippingDirector 0x2
#define SceneObj_StageSwitchContainer 0xA
#define SceneObj_SwitchWatcherHolder 0xB
#define SceneObj_ShadowControllerHolder 0x4C
#define SceneObj_ShadowVolumeDrawInit 0x4E
#define SceneObj_ShadowSurfaceDrawInit 0x4F
#define SceneObj_BaseMatrixFollowTargetHolder 0x3C
#define SceneObj_ChangeObjHolder 0x85

class NameObj;

class SceneObjHolder {
public:
    NameObj* create(int);
    NameObj* getObj(int) const;
    bool isExist(int) const;
    NameObj* newEachObj(int);

    NameObj* mObjs[0x99];  // 0x00
};

namespace MR {
    NameObj* createSceneObj(int);
    SceneObjHolder* getSceneObjHolder();
    bool isExistSceneObj(int);

    template < class T >
    inline T getSceneObj(int objID) {
        return reinterpret_cast< T >(MR::getSceneObjHolder()->getObj(objID));
    }
};  // namespace MR
