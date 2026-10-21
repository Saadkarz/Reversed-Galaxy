#pragma once

#include "Game/Util/Array.hpp"
#include <revolution/types.h>

class CreateResourceHolderArgs;
class JKRHeap;
class LayoutHolder;
class ResourceHolder;
class ResourceHolderManager;

typedef bool (*MakeArchiveFileNameFuncPtr)(char*, u32, const char*);
typedef void (*FuncPtrB)(const char*, CreateResourceHolderArgs*);
typedef void (ResourceHolderManager::*FuncPtrC)(const char*, CreateResourceHolderArgs*);

class CreateResourceHolderArgs {
public:
    CreateResourceHolderArgs();

    /* 0x0 */ ResourceHolder* mResourceHolder;
    /* 0x4 */ LayoutHolder* mLayoutHolder;
    /* 0x8 */ JKRHeap* mHeap;
};

class ResourceHolderManagerName2Resource {
public:
    ResourceHolderManagerName2Resource();

    inline ResourceHolderManagerName2Resource& operator=(const ResourceHolderManagerName2Resource& other) {
        mResourceHolder = other.mResourceHolder;
        mLayoutHolder = other.mLayoutHolder;
        mHash = other.mHash;
        mHeap = other.mHeap;
        return *this;
    }

    /* 0x0 */ ResourceHolder* mResourceHolder;
    /* 0x4 */ LayoutHolder* mLayoutHolder;
    /* 0x8 */ u32 mHash;
    /* 0xC */ JKRHeap* mHeap;
};

class ResourceHolderManager {
public:
    ResourceHolderManager();

    ResourceHolder* createAndAdd(const char*, JKRHeap*);
    ResourceHolder* createAndAddStationed(const char*);
    ResourceHolder* createAndAdd(const char*);
    LayoutHolder* createAndAddLayoutHolder(const char*, JKRHeap*);
    LayoutHolder* createAndAddLayoutHolderStationed(const char*);
    LayoutHolder* createAndAddLayoutHolderRawData(const char*);
    void removeIfIsEqualHeap(JKRHeap*);
    void restoreInitMaterialDataAll();
    static void startCreateResourceHolderOnMainThread(const char*, CreateResourceHolderArgs*);
    static void startCreateLayoutHolderOnMainThread(const char*, CreateResourceHolderArgs*);

private:
    ResourceHolderManagerName2Resource* createAndAddInner(const char*, MakeArchiveFileNameFuncPtr, FuncPtrB);
    ResourceHolderManagerName2Resource* createAndAddInnerStationed(const char*, FuncPtrC) NO_INLINE;
    void createResourceHolder(const char*, CreateResourceHolderArgs*);
    void createLayoutHolder(const char*, CreateResourceHolderArgs*);
    ResourceHolderManagerName2Resource* add(const char*, const CreateResourceHolderArgs&);
    ResourceHolderManagerName2Resource* find(const char*);

private:
    /* 0x0 */ MR::Vector< MR::FixedArray< ResourceHolderManagerName2Resource, 512 > > mResourceArray;
};
