import re, sys
# count methods with code per image in Il2CppDumper dump.cs, and total code size of Assembly-CSharp
dump = sys.argv[1]
cur = None
lo, hi = 4003, 7742
cnt = 0; rvas = []
for line in open(dump, encoding='utf-8', errors='replace'):
    m = re.search(r'// TypeDefIndex: (\d+)', line)
    if m:
        cur = int(m.group(1))
        continue
    m = re.search(r'// RVA: 0x([0-9A-F]+)', line)
    if m and cur is not None and lo <= cur < hi:
        cnt += 1; rvas.append(int(m.group(1), 16))
rvas = sorted(set(rvas))
print('methods', cnt, 'unique', len(rvas))
print('range %x-%x' % (rvas[0], rvas[-1]))
