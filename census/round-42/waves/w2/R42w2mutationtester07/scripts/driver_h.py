#!/usr/bin/env python3
"""Batch H: single-point mutants of the r42 C2 counter's own harness (fixture plumbing, refusals, timeouts)."""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess

FROZEN = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"
CLONE = os.path.join(SCRATCH, "clone-tip")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
CONTROL_TOOL = "census/round-42/controls/c2-stub-tool.py"
LANDED_TOOL = "tools/souji-freeze-check.py"
BASE = open(FROZEN, encoding="utf-8").read()

H = [
 ("H01", "refusal", "the unresolved-revision refusal check is made trivially true (the stub-rejection label is then carried by nothing else)",
  'r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4] and not r1[3],', 'True,'),
 ("H02", "run_tool", "the per-case tool timeout is 1 second (the TimeoutExpired is not handled in run_tool)",
  'env=env(scratch), timeout=300)', 'env=env(scratch), timeout=1)'),
 ("H03", "git helper", "a failed git call no longer raises (a broken fixture is silently scored)",
  'if check and p.returncode != 0:', 'if False:'),
 ("H04", "build", "the fixture-root assertion (git rev-parse --show-toplevel == the fixture dir) is dropped",
  'if os.path.realpath(git(d, scratch, "rev-parse", "--show-toplevel")) != os.path.realpath(d):',
  'if False:'),
 ("H05", "build:commit", "only census/ is staged by the fixture commit (the .ufo/waves files never enter the tree)",
  'git(d, scratch, "add", "-A")', 'git(d, scratch, "add", "-A", "--", "census")'),
 ("H06", "case_ok", "the crash check is dropped from the per-case verdict",
  'ok = (rc == want_rc and got == sorted(want) and not crash and summ is not None',
  'ok = (rc == want_rc and got == sorted(want) and summ is not None'),
 ("H07", "score_tool", "the per-case result list is not returned (the counter reports a case count it never ran)",
  'return sum(1 for _n, ok, _d in results if ok), len(results)',
  'return sum(1 for _n, ok, _d in results if ok), len(CASES) + 2'),
 ("H08", "verdict", "the met() gate stops requiring the second stub (control_findings) to be REJECTED",
  'and stubs["control_findings"] == "REJECTED" and real == "ok"', 'and real == "ok"'),
]


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def run_one(mid, path, tool):
    work = os.path.join(SCRATCH, "runs", mid, tool.replace("/", "_"))
    os.makedirs(work, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = work
    cmd = ["python3", "-B", path, "--root", CLONE, "--rev", REV, "--tool", tool, "--scratch", work]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           env=env, timeout=1200, cwd=work)
        out, rc = p.stdout, p.returncode
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", "replace")
        rc = "TIMEOUT"
    summ = [ln for ln in out.splitlines() if ln.startswith("SUMMARY ")]
    fails = [ln for ln in out.splitlines() if ln.startswith("case-") and "=FAIL" in ln]
    dest = os.path.join(SEAT, "receipts", "%s.%s.txt" % (mid, "landed" if tool == LANDED_TOOL else "control"))
    with open(dest, "w", encoding="utf-8") as h:
        h.write("$ python3 -B %s --root %s --rev %s --tool %s --scratch <scratch>\n"
                % (path, CLONE, REV, tool))
        h.write(out)
    return {"id": mid, "tool": tool, "rc": rc,
            "summary": summ[-1] if summ else None,
            "summary_fields": dict(re.findall(r"(\w+)=([^\s]+)", summ[-1])) if summ else None,
            "n_fail_cases": len(fails),
            "fail_cases": [x.split("=")[0][5:] for x in fails], "out": dest}


def main():
    manifest = []
    for mid, region, desc, old, new in H:
        assert BASE.count(old) == 1, (mid, BASE.count(old))
        src = BASE.replace(old, new, 1)
        path = os.path.join(SEAT, "mutants", "%s.py" % mid)
        with open(path, "w", encoding="utf-8") as h:
            h.write(src)
        manifest.append({"id": mid, "region": region, "desc": desc, "sha256": sha(src)})
    jobs = [(m["id"], os.path.join(SEAT, "mutants", m["id"] + ".py")) for m in manifest]
    results = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for mid, path in jobs:
            for tool in (LANDED_TOOL, CONTROL_TOOL):
                futs[ex.submit(run_one, mid, path, tool)] = (mid, tool)
        for f in cf.as_completed(futs):
            mid, tool = futs[f]
            results.append(f.result())
    results.sort(key=lambda r: (r["id"], r["tool"]))
    with open(os.path.join(SEAT, "receipts", "results-h.json"), "w", encoding="utf-8") as h:
        json.dump({"manifest": manifest, "results": results}, h, indent=1)
    print("done", len(results), "runs")


if __name__ == "__main__":
    main()
