#!/usr/bin/env python3
"""R42w2mutationtester05 driver: mutate a COPY of census/round-42/c3-counter.py and score the
three artifacts (stub-allpass, stub-sniff, landed fixture) through each mutant copy.

Nothing in the lane is written except this seat directory; all clones/work live under
/fast/scratch/hyaku/souji-r42/R42w2mutationtester05/.
"""
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester05"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester05"
CLONE = os.path.join(SCRATCH, "clone")
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
PRISTINE = os.path.join(SEAT, "c3-counter.pristine-copy.py")
MUTDIR = os.path.join(SEAT, "mutants")
RECDIR = os.path.join(SEAT, "receipts")
JOBDIR = os.path.join(SCRATCH, "jobs")

ARTIFACTS = (
    ("stub-allpass", "census/round-42/controls/c3-stub-allpass.py"),
    ("stub-sniff", "census/round-42/controls/c3-stub-sniff.py"),
    ("landed-fixture", "tests/fixtures/r42-drift-conditions.py"),
)

# (id, category, old, new)  -- each old must occur exactly once in the pristine source
MUTANTS = [
    # ---- kill definition (killed()) ----
    ("K1", "kill-definition", "rc == 1 and failed > 0 and not crash",
     "rc != 0 and failed > 0 and not crash"),
    ("K2", "kill-definition", "and failed > 0 and not crash",
     "and failed >= 0 and not crash"),
    ("K3", "kill-definition", "and rc == 1 and failed > 0 and not crash",
     "and rc == 1 and failed > 0"),
    ("K4", "kill-definition", "rc == 1 and failed > 0", "rc == 0 and failed > 0"),
    ("K5", "kill-definition", "and failed > 0 and not crash",
     "and failed > 1 and not crash"),
    ("K6", "kill-definition", "cases is not None and rc == 1", "rc == 1"),
    # ---- equivalence guard (clean()) ----
    ("C1", "equivalence-guard", "rc == 0 and failed == 0 and passed == cases and not crash",
     "rc != 1 and failed == 0 and passed == cases and not crash"),
    ("C2", "equivalence-guard", "passed == cases and not crash",
     "passed >= cases and not crash"),
    ("C3", "equivalence-guard", "failed == 0 and passed == cases",
     "failed <= 1 and passed == cases"),
    ("C4", "equivalence-guard", "failed == 0 and passed == cases and not crash",
     "failed == 0 and passed == cases"),
    ("C5", "equivalence-guard", "cases is not None and rc == 0", "rc == 0"),
    # ---- thresholds ----
    ("T1", "threshold", "and prior_ok == 8", "and prior_ok >= 6"),
    ("T2", "threshold", "and killed_n == 13", "and killed_n >= 12"),
    ("T3", "threshold", "and old_killed == 0", "and old_killed <= 1"),
    ("T4", "threshold", "and len(EQUIV) == 6", "and len(EQUIV) >= 5"),
    ("T5", "threshold", "len(MUTANTS) == 13", "len(MUTANTS) >= 12"),
    # ---- anchors check ----
    ("A1", "anchors-check", 'anchors = "ok" if got == want else "FAIL"',
     'anchors = "ok" if got == want else "ok"'),
    ("A2", "anchors-check", "if source.count(old) != 1:",
     "if source.count(old) != 1 and False:"),
    ("A3", "anchors-check", "got[f[0]] = f[2]", "got[f[0]] = f[1]"),
    ("A4", "anchors-check", "if n and len(f) >= 3:", 'if n and len(f) >= 3 and f[0] != "B1":'),
    # ---- prior leg ----
    ("P1", "prior-leg", ', "tests/fixtures/r41-refusal-sites.py")', ')'),
    ("P2", "prior-leg",
     "prior_ok = sum(1 for p in PRIOR if p in fixtures and clean(pre[p].result()))",
     "prior_ok = sum(1 for p in PRIOR if p in fixtures)"),
    ("P3", "prior-leg", "if args.survey or True:", "if args.survey:"),
    ("P4", "prior-leg", "old_killed += 1 if by else 0", "old_killed += 1"),
    # ---- pristine-case minimum ----
    ("G1", "pristine-minimum", "cand_pre[1] >= 13", "cand_pre[1] >= 1"),
    ("G2", "pristine-minimum", "cand_pre[1] >= 13", "cand_pre[1] >= 14"),
    # ---- scratch handling ----
    ("S1", "scratch-handling", "        shutil.rmtree(work, ignore_errors=True)", "        pass"),
    ("S2", "scratch-handling", '        e["TMPDIR"] = work', '        e["TMPDIR"] = scratch'),
    ("S3", "scratch-handling", "        shutil.rmtree(scratch, ignore_errors=True)", "        pass"),
    ("S4", "scratch-handling", 'scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=scratch_root)',
     'scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=None)'),
    # ---- reporting / classification ----
    ("M1", "reporting", "len(MUTANTS), killed_n, len(MUTANTS) - killed_n,",
     "len(MUTANTS) - 1, killed_n, len(MUTANTS) - killed_n,"),
    ("M2", "reporting", "equiv_killed += 1 if cand else 0", "equiv_killed += 1"),
    ("M3", "reporting", "for mid, _d, _o, _n in EQUIV:", "for mid, _d, _o, _n in MUTANTS:"),
]

