"""Print the JSON at a slash path in r14 (e.g. global_maps/0/code_locations).  usage: refs_get.py <path> [max_chars]"""
import json, sys

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
o = R
for part in sys.argv[1].strip('/').split('/'):
    o = o[int(part)] if isinstance(o, list) else o[part]
s = json.dumps(o, ensure_ascii=False, indent=1)
print(s[:int(sys.argv[2]) if len(sys.argv) > 2 else 6000])
