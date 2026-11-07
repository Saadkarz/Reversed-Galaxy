#!/usr/bin/env python3
"""dol2cpp: static PowerPC (Broadway) -> C++ lifter for Galaxy2Coop.

Reads the user's own SMG2 (SB4E01) main.dol plus the decomp's symbol map and emits
C++ shards with one native function per guest function, a prototype header, and a
registration unit that binds every guest address to its native implementation.

The output is derived from the user's game executable: it is a build artifact and
must never be committed or redistributed.

Usage:
  dol2cpp.py --dol main.dol --symbols symbols.txt --splits splits.txt --out DIR [--units MSL_C,Runtime|ALL] [--shards N]
  dol2cpp.py --selftest
"""

import argparse
import collections
import os
import re
import struct
import sys

# ----------------------------------------------------------------------------- input


class Dol:
    def __init__(self, data):
        self.data = data
        self.sections = []
        for i in range(18):
            off = struct.unpack_from('>I', data, 0x00 + i * 4)[0]
            addr = struct.unpack_from('>I', data, 0x48 + i * 4)[0]
            size = struct.unpack_from('>I', data, 0x90 + i * 4)[0]
            if size:
                self.sections.append((addr, size, off, i < 7))

    def word(self, addr):
        for a, size, off, _ in self.sections:
            if a <= addr < a + size:
                return struct.unpack_from('>I', self.data, off + addr - a)[0]
        raise KeyError('address 0x%08X not in DOL' % addr)


SYM_RE = re.compile(r'^("?)(.+?)\1 = (\.init|\.text):0x([0-9A-Fa-f]+); // type:function size:0x([0-9A-Fa-f]+)')


def load_functions(path):
    funcs = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = SYM_RE.match(line)
        if not m:
            continue
        addr, size = int(m.group(4), 16), int(m.group(5), 16)
        if size == 0 or addr & 3:
            continue
        funcs[addr] = (m.group(2), size, m.group(3))
    return funcs


def load_unit_ranges(path, prefixes):
    ranges = []
    unit = None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^(\S.*):\s*$', line)
        if m:
            unit = m.group(1)
            continue
        m = re.match(r'^\s+\.(text|init)\s+start:0x([0-9A-Fa-f]+) end:0x([0-9A-Fa-f]+)', line)
        if m and unit and any(unit.startswith(p + '/') for p in prefixes):
            ranges.append((int(m.group(2), 16), int(m.group(3), 16)))
    return ranges


# ----------------------------------------------------------------------------- decoding helpers


def sx16(v):
    return v - 0x10000 if v & 0x8000 else v


def mask32(mb, me):
    m = 0
    i = mb
    while True:
        m |= 1 << (31 - i)
        if i == me:
            break
        i = (i + 1) & 31
    return m


def ea_d(ra, d):
    base = '0u' if ra == 0 else 'c.gpr[%d]' % ra
    return '%s + 0x%Xu' % (base, d & 0xFFFFFFFF) if d else base


def ea_x(ra, rb):
    return ('c.gpr[%d]' % rb) if ra == 0 else 'c.gpr[%d] + c.gpr[%d]' % (ra, rb)


def rc0(rc, reg):
    return ' c.recordCr0(%s);' % reg if rc else ''


def bc_cond(bo, bi):
    parts = []
    pre = ''
    if not (bo & 4):
        pre = 'c.ctr--; '
        parts.append('c.ctr == 0' if (bo & 2) else 'c.ctr != 0')
    if not (bo & 16):
        parts.append('c.crBit(%d) == %d' % (bi, (bo >> 3) & 1))
    return pre, (' && '.join(parts) if parts else 'true')


# ----------------------------------------------------------------------------- lifter


