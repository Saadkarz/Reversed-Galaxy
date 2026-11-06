#include "revolution.h"
#include "revolution/bte.h"
#include "revolution/os/OSInterrupt.h"
#include "revolution/wud.h"
#include <cstring>

#define DEBUGPrint(...) ((void)0)

// TODO(kiwi) Is this from BTA?
#define WUD_HH_CUSTOM_EVT 15

typedef struct WUD_HH_EVT15 {
    u16 status0;    // at 0x0
    u16 status1;    // at 0x2
    u16 linkedNum;  // at 0x4

    struct {
        UINT8 handle;      // at 0x0
        UINT16 queueSize;  // at 0x2
        UINT16 notAckNum;  // at 0x4
    } devices[];           // at 0x6
} WUD_HH_EVT15;

WUDDevInfo* WUDiGetDiscoverDevice(void);
void WUDiSetDevAddrForHandle(u8 handle, BD_ADDR_PTR addr);
BD_ADDR_PTR WUDiGetDevAddrForHandle(u8 handle);
void WUDiSetQueueSizeForHandle(u8 handle, u16 size);
void WUDiSetNotAckNumForHandle(u8 handle, u16 num);
BOOL WUDIsLinkedWBC(void);

void WUDiHidHostEventCallback(tBTA_HH_EVT event, tBTA_HH* pData) {
    WUDCB* p = &_wcb;
    WUDDevInfo* pInfo;
    WUD_HH_EVT15* pEvt15;
    int i;

    switch (event) {
    case BTA_HH_ENABLE_EVT: {
        p->hhFlags |= 1;
        break;
    }

    case BTA_HH_OPEN_EVT: {
        tBTA_HH_CONN* pConn = &pData->conn;

        if (pConn->status == BTA_HH_OK) {
            pInfo = WUDiGetDiscoverDevice();

            if (memcmp(pInfo->devAddr, pConn->bda, 6) != 0) {
                pInfo = WUDiGetDevInfo(pConn->bda);
            }

            switch (pInfo->status) {
            case 12:
                p->syncState = WUD_STATE_SYNC_REGISTER_DEVICE;
                break;
            case 2:
                p->syncState = WUD_STATE_SYNC_COMPLETE;
                break;
            }

            pInfo->status = 8;
            pInfo->devHandle = pConn->handle;
            p->connectedNum++;

            pInfo = WUDiGetDevInfo(pConn->bda);
            if (pInfo == NULL) {
                pInfo = WUDiGetDiscoverDevice();
            }

            WUDiSetDevAddrForHandle(pConn->handle, pInfo->devAddr);
            WUDiSetQueueSizeForHandle(pConn->handle, 0);
            WUDiSetNotAckNumForHandle(pConn->handle, 0);

            if (pInfo->sync_type == 3 || pInfo->sync_type == 1) {
                WUDiMoveTopSmpDevInfoPtr(pInfo);
            } else if (!WUDIsLinkedWBC() || (WUDIsLinkedWBC() && memcmp(pInfo, "Nintendo RVL-CNT", 16) == 0)) {
                WUDiMoveTopStdDevInfoPtr(pInfo);
            }

            WUDSetSniffMode(pInfo->devAddr, 8);

            if (p->hidConnCB != NULL) {
                p->hidConnCB(pInfo, TRUE);
            }
        } else if (p->syncState != 0) {
            pInfo = WUDiGetDiscoverDevice();

            if (memcmp(pConn->bda, pInfo->devAddr, 6) == 0 && pInfo->status == 2) {
                if (WUDiGetDevInfo(pConn->bda) && pConn->status == 12) {
                    WUDiRemoveDevice(pConn->bda);
                    p->linkedNum--;
                }

                p->syncState = 255;
            }
        } else if (WUDiGetDevInfo(pConn->bda) && pConn->status == 12) {
            WUDDevInfo* pDev = WUDiGetDevInfo(pConn->bda);

            if (pDev != NULL) {
                if (pDev->sync_type == 3 || pDev->sync_type == 1) {
                    WUDiMoveBottomSmpDevInfoPtr(pDev);
                } else {
                    WUDiMoveBottomStdDevInfoPtr(pDev);
                }
            }

            WUDiRemoveDevice(pConn->bda);
            p->linkedNum--;
        }
        break;
    }

    case BTA_HH_CLOSE_EVT: {
        tBTA_HH_CBDATA* pCbData = &pData->dev_status;

        p->connectedNum--;

        pInfo = WUDiGetDevInfo(WUDiGetDevAddrForHandle(pCbData->handle));
        if (pInfo != NULL) {
            if (pInfo->sync_type == 3 || pInfo->sync_type == 1) {
                WUDiMoveTopOfDisconnectedSmpDevice(pInfo);
            } else if (!WUDIsLinkedWBC() || (WUDIsLinkedWBC() && memcmp(pInfo, "Nintendo RVL-CNT", 16) == 0)) {
                WUDiMoveTopOfDisconnectedStdDevice(pInfo);
            }
        }

        WUDiSetDevAddrForHandle(pCbData->handle, NULL);
        WUDiSetQueueSizeForHandle(pCbData->handle, 0);
        WUDiSetNotAckNumForHandle(pCbData->handle, 0);

        if (p->hidConnCB != NULL) {
            p->hidConnCB(pInfo, FALSE);
        }
        break;
    }

    case BTA_HH_ADD_DEV_EVT: {
        tBTA_HH_CONN* pConn = &pData->dev_info;

        pInfo = WUDiGetDevInfo(pConn->bda);
        pInfo->devHandle = pConn->handle;
        WUDiSetDevAddrForHandle(pConn->handle, pInfo->devAddr);
        WUDiSetQueueSizeForHandle(pConn->handle, 0);
        WUDiSetNotAckNumForHandle(pConn->handle, 0);
        break;
    }

    case WUD_HH_CUSTOM_EVT: {
        pEvt15 = (WUD_HH_EVT15*)pData;

        p->bufferStatus0 = pEvt15->status0;
        p->bufferStatus1 = pEvt15->status1;

        if (p->linkedNum < pEvt15->linkedNum) {
            OSReport("WARNING: link num count is modified.\n");
            p->linkedNum = pEvt15->linkedNum;
        }

        for (i = 0; i < pEvt15->linkedNum; i++) {
            if (pEvt15->devices[i].handle < WUD_MAX_DEV_ENTRY) {
                WUDiSetQueueSizeForHandle(pEvt15->devices[i].handle, pEvt15->devices[i].queueSize);
                WUDiSetNotAckNumForHandle(pEvt15->devices[i].handle, pEvt15->devices[i].notAckNum);
            }
        }
        break;
    }
    }
}

void bta_hh_co_data(UINT8 handle, UINT8* pReport, UINT16 len, tBTA_HH_PROTO_MODE mode, UINT8 subClass, UINT8 appId) {
#pragma unused(mode)
#pragma unused(subClass)

    WUDCB* p = &_wcb;

    if (appId == 3) {
        if (p->hidRecvCB != NULL) {
            p->hidRecvCB(handle, pReport, len);
        }
    } else {
        DEBUGPrint("Invalid app_id [%d]\n", appId);
    }
}

void bta_hh_co_open(UINT8 handle, UINT8 subClass, UINT16 attrMask, UINT8 appId) {
#pragma unused(handle)
#pragma unused(subClass)
#pragma unused(attrMask)
#pragma unused(appId)

    DEBUGPrint("bta_hh_co_open()\n");
}

void bta_hh_co_close(UINT8 handle, UINT8 appId) {
#pragma unused(handle)
#pragma unused(appId)

    DEBUGPrint("bta_hh_co_close()\n");
}

BOOLEAN
bta_dm_co_get_compress_memory(tBTA_SYS_ID id, UINT8** ppMemory, UINT32* memorySize) {
#pragma unused(id)
#pragma unused(ppMemory)
#pragma unused(memorySize)

    return FALSE;
}
