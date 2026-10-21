#pragma once

#include <revolution.h>

class LayoutActor;

namespace nw4r {
    namespace lyt {
        class TexMap;
    }
}

namespace MR {
    nw4r::lyt::TexMap* createLytTexMap(const char*, const char*);
    bool isDead(const LayoutActor*);
}
