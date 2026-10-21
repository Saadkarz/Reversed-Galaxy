#include "Game/System/StationedArchiveLoader.hpp"
#include "Game/System/ResourceHolderManager.hpp"
#include "Game/Util/SingletonHolder.hpp"
#include "Game/Util.hpp"
#include <JSystem/JKernel/JKRExpHeap.hpp>
#include <revolution/dvd.h>

StationedArchiveLoader::Condition::~Condition() {
}

JKRHeap* StationedArchiveLoader::Condition::getProperHeap(const MR::StationedFileInfo*) const {
    return nullptr;
}

JKRHeap* StationedArchiveLoader::getProperHeap(const MR::StationedFileInfo* pInfo) {
    switch (pInfo->mHeapType) {
    case MR::StationedFileInfo::HEAP_TYPE_NAPA:
        return MR::getStationedHeapNapa();
    case MR::StationedFileInfo::HEAP_TYPE_GDDR:
        return MR::getStationedHeapGDDR3();
    default:
        return nullptr;
    }
}

void StationedArchiveLoader::loadResourcesFromTable(const StationedArchiveLoader::Condition& condition) {
    for (const MR::StationedFileInfo* pInfo = MR::getStationedFileInfoTable(); pInfo->mArchive != nullptr; pInfo++) {
        if (!condition.isExecute(pInfo)) {
            continue;
        }

        JKRHeap* pHeap = condition.getProperHeap(pInfo);
        if (pHeap == nullptr) {
            pHeap = getProperHeap(pInfo);
        }
        switch (pInfo->mLoadType) {
        case MR::StationedFileInfo::LOAD_TYPE_FILE:
            MR::loadToMainRAM(pInfo->mArchive, nullptr, pHeap, 1);
            break;
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
            MR::mountArchive(pInfo->mArchive, pHeap, true);
            break;
        }
    }
}

void StationedArchiveLoader::loadScenarioData(JKRHeap* pHeap) {
    DVDDir dir;
    DVDDirEntry entry;
    char path[256];

    DVDOpenDir("/StageData", &dir);

    while (DVDReadDir(&dir, &entry)) {
        if (entry.isDir) {
            MR::makeScenarioArchiveFileName(path, sizeof(path), entry.name);
            if (MR::isFileExist(path, false)) {
                MR::mountArchive(path, pHeap, true);
            }
        }
    }

    DVDCloseDir(&dir);
}

void StationedArchiveLoader::createAndAddResourcesFromTable(const StationedArchiveLoader::Condition& condition) {
    for (const MR::StationedFileInfo* pInfo = MR::getStationedFileInfoTable(); pInfo->mArchive != nullptr; pInfo++) {
        if (!condition.isExecute(pInfo)) {
            continue;
        }

        
        
        switch (pInfo->mLoadType) {
        case 3:
        case 4:
        case 5:
        case 6:
            SingletonHolder<ResourceHolderManager>::get()->createAndAddStationed(pInfo->mArchive);
            break;
        case 7:
        case 8:
            SingletonHolder<ResourceHolderManager>::get()->createAndAddLayoutHolderStationed(pInfo->mArchive);
            break;
        }
    }
}

bool StationedArchiveLoader::createAndAddResourcesFromTable(const StationedArchiveLoader::Condition& condition, s32 min, s32 max) {
    s32 count;
    const MR::StationedFileInfo* pInfo = MR::getStationedFileInfoTable();
    count = 0;

    for (; pInfo->mArchive != nullptr; pInfo++) {
        if (!condition.isExecute(pInfo)) {
            continue;
        }

        count++;
        if (count <= min) {
            continue;
        }
        if (count > max) {
            return false;
        }

        switch (pInfo->mLoadType) {
        case 3:
        case 4:
        case 5:
        case 6:
            SingletonHolder<ResourceHolderManager>::get()->createAndAddStationed(pInfo->mArchive);
            break;
        case 7:
        case 8:
            SingletonHolder<ResourceHolderManager>::get()->createAndAddLayoutHolderStationed(pInfo->mArchive);
            break;
        }
    }

    return true;
}
