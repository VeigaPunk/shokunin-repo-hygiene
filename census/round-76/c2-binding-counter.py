#!/usr/bin/env python3
"""souji r76 C2 counter: a mutant-kill tally's accept/reject verdict against a frozen expected verdict per
receipt-set case (census/round-76/c2-population.tsv).

The tally under test is run once per case, from the lane root, as
  python3 -B <tally> --pristine <receipt> --mutant ID=<receipt> [...]
(the r75 tally's interface, census/round-75/c2-kill-counter.py, unchanged). Its exit code is the verdict:
0 = the receipt set is accepted as "every mutant killed, pristine green", 1 = rejected. A run that exits
anything else, or prints no `SUMMARY ` line, is an error, never a match.

Cases: h-* honest sets (must be accepted, or rejected for a genuine survivor), u-* unread receipt classes
(EXIT=2 with fail>=1; fail=0 with EXIT=1), b-* receipt-to-mutant binding forgeries (a receipt filed
under another mutant's id, an unknown id, a pristine receipt of another counter, a receipt whose own
EXIT lines disagree).

Output: `ROW <case> expect=<e> got=<g> match=<yes|no|error>` per case, then
`SUMMARY cases=<N> mismatches=<M> errors=<E>`; exit 0 iff M == 0 and E == 0, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.normpath(os.path.join(HERE, "..", ".."))


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tally", required=True, help="tally script under test (path; lane-relative or absolute)")
    ns = ap.parse_args(argv)
    tally = ns.tally if os.path.isabs(ns.tally) else os.path.join(LANE, ns.tally)
    if not os.path.isfile(tally):
        print(f"C2-COUNTER-FATAL: no tally at {tally}", file=sys.stderr)
        return 2
    pop = os.path.join(HERE, "c2-population.tsv")
    cases = []
    with open(pop, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            cid, exp, pristine, mutants = line.rstrip("\n").split("\t")
            if exp not in ("0", "1"):
                print(f"C2-COUNTER-FATAL: bad expectation in {cid}", file=sys.stderr)
                return 2
            cases.append((cid, exp, pristine, mutants.split()))
    print(f"# tally path={tally} sha256={sha(tally)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))}")
    mism = errs = 0
    for cid, exp, pristine, mutants in cases:
        argv2 = ["python3", "-B", tally, "--pristine", pristine]
        for m in mutants:
            argv2 += ["--mutant", m]
        p = subprocess.run(argv2, cwd=LANE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        text = p.stdout.decode("utf-8", "replace")
        summ = [l for l in text.splitlines() if l.startswith("SUMMARY ")]
        got = str(p.returncode)
        if p.returncode not in (0, 1) or len(summ) != 1:
            errs += 1
            print(f"ROW {cid} expect={exp} got={got} match=error")
            for l in text.splitlines()[-3:]:
                print(f"#  {cid} {l[:200]}")
            continue
        ok = got == exp
        mism += 0 if ok else 1
        print(f"ROW {cid} expect={exp} got={got} match={'yes' if ok else 'no'} {summ[0]}")
    print(f"SUMMARY cases={len(cases)} mismatches={mism} errors={errs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
