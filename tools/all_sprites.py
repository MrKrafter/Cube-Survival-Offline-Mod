"""Check inventory_stack_view sprite names against the game's asset files (APK assets + OBB data, where every
sprite sits in its own GUID-named file); a missing sprite shows as a white square in the inventory.
usage: all_sprites.py [item ...]   (no items: every sprite; prints the missing ones)"""
import json, os, sys

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
views = R['inventory_stack_view']
blob = b'\n'.join(open(os.path.join(r, f), 'rb').read()
                  for top in (r'D:\CubeSurvival\in\obb\assets', r'D:\CubeSurvival\apktool_cube\assets\bin\Data')
                  for r, _, fs in os.walk(top) for f in fs if not f.endswith(('.dll', '.json', '.xml', '.txt')))


def present(sprite):
    # sprite names are stored as length-prefixed strings: u32 length + name
    name = sprite.split('/')[-1].encode()
    return len(name).to_bytes(4, 'little') + name in blob


if sys.argv[1:]:
    for item in sys.argv[1:]:
        s = views.get(item, {}).get('sprite')
        print(f'{item:32} {s!s:40} {"ok" if s and present(s) else "MISSING"}')
else:
    sprites = sorted({v['sprite'] for v in views.values() if isinstance(v, dict) and v.get('sprite')})
    missing = [s for s in sprites if not present(s)]
    print(len(sprites), 'sprites,', len(missing), 'missing')
    print(' '.join(missing))
