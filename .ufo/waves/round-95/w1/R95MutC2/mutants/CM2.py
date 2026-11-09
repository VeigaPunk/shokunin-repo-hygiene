#!/usr/bin/env python3
"""souji r95 C2 counter: does a forgery probe keep setup failures off its verdict exit code?

The r94 counter (census/round-94/c2-setup-arms.py) with six more setup arms (S9-S14) and a per-arm timeout. S9-S12
are the setup failures the r94 wave found the r94 probe still exiting 1 on, or waiting forever on (r94 closure routed
defect 3; plans/round-94.md A4); S13/S14 bind the two r94 setup checks no r94 arm exercised (R94MutC2 M10, M11).

Runs the probe named by --probe under sixteen arms and checks each arm's exit code and one required output line. Two
arms are verdict arms (the probe must still say "all eight rejected" with exit 0, and "a forgery survived" with exit
1); eight are setup arms (the probe must either run normally or refuse with exit 2 and a `C2-FORGERY-FATAL:` line —
never exit 1, which means "a forgery survived").

  P1 verdict-pass   r93 fixture, filed tool, r91 before, fresh --work      -> exit 0, `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`
  P2 verdict-fail   r92 fixture (F5/F6/F7 pass it), fresh --work          -> exit 1, `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass`
  S1 work-empty     as P1 but --work is an existing EMPTY directory        -> exit 0, `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`
  S2 work-nonempty  --work is a directory holding one file                 -> exit 2, `C2-FORGERY-FATAL:`
  S3 work-file      --work is an existing regular file                     -> exit 2, `C2-FORGERY-FATAL:`
  S4 fixture-absent --fixture names a path that does not exist             -> exit 2, `C2-FORGERY-FATAL:`
  S5 tool-absent    --tool names a path that does not exist                -> exit 2, `C2-FORGERY-FATAL:`
  S6 before-absent  --before names a path that does not exist              -> exit 2, `C2-FORGERY-FATAL:`
  S7 fixture-mute   a fixture that exits 1 and prints nothing              -> exit 2, `C2-FORGERY-FATAL:`
  S8 fixture-crash  a fixture that prints a passing SUMMARY for the filed
                    tool and raises (no SUMMARY) for any other tool        -> exit 2, `C2-FORGERY-FATAL:`
  S9 tool-nonutf8   --tool is the filed tool plus one comment line holding
                    the byte 0xFF (not UTF-8)                              -> exit 2, `C2-FORGERY-FATAL:`
  S10 before-nonutf8 --before is the r91 tool plus the same 0xFF line     -> exit 2, `C2-FORGERY-FATAL:`
  S11 work-fileparent --work is <regular file>/sub                         -> exit 2, `C2-FORGERY-FATAL:`
  S12 fixture-hang  a fixture that sleeps forever                          -> exit 2, `C2-FORGERY-FATAL:`
                    (the counter kills an arm after --arm-timeout seconds, default 300, and scores it `exit=hung`)
  S13 work-tmp      --work is an absent path under /tmp                    -> exit 2, `C2-FORGERY-FATAL:`
  S14 edit-twice    --tool is the filed tool plus a string literal holding
                    a second copy of forgery F3's edit target              -> exit 2, `C2-FORGERY-FATAL:`

The S7/S8/S12 fixtures and the S9/S10/S14 copies are written by this counter under --work (their bytes are printed as
sha256); S13 names a /tmp path the counter never creates. Output: one `ARM <id> exit=<rc|hung> want=<rc>
line=<yes|no> conform=<yes|no>` per arm and `ARMS-SUMMARY arms=16 conform=<k>`. Exit 0 iff k == 16; 1 otherwise;
2 on setup error. Scratch only under --work (never /tmp).
"""
import argparse
import concurrent.futures as cf
import hashlib
import os
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
PASS8 = "FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass"
FAIL5 = "FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass"
FATAL = "C2-FORGERY-FATAL:"
MUTE = "import sys\nsys.exit(1)\n"
CRASH = """import sys
tool = sys.argv[sys.argv.index("--tool") + 1]
if tool == %r:
    print("SUMMARY cases=1 tool_pass=1 before_pass=0")
    sys.exit(0)
raise RuntimeError("fixture-crash arm: no SUMMARY for " + tool)
"""
HANG = "import time\nwhile True:\n    time.sleep(3600)\n"
F3_OLD = "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n"


