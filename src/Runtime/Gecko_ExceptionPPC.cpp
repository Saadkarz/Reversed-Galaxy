#include <NMWException.h>

#pragma opt_strength_reduction off
#pragma exceptions on

typedef struct ProcessInfo {
	__eti_init_info* exception_info;
	char* TOC;
	int active;
} ProcessInfo;

static ProcessInfo fragmentinfo[32];


#pragma schedule once
int __register_fragment(struct __eti_init_info *info, char *TOC) {
	ProcessInfo* f = fragmentinfo;
	int i;

	for(i = 0; i < 0x20; ++i, ++f) if (f->active == 0)
	{
		f->exception_info = info;
		f->TOC = TOC;
		f->active = 1;
		return i;
	}

	return -1;
}
#pragma schedule on
void __unregister_fragment(int id) {
    if (id <= 0x1Fu) {
        ProcessInfo* info = &fragmentinfo[id];
        info->exception_info = 0;
        info->TOC = 0;
        info->active = 0;
    }
}
