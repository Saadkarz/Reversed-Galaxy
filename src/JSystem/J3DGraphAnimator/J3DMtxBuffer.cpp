#include "JSystem/J3DGraphAnimator/J3DMtxBuffer.hpp"
#include "JSystem/J3DGraphAnimator/J3DJoint.hpp"
#include "JSystem/J3DGraphBase/J3DMaterial.hpp"
#include "JSystem/J3DGraphLoader/J3DModelLoader.hpp"
#include "JSystem/JKernel/JKRHeap.hpp"

Mtx J3DMtxBuffer::sNoUseDrawMtx;
Mtx33 J3DMtxBuffer::sNoUseNrmMtx;
Mtx* J3DMtxBuffer::sNoUseDrawMtxPtr = &J3DMtxBuffer::sNoUseDrawMtx;
Mtx33* J3DMtxBuffer::sNoUseNrmMtxPtr = &J3DMtxBuffer::sNoUseNrmMtx;

void J3DMtxBuffer::initialize() {
    mJointTree = NULL;
    mpScaleFlagArr = NULL;
    mpEvlpScaleFlagArr = NULL;
    mpAnmMtx = NULL;
    mpWeightEvlpMtx = NULL;
    mpDrawMtxArr[0] = NULL;
    mpDrawMtxArr[1] = NULL;
    mpNrmMtxArr[0] = NULL;
    mpNrmMtxArr[1] = NULL;
    mpBumpMtxArr[0] = NULL;
    mpBumpMtxArr[1] = NULL;
    mMtxNum = 1;
    mCurrentViewNo = 0;
    mpUserAnmMtx = NULL;
}

enum {
    J3DMdlDataFlag_ConcatView = 0x10,
    J3DMdlDataFlag_NoAnimation = 0x100,
};

s32 J3DMtxBuffer::create(J3DModelData* pModelData, u32 mtxNum) {
    s32 ret = kJ3DError_Success;
    mMtxNum = mtxNum;
    mJointTree = &pModelData->getJointTree();

    ret = createAnmMtx(pModelData);
    if (ret != kJ3DError_Success)
        return ret;

    ret = createWeightEnvelopeMtx(pModelData);
    if (ret != kJ3DError_Success)
        return ret;

    if (pModelData->checkFlag(J3DMdlDataFlag_NoAnimation)) {
        setNoUseDrawMtx();
    } else {
        u32 loadType = getMdlDataFlag_MtxLoadType(pModelData->getFlag());
        switch (loadType) {
        case J3DMdlDataFlag_ConcatView:
            ret = setNoUseDrawMtx();
            break;
        case 0:
        default:
            ret = createDoubleDrawMtx(pModelData, mtxNum);
            break;
        }
    }

    if (ret != kJ3DError_Success)
        return ret;

    if (pModelData->getFlag() & J3DMdlDataFlag_ConcatView) {
        pModelData->setBumpFlag(0);
    } else {
        ret = createBumpMtxArray(pModelData, mtxNum);

        if (ret != kJ3DError_Success)
            return ret;
    }

    return ret;
}

J3DError J3DMtxBuffer::createAnmMtx(J3DModelData* pModelData) {
    if (pModelData->getJointNum() != 0) {
        mpScaleFlagArr = new u8[pModelData->getJointNum()];
        mpAnmMtx = new Mtx[pModelData->getJointNum()];
        mpUserAnmMtx = mpAnmMtx;
    }

    return kJ3DError_Success;
}

s32 J3DMtxBuffer::createWeightEnvelopeMtx(J3DModelData* pModelData) {
    if (pModelData->getWEvlpMtxNum() != 0) {
        mpEvlpScaleFlagArr = new u8[pModelData->getWEvlpMtxNum()];
        mpWeightEvlpMtx = new Mtx[pModelData->getWEvlpMtxNum()];
    }

    return kJ3DError_Success;
}

