#!/usr/bin/env python3
"""Generate one-edit mutants of the r95 probe (PM*) and arms counter (CM*).
Each mutant is the pristine file with exactly one string replacement applied
(asserted to occur exactly once). Originals come from the lane (read-only);
mutants land next to this script, under muted-by-mutants/.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "mutants")
os.makedirs(OUT, exist_ok=True)

PROBE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-95/c2-forgery-probe.py"
COUNTER = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-95/c2-setup-arms.py"

PM: list = [
    ("PM1", PROBE,
     "        return data.decode(\"utf-8\")",
     "        return data.decode(\"utf-8-sig\")",
     "read_utf8: decode variant; 0xFF still raises -> same S9/S10 exit 2?"),
    ("PM2", PROBE,
     '''    try:
        os.makedirs(work, exist_ok=True)
    except OSError as exc:
        raise Fatal(f"--work {work} cannot be created: {exc.strerror or exc}")''',
     "    os.makedirs(work, exist_ok=True)",
     "makedirs try/except removed: does cli()'s OSError handler cover S11?"),
    ("PM3", PROBE,
     '        raise Fatal(f"cannot write {path}: {exc.strerror or exc}")',
     "        pass",
     "write(): silently ignore write failures (no arm forces one after checks)"),
    ("PM4", PROBE,
     "            os.killpg(p.pid, signal.SIGKILL)",
     "            os.killpg(p.pid, signal.SIGTERM)",
     "timeout kill: SIGTERM instead of SIGKILL (hang fixture still dies)"),
    ("PM5", PROBE,
     '''    except Exception as exc:  # an internal error is not a verdict: never exit 1 for it
        print(f"C2-FORGERY-FATAL: internal error {type(exc).__name__}: {exc}", file=sys.stderr)
''',
     "",
     "cli(): catch-all removed (no arm is known to trigger it)"),
    ("PM6", PROBE,
     "    if ns.timeout <= 0:",
     "    if ns.timeout < 0:",
     "cli: --timeout<=0 check weakened (counter never passes --timeout)"),
    ("PM7", PROBE,
     "    return 0 if positive and rejected == len(FORGERIES) else 1",
     "    return 0 if rejected == len(FORGERIES) else 1",
     "verdict: the `positive and` requirement dropped (no arm distinguishes)"),
    ("PM8", PROBE,
     "        os.makedirs(work, exist_ok=True)",
     "        os.makedirs(work, exist_ok=False)",
     "makedirs exist_ok -> False: S1 (existing empty --work) must break"),
    ("PM9", PROBE,
     '    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):',
     '    if os.path.realpath(work).startswith(("/var/tmp/", "/dev/shm/")):',
     "--work /tmp check minus /tmp/: S13 (absent /tmp path) must break"),
    ("PM10", PROBE,
     '        print(f"C2-FORGERY-FATAL: {exc}", file=sys.stderr)',
     '        print(f"C2-FATAL: {exc}", file=sys.stderr)',
     "cli Fatal handler: prefix broken (every FATAL line check must fail)"),
]

CM: list = [
    ("CM1", COUNTER,
     '        ("S14", fpass, tool_dup, before, a("S14"), 2, FATAL),',
     '        ("S14", fpass, tool, before, a("S14"), 2, FATAL),',
     "counter: S14 gets the valid tool (input copy removed)"),
    ("CM2", COUNTER,
     "        stream = se if line == FATAL else so",
     "        stream = so",
     "counter: line check always scans stdout (FATAL is on stderr)"),
    ("CM3", COUNTER,
     '    ap.add_argument("--arm-timeout", type=int, default=300)',
     '    ap.add_argument("--arm-timeout", type=int, default=1)',
     "counter: per-arm timeout 300s -> 1s (legit runs all exceed it)"),
]


def emit(mid, src, old, new, note):
    with open(src) as f:
        text = f.read()
    n = text.count(old)
    assert n == 1, f"{mid}: replacement occurs {n}x, want 1"
    text = text.replace(old, new, 1)
    dst = os.path.join(OUT, f"{mid}.py")
    with open(dst, "w") as f:
        f.write(text)
    sha = hashlib.sha256(text.encode()).hexdigest()[:12]
    print(f"{mid}: {dst} sha={sha} :: {note}")


def main():
    for mid, src, old, new, note in PM + CM:
        emit(mid, src, old, new, note)
    print(f"total={len(PM) + len(CM)} mutants in {OUT}")


main()
