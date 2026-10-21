#pragma once

#include <JSystem/JGeometry/TVec.hpp>

class CollisionParts;
class CollisionPartsFilterBase;
class HitInfo;
class HitSensor;
class JMapInfoIter;
class LiveActor;
class Triangle;
class TriangleFilterBase;

namespace MR {
    const TVec3f* getNormal(const Triangle*);
    bool isWallPolygon(const TVec3f&, const TVec3f&);
    bool isFloorPolygon(const TVec3f&, const TVec3f&);
    bool isFloorPolygonCos(const TVec3f&, const TVec3f&, f32);
    bool isWallPolygon(f32);
    bool isCeilingPolygon(f32);
    bool isWaterPolygon(const Triangle*);
    bool isThroughPolygon(const Triangle*);
    bool getFirstPolyOnLineToMap(TVec3f*, Triangle*, const TVec3f&, const TVec3f&);
    bool getFirstPolyOnLineToMapAndMoveLimit(TVec3f*, Triangle*, const TVec3f&, const TVec3f&);
    bool getFirstPolyOnLineToWaterSurface(TVec3f*, Triangle*, const TVec3f&, const TVec3f&);
    bool getFirstPolyOnLineToMapExceptSensor(TVec3f*, Triangle*, const TVec3f&, const TVec3f&, const HitSensor*);
    bool getFirstPolyOnLineToMapExceptActor(TVec3f*, Triangle*, const TVec3f&, const LiveActor*);
    bool getFirstPolyOnLineToMap(TVec3f*, Triangle*, const TVec3f&, const TVec3f&, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    bool getFirstPolyOnLineToWaterSurface(TVec3f*, Triangle*, const TVec3f&, const TVec3f&, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    bool isGroundCodeDeath(const Triangle*);
    bool isGroundCodeDamage(const Triangle*);
    bool isGroundCodeDamageFire(const Triangle*);
    bool isGroundCodeFireDance(const Triangle*);
    bool isGroundCodeDamageElectric(const Triangle*);
    bool isGroundCodeSinkDeath(const Triangle*);
    bool isGroundCodeSinkDeathMud(const Triangle*);
};  // namespace MR

namespace Collision {
    void addToGlobal(CollisionParts*);
    void removeToGlobal(CollisionParts*);
    s32 checkStrikePointToMap(const TVec3f&, HitInfo*);
    s32 checkStrikeBallToMap(const TVec3f&, f32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeBallToMapWithMovingReaction(const TVec3f&, f32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeBallToMapWithThickness(const TVec3f&, f32, f32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeLineToMap(const TVec3f&, const TVec3f&, s32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    s32 checkStrikeLineToSunshade(const TVec3f&, const TVec3f&, s32, const CollisionPartsFilterBase*, const TriangleFilterBase*);
    const HitInfo* getStrikeInfoMap(u32);
    u32 getStrikeInfoNumMap();
};  // namespace Collision