s32 J3DMtxBuffer::setNoUseDrawMtx() {
    mpDrawMtxArr[0] = mpDrawMtxArr[1] = &sNoUseDrawMtxPtr;
    mpNrmMtxArr[0] = mpNrmMtxArr[1] = &sNoUseNrmMtxPtr;
    mpBumpMtxArr[0] = mpBumpMtxArr[1] = NULL;
    return kJ3DError_Success;
}

s32 J3DMtxBuffer::createDoubleDrawMtx(J3DModelData* pModelData, u32 mtxNum) {
    if (mtxNum != 0) {
        for (s32 i = 0; i < 2; i++) {
            mpDrawMtxArr[i] = new Mtx*[mtxNum];
            mpNrmMtxArr[i] = new Mtx33*[mtxNum];
            mpBumpMtxArr[i] = NULL;
        }
    }

    for (s32 i = 0; i < 2; i++) {
        for (u32 j = 0; j < mtxNum; j++) {
            if (pModelData->getDrawMtxNum() != 0) {
                mpDrawMtxArr[i][j] = new (0x20) Mtx[pModelData->getDrawMtxNum()];
                mpNrmMtxArr[i][j] = new (0x20) Mtx33[pModelData->getDrawMtxNum()];
            }
        }
    }

    return kJ3DError_Success;
}

s32 J3DMtxBuffer::createBumpMtxArray(J3DModelData* i_modelData, u32 mtxNum) {
    if (i_modelData->getModelDataType() == 0) {
        u16 bumpMtxNum = 0;
        u16 materialCount = 0;
        u16 materialNum = i_modelData->getMaterialNum();
        for (u16 j = 0; j < materialNum; j++) {
            J3DMaterial* material = i_modelData->getMaterialNodePointer(j);
            if (material->getNBTScale()->mbHasScale == true) {
                bumpMtxNum += material->getShape()->countBumpMtxNum();
                materialCount++;
            }
        }

        if (bumpMtxNum != 0 && mtxNum != 0) {
            for (int i = 0; i < 2; i++) {
                mpBumpMtxArr[i] = new Mtx33**[(u16)materialCount];
            }
        }

        for (int i = 0; i < 2; i++) {
            u32 offset = 0;
            u16 materialNum = i_modelData->getMaterialNum();
            for (u16 j = 0; j < materialNum; j++) {
                J3DMaterial* material = i_modelData->getMaterialNodePointer(j);
                if (material->getNBTScale()->mbHasScale == true) {
                    mpBumpMtxArr[i][offset] = new Mtx33*[mtxNum];
                    material->getShape()->setBumpMtxOffset(offset);
                    offset++;
                }
            }
        }

        for (int i = 0; i < 2; i++) {
            u32 offset = 0;
            u16 materialNum = i_modelData->getMaterialNum();
            for (u16 j = 0; j < materialNum; j++) {
                J3DMaterial* material = i_modelData->getMaterialNodePointer((u16)j);
                if (material->getNBTScale()->mbHasScale == true) {
                    for (int k = 0; k < mtxNum; k++) {
                        mpBumpMtxArr[i][offset][k] = new (0x20) Mtx33[i_modelData->getDrawMtxNum()];
                    }
                    offset++;
                }
            }
        }

        if (materialCount != 0) {
            i_modelData->setBumpFlag(1);
        }
    }

    return kJ3DError_Success;
}

static f32 J3DUnit01[] = {0.0f, 1.0f};

