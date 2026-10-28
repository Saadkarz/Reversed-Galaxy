#pragma once

#include <revolution/types.h>

enum JASOutputRate {
    OUTPUT_RATE_0,
};

enum JASMixMode {
    MIX_MODE_MONO,
    MIX_MODE_MONO_WIDE,
    MIX_MODE_EXTRA,
    MIX_MODE_INTERLEAVE,
};

namespace JASDriver {
    typedef s16* (*MixCallback)(s32);
    typedef void (*MixFunc)(s16*, u32, MixCallback);
    typedef void (*DSPBufCallback)(s16*, u32);

    void initAI(void (*)(void));
    void startDMA();
    void stopDMA();
    void setOutputRate(JASOutputRate);
    void updateDac();
    void updateDSP();
    void readDspBuffer(s16*, u32);
    void finishDSPFrame();
    inline void registerMixCallback(MixCallback, JASMixMode);
    inline void registDSPBufCallback(DSPBufCallback);
    f32 getDacRate();
    u32 getSubFrames();
    inline u32 getDacSize();
    inline u32 getFrameSamples();
    void mixMonoTrack(s16*, u32, MixCallback);
    void mixMonoTrackWide(s16*, u32, MixCallback);
    void mixExtraTrack(s16*, u32, MixCallback);
    void mixInterleaveTrack(s16*, u32, MixCallback);
    u32 getSubFrameCounter();
    void subframeCallback();
    void DSPSyncCallback();

    extern const MixFunc sMixFuncs[4];
    extern s16* sDmaDacBuffer[3];
    extern JASMixMode sMixMode;
    extern f32 sDacRate;
    extern u32 sSubFrames;
    extern s16** sDspDacBuffer;
    extern s32 sDspDacWriteBuffer;
    extern s32 sDspDacReadBuffer;
    extern s32 sDspStatus;
    extern DSPBufCallback sDspDacCallback;
    extern s16* lastRspMadep;
    extern void (*dacCallbackFunc)(s16*, u32);
    extern MixCallback extMixCallback;
    extern u32 sOutputRate;
    extern volatile u32 sSubFrameCounter;

    inline void registerMixCallback(MixCallback param_0, JASMixMode param_1) {
        extMixCallback = param_0;
        sMixMode = param_1;
    }
    inline void registDSPBufCallback(DSPBufCallback cb) {
        sDspDacCallback = cb;
    }
    inline u32 getDacSize() {
        return sSubFrames * 0x50 * 2;
    }
    inline u32 getFrameSamples() {
        return sSubFrames * 0x50;
    }
};  // namespace JASDriver
