"""Find libunity JNI native tables: for each name, print {name, signature, fnPtr} entries.

usage: python -I unative.py <native name>...
Assumes the REL addends are stored in place (vaddr == file offset for the text segment and the
data segment offset delta taken from the program headers).
"""
import struct
import sys

LIB = r"D:\CubeSurvival\in\apk\lib\armeabi-v7a\libunity.so"
data = open(LIB, "rb").read()

# Program headers: map vaddr -> file offset for PT_LOAD segments.
e_phoff, = struct.unpack_from("<I", data, 0x1C)
e_phentsize, e_phnum = struct.unpack_from("<HH", data, 0x2A)
loads = []
for i in range(e_phnum):
    p_type, p_offset, p_vaddr, _, p_filesz, _, _, _ = struct.unpack_from("<8I", data, e_phoff + i * e_phentsize)
    if p_type == 1:
        loads.append((p_vaddr, p_offset, p_filesz))


def off2va(off):
    for va, fo, sz in loads:
        if fo <= off < fo + sz:
            return va + off - fo
    return None


def va2off(va):
    for v, fo, sz in loads:
        if v <= va < v + sz:
            return fo + va - v
    return None


def cstr(va):
    o = va2off(va)
    if o is None:
        return None
    end = data.find(b"\0", o)
    return data[o:end].decode("latin1") if 0 <= end - o < 200 else None


for name in sys.argv[1:]:
    needle = name.encode() + b"\0"
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            break
        if data[pos - 1] == 0:
            sva = off2va(pos)
            ref = struct.pack("<I", sva)
            r = 0
            while True:
                r = data.find(ref, r)
                if r < 0:
                    break
                if r % 4 == 0:
                    n, sig, fn = struct.unpack_from("<III", data, r)
                    print("%s: entry@%#x sig=%r fn=%#x" % (name, off2va(r), cstr(sig), fn))
                r += 4
        pos += 1
