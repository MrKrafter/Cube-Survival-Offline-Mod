"""Cube Survival Offline Mod patcher: turns your own copy of Cube Survival: LDoE 1.0.4 (APK + OBB) into the offline
build with the mod menu. Pure Python 3.8+, no packages to install, works on Windows, Linux, macOS and Termux.

usage: python cube_patcher.py [files...] [-o output.apk]
files: the game APK and OBB (main.26.cube.survival.adventure.obb), or archives that contain them (.xapk, .zip).
Without files it looks next to the patcher and in the current folder."""
import hashlib
import io
import json
import os
import struct
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), 'scripts')]  # release zip: flat; repo: ../scripts

import apksign
import bspatch
import patch_refs
import patch_unity

DATA = os.path.join(HERE, 'data')
KEY_FILE = os.path.join(HERE, 'cube_patcher_key.json')
OUT_NAME = 'CubeSurvival_offline_1.0.4.apk'

# Google Play release 1.0.4 (versionCode 26). Other copies work too, as long as the files below match.
KNOWN_APK_SHA256 = '15499be6a2d0eefeb66496b394cdfeb5c5828278fc5c7369e594004d15ecb03b'
KNOWN_OBB_SHA256 = '7d46ce31eb8224ac25d32cf2a9540b014f553e1cac60e0efc5d8dbe2775c1578'
OBB_NAME = 'main.26.cube.survival.adventure.obb'
LIBUNITY = 'lib/armeabi-v7a/libunity.so'
# TextAsset r14 (items, recipes, locations) inside the OBB; the offline server serves it with the mod menu actions
R14_FILE = 'assets/bin/Data/0f437f9285f6c4bcebd29b616d503506'
R14_OFFSET, R14_SIZE = 4108, 228682
R14_SHA256 = '5a9487418df47534e255fc9ded955b56a21805210c97270460e9b827a3fac88e'
# Unity streams these straight from the APK by offset, so they stay uncompressed (same list as scripts/build_apk.py)
STORED_EXT = ('.resource', '.ress', '.resS', '.unity3d', '.mp4', '.bank')


def say(ru, en):
    print(ru)
    print('  ' + en)


class Fail(Exception):
    pass


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def raw_entry(zf, info):
    """An entry exactly as stored (still compressed), so 80 MB of game data is copied without recompressing."""
    fp = zf.fp
    fp.seek(info.header_offset)
    head = fp.read(30)
    if head[:4] != b'PK\x03\x04':
        raise Fail('broken zip entry ' + info.filename)
    n, m = struct.unpack('<HH', head[26:30])
    fp.seek(info.header_offset + 30 + n + m)
    return fp.read(info.compress_size)


def copy_entry(zf, info, name=None):
    data = zf.read(info)  # also checks the CRC; the uncompressed data is needed for the v1 digests anyway
    if info.compress_type not in (0, 8):
        return apksign.entry(name or info.filename, data)
    return {'name': name or info.filename, 'method': info.compress_type, 'raw': raw_entry(zf, info),
            'crc': info.CRC, 'size': info.file_size, 'sha1': hashlib.sha1(data).digest()}


def classify(zf):
    names = set(zf.namelist())
    if 'AndroidManifest.xml' in names and 'classes.dex' in names:
        return 'apk'
    if R14_FILE in names:
        return 'obb'
    return None


def find_inputs(paths):
    """-> (apk ZipFile, apk sha256, obb ZipFile, obb sha256); looks one level into archives (.xapk, zipped OBB)."""
    found = {}

    def visit(label, data):
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            return
        kind = classify(zf)
        if kind and kind not in found:
            found[kind] = (zf, sha256(data), label)
            return
        if kind:
            return
        for info in zf.infolist():
            low = info.filename.lower()
            if low.endswith('.apk') or low.endswith('.obb'):
                visit(label + ' -> ' + info.filename, zf.read(info))

    for p in paths:
        with open(p, 'rb') as f:
            visit(os.path.basename(p), f.read())
        if len(found) == 2:
            break
    if 'apk' not in found:
        raise Fail('APK игры не найден. / The game APK was not found.')
    if 'obb' not in found:
        raise Fail('OBB игры (%s) не найден. / The game OBB (%s) was not found.' % (OBB_NAME, OBB_NAME))
    return found['apk'], found['obb']


def default_paths():
    out = []
    for d in dict.fromkeys([HERE, os.getcwd()]):
        for f in sorted(os.listdir(d)):
            low = f.lower()
            if f == OUT_NAME or not low.endswith(('.apk', '.obb', '.xapk', '.zip', '.apks')):
                continue
            if low.startswith('cubesurvival_offline') or low.startswith('cube_survival_offline_mod_patcher'):
                continue
            out.append(os.path.join(d, f))
    return out


def check(what, got, want):
    if got != want:
        raise Fail('%s не совпадает с версией 1.0.4 (SHA-256 %s). / %s does not match version 1.0.4.'
                   % (what, got, what))


