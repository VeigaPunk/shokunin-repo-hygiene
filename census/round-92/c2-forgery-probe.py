#!/usr/bin/env python3
"""souji r92 C2 forgery probe: does the r92 fixture refuse tools that fake the r92 cut repair?

Each forgery is ONE text edit (applied exactly once) to a pinned tool's bytes, run through the committed fixture
(tests/fixtures/r92-k4-flagfail.py) as `--tool`, with the r91 tool as `--before`. A forgery is REJECTED iff the
fixture exits 1 with tool_pass < cases. The positive control is the filed tool, which must exit 0 at cases/cases;
the negative control is the unmodified r91 tool, which must be rejected too.

  F1 ab-special   r91 tool + a special case that keeps the tail cut when an F0 lead is followed by 0x80 (fixes the
                  R91 repro pair, nothing else)
  F2 cont-only    r91 tool + the r91 A2 routed repair WITHOUT range checks: move the tail cut only when every
                  declared byte is a continuation and the sequence ends inside the payload
  F3 no-tail      filed tool with `_cut_tail` returning the cut unchanged
  F4 no-head      filed tool with `_cut_head` returning the cut unchanged
  N0 r91          the r91 tool bytes unchanged (do-nothing control)

Output: `FORGERY <id> exit=<rc> tool_pass=<n>/<cases> rejected=<yes|no>` and
`FORGERY-SUMMARY forgeries=5 rejected=<k> positive=<pass|fail>`. Exit 0 iff all five are rejected and the positive
control passes; 1 otherwise; 2 on setup error. Scratch only under --work (never /tmp).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

R91_TAIL_OLD = """        if need and end > t:
            return min(end, len(raw))
    return t
"""
FORGERIES = (
    ("F1", "before", "    if t <= 0 or t >= len(raw) or not 0x80 <= raw[t] <= 0xBF:\n        return t\n",
     "    if t <= 0 or t >= len(raw) or not 0x80 <= raw[t] <= 0xBF:\n        return t\n"
     "    if raw[t - 1] == 0xF0 and raw[t] == 0x80:  # F1 forgery: the repro pair only\n        return t\n"),
    ("F2", "before", R91_TAIL_OLD,
     "        if need and end > t and end <= len(raw) and all(0x80 <= b <= 0xBF for b in raw[i:end]):  # F2\n"
     "            return end\n    return t\n"),
    ("F3", "tool", "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n",
     "    return t  # F3 forgery\n"),
    ("F4", "tool", "    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n",
     "    return h  # F4 forgery\n"),
    ("N0", "before", None, None),
)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(fixture, tool, before, work):
    p = subprocess.run([sys.executable, "-B", fixture, "--tool", tool, "--before", before, "--work", work],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY cases=(\d+) tool_pass=(\d+) before_pass=(\d+)$", out, re.M)
    return p.returncode, (int(m.group(2)), int(m.group(1))) if m else None, out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--tool", required=True, help="the filed tool (positive control)")
    ap.add_argument("--before", required=True, help="the r91 tool bytes")
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-FORGERY-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C2-FORGERY-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work)
    fixture, tool, before = (os.path.abspath(x) for x in (ns.fixture, ns.tool, ns.before))
    for k, v in (("fixture", fixture), ("tool", tool), ("before", before), ("probe", os.path.abspath(__file__))):
        print(f"# {k} path={v} sha256={sha(v)}")
    src = {"tool": open(tool, encoding="utf-8").read(), "before": open(before, encoding="utf-8").read()}
    rc, res, _out = run(fixture, tool, before, os.path.join(work, "positive"))
    positive = rc == 0 and res is not None and res[0] == res[1]
    print(f"POSITIVE tool exit={rc} tool_pass={res[0] if res else '-'}/{res[1] if res else '-'} "
          f"{'pass' if positive else 'fail'}")
    rejected = 0
    for fid, base, old, new in FORGERIES:
        text = src[base]
        if old is not None:
            if text.count(old) != 1:
                print(f"C2-FORGERY-FATAL: {fid} edit does not apply exactly once", file=sys.stderr)
                return 2
            text = text.replace(old, new, 1)
        path = os.path.join(work, f"{fid}-souji-record-agreement.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        rc, res, out = run(fixture, path, before, os.path.join(work, fid))
        with open(os.path.join(work, f"{fid}.out"), "w", encoding="utf-8") as f:
            f.write(out)
        fails = [l.split()[1] for l in out.splitlines() if l.startswith("CASE ") and " tool=fail " in l]
        rej = rc == 1 and res is not None and res[0] < res[1]
        rejected += rej
        print(f"FORGERY {fid} sha256={sha(path)} exit={rc} tool_pass={res[0] if res else '-'}/{res[1] if res else '-'} "
              f"rejected={'yes' if rej else 'no'} failed={','.join(fails) or '-'}")
    print(f"FORGERY-SUMMARY forgeries={len(FORGERIES)} rejected={rejected} positive={'pass' if positive else 'fail'}")
    return 0 if positive and rejected == len(FORGERIES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
