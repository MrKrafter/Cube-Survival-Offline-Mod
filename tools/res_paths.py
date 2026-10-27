"""List Resources.Load paths (ResourceManager container in globalgamemanagers) matching a regex.
usage: res_paths.py <regex>"""
import re, sys
import UnityPy

env = UnityPy.load(r'D:\CubeSurvival\in\apk\assets\bin\Data\globalgamemanagers')
pat = re.compile(sys.argv[1], re.I)
for obj in env.objects:
    if obj.type.name != 'ResourceManager':
        continue
    tree = obj.read_typetree()
    for path, _ in tree['m_Container']:
        if pat.search(path):
            print(path)
