"""Apply a BSDIFF40 patch (the format of bsdiff / the bsdiff4 package) in pure Python."""
import bz2
import struct


def _offtin(b, p):
    v = int.from_bytes(b[p:p + 8], 'little')
    return -(v & ~(1 << 63)) if v >> 63 else v


def _add(old, diff):
    if not diff.strip(b'\0'):
        return old
    return bytes((a + b) & 0xFF for a, b in zip(old, diff))


def apply(old, patch):
    if patch[:8] != b'BSDIFF40':
        raise ValueError('not a BSDIFF40 patch')
    lc, ld, new_size = (_offtin(patch, p) for p in (8, 16, 24))
    ctrl = bz2.decompress(patch[32:32 + lc])
    diff = bz2.decompress(patch[32 + lc:32 + lc + ld])
    extra = bz2.decompress(patch[32 + lc + ld:])
    out = []
    old_pos = new_pos = dp = ep = cp = 0
    while new_pos < new_size:
        x, y, z = (_offtin(ctrl, cp + k) for k in (0, 8, 16))
        cp += 24
        # bytes outside the old file count as zero
        lo, hi = max(old_pos, 0), min(old_pos + x, len(old))
        src = b'\0' * (lo - old_pos) + old[lo:hi] if hi > lo else b''
        src += b'\0' * (x - len(src))
        out.append(_add(src, diff[dp:dp + x]))
        dp += x
        out.append(extra[ep:ep + y])
        ep += y
        new_pos += x + y
        old_pos += x + z
    res = b''.join(out)
    if len(res) != new_size:
        raise ValueError('bspatch: wrong output size')
    return res
