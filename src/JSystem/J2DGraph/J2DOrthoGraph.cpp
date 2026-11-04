#define J2DORTHO_GRAPH_FILE 1
#define J2DORTHO_NO_GEOMETRY_INLINES 1

#pragma section RX ".unused"

#include "JSystem/J2DGraph/J2DOrthoGraph.hpp"

J2DOrthoGraph::J2DOrthoGraph() : J2DGrafContext(0, 0, 0, 0) {
    this->setLookat();
}

#pragma dont_inline on
template <>
void JGeometry::TBox2< f32 >::set(f32 x0, f32 y0, f32 x1, f32 y1) {
    this->i.x = x0;
    this->i.y = y0;
    this->f.x = x1;
    this->f.y = y1;
}
#pragma dont_inline reset

J2DOrthoGraph::J2DOrthoGraph(f32 x, f32 y, f32 width, f32 height, f32 far, f32 near) : J2DGrafContext(x, y, width, height) {
    JGeometry::TBox2< f32 > box;
    box.set(0, 0, width, height);
    mOrtho = box;
    mNear = -near;
    mFar = -far;
    this->setLookat();
}

void J2DOrthoGraph::setPort() {
    this->J2DGrafContext::setPort();
    C_MTXOrtho(mMtx44, mOrtho.i.y, mOrtho.f.y, mOrtho.i.x, mOrtho.f.x, mNear, mFar);
    GXSetProjection(mMtx44, GX_ORTHOGRAPHIC);
}

void J2DOrthoGraph::setOrtho(JGeometry::TBox2< f32 > const& bounds, f32 far, f32 near) {
    mOrtho = bounds;
    mNear = -near;
    mFar = -far;
}

void J2DOrthoGraph::setLookat() {
    PSMTXIdentity(mPosMtx);
    GXLoadPosMtxImm(mPosMtx, 0);
}

void J2DFillBox(f32 x, f32 y, f32 width, f32 height, JUtility::TColor color) {
    JUtility::TColor col = color;
    JGeometry::TBox2< f32 > box;
    box.set(x, y, x + width, y + height);
    J2DOrthoGraph oGrph;
    oGrph.setColor(col);
    oGrph.fillBox(box);
}
