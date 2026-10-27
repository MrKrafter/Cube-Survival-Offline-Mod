"""script.json (Il2CppDumper) -> "<hexaddr> <name>" list for D:\\Ghidra\\scripts\\ApplyNames.java."""
import json, re, sys

src, dst = sys.argv[1], sys.argv[2]
j = json.load(open(src, encoding='utf-8'))

def clean(s, maxlen=120):
    s = re.sub(r'[^0-9A-Za-z_$.<>]', '_', s)
    return s[:maxlen]

seen = set()
with open(dst, 'w', encoding='utf-8') as w:
    for m in j['ScriptMethod']:
        a = m['Address']
        if a in seen:
            continue
        seen.add(a)
        w.write('%x %s\n' % (a, clean(m['Name'], 200)))
    for s in j.get('ScriptString', []):
        w.write('%x str_%s\n' % (s['Address'], clean(s['Value'], 60) or 'empty'))
    for s in j.get('ScriptMetadata', []):
        w.write('%x %s\n' % (s['Address'], 'md_' + clean(s['Name'])))
    for s in j.get('ScriptMetadataMethod', []):
        w.write('%x %s\n' % (s['Address'], 'mi_' + clean(s['Name'])))
print('ok', len(seen))
