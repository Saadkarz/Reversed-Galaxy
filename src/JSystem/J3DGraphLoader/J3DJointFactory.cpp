#include "JSystem/J3DGraphLoader/J3DJointFactory.hpp"
#include "JSystem/J3DGraphAnimator/J3DJoint.hpp"
#include "JSystem/J3DGraphLoader/J3DModelLoader.hpp"
#include "JSystem/JSupport/JSupport.hpp"
#include <stdint.h>

#pragma push
#pragma schedule off
J3DJointFactory::J3DJointFactory(J3DJointBlock const& block) {
#ifdef __MWERKS__
    asm {
        lwz r0, 0xc(r4)
        cmpwi r0, 0
        bne L_init
        li r0, 0
        b L_tbl
    L_init:
        add r0, r4, r0
    L_tbl:
        lwz r5, 0x10(r4)
        stw r0, 0x0(r3)
        cmpwi r5, 0
        bne L_add
        li r0, 0
        b L_end
    L_add:
        add r0, r4, r5
    L_end:
        stw r0, 0x4(r3)
    }
#else
    mJointInitData = JSUConvertOffsetToPtr< J3DJointInitData >(&block, (uintptr_t)block.mpJointInitData);
    mIndexTable = JSUConvertOffsetToPtr< u16 >(&block, (uintptr_t)block.mpIndexTable);
#endif
}
#pragma pop

J3DJoint* J3DJointFactory::create(int no) {
    J3DJoint* joint = new J3DJoint();
    joint->mJntNo = no;
    joint->mKind = getKind(no);
    joint->mScaleCompensate = getScaleCompensate(no);
    joint->mTransformInfo = getTransformInfo(no);
    joint->mBoundingSphereRadius = getRadius(no);
    joint->mMin = getMin(no);
    joint->mMax = getMax(no);
    joint->mMtxCalc = NULL;

    if (joint->mScaleCompensate == 0xFF)
        joint->mScaleCompensate = 0;

    return joint;
}
