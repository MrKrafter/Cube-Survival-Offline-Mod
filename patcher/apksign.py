"""Write and sign an APK in pure Python: zip with 4-byte aligned stored entries, JAR (v1) and APK Signature Scheme v2.

v1 uses SHA-1 so Android 4.1-4.2 accept it; v2 uses RSA PKCS#1 v1.5 with SHA-256. The key is RSA-2048, generated on
the player's machine (make_key) and kept next to the patcher, so later patched builds install over earlier ones."""
import base64
import hashlib
import json
import os
import secrets
import struct
import zlib

# ---------------------------------------------------------------- RSA


def _is_probable_prime(n, rounds=40):
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        x = pow(secrets.randbelow(n - 3) + 2, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


_SMALL_PRIMES = [p for p in range(3, 2000, 2) if all(p % q for q in range(3, int(p ** 0.5) + 1, 2))]


def _prime(bits, e):
    while True:
        n = secrets.randbits(bits) | (3 << (bits - 2)) | 1  # top two bits set: p*q has the full 2048 bits
        if (n - 1) % e and _is_probable_prime(n):
            return n


def _rsa_keygen(bits=2048, e=65537):
    while True:
        p, q = _prime(bits // 2, e), _prime(bits // 2, e)
        if p != q:
            break
    n = p * q
    d = pow(e, -1, (p - 1) * (q - 1))
    return n, e, d


_DIGEST_INFO = {
    'sha1': bytes.fromhex('3021300906052b0e03021a05000414'),
    'sha256': bytes.fromhex('3031300d060960864801650304020105000420'),
}


def _rsa_sign(key, data, hash_name):
    n, d = key['n'], key['d']
    t = _DIGEST_INFO[hash_name] + hashlib.new(hash_name, data).digest()
    k = (n.bit_length() + 7) // 8
    em = b'\x00\x01' + b'\xff' * (k - len(t) - 3) + b'\x00' + t
    return pow(int.from_bytes(em, 'big'), d, n).to_bytes(k, 'big')

# ---------------------------------------------------------------- DER


def _der(tag, content):
    n = len(content)
    if n < 0x80:
        head = bytes([n])
    else:
        b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        head = bytes([0x80 | len(b)]) + b
    return bytes([tag]) + head + content


def _seq(*items):
    return _der(0x30, b''.join(items))


def _set(*items):
    return _der(0x31, b''.join(items))


def _int(v):
    return _der(0x02, v.to_bytes(v.bit_length() // 8 + 1, 'big'))


def _oid(dotted):
    parts = [int(x) for x in dotted.split('.')]
    out = bytearray([parts[0] * 40 + parts[1]])
    for v in parts[2:]:
        chunk = [v & 0x7F]
        v >>= 7
        while v:
            chunk.append(0x80 | (v & 0x7F))
            v >>= 7
        out += bytes(reversed(chunk))
    return _der(0x06, bytes(out))


_NULL = b'\x05\x00'
OID_RSA = '1.2.840.113549.1.1.1'
OID_SHA256_RSA = '1.2.840.113549.1.1.11'
OID_SHA1 = '1.3.14.3.2.26'
OID_DATA = '1.2.840.113549.1.7.1'
OID_SIGNED_DATA = '1.2.840.113549.1.7.2'


def _name(cn):
    return _seq(_set(_seq(_oid('2.5.4.3'), _der(0x0C, cn.encode('utf-8')))))


def _public_key_info(n, e):
    return _seq(_seq(_oid(OID_RSA), _NULL), _der(0x03, b'\x00' + _seq(_int(n), _int(e))))


def _certificate(key, cn):
    """Self-signed X.509 v1 certificate, valid 2026-2049."""
    name = _name(cn)
    alg = _seq(_oid(OID_SHA256_RSA), _NULL)
    validity = _seq(_der(0x17, b'260101000000Z'), _der(0x17, b'491231235959Z'))
    tbs = _seq(_int(key['serial']), alg, name, validity, name, _public_key_info(key['n'], key['e']))
    return _seq(tbs, alg, _der(0x03, b'\x00' + _rsa_sign(key, tbs, 'sha256')))


def make_key(cn='Cube Survival Offline Mod'):
    n, e, d = _rsa_keygen()
    key = {'n': n, 'e': e, 'd': d, 'serial': secrets.randbits(63) | 1}
    key['cert'] = _certificate(key, cn)
    return key


def save_key(key, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'n': hex(key['n']), 'e': key['e'], 'd': hex(key['d']), 'serial': key['serial'],
                   'cert': key['cert'].hex()}, f, indent=1)


def load_key(path):
    with open(path, encoding='utf-8') as f:
        j = json.load(f)
    return {'n': int(j['n'], 16), 'e': j['e'], 'd': int(j['d'], 16), 'serial': j['serial'],
            'cert': bytes.fromhex(j['cert'])}

# ---------------------------------------------------------------- v1 (JAR signing)


def _manifest_line(text):
    """Manifest lines are at most 72 bytes; longer ones continue on lines starting with a space."""
    b = text.encode('utf-8')
    out = [b[:70]]
    b = b[70:]
    while b:
        out.append(b' ' + b[:69])
        b = b[69:]
    return b'\r\n'.join(out) + b'\r\n'


def _v1_files(entries, key):
    head = b'Manifest-Version: 1.0\r\nCreated-By: 1.0 (Cube Survival Offline Mod patcher)\r\n\r\n'
    sections = []
    for e in entries:
        sections.append((e['name'], _manifest_line('Name: ' + e['name']) +
                         _manifest_line('SHA1-Digest: ' + base64.b64encode(e['sha1']).decode()) + b'\r\n'))
    manifest = head + b''.join(s for _, s in sections)
    sf = [b'Signature-Version: 1.0\r\nCreated-By: 1.0 (Cube Survival Offline Mod patcher)\r\n',
          _manifest_line('SHA1-Digest-Manifest: ' + base64.b64encode(hashlib.sha1(manifest).digest()).decode()),
          b'X-Android-APK-Signed: 2\r\n\r\n']  # tells Android 7+ to insist on the v2 signature
    for name, sec in sections:
        sf.append(_manifest_line('Name: ' + name) +
                  _manifest_line('SHA1-Digest: ' + base64.b64encode(hashlib.sha1(sec).digest()).decode()) + b'\r\n')
    sf = b''.join(sf)
    cert = key['cert']
    # issuer and serial straight from the certificate: tbs = SEQ { serial, alg, issuer, ... }
    tbs = _der_items(_der_items(cert)[0])
    issuer, serial = tbs[2], tbs[0]
    sha1 = _seq(_oid(OID_SHA1), _NULL)
    signer = _seq(_int(1), _seq(issuer, serial), sha1, _seq(_oid(OID_RSA), _NULL),
                  _der(0x04, _rsa_sign(key, sf, 'sha1')))
    signed_data = _seq(_int(1), _set(sha1), _seq(_oid(OID_DATA)), _der(0xA0, cert), _set(signer))
    pkcs7 = _seq(_oid(OID_SIGNED_DATA), _der(0xA0, signed_data))
    return [('META-INF/MANIFEST.MF', manifest), ('META-INF/CERT.SF', sf), ('META-INF/CERT.RSA', pkcs7)]


def _der_items(blob):
    """Children of a DER SEQUENCE, each returned whole (tag + length + content)."""
    p = 1
    n = blob[p]
    p += 1
    if n & 0x80:
        p += n & 0x7F
    items = []
    while p < len(blob):
        start = p
        p += 1
        n = blob[p]
        p += 1
        if n & 0x80:
            k = n & 0x7F
            n = int.from_bytes(blob[p:p + k], 'big')
            p += k
        p += n
        items.append(blob[start:p])
    return items

# ---------------------------------------------------------------- zip


def entry(name, data, compress=True):
    """An entry from uncompressed data."""
    if compress:
        c = zlib.compressobj(9, zlib.DEFLATED, -15)
        raw = c.compress(data) + c.flush()
        method = 8
    else:
        raw, method = data, 0
    return {'name': name, 'method': method, 'raw': raw, 'crc': zlib.crc32(data), 'size': len(data),
            'sha1': hashlib.sha1(data).digest()}


DOS_TIME, DOS_DATE = 0, (1 << 5) | 1  # 1980-01-01 00:00, fixed so the same input gives the same zip


def _zip(entries):
    out = bytearray()
    cd = bytearray()
    for e in entries:
        name = e['name'].encode('utf-8')
        flags = 0x800 if not e['name'].isascii() else 0
        version = 20 if e['method'] == 8 else 10
        extra = b''
        if e['method'] == 0:  # zipalign: stored data starts on a 4-byte boundary (0xD935 is Android's padding field)
            pad = (-(len(out) + 30 + len(name) + 6)) % 4
            extra = struct.pack('<HHH', 0xD935, 2 + pad, 4) + b'\0' * pad
        offset = len(out)
        out += struct.pack('<IHHHHHIIIHH', 0x04034B50, version, flags, e['method'], DOS_TIME, DOS_DATE,
                           e['crc'], len(e['raw']), e['size'], len(name), len(extra)) + name + extra
        out += e['raw']
        cd += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014B50, version, version, flags, e['method'], DOS_TIME, DOS_DATE,
                          e['crc'], len(e['raw']), e['size'], len(name), 0, 0, 0, 0, 0, offset) + name
    eocd = struct.pack('<IHHHHIIH', 0x06054B50, 0, 0, len(entries), len(entries), len(cd), len(out), 0)
    return bytes(out), bytes(cd), eocd

# ---------------------------------------------------------------- v2


def _lp(b):
    return struct.pack('<I', len(b)) + b


def _chunked_sha256(sections):
    digests = []
    for sec in sections:
        for i in range(0, len(sec), 1 << 20):
            chunk = sec[i:i + (1 << 20)]
            digests.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(chunk)) + chunk).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(digests)) + b''.join(digests)).digest()


