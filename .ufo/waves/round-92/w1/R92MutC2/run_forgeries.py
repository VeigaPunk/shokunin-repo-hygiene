#!/usr/bin/env python3
"""Run 8 forgeries + filed positive through r92 fixture; copy receipts to seat dir."""
import subprocess, sys, pathlib, shutil, re
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
SCR = pathlib.Path("/fast/scratch/hyaku/souji-r92/R92MutC2")
SEAT = LANE / ".ufo/waves/round-92/w1/R92MutC2"
FIX = LANE / "tests/fixtures/r92-k4-flagfail.py"
BEFORE = LANE / "census/round-92/controls/c2-before-tool.py"
NAMES = ["A_window3","B_leadtable","C_surrogatepass","D_len_ge1","E_head_fwd","F_tail_back","G_end_minus1","H_reprokey"]
def run(name, toolpath):
    work = SCR / f"work_{name}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    p = subprocess.run([sys.executable,"-B",str(FIX),"--tool",str(toolpath),"--before",str(BEFORE),"--work",str(work)],
                       cwd=str(LANE), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    out = p.stdout.decode("utf-8","replace") + "\nSTDERR:\n" + p.stderr.decode("utf-8","replace")
    (SEAT / f"fixture_{name}.txt").write_text(f"tool={toolpath}\nrc={p.returncode}\n{out}", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    m = re.search(r"SUMMARY cases=(\d+) tool_pass=(\d+) before_pass=(\d+)", out)
    fails = re.findall(r"^CASE (\S+) tool=fail", out, re.M)
    print(f"{name}: rc={p.returncode} summary={m.group(0) if m else 'NO-SUMMARY'} fails={fails}", flush=True)
    return p.returncode, fails, m.group(0) if m else ""
results = {}
for n in NAMES:
    results[n] = run(n, SCR / f"{n}.py")
# positive control: filed tool
results["FILED"] = run("FILED", LANE / "tools/souji-record-agreement.py")
# r91 negative control
results["R91"] = run("R91", BEFORE)
(SEAT / "forgery_table.tsv").write_text(
    "name\trc\tsummary\tfails\n" + "\n".join(f"{k}\t{v[0]}\t{v[2]}\t{','.join(v[1])}" for k,v in results.items()) + "\n",
    encoding="utf-8")
print("DONE")
