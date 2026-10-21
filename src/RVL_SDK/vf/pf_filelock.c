#include "revolution/vf/pf_filelock.h"

PF_SYSTEM_SET VFipf_sys_set;

void VFiPF_InitLockFile() {
    VFipf_sys_set.flock_count = 0;
}

long VFiPF_UnLockFile(PF_FILE* p_file) {
    return -1;
}
