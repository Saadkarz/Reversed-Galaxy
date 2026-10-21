#pragma once

#include <revolution/types.h>

namespace nw4r {
    namespace ut {
        class Font;
        class ResFont;
    };  // namespace ut
};  // namespace nw4r

class JKRArchive;
class JKRHeap;
class JKRMemArchive;

namespace MR {
    void getMountedArchiveAndHeap(const char* pFilePath, JKRArchive** ppArchive, JKRHeap** ppHeap);
    void* decompressFileFromArchive(JKRArchive* pArchive, const char* pFilePath, JKRHeap* pHeap, int align);
}

class GameSystemFontHolder {
public:
    GameSystemFontHolder();

    nw4r::ut::Font* getMessageFont() const;
    void createFontFromEmbeddedData();
    void createFontFromFile();

    /* 0x00 */ u8* _0;
    /* 0x04 */ JKRMemArchive* _4;
    /* 0x08 */ nw4r::ut::ResFont* mEmbeddedMessageFont;
    /* 0x0C */ nw4r::ut::ResFont* mMessageFont;
    /* 0x10 */ nw4r::ut::ResFont* mPictureFont;
    /* 0x14 */ nw4r::ut::ResFont* mMenuFont;
    /* 0x18 */ nw4r::ut::ResFont* mNumberFont;
    /* 0x1C */ nw4r::ut::ResFont* mMenuFont96;
    /* 0x20 */ nw4r::ut::ResFont* mStaffFont18;
};
