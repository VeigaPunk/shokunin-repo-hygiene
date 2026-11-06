#!/usr/bin/env python3
"""In-process probes of the survivors: call the pure functions of the pristine and the mutated
counter on inputs the frozen selftest never builds, and on the frozen battery's real SHA256SUMS."""
import hashlib
import importlib.util
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PRISTINE = os.path.join(S, "c1-counter.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    pr = load(PRISTINE, "pristine")
    muts = {x: load(os.path.join(S, "mut", x, "c1-counter.py"), x.lower())
            for x in ("X6", "X7", "X8", "X9", "X10")}

    print("== X6 battery_verdict: a manifest entry EXPECTING 'error' ==")
    for label, mod in (("pristine", pr), ("X6", muts["X6"])):
        t, a, rc = mod.battery_verdict([("E", "error", "error")])
        print(f"  {label}: tally={t} all_match={a} rc={rc}")
    print("== X6 battery_verdict: an observed error against a non-error expectation ==")
    for label, mod in (("pristine", pr), ("X6", muts["X6"])):
        t, a, rc = mod.battery_verdict([("E", "error", "forgery")])
        print(f"  {label}: tally={t} all_match={a} rc={rc}")

    print("== X7 clean_env: ambient GIT_LITERAL_PATHSPECS=1 ==")
    os.environ["GIT_LITERAL_PATHSPECS"] = "1"
    os.environ["GIT_GLOB_PATHSPECS"] = "1"
    os.environ["GIT_NOGLOB_PATHSPECS"] = "1"
    os.environ["GIT_ICASE_PATHSPECS"] = "1"
    for label, mod in (("pristine", pr), ("X7", muts["X7"])):
        e = mod.clean_env()
        kept = {k: e.get(k) for k in ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS",
                                      "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS")}
        print(f"  {label}: kept={kept}")
    for k in ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS",
              "GIT_ICASE_PATHSPECS"):
        del os.environ[k]

    print("== X8 case_env: a row carrying pathspec_env ==")
    spec = {"pathspec_env": {"GIT_LITERAL_PATHSPECS": "1"}}
    for label, mod in (("pristine", pr), ("X8", muts["X8"])):
        print(f"  {label}: case_env={mod.case_env(spec, '/nonexistent-repo')!r}")

    bd = os.path.join(S, "probe-battery")
    os.makedirs(bd, exist_ok=True)
    open(os.path.join(bd, "M1.py"), "wb").write(b"print('m1')\n")
    d1 = hashlib.sha256(b"print('m1')\n").hexdigest()
    open(os.path.join(bd, "SHA256SUMS"), "w").write(f"{d1}  M1.py\n{d1}  M1.py\n")
    print("== X9 verify_members: SHA256SUMS lists M1.py TWICE (well-formed, same digest) ==")
    for label, mod in (("pristine", pr), ("X9", muts["X9"])):
        v, e = mod.verify_members(bd, ["M1"])
        print(f"  {label}: accepted={v is not None} reason={e!r}")

    open(os.path.join(bd, "SHA256SUMS"), "w").write("this line is not a sha256 line\n")
    print("== X10 verify_members: SHA256SUMS has a MALFORMED line ==")
    for label, mod in (("pristine", pr), ("X10", muts["X10"])):
        v, e = mod.verify_members(bd, ["M1"])
        print(f"  {label}: accepted={v is not None} reason={e!r}")

    print("== every survivor on the FROZEN battery dir (real SHA256SUMS, 28 entries) ==")
    real = os.path.join(L, "census/round-69/battery")
    names = [l.split()[1][:-3] for l in open(os.path.join(real, "SHA256SUMS")) if l.strip()]
    for label, mod in [("pristine", pr)] + [(x, muts[x]) for x in ("X6", "X7", "X8", "X9", "X10")]:
        v, e = mod.verify_members(real, names)
        print(f"  {label}: members={len(names)} accepted={v is not None} reason={e!r}")


if __name__ == "__main__":
    sys.exit(main())
