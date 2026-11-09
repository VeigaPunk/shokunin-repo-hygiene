#!/usr/bin/env python3
"""R92Sentinel: signal behaviour of the survivor search (SIGKILL orphaning; SIGINT draining) on two --ids targets."""
import os
import signal
import subprocess
import sys
import time

SCR = "/fast/scratch/hyaku/souji-r92/R92Sentinel"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"


def cmd(work, jobs):
    return [sys.executable, "-B", "census/round-92/c1-survivor-search.py", "--counter", "census/round-87/c1-pointer-counter.py",
            "--harness", "census/round-92/c1-false-row-harness.py", "--population", "census/round-92/c1-false-rows.tsv",
            "--lane", ".", "--fleet-root", "/home/vgpnk/Projects/shokunin", "--work", work, "--jobs", str(jobs),
            "--ids", os.path.join(SCR, "ids2.json")]


def start(work, jobs, out):
    os.makedirs(work, exist_ok=True)
    f = open(out, "w")
    p = subprocess.Popen(cmd(work, jobs), cwd=LANE, stdout=f, stderr=subprocess.STDOUT)
    return p, f


def harness_alive():
    r = subprocess.run(["ps", "-eo", "pid,pgid,etimes,args"], capture_output=True, text=True)
    mine = [l for l in r.stdout.splitlines() if "c1-false-row-harness.py" in l and "/fast/scratch/hyaku/souji-r92/R92Sentinel" in l]
    return mine


def scenario_kill():
    work = os.path.join(SCR, "s2", "work")
    p, f = start(work, 2, os.path.join(SCR, "s2.out"))
    time.sleep(10)
    print(f"KILL t=10s parent_pid={p.pid} alive_before={p.poll() is None} work_du_before={du(work)}", flush=True)
    os.kill(p.pid, signal.SIGKILL)
    rc = p.wait()
    f.close()
    print(f"KILL parent_rc={rc} harness_procs_after_parent_death={len(harness_alive())}", flush=True)
    for t in (20, 40, 60):
        time.sleep(20)
        print(f"KILL +{t - 0}s-ish harness_procs={len(harness_alive())} du_bytes={du(work)} "
              f"entries={sorted(os.listdir(work)) if os.path.isdir(work) else None}", flush=True)
    for root, dirs, files in os.walk(work):
        if root.count(os.sep) - work.count(os.sep) <= 2:
            print("  LEFT", root, sorted(dirs)[:4], sorted(files)[:4], flush=True)


def scenario_int():
    work = os.path.join(SCR, "s3", "work")
    p, f = start(work, 1, os.path.join(SCR, "s3.out"))
    time.sleep(6)
    t_sig = time.time()
    print(f"INT signal sent at +6s parent_alive={p.poll() is None}", flush=True)
    os.kill(p.pid, signal.SIGINT)
    rc = p.wait()
    f.close()
    print(f"INT parent_rc={rc} parent_exit_after_signal={time.time() - t_sig:.1f}s du_bytes={du(work)}", flush=True)


def du(path):
    if not os.path.exists(path):
        return 0
    tot = 0
    for root, _d, files in os.walk(path):
        for n in files:
            try:
                tot += os.lstat(os.path.join(root, n)).st_size
            except OSError:
                pass
    return tot


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "kill":
        scenario_kill()
    else:
        scenario_int()
