"""Make Ghidra output of libil2cpp readable: resolve PIC literal patterns `&UNK_A + _UNK_B`
(GOT entry = A + word@B) through the ELF relocations to Il2CppDumper names (str_/md_/mi_),
and func_0xADDR (PLT veneers or direct) to method/symbol names.
usage: resolve_dec.py <lib.so> <names.txt> <in.c> <out.c>"""
import re, struct, sys

so, names_path, src, dst = sys.argv[1:5]
blob = open(so, 'rb').read()
names = {}
for line in open(names_path, encoding='utf-8'):
    p = line.split(None, 1)
    if len(p) == 2:
        names.setdefault(int(p[0], 16), p[1].strip())

phoff = struct.unpack_from('<I', blob, 0x1c)[0]
phnum = struct.unpack_from('<H', blob, 0x2c)[0]
segs, dyn = [], None
for i in range(phnum):
    t, off, va, pa, fs, ms = struct.unpack_from('<IIIIII', blob, phoff + i * 32)
    if t == 1:
        segs.append((va, off, fs))
    if t == 2:
        dyn = (va, fs)

def fo(va):
    for sva, off, fs in segs:
        if sva <= va < sva + fs:
            return off + va - sva
    return None

def rd(va):
    o = fo(va)
    return struct.unpack_from('<I', blob, o)[0] if o is not None else None

d = {}
o = fo(dyn[0])
for i in range(dyn[1] // 8):
    tag, val = struct.unpack_from('<II', blob, o + i * 8)
    if tag == 0:
        break
    d.setdefault(tag, val)
symtab, strtab = d[6], d[5]

def sym(idx):
    so_ = fo(symtab + idx * 16)
    st_name, st_value = struct.unpack_from('<II', blob, so_)
    s = fo(strtab + st_name)
    e = blob.index(b'\0', s)
    return blob[s:e].decode('latin1'), st_value

got = {}      # address -> resolved pointer value
gotname = {}  # address -> imported symbol name
def relocs(addr, size):
    o = fo(addr)
    for i in range(size // 8):
        r_off, r_info = struct.unpack_from('<II', blob, o + i * 8)
        t, si = r_info & 0xff, r_info >> 8
        if t == 23:
            got[r_off] = rd(r_off)
        elif t in (21, 22, 2):
            n, v = sym(si)
            if v:
                got[r_off] = v + (rd(r_off) if t == 2 else 0)
            else:
                gotname[r_off] = n
if 17 in d: relocs(d[17], d[18])
if 23 in d: relocs(d[23], d[2])

def name_of(a):
    n = names.get(a)
    if n:
        return n
    return None

def lit(m):
    a, b = int(m.group(1), 16), int(m.group(2), 16)
    w = rd(b)
    if w is None:
        return m.group(0)
    g = (a + w) & 0xffffffff
    n = name_of(g)
    if n:
        return '&' + n
    if g in gotname:
        return '&GOT[' + gotname[g] + ']'
    v = got.get(g)
    if v is not None:
        n = name_of(v)
        return '&GOT[%s]' % (n or 'G_%x' % v)
    return '&G_%x' % g

text = open(src, encoding='utf-8').read()
text = re.sub(r'&(?:UNK|DAT|PTR_[A-Za-z0-9_]*)_([0-9a-f]{8}) \+ _(?:UNK|DAT)_([0-9a-f]{8})', lit, text)
text = re.sub(r'\(&(?:UNK|DAT)_([0-9a-f]{8})\)\[_(?:UNK|DAT)_([0-9a-f]{8})\]', lambda m: '*' + lit(m), text)

def plt_target(a):
    """ARM PLT veneer: add ip,pc,#X ; add ip,ip,#Y ; ldr pc,[ip,#Z]!"""
    w = [rd(a + 4 * i) for i in range(3)]
    if None in w or (w[0] & 0xfffff000) != 0xe28fc000 or (w[1] & 0xfffff000) != 0xe28cc000 \
            or (w[2] & 0xfffff000) != 0xe5bcf000:
        return None
    def imm(x):
        r, v = (x >> 8) & 0xf, x & 0xff
        return ((v >> (2 * r)) | (v << (32 - 2 * r))) & 0xffffffff
    g = (a + 8 + imm(w[0]) + imm(w[1]) + (w[2] & 0xfff)) & 0xffffffff
    return g

def clean(n):
    return re.sub(r'[^0-9A-Za-z_]', '_', n.replace('$$', '::').replace('::', '__'))

def fn(m):
    a = int(m.group(1), 16)
    n = name_of(a)
    if not n:
        g = plt_target(a)
        if g is not None:
            if g in gotname:
                n = gotname[g]
            elif g in got:
                n = name_of(got[g]) or 'sub_%x' % got[g]
    return clean(n) if n else m.group(0)

text = re.sub(r'func_0x([0-9a-f]{8})', fn, text)
open(dst, 'w', encoding='utf-8').write(text)
print('ok', len(got), len(gotname))
