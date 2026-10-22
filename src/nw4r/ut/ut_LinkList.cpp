#include "revolution/types.h"
#include "nw4r/ut/LinkList.h"

namespace nw4r {
    namespace ut {
        namespace detail {

            LinkListImpl::~LinkListImpl() {
                Clear();
            }

            LinkListImpl::Iterator LinkListImpl::Erase(Iterator it) {
                Iterator itNext = it;
                (void)++itNext;
                return Erase(it, itNext);
            }

            LinkListImpl::Iterator LinkListImpl::Insert(Iterator it, pointer p) {
                Node* const pIt = it.mPointer;
                Node* const pItPrev = pIt->mPrev;
                p->mNext = pIt;
                p->mPrev = pItPrev;

                pIt->mPrev = p;
                pItPrev->mNext = p;

                ++mSize;
                return Iterator(p);
            }

            LinkListImpl::Iterator LinkListImpl::Erase(pointer p) {
                Node* const pNext = p->mNext;
                Node* const pPrev = p->mPrev;
                pNext->mPrev = pPrev;
                pPrev->mNext = pNext;
                --mSize;

                p->mNext = nullptr;
                p->mPrev = nullptr;

                return Iterator(pNext);
            }
        };  // namespace detail
    };  // namespace ut
};  // namespace nw4r
