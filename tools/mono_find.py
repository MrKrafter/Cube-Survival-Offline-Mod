"""Find MonoBehaviours whose script class matches a regex in the APK's Unity data and print their raw field bytes.
Player builds strip MonoBehaviour type trees, so the fields are printed raw (after m_Name) for manual decoding.
usage: mono_find.py <class regex> [max bytes]"""
import os, re, struct, sys
import UnityPy

DATA = r'D:\CubeSurvival\in\apk\assets\bin\Data'
pat = re.compile(sys.argv[1])
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 96

env = UnityPy.load(DATA)  # the whole dir, so sharedassets0.assets.split* are joined
for af in env.assets:
    name = af.name
    for obj in af.objects.values():
        if obj.type.name != 'MonoBehaviour':
            continue
        try:
            mb = obj.read(check_read=False)
            script = mb.m_Script.read()
        except Exception:
            continue
        if not pat.search(script.m_ClassName):
            continue
        raw = obj.get_raw_data()
        # m_GameObject(12) m_Enabled(4) m_Script(12) m_Name(len+chars, aligned)
        n = struct.unpack_from('<i', raw, 28)[0]
        off = 32 + ((n + 3) & ~3)
        body = raw[off:off + limit]
        go = mb.m_GameObject.read().m_Name if mb.m_GameObject else ''
        print(f'{name} path={obj.path_id} {script.m_ClassName} go={go!r} size={len(raw) - off}')
        print('   ', body.hex(' ', 4))
