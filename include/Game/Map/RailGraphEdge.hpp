#pragma once

#include <revolution.h>

class JMapInfo;

class RailGraphEdge {
public:
    RailGraphEdge();

    void clearConnectInfo();
    s32 getNextNode(s32) const;
    s32 getNextEdge(s32) const;
    void setNextEdge(s32, s32);
    void setArgs(const JMapInfo*, s32);

    RailGraphEdge& operator=(const RailGraphEdge& rEdge);

    f32 mDistance;  // 0x0
    s32 _4;
    s32 _8;
    s32 _C;
    s32 _10;
    s32 mPointArg0;  // 0x14
    s32 mPointArg1;  // 0x18
    s32 mPointArg2;  // 0x1C
    s32 mPointArg3;  // 0x20
    s32 mPointArg4;  // 0x24
    s32 mPointArg5;  // 0x28
    s32 mPointArg6;  // 0x2C
    s32 mPointArg7;  // 0x30
};
