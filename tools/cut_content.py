"""Look for content present in the references but unreachable in play: items no recipe/loot/reward/shop
mentions, researches and recipes behind a "false" requirement, global map locations/events gated off.
usage: cut_content.py"""
import json, re, collections

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))


def strings(o, skip_path, path=''):
    """Yield (path, string) for every string value and key, outside skip_path."""
    if path.startswith(skip_path):
        return
    if isinstance(o, dict):
        for k, v in o.items():
            yield path, str(k)
            yield from strings(v, skip_path, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, skip_path, '%s[%d]' % (path, i))
    elif isinstance(o, str):
        yield path, o


# index: string -> set of top-level sections where it appears
where = collections.defaultdict(set)
for p, s in strings(R, '\0'):
    where[s].add(p.split('/')[1] if p.count('/') else p)

VIEW = re.compile(r'_views?$|^localization|^texts?$')


def users(key, own):
    return sorted(s for s in where.get(key, ()) if s != own and not VIEW.search(s))


print('== sections mentioning inventory stacks (how many stacks each)')
hist = collections.Counter(s for k in R['inventory_stacks'] for s in users(k, 'inventory_stacks'))
print(hist.most_common())
# A stack is obtainable when some loot, recipe, reward, shop or trader source names it.
SOURCES = re.compile(r'loot|recipe|reward|action|shop|trader|gacha|location|drop|chest|box|craft|research|event')
orphans = [k for k in R['inventory_stacks'] if not any(SOURCES.search(s) for s in users(k, 'inventory_stacks'))]
print('\n== inventory_stacks with no loot/recipe/reward/shop source:', len(orphans), 'of', len(R['inventory_stacks']))
for k in orphans:
    print(' ', k, users(k, 'inventory_stacks'))


def false_gated(section, fields=('requirement',)):
    out = []
    for k, v in R.get(section, {}).items():
        if not isinstance(v, dict):
            continue
        for f in fields:
            r = v.get(f)
            if isinstance(r, dict) and r.get('type') == 'false':
                out.append('%s(%s)' % (k, f))
    return out


for sec in ('researches', 'recipes', 'actions', 'workbench_recipes', 'trader_recipes'):
    g = false_gated(sec)
    print('\n== %s with requirement false: %d' % (sec, len(g)))
    print(' '.join(g[:200]))

print('\n== researches nothing else mentions')
print(' '.join(k for k in R.get('researches', {}) if not users(k, 'researches')))

print('\n== recipes whose reward stack is an orphan item')
orph = set(orphans)
for k, v in R.get('recipes', {}).items():
    st = (v.get('reward') or {}).get('stack')
    if st in orph:
        print(k, st)

gm = R.get('global_maps') or R.get('global_map') or {}
print('\n== global map sections:', [k for k in R if 'global' in k])
