#include "JSystem/JAudio2/JAUSoundTable.hpp"

template <>
JAUSoundNameTableSection* JAUSoundTable_<JAUSoundNameTableRoot, JAUSoundNameTableSection, JAUSoundNameTableGroup, char>::getSection(int index) const {
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
    return (JAUSoundNameTableSection*)((u8*)mData + offset);
}

template <>
JAUSoundNameTableGroup* JAUSoundTable_<JAUSoundNameTableRoot, JAUSoundNameTableSection, JAUSoundNameTableGroup, char>::getGroup(const JAUSoundNameTableSection* section, int index) const {
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
    return (JAUSoundNameTableGroup*)((u8*)mData + offset);
}

template <>
char* JAUSoundTable_<JAUSoundNameTableRoot, JAUSoundNameTableSection, JAUSoundNameTableGroup, char>::getItem(const JAUSoundNameTableGroup* group, int index) const {
    u32 offset = group->getItemOffset(index);
    if (offset == 0) {
        return nullptr;
    }
    return (char*)((u8*)mData + offset);
}

int JAUSoundNameTable::getNumGroups_inSection(u8 sectionID) const {
    JAUSoundNameTableSection* section = mTable.getSection(sectionID);
    if (section == nullptr) {
        return -1;
    }
    return section->mNumGroups;
}

int JAUSoundNameTable::getNumItems_inGroup(u8 sectionID, u8 groupID) const {
    JAUSoundNameTableSection* section = mTable.getSection(sectionID);
    if (section == nullptr) {
        return -1;
    }
    JAUSoundNameTableGroup* group = mTable.getGroup(section, groupID);
    if (group == nullptr) {
        return -1;
    }
    return group->mNumItems;
}

void JAUSoundNameTable::init(void const* pData) {
    if (pData != nullptr) {
        mTable.init(pData);
    } else {
        mTable.reset();
    }
}

const char* JAUSoundNameTable::getName(JAISoundID soundID) const {
    if (soundID.isAnonymous()) {
        return "<Anonymous>";
    }
    JAUSoundNameTableSection* section = mTable.getSection(soundID.getSectionID());
    if (section == nullptr) {
        return "";
    }
    JAUSoundNameTableGroup* group = mTable.getGroup(section, soundID.getGroupID());
    if (group == nullptr) {
        return "";
    }
    return mTable.getItem(group, soundID.getWaveID());
}
