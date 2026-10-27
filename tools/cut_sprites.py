"""For each cut item of patch_refs.py: print its inventory_stack_view sprite and whether that sprite name occurs in the
game's Unity asset files (a missing one shows as a white square in the inventory).
usage: cut_sprites.py"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patch_refs import CUT_ITEMS

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
DATA = r'D:\CubeSurvival\apktool_cube\assets\bin\Data'
blobs = []
for root, _, files in os.walk(DATA):
    for f in files:
        if not f.endswith(('.dll', '.json', '.xml')):
            blobs.append(open(os.path.join(root, f), 'rb').read())
print('asset files:', len(blobs))
for item in CUT_ITEMS:
    sprite = R['inventory_stack_view'].get(item, {}).get('sprite')
    name = (sprite or '').split('/')[-1].encode()
    found = bool(name) and any(name in b for b in blobs)
    print(f'{item:32} {sprite!s:40} {"ok" if found else "MISSING"}')
