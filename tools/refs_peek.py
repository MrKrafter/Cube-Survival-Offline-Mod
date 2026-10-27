"""Peek into decoded references (cmp/r14.json).
usage: refs_peek.py keys                 -> top-level sections with sizes
       refs_peek.py show <section> [n]   -> first n entries of a section (json)
       refs_peek.py grep <regex> [n]     -> paths whose key or string value matches"""
import json, re, sys

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
cmd = sys.argv[1]
if cmd == 'keys':
    for k, v in R.items():
        print('%-40s %-6s %d' % (k, type(v).__name__, len(v) if hasattr(v, '__len__') else 0))
elif cmd == 'show':
    v = R[sys.argv[2]]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    items = list(v.items())[:n] if isinstance(v, dict) else v[:n]
    print(json.dumps(items, ensure_ascii=False, indent=1)[:20000])
elif cmd == 'grep':
    rx = re.compile(sys.argv[2], re.I)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    out = []
    def walk(o, path):
        if len(out) >= n:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if rx.search(str(k)):
                    out.append(path + '/' + str(k))
                walk(v, path + '/' + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, '%s[%d]' % (path, i))
        elif isinstance(o, str) and rx.search(o):
            out.append('%s = %s' % (path, o[:80]))
    walk(R, '')
    print('\n'.join(out))