def build(apk, obb, out_path):
    with open(os.path.join(DATA, 'patch.json'), encoding='utf-8') as f:
        meta = json.load(f)

    dex = apk.read('classes.dex')
    check('classes.dex', sha256(dex), meta['classes_dex_src'])
    say('Патчу classes.dex...', 'Patching classes.dex...')
    with open(os.path.join(DATA, 'classes.dex.bsdiff'), 'rb') as f:
        dex = bspatch.apply(dex, f.read())
    check('classes.dex (patched)', sha256(dex), meta['classes_dex_dst'])

    unity = apk.read(LIBUNITY)
    check(LIBUNITY, sha256(unity), meta['libunity_src'])
    unity = patch_unity.patch(unity)

    say('Готовлю данные игры для офлайн-сервера...', 'Preparing the game data for the offline server...')
    r14 = obb.read(R14_FILE)[R14_OFFSET:R14_OFFSET + R14_SIZE]
    check('r14', sha256(r14), R14_SHA256)
    refs = patch_refs.patch(r14)
    with open(os.path.join(DATA, 'libcubefix_slot.so'), 'rb') as f:
        lib = bytearray(f.read())
    check('libcubefix_slot.so', sha256(lib), meta['libcubefix_slot'])
    at = lib.find(b'CUBEREFSLOT1')
    slot, = struct.unpack_from('<I', lib, at + 12)
    if len(refs) > slot:
        raise Fail('refs do not fit the slot: %d > %d' % (len(refs), slot))
    struct.pack_into('<I', lib, at + 16, len(refs))
    lib[at + 20:at + 20 + len(refs)] = refs

    say('Собираю APK...', 'Building the APK...')
    entries = []
    for info in apk.infolist():
        name = info.filename
        if info.is_dir() or name.startswith('META-INF/') or name.startswith('lib/x86/'):
            continue  # old signature; the game has no x86 build of the offline patch
        if name == 'classes.dex':
            entries.append(apksign.entry(name, dex))
        elif name == LIBUNITY:
            entries.append(apksign.entry(name, unity))
        else:
            entries.append(copy_entry(apk, info))
    entries.append(apksign.entry('lib/armeabi-v7a/libcubefix.so', bytes(lib)))
    have = {e['name'] for e in entries}
    for info in obb.infolist():  # the OBB goes inside the APK, so the game needs no separate download
        if info.is_dir() or info.filename in have:
            continue
        e = copy_entry(obb, info)
        if info.filename.endswith(STORED_EXT) and e['method'] != 0:
            e = apksign.entry(info.filename, obb.read(info), compress=False)
        entries.append(e)

    if os.path.exists(KEY_FILE):
        key = apksign.load_key(KEY_FILE)
    else:
        say('Создаю ключ подписи (один раз, несколько секунд)...',
            'Creating a signing key (once, a few seconds)...')
        key = apksign.make_key()
        apksign.save_key(key, KEY_FILE)
    say('Подписываю...', 'Signing...')
    apksign.write_signed(entries, out_path, key)


def main():
    args = sys.argv[1:]
    out = None
    if '-o' in args:
        i = args.index('-o')
        out = args[i + 1]
        del args[i:i + 2]
    if any(a in ('-h', '--help') for a in args):
        print(__doc__)
        return 0
    print('Cube Survival Offline Mod patcher')
    print()
    paths = args or default_paths()
    try:
        (apk, apk_sha, apk_label), (obb, obb_sha, obb_label) = find_inputs(paths)
        say('APK: ' + apk_label, 'SHA-256 ' + apk_sha + (' (Google Play 1.0.4)' if apk_sha == KNOWN_APK_SHA256 else ''))
        say('OBB: ' + obb_label, 'SHA-256 ' + obb_sha + (' (Google Play 1.0.4)' if obb_sha == KNOWN_OBB_SHA256 else ''))
        out = out or os.path.join(os.getcwd(), OUT_NAME)
        t = time.time()
        build(apk, obb, out)
    except Fail as e:
        print()
        print('ОШИБКА / ERROR: %s' % e)
        print('Нужна Cube Survival 1.0.4: APK и %s. Подробности в README.' % OBB_NAME)
        print('You need Cube Survival 1.0.4: the APK and %s. See the README.' % OBB_NAME)
        return 1
    with open(out, 'rb') as f:
        digest = sha256(f.read())
    print()
    say('Готово за %d с: %s' % (time.time() - t, out), 'Done in %d s: %s' % (time.time() - t, out))
    print('SHA-256: ' + digest)
    say('Ключ подписи: %s. Сохраните его: обновить игру можно только сборкой с тем же ключом.' % KEY_FILE,
        'Signing key: %s. Keep it: the game only updates with a build signed by the same key.' % KEY_FILE)
    return 0


if __name__ == '__main__':
    sys.exit(main())
