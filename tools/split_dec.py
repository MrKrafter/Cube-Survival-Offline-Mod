"""Split a DecompMatch output into per-function sizes; optionally print one function by name substring."""
import sys, re
text = open(sys.argv[1], encoding='utf-8').read()
parts = re.split(r'^// ==== ', text, flags=re.M)[1:]
if len(sys.argv) > 2:
    for p in parts:
        head = p.split('\n', 1)[0]
        if sys.argv[2] in head:
            body = p if len(sys.argv) < 4 else p[:int(sys.argv[3])]
            print('// ==== ' + body)
else:
    sizes = sorted(((len(p), p.split('\n', 1)[0]) for p in parts), reverse=True)
    for s, h in sizes[:25]:
        print(s, h)
