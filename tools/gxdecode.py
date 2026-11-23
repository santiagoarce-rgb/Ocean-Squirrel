"""Decode a raw GameCube/Wii GX FIFO byte stream (as dumped by NWII_GXDUMP).

Tracks CP VCD/VAT registers so primitive vertex data can be skipped exactly.
Prints an opcode histogram, the first primitives, and the first decode error.
"""
import struct, sys, collections

PRIMS = {0x80: 'QUADS', 0x88: 'QUADS2', 0x90: 'TRIANGLES', 0x98: 'TRISTRIP',
         0xA0: 'TRIFAN', 0xA8: 'LINES', 0xB0: 'LINESTRIP', 0xB8: 'POINTS'}
COMP = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4}          # u8 s8 u16 s16 f32
COLOR = {0: 2, 1: 3, 2: 4, 3: 2, 4: 3, 5: 4}    # 565 888 888x 4444 6666 8888

cp = collections.defaultdict(int)

def bits(v, lo, n): return (v >> lo) & ((1 << n) - 1)

def vertex_size(vat):
    lo, hi = cp[0x50], cp[0x60]
    a, b, c = cp[0x70 + vat], cp[0x80 + vat], cp[0x90 + vat]
    size = bin(lo & 0x1FF).count('1')           # PNMTXIDX + TEX0..7 MTXIDX
    def attr(kind, direct):
        return {0: 0, 1: direct, 2: 1, 3: 2}[kind]
    pos = bits(lo, 9, 2)
    size += attr(pos, (3 if bits(a, 0, 1) else 2) * COMP.get(bits(a, 1, 3), 4))
    nrm = bits(lo, 11, 2)
    nbt = bits(a, 9, 1)
    ncomp = 9 if nbt else 3
    nidx3 = bits(a, 31, 1)
    if nrm in (2, 3) and nbt and nidx3:
        size += 3 * (1 if nrm == 2 else 2)
    else:
        size += attr(nrm, ncomp * COMP.get(bits(a, 10, 3), 4))
    size += attr(bits(lo, 13, 2), COLOR.get(bits(a, 14, 3), 4))
    size += attr(bits(lo, 15, 2), COLOR.get(bits(a, 18, 3), 4))
    tex = [(bits(a, 21, 1), bits(a, 22, 3)), (bits(b, 0, 1), bits(b, 1, 3)),
           (bits(b, 9, 1), bits(b, 10, 3)), (bits(b, 18, 1), bits(b, 19, 3)),
           (bits(b, 27, 1), bits(b, 28, 3)), (bits(c, 5, 1), bits(c, 6, 3)),
           (bits(c, 14, 1), bits(c, 15, 3)), (bits(c, 23, 1), bits(c, 24, 3))]
    for i, (cnt, fmt) in enumerate(tex):
        size += attr(bits(hi, i * 2, 2), (2 if cnt else 1) * COMP.get(fmt, 4))
    return size

def main(path, show=25):
    d = open(path, 'rb').read()
    i, n = 0, len(d)
    hist = collections.Counter()
    prims, shown = 0, 0
    bp_regs = collections.Counter()
    while i < n:
        op = d[i]
        start = i
        i += 1
        try:
            if op == 0x00:
                hist['NOP'] += 1
            elif op == 0x08:
                reg = d[i]; val, = struct.unpack('>I', d[i+1:i+5]); i += 5
                cp[reg] = val; hist['CP'] += 1
            elif op == 0x10:
                hdr, = struct.unpack('>I', d[i:i+4]); i += 4
                i += (((hdr >> 16) & 0xF) + 1) * 4; hist['XF'] += 1
            elif op in (0x20, 0x28, 0x30, 0x38):
                i += 4; hist['XF_INDEXED'] += 1
            elif op == 0x40:
                addr, size = struct.unpack('>II', d[i:i+8]); i += 8
                hist['CALL_DL'] += 1
                if hist['CALL_DL'] <= 5:
                    print(f'@{start:#08x} CALL_DL addr={addr:#010x} size={size:#x}')
            elif op in (0x44, 0x48):
                hist['INVAL_VTX' if op == 0x48 else 'OP_44'] += 1
            elif op == 0x61:
                val, = struct.unpack('>I', d[i:i+4]); i += 4
                hist['BP'] += 1; bp_regs[val >> 24] += 1
            elif op & 0x80:
                prim, vat = op & 0xF8, op & 7
                if prim not in PRIMS:
                    raise ValueError('bad primitive')
                count, = struct.unpack('>H', d[i:i+2]); i += 2
                vs = vertex_size(vat)
                i += count * vs
                hist[PRIMS[prim]] += 1; prims += 1
                if shown < show:
                    shown += 1
                    print(f'@{start:#08x} {PRIMS[prim]} vat={vat} verts={count} '
                          f'vtx_size={vs} VCD_LO={cp[0x50]:#x} VCD_HI={cp[0x60]:#x}')
            else:
                raise ValueError('unknown opcode')
        except (ValueError, struct.error) as e:
            ctx = d[start:start + 16].hex(' ')
            print(f'\nDECODE STOP @{start:#08x} op={op:#04x}: {e}\n  bytes: {ctx}')
            prev = d[max(0, start - 32):start].hex(' ')
            print(f'  before: {prev}')
            break
    print(f'\ndecoded {i} of {n} bytes; primitives={prims}')
    for k, v in hist.most_common():
        print(f'  {k:12s} {v}')
    print('top BP registers:', ', '.join(f'{r:#04x}:{c}' for r, c in bp_regs.most_common(12)))

if __name__ == '__main__':
    main(sys.argv[1])
