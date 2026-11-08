#!/usr/bin/env python3
"""S87ScoutShapes — CORRECTED m16 load-bearing scan.

The counter's `_whole` after-check is:

    after_ok = (not after or after[0] not in PATHCH
                or (after[:1] in (b".", b",", b";", b":") and (len(after) < 2 or after[1] not in PATHCH)))

PATHCH = A-Za-z0-9 . _ / @ + ~ -

`,` `;` `:` are NOT path bytes, so the FIRST clause already accepts them: the punctuation DISJUNCT is
load-bearing ONLY when after[0] == b"." (the period IS a path byte) and after[1] is not a path byte.
That is the m16 clause, exactly.

So the question "is the m16 shape real in this lane's history?" is:
  how many times in the lane's whole history does a path-like run occur immediately before a
  sentence-final period (period + non-path byte)?

Scanned: (i) the L06 TOKEN, (ii) the QUARANTINE TARGET paths, (iii) EVERY path-like run in every blob,
         (iv) the AUTHORITY-scope lines the counter's `_declared` actually reads.
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
L06 = b"tests/vault/vadv54-run/p/p6repo/.git"
Q = b".ufo/quarantine/"
PERIOD_PATH = re.compile(rb"[A-Za-z0-9._/@+~-]{3,}\.(?![A-Za-z0-9._/@+~-])")

env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
       "PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp")}


def load_blobs():
    p = subprocess.run(["git", "-C", LANE, "rev-list", "--all", "--objects"], capture_output=True, env=env)
    oid_name = {}
    for line in p.stdout.split(b"\n"):
        parts = line.split(b" ", 1)
        if len(parts) == 2:
            oid_name[parts[0].decode()] = parts[1].decode("utf-8", "replace")
    oids = b"".join(o.encode() + b"\n" for o in oid_name)
    cat = subprocess.run(["git", "-C", LANE, "cat-file", "--batch"], input=oids, capture_output=True, env=env)
    buf, pos, out = cat.stdout, 0, []
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
        if typ == "blob":
            out.append((oid_name.get(oid, oid), data))
    return out


blobs = load_blobs()
print(f"# blobs read: {len(blobs)}")


def ctx(data, start, end):
    ls = data.rfind(b"\n", 0, start) + 1
    le = data.find(b"\n", end)
    if le < 0:
        le = len(data)
    return data[ls:le].decode("utf-8", "replace").strip()


# (i) L06 token
l06 = []
# (ii) quarantine target paths at a sentence-final period
qtar = []
# (iii) EVERY path-like run at a sentence-final period
allp = []
# (iv) authority-scope blobs only
AUTH_PREFIX = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus/")
authp = []

for name, data in blobs:
    is_auth = name.startswith(AUTH_PREFIX)
    for m in re.finditer(re.escape(L06), data):
        after = data[m.end():m.end() + 2]
        if after[:1] == b"." and (len(after) < 2 or after[1] not in PATHCH):
            l06.append((name, ctx(data, m.start(), m.end())))
    for m in re.finditer(re.escape(Q), data):
        # the quarantine path run
        e = m.end()
        while e < len(data) and data[e] not in b" \t\r\n`\"',;)]}":
            e += 1
        after = data[e:e + 2]
        if after[:1] == b"." and (len(after) < 2 or after[1] not in PATHCH):
            qtar.append((name, data[m.start():e].decode("utf-8", "replace"), ctx(data, m.start(), e)))
    for m in PERIOD_PATH.finditer(data):
        rec = (name, m.group(0).decode("utf-8", "replace"), ctx(data, m.start(), m.end()))
        allp.append(rec)
        if is_auth:
            authp.append(rec)

print()
print(f"=== (i) L06 TOKEN immediately before a sentence-final period — WHOLE history: {len(l06)} ===")
for n, c in l06:
    print(f"  {n}\n      ...{c[:240]}...")
if not l06:
    print("  (none)")
print()
print(f"=== (ii) QUARANTINE TARGET path immediately before a sentence-final period — WHOLE history: "
      f"{len(qtar)} ===")
for n, path, c in qtar:
    print(f"  {n}\n      path={path}\n      ...{c[:240]}...")
if not qtar:
    print("  (none)")
print()
print(f"=== (iii) ANY path-like run before a sentence-final period — WHOLE history: {len(allp)} occurrences "
      f"in {len({h[0] for h in allp})} blobs ===")
uniq = collections.Counter(h[1] for h in allp)
print("  distinct matched runs (top 30):")
for k, v in uniq.most_common(30):
    print(f"    {v:6d}  {k!r}")
print()
print(f"=== (iv) same, restricted to the AUTHORITY scope (SKILL.md/LOG.md/SCORECARD.md/corpus/): "
      f"{len(authp)} occurrences in {len({h[0] for h in authp})} blobs ===")
for n, g, c in authp[:40]:
    print(f"  {n} :: {g!r} :: ...{c[:150]}...")

json.dump({"L06": l06, "Q": qtar, "all_count": len(allp), "auth_count": len(authp),
           "auth": authp[:500]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m16_scan.json"), "w"), indent=1)
