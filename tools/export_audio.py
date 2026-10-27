"""List the game's AudioClips (name, length) and export those whose names match a regex as wav/ogg.
usage: export_audio.py <out dir> [name regex] [min seconds]"""
import os, re, sys
import UnityPy

DIRS = [r'D:\CubeSurvival\in\obb\assets\bin\Data', r'D:\CubeSurvival\in\apk\assets\bin\Data']
UnityPy.config.FALLBACK_UNITY_VERSION = '2017.2.0p4'


def main():
    out = sys.argv[1]
    rx = re.compile(sys.argv[2] if len(sys.argv) > 2 else '.', re.I)
    min_len = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    os.makedirs(out, exist_ok=True)
    env = UnityPy.Environment()
    for d in DIRS:
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p):
                try:
                    env.load_file(p)
                except Exception:
                    pass
    for obj in env.objects:
        if obj.type.name != 'AudioClip':
            continue
        try:
            clip = obj.read()
        except Exception:
            continue
        length = getattr(clip, 'm_Length', 0) or 0
        if not rx.search(clip.m_Name) or length < min_len:
            continue
        print('%-40s %6.1f s' % (clip.m_Name, length))
        try:
            for name, data in clip.samples.items():
                open(os.path.join(out, re.sub(r'[^A-Za-z0-9_.-]', '_', name)), 'wb').write(data)
        except Exception as e:
            print('  export failed:', e)


if __name__ == '__main__':
    main()
