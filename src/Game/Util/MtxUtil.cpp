#include "Game/Util/MtxUtil.hpp"
#include "Game/Util/MathUtil.hpp"
#include "revolution/mtx/mtx.h"
#include <JSystem/JGeometry/TVec.hpp>
#include <JSystem/JMath.hpp>
#include <JSystem/JMath/JMATrigonometric.hpp>

static Mtx mtrans_org = {{1.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 1.0f, 0.0f}};
static Mtx tmpmtx_sc = {{1.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 1.0f, 0.0f}};
static Mtx tmpmtx_rx = {{1.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 1.0f, 0.0f}};
static Mtx tmpmtx_ry = {{1.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 1.0f, 0.0f}};
static Mtx tmpmtx_rz = {{1.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 1.0f, 0.0f}};

namespace MR {
    void makeMtxRotate(MtxPtr pMtx, s16 rx, s16 ry, s16 rz) {
        f32 sinX = JMASSin(rx);
        f32 sinY = JMASSin(ry);
        f32 sinZ = JMASSin(rz);
        f32 cosX = JMASCos(rx);
        f32 cosY = JMASCos(ry);
        f32 cosZ = JMASCos(rz);

        pMtx[0][0] = cosZ * cosY;
        pMtx[1][0] = sinZ * cosY;
        pMtx[2][0] = -sinY;

        pMtx[0][1] = cosZ * sinY * sinX - sinZ * cosX;
        pMtx[1][1] = sinZ * sinY * sinX + cosZ * cosX;
        pMtx[2][1] = cosY * sinX;

        pMtx[0][2] = cosZ * sinY * cosX + sinZ * sinX;
        pMtx[1][2] = sinZ * sinY * cosX - cosZ * sinX;
        pMtx[2][2] = cosY * cosX;

        pMtx[0][3] = 0.0f;
        pMtx[1][3] = 0.0f;
        pMtx[2][3] = 0.0f;
    }

    void makeMtxRotate(MtxPtr pMtx, f32 rx, f32 ry, f32 rz) {
        s16 angleX = (s16)(rx * DEGREE_TO_S16);
        s16 angleY = (s16)(ry * DEGREE_TO_S16);
        s16 angleZ = (s16)(rz * DEGREE_TO_S16);
        makeMtxRotate(pMtx, angleX, angleY, angleZ);
    }

    void makeMtxRotate(MtxPtr pMtx, const TVec3f& rVec) {
        makeMtxRotate(pMtx, rVec.x, rVec.y, rVec.z);
    }

    void makeMtxRotateY(MtxPtr pMtx, f32 ry) {
        s16 angle = (s16)(ry * DEGREE_TO_S16);
        f32 sinY = JMASSin(angle);
        f32 cosY = JMASCos(angle);

        pMtx[0][0] = cosY;
        pMtx[1][0] = 0.0f;
        pMtx[2][0] = -sinY;
        pMtx[0][1] = 0.0f;
        pMtx[1][1] = 1.0f;
        pMtx[2][1] = 0.0f;
        pMtx[0][2] = sinY;
        pMtx[1][2] = 0.0f;
        pMtx[2][2] = cosY;
        pMtx[0][3] = 0.0f;
        pMtx[1][3] = 0.0f;
        pMtx[2][3] = 0.0f;
    }

    void makeMtxTR(MtxPtr pMtx, f32 tx, f32 ty, f32 tz, f32 rx, f32 ry, f32 rz) {
        f32 sinX = JMASinDegree(rx);
        f32 sinY = JMASinDegree(ry);
        f32 sinZ = JMASinDegree(rz);
        f32 cosX = JMACosDegree(rx);
        f32 cosY = JMACosDegree(ry);
        f32 cosZ = JMACosDegree(rz);

        pMtx[0][0] = cosZ * cosY;
        pMtx[1][0] = sinZ * cosY;
        pMtx[2][0] = -sinY;

        pMtx[0][1] = cosZ * sinY * sinX - sinZ * cosX;
        pMtx[1][1] = sinZ * sinY * sinX + cosZ * cosX;
        pMtx[2][1] = cosY * sinX;

        pMtx[0][2] = cosZ * sinY * cosX + sinZ * sinX;
        pMtx[1][2] = sinZ * sinY * cosX - cosZ * sinX;
        pMtx[2][2] = cosY * cosX;

        pMtx[0][3] = tx;
        pMtx[1][3] = ty;
        pMtx[2][3] = tz;
    }

    void makeMtxTR(MtxPtr pMtx, const TVec3f& rTrans, const TVec3f& rRot) {
        makeMtxTR(pMtx, rTrans.x, rTrans.y, rTrans.z, rRot.x, rRot.y, rRot.z);
    }

    void makeMtxTransRotateY(MtxPtr pMtx, f32 tx, f32 ty, f32 tz, f32 ry) {
        makeMtxRotateY(pMtx, ry);
        pMtx[0][3] = tx;
        pMtx[1][3] = ty;
        pMtx[2][3] = tz;
    }

