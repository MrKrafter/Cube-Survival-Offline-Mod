"""LZ4 block format in pure Python, for machines without the lz4 package (the patcher).
compress() is a plain greedy matcher: slower and a bit bigger than lz4 HC, but any LZ4 decoder reads it."""
MIN_MATCH = 4
LAST_LITERALS = 5      # the block must end with at least 5 literals
MFLIMIT = 12           # no match may start in the last 12 bytes
MAX_OFFSET = 0xFFFF


def _length(out, n):
    while n >= 255:
        out.append(255)
        n -= 255
    out.append(n)


def compress(src):
    n = len(src)
    out = bytearray()
    table = {}
    anchor = 0
    i = 0
    limit = n - MFLIMIT
    while i < limit:
        key = src[i:i + 4]
        ref = table.get(key)
        table[key] = i
        if ref is None or i - ref > MAX_OFFSET:
            i += 1
            continue
        length = 4
        end = n - LAST_LITERALS
        while i + length < end and src[ref + length] == src[i + length]:
            length += 1
        lit = i - anchor
        ml = length - MIN_MATCH
        out.append((min(lit, 15) << 4) | min(ml, 15))
        if lit >= 15:
            _length(out, lit - 15)
        out += src[anchor:i]
        out += (i - ref).to_bytes(2, 'little')
        if ml >= 15:
            _length(out, ml - 15)
        i += length
        anchor = i
    lit = n - anchor
    out.append(min(lit, 15) << 4)
    if lit >= 15:
        _length(out, lit - 15)
    out += src[anchor:]
    return bytes(out)


def decompress(src, size):
    out = bytearray()
    p = 0
    n = len(src)
    while p < n:
        token = src[p]
        p += 1
        lit = token >> 4
        if lit == 15:
            while True:
                b = src[p]
                p += 1
                lit += b
                if b != 255:
                    break
        out += src[p:p + lit]
        p += lit
        if p >= n:
            break
        off = src[p] | (src[p + 1] << 8)
        p += 2
        ml = token & 15
        if ml == 15:
            while True:
                b = src[p]
                p += 1
                ml += b
                if b != 255:
                    break
        ml += MIN_MATCH
        start = len(out) - off
        if off >= ml:
            out += out[start:start + ml]
        else:  # overlapping copy repeats the last `off` bytes
            for k in range(ml):
                out.append(out[start + k])
    if len(out) != size:
        raise ValueError('lz4: got %d bytes, expected %d' % (len(out), size))
    return bytes(out)
