#include "JSystem/JAudio2/JAUSoundTable.hpp"

void JAUSoundTable::init(void const* pData) {
    if (pData != nullptr) {
        mTable.init(pData);
    } else {
        mTable.reset();
    }
}

u8 JAUSoundTable::getTypeID(JAISoundID soundID) const {
    if (soundID.isAnonymous()) {
        return -1;
    }
    JAUSoundTableSection* section = mTable.getSection(soundID.getSectionID());
    if (section == nullptr) {
        return -1;
    }
    JAUSoundTableGroup* group = mTable.getGroup(section, soundID.getGroupID());
    if (group == nullptr) {
        return -1;
    }
    return group->getTypeID(soundID.getWaveID());
}

template <>
JAUSoundTableSection* JAUSoundTable_<JAUSoundTableRoot, JAUSoundTableSection, JAUSoundTableGroup, void>::getSection(int index) const {
    if (index < 0) {
        return nullptr;
    }
    if ((u32)index >= mRoot->mSectionNumber) {
        return nullptr;
    }
    u32 offset = mRoot->mSectionOffsets[index];
    if (offset == 0) {
        return nullptr;
    }
    return (JAUSoundTableSection*)((u8*)mData + offset);
}

template <>
JAUSoundTableGroup* JAUSoundTable_<JAUSoundTableRoot, JAUSoundTableSection, JAUSoundTableGroup, void>::getGroup(const JAUSoundTableSection* section, int index) const {
    if (index < 0) {
        return nullptr;
    }
    if ((u32)index >= section->mNumGroups) {
        return nullptr;
    }
    u32 offset = section->getGroupOffset(index);
    if (offset == 0) {
        return nullptr;
    }
    return (JAUSoundTableGroup*)((u8*)mData + offset);
}

JAUSoundTableItem* JAUSoundTable::getData(JAISoundID soundID) const {
    if (soundID.isAnonymous()) {
        return nullptr;
    }
    JAUSoundTableSection* section = mTable.getSection(soundID.getSectionID());
    if (section == nullptr) {
        return nullptr;
    }
    JAUSoundTableGroup* group = mTable.getGroup(section, soundID.getGroupID());
    if (group == nullptr) {
        return nullptr;
    }
    return getItem(group, soundID.getWaveID());
}