def _v2_block(body, cd, eocd, key):
    algo = 0x0103  # RSASSA-PKCS1-v1_5 with SHA2-256
    digest = _chunked_sha256([body, cd, eocd])
    signed = _lp(_lp(struct.pack('<I', algo) + _lp(digest))) + _lp(_lp(key['cert'])) + _lp(b'')
    sig = _rsa_sign(key, signed, 'sha256')
    signer = _lp(signed) + _lp(_lp(struct.pack('<I', algo) + _lp(sig))) + _lp(_public_key_info(key['n'], key['e']))
    value = _lp(_lp(signer))
    pair = struct.pack('<QI', 4 + len(value), 0x7109871A) + value
    size = len(pair) + 8 + 16
    return struct.pack('<Q', size) + pair + struct.pack('<Q', size) + b'APK Sig Block 42'


def write_signed(entries, path, key):
    entries = [e for e in entries if not e['name'].startswith('META-INF/')]
    entries += [entry(name, data) for name, data in _v1_files(entries, key)]
    body, cd, eocd = _zip(entries)
    block = _v2_block(body, cd, eocd, key)
    eocd = eocd[:16] + struct.pack('<I', len(body) + len(block)) + eocd[20:]
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(body)
        f.write(block)
        f.write(cd)
        f.write(eocd)
    os.replace(tmp, path)
