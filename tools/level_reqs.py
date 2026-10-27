"""Count requirements of type "level" in r14 per top-level section, with sample paths.  usage: level_reqs.py"""
import collections, json

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
hits = collections.defaultdict(list)


def walk(o, path):
    if isinstance(o, dict):
        if o.get('type') == 'level':
            hits[path.split('/')[1]].append(path)
        for k, v in o.items():
            walk(v, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f'{path}/{i}')


walk(R, '')
for sec, paths in sorted(hits.items(), key=lambda x: -len(x[1])):
    print(f'{sec:24} {len(paths):5}  {paths[0]}')
