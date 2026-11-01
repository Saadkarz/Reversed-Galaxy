#pragma once

#include "JSystem/JSupport/JSURandomInputStream.hpp"

class JKRFile;

class JSUFileInputStream : public JSURandomInputStream {
public:
    JSUFileInputStream(JKRFile*);

    virtual u32 readData(void*, s32);
    virtual s32 seekPos(s32, JSUStreamSeekFrom);
    virtual ~JSUFileInputStream();
    virtual s32 getLength() const;
    virtual s32 getPosition() const;

private:
    /* 0x08 */ JKRFile* mFile;
    /* 0x0C */ s32 mPosition;
};  // Size = 0x10
