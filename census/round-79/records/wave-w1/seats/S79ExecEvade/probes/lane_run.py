#!/usr/bin/env python3
"""S79ExecEvade P4: base vs W1 gate, no signal — check-line equality and wall
time on (a) the clean scratch fixture, (b) the lane read-only. 5 reps each."""
import json, os, statistics, subprocess, time

S = "/fast/scratch/hyaku/souji-r79/S79ExecEvade"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PREREG = LANE + "/census/round-79/preregistration.txt"
os.makedirs(S + "/lanework", exist_ok=True)
lane_report = S + "/lanework/report.md"
open(lane_report, "w").write("## SHONEN\nsee census/round-79/preregistration.txt\n")

def run(gate, lane, report):
    t0 = time.perf_counter()
    r = subprocess.run(["bash", gate, "--lane", lane, "--branch", "master",
                        "--report", report, "--prereg", PREREG],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    dt = time.perf_counter() - t0
    checks = [l for l in r.stdout.splitlines() if l.startswith("check-")]
    return r.returncode, checks, round(dt * 1000), r.stderr[-200:]

res = {}
for name, lane, report in (("fixture", S + "/fx/repo", S + "/fx/report.md"),
                           ("lane", LANE, lane_report)):
    for tag, gate in (("w1", S + "/D/souji-pre-report-gate.sh"),
                      ("base", S + "/DB/souji-pre-report-gate.sh")):
        rows = [run(gate, lane, report) for _ in range(5)]
        res[name + "-" + tag] = {
            "rcs": [r[0] for r in rows],
            "checks": rows[0][1],
            "stable": len({tuple(r[1]) for r in rows}) == 1,
            "ms": [r[2] for r in rows],
            "err_full": [r[3] for r in rows[:1]] }
res["fixture_checks_equal"] = res["fixture-w1"]["checks"] == res["fixture-base"]["checks"]
res["lane_checks_equal"] = res["lane-w1"]["checks"] == res["lane-base"]["checks"]
res["ms_median"] = {k: statistics.median(v["ms"]) for k, v in res.items() if isinstance(v, dict) and "ms" in v}
print(json.dumps(res, indent=1))
