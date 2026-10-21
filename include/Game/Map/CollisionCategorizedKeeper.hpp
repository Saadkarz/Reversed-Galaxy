#pragma once

#include "Game/Map/HitInfo.hpp"
#include "Game/NameObj/NameObj.hpp"
#include <revolution.h>

class CollisionZone;
class CollisionParts;
class TriangleFilterBase;
class CollisionPartsFilterBase;

class CollisionCategorizedKeeper : public NameObj {
public:
    CollisionCategorizedKeeper(s32);

    virtual ~CollisionCategorizedKeeper();
    virtual void movement();

    void addToZone(CollisionParts*, s32);
    void removeFromZone(CollisionParts*, s32);
    void addToGlobal(CollisionParts*);
    void removeFromGlobal(CollisionParts*);

    s32 checkStrikePoint(const TVec3f&, HitInfo*);
    s32 checkStrikeBall(const TVec3f&, f32, bool, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeBallWithThickness(const TVec3f&, f32, f32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeLine(const TVec3f&, const TVec3f&, s32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    u32 createAreaPolygonList(Triangle*, u32, const TVec3f&, const TVec3f&);
    u32 createAreaPolygonListArray(Triangle*, u32, TVec3f*, u32);
    bool isSphereOverlappingWithBox(const TVec3f&, const TVec3f&, const TVec3f&, f32);
    bool searchSameHostParts(CollisionParts**, CollisionParts*) const;
    HitInfo* getStrikeInfo(u32);
    CollisionZone* getZone(int);
};
