#!/usr/bin/env python3
"""Run each forgery through the r93 fixture (r91 tool as --before); record rc,
tool_pass/cases, failing cases. Lane untouched. Mirrors the r93 C2 forgery probe's
run/rejected logic for consistency."""
import hashlib
import pathlib
import re
import subprocess
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r93/R93MutC2")
FORG = SCR / "forg"
SEAT = LANE / ".ufo/waves/round-93/w1/R93MutC2"
FIXTURE = LANE / "tests/fixtures/r93-k4-flagfail.py"
BEFORE = LANE / "census/round-92/controls/c2-before-tool.py"
RECEIPTS = SCR / "receipts"
RECEIPTS.mkdir(parents=True, exist_ok=True)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def run(tool, work):
    p = subprocess.run([sys.executable, "-B", str(FIXTURE), "--tool", str(tool),
                        "--before", str(BEFORE), "--work", str(work)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY cases=(\d+) tool_pass=(\d+) before_pass=(\d+)$", out, re.M)
    return p.returncode, ((int(m.group(2)), int(m.group(1))) if m else None), out


print(f"# fixture sha256={sha(FIXTURE)} before sha256={sha(BEFORE)}")
rows = []
for forg in sorted(FORG.glob("*.py")):
    name = forg.stem
    work = SCR / f"work-{name}"
    work.mkdir(exist_ok=True)
    rc, res, out = run(forg, work)
    (RECEIPTS / f"fixture_{name}.txt").write_text(out, encoding="utf-8")
    fails = [l.split()[1] for l in out.splitlines()
             if l.startswith("CASE ") and " tool=fail " in l]
    tp, cases = res if res else ("-", "-")
    rej = rc == 1 and res is not None and res[0] < res[1]
    rows.append((name, sha(forg), rc, tp, cases, ",".join(fails) or "-", "yes" if rej else "no"))
    print(f"{name}: rc={rc} tool_pass={tp}/{cases} fails={','.join(fails) or '-'} rejected={'yes' if rej else 'no'}")

with open(SEAT / "forgery_table.tsv", "w", encoding="utf-8") as f:
    for name, h, rc, tp, cases, fails, rej in rows:
        f.write(f"{name}\tsha256={h}\trc={rc}\ttool_pass={tp}/{cases}\tfails={fails}\trejected={rej}\n")
print("OK")
