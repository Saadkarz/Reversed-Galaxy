#pragma once

#include "Game/System/StationedFileInfo.hpp"

class JKRHeap;

class StationedArchiveLoader {
public:
    class __declspec(novtable) Condition {
    public:
        virtual ~Condition();
        virtual bool isExecute(const MR::StationedFileInfo*) const = 0;
        virtual JKRHeap* getProperHeap(const MR::StationedFileInfo*) const;
    };

    static JKRHeap* getProperHeap(const MR::StationedFileInfo*);
    static void loadResourcesFromTable(const StationedArchiveLoader::Condition&);
    static void createAndAddResourcesFromTable(const StationedArchiveLoader::Condition&);
    static bool createAndAddResourcesFromTable(const StationedArchiveLoader::Condition&, s32, s32);
    static void loadScenarioData(JKRHeap*);
};