class Lifter:
    def __init__(self, funcs, lifted):
        self.funcs = funcs        # addr -> (name, size, section) for every known function
        self.lifted = lifted      # addrs being emitted
        self.unimpl = collections.Counter()
        self.ninsn = 0

    def call(self, target):
        if target in self.lifted:
            return 'f_%08X(c);' % target
        return 'call_indirect(c, 0x%08Xu);' % target

    def lift_function(self, dol, start, size):
        end = start + size
        words = [(a, dol.word(a)) for a in range(start, end, 4)]
        has_bctr = any((w >> 26) == 19 and ((w >> 1) & 0x3FF) == 528 and not (w & 1) for _, w in words)
        labels = set()
        body = []
        for a, w in words:
            code = self.insn(a, w, start, end, labels)
            body.append((a, w, code))
        if has_bctr:
            labels.update(a for a, _ in words)
        lines = []
        for a, w, code in body:
            if a in labels:
                lines.append('L_%08X:' % a)
            lines.append('    %s  // %08X: %08X' % (code, a, w))
        lines.append('    return;')
        return lines

    def unimp(self, a, w, key):
        self.unimpl[key] += 1
        return 'unimplemented(c, 0x%08Xu, 0x%08Xu);' % (a, w)

    def branch_to(self, a, target, lk, start, end, labels):
        inside = start <= target < end
        if lk:
            if inside:
                labels.add(target)
                return 'c.lr = 0x%08Xu; goto L_%08X;' % (a + 4, target)
            return 'c.lr = 0x%08Xu; %s' % (a + 4, self.call(target))
        if inside:
            labels.add(target)
            return 'goto L_%08X;' % target
        return '%s return;' % self.call(target)

    def insn(self, a, w, start, end, labels):
        self.ninsn += 1
        op = w >> 26
        d = (w >> 21) & 31
        ra = (w >> 16) & 31
        rb = (w >> 11) & 31
        rc = (w >> 6) & 31
        imm = w & 0xFFFF
        simm = sx16(imm)
        R = 'c.gpr[%d]'
        F = 'c.fpr[%d]'

        if w == 0x60000000:
            return ';  // nop'

        # ---------------- branches
        if op == 18:
            li = w & 0x03FFFFFC
            if li & 0x02000000:
                li -= 0x04000000
            target = (li if (w & 2) else a + li) & 0xFFFFFFFF
            return self.branch_to(a, target, w & 1, start, end, labels)
        if op == 16:
            bo, bi = d, ra
            bd = w & 0xFFFC
            if bd & 0x8000:
                bd -= 0x10000
            target = (bd if (w & 2) else a + bd) & 0xFFFFFFFF
            pre, cond = bc_cond(bo, bi)
            return '%sif (%s) { %s }' % (pre, cond, self.branch_to(a, target, w & 1, start, end, labels))
        if op == 19:
            xo = (w >> 1) & 0x3FF
            bo, bi = d, ra
            if xo == 16:  # bclr
                pre, cond = bc_cond(bo, bi)
                if w & 1:
                    act = '{ u32 t = c.lr; c.lr = 0x%08Xu; call_indirect(c, t); }' % (a + 4)
                else:
                    act = 'return;'
                return '%sif (%s) %s' % (pre, cond, act) if cond != 'true' else pre + act
            if xo == 528:  # bcctr
                pre, cond = bc_cond(bo | 4, bi)
                if w & 1:
                    act = '{ c.lr = 0x%08Xu; call_indirect(c, c.ctr); }' % (a + 4)
                else:
                    cases = ' '.join('case 0x%08Xu: goto L_%08X;' % (x, x) for x in range(start, end, 4))
                    act = '{ switch (c.ctr) { %s default: call_indirect(c, c.ctr); return; } }' % cases
                return '%sif (%s) %s' % (pre, cond, act) if cond != 'true' else pre + act
            if xo == 0:  # mcrf
                return 'c.setCrField(%d, (c.cr >> (28 - %d * 4)) & 0xF);' % (d >> 2, ra >> 2)
            crops = {257: '%s & %s', 129: '%s & !%s', 289: '!(%s ^ %s)', 225: '!(%s & %s)', 33: '!(%s | %s)',
                     449: '%s | %s', 417: '%s | !%s', 193: '%s ^ %s'}
            if xo in crops:
                expr = crops[xo] % ('c.crBit(%d)' % ra, 'c.crBit(%d)' % rb)
                return 'c.setCrBit(%d, (%s) ? 1u : 0u);' % (d, expr)
            if xo == 150:
                return ';  // isync'
            return self.unimp(a, w, 'op19_%d' % xo)

        # ---------------- integer immediate
        if op == 14:  # addi
            return '%s = %s;' % (R % d, ea_d(ra, simm))
        if op == 15:  # addis
            return '%s = %s;' % (R % d, ea_d(ra, (simm << 16) & 0xFFFFFFFF))
        if op in (12, 13):  # addic / addic.
            return '%s = add_carry(c, %s, 0x%Xu, 0);%s' % (R % d, R % ra, simm & 0xFFFFFFFF, rc0(op == 13, R % d))
        if op == 8:  # subfic
            return '%s = add_carry(c, ~%s, 0x%Xu, 1);' % (R % d, R % ra, simm & 0xFFFFFFFF)
        if op == 7:  # mulli
            return '%s = (u32)((s32)%s * %d);' % (R % d, R % ra, simm)
        if op == 11:  # cmpi
            return 'c.cmpSigned(%d, (s32)%s, %d);' % (d >> 2, R % ra, simm)
        if op == 10:  # cmpli
            return 'c.cmpUnsigned(%d, %s, 0x%Xu);' % (d >> 2, R % ra, imm)
        if op == 24:
            return '%s = %s | 0x%Xu;' % (R % ra, R % d, imm)
        if op == 25:
            return '%s = %s | 0x%Xu;' % (R % ra, R % d, imm << 16)
        if op == 26:
            return '%s = %s ^ 0x%Xu;' % (R % ra, R % d, imm)
        if op == 27:
            return '%s = %s ^ 0x%Xu;' % (R % ra, R % d, imm << 16)
        if op == 28:
            return '%s = %s & 0x%Xu; c.recordCr0(%s);' % (R % ra, R % d, imm, R % ra)
        if op == 29:
            return '%s = %s & 0x%Xu; c.recordCr0(%s);' % (R % ra, R % d, imm << 16, R % ra)
        if op in (20, 21, 23):
            sh, mb, me = rb, rc, (w >> 1) & 31
            m = mask32(mb, me)
            rot = 'rotl32(%s, %d)' % (R % d, sh) if op != 23 else 'rotl32(%s, %s & 31)' % (R % d, R % rb)
            if op == 20:
                expr = '(%s & 0x%Xu) | (%s & 0x%Xu)' % (rot, m, R % ra, (~m) & 0xFFFFFFFF)
            else:
                expr = '%s & 0x%Xu' % (rot, m)
            return '%s = %s;%s' % (R % ra, expr, rc0(w & 1, R % ra))

        # ---------------- loads / stores (D-form)
        mem_d = {32: ('lwz', 'c.mem.read32(%s)', 0), 33: ('lwzu', 'c.mem.read32(%s)', 1),
                 34: ('lbz', 'c.mem.read8(%s)', 0), 35: ('lbzu', 'c.mem.read8(%s)', 1),
                 40: ('lhz', 'c.mem.read16(%s)', 0), 41: ('lhzu', 'c.mem.read16(%s)', 1),
                 42: ('lha', '(u32)(s32)(s16)c.mem.read16(%s)', 0), 43: ('lhau', '(u32)(s32)(s16)c.mem.read16(%s)', 1)}
        if op in mem_d:
            _, rd_expr, upd = mem_d[op]
            if upd:
                return '{ u32 ea = %s + 0x%Xu; %s = %s; %s = ea; }' % (R % ra, simm & 0xFFFFFFFF, R % d, rd_expr % 'ea', R % ra)
            return '%s = %s;' % (R % d, rd_expr % ea_d(ra, simm))
        st_d = {36: ('c.mem.write32(%s, %s);', 0), 37: ('c.mem.write32(%s, %s);', 1),
                38: ('c.mem.write8(%s, (u8)%s);', 0), 39: ('c.mem.write8(%s, (u8)%s);', 1),
                44: ('c.mem.write16(%s, (u16)%s);', 0), 45: ('c.mem.write16(%s, (u16)%s);', 1)}
        if op in st_d:
            tmpl, upd = st_d[op]
            if upd:
                return '{ u32 ea = %s + 0x%Xu; %s %s = ea; }' % (R % ra, simm & 0xFFFFFFFF, tmpl % ('ea', R % d), R % ra)
            return tmpl % (ea_d(ra, simm), R % d)
        if op == 46:  # lmw
            return '{ u32 ea = %s; for (u32 r = %d; r < 32; r++, ea += 4) c.gpr[r] = c.mem.read32(ea); }' % (ea_d(ra, simm), d)
        if op == 47:  # stmw
            return '{ u32 ea = %s; for (u32 r = %d; r < 32; r++, ea += 4) c.mem.write32(ea, c.gpr[r]); }' % (ea_d(ra, simm), d)
        if op in (48, 49):  # lfs / lfsu
            ea = ('%s + 0x%Xu' % (R % ra, simm & 0xFFFFFFFF)) if op == 49 else ea_d(ra, simm)
            upd = ' %s = ea;' % (R % ra) if op == 49 else ''
            return '{ u32 ea = %s; f64 v = (f64)c.mem.read_f32(ea); %s.ps0 = v; %s.ps1 = v;%s }' % (ea, F % d, F % d, upd)
        if op in (50, 51):  # lfd / lfdu
            ea = ('%s + 0x%Xu' % (R % ra, simm & 0xFFFFFFFF)) if op == 51 else ea_d(ra, simm)
            upd = ' %s = ea;' % (R % ra) if op == 51 else ''
            return '{ u32 ea = %s; %s.ps0 = c.mem.read_f64(ea);%s }' % (ea, F % d, upd)
        if op in (52, 53):  # stfs / stfsu
            ea = ('%s + 0x%Xu' % (R % ra, simm & 0xFFFFFFFF)) if op == 53 else ea_d(ra, simm)
            upd = ' %s = ea;' % (R % ra) if op == 53 else ''
            return '{ u32 ea = %s; c.mem.write_f32(ea, (f32)%s.ps0);%s }' % (ea, F % d, upd)
        if op in (54, 55):  # stfd / stfdu
            ea = ('%s + 0x%Xu' % (R % ra, simm & 0xFFFFFFFF)) if op == 55 else ea_d(ra, simm)
            upd = ' %s = ea;' % (R % ra) if op == 55 else ''
            return '{ u32 ea = %s; c.mem.write_f64(ea, %s.ps0);%s }' % (ea, F % d, upd)
        if op in (56, 57, 60, 61):  # psq_l(u) / psq_st(u)
            off = w & 0xFFF
            if off & 0x800:
                off -= 0x1000
            wbit, gi = (w >> 15) & 1, (w >> 12) & 7
            upd = op in (57, 61)
            ea = ('%s + 0x%Xu' % (R % ra, off & 0xFFFFFFFF)) if upd else ea_d(ra, off)
            fn = 'psq_load' if op in (56, 57) else 'psq_store'
            tail = ' %s = ea;' % (R % ra) if upd else ''
            return '{ u32 ea = %s; %s(c, %d, ea, %d, %d);%s }' % (ea, fn, d, wbit, gi, tail)

        # ---------------- opcode 31
        if op == 31:
            return self.op31(a, w, d, ra, rb)

        # ---------------- floating point
        if op in (59, 63):
            return self.fp(a, w, op, d, ra, rb, rc)
        if op == 4:
            return self.ps(a, w, d, ra, rb, rc)

        return self.unimp(a, w, 'op%d' % op)

    def op31(self, a, w, d, ra, rb):
        R = 'c.gpr[%d]'
        F = 'c.fpr[%d]'
        rc = w & 1
        xo = (w >> 1) & 0x3FF
        xo9 = (w >> 1) & 0x1FF
        rd, rs = d, d
        arith = {
            266: '%(a)s + %(b)s',
            40: '%(b)s - %(a)s',
            104: '0u - %(a)s',
            235: '(u32)((s32)%(a)s * (s32)%(b)s)',
            75: 'mulhw(%(a)s, %(b)s)',
            11: 'mulhwu(%(a)s, %(b)s)',
            491: 'divw(%(a)s, %(b)s)',
            459: 'divwu(%(a)s, %(b)s)',
        }
        if xo9 in arith:
            expr = arith[xo9] % {'a': R % ra, 'b': R % rb}
            return '%s = %s;%s' % (R % rd, expr, rc0(rc, R % rd))
        carry = {10: ('%s', '%s', '0'), 138: ('%s', '%s', 'c.ca()'), 202: ('%s', '0u', 'c.ca()'),
                 234: ('%s', '0xFFFFFFFFu', 'c.ca()'), 8: ('~%s', '%s', '1'), 136: ('~%s', '%s', 'c.ca()'),
                 200: ('~%s', '0u', 'c.ca()'), 232: ('~%s', '0xFFFFFFFFu', 'c.ca()')}
        if xo9 in carry:
            x, y, cin = carry[xo9]
            x = x % (R % ra)
            y = y % (R % rb) if '%s' in y else y
            return '%s = add_carry(c, %s, %s, %s);%s' % (R % rd, x, y, cin, rc0(rc, R % rd))
        logic = {28: '%(s)s & %(b)s', 60: '%(s)s & ~%(b)s', 444: '%(s)s | %(b)s', 412: '%(s)s | ~%(b)s',
                 316: '%(s)s ^ %(b)s', 476: '~(%(s)s & %(b)s)', 124: '~(%(s)s | %(b)s)', 284: '~(%(s)s ^ %(b)s)',
                 24: '((%(b)s & 0x20) ? 0u : (%(s)s << (%(b)s & 31)))',
                 536: '((%(b)s & 0x20) ? 0u : (%(s)s >> (%(b)s & 31)))',
                 26: '(u32)std::countl_zero(%(s)s)', 954: '(u32)(s32)(s8)%(s)s', 922: '(u32)(s32)(s16)%(s)s'}
        if xo in logic:
            expr = logic[xo] % {'s': R % rs, 'b': R % rb}
            return '%s = %s;%s' % (R % ra, expr, rc0(rc, R % ra))
        if xo == 792:
            return '%s = sraw(c, %s, %s & 63);%s' % (R % ra, R % rs, R % rb, rc0(rc, R % ra))
        if xo == 824:
            return '%s = sraw(c, %s, %d);%s' % (R % ra, R % rs, rb, rc0(rc, R % ra))
        if xo == 0:
            return 'c.cmpSigned(%d, (s32)%s, (s32)%s);' % (d >> 2, R % ra, R % rb)
        if xo == 32:
            return 'c.cmpUnsigned(%d, %s, %s);' % (d >> 2, R % ra, R % rb)
        if xo == 19:
            return '%s = c.cr;' % (R % rd)
        if xo == 144:
            crm = (w >> 12) & 0xFF
            m = 0
            for i in range(8):
                if crm & (0x80 >> i):
                    m |= 0xF << (28 - i * 4)
            return 'c.cr = (c.cr & 0x%Xu) | (%s & 0x%Xu);' % ((~m) & 0xFFFFFFFF, R % rs, m)
        if xo in (339, 467):
            spr = ((w >> 16) & 31) | (((w >> 11) & 31) << 5)
            names = {8: 'c.lr', 9: 'c.ctr', 1: 'c.xer'}
            if spr in names:
                tgt = names[spr]
            elif 912 <= spr <= 919:
                tgt = 'c.gqr[%d]' % (spr - 912)
            else:
                tgt = 'c.spr[%d]' % spr
            return ('%s = %s;' % (R % rd, tgt)) if xo == 339 else ('%s = %s;' % (tgt, R % rs))
        if xo == 371:  # mftb
            tbr = ((w >> 16) & 31) | (((w >> 11) & 31) << 5)
            return '%s = timebase(%s);' % (R % rd, 'true' if tbr == 269 else 'false')
        if xo == 83:
            return '%s = c.msr;' % (R % rd)
        if xo == 146:
            return 'c.msr = %s;' % (R % rs)
        loads = {23: ('c.mem.read32(%s)', 0), 55: ('c.mem.read32(%s)', 1), 87: ('c.mem.read8(%s)', 0),
                 119: ('c.mem.read8(%s)', 1), 279: ('c.mem.read16(%s)', 0), 311: ('c.mem.read16(%s)', 1),
                 343: ('(u32)(s32)(s16)c.mem.read16(%s)', 0), 375: ('(u32)(s32)(s16)c.mem.read16(%s)', 1),
                 534: ('bswap32(c.mem.read32(%s))', 0), 790: ('(u32)bswap16(c.mem.read16(%s))', 0)}
        if xo in loads:
            expr, upd = loads[xo]
            if upd:
                return '{ u32 ea = %s + %s; %s = %s; %s = ea; }' % (R % ra, R % rb, R % rd, expr % 'ea', R % ra)
            return '%s = %s;' % (R % rd, expr % ea_x(ra, rb))
        stores = {151: ('c.mem.write32(%s, %s);', 0), 183: ('c.mem.write32(%s, %s);', 1),
                  215: ('c.mem.write8(%s, (u8)%s);', 0), 247: ('c.mem.write8(%s, (u8)%s);', 1),
                  407: ('c.mem.write16(%s, (u16)%s);', 0), 439: ('c.mem.write16(%s, (u16)%s);', 1),
                  662: ('c.mem.write32(%s, bswap32(%s));', 0), 918: ('c.mem.write16(%s, bswap16((u16)%s));', 0)}
        if xo in stores:
            tmpl, upd = stores[xo]
            if upd:
                return '{ u32 ea = %s + %s; %s %s = ea; }' % (R % ra, R % rb, tmpl % ('ea', R % rs), R % ra)
            return tmpl % (ea_x(ra, rb), R % rs)
        fls = {535: ('lfs', 0), 567: ('lfs', 1), 599: ('lfd', 0), 631: ('lfd', 1),
               663: ('stfs', 0), 695: ('stfs', 1), 727: ('stfd', 0), 759: ('stfd', 1)}
        if xo in fls:
            kind, upd = fls[xo]
            ea = ('%s + %s' % (R % ra, R % rb)) if upd else ea_x(ra, rb)
            tail = ' %s = ea;' % (R % ra) if upd else ''
            body = {'lfs': 'f64 v = (f64)c.mem.read_f32(ea); %(f)s.ps0 = v; %(f)s.ps1 = v;',
                    'lfd': '%(f)s.ps0 = c.mem.read_f64(ea);',
                    'stfs': 'c.mem.write_f32(ea, (f32)%(f)s.ps0);',
                    'stfd': 'c.mem.write_f64(ea, %(f)s.ps0);'}[kind] % {'f': F % d}
            return '{ u32 ea = %s; %s%s }' % (ea, body, tail)
        if xo == 983:  # stfiwx
            return 'c.mem.write32(%s, fpr_low_word(%s.ps0));' % (ea_x(ra, rb), F % d)
        if xo == 1014:  # dcbz
            return 'dcbz(c, %s);' % ea_x(ra, rb)
        if xo in (86, 54, 278, 246, 470, 982, 598, 854):
            return ';  // cache/sync op'
        x6 = (w >> 1) & 0x3F
        if x6 in (6, 38, 7, 39):  # psq_lx / psq_lux / psq_stx / psq_stux
            wbit, gi = (w >> 10) & 1, (w >> 7) & 7
            upd = x6 in (38, 39)
            ea = ('%s + %s' % (R % ra, R % rb)) if upd else ea_x(ra, rb)
            fn = 'psq_load' if x6 in (6, 38) else 'psq_store'
            tail = ' %s = ea;' % (R % ra) if upd else ''
            return '{ u32 ea = %s; %s(c, %d, ea, %d, %d);%s }' % (ea, fn, d, wbit, gi, tail)
        return self.unimp(a, w, 'op31_%d' % xo)

    def fp(self, a, w, op, d, ra, rb, rc):
        F = 'c.fpr[%d].ps0'
        single = op == 59
        xo5 = (w >> 1) & 31
        rcbit = w & 1
        fa, fb, fc = F % ra, F % rb, F % rc
        a_ops = {21: '%(a)s + %(b)s', 20: '%(a)s - %(b)s', 25: '%(a)s * %(c)s', 18: '%(a)s / %(b)s',
                 29: '%(a)s * %(c)s + %(b)s', 28: '%(a)s * %(c)s - %(b)s',
                 31: '-(%(a)s * %(c)s + %(b)s)', 30: '-(%(a)s * %(c)s - %(b)s)'}
        if xo5 in a_ops:
            expr = a_ops[xo5] % {'a': fa, 'b': fb, 'c': fc}
            if single:
                return '{ f64 r = to_single(%s); c.fpr[%d].ps0 = r; c.fpr[%d].ps1 = r; }' % (expr, d, d)
            return 'c.fpr[%d].ps0 = %s;' % (d, expr)
        if xo5 == 23 and not single:  # fsel
            return 'c.fpr[%d].ps0 = (%s >= 0.0) ? %s : %s;' % (d, fa, fc, fb)
        if xo5 == 24 and single:  # fres
            return '{ f64 r = fres(%s); c.fpr[%d].ps0 = r; c.fpr[%d].ps1 = r; }' % (fb, d, d)
        if xo5 == 26 and not single:  # frsqrte
            return 'c.fpr[%d].ps0 = frsqrte(%s);' % (d, fb)
        if single:
            return self.unimp(a, w, 'op59_%d' % xo5)
        xo = (w >> 1) & 0x3FF
        if xo in (0, 32):
            return 'c.cmpFloat(%d, %s, %s);' % (d >> 2, fa, fb)
        unary = {12: 'to_single(%s)', 40: '-%s', 72: '%s', 136: '-std::fabs(%s)', 264: 'std::fabs(%s)',
                 14: 'fctiw(%s, false)', 15: 'fctiw(%s, true)'}
        if xo in unary:
            return 'c.fpr[%d].ps0 = %s;' % (d, unary[xo] % fb)
        if xo == 583:  # mffs
            return 'c.fpr[%d].ps0 = std::bit_cast<f64>((u64)c.fpscr);' % d
        if xo == 711:  # mtfsf
            fm = (w >> 17) & 0xFF
            m = 0
            for i in range(8):
                if fm & (0x80 >> i):
                    m |= 0xF << (28 - i * 4)
            return 'c.fpscr = (c.fpscr & 0x%Xu) | (fpr_low_word(%s) & 0x%Xu);' % ((~m) & 0xFFFFFFFF, fb, m)
        if xo in (38, 70):  # mtfsb1 / mtfsb0
            bit = 1 << (31 - d)
            return ('c.fpscr |= 0x%Xu;' % bit) if xo == 38 else ('c.fpscr &= 0x%Xu;' % ((~bit) & 0xFFFFFFFF))
        return self.unimp(a, w, 'op63_%d' % xo)

    def ps(self, a, w, d, ra, rb, rc):
        P = 'c.fpr[%d]'
        xo5 = (w >> 1) & 31
        xo = (w >> 1) & 0x3FF
        A, B, C = P % ra, P % rb, P % rc
        a_ops = {21: '%s.ps%%d + %s.ps%%d', 20: '%s.ps%%d - %s.ps%%d', 18: '%s.ps%%d / %s.ps%%d'}
        if xo5 in a_ops:
            t = a_ops[xo5] % (A, B)
            return '{ f64 r0 = to_single(%s); f64 r1 = to_single(%s); %s.ps0 = r0; %s.ps1 = r1; }' % (t % (0, 0), t % (1, 1), P % d, P % d)
        if xo5 == 25:  # ps_mul
            return '{ f64 r0 = to_single(%s.ps0 * %s.ps0); f64 r1 = to_single(%s.ps1 * %s.ps1); %s.ps0 = r0; %s.ps1 = r1; }' % (A, C, A, C, P % d, P % d)
        fma = {29: ('', '+'), 28: ('', '-'), 31: ('-', '+'), 30: ('-', '-')}
        if xo5 in fma:
            neg, sign = fma[xo5]
            e0 = '%s(%s.ps0 * %s.ps0 %s %s.ps0)' % (neg, A, C, sign, B)
            e1 = '%s(%s.ps1 * %s.ps1 %s %s.ps1)' % (neg, A, C, sign, B)
            return '{ f64 r0 = to_single(%s); f64 r1 = to_single(%s); %s.ps0 = r0; %s.ps1 = r1; }' % (e0, e1, P % d, P % d)
        if xo5 in (12, 13):  # ps_muls0/1
            s = 'ps%d' % (xo5 - 12)
            return '{ f64 r0 = to_single(%s.ps0 * %s.%s); f64 r1 = to_single(%s.ps1 * %s.%s); %s.ps0 = r0; %s.ps1 = r1; }' % (A, C, s, A, C, s, P % d, P % d)
        if xo5 in (14, 15):  # ps_madds0/1
            s = 'ps%d' % (xo5 - 14)
            return '{ f64 r0 = to_single(%s.ps0 * %s.%s + %s.ps0); f64 r1 = to_single(%s.ps1 * %s.%s + %s.ps1); %s.ps0 = r0; %s.ps1 = r1; }' % (A, C, s, B, A, C, s, B, P % d, P % d)
        if xo5 == 10:  # ps_sum0
            return '{ f64 r0 = to_single(%s.ps0 + %s.ps1); f64 r1 = %s.ps1; %s.ps0 = r0; %s.ps1 = r1; }' % (A, B, C, P % d, P % d)
        if xo5 == 11:  # ps_sum1
            return '{ f64 r0 = %s.ps0; f64 r1 = to_single(%s.ps0 + %s.ps1); %s.ps0 = r0; %s.ps1 = r1; }' % (C, A, B, P % d, P % d)
        if xo5 == 23:  # ps_sel
            return '{ f64 r0 = %s.ps0 >= 0.0 ? %s.ps0 : %s.ps0; f64 r1 = %s.ps1 >= 0.0 ? %s.ps1 : %s.ps1; %s.ps0 = r0; %s.ps1 = r1; }' % (A, C, B, A, C, B, P % d, P % d)
        if xo5 == 24:  # ps_res
            return '{ f64 r0 = fres(%s.ps0); f64 r1 = fres(%s.ps1); %s.ps0 = r0; %s.ps1 = r1; }' % (B, B, P % d, P % d)
        if xo5 == 26:  # ps_rsqrte
            return '{ f64 r0 = to_single(frsqrte(%s.ps0)); f64 r1 = to_single(frsqrte(%s.ps1)); %s.ps0 = r0; %s.ps1 = r1; }' % (B, B, P % d, P % d)
        merges = {528: ('ps0', 'ps0'), 560: ('ps0', 'ps1'), 592: ('ps1', 'ps0'), 624: ('ps1', 'ps1')}
        if xo in merges:
            x, y = merges[xo]
            return '{ f64 r0 = %s.%s; f64 r1 = %s.%s; %s.ps0 = r0; %s.ps1 = r1; }' % (A, x, B, y, P % d, P % d)
        unary = {40: '-%s', 72: '%s', 136: '-std::fabs(%s)', 264: 'std::fabs(%s)'}
        if xo in unary:
            u = unary[xo]
            return '{ f64 r0 = %s; f64 r1 = %s; %s.ps0 = r0; %s.ps1 = r1; }' % (u % (B + '.ps0'), u % (B + '.ps1'), P % d, P % d)
        if xo in (0, 32):
            return 'c.cmpFloat(%d, %s.ps0, %s.ps0);' % (d >> 2, A, B)
        if xo in (64, 96):
            return 'c.cmpFloat(%d, %s.ps1, %s.ps1);' % (d >> 2, A, B)
        x6 = (w >> 1) & 0x3F
        if x6 in (6, 38, 7, 39):
            return self.op31(a, w, d, ra, rb)
        return self.unimp(a, w, 'op4_%d' % xo)


