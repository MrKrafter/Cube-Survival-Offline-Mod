"""Name the il2cpp methods containing RVAs, from Il2CppDumper's script.json.

usage: python -I addr2method.py <hex rva>...
"""
import bisect
import json
import sys

with open(r"D:\CubeSurvival\dump\script.json", encoding="utf-8") as f:
    data = json.load(f)
methods = sorted((m["Address"], m["Name"]) for m in data["ScriptMethod"])
starts = [a for a, _ in methods]
for arg in sys.argv[1:]:
    rva = int(arg, 16) & ~1
    i = bisect.bisect_right(starts, rva) - 1
    if i < 0:
        print(f"{rva:#x}: (before first method)")
        continue
    addr, name = methods[i]
    nxt = starts[i + 1] if i + 1 < len(starts) else None
    print(f"{rva:#x}: {name} +{rva - addr:#x}" + ("" if nxt is None else f" (next {nxt:#x})"))