asm void J3DMtxBuffer::calcWeightEnvelopeMtx() {
    nofralloc
    stwu r1, -0xb0(r1)
    lis r5, J3DUnit01@ha
    addi r5, r5, J3DUnit01@l
    li r4, -0x1
    stfd f31, 0xa0(r1)
    li r8, 0x1
    psq_st f31, 0xa8(r1), 0, 0
    stfd f30, 0x90(r1)
    psq_st f30, 0x98(r1), 0, 0
    stfd f29, 0x80(r1)
    psq_st f29, 0x88(r1), 0, 0
    stfd f28, 0x70(r1)
    psq_st f28, 0x78(r1), 0, 0
    stfd f27, 0x60(r1)
    psq_st f27, 0x68(r1), 0, 0
    stfd f26, 0x50(r1)
    psq_st f26, 0x58(r1), 0, 0
    stfd f25, 0x40(r1)
    psq_st f25, 0x48(r1), 0, 0
    stfd f24, 0x30(r1)
    psq_st f24, 0x38(r1), 0, 0
    stfd f23, 0x20(r1)
    psq_st f23, 0x28(r1), 0, 0
    stw r31, 0x1c(r1)
    stw r30, 0x18(r1)
    stw r29, 0x14(r1)
    stw r28, 0x10(r1)
    psq_l f23, 0x0(r5), 0, 0
    li r5, -0x30
    lwz r9, 0x0(r3)
    ps_merge00 f11, f23, f23
    lwz r6, 0x24(r9)
    ps_merge00 f13, f23, f23
    lwz r7, 0x28(r9)
    ps_merge00 f30, f23, f23
    lhz r10, 0x1e(r9)
    subi r29, r6, 0x2
    subi r28, r7, 0x4
    b L_8052A32C
L_8052A1FC:
    lwz r9, 0x8(r3)
    ps_merge00 f10, f23, f23
    ps_merge00 f12, f23, f23
    clrlwi r0, r4, 16
    stbx r8, r9, r4
    ps_merge00 f31, f23, f23
    li r30, 0x0
    lwz r7, 0x0(r3)
    lwz r6, 0x10(r3)
    lwz r7, 0x20(r7)
    add r12, r6, r5
    lbzx r11, r7, r0
L_8052A22C:
    lhzu r31, 0x2(r29)
    addi r30, r30, 0x1
    lwz r7, 0x0(r3)
    cmpw r30, r11
    mulli r6, r31, 0x30
    lwz r0, 0xc(r3)
    lwz r7, 0x2c(r7)
    lfsu f0, 0x4(r28)
    add r7, r7, r6
    add r6, r0, r6
    psq_l f2, 0x0(r7), 0, 0
    psq_l f1, 0x0(r6), 0, 0
    psq_l f3, 0x10(r6), 0, 0
    ps_muls0 f29, f2, f1
    psq_l f8, 0x10(r7), 0, 0
    ps_muls0 f27, f2, f3
    psq_l f5, 0x20(r6), 0, 0
    psq_l f7, 0x8(r7), 0, 0
    ps_muls0 f25, f2, f5
    ps_madds1 f29, f8, f1, f29
    psq_l f9, 0x20(r7), 0, 0
    psq_l f2, 0x8(r6), 0, 0
    ps_madds1 f27, f8, f3, f27
    psq_l f4, 0x18(r6), 0, 0
    ps_madds0 f29, f9, f2, f29
    ps_madds1 f25, f8, f5, f25
    psq_l f6, 0x28(r6), 0, 0
    ps_madds0 f27, f9, f4, f27
    psq_l f8, 0x18(r7), 0, 0
    ps_muls0 f28, f7, f1
    ps_muls0 f26, f7, f3
    ps_muls0 f24, f7, f5
    psq_l f7, 0x28(r7), 0, 0
    ps_madds0 f10, f29, f0, f10
    ps_madds0 f25, f9, f6, f25
    ps_madds1 f28, f8, f1, f28
    psq_st f10, 0x0(r12), 0, 0
    ps_madds0 f12, f27, f0, f12
    ps_madds1 f26, f8, f3, f26
    ps_madds1 f24, f8, f5, f24
    psq_st f12, 0x10(r12), 0, 0
    ps_madds0 f31, f25, f0, f31
    ps_madds0 f28, f7, f2, f28
    psq_st f31, 0x20(r12), 0, 0
    ps_madds0 f26, f7, f4, f26
    ps_madds0 f24, f7, f6, f24
    ps_madd f28, f23, f2, f28
    lwz r6, 0x4(r3)
    ps_madd f26, f23, f4, f26
    lbzx r7, r9, r4
    ps_madd f24, f23, f6, f24
    lbzx r0, r6, r31
    ps_madds0 f11, f28, f0, f11
    and r0, r7, r0
    ps_madds0 f13, f26, f0, f13
    ps_madds0 f30, f24, f0, f30
    stbx r0, r9, r4
    blt L_8052A22C
    psq_st f11, 0x8(r12), 0, 0
    ps_merge00 f11, f23, f23
    psq_st f13, 0x18(r12), 0, 0
    ps_merge00 f13, f23, f23
    psq_st f30, 0x28(r12), 0, 0
    ps_merge00 f30, f23, f23
L_8052A32C:
    addi r4, r4, 0x1
    addi r5, r5, 0x30
    cmpw r4, r10
    blt L_8052A1FC
    psq_l f31, 0xa8(r1), 0, 0
    lfd f31, 0xa0(r1)
    psq_l f30, 0x98(r1), 0, 0
    lfd f30, 0x90(r1)
    psq_l f29, 0x88(r1), 0, 0
    lfd f29, 0x80(r1)
    psq_l f28, 0x78(r1), 0, 0
    lfd f28, 0x70(r1)
    psq_l f27, 0x68(r1), 0, 0
    lfd f27, 0x60(r1)
    psq_l f26, 0x58(r1), 0, 0
    lfd f26, 0x50(r1)
    psq_l f25, 0x48(r1), 0, 0
    lfd f25, 0x40(r1)
    psq_l f24, 0x38(r1), 0, 0
    lfd f24, 0x30(r1)
    psq_l f23, 0x28(r1), 0, 0
    lfd f23, 0x20(r1)
    lwz r31, 0x1c(r1)
    lwz r30, 0x18(r1)
    lwz r29, 0x14(r1)
    lwz r28, 0x10(r1)
    addi r1, r1, 0xb0
    blr
}

