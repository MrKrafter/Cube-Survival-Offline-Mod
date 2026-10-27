"""Export the game's Font assets (TTF/OTF data) from the Unity data (apk + obb).
usage: export_fonts.py <out dir>"""
import os, re, sys
import UnityPy

DIRS = [r'D:\CubeSurvival\in\obb\assets\bin\Data', r'D:\CubeSurvival\in\apk\assets\bin\Data']
UnityPy.config.FALLBACK_UNITY_VERSION = '2017.2.0p4'


def main():
    out = sys.argv[1]
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
        if obj.type.name != 'Font':
            continue
        try:
            data = obj.read()
        except Exception:
            continue
        raw = bytes(getattr(data, 'm_FontData', b'') or b'')
        print(data.m_Name, len(raw))
        if raw:
            ext = '.otf' if raw[:4] == b'OTTO' else '.ttf'
            open(os.path.join(out, re.sub(r'[^A-Za-z0-9_.-]', '_', data.m_Name) + ext), 'wb').write(raw)


if __name__ == '__main__':
    main()
