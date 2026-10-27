"""Print every path in r14 whose key or string value matches a regex, with a short value preview.
usage: refs_find.py <regex> [max]"""
import json, re, sys

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
pat = re.compile(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60
n = 0


def walk(o, path):
    global n
    if n >= limit:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            p = path + '/' + str(k)
            if pat.search(str(k)):
                n += 1
                print(p, '=', json.dumps(v, ensure_ascii=False)[:300])
            else:
                walk(v, p)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i))
    elif isinstance(o, str) and pat.search(o):
        n += 1
        print(path, '=', o)


walk(R, '')
