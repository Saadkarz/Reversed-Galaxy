#pragma once

#include "Game/Screen/LayoutActor.hpp"

namespace nw4r {
    namespace lyt {
        class TexMap;
    }
}

class ErrorMessageWindow : public LayoutActor {
public:
    enum MessageType {
        MessageType_System,
        MessageType_Game
    };

    ErrorMessageWindow();
    virtual ~ErrorMessageWindow();

    virtual void init(const JMapInfoIter& rIter);
    virtual void appear();

    bool isAnimEnd() const;
    void appearWithMessage(const char*, MessageType, const nw4r::lyt::TexMap*);
    void disappear();

private:
    /* 0x20 */ MessageType mMessageType;
    /* 0x24 */ const char* mMessageId;
    /* 0x28 */ const nw4r::lyt::TexMap* mTexture;
    /* 0x2C */ u32 _2C;
};
