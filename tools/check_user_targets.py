import os
import re

targets = [
    # Game/LiveActor
    'Game/LiveActor/LiveActor.cpp',
    'Game/LiveActor/ShadowController.cpp',
    'Game/LiveActor/MaterialCtrl.cpp',
    'Game/LiveActor/ModelObj.cpp',
    'Game/LiveActor/ActorStateKeeper.cpp',
    'Game/LiveActor/LiveActorGroupArray.cpp',
    'Game/LiveActor/ActorLightCtrl.cpp',
    'Game/LiveActor/BreakModel.cpp',
    'Game/LiveActor/PartsModel.cpp',
    'Game/LiveActor/RailObj.cpp',
    'Game/LiveActor/RailRider.cpp',
    'Game/LiveActor/SensorHitChecker.cpp',
    'Game/LiveActor/ShadowDrawer.cpp',
    'Game/LiveActor/ShadowVolumeFlatModel.cpp',
    'Game/LiveActor/ShadowVolumeBox.cpp',
    'Game/LiveActor/ShadowVolumeLine.cpp',
    'Game/LiveActor/ShadowVolumeModel.cpp',
    'Game/LiveActor/ShadowVolumeOval.cpp',
    'Game/LiveActor/ShadowVolumeOvalPole.cpp',
    'Game/LiveActor/ShadowVolumeSphere.cpp',
    'Game/LiveActor/ShadowSurfaceOval.cpp',
    'Game/LiveActor/ClippingJudge.cpp',

    # Game/System
    'Game/System/MainLoopFramework.cpp',
    'Game/System/PlayerHeapHolder.cpp',
    'Game/System/PlayResultInStageHolder.cpp',
    'Game/System/PlayResultMarioFaceShipHolder.cpp',
    'Game/System/PlayResultWorldMapHolder.cpp',
    'Game/System/RenderMode.cpp',
    'Game/System/RenderModeObj.cpp',
    'Game/System/ScenarioDataParser.cpp',
    'Game/System/StationedArchiveLoader.cpp',
    'Game/System/GameSystemFontHolder.cpp',
    'Game/System/HeapMemoryWatcher.cpp',
    'Game/System/ResourceShare.cpp',
    'Game/System/DrawSyncManager.cpp',
    'Game/System/FunctionAsyncExecutor.cpp',
    'Game/System/WPadAcceleration.cpp',
    'Game/System/WPadButton.cpp',
    'Game/System/WPadHVSwing.cpp',
    'Game/System/WPadHolder.cpp',
    'Game/System/WPadInfoChecker.cpp',
    'Game/System/WPadLeaveWatcher.cpp',

    # Game/Util, Map, Ride
    'Game/Util/ValueControl.cpp',
    'Game/Util/SpringValue.cpp',
    'Game/Util/BitArray.cpp',
    'Game/Util/BothDirList.cpp',
    'Game/Util/SchedulerUtil.cpp',
    'Game/Map/StageSwitch.cpp',
    'Game/Ride/TubeSliderCrystal.cpp',
]

with open('configure.py', 'r', encoding='utf-8') as f:
    cfg = f.read()

splits = open('config/SB4E01/splits.txt', 'r', encoding='utf-8').read()

print(f'Checking {len(targets)} targets:')
for t in targets:
    m_match = re.search(rf'Object\(Matching,\s*"{re.escape(t)}"\)', cfg)
    m_nonmatch = re.search(rf'Object\(NonMatching,\s*"{re.escape(t)}"\)', cfg)
    status = 'MATCHING' if m_match else ('NONMATCHING' if m_nonmatch else 'NOT_IN_CFG')
    in_splits = (t + ':') in splits
    obj_exists = os.path.exists('build/SB4E01/src/' + t.replace('.cpp', '.o'))
    src_exists = os.path.exists('src/' + t)
    print(f'{t:<45} | cfg:{status:<11} | src:{src_exists} | obj:{obj_exists} | splits:{in_splits}')