SUMMARY_RE = re.compile(r"^SUMMARY .*$", re.M)


def sha(path):
    with open(path, "rb") as h:
        return hashlib.sha256(h.read()).hexdigest()


def build_mutants():
    src = open(PRISTINE, "r", encoding="utf-8").read()
    out = []
    for mid, cat, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            raise SystemExit("MUTANT %s anchor occurs %d times (expected 1): %r" % (mid, n, old))
        path = os.path.join(MUTDIR, "mut-%s.py" % mid)
        with open(path, "w", encoding="utf-8") as h:
            h.write(src.replace(old, new, 1))
        out.append((mid, cat, old, new, path, sha(path)))
    return out


def run_job(mid, cat, counter_path, artifact_name, fixture_path):
    job = os.path.join(JOBDIR, "%s__%s" % (mid, artifact_name))
    shutil.rmtree(job, ignore_errors=True)
    os.makedirs(job, exist_ok=True)
    env = dict(os.environ)
    env["TMPDIR"] = job
    env["LC_ALL"] = "C"
    cmd = ["python3", "-B", counter_path, "--root", CLONE, "--rev", REV,
           "--fixture", fixture_path, "--scratch", job]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           env=env, timeout=2400, check=False)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "TIMEOUT"
    m = SUMMARY_RE.findall(out)
    rec = {
        "mutant": mid, "category": cat, "artifact": artifact_name, "fixture": fixture_path,
        "rc": rc, "summary": m[-1] if m else None,
        "n_summary_lines": len(m),
        "mutant_lines": [l for l in out.split("\n") if l.startswith("MUTANT ")],
        "equiv_lines": [l for l in out.split("\n") if l.startswith("EQUIV ")],
        "stderr": err[-800:],
        "cmd": " ".join(cmd),
    }
    with open(os.path.join(RECDIR, "%s__%s.json" % (mid, artifact_name)), "w") as h:
        json.dump(rec, h, indent=1)
    with open(os.path.join(RECDIR, "%s__%s.out" % (mid, artifact_name)), "w") as h:
        h.write(out)
    shutil.rmtree(job, ignore_errors=True)
    return rec


def main():
    os.makedirs(MUTDIR, exist_ok=True)
    os.makedirs(RECDIR, exist_ok=True)
    os.makedirs(JOBDIR, exist_ok=True)
    built = build_mutants()
    print("built %d mutant counter copies" % len(built), flush=True)
    jobs = []
    for mid, cat, _o, _n, path, _s in built:
        for aname, afix in ARTIFACTS:
            jobs.append((mid, cat, path, aname, afix))
    for aname, afix in ARTIFACTS:
        jobs.append(("PRISTINE", "baseline", PRISTINE, aname, afix))
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    recs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_job, *j) for j in jobs]
        for i, f in enumerate(concurrent.futures.as_completed(futs)):
            r = f.result()
            recs.append(r)
            print("[%d/%d] %s %s rc=%s %s" % (i + 1, len(jobs), r["mutant"], r["artifact"],
                                              r["rc"], r["summary"]), flush=True)
    with open(os.path.join(RECDIR, "all-records.json"), "w") as h:
        json.dump(recs, h, indent=1)
    print("DONE %d records" % len(recs))


if __name__ == "__main__":
    main()
