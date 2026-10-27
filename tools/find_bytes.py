"""Find a byte string (ASCII, case-insensitive; also UTF-16LE) in every file under a directory; print file, offset and
nearby printable context.  usage: find_bytes.py <dir> <text> [max_hits]"""
import os, re, sys

root, text = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
pats = [re.compile(re.escape(text.encode()), re.I), re.compile(re.escape(text.encode('utf-16-le')), re.I)]
hits = 0
for d, _, files in os.walk(root):
    for f in files:
        p = os.path.join(d, f)
        data = open(p, 'rb').read()
        for pat in pats:
            for m in pat.finditer(data):
                ctx = re.sub(rb'[^\x20-\x7e]', b'.', data[max(0, m.start() - 40):m.end() + 40]).decode()
                print(f'{p} @{m.start():#x}: {ctx}')
                hits += 1
                if hits >= limit:
                    sys.exit()
print('hits:', hits)
