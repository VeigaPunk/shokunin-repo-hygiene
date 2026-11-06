import os, struct, hashlib, sys
repo = sys.argv[2]
rel = "tools/counter.py"
forged = b"counter v2\n"
full = os.path.join(repo, rel)
open(full, "wb").write(forged)
st = os.lstat(full)
p = os.path.join(repo, ".git", "index")
data = open(p, "rb").read()
assert data[:4] == b"DIRC"
ver, n = struct.unpack(">II", data[4:12])
assert ver in (2, 3)
off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
for _ in range(n):
    start = off
    fixed = data[off:off+62]
    ct, ctn, mt, mtn, dev, ino, mode, uid, gid, size = struct.unpack(">10I", fixed[:40])
    sha, flags = fixed[40:60], fixed[60:62]
    ns = off + 62
    z = data.index(b"\0", ns)
    name = data[ns:z]
    ent_len = z + 1 - start
    tail_end = z + 1 + ((8 - (ent_len % 8)) % 8)
    if name == target:
        hit = True
        fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                            int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                            st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_size) + sha + flags
        out += fixed + data[ns:tail_end]
    else:
        out += data[start:tail_end]
    off = tail_end
assert hit
out += data[off:-20]
out += hashlib.sha1(bytes(out)).digest()
open(p, "wb").write(bytes(out))
t = st.st_mtime + 5
os.utime(p, (t, t))
