"""Export Texture2D/Sprite images whose names match a regex (or are big) from the game's Unity data (apk + obb).
usage: export_art.py <out dir> <name regex> [min side]"""
import os, re, sys
import UnityPy

DIRS = [r'D:\CubeSurvival\in\obb\assets\bin\Data', r'D:\CubeSurvival\in\apk\assets\bin\Data']
UnityPy.config.FALLBACK_UNITY_VERSION = '2017.2.0p4'


def main():
    out, rx = sys.argv[1], re.compile(sys.argv[2], re.I)
    min_side = int(sys.argv[3]) if len(sys.argv) > 3 else 0
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
    seen = set()
    for obj in env.objects:
        if obj.type.name not in ('Texture2D', 'Sprite'):
            continue
        try:
            data = obj.read()
            name = data.m_Name
        except Exception:
            continue
        if not rx.search(name) or (obj.type.name, name) in seen:
            continue
        try:
            img = data.image
        except Exception:
            continue
        if min(img.size) < min_side:
            continue
        seen.add((obj.type.name, name))
        safe = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
        img.save(os.path.join(out, '%s_%s.png' % (obj.type.name[0], safe)))
        print(obj.type.name, name, img.size)


if __name__ == '__main__':
    main()
