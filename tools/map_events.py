"""List global map events, event groups and locations from r14.  usage: map_events.py"""
import json

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))
gm = R['global_maps']
g = gm['0'] if '0' in gm else next(iter(gm.values()))
print('keys:', list(g.keys()))
ev = g.get('events', {})
print('events:', len(ev))
for k, v in ev.items():
    print(' ', k, v.get('type'), 'lvl', v.get('level'), 'locs', len(v.get('locations', [])),
          json.dumps(v.get('player_requirement'), ensure_ascii=False)[:100])
print('groups:', json.dumps(g.get('event_groups'), ensure_ascii=False)[:2000])
locs = g.get('locations', {})
print('locations:', len(locs))
for k, v in locs.items():
    print(' ', k, json.dumps({x: v[x] for x in v if x in ('requirement', 'code_location', 'type', 'tier')}, ensure_ascii=False)[:160])
