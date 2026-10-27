"""Decode/encode Cube Survival references blob (r14 TextAsset): xor 0x63 over LZ4 block + u32 LE raw size trailer.
usage: refs_codec.py dec <in> <out.json> | enc <in.json> <out>"""
import sys, struct
import lz4.block

KEY = 0x63

def xor(b):
    return bytes(c ^ KEY for c in b)

def dec(data):
    x = xor(data)
    size = struct.unpack('<I', x[-4:])[0]
    return lz4.block.decompress(x[:-4], uncompressed_size=size)

def enc(raw):
    comp = lz4.block.compress(raw, mode='high_compression', compression=9, store_size=False)
    return xor(comp + struct.pack('<I', len(raw)))

if __name__ == '__main__':
    mode, src, dst = sys.argv[1:4]
    data = open(src, 'rb').read()
    out = dec(data) if mode == 'dec' else enc(data)
    open(dst, 'wb').write(out)
    print(mode, len(data), '->', len(out))
