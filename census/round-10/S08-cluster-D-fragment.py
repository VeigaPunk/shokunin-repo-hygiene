#!/usr/bin/env python3
"""S08 (round 10) cluster-D member 2 — candidate fragment.

Regenerates the numbers in S08-cluster-D.md by running every battery fresh
against each tool. Fixtures under /var/tmp only; read-only against the tools.

Usage: python3 S08-cluster-D-fragment.py [--tools DIR]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument("--tools", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools")
P.add_argument("--out", default="")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()
CENSUS = Path(__file__).resolve().parent
REPO = TOOLS.parent

TOOLS_UNDER_TEST = [
    ("souji-verify.sh", "installed (S17-patched patch base)"),
    ("souji-verify.r9-s18.sh", "r9 S18 candidate"),
    ("cand-d2-verify.sh", "S08 candidate (this seat)"),
]


def run(cmd, cwd=None):
    # This host's /tmp is quota-limited (r8/r9 incident); every fixture run is
    # forced under /var/tmp so a quota stall cannot masquerade as a tool result.
    env = dict(os.environ, TMPDIR="/var/tmp", GIT_OPTIONAL_LOCKS="0")
    return subprocess.run([str(x) for x in cmd], capture_output=True, text=True,
                          cwd=cwd or REPO, timeout=900, env=env)


def parse_probe(out):
    m = re.search(r"PROBE\t\S+\tpass=(\d+)\tdefect=(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def parse_selftest(out):
    m = re.search(r"selftest: (\d+) checks, (\d+) failed", out)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


rows = []
for tool, label in TOOLS_UNDER_TEST:
    path = TOOLS / tool
    if not path.exists():
        rows.append({"tool": tool, "label": label, "present": False})
        continue
    rec = {"tool": tool, "label": label, "present": True}

    st = run(["bash", path, "--selftest"], cwd=REPO)
    rec["selftest_total"], rec["selftest_failed"] = parse_selftest(st.stdout)

    r9 = run(["bash", REPO / "tools/souji-round9-selftest.sh", "verify", path])
    m = re.search(r"ROUND9\t(\d+)\t(\d+)", r9.stdout)
    rec["r9_pass"], rec["r9_fail"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)

    aj = run(["bash", REPO / "tools/cand-d2-probe.sh", path, tool])
    rec["AJ_pass"], rec["AJ_defect"] = parse_probe(aj.stdout)

    kt = run([sys.executable, CENSUS / "S08-cluster-D-repro.py", "--tool", tool])
    rec["KT_pass"], rec["KT_defect"] = parse_probe(kt.stdout)

    unsafe = sum(v for v in (rec["AJ_defect"], rec["KT_defect"], rec["r9_fail"]) if v)
    rec["unsafe_verdicts"] = unsafe
    rows.append(rec)

print(json.dumps(rows, indent=1))
if A.out:
    Path(A.out).write_text(json.dumps(rows, indent=1))
