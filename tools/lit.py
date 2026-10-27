"""Resolve PIC literal (pc-anchor A, pool word at B) -> GOT -> name.  usage: lit.py A B [A B ...] (hex)"""
import sys, importlib.util, os
sys.argv = [sys.argv[0], r'D:\CubeSurvival\in\apk\lib\armeabi-v7a\libil2cpp.so', r'D:\CubeSurvival\dump\names.txt',
            os.devnull, os.devnull] + sys.argv[1:]
spec = importlib.util.spec_from_file_location('r', r'D:\CubeSurvival\scripts\resolve_dec.py')
r = importlib.util.module_from_spec(spec)
args = sys.argv[5:]
spec.loader.exec_module(r)
import re
for i in range(0, len(args), 2):
    m = re.match(r'(.*)', '')
    class M:
        def __init__(s, a, b): s.a, s.b = a, b
        def group(s, k): return {0: '?', 1: s.a, 2: s.b}[k]
    print(args[i], args[i + 1], r.lit(M(args[i], args[i + 1])))
