"""Disassemble libunity (ARM or Thumb) before return addresses, with PLT names.

usage: python -I udis.py <hex addr>...   (odd address = Thumb)
"""
import re
import subprocess
import sys

LIB = r"D:\CubeSurvival\in\apk\lib\armeabi-v7a\libunity.so"
BIN = r"D:\SupercowAndroid\toolchain\ndk\android-ndk-r27d\toolchains\llvm\prebuilt\windows-x86_64\bin"

# PLT stub address -> imported symbol, from the relocations of .rel.plt
plt = {}
rel = subprocess.run([BIN + r"\llvm-objdump.exe", "-d", "-j", ".plt", "--no-show-raw-insn", LIB],
                     capture_output=True, text=True).stdout
relocs = subprocess.run([BIN + r"\llvm-readelf.exe", "-r", "--wide", LIB], capture_output=True, text=True).stdout
got2name = {}
for line in relocs.splitlines():
    m = re.match(r"\s*([0-9a-f]{8})\s+[0-9a-f]{8}\s+R_ARM_JUMP_SLOT\s+[0-9a-f]+\s+(\S+)", line)
    if m:
        got2name[int(m.group(1), 16)] = m.group(2)
# Each ARM PLT entry is: add ip, pc, #X; add ip, ip, #Y; ldr pc, [ip, #Z]!  -> GOT = entry+8+X+Y+Z
lines = [l for l in rel.splitlines() if re.match(r"\s*[0-9a-f]+:", l)]
for i in range(len(lines) - 2):
    m0 = re.match(r"\s*([0-9a-f]+):\s+add\s+r12, pc, #(\d+)(?:, (\d+))?", lines[i])
    m1 = re.match(r"\s*[0-9a-f]+:\s+add\s+r12, r12, #(\d+)(?:, (\d+))?", lines[i + 1])
    m2 = re.match(r"\s*[0-9a-f]+:\s+ldr\s+pc, \[r12, #(\d+)\]!", lines[i + 2])
    if m0 and m1 and m2:
        def imm(v, rot):
            v = int(v)
            if rot:
                r = int(rot)
                v = ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF
            return v
        a = int(m0.group(1), 16)
        got = a + 8 + imm(m0.group(2), m0.group(3)) + imm(m1.group(1), m1.group(2)) + int(m2.group(1))
        if got in got2name:
            plt[a] = got2name[got]

for arg in sys.argv[1:]:
    addr = int(arg, 16)
    thumb = addr & 1
    addr &= ~1
    triple = "thumbv7a" if thumb else "armv7a"
    out = subprocess.run([BIN + r"\llvm-objdump.exe", "-d", "--no-show-raw-insn", "--triple=" + triple,
                          "--start-address=%#x" % (addr - 0x28), "--stop-address=%#x" % (addr + 4), LIB],
                         capture_output=True, text=True).stdout
    print("== %#x (%s)" % (addr, "thumb" if thumb else "arm"))
    for l in out.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\s+(.*)", l)
        if not m:
            continue
        text = m.group(2)
        t = re.search(r"\bbl[x]?\s+0x([0-9a-f]+)", text)
        if t and int(t.group(1), 16) in plt:
            text += "  ; " + plt[int(t.group(1), 16)]
        print("  %s  %s" % (m.group(1), text))
