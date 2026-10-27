"""Print decompiled functions (name substring match) with il2cpp boilerplate stripped.
usage: show.py <file.c> <substr> [<substr>...]"""
import re, sys

text = open(sys.argv[1], encoding='utf-8').read()
parts = re.split(r'^// ==== ', text, flags=re.M)[1:]
DECL = re.compile(r'^\s+(undefined\d?|int|uint|float|double|bool|char|short|ushort|byte|longlong|ulonglong|code)[0-9 *]+\w+(\s*\[\d+\])?;$')
for want in sys.argv[2:]:
    for p in parts:
        head = p.split('\n', 1)[0]
        if want not in head:
            continue
        out = []
        lines = p.split('\n')
        skip_init = 0
        for ln in lines[1:]:
            s = ln.strip()
            if DECL.match(ln) or s.startswith('/* WARNING'):
                continue
            if 'sub_230e4ac(' in s or re.match(r'^\*&G_[0-9a-f]+ = 1;$', s) or re.match(r'^if \(\*&G_[0-9a-f]+ == .\\0.\) \{$', s):
                continue
            if s.endswith('+ 0xb2) & 1) != 0) &&') or s.endswith('+ 0x60) == 0)) {') or s == 'sub_2326ec0();':
                continue
            if 'func_0x0111438c()' in s or re.search(r'= (\(int \*\))?sub_23466f8\(\);$', s):
                out.append('  <throw NRE / tail>')
                break
            out.append(ln)
        txt = '\n'.join(out)
        txt = re.sub(r'\n\s*\}\n(\s*\}\n)', r'\n\1', txt)
        print('// ==== ' + head)
        print(re.sub(r'\n{3,}', '\n\n', txt))
