#!/usr/bin/env python3
"""R42mutationtester03 matrix runner. `--plan FILE` lists one cell per line as `MUTANT INPUT`; each cell
runs the mutated counter on the input clone and appends one JSON record to results.jsonl (records are
appended, the analyser keeps every record and reports both runs of a repeated cell). Each run gets its own
--scratch under the scratch root and removes it afterwards. The frozen counter file is never run or written:
mutants are copies under SCRATCH/mutants. `--workers N` (default 4) bounds concurrent counter runs.
"""
import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import threading
import tempfile

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42mutationtester03"
RESULTS = os.path.join(SEAT, "harness", "results.jsonl")
LOCK = threading.Lock()


def one(mid, name, inp, env_tmp, tag):
    scratch = tempfile.mkdtemp(prefix="%s-%s-" % (mid, tag), dir=os.path.join(SCRATCH, "work"))
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "TMPDIR": env_tmp}
    cmd = ["python3", "-B", os.path.join(SCRATCH, "mutants", mid + ".py"), "--root", inp["clone"],
           "--rev", inp["rev"], "--scratch", scratch]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           check=False, env=env, timeout=1200)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 124, (e.stdout or ""), "HARNESS-TIMEOUT"
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    rec = {"mutant": mid, "input": name, "tag": tag, "rc": rc, "stdout": out, "stderr": err}
    with LOCK:
        with open(RESULTS, "a", encoding="utf-8") as h:
            h.write(json.dumps(rec) + "\n")
    return rec


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    with open(os.path.join(SCRATCH, "inputs.json")) as h:
        inputs = json.load(h)
    env_tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(env_tmp, exist_ok=True)
    cells = []
    with open(a.plan) as h:
        for line in h:
            line = line.strip()
            if line and not line.startswith("#"):
                mid, name = line.split()
                cells.append((mid, name))
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = [pool.submit(one, mid, name, inputs[name], env_tmp, a.tag) for mid, name in cells]
        for _f in concurrent.futures.as_completed(futs):
            done += 1
            if done % 25 == 0 or done == len(cells):
                print("done %d/%d" % (done, len(cells)), flush=True)
    print("cells=%d tag=%s" % (len(cells), a.tag))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
