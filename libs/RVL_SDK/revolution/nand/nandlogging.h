#ifndef NANDLOGGING_H
#define NANDLOGGING_H

#include "revolution/os.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*NANDLoggingCallback)(BOOL, s32);

BOOL NANDLoggingAddMessageAsync(NANDLoggingCallback, s32, const char *, ...);

#ifdef __cplusplus
}
#endif

#endif // NANDLOGGING_H