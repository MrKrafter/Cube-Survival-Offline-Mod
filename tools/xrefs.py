"""Find callers (ARM BL/BLX imm, also via PLT veneers) of methods matching a regex in libil2cpp.so.
usage: xrefs.py <lib.so> <names.txt> <regex>"""
import re, struct, sys, bisect

so, names_path, rx = sys.argv[1:4]
blob = open(so, 'rb').read()
meth = {}
for line in open(names_path, encoding='utf-8'):
    p = line.split(None, 1)
    if len(p) == 2 and not p[1].startswith(('str_', 'md_', 'mi_')):
        meth.setdefault(int(p[0], 16), p[1].strip())
starts = sorted(meth)

phoff = struct.unpack_from('<I', blob, 0x1c)[0]
phnum = struct.unpack_from('<H', blob, 0x2c)[0]
segs, dyn = [], None
for i in range(phnum):
    t, off, va, pa, fs, ms = struct.unpack_from('<IIIIII', blob, phoff + i * 32)
    if t == 1: segs.append((va, off, fs))
    if t == 2: dyn = (va, fs)
def fo(va):
    for sva, off, fs in segs:
        if sva <= va < sva + fs: return off + va - sva
def rd(va):
    o = fo(va); return struct.unpack_from('<I', blob, o)[0] if o is not None else None

# relocations -> GOT values
d = {}
o = fo(dyn[0])
for i in range(dyn[1] // 8):
    tag, val = struct.unpack_from('<II', blob, o + i * 8)
    if tag == 0: break
    d.setdefault(tag, val)
def sym(idx):
    s = fo(d[6] + idx * 16); return struct.unpack_from('<I', blob, s + 4)[0]
got = {}
for a, sz in ((d.get(17), d.get(18)), (d.get(23), d.get(2))):
    if not a: continue
    o = fo(a)
    for i in range(sz // 8):
        r_off, r_info = struct.unpack_from('<II', blob, o + i * 8)
        t = r_info & 0xff
        if t == 23: got[r_off] = rd(r_off)
        elif t in (21, 22): got[r_off] = sym(r_info >> 8)

def imm(x):
    r, v = (x >> 8) & 0xf, x & 0xff
    return ((v >> (2 * r)) | (v << (32 - 2 * r))) & 0xffffffff

targets = {a for a, n in meth.items() if re.search(rx, n)}
text_va, text_off, text_sz = segs[0]
# PLT veneers pointing at targets
plt = {}
for a in range(text_va, text_va + text_sz - 12, 4):
    w0 = rd(a)
    if (w0 & 0xfffff000) != 0xe28fc000: continue
    w1, w2 = rd(a + 4), rd(a + 8)
    if (w1 & 0xfffff000) != 0xe28cc000 or (w2 & 0xfffff000) != 0xe5bcf000: continue
    g = (a + 8 + imm(w0) + imm(w1) + (w2 & 0xfff)) & 0xffffffff
    v = got.get(g)
    if v in targets: plt[a] = v
dest = set(targets) | set(plt)
words = struct.unpack_from('<%dI' % (text_sz // 4), blob, text_off)
hits = {}
for i, w in enumerate(words):
    if (w & 0x0f000000) == 0x0b000000 and (w >> 28) != 0xf:  # BL (cond)
        off = w & 0xffffff
        if off & 0x800000: off -= 0x1000000
        a = text_va + i * 4
        t = (a + 8 + off * 4) & 0xffffffff
        if t in dest:
            tgt = plt.get(t, t)
            k = bisect.bisect_right(starts, a) - 1
            caller = meth[starts[k]] if k >= 0 else '?'
            hits.setdefault(meth[tgt], []).append((a, caller))
for t, lst in sorted(hits.items()):
    print('==', t)
    for a, c in lst:
        print('   %08x  %s' % (a, c))
