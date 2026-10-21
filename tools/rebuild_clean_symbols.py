import subprocess
import re

# 1. Start from HEAD:symbols.txt
head_syms = subprocess.check_output(['git', 'show', 'HEAD:config/SB4E01/symbols.txt'], text=True)

# 2. Targeted replacements
replacements = {
    # LiveActorGroup & ClippingJudge vtable size
    '__vt__14LiveActorGroup = .data:0x80695348; // type:object size:0x30':
    '__vt__14LiveActorGroup = .data:0x80695348; // type:object size:0x2C',
    '__vt__13ClippingJudge = .data:0x80694EC8; // type:object size:0x30':
    '__vt__13ClippingJudge = .data:0x80694EC8; // type:object size:0x2C',

    # sdata2 float sizes
    'lbl_807DC550 = .sdata2:0x807DC550; // type:object size:0x8 align:4 data:float':
    'lbl_807DC550 = .sdata2:0x807DC550; // type:object size:0x4 align:4 data:float',
    'lbl_807DC568 = .sdata2:0x807DC568; // type:object size:0x8 align:4 data:float':
    'lbl_807DC568 = .sdata2:0x807DC568; // type:object size:0x4 align:4 data:float',
    'lbl_807DC588 = .sdata2:0x807DC588; // type:object size:0x8 align:4 data:float':
    'lbl_807DC588 = .sdata2:0x807DC588; // type:object size:0x4 align:4 data:float',

    # LiveActorGroup weak destructor
    '__dt__14LiveActorGroupFv = .text:0x8008AD40; // type:function size:0x58':
    '__dt__14LiveActorGroupFv = .text:0x8008AD40; // type:function size:0x58 scope:weak',

    # JGeometry weak inlines
    'mult__Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>CFRCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f> = .text:0x80006F00; // type:function size:0x90':
    'mult__Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>CFRCQ29JGeometry8TVec3<f>RQ29JGeometry8TVec3<f> = .text:0x80006F00; // type:function size:0x90 scope:weak',
    'set<f>__Q29JGeometry8TVec3<f>Ffff_v = .text:0x80006F90; // type:function size:0x10':
    'set<f>__Q29JGeometry8TVec3<f>Ffff_v = .text:0x80006F90; // type:function size:0x10 scope:weak',
    'concat__Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>FRCQ29JGeometry13SMatrix34C<f>RCQ29JGeometry13SMatrix34C<f> = .text:0x80007380; // type:function size:0x2AC':
    'concat__Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>FRCQ29JGeometry13SMatrix34C<f>RCQ29JGeometry13SMatrix34C<f> = .text:0x80007380; // type:function size:0x2AC scope:weak',
    'set__Q29JGeometry13SMatrix34C<f>Fffffffffffff = .text:0x80007630; // type:function size:0x44':
    'set__Q29JGeometry13SMatrix34C<f>Fffffffffffff = .text:0x80007630; // type:function size:0x44 scope:weak',
    'dot__Q29JGeometry8TVec3<f>CFRCQ29JGeometry8TVec3<f> = .text:0x8000D750; // type:function size:0x20':
    'dot__Q29JGeometry8TVec3<f>CFRCQ29JGeometry8TVec3<f> = .text:0x8000D750; // type:function size:0x20 scope:weak',
    'getTrans__Q29JGeometry64TPosition3<Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>>CFRQ29JGeometry8TVec3<f> = .text:0x80026A80; // type:function size:0x18':
    'getTrans__Q29JGeometry64TPosition3<Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>>CFRQ29JGeometry8TVec3<f> = .text:0x80026A80; // type:function size:0x18 scope:weak',
    'set__Q29JGeometry14TPartition3<f>FRCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f> = .text:0x80026AA0; // type:function size:0x90':
    'set__Q29JGeometry14TPartition3<f>FRCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f> = .text:0x80026AA0; // type:function size:0x90 scope:weak',
    'sub__Q29JGeometry8TVec3<f>FRCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f> = .text:0x80026B30; // type:function size:0x24':
    'sub__Q29JGeometry8TVec3<f>FRCQ29JGeometry8TVec3<f>RCQ29JGeometry8TVec3<f> = .text:0x80026B30; // type:function size:0x24 scope:weak',
    'setTrans__Q29JGeometry64TPosition3<Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>>FRCQ29JGeometry8TVec3<f> = .text:0x80044FB0; // type:function size:0x1C':
    'setTrans__Q29JGeometry64TPosition3<Q29JGeometry38TMatrix34<Q29JGeometry13SMatrix34C<f>>>FRCQ29JGeometry8TVec3<f> = .text:0x80044FB0; // type:function size:0x1C scope:weak',

    # DelegateHeap
    'fn_8001F0C0 = .text:0x8001F0C0; // type:function size:0x74':
    '__ct__12DelegateHeapFP7JKRHeap = .text:0x8001F0C0; // type:function size:0x74 scope:weak',
    'fn_8001F140 = .text:0x8001F140; // type:function size:0x58':
    '__dt__12DelegateHeapFv = .text:0x8001F140; // type:function size:0x58 scope:weak',

    # JAudio2 DRAM / ARAM Base
    'lbl_807D6458 = .sbss:0x807D6458; // type:object size:0x4 data:4byte':
    'JASDram = .sbss:0x807D6458; // type:object size:0x4 data:4byte',
    'lbl_807D645C = .sbss:0x807D645C; // type:object size:0x4 data:4byte':
    'sAramBase__9JASKernel = .sbss:0x807D645C; // type:object size:0x4 data:4byte',

    # KPAD Set Param functions
    'KPADGetHoriParam = .text:0x80547FB0; // type:function size:0x1C':
    'KPADSetHoriParam = .text:0x80547FB0; // type:function size:0x1C',
    'KPADGetDistParam = .text:0x80547FD0; // type:function size:0x1C':
    'KPADSetDistParam = .text:0x80547FD0; // type:function size:0x1C',
    'KPADGetAccParam = .text:0x80547FF0; // type:function size:0x1C':
    'KPADSetAccParam = .text:0x80547FF0; // type:function size:0x1C',

    # BTE global control blocks
    'lbl_807C4150 = .bss:0x807C4150; // type:object size:0x88 data:4byte':
    'btu_cb = .bss:0x807C4150; // type:object size:0x88 data:4byte',
    'lbl_807C41D8 = .bss:0x807C41D8; // type:object size:0x90 data:4byte':
    'bta_sys_cb = .bss:0x807C41D8; // type:object size:0x90 data:4byte',
    'lbl_807C4678 = .bss:0x807C4678; // type:object size:0x27C8':
    'btm_cb = .bss:0x807C4678; // type:object size:0x27C8',
    'lbl_807C7740 = .bss:0x807C7740; // type:object size:0x7E8 data:byte':
    'l2cb = .bss:0x807C7740; // type:object size:0x7E8 data:byte',
    'lbl_807C8340 = .bss:0x807C8340; // type:object size:0x4638':
    'sdp_cb = .bss:0x807C8340; // type:object size:0x4638',

    # VF functions & data
    'fn_8056A320 = .text:0x8056A320; // type:function size:0x1C':
    'VFipdm_part_set_driver_error_code = .text:0x8056A320; // type:function size:0x1C',
    'fn_8057C6A0 = .text:0x8057C6A0; // type:function size:0x54':
    'VFiPFVOL_GetVolumeFromDrvChar = .text:0x8057C6A0; // type:function size:0x54',
    'fn_8057CA00 = .text:0x8057CA00; // type:function size:0x5F4':
    'VFiPFVOL_attach = .text:0x8057CA00; // type:function size:0x5F4',
    'fn_8057D000 = .text:0x8057D000; // type:function size:0x11C':
    'VFiPFVOL_detach = .text:0x8057D000; // type:function size:0x11C',
    'fn_8057D120 = .text:0x8057D120; // type:function size:0x1F0':
    'VFiPFVOL_unmount = .text:0x8057D120; // type:function size:0x1F0',
    'lbl_807527A0 = .bss:0x807527A0; // type:object size:0xBD0 data:2byte':
    'VFipdm_disk_set = .bss:0x807527A0; // type:object size:0xBD0 data:2byte',
    'lbl_80753370 = .bss:0x80753370; // type:object size:0xD154 data:4byte':
    'VFipf_vol_set = .bss:0x80753370; // type:object size:0xD154 data:4byte',
}

cur_syms = head_syms
applied = 0
for target, replacement in replacements.items():
    if target in cur_syms:
        cur_syms = cur_syms.replace(target, replacement, 1)
        applied += 1
    else:
        print(f"Warning: target not found:\n  {target[:50]}...")

print(f"Applied {applied}/{len(replacements)} targeted symbol replacements.")
with open('config/SB4E01/symbols.txt', 'w', encoding='utf-8') as f:
    f.write(cur_syms)

print("Clean symbols.txt written.")
