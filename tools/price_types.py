"""Count price types (any key containing "price") per r14 section.  usage: price_types.py <section> [<section>...]"""
import collections, json, sys

R = json.load(open(r'D:\CubeSurvival\cmp\r14.json', encoding='utf-8'))


def walk(o, c, key=''):
    if isinstance(o, dict):
        if 'price' in key and 'type' in o:
            c[key + ':' + str(o['type'])] += 1
            if o['type'] == 'static_resource':
                c['  resource ' + str(o.get('resource'))] += 1
        for k, v in o.items():
            walk(v, c, k)
    elif isinstance(o, list):
        for v in o:
            walk(v, c, key)


for sec in sys.argv[1:]:
    c = collections.Counter()
    walk(R.get(sec, {}), c)
    print(sec, dict(c))