    void rotateMtxLocalX(MtxPtr pMtx, f32 rad) {
        f32 cosAngle = JMACosRadian(rad);
        f32 sinAngle = JMASinRadian(rad);
        f32 a0 = cosAngle * pMtx[0][1] + sinAngle * pMtx[0][2];
        f32 a1 = cosAngle * pMtx[1][1] + sinAngle * pMtx[1][2];
        f32 a2 = cosAngle * pMtx[2][1] + sinAngle * pMtx[2][2];
        f32 b0 = -sinAngle * pMtx[0][1] + cosAngle * pMtx[0][2];
        f32 b1 = -sinAngle * pMtx[1][1] + cosAngle * pMtx[1][2];
        f32 b2 = -sinAngle * pMtx[2][1] + cosAngle * pMtx[2][2];
        pMtx[0][1] = a0;
        pMtx[1][1] = a1;
        pMtx[2][1] = a2;
        pMtx[0][2] = b0;
        pMtx[1][2] = b1;
        pMtx[2][2] = b2;
    }

    void rotateMtxLocalY(MtxPtr pMtx, f32 rad) {
        f32 cosAngle = JMACosRadian(rad);
        f32 sinAngle = JMASinRadian(rad);
        f32 a0 = cosAngle * pMtx[0][0] - sinAngle * pMtx[0][2];
        f32 a1 = cosAngle * pMtx[1][0] - sinAngle * pMtx[1][2];
        f32 a2 = cosAngle * pMtx[2][0] - sinAngle * pMtx[2][2];
        f32 b0 = sinAngle * pMtx[0][0] + cosAngle * pMtx[0][2];
        f32 b1 = sinAngle * pMtx[1][0] + cosAngle * pMtx[1][2];
        f32 b2 = sinAngle * pMtx[2][0] + cosAngle * pMtx[2][2];
        pMtx[0][0] = a0;
        pMtx[1][0] = a1;
        pMtx[2][0] = a2;
        pMtx[0][2] = b0;
        pMtx[1][2] = b1;
        pMtx[2][2] = b2;
    }

    void rotateMtxLocalZ(MtxPtr pMtx, f32 rad) {
        f32 cosAngle = JMACosRadian(rad);
        f32 sinAngle = JMASinRadian(rad);
        f32 a0 = cosAngle * pMtx[0][0] + sinAngle * pMtx[0][1];
        f32 a1 = cosAngle * pMtx[1][0] + sinAngle * pMtx[1][1];
        f32 a2 = cosAngle * pMtx[2][0] + sinAngle * pMtx[2][1];
        f32 b0 = -sinAngle * pMtx[0][0] + cosAngle * pMtx[0][1];
        f32 b1 = -sinAngle * pMtx[1][0] + cosAngle * pMtx[1][1];
        f32 b2 = -sinAngle * pMtx[2][0] + cosAngle * pMtx[2][1];
        pMtx[0][0] = a0;
        pMtx[1][0] = a1;
        pMtx[2][0] = a2;
        pMtx[0][1] = b0;
        pMtx[1][1] = b1;
        pMtx[2][1] = b2;
    }

    void rotateMtxLocalXDegree(MtxPtr pMtx, f32 deg) {
        rotateMtxLocalX(pMtx, deg * PI_180);
    }

    void rotateMtxLocalYDegree(MtxPtr pMtx, f32 deg) {
        rotateMtxLocalY(pMtx, deg * PI_180);
    }

    void rotateMtxLocalZDegree(MtxPtr pMtx, f32 deg) {
        rotateMtxLocalZ(pMtx, deg * PI_180);
    }

    void preScaleMtx(MtxPtr pMtx, f32 scale) {
        preScaleMtx(pMtx, scale, scale, scale);
    }

    void preScaleMtx(MtxPtr pMtx, const TVec3f& rScale) {
        preScaleMtx(pMtx, rScale.x, rScale.y, rScale.z);
    }

    void preScaleMtx(MtxPtr pMtx, f32 sx, f32 sy, f32 sz) {
        pMtx[0][0] *= sx;
        pMtx[1][0] *= sx;
        pMtx[2][0] *= sx;
        pMtx[0][1] *= sy;
        pMtx[1][1] *= sy;
        pMtx[2][1] *= sy;
        pMtx[0][2] *= sz;
        pMtx[1][2] *= sz;
        pMtx[2][2] *= sz;
    }

    void scaleMtxToLocalMtx(MtxPtr pDst, MtxPtr pSrc, MtxPtr pBase, const TVec3f& rScale) {
        TPos3f baseCopy;
        baseCopy.setInline(pBase);
        TVec3f srcTrans;
        baseCopy.setTrans(TVec3f(0.0f, 0.0f, 0.0f));

        TPos3f invMtx;
        invMtx.invert(baseCopy);
        preScaleMtx(baseCopy, rScale.x, rScale.y, rScale.z);

        extractMtxTrans(pSrc, &srcTrans);
        multMtx(pDst, pSrc, invMtx);
        multMtx(pDst, pDst, baseCopy);
        setMtxTrans(pDst, srcTrans.x, srcTrans.y, srcTrans.z);
    }

