"""Disassemble a libil2cpp range with call targets named.  usage: dis.py <start_rva> <end_rva>  (hex)"""
import os, re, subprocess, sys, importlib.util

LIB = r'D:\CubeSurvival\in\apk\lib\armeabi-v7a\libil2cpp.so'
OBJDUMP = r'D:\SupercowAndroid\toolchain\ndk\android-ndk-r27d\toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-objdump.exe'
start, end = int(sys.argv[1], 16), int(sys.argv[2], 16)
argv = sys.argv
sys.argv = [argv[0], LIB, r'D:\CubeSurvival\dump\names.txt', os.devnull, os.devnull]
spec = importlib.util.spec_from_file_location('r', r'D:\CubeSurvival\scripts\resolve_dec.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

def callee(a):
    n = r.name_of(a)
    if n:
        return n
    g = r.plt_target(a)
    if g is not None:
        if g in r.gotname:
            return r.gotname[g]
        if g in r.got:
            return r.name_of(r.got[g]) or 'sub_%x' % r.got[g]
    return None

out = subprocess.run([OBJDUMP, '-d', '--no-show-raw-insn', '--triple=armv7a', '--start-address=%#x' % start,
                      '--stop-address=%#x' % end, LIB], capture_output=True, text=True).stdout
for ln in out.splitlines():
    m = re.match(r'\s*([0-9a-f]+):\s+(.*)', ln)
    if not m:
        continue
    addr, ins = int(m.group(1), 16), m.group(2).split('@')[0].rstrip()
    note = ''
    c = re.match(r'(bl|blx|b)\s+0x([0-9a-f]+)', ins)
    if c:
        n = callee(int(c.group(2), 16))
        if n:
            note = '  ; ' + n
    print('%08x  %s%s' % (addr, ins, note))
