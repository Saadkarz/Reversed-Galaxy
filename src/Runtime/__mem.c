#include <__mem.h>

#pragma ANSI_strict off

#ifdef __MWERKS__
asm void* memcpy(void *pDest, const void *pSrc, size_t len) {
    nofralloc
    cmplwi cr1, r5, 0
    beqlr cr1
    cmplw cr1, r4, r3
    blt cr1, lbl_178
    beqlr cr1
    li r6, 0x80
    cmplw cr5, r5, r6
    blt cr5, lbl_c0
    clrlwi r9, r4, 29
    clrlwi r10, r3, 29
    subf r8, r10, r3
    dcbt 0, r4
    xor. r11, r10, r9
    bne lbl_15c
    andi. r10, r10, 7
    beq+ lbl_68
    li r6, 8
    subf r9, r9, r6
    addi r8, r3, 0
    mtctr r9
    subf r5, r9, r5
lbl_54:
    lbz r9, 0(r4)
    addi r4, r4, 1
    stb r9, 0(r8)
    addi r8, r8, 1
    bdnz lbl_54
lbl_68:
    srwi r6, r5, 5
    mtctr r6
lbl_70:
    lfd f1, 0(r4)
    lfd f2, 8(r4)
    lfd f3, 16(r4)
    lfd f4, 24(r4)
    addi r4, r4, 32
    stfd f1, 0(r8)
    stfd f2, 8(r8)
    stfd f3, 16(r8)
    stfd f4, 24(r8)
    addi r8, r8, 32
    bdnz lbl_70
    andi. r6, r5, 31
    beqlr
    subi r4, r4, 1
    mtctr r6
    subi r8, r8, 1
lbl_b0:
    lbzu r9, 1(r4)
    stbu r9, 1(r8)
    bdnz lbl_b0
    blr
lbl_c0:
    li r6, 20
    cmplw cr5, r5, r6
    ble cr5, lbl_15c
    clrlwi r9, r4, 30
    clrlwi r10, r3, 30
    xor. r11, r10, r9
    bne lbl_15c
    li r6, 4
    subf r9, r9, r6
    addi r8, r3, 0
    subf r5, r9, r5
    mtctr r9
lbl_f0:
    lbz r9, 0(r4)
    addi r4, r4, 1
    stb r9, 0(r8)
    addi r8, r8, 1
    bdnz lbl_f0
    srwi r6, r5, 4
    mtctr r6
lbl_10c:
    lwz r9, 0(r4)
    lwz r10, 4(r4)
    lwz r11, 8(r4)
    lwz r12, 12(r4)
    addi r4, r4, 16
    stw r9, 0(r8)
    stw r10, 4(r8)
    stw r11, 8(r8)
    stw r12, 12(r8)
    addi r8, r8, 16
    bdnz lbl_10c
    andi. r6, r5, 15
    beqlr
    subi r4, r4, 1
    mtctr r6
    subi r8, r8, 1
lbl_14c:
    lbzu r9, 1(r4)
    stbu r9, 1(r8)
    bdnz lbl_14c
    blr
lbl_15c:
    subi r7, r4, 1
    subi r8, r3, 1
    mtctr r5
lbl_168:
    lbzu r9, 1(r7)
    stbu r9, 1(r8)
    bdnz lbl_168
    blr
lbl_178:
    add r4, r4, r5
    add r12, r3, r5
    li r6, 0x80
    cmplw cr5, r5, r6
    blt cr5, lbl_204
    clrlwi r9, r4, 29
    clrlwi r10, r12, 29
    xor. r11, r10, r9
    bne lbl_288
    andi. r10, r10, 7
    beq+ lbl_1b4
    mtctr r10
lbl_1a8:
    lbzu r9, -1(r4)
    stbu r9, -1(r12)
    bdnz lbl_1a8
lbl_1b4:
    subf r5, r10, r5
    srwi r6, r5, 5
    mtctr r6
lbl_1c0:
    lfd f1, -8(r4)
    lfd f2, -16(r4)
    lfd f3, -24(r4)
    lfd f4, -32(r4)
    subi r4, r4, 32
    stfd f1, -8(r12)
    stfd f2, -16(r12)
    stfd f3, -24(r12)
    stfdu f4, -32(r12)
    bdnz lbl_1c0
    andi. r6, r5, 31
    beqlr
    mtctr r6
lbl_1f4:
    lbzu r9, -1(r4)
    stbu r9, -1(r12)
    bdnz lbl_1f4
    blr
lbl_204:
    li r6, 20
    cmplw cr5, r5, r6
    ble cr5, lbl_288
    clrlwi r9, r4, 30
    clrlwi r10, r12, 30
    xor. r11, r10, r9
    bne lbl_288
    andi. r10, r10, 7
    beq+ lbl_238
    mtctr r10
lbl_22c:
    lbzu r9, -1(r4)
    stbu r9, -1(r12)
    bdnz lbl_22c
lbl_238:
    subf r5, r10, r5
    srwi r6, r5, 4
    mtctr r6
lbl_244:
    lwz r9, -4(r4)
    lwz r10, -8(r4)
    lwz r11, -12(r4)
    lwz r8, -16(r4)
    subi r4, r4, 16
    stw r9, -4(r12)
    stw r10, -8(r12)
    stw r11, -12(r12)
    stwu r8, -16(r12)
    bdnz lbl_244
    andi. r6, r5, 15
    beqlr
    mtctr r6
lbl_278:
    lbzu r9, -1(r4)
    stbu r9, -1(r12)
    bdnz lbl_278
    blr
lbl_288:
    mtctr r5
lbl_28c:
    lbzu r9, -1(r4)
    stbu r9, -1(r12)
    bdnz lbl_28c
    blr
}
#endif

void __fill_mem(void *pDest, int val, unsigned long n) {
	unsigned long v = (unsigned char) val;
	unsigned long i;

	((unsigned char*)pDest) = ((unsigned char*)pDest) - 1;

	if (n >= 32) {
		i = (~(unsigned long)pDest) & 3;

		if (i) {
			n -= i;

			do {
				*++(((unsigned char*)pDest)) = v;
			}
			while (--i);
		}

		if (v != 0) {
			v |= v << 24 | v << 16 | v <<  8;
		}

		((unsigned long*)pDest) = ((unsigned long*) (((unsigned char*)pDest) + 1)) - 1;
		i = n >> 5;

		if (i != 0) {
			do {
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
				*++(((unsigned long*)pDest)) = v;
			}
			while (--i);
		}

		i = (n & 31) >> 2;

		if (i) {
			do {
				*++(((unsigned long*)pDest)) = v;
			}	
			while (--i);
		}

		((unsigned char*)pDest) = ((unsigned char*) (((unsigned long*)pDest) + 1)) - 1;
		n &= 3;
	}

	if (n) {
		do {
			*++(((unsigned char*)pDest)) = v;
		}
		while (--n);
	}
}

void* memset(void *pDest, int val, size_t num) {
    __fill_mem(pDest, val, num);
    return pDest;
}