    void scaleMtxToLocalMtx(MtxPtr pDst, MtxPtr pSrc, const TVec3f& rScale) {
        scaleMtxToLocalMtx(pDst, pDst, pSrc, rScale);
    }

    void scaleMtxToDir(TPos3f* pDst, const TVec3f& rDir, const TVec3f& rScale) {
        TVec3f axisX, axisY;
        MR::makeAxisCrossPlane(&axisX, &axisY, rDir);

        TPos3f tmp1;
        tmp1.identity();
        TPos3f tmp2;
        tmp2.identity();

        tmp1.setXYZDir(axisX, rDir, axisY);

        tmp2.mMtx[0][0] = axisX.x;
        tmp2.mMtx[0][1] = axisX.y;
        tmp2.mMtx[0][2] = axisX.z;
        tmp2.mMtx[1][0] = rDir.x;
        tmp2.mMtx[1][1] = rDir.y;
        tmp2.mMtx[1][2] = rDir.z;
        tmp2.mMtx[2][0] = axisY.x;
        tmp2.mMtx[2][1] = axisY.y;
        tmp2.mMtx[2][2] = axisY.z;

        pDst->zeroTrans();
        pDst->setScale(rScale.x, rScale.y, rScale.z);
        pDst->concat(*pDst, tmp2);
        pDst->concat(tmp1, *pDst);
    }

    void makeMtxTRS(MtxPtr pMtx, f32 tx, f32 ty, f32 tz, f32 rx, f32 ry, f32 rz, f32 sx, f32 sy, f32 sz) {
        f32 sinX = JMASinDegree(rx);
        f32 sinY = JMASinDegree(ry);
        f32 sinZ = JMASinDegree(rz);
        f32 cosX = JMACosDegree(rx);
        f32 cosY = JMACosDegree(ry);
        f32 cosZ = JMACosDegree(rz);

        pMtx[0][0] = sx * (cosZ * cosY);
        pMtx[1][0] = sx * (sinZ * cosY);
        pMtx[2][0] = -sinY * sx;

        pMtx[0][1] = sy * (cosZ * sinY * sinX - sinZ * cosX);
        pMtx[1][1] = sy * (sinZ * sinY * sinX + cosZ * cosX);
        pMtx[2][1] = sy * (cosY * sinX);

        pMtx[0][2] = sz * (cosZ * sinY * cosX + sinZ * sinX);
        pMtx[1][2] = sz * (sinZ * sinY * cosX - cosZ * sinX);
        pMtx[2][2] = sz * (cosY * cosX);

        pMtx[0][3] = tx;
        pMtx[1][3] = ty;
        pMtx[2][3] = tz;
    }

    void makeMtxTRS(MtxPtr pMtx, const TVec3f& rTrans, const TVec3f& rRot, const TVec3f& rScale) {
        makeMtxTRS(pMtx, rTrans.x, rTrans.y, rTrans.z, rRot.x, rRot.y, rRot.z, rScale.x, rScale.y, rScale.z);
    }

    void setMtxAxisXYZ(MtxPtr pMtx, const TVec3f& rAxisX, const TVec3f& rAxisY, const TVec3f& rAxisZ) {
        pMtx[0][0] = rAxisX.x;
        pMtx[1][0] = rAxisX.y;
        pMtx[2][0] = rAxisX.z;
        pMtx[0][1] = rAxisY.x;
        pMtx[1][1] = rAxisY.y;
        pMtx[2][1] = rAxisY.z;
        pMtx[0][2] = rAxisZ.x;
        pMtx[1][2] = rAxisZ.y;
        pMtx[2][2] = rAxisZ.z;
    }

    void flattenMtx(MtxPtr pDst, MtxPtr pSrc, const TVec3f& rNormal) {
        TVec3f axisX, axisY, axisZ;
        MR::extractMtxXDir(pSrc, &axisX);
        MR::extractMtxYDir(pSrc, &axisY);
        MR::extractMtxZDir(pSrc, &axisZ);

        axisX.orthogonalize(rNormal);
        axisY.orthogonalize(rNormal);
        axisZ.orthogonalize(rNormal);

        MR::setMtxAxisXYZ(pDst, axisX, axisY, axisZ);
    }

    void flattenMtx(MtxPtr pMtx, const TVec3f& rNormal) {
        flattenMtx(pMtx, pMtx, rNormal);
    }

    void blendMtxRotate(MtxPtr pMtxA, MtxPtr pMtxB, f32 blend, MtxPtr pDst) {
        Quaternion quatA, quatB, quatR;
        C_QUATMtx(&quatA, pMtxA);
        C_QUATMtx(&quatB, pMtxB);
        JMAQuatLerp(&quatA, &quatB, blend, &quatR);
        PSMTXQuat(pDst, &quatR);
    }

