#!/usr/bin/env python3
"""S88MutCounter: row-level counterfactuals on scratch copies of the r88 harness.

Scenario nf6g-predecessor: the R11 declaration names the L06 token after a '/' instead of 'x'
  (vendor/tests/... instead of xtests/...). If the NF6g row binds the before-byte half only at the
  alnum spelling, m18b (alnum-only guard) must go RED under this shape while it stays GREEN on the
  filed 'x' shape.
Scenario ld1-diff-target: the LD1 duplicate row carries a DIFFERENT target (census/nowhere) instead of '-'.
  If LD1 binds only the target-equal spelling, m17b (same-target-only duplicate refusal) must go RED here
  while it stays GREEN on the filed shape.
Nothing outside the scratch dir is written; the counter bytes are the scorep copies.
"""
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
HARNESS = os.path.join(LANE, "census/round-88/c1-false-row-harness.py")
POP88 = os.path.join(LANE, "census/round-88/c1-false-rows.tsv")
S = "/fast/scratch/hyaku/souji-r88/S88MutCounter"
COUNTERS = os.path.join(S, "probes2/counters")

SCEN = {
    "nf6g-slash": [("""f.write(f"\\n- retired copy: xtests/vault/vadv54-run/p/p6repo/.git; quarantine slot `{q6}git-stub`.\\n".encode())""",
                    """f.write(f"\\n- retired copy: vendor/tests/vault/vadv54-run/p/p6repo/.git; quarantine slot `{q6}git-stub`.\\n".encode())""")],
    "ld1-diff-target": [("""f.write(base + f"{item}\\tABSENT\\t-\\tr88 {rid} duplicate-id control\\n".encode())""",
                         """f.write(base + f"{item}\\tABSENT\\tcensus/nowhere/{rid}\\tr88 {rid} duplicate-id control\\n".encode())""")],
}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(job):
    scen, counter, work = job
    d = os.path.join(work, f"run-{scen}-{os.path.basename(counter)[:-3]}")
    p = subprocess.run([sys.executable, "-B", os.path.join(work, f"harness-{scen}.py"),
                        "--counter", counter, "--lane", LANE, "--fleet-root", FLEET,
                        "--work", d, "--population", POP88],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", out, re.M)
    red = [l for l in out.splitlines() if (l.startswith("ROW ") and "match=no" in l) or "FATAL" in l]
    return scen, os.path.basename(counter), (m.groups() if m else None), p.returncode, red[:3], err[:200]


def main():
    work = os.path.join(S, "cf")
    src = open(HARNESS, encoding="utf-8").read()
    for scen, subs in SCEN.items():
        body = src
        for old, new in subs:
            n = body.count(old)
            if n != 1:
                print(f"SCENARIO {scen} FATAL anchor occurs {n} times")
                sys.exit(2)
            body = body.replace(old, new)
        with open(os.path.join(work, f"harness-{scen}.py"), "w", encoding="utf-8") as f:
            f.write(body)
        print(f"SCENARIO {scen} harness_sha={sha(os.path.join(work, f'harness-{scen}.py'))}", flush=True)
    jobs = []
    for scen, ctrs in (("nf6g-slash", ["pristine", "m18-filed", "m18b-alnum-only"]),
                       ("ld1-diff-target", ["pristine", "m17-filed", "m17b-same-target"])):
        for c in ctrs:
            jobs.append((scen, os.path.join(COUNTERS, c + ".py"), work))
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for scen, cname, groups, rc, red, err in ex.map(run, jobs):
            print(f"CF {scen:16s} counter={cname:22s} summary={groups} exit={rc}"
                  + (f" red={' | '.join(red)}" if red else "") + (f" stderr={err!r}" if groups is None else ""),
                  flush=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(S, "cf"), exist_ok=True)
    main()
