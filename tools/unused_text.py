"""List localization terms (I2 source in the OBB data) that nothing uses: not a string in the references (r14) and not
a string literal in the code (global-metadata.dat). Prints them grouped by prefix with their Russian text.
Keys built at run time (prefix + id) can look unused, so the output is a lead, not proof.
usage: unused_text.py [out.txt]"""
import collections, json, os, re, struct, sys

LOC = r'D:\CubeSurvival\in\obb\assets\bin\Data\209a2243dbc6046478ffa6495f566040'
REFS = r'D:\CubeSurvival\cmp\r14.json'
META = r'D:\CubeSurvival\in\apk\assets\bin\Data\Managed\Metadata\global-metadata.dat'
TERM = re.compile(rb'(?s)(.{4})([A-Za-z0-9_\-./ ]{3,120})\x00{0,3}')


def read_str(b, off):
    n = struct.unpack_from('<i', b, off)[0]
    if not 0 <= n < 20000:
        raise ValueError
    return b[off + 4:off + 4 + n].decode('utf-8', 'replace'), off + 4 + ((n + 3) & ~3)


def terms(blob):
    out = {}
    for m in re.finditer(rb'[A-Za-z][A-Za-z0-9_\-.]{2,120}', blob):
        k = m.group()
        start = m.start() - 4
        if start < 0 or struct.unpack_from('<i', blob, start)[0] != len(k):
            continue
        off = m.start() + ((len(k) + 3) & ~3)
        try:
            off += 4  # TermType
            _, off = read_str(blob, off)
            if struct.unpack_from('<i', blob, off)[0] != 16:
                continue
            en, off = read_str(blob, off + 4)
            ru, off = read_str(blob, off)
        except (ValueError, struct.error):
            continue
        out[k.decode()] = (ru, en)
    return out


def refs_strings(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(k)
            refs_strings(v, acc)
    elif isinstance(o, list):
        for v in o:
            refs_strings(v, acc)
    elif isinstance(o, str):
        acc.add(o)


def main():
    T = terms(open(LOC, 'rb').read())
    used = set()
    refs_strings(json.load(open(REFS, encoding='utf-8')), used)
    meta = open(META, 'rb').read()
    unused = [k for k in T if k not in used and k.encode() not in meta]
    # UI prefabs and scenes name their terms in Localize components
    for d in (os.path.dirname(LOC), os.path.dirname(os.path.dirname(META))[:-len('Managed')]):
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and p != LOC and unused:
                data = open(p, 'rb').read()
                unused = [k for k in unused if k.encode() not in data]
    # a key that is a known prefix + something used is probably built at run time
    groups = collections.defaultdict(list)
    for k in sorted(unused):
        groups[k.split('_')[0]].append(k)
    lines = ['terms %d, unused %d' % (len(T), len(unused))]
    for g, ks in sorted(groups.items(), key=lambda x: -len(x[1])):
        lines.append('== %s (%d)' % (g, len(ks)))
        for k in ks:
            ru, en = T[k]
            lines.append('  %s | %s | %s' % (k, ru.replace('\n', ' ')[:90], en.replace('\n', ' ')[:90]))
    text = '\n'.join(lines)
    if len(sys.argv) > 1:
        open(sys.argv[1], 'w', encoding='utf-8').write(text)
    print(lines[0])


if __name__ == '__main__':
    main()
