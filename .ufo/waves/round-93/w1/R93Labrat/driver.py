#!/usr/bin/env python3
import os, sys, time, subprocess, signal, shutil, json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCRATCH = "/fast/scratch/hyaku/souji-r93/R93Labrat"
IDS = os.path.join(SCRATCH, "ids4.json")

def run_arm(name, search, harness, population, sig, delay=6.0, wait_timeout=30.0):
    work = os.path.join(SCRATCH, f"work-{name}")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    cmd = [sys.executable, "-B", search,
           "--counter", os.path.join(LANE, "census/round-87/c1-pointer-counter.py"),
           "--harness", harness,
           "--population", population,
           "--lane", LANE,
           "--fleet-root", "/home/vgpnk/Projects/shokunin",
           "--work", work,
           "--jobs", "2",
           "--ids", IDS]
    print(f"\n=== ARM {name} sig={sig} ===", flush=True)
    print("CMD:", " ".join(cmd), flush=True)
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=LANE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, start_new_session=True)
    time.sleep(delay)
    # snapshot before signal
    def measures():
        wdirs = []
        for root, dirs, files in os.walk(work):
            for d in dirs:
                if d == "w":
                    wdirs.append(os.path.join(root, d))
        total_kb = 0
        for root, dirs, files in os.walk(work):
            for f in files:
                try:
                    total_kb += os.path.getsize(os.path.join(root, f)) // 1024
                except OSError:
                    pass
        # also du via subprocess for whole work
        try:
            du = subprocess.run(["du", "-sk", work], capture_output=True, text=True).stdout.strip()
        except Exception as e:
            du = f"du-error {e}"
        # processes filtered by work path
        ps = subprocess.run(["bash", "-c", f"ps -ef | grep -F '{work}' | grep -v grep | grep -v 'ps -ef' || true"],
                            capture_output=True, text=True).stdout.strip()
        return wdirs, du, ps
    pre_w, pre_du, pre_ps = measures()
    print(f"PRE-SIGNAL after {delay}s: w_dirs={len(pre_w)} du={pre_du} ps_lines={(pre_ps.splitlines() if pre_ps else [])}", flush=True)
    if sig == "SIGKILL":
        p.send_signal(signal.SIGKILL)
    elif sig == "SIGTERM":
        p.send_signal(signal.SIGTERM)
    elif sig == "SIGINT":
        p.send_signal(signal.SIGINT)
    try:
        out, _ = p.communicate(timeout=wait_timeout)
        rc = p.returncode
        elapsed = time.time() - t0 - delay
    except subprocess.TimeoutExpired:
        print("TIMEOUT waiting 30s after signal; killing pg", flush=True)
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except Exception:
            pass
        out, _ = p.communicate()
        rc = f"TIMEOUT rc={p.returncode}"
        elapsed = time.time() - t0 - delay
    post_w, post_du, post_ps = measures()
    # give a moment then re-check processes (zombies?)
    time.sleep(1.0)
    post2_w, post2_du, post2_ps = measures()
    print(f"rc={rc} elapsed_after_signal={elapsed:.2f}s", flush=True)
    print(f"POST w_dirs={len(post_w)} {post_w} du={post_du} ps={post_ps!r}", flush=True)
    print(f"POST+1s w_dirs={len(post2_w)} du={post2_du} ps={post2_ps!r}", flush=True)
    print("--- search output tail ---", flush=True)
    lines = out.splitlines()
    for l in lines[-12:]:
        print(l, flush=True)
    print("--- end ---", flush=True)
    # cleanup work tree for disk budget after recording
    shutil.rmtree(work, ignore_errors=True)
    print(f"cleanup done for {name}", flush=True)
    return {"arm": name, "sig": sig, "rc": str(rc), "elapsed": round(elapsed, 2),
            "pre_w": len(pre_w), "post_w": len(post_w), "post2_w": len(post2_w),
            "post_du": post_du, "post_ps": post_ps, "post2_ps": post2_ps, "tail": lines[-12:]}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "one"
    results = []
    R93S = os.path.join(LANE, "census/round-93/c1-survivor-search.py")
    R93H = os.path.join(LANE, "census/round-93/c1-false-row-harness.py")
    R93P = os.path.join(LANE, "census/round-93/c1-false-rows.tsv")
    R92S = os.path.join(LANE, "census/round-92/c1-survivor-search.py")
    R92H = os.path.join(LANE, "census/round-92/c1-false-row-harness.py")
    R92P = os.path.join(LANE, "census/round-92/c1-false-rows.tsv")
    if which == "one":
        results.append(run_arm("r93-term-1", R93S, R93H, R93P, "SIGTERM"))
    elif which == "r93":
        results.append(run_arm("r93-term-1", R93S, R93H, R93P, "SIGTERM"))
        results.append(run_arm("r93-term-2", R93S, R93H, R93P, "SIGTERM"))
        results.append(run_arm("r93-int-1", R93S, R93H, R93P, "SIGINT"))
        results.append(run_arm("r93-int-2", R93S, R93H, R93P, "SIGINT"))
    elif which == "r92":
        results.append(run_arm("r92-term-1", R92S, R92H, R92P, "SIGTERM"))
        results.append(run_arm("r92-term-2", R92S, R92H, R92P, "SIGTERM"))
        results.append(run_arm("r92-int-1", R92S, R92H, R92P, "SIGINT"))
        results.append(run_arm("r92-int-2", R92S, R92H, R92P, "SIGINT"))
    elif which == "kill":
        results.append(run_arm("r93-kill-1", R93S, R93H, R93P, "SIGKILL"))
    json.dump(results, open(os.path.join(SCRATCH, f"results-{which}.json"), "w"), indent=1)
    print(json.dumps(results, indent=1))
