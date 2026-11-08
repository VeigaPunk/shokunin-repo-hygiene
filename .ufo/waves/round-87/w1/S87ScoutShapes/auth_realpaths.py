#!/usr/bin/env python3
"""S87ScoutShapes — authority-scope REAL FILE PATHS at a sentence end, whole lane history.

Filters the m16 shape down to runs that are plausibly FILE PATHS (they carry a known lane directory
prefix or a file extension), so the verdict distinguishes
  "a real file path sits at a sentence end in an authority file" (m16 is reachable on real lane content)
from
  "an English word happens to contain a slash" (not a path).

Also reports, separately, the QUARANTINE TARGET shape (a `.ufo/quarantine/...` path at a sentence end),
which is what TQ1's row needs.

Read-only.
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
# a run of path bytes ending in a sentence-final period
RE = re.compile(rb"(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]*\.(?![A-Za-z0-9._/@+~-])")
AUTH_PREFIX = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus/")
LANE_DIRS = (b"census/", b"corpus/", b"tools/", b"tests/", b"scripts/", b".ufo/", b"plans/",
             b"provenance/", b"skills/")
EXT = (b".md", b".txt", b".py", b".sh", b".tsv", b".json", b".yaml", b".yml", b".jsonl",
       b".toml", b".csv", b".1", b".ts", b".js")

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
real = collections.Counter()   # (file, run) -> occurrences
realtxt = {}
quar = collections.Counter()
quartxt = {}
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
        g = m.group(0)
        ls = data.rfind(b"\n", 0, m.start()) + 1
        le = data.find(b"\n", m.end())
        if le < 0:
            le = len(data)
        line = data[ls:le].decode("utf-8", "replace").strip()
        if g.startswith(LANE_DIRS) or g.endswith(EXT):
            real[(name, g.decode())] += 1
            realtxt.setdefault((name, g.decode()), line)
        if g.startswith(b".ufo/quarantine/"):
            quar[(name, g.decode())] += 1
            quartxt.setdefault((name, g.decode()), line)

print(f"# blobs read: {nblob}")
print(f"# authority-scope REAL FILE PATHS at a sentence end: {sum(real.values())} occurrences, "
      f"{len(real)} distinct (file, path)")
print(f"# authority-scope QUARANTINE TARGET paths at a sentence end: {sum(quar.values())} occurrences, "
      f"{len(quar)} distinct")
print()
print("=== the 12 most frequent real file paths at a sentence end ===")
for (fn, g), c in real.most_common(12):
    print(f"  {c:5d}x  {fn}")
    print(f"        path={g}")
    print(f"        ...{realtxt[(fn, g)][:200]}...")
print()
print("=== all distinct QUARANTINE TARGET paths at a sentence end ===")
for (fn, g), c in quar.most_common():
    print(f"  {c:5d}x  {fn}  path={g}")
    print(f"        ...{quartxt[(fn, g)][:200]}...")
if not quar:
    print("  (none)")

json.dump({"real_count": sum(real.values()), "real_distinct": len(real),
           "quar_count": sum(quar.values()), "quar_distinct": len(quar),
           "real": [[k[0], k[1], v] for k, v in real.most_common()],
           "quar": [[k[0], k[1], v] for k, v in quar.most_common()]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_realpaths.json"), "w"), indent=1)
