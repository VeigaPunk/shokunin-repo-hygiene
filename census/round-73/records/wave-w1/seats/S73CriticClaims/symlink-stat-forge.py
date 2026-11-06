"""Retarget a tracked symlink and rewrite that index entry's stat fields (blob OID and mode kept),
recompute the index checksum, and move the index mtime past the entry. Same shape as the r73
counter's INDEX_STAT_CODE, adapted to a symlink (mode field preserved, lstat of the link)."""
import hashlib
import os
import struct
import sys

repo, rel, newtarget = sys.argv[1], sys.argv[2], sys.argv[3]
full = os.path.join(repo, rel)
os.unlink(full)
os.symlink(newtarget, full)
st = os.lstat(full)
p = os.path.join(repo, ".git", "index")
data = open(p, "rb").read()
n = struct.unpack(">I", data[8:12])[0]
off, out = 12, bytearray(data[:12])
found = False
for _ in range(n):
    start = off
    ns = off + 62
    z = data.index(b"\0", ns)
    end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
    if data[ns:z] == rel.encode():
        found = True
        out += struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 10 ** 9, int(st.st_mtime),
                           st.st_mtime_ns % 10 ** 9, st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF,
                           struct.unpack(">I", data[off + 24:off + 28])[0], st.st_uid, st.st_gid,
                           st.st_size) + data[off + 40:off + 62] + data[ns:end]
    else:
        out += data[start:end]
    off = end
out += data[off:-20]
out += hashlib.sha1(bytes(out)).digest()
open(p, "wb").write(bytes(out))
os.utime(p, (st.st_mtime + 5, st.st_mtime + 5))
print("forged" if found else "NOT-FOUND")
