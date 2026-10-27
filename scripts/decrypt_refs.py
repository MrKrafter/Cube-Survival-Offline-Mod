"""Try to decode the r14 TextAsset: utf8 text -> xor chars -> base64 -> lz4."""
import sys, base64, collections

raw = open(sys.argv[1], 'rb').read()
print('len', len(raw), raw[:32])
try:
    txt = raw.decode('utf-8')
    print('utf8 chars', len(txt), collections.Counter(ord(c) >> 8 for c in txt).most_common(5))
except Exception as e:
    print('not utf8', e)
    txt = None
# guess xor key: base64 alphabet chars xor key -> observed chars
if txt:
    c0 = ord(txt[0])
    for k in (5987,):
        s = ''.join(chr(ord(c) ^ k) for c in txt[:80])
        print(k, repr(s))
