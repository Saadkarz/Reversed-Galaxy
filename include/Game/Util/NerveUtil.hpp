#pragma once

#include <revolution/types.h>

class Nerve;
class NerveExecutor;

namespace MR {
    bool isStep(const NerveExecutor* pExecutor, s32 step);
    bool isFirstStep(const NerveExecutor* pExecutor);
    bool isLessStep(const NerveExecutor* pExecutor, s32 step);
    bool isLessEqualStep(const NerveExecutor* pExecutor, s32 step);
    bool isGreaterStep(const NerveExecutor* pExecutor, s32 step);
    bool isGreaterEqualStep(const NerveExecutor* pExecutor, s32 step);
    bool isIntervalStep(const NerveExecutor* pExecutor, s32 step);
    bool isNewNerve(const NerveExecutor* pExecutor);

    f32 calcNerveRate(const NerveExecutor* pExecutor, s32 stepMax);
    f32 calcNerveRate(const NerveExecutor* pExecutor, s32 stepMin, s32 stepMax);
    f32 calcNerveEaseInRate(const NerveExecutor* pExecutor, s32 stepMax);
    f32 calcNerveEaseOutRate(const NerveExecutor* pExecutor, s32 stepMax);
    f32 calcNerveEaseInOutRate(const NerveExecutor* pExecutor, s32 stepMax);
    f32 calcNerveValue(const NerveExecutor* pExecutor, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveEaseInValue(const NerveExecutor* pExecutor, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveEaseOutValue(const NerveExecutor* pExecutor, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveEaseOutValue(const NerveExecutor* pExecutor, s32 stepMin, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveEaseInOutValue(const NerveExecutor* pExecutor, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveEaseInOutValue(const NerveExecutor* pExecutor, s32 stepMin, s32 stepMax, f32 valueStart, f32 valueEnd);
    f32 calcNerveParabolaValue(const NerveExecutor* pExecutor, s32 stepMax);

    void setNerveAtStep(NerveExecutor* pExecutor, const Nerve* pNerve, s32 step);
};  // namespace MR

extern "C" f32 fn_800483E0(const NerveExecutor* pExecutor, s32 a, s32 b, s32 c);
extern "C" f32 fn_80048480(const NerveExecutor* pExecutor, s32 stepMax, f32 valStart, f32 valEnd);
