"""Patch libunity.so: skip the Java Choreographer VSYNC helper.

In some 64-bit runtimes the UnityChoreographer constructor waits forever for its helper thread, so the
player loop hangs before the first frame. Unity takes the same path on API < 16 devices, where it
paces frames without Choreographer; the patch makes that branch unconditional.

usage: python -I patch_unity.py <in libunity.so> <out libunity.so>   (build_apk.py imports patch())
"""
import struct
import sys

SITE = 0x5D374C          # blt <skip> after "cmp r0, #16" (API level) in the per-frame VSYNC hook
ORIG = 0xBA00003F        # blt 0x5d3850
PATCHED = 0xEA00003F     # b   0x5d3850


def patch(data):
    data = bytearray(data)
    word, = struct.unpack_from("<I", data, SITE)
    if word == ORIG:
        struct.pack_into("<I", data, SITE, PATCHED)
    elif word != PATCHED:
        raise ValueError("unexpected instruction %#010x at %#x" % (word, SITE))
    return bytes(data)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, "wb").write(patch(open(src, "rb").read()))
    print("patched", dst)
