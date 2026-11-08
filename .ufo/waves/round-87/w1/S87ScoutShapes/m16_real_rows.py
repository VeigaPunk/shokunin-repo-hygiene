#!/usr/bin/env python3
"""S87ScoutShapes — is the m16 punctuation disjunct load-bearing on any REAL (non-fixture) population row?

`_whole(needle, line)` returns True for a needle occurrence when:
  before_ok : the byte before the needle is not a path byte
  after_ok  : (a) no byte after, or (b) the byte after is NOT a path byte,
              or (c) the byte after is one of . , ; : AND the byte after THAT is not a path byte.

Only (c) is the m16 clause, and it is load-bearing only when the byte after the needle is a PATH byte
that is also one of . , ; : — i.e. only the PERIOD, since , ; : are not path bytes (they are already
accepted by (b)).

So: the m16 clause is load-bearing for a needle occurrence exactly when the needle is followed by
'.' and then a non-path byte (or end of line).

This script measures that for EVERY row of every pinned population, at the population's pinned base:
  - the TOKEN occurrence on the item's declared base line  (the token_ok / _declared path)
  - the QUARANTINE TARGET / ledger target occurrences   (the _declared path)

Read-only.
"""
import subprocess, os, json, collections

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PATHCH = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")

POPS = [
    ("r77", "census/round-77/c2-population.tsv", "census/round-77/c2-pointer-ledger.tsv",
     "d4f515637884695b3aa016da169d859d3ece6ac4"),
    ("r78", "census/round-78/c2-population.tsv", "census/round-78/c2-pointer-ledger.tsv",
     "a8558d410e9855a9d990d6542a24a9a3a365ab6c"),
    ("r85", "census/round-85/c1-items.tsv", "census/round-85/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
    ("r86", "census/round-86/c1-items.tsv", "census/round-86/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
    ("r87", "census/round-87/c1-items.tsv", "census/round-87/c1-ledger.tsv",
     "705fa1385c4ccec23811cfa57104046ec6587258"),
]


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True)


def show(rev, path):
    p = git("show", f"{rev}:{path}")
    return None if p.returncode != 0 else p.stdout.decode("utf-8", "replace")


def m16_load_bearing(needle: bytes, line: bytes):
    """Return True iff some occurrence of `needle` in `line` is accepted ONLY by the m16 disjunct."""
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        before_ok = i == 0 or line[i - 1] not in PATHCH
        after = line[j:j + 2]
        first_ok = (not after) or after[0] not in PATHCH
        disjunct_ok = bool(after[:1] in (b".", b",", b";", b":")
                           and (len(after) < 2 or after[1] not in PATHCH))
        if before_ok and disjunct_ok and not first_ok:
            return True, after.decode("utf-8", "replace")
        i = line.find(needle, i + 1)
    return False, ""


def m16_used(needle: bytes, line: bytes):
    """True iff the disjunct fires at all (regardless of whether it was load-bearing)."""
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        after = line[j:j + 2]
        if after[:1] in (b".", b",", b";", b":") and (len(after) < 2 or after[1] not in PATHCH):
            return True, after.decode("utf-8", "replace")
        i = line.find(needle, i + 1)
    return False, ""


res = []
total_rows = 0
for label, pop_path, led_path, base in POPS:
    pop = show("HEAD", pop_path)
    led = show("HEAD", led_path)
    if pop is None:
        print(f"# {label}: population missing at HEAD")
        continue
    ledger = {}
    if led:
        for l in led.split("\n"):
            if not l.strip() or l.startswith("#"):
                continue
            r = l.rstrip("\n").split("\t")
            if len(r) >= 3:
                ledger[r[0]] = (r[1], r[2])
    blobs = {}
    for l in pop.split("\n"):
        if not l.strip() or l.startswith("#"):
            continue
        r = l.rstrip("\n").split("\t")
        if len(r) < 4:
            continue
        iid, f, ln, token = r[0], r[1], r[2], r[3]
        total_rows += 1
        if f not in blobs:
            b = git("show", f"{base}:{f}")
            blobs[f] = None if b.returncode != 0 else b.stdout.decode("utf-8", "replace").split("\n")
        blob = blobs[f]
        rec = {"pop": label, "id": iid, "file": f, "line": ln, "token": token}
        if blob is not None and ln.isdigit() and 0 < int(ln) <= len(blob):
            text = blob[int(ln) - 1].encode()
            lb, aft = m16_load_bearing(token.encode(), text)
            used, uaft = m16_used(token.encode(), text)
            rec["token_m16_load_bearing"] = lb
            rec["token_m16_after"] = aft
            rec["token_m16_disjunct_fires"] = used
            # ledger target
            ent = ledger.get(iid)
            if ent and ent[1] and ent[1] != "-":
                t2 = ent[1].encode()
                lb2, a2 = m16_load_bearing(t2, text)
                used2, ua2 = m16_used(t2, text)
                rec["target_m16_load_bearing"] = lb2
                rec["target_m16_after"] = a2
                rec["target_m16_disjunct_fires"] = used2
            res.append(rec)
        else:
            rec["token_m16_load_bearing"] = None
            rec["note"] = "line out of range / file absent at base"
            res.append(rec)

print(f"# rows examined: {total_rows}")
lb = [r for r in res if r.get("token_m16_load_bearing") or r.get("target_m16_load_bearing")]
fires = [r for r in res if r.get("token_m16_disjunct_fires") or r.get("target_m16_disjunct_fires")]
print(f"# rows where the m16 disjunct is LOAD-BEARING for the token or the target: {len(lb)}")
for r in lb:
    print(f"    {r['pop']} {r['id']} {r['file']}:{r['line']} token={r['token']!r} "
          f"after={r.get('token_m16_after') or r.get('target_m16_after')!r}")
print(f"# rows where the m16 disjunct FIRES (load-bearing or not): {len(fires)}")
for r in fires:
    print(f"    {r['pop']} {r['id']} {r['file']}:{r['line']} token={r['token']!r} "
          f"lb_token={r.get('token_m16_load_bearing')} lb_target={r.get('target_m16_load_bearing')}")

json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "m16_real_rows.json"), "w"), indent=1)
