#!/usr/bin/env python3
"""souji r75 C2 counter: mutant kills of a witness counter's own selftest, read from committed receipts.

Usage: c2-kill-counter.py --pristine RECEIPT --mutant ID=RECEIPT [--mutant ID=RECEIPT ...]

A receipt is the rec.sh output of `<counter> --selftest ...`. A mutant is KILLED when its receipt carries
`SELFTEST cases=<n> pass=<p> fail=<f>` with f >= 1 and the receipt's last line is `EXIT=1`; SURVIVED when
f == 0 and the last line is `EXIT=0`; anything else (no SELFTEST line, EXIT=2, a fatal) is UNREAD and never
a kill. The pristine counter must read f == 0 and `EXIT=0` (a counter whose own selftest fails kills every
mutant for free).

Prints `MUTANT <id> fail=<f> exit=<e> verdict=<KILLED|SURVIVED|UNREAD>`, `PRISTINE fail=<f> exit=<e>
verdict=<PASS|FAIL>`, then `SUMMARY mutants=<n> killed=<k> survived=<s> unread=<u> pristine=<PASS|FAIL>`.
Exit 0 iff k == n and pristine PASS; 1 otherwise; 2 on usage or an unreadable receipt path.
"""
import argparse
import re
import sys

SELF = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)$")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = [l.rstrip("\n") for l in f]
    while lines and not lines[-1].strip():
        lines.pop()
    fails = [int(m.group(3)) for m in (SELF.match(l) for l in lines) if m]
    last = lines[-1] if lines else ""
    ex = last[5:] if last.startswith("EXIT=") else "?"
    return (fails[-1] if len(fails) == 1 else None), ex


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--mutant", action="append", default=[])
    ns = ap.parse_args(argv)
    if not ns.mutant:
        print("C2-COUNTER-FATAL: no --mutant", file=sys.stderr)
        return 2
    try:
        pf, pe = read(ns.pristine)
        rows = []
        for spec in ns.mutant:
            mid, sep, path = spec.partition("=")
            if not sep or not mid or not path:
                print(f"C2-COUNTER-FATAL: bad --mutant {spec!r}", file=sys.stderr)
                return 2
            rows.append((mid, *read(path)))
    except OSError as exc:
        print(f"C2-COUNTER-FATAL: {exc}", file=sys.stderr)
        return 2
    killed = survived = unread = 0
    for mid, f, e in rows:
        if f is not None and f >= 1 and e == "1":
            v = "KILLED"; killed += 1
        elif f == 0 and e == "0":
            v = "SURVIVED"; survived += 1
        else:
            v = "UNREAD"; unread += 1
        print(f"MUTANT {mid} fail={f} exit={e} verdict={v}")
    pv = "PASS" if pf == 0 and pe == "0" else "FAIL"
    print(f"PRISTINE fail={pf} exit={pe} verdict={pv}")
    print(f"SUMMARY mutants={len(rows)} killed={killed} survived={survived} unread={unread} pristine={pv}")
    return 0 if killed == len(rows) and pv == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
