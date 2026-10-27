"""Read PC-relative string literals of libunity (ARM: pc = insn + 8).

usage: python -I ustr.py <literal_addr>:<add_insn_addr> ...   (hex; file offset == vaddr in the text segment)
"""
import struct
import sys

data = open(r"D:\CubeSurvival\in\apk\lib\armeabi-v7a\libunity.so", "rb").read()
for arg in sys.argv[1:]:
    lit, insn = (int(x, 16) for x in arg.split(":"))
    off = struct.unpack_from("<I", data, lit)[0]
    addr = (insn + 8 + off) & 0xFFFFFFFF
    end = data.find(b"\0", addr)
    print("%s -> %#x %r" % (arg, addr, data[addr:min(end, addr + 120)]))
