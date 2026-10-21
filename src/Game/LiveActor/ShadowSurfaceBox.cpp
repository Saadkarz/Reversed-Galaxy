#include "Game/LiveActor/ShadowSurfaceBox.hpp"
#include "Game/LiveActor/LiveActor.hpp"
#include "Game/LiveActor/ShadowController.hpp"
#include "Game/LiveActor/ShadowSurfaceDrawer.hpp"
#include "Game/Util/DirectDraw.hpp"
#include <JSystem/JGeometry/TMatrix.hpp>
#include <JSystem/JGeometry/TVec.hpp>
#include <revolution/gx/GXEnum.h>
#include <revolution/gx/GXGeometry.h>
#include <revolution/gx/GXVert.h>
#include <revolution/mtx.h>

ShadowSurfaceBox::ShadowSurfaceBox() : ShadowSurfaceDrawer(((void)1.0f, (void)0.0f, (void)0.5f, (void)-1.0f, "影描画[水面ボックス]")), mSize(100.0f, 100.0f, 100.0f) {
}

void ShadowSurfaceBox::setSize(const TVec3f& pSize) {
    mSize.x = pSize.x;
    mSize.y = pSize.y;
    mSize.z = pSize.z;
}

void ShadowSurfaceBox::draw() const {
    ShadowController* controller = getController();

    if (!controller->isProjected() || !controller->isDraw()) {
        return;
    }

    TPos3f baseMtx;
    controller->getBaseMtx(baseMtx.toMtxPtr());
    TVec3f side;
    TVec3f up;
    TVec3f front;
    baseMtx.getXYZDir(side, up, front);
    TVec3f normal;
    controller->getProjectionNormal(&normal);
    f32 sideDot = normal.dot(side);
    f32 upDot = normal.dot(up);
    f32 frontDot = normal.dot(front);
    TVec3f size(mSize);
    TVec3f position;

    if (controller->isFollowHostScale()) {
        const TVec3f& hostScale = controller->getHost()->mScale;
        TVec3f scale(hostScale);
        scale /= 2.0f;
        size *= scale;
    } else {
        size /= 2.0f;
    }

    side -= normal * sideDot;
    up -= normal * upDot;
    front -= normal * frontDot;
    side.scale(size.x);
    up.scale(size.y);
    front.scale(size.z);
    TPos3f modelMtx;
    modelMtx.setXYZDir(side, up, front);
    controller->getProjectionPos(&position);
    modelMtx.setTrans(position + normal);
    TDDraw::setModelMtx(modelMtx.toMtxPtr());

    sideDot = sideDot >= 0.0f ? 1.0f : -1.0f;
    upDot = upDot >= 0.0f ? 1.0f : -1.0f;
    frontDot = frontDot >= 0.0f ? 1.0f : -1.0f;

    GXBegin(GX_QUADS, GX_VTXFMT0, 4);
    GXPosition3f32(sideDot, -sideDot, -1.0f);
    GXColor1u32(0x80);
    GXPosition3f32(sideDot, -sideDot, 1.0f);
    GXColor1u32(0x80);
    GXPosition3f32(sideDot, sideDot, 1.0f);
    GXColor1u32(0x80);
    GXPosition3f32(sideDot, sideDot, -1.0f);
    GXColor1u32(0x80);
    GXEnd();

    GXBegin(GX_QUADS, GX_VTXFMT0, 4);
    GXPosition3f32(-1.0f, upDot, -upDot);
    GXColor1u32(0x80);
    GXPosition3f32(1.0f, upDot, -upDot);
    GXColor1u32(0x80);
    GXPosition3f32(1.0f, upDot, upDot);
    GXColor1u32(0x80);
    GXPosition3f32(-1.0f, upDot, upDot);
    GXColor1u32(0x80);
    GXEnd();

    GXBegin(GX_QUADS, GX_VTXFMT0, 4);
    GXPosition3f32(-frontDot, -1.0f, frontDot);
    GXColor1u32(0x80);
    GXPosition3f32(-frontDot, 1.0f, frontDot);
    GXColor1u32(0x80);
    GXPosition3f32(frontDot, 1.0f, frontDot);
    GXColor1u32(0x80);
    GXPosition3f32(frontDot, -1.0f, frontDot);
    GXColor1u32(0x80);
    GXEnd();
}

ShadowSurfaceBox::~ShadowSurfaceBox() {
}
