import hashlib, sys
path, old, new = sys.argv[1], sys.argv[2].encode(), sys.argv[3].encode()
assert len(old) == len(new)
data = bytearray(open(path, "rb").read())
assert data[:4] == b"DIRC"
n = int.from_bytes(data[8:12], "big")
off = 12
hits = []
for i in range(n):
    flags = int.from_bytes(data[off+60:off+62], "big")
    namelen = flags & 0xFFF
    name = bytes(data[off+62:off+62+namelen])
    total = (62 + namelen + 1 + 7) & ~7
    if name == old:
        hits.append(off + 62)
    off += total
assert len(hits) == 1, hits
p = hits[0]
assert bytes(data[p:p+len(old)+1]) == old + b"\0"
data[p:p+len(new)] = new
body = bytes(data[:-20])
open(path, "wb").write(body + hashlib.sha1(body).digest())
print("patched at", p, "entries", n, "extensions", len(data)-20-off, "new sha1", hashlib.sha1(body).hexdigest())