    void blendMtxRotateSlerp(MtxPtr pMtxA, MtxPtr pMtxB, f32 blend, MtxPtr pDst) {
        Quaternion quatA, quatB, quatR;
        C_QUATMtx(&quatA, pMtxA);
        C_QUATMtx(&quatB, pMtxB);
        C_QUATSlerp(&quatA, &quatB, &quatR, blend);
        PSMTXQuat(pDst, &quatR);
    }

    void blendMtx(MtxPtr pMtxA, MtxPtr pMtxB, f32 blend, MtxPtr pDst) {
        TVec3f transA, transB, transR;
        extractMtxTrans(pMtxA, &transA);
        extractMtxTrans(pMtxB, &transB);

        transR = transA * (1.0f - blend) + transB * blend;

        blendMtxRotate(pMtxA, pMtxB, blend, pDst);
        setMtxTrans(pDst, transR.x, transR.y, transR.z);
    }

    void makeMtxWithoutScale(TPos3f* pDst, const TPos3f& rSrc) {
        TVec3f trans;
        rSrc.getTrans(trans);

        TVec3f axisX, axisY, axisZ;
        rSrc.getXYZDir(axisX, axisY, axisZ);

        pDst->setTrans(trans);

        MR::normalize(&axisX);
        MR::normalize(&axisY);
        MR::normalize(&axisZ);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeSRTFromMtxPtr(TVec3f* pOutTrans, TVec3f* pOutRot, TVec3f* pOutScale, MtxPtr pSrc, bool toDegree) {
        TVec3f scale;
        scale.x = JGeometry::TUtil< f32 >::sqrt(pSrc[0][0] * pSrc[0][0] + pSrc[1][0] * pSrc[1][0] + pSrc[2][0] * pSrc[2][0]);
        scale.y = JGeometry::TUtil< f32 >::sqrt(pSrc[0][1] * pSrc[0][1] + pSrc[1][1] * pSrc[1][1] + pSrc[2][1] * pSrc[2][1]);
        scale.z = JGeometry::TUtil< f32 >::sqrt(pSrc[0][2] * pSrc[0][2] + pSrc[1][2] * pSrc[1][2] + pSrc[2][2] * pSrc[2][2]);

        TPos3f scaleMtx;
        scaleMtx.identity();
        scaleMtx.setScale(JMath::fastReciprocal(scale.x), JMath::fastReciprocal(scale.y), JMath::fastReciprocal(scale.z));

        TPos3f mtx;
        mtx.concat(*reinterpret_cast< TPos3f* >(pSrc), scaleMtx);

        if (pOutTrans != nullptr) {
            mtx.getTrans(*pOutTrans);
        }

        if (pOutRot != nullptr) {
            mtx.getEuler(*pOutRot);

            if (toDegree) {
                pOutRot->set(*pOutRot * _180_PI);
            }
        }

        if (pOutScale != nullptr) {
            pOutScale->set(scale);
        }
    }

    void makeRTFromMtxPtr(TVec3f* pOutTrans, TVec3f* pOutRot, MtxPtr pSrc, bool toDegree) {
        TPos3f* pMtx = reinterpret_cast< TPos3f* >(pSrc);
        if (pOutTrans != nullptr) {
            pMtx->getTrans(*pOutTrans);
        }

        if (pOutRot != nullptr) {
            pMtx->getEuler(*pOutRot);

            if (toDegree) {
                pOutRot->set(*pOutRot * _180_PI);
            }
        }
    }

    void makeMtxSideUp(TPos3f* pDst, const TVec3f& rSide, const TVec3f& rUp) {
        TVec3f axisZ, axisY, axisX;
        MR::normalize(&axisX, rSide);

        axisZ.cross(axisX, rUp);
        MR::normalize(&axisZ);

        axisY.cross(axisZ, axisX);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxSideUpPos(TPos3f* pDst, const TVec3f& rSide, const TVec3f& rUp, const TVec3f& rPos) {
        makeMtxSideUp(pDst, rSide, rUp);
        pDst->setTrans(rPos);
    }

    void makeMtxSideFront(TPos3f* pDst, const TVec3f& rSide, const TVec3f& rFront) {
        TVec3f axisZ, axisY, axisX;
        MR::normalize(&axisX, rSide);

        axisY.cross(rFront, axisX);
        MR::normalize(&axisY);

        axisZ.cross(axisX, axisY);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxUpSide(TPos3f* pDst, const TVec3f& rUp, const TVec3f& rSide) {
        TVec3f axisZ, axisY, axisX;
        MR::normalize(&axisY, rUp);

        axisZ.cross(rSide, axisY);
        MR::normalize(&axisZ);

        axisX.cross(axisY, axisZ);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxUpSidePos(TPos3f* pDst, const TVec3f& rUp, const TVec3f& rSide, const TVec3f& rPos) {
        makeMtxUpSide(pDst, rUp, rSide);
        pDst->setTrans(rPos);
    }

    void makeMtxUpFront(TPos3f* pDst, const TVec3f& rUp, const TVec3f& rFront) {
        TVec3f axisZ, axisY, axisX;
        MR::normalize(&axisY, rUp);

        axisX.cross(axisY, rFront);
        MR::normalize(&axisX);

        axisZ.cross(axisX, axisY);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxUpFrontPos(TPos3f* pDst, const TVec3f& rUp, const TVec3f& rFront, const TVec3f& rPos) {
        makeMtxUpFront(pDst, rUp, rFront);
        pDst->setTrans(rPos);
    }

    void makeMtxFrontSidePos(TPos3f* pDst, const TVec3f& rFront, const TVec3f& rSide, const TVec3f& rPos) {
        TVec3f axisX, axisY, axisZ;
        MR::normalize(&axisZ, rFront);

        axisY.cross(axisZ, rSide);
        MR::normalize(&axisY);

        axisX.cross(axisY, axisZ);

        pDst->setXYZDir(axisX, axisY, axisZ);
        pDst->setTrans(rPos);
    }

    void makeMtxFrontUp(TPos3f* pDst, const TVec3f& rFront, const TVec3f& rUp) {
        TVec3f axisZ, axisY, axisX;
        MR::normalize(&axisZ, rFront);

        axisX.cross(rUp, axisZ);
        MR::normalize(&axisX);

        axisY.cross(axisZ, axisX);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxFrontUpPos(TPos3f* pDst, const TVec3f& rFront, const TVec3f& rUp, const TVec3f& rPos) {
        makeMtxFrontUp(pDst, rFront, rUp);
        pDst->setTrans(rPos);
    }

    void makeMtxUpNoSupport(TPos3f* pDst, const TVec3f& rUp) {
        TVec3f support;
        if (MR::getMaxAbsElementIndex(rUp) == 2) {
            support.set< f32 >(0.0f, 1.0f, 0.0f);
        } else {
            support.set< f32 >(0.0f, 0.0f, 1.0f);
        }

        TVec3f axisX, axisY, axisZ;
        MR::normalize(&axisY, rUp);

        axisX.cross(axisY, support);
        MR::normalize(&axisX);

        axisZ.cross(axisX, axisY);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxUpNoSupportPos(TPos3f* pDst, const TVec3f& rUp, const TVec3f& rPos) {
        TVec3f support;
        if (MR::getMaxAbsElementIndex(rUp) == 2) {
            support.set< f32 >(0.0f, 1.0f, 0.0f);
        } else {
            support.set< f32 >(0.0f, 0.0f, 1.0f);
        }

        MR::makeMtxUpFrontPos(pDst, rUp, support, rPos);
    }

    void makeMtxFrontNoSupport(TPos3f* pDst, const TVec3f& rFront) {
        TVec3f support;
        if (MR::getMaxAbsElementIndex(rFront) == 1) {
            support.set< f32 >(1.0f, 0.0f, 0.0f);
        } else {
            support.set< f32 >(0.0f, 1.0f, 0.0f);
        }

        TVec3f axisX, axisY, axisZ;
        MR::normalize(&axisZ, rFront);

        axisX.cross(support, axisZ);
        MR::normalize(&axisX);

        axisY.cross(axisZ, axisX);

        pDst->setXYZDir(axisX, axisY, axisZ);
    }

    void makeMtxFrontNoSupportPos(TPos3f* pDst, const TVec3f& rFront, const TVec3f& rPos) {
        TVec3f support;
        if (MR::getMaxAbsElementIndex(rFront) == 1) {
            support.set< f32 >(1.0f, 0.0f, 0.0f);
        } else {
            support.set< f32 >(0.0f, 1.0f, 0.0f);
        }

        MR::makeMtxFrontUpPos(pDst, rFront, support, rPos);
    }

#pragma push
#pragma opt_propagation off
    void orthogonalize(TPos3f* pMtx) {
        TVec3f axisZ, axisY, axisX;

        pMtx->getXYZDir(axisX, axisY, axisZ);

        TVec3f* pZ;
        TVec3f* pY;
        pY = &axisY;
        pZ = &axisZ;

        PSVECCrossProduct(pY, pZ, &axisX);
        PSVECCrossProduct(pZ, &axisX, pY);

        axisX.normalize();
        pY->normalize();

        pMtx->setXYZDir(axisX, *pY, *pZ);

        TVec3f zDir;
        pMtx->getZDir(zDir);

        JGeometry::TUtil< f32 >::sqrt((pMtx->get(0, 0) * pMtx->get(0, 0)) + (pMtx->get(1, 0) * pMtx->get(1, 0)) + (pMtx->get(2, 0) * pMtx->get(2, 0)) +
                                      (pMtx->get(0, 1) * pMtx->get(0, 1)) + (pMtx->get(1, 1) * pMtx->get(1, 1)) + (pMtx->get(2, 1) * pMtx->get(2, 1)) +
                                      (pMtx->get(0, 2) * pMtx->get(0, 2)) + (pMtx->get(1, 2) * pMtx->get(1, 2)) + (pMtx->get(2, 2) * pMtx->get(2, 2)));

        if (pMtx != nullptr) {
            f32 invLenX = JGeometry::TUtil< f32 >::inv_sqrt((pMtx->get(0, 0) * pMtx->get(0, 0)) + (pMtx->get(1, 0) * pMtx->get(1, 0)) +
                                                            (pMtx->get(2, 0) * pMtx->get(2, 0)));
            pMtx->mMtx[0][0] = invLenX * pMtx->get(0, 0);
            pMtx->mMtx[1][0] = invLenX * pMtx->get(1, 0);
            pMtx->mMtx[2][0] = invLenX * pMtx->get(2, 0);

            f32 invLenY = JGeometry::TUtil< f32 >::inv_sqrt((pMtx->get(0, 1) * pMtx->get(0, 1)) + (pMtx->get(1, 1) * pMtx->get(1, 1)) +
                                                            (pMtx->get(2, 1) * pMtx->get(2, 1)));
            pMtx->mMtx[0][1] = invLenY * pMtx->get(0, 1);
            pMtx->mMtx[1][1] = invLenY * pMtx->get(1, 1);
            pMtx->mMtx[2][1] = invLenY * pMtx->get(2, 1);

            f32 invLenZ = JGeometry::TUtil< f32 >::inv_sqrt((pMtx->get(0, 2) * pMtx->get(0, 2)) + (pMtx->get(1, 2) * pMtx->get(1, 2)) +
                                                            (pMtx->get(2, 2) * pMtx->get(2, 2)));
            pMtx->mMtx[0][2] = invLenZ * pMtx->get(0, 2);
            pMtx->mMtx[1][2] = invLenZ * pMtx->get(1, 2);
            pMtx->mMtx[2][2] = invLenZ * pMtx->get(2, 2);
        }

        pMtx->mMtx[0][2] = zDir.x;
        pMtx->mMtx[1][2] = zDir.y;
        pMtx->mMtx[2][2] = zDir.z;
    }
#pragma pop

    void turnMtxToXDirRate(TPos3f* pMtx, const TVec3f& rDir, f32 rate) {
        TQuat4f quat;
        pMtx->getQuat(quat);
        MR::turnQuatXDirRate(&quat, quat, rDir, rate);
        pMtx->setQuat(quat);
    }

    void turnMtxToXDirDegree(TPos3f* pMtx, const TVec3f& rDir, f32 degree) {
        TQuat4f quat;
        pMtx->getQuat(quat);
        MR::turnQuatXDirRad(&quat, quat, rDir, PI_180 * degree);
        pMtx->setQuat(quat);
    }

    void turnMtxToYDirRate(TPos3f* pMtx, const TVec3f& rDir, f32 rate) {
        TQuat4f quat;
        pMtx->getQuat(quat);
        MR::turnQuatYDirRate(&quat, quat, rDir, rate);
        pMtx->setQuat(quat);
    }

    void turnMtxToYDirDegree(TPos3f* pMtx, const TVec3f& rDir, f32 degree) {
        TQuat4f quat;
        pMtx->getQuat(quat);
        MR::turnQuatYDirRad(&quat, quat, rDir, PI_180 * degree);
        pMtx->setQuat(quat);
    }

    void turnMtxToLocalDirDegree(TPos3f* pMtx, const TVec3f& rLocalAxis, const TVec3f& rDir, f32 degree) {
        TVec3f worldAxis;
        pMtx->mult33(rLocalAxis, worldAxis);

        TQuat4f quat;
        pMtx->getQuat(quat);
        MR::turnQuat(&quat, quat, worldAxis, rDir, PI_180 * degree);
        pMtx->setQuat(quat);
    }

    void makeMtxMoment(TPos3f* pMtx, const TVec3f& rMoment) {
        pMtx->identity();

        if (!rMoment.isZero()) {
            TVec3f dir(rMoment);
            f32 mag;
            MR::separateScalarAndDirection(&mag, &dir, dir);
            pMtx->makeRotate(dir, mag);
        }
    }

    // Non-official symbol.
    void concatMtxKeepTrans(MtxPtr pDst, MtxPtr pA, MtxPtr pB) {
        TVec3f trans(pB[0][3], pB[1][3], pB[2][3]);
        pB[0][3] = 0.0f;
        pB[1][3] = 0.0f;
        pB[2][3] = 0.0f;
        PSMTXConcat(pA, pB, pDst);
        pDst[0][3] = trans.x;
        pDst[1][3] = trans.y;
        pDst[2][3] = trans.z;
    }

    void setMtxTrans(MtxPtr mtx, f32 x, f32 y, f32 z) {
        mtx[0][3] = x;
        mtx[1][3] = y;
        mtx[2][3] = z;
    }

    void addTransMtx(MtxPtr mtx, const TVec3f& rTrans) {
        mtx[0][3] += rTrans.x;
        mtx[1][3] += rTrans.y;
        mtx[2][3] += rTrans.z;
    }

    void addTransMtxLocal(MtxPtr mtx, const TVec3f& rVec) {
        MR::addTransMtxLocalX(mtx, rVec.x);
        MR::addTransMtxLocalY(mtx, rVec.y);
        MR::addTransMtxLocalZ(mtx, rVec.z);
    }

    void addTransMtxLocalX(MtxPtr mtx, f32 x) {
        mtx[0][3] += mtx[0][0] * x;
        mtx[1][3] += mtx[1][0] * x;
        mtx[2][3] += mtx[2][0] * x;
    }

    void addTransMtxLocalY(MtxPtr mtx, f32 y) {
        mtx[0][3] += mtx[0][1] * y;
        mtx[1][3] += mtx[1][1] * y;
        mtx[2][3] += mtx[2][1] * y;
    }

    void addTransMtxLocalZ(MtxPtr mtx, f32 z) {
        mtx[0][3] += mtx[0][2] * z;
        mtx[1][3] += mtx[1][2] * z;
        mtx[2][3] += mtx[2][2] * z;
    }

    void extractMtxXDir(MtxPtr mtx, TVec3f* pDir) {
        pDir->x = mtx[0][0];
        pDir->y = mtx[1][0];
        pDir->z = mtx[2][0];
    }

    void extractMtxYDir(MtxPtr mtx, TVec3f* pDir) {
        pDir->x = mtx[0][1];
        pDir->y = mtx[1][1];
        pDir->z = mtx[2][1];
    }

    void extractMtxZDir(MtxPtr mtx, TVec3f* pDir) {
        pDir->x = mtx[0][2];
        pDir->y = mtx[1][2];
        pDir->z = mtx[2][2];
    }

    void extractMtxXYZDir(MtxPtr mtx, TVec3f* pX, TVec3f* pY, TVec3f* pZ) {
        MR::extractMtxXDir(mtx, pX);
        MR::extractMtxYDir(mtx, pY);
        MR::extractMtxZDir(mtx, pZ);
    }

    void extractMtxTrans(MtxPtr mtx, TVec3f* pTrans) {
        pTrans->x = mtx[0][3];
        pTrans->y = mtx[1][3];
        pTrans->z = mtx[2][3];
    }

    /*
    f32 sqrt(f32 val) {
        if (val < 0.0f) {
            return val;
        }

        #ifdef __MWERKS__
        f64 sq = __frsqrte(val);
        #else
        f32 sq = 0.0f;
        #endif

        return ((-(((sq * val) * sq) - 3.0f) * (sq * val)) * 0.5f);
    }*/

    namespace {
        inline f32 safeReciprocal(f32 x) {
            return MR::isNearZero(x) ? 0.0f : 1.0f / x;
        }
    }  // namespace

    // Non-official symbol.
    void separateScaleMtx(MtxPtr pRotDst, MtxPtr pScaleDst, MtxPtr pSrc) {
        TVec3f scaleSq;
        scaleSq.x = pSrc[0][0] * pSrc[0][0] + pSrc[1][0] * pSrc[1][0] + pSrc[2][0] * pSrc[2][0];
        scaleSq.y = pSrc[0][1] * pSrc[0][1] + pSrc[1][1] * pSrc[1][1] + pSrc[2][1] * pSrc[2][1];
        scaleSq.z = pSrc[0][2] * pSrc[0][2] + pSrc[1][2] * pSrc[1][2] + pSrc[2][2] * pSrc[2][2];
        PSMTXScale(pScaleDst, MR::sqrt(scaleSq.x), MR::sqrt(scaleSq.y), MR::sqrt(scaleSq.z));

        Mtx invScale;
        PSMTXScale(invScale, safeReciprocal(pScaleDst[0][0]), safeReciprocal(pScaleDst[1][1]), safeReciprocal(pScaleDst[2][2]));
        PSMTXConcat(pSrc, invScale, pRotDst);
    }

    bool isSameMtx(MtxPtr a, MtxPtr b) {
        f32* a2 = (f32*)a;
        f32* b2 = (f32*)b;
        for (u32 i = 0; i < 12; a2++, b2++, i++) {
            if (*a2 != *b2) {
                return false;
            }
        }
        return true;
    }

    bool isSameMtxRot(MtxPtr a, MtxPtr b) {
        f32* a2 = (f32*)a;
        f32* b2 = (f32*)b;
        for (u32 i = 0; i < 12; a2++, b2++, i++) {
            if ((i % 4) == 3) {
                continue;
            }
            if (*a2 != *b2) {
                return false;
            }
        }
        return true;
    }

    bool isRotAxisY(MtxPtr pMtxA, MtxPtr pMtxB) {
        TVec3f yDirA, yDirB;
        ((TRot3f*)pMtxA)->getYDir(yDirA);
        ((TRot3f*)pMtxB)->getYDir(yDirB);
        bool result = false;

        if (JGeometry::TUtil< f32 >::epsilonEquals(yDirA.x, yDirB.x, JGeometry::TUtil< f32 >::epsilon()) &&
            JGeometry::TUtil< f32 >::epsilonEquals(yDirA.y, yDirB.y, JGeometry::TUtil< f32 >::epsilon()) &&
            JGeometry::TUtil< f32 >::epsilonEquals(yDirA.z, yDirB.z, JGeometry::TUtil< f32 >::epsilon())) {
            result = true;
        }

        return result;
    }

    void calcMtxRotAxis(TVec3f* pOut, MtxPtr pMtxA, MtxPtr pMtxB) {
        TVec3f localY(0.0f, 1.0f, 0.0f);

        Mtx invA;
        PSMTXInverse(pMtxA, invA);

        TVec3f axisYA, axisYB;
        PSMTXMultVecSR(invA, &localY, &axisYA);
        PSMTXMultVecSR(pMtxB, &axisYA, &axisYB);

        TVec3f cross = localY.cross(axisYB);

        if (MR::normalizeOrZero(&cross)) {
            *pOut = localY;
        } else {
            *pOut = cross;
        }
    }

    MtxPtr tmpMtxTrans(const TVec3f& rVec) {
        setMtxTrans(mtrans_org, rVec.x, rVec.y, rVec.z);
        return mtrans_org;
    }

    MtxPtr tmpMtxScale(f32 x, f32 y, f32 z) {
        tmpmtx_sc[0][0] = x;
        tmpmtx_sc[1][1] = y;
        tmpmtx_sc[2][2] = z;
        return tmpmtx_sc;
    }

    MtxPtr tmpMtxRotXRad(f32 angle) {
        f32 cos = JMACosRadian(angle);
        f32 sin = JMASinRadian(angle);
        tmpmtx_rx[1][1] = cos;
        tmpmtx_rx[2][1] = sin;
        tmpmtx_rx[1][2] = -sin;
        tmpmtx_rx[2][2] = cos;
        return tmpmtx_rx;
    }

    MtxPtr tmpMtxRotYRad(f32 angle) {
        f32 cos = JMACosRadian(angle);
        f32 sin = JMASinRadian(angle);
        tmpmtx_ry[0][0] = cos;
        tmpmtx_ry[0][2] = sin;
        tmpmtx_ry[2][0] = -sin;
        tmpmtx_ry[2][2] = cos;
        return tmpmtx_ry;
    }

    MtxPtr tmpMtxRotZRad(f32 angle) {
        f32 cos = JMACosRadian(angle);
        f32 sin = JMASinRadian(angle);
        tmpmtx_rz[0][0] = cos;
        tmpmtx_rz[1][0] = sin;
        tmpmtx_rz[0][1] = -sin;
        tmpmtx_rz[1][1] = cos;
        return tmpmtx_rz;
    }

    MtxPtr tmpMtxRotXDeg(f32 angle) {
        f32 cos = JMACosDegree(angle);
        f32 sin = JMASinDegree(angle);
        tmpmtx_rx[1][1] = cos;
        tmpmtx_rx[2][1] = sin;
        tmpmtx_rx[1][2] = -sin;
        tmpmtx_rx[2][2] = cos;
        return tmpmtx_rx;
    }

    MtxPtr tmpMtxRotYDeg(f32 angle) {
        f32 cos = JMACosDegree(angle);
        f32 sin = JMASinDegree(angle);
        tmpmtx_ry[0][0] = cos;
        tmpmtx_ry[0][2] = sin;
        tmpmtx_ry[2][0] = -sin;
        tmpmtx_ry[2][2] = cos;
        return tmpmtx_ry;
    }

    MtxPtr tmpMtxRotZDeg(f32 angle) {
        f32 cos = JMACosDegree(angle);
        f32 sin = JMASinDegree(angle);
        tmpmtx_rz[0][0] = cos;
        tmpmtx_rz[1][0] = sin;
        tmpmtx_rz[0][1] = -sin;
        tmpmtx_rz[1][1] = cos;
        return tmpmtx_rz;
    }

    void orderRotateMtx(s16 idx, const TVec3f& rSrc, MtxPtr mtx) {
        MtxPtr xRot = MR::tmpMtxRotXRad(rSrc.x);
        MtxPtr yRot = MR::tmpMtxRotYRad(rSrc.y);
        MtxPtr zRot = MR::tmpMtxRotZRad(rSrc.z);

        MtxPtr v9 = yRot;
        MtxPtr v10;
        MtxPtr v12;

        switch (idx) {
        case 0:
            v12 = v9;
            v10 = xRot;
            v9 = zRot;
            break;
        case 1:
            v10 = xRot;
            v12 = zRot;
            break;
        case 2:
            v10 = v9;
            v12 = xRot;
            v9 = zRot;
            break;
        case 3:
            v10 = v9;
            v12 = zRot;
            v9 = xRot;
            break;
        case 4:
            v10 = zRot;
            v12 = xRot;
            v9 = zRot;
            break;
        case 5:
            v12 = v9;
            v10 = zRot;
            v9 = xRot;
            break;
        }

        PSMTXConcat(v12, v10, mtx);
        PSMTXConcat(v9, mtx, mtx);
    }

    void inverseConcatMtx(MtxPtr a1, MtxPtr a2, TMtx34f* pMtx) {
        Mtx mtx;
        PSMTXInverse(a1, mtx);
        PSMTXConcat(mtx, a2, *pMtx);
    }
};  // namespace MR
