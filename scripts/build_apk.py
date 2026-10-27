"""Build the offline Cube Survival APK: libcubefix (fake server), smali patch (apktool), OBB data merged into assets,
zipalign, sign.  usage: build_apk.py [--keep-x86] [--rec]
--rec: a copy under another package name (own save, installs next to the main game), for recording videos"""
import os, sys, subprocess, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_unity

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')


def env_path(name, default=None):
    v = os.environ.get(name, default)
    if not v:
        sys.exit('set the %s environment variable (see "Building it yourself" in README.md)' % name)
    return v.replace('\\', '/')


JDK = env_path('CUBE_JDK')                  # JDK 17+ home
BT = env_path('CUBE_BUILD_TOOLS')           # Android SDK build-tools dir (zipalign, apksigner, d8)
APKTOOL = env_path('CUBE_APKTOOL', R + '/toolchain/apktool.jar')
KEYSTORE = env_path('CUBE_KEYSTORE', R + '/signing/cube.keystore')
OUT = R + '/build'
OBB = R + '/in/obb'
FINAL = R + '/out/CubeSurvival_offline_1.0.4.apk'
ENV = dict(os.environ, JAVA_HOME=JDK, PATH=JDK + '/bin;' + os.environ['PATH'])
# Unity streams these from the APK by offset, so they must not be deflated
STORED_EXT = ('.resource', '.ress', '.resS', '.unity3d', '.mp4', '.bank')
PACKAGE = 'cube.survival.adventure'
REC_PACKAGE = PACKAGE + '.rec'
REC_LABEL = 'Cube Survival REC'
REC_FINAL = R + '/out/CubeSurvival_offline_1.0.4_rec.apk'


def run(cmd, **kw):
    print('>', ' '.join(cmd))
    subprocess.run(cmd, check=True, env=ENV, **kw)


def rec_project():
    """apktool project for the --rec copy: own manifest and apktool.yml, everything else linked from apktool_cube."""
    src, dst = R + '/apktool_cube', OUT + '/apktool_rec'
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(src):
        p, q = os.path.join(src, name), os.path.join(dst, name)
        if name in ('AndroidManifest.xml', 'apktool.yml', 'build') or not os.path.isdir(p) or os.path.exists(q):
            continue
        subprocess.run(['cmd', '/c', 'mklink', '/J', q.replace('/', '\\'), p.replace('/', '\\')], check=True,
                       stdout=subprocess.DEVNULL)
    with open(src + '/AndroidManifest.xml', encoding='utf-8') as f:
        m = f.read()
    # permissions and provider authorities must be unique per device
    m = m.replace('"%s.gcm.permission' % PACKAGE, '"%s.gcm.permission' % REC_PACKAGE)
    m = m.replace('android:authorities="com.facebook.app.FacebookContentProvider197282321092832"',
                  'android:authorities="%s.FacebookContentProvider"' % REC_PACKAGE)
    m = m.replace('android:label="@string/app_name"', 'android:label="%s"' % REC_LABEL)
    with open(dst + '/AndroidManifest.xml', 'w', encoding='utf-8') as f:
        f.write(m)
    with open(src + '/apktool.yml', encoding='utf-8') as f:
        yml = f.read()
    # aapt renames the package but keeps the resource package and absolute class names
    if 'renameManifestPackage' not in yml:
        yml = yml.replace('packageInfo:', 'packageInfo:\n  renameManifestPackage: %s' % REC_PACKAGE, 1)
    with open(dst + '/apktool.yml', 'w', encoding='utf-8') as f:
        f.write(yml)
    return dst


def main():
    rec = '--rec' in sys.argv
    final = REC_FINAL if rec else FINAL
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.dirname(final), exist_ok=True)
    run([sys.executable, R + '/scripts/patch_refs.py'])
    run(['powershell', '-NoProfile', '-File', R + '/cubefix/build.ps1'])
    base = OUT + '/apktool.apk'
    project = rec_project() if rec else R + '/apktool_cube'
    run([JDK + '/bin/java.exe', '-jar', APKTOOL, 'b', '-f', project, '-o', base])
    unsigned = OUT + '/unsigned.apk'
    keep_x86 = '--keep-x86' in sys.argv
    with zipfile.ZipFile(base) as zi, zipfile.ZipFile(unsigned, 'w') as zo:
        for e in zi.infolist():
            if e.filename.startswith('META-INF/') or (e.filename.startswith('lib/x86/') and not keep_x86):
                continue
            body = zi.read(e.filename)
            if e.filename == 'lib/armeabi-v7a/libunity.so':
                body = patch_unity.patch(body)
            zo.writestr(e, body, compress_type=e.compress_type)
        zo.write(R + '/cubefix/libcubefix.so', 'lib/armeabi-v7a/libcubefix.so', zipfile.ZIP_DEFLATED)
        if keep_x86:
            print('warning: x86 build has no libcubefix, it will not start')
        for root, dirs, files in os.walk(OBB):
            for f in sorted(files):
                p = os.path.join(root, f)
                name = os.path.relpath(p, OBB).replace('\\', '/')
                ct = zipfile.ZIP_STORED if f.endswith(STORED_EXT) else zipfile.ZIP_DEFLATED
                zo.write(p, name, ct)
    aligned = OUT + '/aligned.apk'
    run([BT + '/zipalign.exe', '-f', '-p', '4', unsigned, aligned])
    ks = KEYSTORE
    if not os.path.exists(ks):
        os.makedirs(os.path.dirname(ks), exist_ok=True)
        run([JDK + '/bin/keytool.exe', '-genkeypair', '-keystore', ks, '-storepass', 'cubesurv', '-keypass', 'cubesurv',
             '-alias', 'cube', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
             '-dname', 'CN=Cube Survival Offline, O=Fan patch, C=RU'])
    run(['cmd', '/c', BT.replace('/', '\\') + '\\apksigner.bat', 'sign', '--ks', ks, '--ks-pass', 'pass:cubesurv',
         '--key-pass', 'pass:cubesurv', '--ks-key-alias', 'cube', '--out', final, aligned])
    print('APK:', final, os.path.getsize(final) // 1024, 'KB')


if __name__ == '__main__':
    main()