void J3DMtxBuffer::calcDrawMtx(u32 mdlFlag, Vec const& param_1, Mtx const& param_2) {
    Mtx *sp24, *sp20;
    int sp1C = 0;
    sp20 = mpAnmMtx;
    sp24 = mpWeightEvlpMtx;

    MtxPtr viewMtx;
    Mtx viewBaseMtx;
    u16 fullWgtNum;

    switch (mdlFlag) {
    case 0:
        viewMtx = j3dSys.getViewMtx();
        fullWgtNum = mJointTree->getDrawFullWgtMtxNum();
        for (u16 i = 0; i < fullWgtNum; i++) {
            PSMTXConcat(viewMtx, getAnmMtx(mJointTree->getDrawMtxIndex(i)), *getDrawMtx(i));
        }
        if (mJointTree->getDrawMtxNum() > fullWgtNum) {
            J3DPSMtxArrayConcat(viewMtx, *mpWeightEvlpMtx, *getDrawMtx(fullWgtNum), mJointTree->getWEvlpMtxNum());
        }
        return;
    case 1:
        fullWgtNum = mJointTree->getDrawFullWgtMtxNum();
        for (u16 i = 0; i < fullWgtNum; i++) {
            PSMTXCopy(getAnmMtx(mJointTree->getDrawMtxIndex(i)), *getDrawMtx(i));
        }
        fullWgtNum = mJointTree->getDrawFullWgtMtxNum();
        for (u16 i = 0; i < fullWgtNum; i++) {
            PSMTXCopy(getWeightAnmMtx(i), *getDrawMtx(mJointTree->getDrawFullWgtMtxNum() + i));
        }
        break;
    case 2:
        J3DCalcViewBaseMtx(j3dSys.getViewMtx(), param_1, param_2, viewBaseMtx);
        fullWgtNum = mJointTree->getDrawFullWgtMtxNum();
        for (u16 i = 0; i < fullWgtNum; i++) {
            PSMTXConcat(viewBaseMtx, getAnmMtx(mJointTree->getDrawMtxIndex(i)), *getDrawMtx(i));
        }
        if (mJointTree->getDrawMtxNum() > mJointTree->getDrawFullWgtMtxNum()) {
            J3DPSMtxArrayConcat(viewBaseMtx, *mpWeightEvlpMtx, *getDrawMtx(mJointTree->getDrawFullWgtMtxNum()), mJointTree->getWEvlpMtxNum());
        }
        return;
    default:
        break;
    }
}

