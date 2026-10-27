"""Print every global map point: open/walk requirement, levels it loads, view flags (tier, icons).
usage: map_points.py"""
import json

REFS = r'D:\CubeSurvival\cmp\r14.json'


def req(r, depth=0):
    if not isinstance(r, dict):
        return str(r)
    t = r.get('type')
    if t in ('and', 'or'):
        return t + '(' + ', '.join(req(x, depth + 1) for x in r['requirements']) + ')'
    if t == 'not':
        return 'not ' + req(r['requirement'], depth + 1)
    if t in ('resource', 'static_resource', 'expiring_resource'):
        return '%s>=%s' % (r['resource'], r.get('amount'))
    if t == 'level':
        return 'lvl%s' % r['level']
    if t == 'operation':
        return '(%s %s %s)' % (req(r['first']), r['operation'], req(r['second']))
    if t == 'single':
        return str(r['amount'])
    if t == 'external':
        return 'ext:' + r['id']
    rest = {k: v for k, v in r.items() if k != 'type'}
    return t + (json.dumps(rest, ensure_ascii=False)[:80] if rest else '')


def main():
    R = json.load(open(REFS, encoding='utf-8'))
    G = R['global_maps']['0']
    V = R['global_maps_view']['0']['locations']
    for lid, loc in G['locations'].items():
        v = V.get(lid, {})
        flags = {k: v[k] for k in v if k not in ('name', 'stats', 'speeches', 'speech_interval', 'speech_max',
                                                 'large_icon', 'description')}
        print('%-22s req=%s | walk=%s | levels=%s | price=%s | view=%s' % (
            lid, req(loc.get('requirement')), req(loc.get('walk_requirement')), loc.get('levels'),
            req(loc.get('price')) if 'price' in loc else '-', json.dumps(flags, ensure_ascii=False)[:160]))


if __name__ == '__main__':
    main()
