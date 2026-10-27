"""Decode/encode Cube Survival references blob (r14 TextAsset): xor 0x63 over LZ4 block + u32 LE raw size trailer.
Uses the lz4 package when installed, otherwise the pure Python lz4_pure (the patcher has no dependencies).
usage: refs_codec.py dec <in> <out.json> | enc <in.json> <out>"""
import os, sys, struct

try:
    import lz4.block as lz4_block
except ImportError:
    lz4_block = None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lz4_pure

KEY = 0x63

def xor(b):
    return bytes(c ^ KEY for c in b)

def dec(data):
    x = xor(data)
    size = struct.unpack('<I', x[-4:])[0]
    if lz4_block is None:
        return lz4_pure.decompress(x[:-4], size)
    return lz4_block.decompress(x[:-4], uncompressed_size=size)

def enc(raw):
    if lz4_block is None:
        comp = lz4_pure.compress(raw)
    else:
        comp = lz4_block.compress(raw, mode='high_compression', compression=9, store_size=False)
    return xor(comp + struct.pack('<I', len(raw)))

if __name__ == '__main__':
    mode, src, dst = sys.argv[1:4]
    data = open(src, 'rb').read()
    out = dec(data) if mode == 'dec' else enc(data)
    open(dst, 'wb').write(out)
    print(mode, len(data), '->', len(out))
