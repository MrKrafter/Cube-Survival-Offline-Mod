"""For dump.cs line numbers, print the owning class and the method line with RVA.  usage: owner.py <line> [...]"""
import re, sys

lines = open(r'D:\CubeSurvival\dump\dump.cs', encoding='utf-8').read().split('\n')
for a in sys.argv[1:]:
    n = int(a) - 1
    cls = '?'
    for i in range(n, -1, -1):
        m = re.match(r'(?:public |internal |private |protected )?(?:sealed |abstract |static )*(?:class|struct|interface) (.*?) //', lines[i])
        if m:
            cls = m.group(1)
            break
    rva = lines[n - 1].strip() if 'RVA' in lines[n - 1] else ''
    m = re.search(r'RVA: (0x[0-9A-F]+)', rva)
    print('%-7s %-10s %-60s %s' % (a, m.group(1) if m else '', cls[:60], lines[n].strip()))
