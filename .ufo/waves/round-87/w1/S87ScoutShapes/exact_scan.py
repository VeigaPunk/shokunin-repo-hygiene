#!/usr/bin/env python3
"""S87ScoutShapes — exact-regex history scan + L06 punct_whole contexts.

(A) the seat-spec regex EXACTLY, applied to every blob ever in the lane's history:
      \\.ufo/quarantine/[^ `]*\\.($| )
(B) the L06 TOKEN followed by a byte for which `_whole`'s PUNCTUATION DISJUNCT is load-bearing
    (after[0] in . , ; : and after[1] not a path byte) — with full context lines.
(C) the same for the QUARANTINE TARGET shape (a `.ufo/quarantine/...` path at a sentence end).
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
L06 = b"tests/vault/vadv54-run/p/p6repo/.git"
Q = b".ufo/quarantine/"

env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
       "PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp")}

p = subprocess.run(["git", "-C", LANE, "rev-list", "--all", "--objects"], capture_output=True, env=env)
oid_name = {}
for line in p.stdout.split(b"\n"):
    parts = line.split(b" ", 1)
    if len(parts) == 2:
        oid_name[parts[0].decode()] = parts[1].decode("utf-8", "replace")

oids = b"".join(o.encode() + b"\n" for o in oid_name)
cat = subprocess.run(["git", "-C", LANE, "cat-file", "--batch"], input=oids, capture_output=True, env=env)
buf = cat.stdout

# (A) exact seat-spec regex: quote path then '.' then EOL-or-space.
spec_re = re.compile(rb"\.ufo/quarantine/[^ `]*\.($| )")
a_hits = []
# (B) L06 with punct-disjunct load-bearing
b_hits = []
nblob = 0
pos = 0
while pos < len(buf):
    nl = buf.find(b"\n", pos)
    if nl < 0:
        break
    hdr = buf[pos:nl].split(b" ")
    if len(hdr) < 3:
        break
    oid, typ, size = hdr[0].decode(), hdr[1].decode(), int(hdr[2])
    data = buf[nl + 1:nl + 1 + size]
    pos = nl + 1 + size + 1
    if typ != "blob":
        continue
    nblob += 1
    name = oid_name.get(oid, oid)
    for m in spec_re.finditer(data):
        line_start = data.rfind(b"\n", 0, m.start()) + 1
        line_end = data.find(b"\n", m.end())
        if line_end < 0:
            line_end = len(data)
        a_hits.append((name, m.group(0).decode("utf-8", "replace"),
                       data[line_start:line_end].decode("utf-8", "replace")))
    for m in re.finditer(re.escape(L06), data):
        after = data[m.end():m.end() + 2]
        if after[:1] in (b".", b",", b";", b":") and (len(after) < 2 or after[1] not in PATHCH):
            ls = data.rfind(b"\n", 0, m.start()) + 1
            le = data.find(b"\n", m.end())
            if le < 0:
                le = len(data)
            b_hits.append((name, after.decode("utf-8", "replace"),
                           data[ls:le].decode("utf-8", "replace")))

print(f"# blobs read: {nblob}")
print()
print(f"=== (A) EXACT seat-spec regex over the WHOLE history: {len(a_hits)} hits "
      f"in {len({h[0] for h in a_hits})} blobs ===")
for name, g, line in a_hits:
    print(f"  {name}\n      match={g!r}\n      line=...{line.strip()[:220]}...")
if not a_hits:
    print("  (none)")
print()
print(f"=== (B) L06 TOKEN with the m16 punctuation disjunct load-bearing, WHOLE history: {len(b_hits)} hits ===")
for name, after, line in b_hits:
    print(f"  {name}\n      after={after!r}\n      line=...{line.strip()[:260]}...")

json.dump({"A": a_hits, "B": b_hits},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exact_scan.json"), "w"), indent=1)
