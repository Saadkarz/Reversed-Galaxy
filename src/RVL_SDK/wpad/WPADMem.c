#include "revolution/types.h"

typedef void (*WPADCallback)(s32 chan, s32 result);

typedef struct WPADControlBlock {
    u8 pad_000[0x160];
    u8 cmdq[1];
    u8 pad_161[0x900 - 0x161];
    s32 status;
    u8 pad_904[0x920 - 0x904];
    s32 setup;
    u8 pad_924[0xb8c - 0x924];
    u32 mem_used;
    u32 mem_buf;
    u16 mem_len;
    u16 mem_pad;
    u32 mem_addr;
    WPADCallback mem_cb;
} WPADControlBlock;

extern WPADControlBlock* lbl_80791C10[];

BOOL OSDisableInterrupts(void);
BOOL OSRestoreInterrupts(BOOL);
BOOL WPADiSendWriteData(void* queue, void* p_buf, u16 len, u32 addr, WPADCallback callback);

void fn_805F8530(s32 chan) {
    WPADControlBlock* p_wpd = lbl_80791C10[chan];
    p_wpd->mem_used = 0;
    p_wpd->mem_buf = 0;
    p_wpd->mem_len = 0;
    p_wpd->mem_addr = 0;
    p_wpd->mem_cb = 0;
}

s32 fn_805F8560(s32 chan, void* p_buf, u16 len, u32 addr_hi, u16 addr_lo, WPADCallback callback) {
    WPADControlBlock* p_wpd = lbl_80791C10[chan];
    BOOL enable;
    s32 status;
    s32 setup;
    s32 result;
    u32 addr;

    enable = OSDisableInterrupts();
    status = p_wpd->status;
    setup = p_wpd->setup;
    OSRestoreInterrupts(enable);

    result = status;
    if (result != -1) {
        if (!setup) {
            result = -2;
        } else {
            addr = (addr_hi & 0xFF) << 16;
            addr |= addr_lo;
            addr |= 0x04000000;
            result = WPADiSendWriteData(&p_wpd->cmdq, p_buf, len, addr, callback) ? 0 : -2;
        }
    }

    if (result != 0 && callback != 0) {
        callback(chan, result);
    }

    return result;
}
