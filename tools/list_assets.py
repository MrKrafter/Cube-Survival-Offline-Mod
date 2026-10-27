"""List TextAsset / MonoBehaviour names in the game's Unity data (apk + obb), optionally dump TextAssets."""
import sys, os, collections
import UnityPy

dirs = sys.argv[1].split(';')
out = sys.argv[2] if len(sys.argv) > 2 else None
UnityPy.config.FALLBACK_UNITY_VERSION = '2017.2.0p4'
env = UnityPy.Environment()
for d in dirs:
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            if '.split' in f and not f.endswith('.split0'):
                continue
            try:
                env.load_file(p if '.split' not in f else p[:-len('.split0')])
            except Exception as e:
                pass
types = collections.Counter()
for obj in env.objects:
    types[obj.type.name] += 1
print(types.most_common())
for obj in env.objects:
    if obj.type.name == 'TextAsset':
        data = obj.read()
        name = data.m_Name
        raw = data.m_Script
        if isinstance(raw, str):
            raw = raw.encode('utf-8', 'surrogateescape')
        print('TA', name, len(raw))
        if out:
            os.makedirs(out, exist_ok=True)
            with open(os.path.join(out, name.replace('/', '_') + '.bytes'), 'wb') as fh:
                fh.write(raw)
