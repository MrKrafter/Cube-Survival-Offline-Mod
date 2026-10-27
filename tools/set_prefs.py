"""Write the mod menu prefs on the emulator and restart the game.  usage: set_prefs.py <opt ids on...> [speed=N]"""
import os, subprocess, sys

PKG = 'cube.survival.adventure'
serial = os.environ.get('ANDROID_SERIAL', 'emulator-5554')
on = [int(a) for a in sys.argv[1:] if a.isdigit()]
speed = next((int(a[6:]) for a in sys.argv[1:] if a.startswith('speed=')), 10)
lines = ["<?xml version='1.0' encoding='utf-8' standalone='yes' ?>", '<map>']
lines += ['    <boolean name="opt%d" value="%s" />' % (i, 'true' if i in on else 'false') for i in range(1, 17)]
lines += ['    <int name="speed" value="%d" />' % speed, '</map>', '']
local = r'D:\CubeSurvival\avd\cubemod.xml'
with open(local, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines))

def adb(*a):
    return subprocess.run(['adb', '-s', serial] + list(a), capture_output=True, text=True).stdout

adb('shell', 'am', 'force-stop', PKG)
adb('push', local, '/data/local/tmp/cubemod.xml')
dst = '/data/data/%s/shared_prefs/cubemod.xml' % PKG
print(adb('shell', "su 0 sh -c 'cp /data/local/tmp/cubemod.xml %s && chown $(stat -c %%u /data/data/%s):$(stat -c %%g /data/data/%s) %s && chmod 660 %s && cat %s'" % (dst, PKG, PKG, dst, dst, dst)))