def main(argv):
    ap = argparse.ArgumentParser()
    for a in ("--probe", "--fixture-pass", "--fixture-fail", "--tool", "--before", "--work"):
        ap.add_argument(a, required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--arm-timeout", type=int, default=300)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-ARMS-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print(f"C2-ARMS-FATAL: --work {work} is not an empty directory", file=sys.stderr)
        return 2
    probe, fpass, ffail, tool, before = (os.path.abspath(x) for x in
                                         (ns.probe, ns.fixture_pass, ns.fixture_fail, ns.tool, ns.before))
    for k, v in (("probe", probe), ("fixture-pass", fpass), ("fixture-fail", ffail), ("tool", tool),
                 ("before", before)):
        if not os.path.isfile(v):
            print(f"C2-ARMS-FATAL: --{k} {v} is not a file", file=sys.stderr)
            return 2
    os.makedirs(work, exist_ok=True)
    for k, v in (("probe", probe), ("fixture-pass", fpass), ("fixture-fail", ffail), ("tool", tool),
                 ("before", before), ("counter", os.path.abspath(__file__))):
        with open(v, "rb") as f:
            print(f"# {k} path={v} sha256={hashlib.sha256(f.read()).hexdigest()}")
    mute, crash = os.path.join(work, "fixture-mute.py"), os.path.join(work, "fixture-crash.py")
    with open(mute, "w", encoding="utf-8") as f:
        f.write(MUTE)
    with open(crash, "w", encoding="utf-8") as f:
        f.write(CRASH % tool)
    hang = os.path.join(work, "fixture-hang.py")
    with open(hang, "w", encoding="utf-8") as f:
        f.write(HANG)
    tool_bad, before_bad, tool_dup = (os.path.join(work, n) for n in ("tool-nonutf8.py", "before-nonutf8.py",
                                                                      "tool-edit-twice.py"))
    with open(tool, "rb") as f:
        tool_bytes = f.read()
    with open(before, "rb") as f:
        before_bytes = f.read()
    if tool_bytes.decode("utf-8").count(F3_OLD) != 1:
        print("C2-ARMS-FATAL: the filed tool does not hold F3's edit target exactly once", file=sys.stderr)
        return 2
    with open(tool_bad, "wb") as f:
        f.write(tool_bytes + b"# \xff not utf-8 (S9)\n")
    with open(before_bad, "wb") as f:
        f.write(before_bytes + b"# \xff not utf-8 (S10)\n")
    with open(tool_dup, "wb") as f:
        f.write(tool_bytes + ("_SOUJI_R95_S14 = \"\"\"\n" + F3_OLD + "\"\"\"\n").encode("utf-8"))
    for k, v in (("fixture-mute", mute), ("fixture-crash", crash), ("fixture-hang", hang), ("tool-nonutf8", tool_bad),
                 ("before-nonutf8", before_bad), ("tool-edit-twice", tool_dup)):
        with open(v, "rb") as f:
            print(f"# {k} sha256={hashlib.sha256(f.read()).hexdigest()}")
    a = lambda i: os.path.join(work, i)  # noqa: E731
    os.makedirs(a("S1"))
    os.makedirs(a("S2"))
    with open(os.path.join(a("S2"), "keep"), "w") as f:
        f.write("x\n")
    with open(a("S3"), "w") as f:
        f.write("x\n")
    missing = a("absent-path")
    with open(a("S11-parent"), "w") as f:
        f.write("x\n")
    tmp_work = f"/tmp/souji-r95-arm-S13-{os.getpid()}-absent"
    if os.path.lexists(tmp_work):
        print(f"C2-ARMS-FATAL: {tmp_work} exists", file=sys.stderr)
        return 2
    arms = (
        ("P1", fpass, tool, before, a("P1"), 0, PASS8),
        ("P2", ffail, tool, before, a("P2"), 1, FAIL5),
        ("S1", fpass, tool, before, a("S1"), 0, PASS8),
        ("S2", fpass, tool, before, a("S2"), 2, FATAL),
        ("S3", fpass, tool, before, a("S3"), 2, FATAL),
        ("S4", missing, tool, before, a("S4"), 2, FATAL),
        ("S5", fpass, missing, before, a("S5"), 2, FATAL),
        ("S6", fpass, tool, missing, a("S6"), 2, FATAL),
        ("S7", mute, tool, before, a("S7"), 2, FATAL),
        ("S8", crash, tool, before, a("S8"), 2, FATAL),
        ("S9", fpass, tool_bad, before, a("S9"), 2, FATAL),
        ("S10", fpass, tool, before_bad, a("S10"), 2, FATAL),
        ("S11", fpass, tool, before, os.path.join(a("S11-parent"), "sub"), 2, FATAL),
        ("S12", hang, tool, before, a("S12"), 2, FATAL),
        ("S13", fpass, tool, before, tmp_work, 2, FATAL),
        ("S14", fpass, tool_dup, before, a("S14"), 2, FATAL),
    )

    def one(arm):
        aid, fx, tl, bf, wk, want, line = arm
        p = subprocess.Popen([sys.executable, "-B", probe, "--fixture", fx, "--tool", tl, "--before", bf,
                              "--work", wk], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            so, se = p.communicate(timeout=ns.arm_timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            so, se = p.communicate()
            rc = "hung"
        text = so.decode("utf-8", "replace") + "\n--stderr--\n" + se.decode("utf-8", "replace")
        with open(a(f"{aid}.out"), "w", encoding="utf-8") as f:
            f.write(text + (f"\n--hung: killed after --arm-timeout {ns.arm_timeout}s--\n" if rc == "hung" else ""))
        stream = so
        has = any(l.startswith(line) for l in stream.decode("utf-8", "replace").splitlines())
        return aid, rc, want, has

    with cf.ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        res = list(ex.map(one, arms))
    conform = 0
    for aid, rc, want, has in res:
        ok = rc == want and has
        conform += ok
        print(f"ARM {aid} exit={rc} want={want} line={'yes' if has else 'no'} conform={'yes' if ok else 'no'}")
    print(f"ARMS-SUMMARY arms={len(arms)} conform={conform}")
    return 0 if conform == len(arms) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
