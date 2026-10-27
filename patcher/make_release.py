"""Make the patcher release zip (for the developer, after a normal build; see README).
Needs: in/apk (unpacked original APK), build/apktool.apk (from scripts/build_apk.py),
cubefix/libcubefix_slot.so (cubefix/build.ps1 -Slot) and pip install bsdiff4.

usage: python make_release.py [version]   -> out/Cube_Survival_Offline_Mod_patcher_<version>.zip
The zip holds only our code and a binary diff of classes.dex: no game files."""
import hashlib
import json
import os
import sys
import zipfile

import bsdiff4

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get('CUBE_WORK', R)  # where in/, build/ and out/ are (the repo root by default)
HERE = os.path.join(R, 'patcher')
DATA = os.path.join(HERE, 'data')
FILES = [('patcher/cube_patcher.py', 'cube_patcher.py'), ('patcher/apksign.py', 'apksign.py'),
         ('patcher/bspatch.py', 'bspatch.py'), ('scripts/patch_refs.py', 'patch_refs.py'),
         ('scripts/refs_codec.py', 'refs_codec.py'), ('scripts/lz4_pure.py', 'lz4_pure.py'),
         ('scripts/patch_unity.py', 'patch_unity.py'), ('patcher/patch.bat', 'patch.bat'),
         ('patcher/README.txt', 'README.txt'), ('LICENSE', 'LICENSE.txt')]


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else '1.0'
    src_dex = open(os.path.join(W, 'in', 'apk', 'classes.dex'), 'rb').read()
    dst_dex = zipfile.ZipFile(os.path.join(W, 'build', 'apktool.apk')).read('classes.dex')
    libunity = open(os.path.join(W, 'in', 'apk', 'lib', 'armeabi-v7a', 'libunity.so'), 'rb').read()
    slot = open(os.path.join(R, 'cubefix', 'libcubefix_slot.so'), 'rb').read()
    assert b'CUBEREFSLOT1' in slot, 'build libcubefix_slot.so with cubefix/build.ps1 -Slot'
    os.makedirs(DATA, exist_ok=True)
    patch = bsdiff4.diff(src_dex, dst_dex)
    meta = {'classes_dex_src': sha256(src_dex), 'classes_dex_dst': sha256(dst_dex),
            'libunity_src': sha256(libunity), 'libcubefix_slot': sha256(slot)}
    with open(os.path.join(DATA, 'classes.dex.bsdiff'), 'wb') as f:
        f.write(patch)
    with open(os.path.join(DATA, 'libcubefix_slot.so'), 'wb') as f:
        f.write(slot)
    with open(os.path.join(DATA, 'patch.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=1)
    top = 'Cube_Survival_Offline_Mod_patcher_' + version
    out = os.path.join(W, 'out', top + '.zip')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src, dst in FILES:
            z.write(os.path.join(R, src), top + '/' + dst)
        for f in ('classes.dex.bsdiff', 'libcubefix_slot.so', 'patch.json'):
            z.write(os.path.join(DATA, f), top + '/data/' + f)
    print('classes.dex patch: %d bytes' % len(patch))
    print(out, os.path.getsize(out), 'bytes, SHA-256', sha256(open(out, 'rb').read()))


if __name__ == '__main__':
    main()
