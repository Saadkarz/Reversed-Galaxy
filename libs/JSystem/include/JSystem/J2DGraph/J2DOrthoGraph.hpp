#pragma once

#include "JSystem/J2DGraph/J2DGrafContext.hpp"
#include "JSystem/JGeometry/TBox.hpp"

class J2DOrthoGraph : public J2DGrafContext {
public:
    J2DOrthoGraph();
    J2DOrthoGraph(f32, f32, f32, f32, f32, f32);

#ifndef J2DORTHO_GRAPH_FILE
    virtual ~J2DOrthoGraph() {}
    virtual void setPort();
    virtual J2DGrafType getGrafType() const {
        return J2DGraf_Ortho;
    }
#else
    __declspec(section ".unused") virtual ~J2DOrthoGraph() {}
    virtual void setPort();
    __declspec(section ".unused") virtual J2DGrafType getGrafType() const {
        return J2DGraf_Ortho;
    }
#endif
    virtual void setLookat();

    void setOrtho(const TBox2f& rBounds, f32 far, f32 near);

    /* 0xBC */ TBox2f mOrtho;
    /* 0xCC */ f32 mNear;
    /* 0xD0 */ f32 mFar;
};

void J2DFillBox(f32 x, f32 y, f32 width, f32 height, JUtility::TColor color);
