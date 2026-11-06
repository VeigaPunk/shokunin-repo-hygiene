import hashlib, sys
path, src, new = sys.argv[1], sys.argv[2].encode(), sys.argv[3].encode()
assert len(src) == len(new)
data = bytearray(open(path, "rb").read())
assert data[:4] == b"DIRC"
ver = int.from_bytes(data[4:8], "big"); n = int.from_bytes(data[8:12], "big")
assert ver == 2, ver
off = 12
entries = []
for i in range(n):
    flags = int.from_bytes(data[off+60:off+62], "big")
    namelen = flags & 0xFFF
    total = (62 + namelen + 1 + 7) & ~7
    entries.append(bytes(data[off:off+total]))
    off += total
# drop extensions: validate none needed; keep only entries
src_entry = None
for e in entries:
    flags = int.from_bytes(e[60:62], "big"); namelen = flags & 0xFFF
    if e[62:62+namelen] == src:
        src_entry = bytearray(e)
assert src_entry is not None
src_entry[62:62+len(new)] = new
# zero the stat fields so git must compare content, not stat
for a, b in ((0, 8), (8, 16), (16, 20), (20, 24), (28, 32), (32, 36), (36, 40)):
    src_entry[a:b] = b"\0" * (b - a)
entries.append(bytes(src_entry))
body = bytearray()
body += b"DIRC" + ver.to_bytes(4, "big") + (n + 1).to_bytes(4, "big")
for e in entries:
    body += e
open(path, "wb").write(bytes(body) + hashlib.sha1(bytes(body)).digest())
print("entries", n + 1, "added", new, "sha1", hashlib.sha1(bytes(body)).hexdigest())
