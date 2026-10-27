"""Print classes from dump.cs compactly: fields + methods with RVA.  usage: cls.py <ClassName> [...]
A name matches the exact class name (nested classes as Outer.Inner)."""
import re, sys

text = open(r'D:\CubeSurvival\dump\dump.cs', encoding='utf-8').read()
HDR = re.compile(r'^(?:// Namespace: (?P<ns>.*)\n)(?:\[.*\n)*(?P<decl>(?:public |internal |private |protected )?(?:sealed |abstract |static )*(?:class|struct|interface|enum) (?P<name>[^\s:<]+(?:<[^>]*>)?)[^\n]*)\n\{', re.M)
for want in sys.argv[1:]:
    for m in HDR.finditer(text):
        name = re.sub(r'<.*', '', m.group('name'))
        if name != want:
            continue
        end = text.index('\n}\n', m.end())
        body = text[m.end():end].split('\n')
        print('//', m.group('ns'), '|', m.group('decl'))
        rva = None
        for ln in body:
            s = ln.strip()
            r = re.match(r'// RVA: (0x[0-9A-F]+)', s)
            if r:
                rva = r.group(1)
                continue
            if not s or s.startswith('[') or s.startswith('//'):
                continue
            if '(' in s and rva:
                print('  %-10s %s' % (rva, s.rstrip(' {}')))
                rva = None
            elif '(' not in s:
                print('  ' + ' ' * 11 + s)
        print()