void J3DMtxBuffer::calcNrmMtx() {
    u16 drawMtxNum = mJointTree->getDrawMtxNum();
    for (u16 i = 0; i < drawMtxNum; i++) {
        if (mJointTree->getDrawMtxFlag(i) == 0) {
            if (getScaleFlag(mJointTree->getDrawMtxIndex(i)) == 1) {
                setNrmMtx(i, *getDrawMtx(i));
            } else {
                J3DPSCalcInverseTranspose(*getDrawMtx(i), *getNrmMtx(i));
            }
        } else {
            if (getEnvScaleFlag(mJointTree->getDrawMtxIndex(i)) == 1) {
                setNrmMtx(i, *getDrawMtx(i));
            } else {
                J3DPSCalcInverseTranspose(*getDrawMtx(i), *getNrmMtx(i));
            }
        }
    }
}

void J3DMtxBuffer::calcBBoardMtx() {
    u16 drawMtxNum = mJointTree->getDrawMtxNum();
    for (u16 i = 0; i < drawMtxNum; i++) {
        if (mJointTree->getDrawMtxFlag(i) == 0) {
            u16 index = mJointTree->getDrawMtxIndex(i);
            if (mJointTree->getJointNodePointer(index)->getMtxType() == 1) {
                MtxPtr drawMtx = *getDrawMtx(i);
                J3DCalcBBoardMtx(drawMtx);

                Mtx33* nrmMtx = getNrmMtx(i);
                (*nrmMtx)[0][0] = 1.0f / drawMtx[0][0];
                (*nrmMtx)[0][1] = 0.0f;
                (*nrmMtx)[0][2] = 0.0f;
                (*nrmMtx)[1][0] = 0.0f;
                (*nrmMtx)[1][1] = 1.0f / drawMtx[1][1];
                (*nrmMtx)[1][2] = 0.0f;
                (*nrmMtx)[2][0] = 0.0f;
                (*nrmMtx)[2][1] = 0.0f;
                (*nrmMtx)[2][2] = 1.0f / drawMtx[2][2];
            } else if (mJointTree->getJointNodePointer(index)->getMtxType() == 2) {
                MtxPtr drawMtx = *getDrawMtx(i);
                J3DCalcYBBoardMtx(drawMtx);
                Mtx33* nrmMtx = getNrmMtx(i);
                J3DPSCalcInverseTranspose(drawMtx, *nrmMtx);
            }
        }
    }
}

void J3DCalcViewBaseMtx(Mtx view, Vec const& scale, const Mtx& base, Mtx dst) {
    Mtx m;

    m[0][0] = base[0][0] * scale.x;
    m[0][1] = base[0][1] * scale.y;
    m[0][2] = base[0][2] * scale.z;
    m[0][3] = base[0][3];

    m[1][0] = base[1][0] * scale.x;
    m[1][1] = base[1][1] * scale.y;
    m[1][2] = base[1][2] * scale.z;
    m[1][3] = base[1][3];

    m[2][0] = base[2][0] * scale.x;
    m[2][1] = base[2][1] * scale.y;
    m[2][2] = base[2][2] * scale.z;
    m[2][3] = base[2][3];

    PSMTXConcat(view, m, dst);
}
