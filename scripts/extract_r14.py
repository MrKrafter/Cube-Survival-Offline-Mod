"""Extract the TextAsset "r14" (game references: items, recipes, locations) from your own copy of Cube Survival 1.0.4.
The offline server in libcubefix.so serves it as /refs; patch_refs.py then adds the mod menu actions to it.

usage: python -I extract_r14.py [data dir ...] [-o textassets/r14.bytes]
Without data dirs it looks in in/obb/assets/bin/Data and in/apk/assets/bin/Data (see README, build step 1)."""
import os
import sys

import UnityPy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    args = sys.argv[1:]
    out = os.path.join(ROOT, 'textassets', 'r14.bytes')
    if '-o' in args:
        i = args.index('-o')
        out = args[i + 1]
        del args[i:i + 2]
    dirs = args or [os.path.join(ROOT, 'in', 'obb', 'assets', 'bin', 'Data'),
                    os.path.join(ROOT, 'in', 'apk', 'assets', 'bin', 'Data')]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for obj in UnityPy.load(d).objects:
            if obj.type.name != 'TextAsset':
                continue
            asset = obj.read()
            if asset.m_Name != 'r14':
                continue
            data = asset.m_Script
            data = data.encode('utf-8', 'surrogateescape') if isinstance(data, str) else bytes(data)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'wb') as f:
                f.write(data)
            print('r14: %d bytes from %s -> %s' % (len(data), d, out))
            return
    sys.exit('TextAsset r14 not found; unpack the APK to in/apk and the OBB to in/obb first')


if __name__ == '__main__':
    main()