# ----------------------------------------------------------------------------- emit


HEADER = '''// Generated by pc_port/tools/dol2cpp.py from the user's own main.dol.
// Build artifact: do not commit or redistribute.
#include "recomp_helpers.hpp"
#include "recomp_decls.hpp"
#if defined(_MSC_VER)
#pragma warning(disable : 4102 4146)
#endif
using namespace g2c;
'''


def c_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def emit(out_dir, dol, funcs, lifted, shards):
    os.makedirs(out_dir, exist_ok=True)
    lf = Lifter(funcs, set(lifted))
    order = sorted(lifted)
    with open(os.path.join(out_dir, 'recomp_decls.hpp'), 'w', newline='\n') as f:
        f.write('#pragma once\n#include "cpu.hpp"\n')
        for addr in order:
            f.write('void f_%08X(g2c::CpuContext& c);\n' % addr)
    buckets = [[] for _ in range(shards)]
    for i, addr in enumerate(order):
        buckets[i * shards // max(1, len(order))].append(addr)
    for i, bucket in enumerate(buckets):
        path = os.path.join(out_dir, 'recomp_funcs_%02d.cpp' % i)
        with open(path, 'w', newline='\n') as f:
            f.write(HEADER)
            for addr in bucket:
                name, size, _ = funcs[addr]
                f.write('\n// %s\nvoid f_%08X(CpuContext& c) {\n' % (name.replace('\n', ' '), addr))
                f.write('\n'.join(lf.lift_function(dol, addr, size)))
                f.write('\n}\n')
    stats = 'functions %d, instructions %d, unimplemented %d' % (len(order), lf.ninsn, sum(lf.unimpl.values()))
    top = ', '.join('%s:%d' % kv for kv in lf.unimpl.most_common(12))
    with open(os.path.join(out_dir, 'recomp_register.cpp'), 'w', newline='\n') as f:
        f.write('// Generated by dol2cpp.py. Build artifact: do not commit.\n#include "dispatch.hpp"\n#include "recomp_decls.hpp"\n\n')
        f.write('void g2c_register_all() {\n')
        for addr in order:
            f.write('    g2c::register_func(0x%08Xu, &f_%08X);\n' % (addr, addr))
        f.write('}\n\nconst g2c::SymbolEntry g2c_symbols[] = {\n')
        for addr in order:
            f.write('    {%s, 0x%08Xu},\n' % (c_str(funcs[addr][0]), addr))
        f.write('    {nullptr, 0},\n};\n')
        f.write('const std::size_t g2c_symbol_count = %d;\n' % len(order))
        f.write('const char* const g2c_lift_stats = %s;\n' % c_str(stats + ('; top unimplemented: ' + top if top else '')))
    return lf, stats, top


# ----------------------------------------------------------------------------- self test


def selftest():
    funcs = {0x80004000: ('test', 0x40, '.text')}
    lf = Lifter(funcs, {0x80004000})
    cases = [
        (0x38600005, 'c.gpr[3] = 0u + 0x5u;'),                     # li r3, 5
        (0x7C632214, 'c.gpr[3] = c.gpr[3] + c.gpr[4];'),           # add r3, r3, r4
        (0x5463103A, 'c.gpr[3] = rotl32(c.gpr[3], 2) & 0xFFFFFFFCu;'),  # slwi r3, r3, 2
        (0x2C030000, 'c.cmpSigned(0, (s32)c.gpr[3], 0);'),         # cmpwi r3, 0
        (0x80630004, 'c.gpr[3] = c.mem.read32(c.gpr[3] + 0x4u);'),  # lwz r3, 4(r3)
        (0x9421FFF0, 'u32 ea = c.gpr[1] + 0xFFFFFFF0u; c.mem.write32(ea, c.gpr[1]); c.gpr[1] = ea;'),  # stwu r1,-16(r1)
        (0x4E800020, 'return;'),                                   # blr
        (0x7C0802A6, 'c.gpr[0] = c.lr;'),                          # mflr r0
        (0xFC20102A, 'c.fpr[1].ps0 = c.fpr[0].ps0 + c.fpr[2].ps0;'),  # fadd f1, f0, f2
        (0x10421028, 'to_single(c.fpr[2].ps0 - c.fpr[2].ps0)'),     # ps_sub f2, f2, f2
    ]
    bad = 0
    for word, want in cases:
        got = lf.insn(0x80004000, word, 0x80004000, 0x80004040, set())
        if want not in got:
            print('FAIL %08X: want %r got %r' % (word, want, got))
            bad += 1
    # in-function branch -> goto
    got = lf.insn(0x80004000, 0x48000010, 0x80004000, 0x80004040, set())
    if 'goto L_80004010;' not in got:
        print('FAIL b +0x10: %r' % got)
        bad += 1
    if lf.unimpl:
        print('FAIL unexpected unimplemented', dict(lf.unimpl))
        bad += 1
    print('selftest: %d/%d passed' % (len(cases) + 2 - bad, len(cases) + 2))
    return 1 if bad else 0


# ----------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dol')
    ap.add_argument('--symbols')
    ap.add_argument('--splits')
    ap.add_argument('--out')
    ap.add_argument('--units', default='MSL_C,Runtime', help="comma-separated unit prefixes from splits.txt, or ALL")
    ap.add_argument('--shards', type=int, default=16)
    ap.add_argument('--also', default='', help='comma-separated extra function names to lift')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.dol and args.symbols and args.out):
        ap.error('--dol, --symbols and --out are required')
    dol = Dol(open(args.dol, 'rb').read())
    funcs = load_functions(args.symbols)
    if args.units.upper() == 'ALL':
        lifted = list(funcs)
    else:
        if not args.splits:
            ap.error('--splits is required unless --units ALL')
        ranges = load_unit_ranges(args.splits, [p.strip() for p in args.units.split(',') if p.strip()])
        lifted = [a for a, (n, s, sec) in funcs.items() if sec == '.init' or any(lo <= a < hi for lo, hi in ranges)]
    extra = {x.strip() for x in args.also.split(',') if x.strip()}
    if extra:
        found = {a for a, (n, s, sec) in funcs.items() if n in extra}
        missing = extra - {funcs[a][0] for a in found}
        if missing:
            ap.error('unknown --also functions: ' + ', '.join(sorted(missing)))
        lifted = sorted(set(lifted) | found)
    _, stats, top = emit(args.out, dol, funcs, lifted, args.shards)
    print('dol2cpp:', stats)
    if top:
        print('dol2cpp: top unimplemented:', top)
    return 0


if __name__ == '__main__':
    sys.exit(main())
