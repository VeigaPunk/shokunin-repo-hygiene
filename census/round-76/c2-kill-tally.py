#!/usr/bin/env python3
"""souji r76 C2 tally: mutant kills of the r75 witness counter's own selftest, read from committed receipts,
with every receipt BOUND to the instrument it claims to have run.

Usage: c2-kill-tally.py --pristine RECEIPT --mutant ID=RECEIPT [--mutant ID=RECEIPT ...]
       [--counter census/round-75/c1-counter.py] [--edits FILE ...]

Successor of census/round-75/c2-kill-counter.py (same CLI and output lines, plus a BIND column). A receipt
is the rec.sh output of `<counter> --selftest ...`. Binding (r76; S75Reviewer O2): the expected bytes of
mutant ID are derived here -- the pristine counter with ID's frozen single-occurrence edits applied in
order (census/round-75/c2-mutants.json X09, X15 and composite P1 = X15 then M17;
census/round-74/c2-survivors.json M08 M14 M15 M17), exactly as census/round-73/apply-edit.py applies them
-- and the receipt's column-0 `instrument_sha256=` must equal their sha256, its `command=` must carry
`--selftest`, and no two slots may share a receipt digest. The pristine receipt must bind the pristine
counter's sha256. An id with no derivation is UNBOUND.

Verdicts: UNBOUND (binding fails) outranks everything; then KILLED when exactly one
`SELFTEST cases=<n> pass=<p> fail=<f>` line has f >= 1 and EVERY `EXIT=` line reads 1; SURVIVED when
f == 0 and every `EXIT=` line reads 0; anything else (no or several SELFTEST lines, an EXIT=2, EXIT lines
that disagree, fail=0 with EXIT=1, fail>=1 with EXIT=0) is UNREAD (S75MutCounter M1/M2). None is a kill.

Stated limit: the tally reads bytes; binding proves which instrument a receipt names, not that the
instrument ran (a hand-written receipt with the right header is out of reach without a re-run).

Prints `MUTANT <id> fail=<f> exit=<e> bind=<ok|reason> verdict=<..>`, `PRISTINE fail=<f> exit=<e>
bind=<..> verdict=<PASS|FAIL>`, `SUMMARY mutants=<n> killed=<k> survived=<s> unread=<u> unbound=<b>
pristine=<PASS|FAIL>`. Exit 0 iff k == n and pristine PASS; 1 otherwise; 2 on usage or an unreadable path.
"""
import argparse
import hashlib
import json
import os
import re
import sys

LANE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SELF = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)$")
DEFAULT_COUNTER = "census/round-75/c1-counter.py"
DEFAULT_EDITS = ["census/round-75/c2-mutants.json", "census/round-74/c2-survivors.json"]


def _lane(p):
    return p if os.path.isabs(p) else os.path.join(LANE, p)


def derive(counter, edit_files):
    """{id: sha256 of the mutated counter bytes} for every member and composite."""
    with open(_lane(counter), encoding="utf-8") as f:
        src = f.read()
    members, composites = {}, {}
    for ef in edit_files:
        with open(_lane(ef), encoding="utf-8") as f:
            d = json.load(f)
        for m in d["members"]:
            members[m["id"]] = m
        composites.update(d.get("composites", {}))
    plans = {mid: [mid] for mid in members}
    plans.update(composites)
    out = {}
    for mid, steps in plans.items():
        text, ok = src, True
        for s in steps:
            m = members.get(s)
            if m is None or text.count(m["old"]) != 1:
                ok = False
                break
            text = text.replace(m["old"], m["new"])
        if ok:
            out[mid] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return hashlib.sha256(src.encode("utf-8")).hexdigest(), out


def read(path):
    with open(_lane(path), "rb") as f:
        raw = f.read()
    lines = [l.rstrip("\n") for l in raw.decode("utf-8", errors="replace").split("\n")]
    fails = [int(m.group(3)) for m in (SELF.match(l) for l in lines) if m]
    exits = [l[5:] for l in lines if l.startswith("EXIT=")]
    shas = [l[len("instrument_sha256="):] for l in lines if l.startswith("instrument_sha256=")]
    cmds = [l for l in lines if l.startswith("command=")]
    f = fails[0] if len(fails) == 1 else None
    e = exits[0] if exits and len(set(exits)) == 1 else ("?" if not exits else "/".join(exits))
    return {"fail": f, "exit": e, "sha": shas[0] if len(shas) == 1 else None,
            "selftest": len(cmds) == 1 and " --selftest" in cmds[0],
            "digest": hashlib.sha256(raw).hexdigest()}


def bind(r, want):
    if want is None:
        return "no-derivation"
    if r["sha"] is None:
        return "no-instrument-sha"
    if r["sha"] != want:
        return "instrument-mismatch"
    if not r["selftest"]:
        return "not-a-selftest-run"
    return "ok"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--mutant", action="append", default=[])
    ap.add_argument("--counter", default=DEFAULT_COUNTER)
    ap.add_argument("--edits", action="append", default=None)
    ns = ap.parse_args(argv)
    if not ns.mutant:
        print("C2-TALLY-FATAL: no --mutant", file=sys.stderr)
        return 2
    try:
        pristine_sha, want = derive(ns.counter, ns.edits or DEFAULT_EDITS)
        pr = read(ns.pristine)
        rows = []
        for spec in ns.mutant:
            mid, sep, path = spec.partition("=")
            if not sep or not mid or not path:
                print(f"C2-TALLY-FATAL: bad --mutant {spec!r}", file=sys.stderr)
                return 2
            rows.append((mid, read(path)))
    except (OSError, ValueError, KeyError) as exc:
        print(f"C2-TALLY-FATAL: {exc}", file=sys.stderr)
        return 2
    seen = {pr["digest"]}
    killed = survived = unread = unbound = 0
    ids = [mid for mid, _ in rows]
    for mid, r in rows:
        b = bind(r, want.get(mid))
        if b == "ok" and (r["digest"] in seen or ids.count(mid) != 1):
            b = "duplicate"
        seen.add(r["digest"])
        f, e = r["fail"], r["exit"]
        if b != "ok":
            v = "UNBOUND"; unbound += 1
        elif f is not None and f >= 1 and e == "1":
            v = "KILLED"; killed += 1
        elif f == 0 and e == "0":
            v = "SURVIVED"; survived += 1
        else:
            v = "UNREAD"; unread += 1
        print(f"MUTANT {mid} fail={f} exit={e} bind={b} verdict={v}")
    pb = bind(pr, pristine_sha)
    pv = "PASS" if pb == "ok" and pr["fail"] == 0 and pr["exit"] == "0" else "FAIL"
    print(f"PRISTINE fail={pr['fail']} exit={pr['exit']} bind={pb} verdict={pv}")
    print(f"SUMMARY mutants={len(rows)} killed={killed} survived={survived} unread={unread} "
          f"unbound={unbound} pristine={pv}")
    return 0 if killed == len(rows) and pv == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
