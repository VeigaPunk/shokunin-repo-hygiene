#!/usr/bin/env python3
"""c2-harness.py — souji round-71 C2 (calibration) instrument-mutant harness.

Scores one c1-counter.py file (the frozen r70 counter, the r71 counter, or a control variant) on
whether its OWN --selftest kills the five counter mutants that survived the r70 counter's selftest
(S70MutCounter X6-X10, frozen as exact string edits in census/round-71/c2-mutants.json; each edit
reproduces the seat's committed mutant file byte for byte when applied to the r70 counter), plus
the four carried r70 harness mutants CM1-CM4 (regression: they must stay killed).

  positive arm (must pass, else INVALID, EXIT=2 — a counter that fails everything is not a gain):
    P-SELFTEST  the unmutated counter's --selftest exits 0 and prints `fail=0`
  mutants: every edit must match exactly once in the counter text, else INVALID (EXIT=2).
    A mutant is KILLED iff the mutated counter's --selftest exits non-zero AND prints a
    `SELFTEST cases=N pass=P fail=F` line with F >= 1 (a crash without a SELFTEST line is
    `crashed`, which is not a kill). Otherwise SURVIVED (or crashed).

  SUMMARY label=<L> positive_selftest=PASS|FAIL x_mutants=5 x_killed=<k> x_survived=<s>
          cm_mutants=4 cm_killed=<k> cm_survived=<s> score=<x_survived + cm_survived>
  EXIT=0 iff the positive passes and score=0; EXIT=1 iff the positive passes and score>0;
  EXIT=2 otherwise.

r71 hardening (S70Sentinel F5/F6): --label must be one plain path component; the per-label run
directory is removed after the run unless --keep. Stdlib only. Writes only under --work (and
--receipt, created exclusively).

Usage:
  python3 -B c2-harness.py --label L --counter FILE --matrix FILE --root LANE --base-rev FULL40 \
      --mutants census/round-71/c2-mutants.json --work DIR [--receipt FILE] [--keep]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

HARNESS_REL = "census/round-71/c2-harness.py"
LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)$", re.M)

CM = [
    ("CM1", "precedence swap forgery<->over-refusal", None, None),
    ("CM2", "expectation gate off", r"(if obs != exp:\n[ ]+)all_match = False", r"\1pass"),
    ("CM3", "echo judge blind", r"if val and val in stderr:", "if False:"),
    ("CM4", "survived gate off", r'all_match and tally\["survived"\] == 0 and ', "all_match and "),
]
FORGERY_BLOCK = '    if forgeries:\n        return "forgery"\n'
HONEST_BLOCK = '    if honest:\n        return "over-refusal"\n'


def apply_cm(text: str, mid: str, pat, repl) -> tuple[str | None, str]:
    if mid == "CM1":
        nf, nh = text.count(FORGERY_BLOCK), text.count(HONEST_BLOCK)
        if nf != 1 or nh != 1:
            return None, f"forgery_block={nf} honest_block={nh} (want 1 and 1)"
        t = text.replace(FORGERY_BLOCK, "\0F\0").replace(HONEST_BLOCK, FORGERY_BLOCK)
        return t.replace("\0F\0", HONEST_BLOCK), "ok"
    n = len(re.findall(pat, text))
    if n != 1:
        return None, f"pattern matched {n} times (want 1)"
    return re.sub(pat, repl, text, count=1), "ok"


def apply_x(text: str, old: str, new: str) -> tuple[str | None, str]:
    n = text.count(old)
    if n != 1:
        return None, f"edit matched {n} times (want 1)"
    return text.replace(old, new, 1), "ok"


def run(argv: list[str], cwd: str) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=env, timeout=1800)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def selftest_line(text: str) -> tuple[str, int | None]:
    hits = SELFTEST_RE.findall(text)
    if not hits:
        return "SELFTEST<none>", None
    c, p, f = hits[-1]
    return f"SELFTEST cases={c} pass={p} fail={f}", int(f)


def fate_of(rc: int, fail: int | None) -> str:
    if fail is None:
        return "crashed"
    return "killed" if (rc != 0 and fail >= 1) else "survived"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="c2-harness.py")
    for a in ("--label", "--counter", "--matrix", "--root", "--base-rev", "--mutants", "--work"):
        ap.add_argument(a, required=True)
    ap.add_argument("--receipt")
    ap.add_argument("--keep", action="store_true")
    ns = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", ns.base_rev):
        print("C2-HARNESS-FATAL: --base-rev must be full 40-hex", file=sys.stderr)
        print("EXIT=2")
        return 2
    if not LABEL_RE.match(ns.label):
        print("C2-HARNESS-FATAL: --label must be one plain path component", file=sys.stderr)
        print("EXIT=2")
        return 2
    root = os.path.abspath(ns.root)
    work = os.path.abspath(ns.work)
    rp = os.path.realpath(work)
    if not os.path.isdir(rp):
        print(f"C2-HARNESS-FATAL: --work does not exist: {work}", file=sys.stderr)
        print("EXIT=2")
        return 2
    for bad in ("/tmp", "/var/tmp", os.path.realpath(root)):
        if rp == bad or rp.startswith(bad + os.sep):
            print(f"C2-HARNESS-FATAL: --work must not live under {bad}", file=sys.stderr)
            print("EXIT=2")
            return 2
    base = os.path.join(rp, ns.label)
    if os.path.realpath(os.path.dirname(base)) != rp:
        print("C2-HARNESS-FATAL: label escapes --work", file=sys.stderr)
        print("EXIT=2")
        return 2
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    try:
        return _score(ns, argv, root, base)
    finally:
        if not ns.keep:
            shutil.rmtree(base, ignore_errors=True)


def _score(ns, argv: list[str], root: str, base: str) -> int:
    with open(ns.counter, "rb") as f:
        counter_bytes = f.read()
    text = counter_bytes.decode("utf-8")
    matrix = os.path.abspath(ns.matrix)
    with open(ns.mutants, "rb") as f:
        mutants_bytes = f.read()
    xm = json.loads(mutants_bytes.decode("utf-8"))["mutants"]
    out: list[str] = []

    def emit(line: str) -> None:
        print(line, flush=True)
        out.append(line)

    emit(f"# c2-harness label={ns.label} counter={os.path.abspath(ns.counter)} "
         f"counter_sha256={hashlib.sha256(counter_bytes).hexdigest()} base-rev={ns.base_rev}")
    emit(f"# matrix={matrix} sha256={hashlib.sha256(open(matrix, 'rb').read()).hexdigest()}")
    emit(f"# mutants={os.path.abspath(ns.mutants)} sha256={hashlib.sha256(mutants_bytes).hexdigest()}")

    def selftest(path: str, tag: str) -> tuple[int, str]:
        w = os.path.join(base, f"w-{tag}")
        os.makedirs(w, exist_ok=True)
        return run([sys.executable, "-B", path, "--selftest", "--root", root, "--matrix", matrix,
                    "--base-rev", ns.base_rev, "--work", w], cwd=base)

    orig = os.path.join(base, "orig", "c1-counter.py")
    os.makedirs(os.path.dirname(orig))
    with open(orig, "wb") as f:
        f.write(counter_bytes)
    p_rc, p_txt = selftest(orig, "pos-selftest")
    p_line, p_fail = selftest_line(p_txt)
    pos_self = "PASS" if (p_rc == 0 and p_fail == 0) else "FAIL"
    emit(f"POSITIVE P-SELFTEST rc={p_rc} {p_line} verdict={pos_self}")

    invalid = False
    tallies = {"x": [0, 0], "cm": [0, 0]}

    def score_one(group: str, mid: str, desc: str, mtext: str | None, why: str) -> None:
        nonlocal invalid
        if mtext is None:
            emit(f"MUTANT {mid} apply=FAIL reason={why}")
            invalid = True
            return
        mpath = os.path.join(base, mid, "c1-counter.py")
        os.makedirs(os.path.dirname(mpath))
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(mtext)
        rc, txt = selftest(mpath, mid)
        line, fail = selftest_line(txt)
        fate = fate_of(rc, fail)
        tallies[group][0 if fate == "killed" else 1] += 1
        emit(f"MUTANT {mid} desc={desc!r} sha256={hashlib.sha256(mtext.encode()).hexdigest()[:16]} "
             f"selftest_rc={rc} {line} fate={fate}")

    for m in xm:
        mtext, why = apply_x(text, m["old"], m["new"])
        score_one("x", m["id"], m["desc"], mtext, why)
    for mid, desc, pat, repl in CM:
        mtext, why = apply_cm(text, mid, pat, repl)
        score_one("cm", mid, desc, mtext, why)

    score = tallies["x"][1] + tallies["cm"][1]
    emit(f"SUMMARY label={ns.label} positive_selftest={pos_self} x_mutants={len(xm)} "
         f"x_killed={tallies['x'][0]} x_survived={tallies['x'][1]} cm_mutants={len(CM)} "
         f"cm_killed={tallies['cm'][0]} cm_survived={tallies['cm'][1]} score={score}")
    if invalid or pos_self != "PASS":
        rc = 2
    else:
        rc = 0 if score == 0 else 1
    emit(f"EXIT={rc}")
    if ns.receipt:
        hsha = hashlib.sha256(open(os.path.realpath(__file__), "rb").read()).hexdigest()
        with open(ns.receipt, "x", encoding="utf-8") as f:
            f.write(f"rev={ns.base_rev}\ninstrument={HARNESS_REL}\ninstrument_sha256={hsha}\n")
            f.write("command=python3 -B " + " ".join(shlex.quote(a) for a in [HARNESS_REL, *argv]) + "\n")
            for line in out:
                f.write(line + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
