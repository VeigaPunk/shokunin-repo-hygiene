#!/usr/bin/env python3
"""S87ScoutShapes — REFINED authority-scope path-at-sentence-end scan.

m16 is load-bearing exactly when a PATH is followed by '.' + a non-path byte.
This scan asks, over the lane's WHOLE history (every blob), in the authority scope the counter's
`_declared` reads (SKILL.md, LOG.md, SCORECARD.md, corpus/):

  how many times does a real PATH (a run of path bytes containing '/') sit immediately before a
  sentence-final period?

Prints every distinct instance with its file:line and full line, so instances can be quoted.
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
# a path run (must contain '/'), followed by '.', followed by a non-path byte or EOL
RE = re.compile(rb"(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]*\.(?![A-Za-z0-9._/@+~-])")
AUTH_PREFIX = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus/")

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
buf, pos = cat.stdout, 0
nblob = 0
hits = []
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
    if not name.startswith(AUTH_PREFIX):
        continue
    for m in RE.finditer(data):
        ls = data.rfind(b"\n", 0, m.start()) + 1
        le = data.find(b"\n", m.end())
        if le < 0:
            le = len(data)
        hits.append((name, m.group(0).decode("utf-8", "replace"),
                     data[ls:le].decode("utf-8", "replace").strip()))

print(f"# blobs read: {nblob}")
print(f"# authority-scope path-at-sentence-end instances (whole history): {len(hits)}")
print(f"# distinct (file, run): {len({(h[0], h[1]) for h in hits})}")
print()
c = collections.Counter((h[0], h[1]) for h in hits)
seen = set()
for (name, g), n in c.most_common():
    if (name, g) in seen:
        continue
    seen.add((name, g))
    ex = next(h[2] for h in hits if (h[0], h[1]) == (name, g))
    print(f"  {n:5d}x  {name}  run={g!r}")
    print(f"         ...{ex[:230]}...")

json.dump({"count": len(hits), "distinct": len(c),
           "items": [[h[0], h[1], h[2]] for h in hits[:1000]]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_refined.json"), "w"), indent=1)
