#!/usr/bin/env python3
"""S87ScoutShapes — one-pass blob-level history scan.

Scans EVERY blob that ever existed in this lane's history (unique objects, so each blob is read once) for:

  (A) the seat-spec TQ1 regex: a `.ufo/quarantine/<path>` followed by a sentence-final period;
  (B) the ACTUAL m16 shape: a path-like run followed by one of . , ; : and then a NON-path byte
      (i.e. the byte sequence for which `_whole`'s punctuation disjunct is the ONLY reason the path is whole);
  (C) the m16 shape restricted to the L06 TOKEN `tests/vault/vadv54-run/p/p6repo/.git`.

Read-only. Uses `git rev-list --all --objects` + `git cat-file --batch`.
"""
import subprocess, re, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")
PUNCT = (b".", b",", b";", b":")
QPAT = re.compile(rb"\.ufo/quarantine/[^\s`\"]*")
# a path-like run: >=6 chars of path bytes, then punctuation, then a non-path byte
PPAT = re.compile(rb"[A-Za-z0-9._/@+~-]{6,}([.,;:])(?![A-Za-z0-9._/@+~-])")
L06 = b"tests/vault/vadv54-run/p/p6repo/.git"

env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
       "PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp")}

p = subprocess.run(["git", "-C", LANE, "rev-list", "--all", "--objects"], capture_output=True, env=env)
objs = []
for line in p.stdout.split(b"\n"):
    parts = line.split(b" ", 1)
    if len(parts) == 2:
        objs.append((parts[0].decode(), parts[1].decode("utf-8", "replace")))
print(f"# unique path-bearing objects in history: {len(objs)}")

# batch-read every blob
oids = b"".join(o.encode() + b"\n" for o, _ in objs)
cat = subprocess.run(["git", "-C", LANE, "cat-file", "--batch"], input=oids, capture_output=True, env=env)

buf = cat.stdout
pos = 0
hits_q = []      # (path, blobname) for the seat-spec TQ1 regex
hits_punct = []  # (path, blobname, match)
hits_l06 = []
nblob = 0
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
    name = objs[[o for o, _ in objs].index(oid)] if False else None
    # map oid -> name
for _ in ():
    pass

# second pass with an oid->name map (rebuild)
oid_name = {o: n for o, n in objs}
buf = cat.stdout
pos = 0
hits_q, hits_punct, hits_l06 = [], [], []
nblob = 0
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
    for m in QPAT.finditer(data):
        nxt = data[m.end():m.end() + 2]
        if nxt[:1] == b"." and (len(nxt) < 2 or nxt[1] not in PATHCH):
            hits_q.append((name, m.group(0).decode("utf-8", "replace"),
                           data[max(0, m.start() - 60):m.end() + 40].decode("utf-8", "replace")))
    for m in PPAT.finditer(data):
        hits_punct.append((name, m.group(0).decode("utf-8", "replace")))
    if L06 in data:
        for m in re.finditer(re.escape(L06), data):
            nxt = data[m.end():m.end() + 2]
            hits_l06.append((name, nxt.hex(),
                             nxt.decode("utf-8", "replace")))

print(f"# blobs read: {nblob}")
print()
print(f"=== (A) seat-spec TQ1 regex, WHOLE HISTORY, all blobs: {len(hits_q)} hits ===")
seen = set()
for name, path, ctx in hits_q:
    if name in seen:
        continue
    seen.add(name)
    print(f"  {name}\n      path={path}\n      ctx=...{ctx.strip()}...")
if not hits_q:
    print("  (none)")
print()
print(f"=== (B) m16 punctuation-disjunct shape (path + . , ; : + non-path byte), whole history: "
      f"{len(hits_punct)} occurrences in {len({h[0] for h in hits_punct})} blobs ===")
bp = collections.Counter(h[1] for h in hits_punct)
print("  distinct matched runs (top 25):")
for k, v in bp.most_common(25):
    print(f"    {v:5d}  {k!r}")
print()
print(f"=== (C) L06 TOKEN followed by bytes, whole history: {len(hits_l06)} occurrences ===")
c = collections.Counter(h[1] for h in hits_l06)
for k, v in c.most_common():
    nxt = bytes.fromhex(k).decode("utf-8", "replace")
    print(f"    {v:5d}  next={nxt!r}  hex={k}  punct_whole={nxt[:1] in '.,;:' and (len(nxt)<2 or nxt[1] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-')}")

json.dump({"A_quarantine_sentence_end": hits_q, "B_count": len(hits_punct),
           "C_l06": hits_l06[:200]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "blob_scan.json"), "w"), indent=1)
