#!/usr/bin/env python3
"""c2-harness.py — souji round-70 C2 (calibration) instrument-mutant harness.

Scores one c1-counter.py file (the r69 frozen counter, the r70 counter, or a control variant) on
whether its OWN self-checks catch four frozen instrument mutants and one battery-member tamper.

  positive arms (must pass, else the run is INVALID, EXIT=2 — a counter that refuses everything is
  not a gain):
    P-SELFTEST  the unmutated counter's --selftest exits 0
    P-BATTERY   the unmutated counter's battery arm over the untampered member D01 exits 0
  mutants (each applied by one regex that must match exactly once in the counter text; a counter
  where a pattern does not match exactly once is INVALID, EXIT=2):
    CM1  Q131 precedence swap: the forgery and over-refusal branches of classify_outcome trade places
    CM2  expectation gate off: `all_match = False` after `if obs != exp:` becomes `pass`
    CM3  echo judge blind: `if val and val in stderr:` becomes `if False:`
    CM4  survived gate off: `tally["survived"] == 0 and ` is removed from the battery rc
    a mutant is KILLED iff the mutated counter's --selftest exits non-zero; SURVIVED otherwise.
  tamper:
    T1   a copy of the battery dir whose D01.py bytes are replaced by D05.py's (both expected
         `forgery`; SHA256SUMS untouched); the unmutated counter's battery arm over D01 is DETECTED
         iff it exits non-zero, UNDETECTED iff it exits 0.

  SUMMARY label=<L> positive_selftest=PASS|FAIL positive_battery=PASS|FAIL mutants=4 killed=<k>
          survived=<s> tamper=detected|undetected score=<s + (1 if undetected)>
  EXIT=0 iff both positives PASS and score=0; EXIT=1 iff both positives PASS and score>0;
  EXIT=2 otherwise (invalid run).

Stdlib only. Writes only under --work (and --receipt). The counter under test is copied into
--work and run from there; the lane is read, never written.

Usage:
  python3 -B c2-harness.py --label L --counter FILE --matrix FILE --root LANE --base-rev FULL40 \
      --battery-dir DIR --battery-manifest FILE --work DIR [--receipt FILE]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys

HARNESS_REL = "census/round-70/c2-harness.py"

MUTANTS = [
    ("CM1", "precedence swap forgery<->over-refusal", None, None),
    ("CM2", "expectation gate off",
     r"(if obs != exp:\n[ ]+)all_match = False", r"\1pass"),
    ("CM3", "echo judge blind",
     r"if val and val in stderr:", "if False:"),
    ("CM4", "survived gate off",
     r'all_match and tally\["survived"\] == 0 and ', "all_match and "),
]

FORGERY_BLOCK = '    if forgeries:\n        return "forgery"\n'
HONEST_BLOCK = '    if honest:\n        return "over-refusal"\n'


def apply_mutant(text: str, mid: str, pat, repl) -> tuple[str | None, str]:
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


def run(argv: list[str], cwd: str) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=env, timeout=1800)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def last(text: str, prefix: str) -> str:
    hits = [l for l in text.splitlines() if l.startswith(prefix)]
    return hits[-1] if hits else f"{prefix}<none>"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="c2-harness.py")
    for a in ("--label", "--counter", "--matrix", "--root", "--base-rev", "--battery-dir",
              "--battery-manifest", "--work"):
        ap.add_argument(a, required=True)
    ap.add_argument("--receipt")
    ns = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", ns.base_rev):
        print("C2-HARNESS-FATAL: --base-rev must be full 40-hex", file=sys.stderr)
        print("EXIT=2")
        return 2
    root = os.path.abspath(ns.root)
    work = os.path.abspath(ns.work)
    rp = os.path.realpath(work)
    for bad in ("/tmp", "/var/tmp", os.path.realpath(root)):
        if rp == bad or rp.startswith(bad + os.sep):
            print(f"C2-HARNESS-FATAL: --work must not live under {bad}", file=sys.stderr)
            print("EXIT=2")
            return 2
    base = os.path.join(work, ns.label)
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    with open(ns.counter, "rb") as f:
        counter_bytes = f.read()
    text = counter_bytes.decode("utf-8")
    matrix = os.path.abspath(ns.matrix)
    manifest = os.path.abspath(ns.battery_manifest)
    bdir = os.path.abspath(ns.battery_dir)
    out: list[str] = []

    def emit(line: str) -> None:
        print(line, flush=True)
        out.append(line)

    emit(f"# c2-harness label={ns.label} counter={os.path.abspath(ns.counter)} "
         f"counter_sha256={hashlib.sha256(counter_bytes).hexdigest()} base-rev={ns.base_rev}")
    emit(f"# matrix={matrix} sha256={hashlib.sha256(open(matrix, 'rb').read()).hexdigest()}")

    def selftest(path: str, tag: str) -> tuple[int, str]:
        w = os.path.join(base, f"w-{tag}")
        os.makedirs(w, exist_ok=True)
        rc, txt = run([sys.executable, "-B", path, "--selftest", "--root", root, "--matrix", matrix,
                       "--base-rev", ns.base_rev, "--work", w], cwd=base)
        return rc, txt

    def battery(path: str, battery_dir: str, tag: str) -> tuple[int, str]:
        w = os.path.join(base, f"w-{tag}")
        os.makedirs(w, exist_ok=True)
        return run([sys.executable, "-B", path, "--root", root, "--matrix", matrix,
                    "--base-rev", ns.base_rev, "--work", w, "--battery-manifest", manifest,
                    "--battery-dir", battery_dir, "--only", "D01"], cwd=base)

    orig = os.path.join(base, "orig", "c1-counter.py")
    os.makedirs(os.path.dirname(orig))
    with open(orig, "wb") as f:
        f.write(counter_bytes)

    p_rc, p_txt = selftest(orig, "pos-selftest")
    pos_self = "PASS" if p_rc == 0 else "FAIL"
    emit(f"POSITIVE P-SELFTEST rc={p_rc} {last(p_txt, 'SELFTEST')} verdict={pos_self}")
    b_rc, b_txt = battery(orig, bdir, "pos-battery")
    pos_batt = "PASS" if b_rc == 0 else "FAIL"
    emit(f"POSITIVE P-BATTERY rc={b_rc} {last(b_txt, 'MUTANT D01')} verdict={pos_batt}")

    invalid = False
    killed = survived = 0
    for mid, desc, pat, repl in MUTANTS:
        mtext, why = apply_mutant(text, mid, pat, repl)
        if mtext is None:
            emit(f"MUTANT {mid} apply=FAIL reason={why}")
            invalid = True
            continue
        mpath = os.path.join(base, mid, "c1-counter.py")
        os.makedirs(os.path.dirname(mpath))
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(mtext)
        rc, txt = selftest(mpath, mid)
        fate = "killed" if rc != 0 else "survived"
        killed += fate == "killed"
        survived += fate == "survived"
        emit(f"MUTANT {mid} desc={desc!r} sha256={hashlib.sha256(mtext.encode()).hexdigest()[:16]} "
             f"selftest_rc={rc} {last(txt, 'SELFTEST')} fate={fate}")

    tdir = os.path.join(base, "tampered-battery")
    shutil.copytree(bdir, tdir, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(os.path.join(bdir, "D05.py"), os.path.join(tdir, "D01.py"))
    t_rc, t_txt = battery(orig, tdir, "tamper")
    tamper = "detected" if t_rc != 0 else "undetected"
    fatal = [l for l in t_txt.splitlines() if "FATAL" in l]
    emit(f"TAMPER T1 rc={t_rc} {last(t_txt, 'MUTANT D01')} fatal={fatal[-1] if fatal else '-'} "
         f"fate={tamper}")

    score = survived + (1 if tamper == "undetected" else 0)
    emit(f"SUMMARY label={ns.label} positive_selftest={pos_self} positive_battery={pos_batt} "
         f"mutants={len(MUTANTS)} killed={killed} survived={survived} tamper={tamper} score={score}")
    if invalid or pos_self != "PASS" or pos_batt != "PASS":
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
