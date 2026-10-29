#!/usr/bin/env python3
"""R42w2executor01 gate-registry axis-harm runner. Scratch-only; writes under S, never the lane.
Usage: run-gates.py [--only i,j] [--out NAME]   (env JOBS, default 6; TIMEOUT default 300)"""
import os, subprocess, sys, time, json, re, shutil
from concurrent.futures import ThreadPoolExecutor

S = "/fast/scratch/hyaku/souji-r42/R42w2executor01"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
REVS = {"base": BASE, "tip": TIP}
B = S + "/blobs"
TIMEOUT = int(os.environ.get("TIMEOUT", "300"))
PREREG41 = "b8cb4b31ce80e2e3314b88e85d40ea9873180804"
# placeholders: {B} blob dir, {CL} tree (git checkout = LANE clone), {REV}, {SCR}, {PREREG}
# (name, command[, flags]) flags: V = TMPDIR=/var/tmp/<unique> (legacy selftest prescription)
CASES = [
 ("souji-verify selftest", "bash tools/souji-verify.sh --selftest", "V"),
 ("souji-vault-verify selftest", "SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest", "V"),
 ("souji-census selftest", "bash tools/souji-census.sh --selftest", "V"),
 ("souji-quarantine selftest", "bash tools/souji-quarantine.sh --selftest", "V"),
 ("r12-maintenance-guard --selftest", "bash tests/fixtures/r12-maintenance-guard.sh --selftest"),
 ("souji-cert-evidence selftest", "python3 tools/souji-cert-evidence.py --selftest"),
 ("r13-cert-evidence", "python3 tests/fixtures/r13-cert-evidence.py"),
 ("r13-repo-structure", "bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh"),
 ("r13-quarantine-bounds", "bash tests/fixtures/r13-quarantine-bounds.sh"),
 ("souji-evidence-cache selftest", "python3 tools/souji-evidence-cache.py --selftest"),
 ("r14-evidence-cache", "python3 tests/fixtures/r14-evidence-cache.py"),
 ("r14-census-boundary", "python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh"),
 ("r15-census-config", "python3 tests/fixtures/r15-census-config.py --tool tools/souji-census.sh"),
 ("r17-census-hygiene", "python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh"),
 ("r17-jj-receipts", "bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools"),
 ("souji-preservation-evidence selftest", "python3 tools/souji-preservation-evidence.py --selftest"),
 ("r15-preservation-evidence", "python3 tests/fixtures/r15-preservation-evidence.py"),
 ("souji-landing-gate selftest", "python3 tools/souji-landing-gate.py --selftest"),
 ("r18-landing-pointers", "python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py"),
 ("r16-landing-gate", "python3 tests/fixtures/r16-landing-gate.py"),
 ("souji-seat-audit selftest", "python3 tools/souji-seat-audit.py --selftest"),
 ("r17-transcript-manifest --check", "python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts"),
 ("r18-census-bounded", "python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh"),
 ("souji-proc-census selftest", "bash tools/souji-proc-census.sh --selftest", "V"),
 ("r18-proc-census", "bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh"),
 ("r18-leak-count selftest", "python3 census/round-18/leak-count.py --selftest"),
 ("souji-rev-pin selftest", "python3 tools/souji-rev-pin.py --selftest"),
 ("r19-rev-pin", "python3 tests/fixtures/r19-rev-pin.py"),
 ("r19-carry-wrap", "python3 tests/fixtures/r19-carry-wrap.py"),
 ("probe-carry-invariants", "python3 census/round-19/probe-carry-invariants.py"),
 ("r19-seat-audit-shapes", "python3 tests/fixtures/r19-seat-audit-shapes.py"),
 ("verify-agreement-pin selftest", "python3 census/round-19/verify-agreement-pin.py --selftest"),
 ("r20-audit-contract", "python3 tests/fixtures/r20-audit-contract.py"),
 ("r21-read-root", "python3 tests/fixtures/r21-read-root.py --tool tools/souji-seat-audit.py --base-tool {B}/audit-6ff3413.py"),
 ("r21-reason-canary", "bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base {B}/proc-6ff3413.sh"),
 ("r21-read-render-edges", "python3 tests/fixtures/r21-read-render-edges.py --tool tools/souji-seat-audit.py"),
 ("r21-replay-boundaries", "python3 tests/fixtures/r21-replay-boundaries.py --tool census/round-21/run-acceptance.py --base-tool {B}/run-8513d6ac.py"),
 ("r21-source-head", "python3 tests/fixtures/r21-source-head.py --tool census/round-21/run-acceptance.py --base-tool {B}/run-522dcd76.py"),
 ("r22-result-oracle", "python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py"),
 ("r22-mutation-adequacy", "python3 -B census/round-22/mutation-adequacy.py"),
 ("r27-pre-report-gate fixture", "bash tests/fixtures/r27-pre-report-gate.sh"),
 ("souji-report-contract selftest", "python3 tools/souji-report-contract.py --selftest"),
 ("r36-report-gate", "python3 tests/fixtures/r36-report-gate.py"),
 ("r36-worktree-drift", "python3 tests/fixtures/r36-worktree-drift.py"),
 ("r37-citation-reconcile", "python3 tests/fixtures/r37-citation-reconcile.py"),
 ("r38-counter-arms", "python3 -B tests/fixtures/r38-counter-arms.py"),
 ("r37-drift-escapes", "python3 tests/fixtures/r37-drift-escapes.py --base-tool {B}/drift-1e771ed.py"),
 ("r37-drift-discrimination", "python3 tests/fixtures/r37-drift-discrimination.py"),
 ("r37-drift-mutants", "python3 tests/fixtures/r37-drift-mutants.py --fixture tests/fixtures/r37-drift-discrimination.py"),
 ("r29-registry-agreement fixture", "python3 -B tests/fixtures/r29-registry-agreement.py --tool {CL}/tools/souji-registry-agreement.py"),
 ("r28-wave-evidence-capture", "bash tests/fixtures/r28-wave-evidence-capture.sh"),
 ("r30-landing-gate-discovery", "python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py"),
 ("r31-landing-gate-precision", "python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py"),
 ("r38-citation-commit", "python3 -B tests/fixtures/r38-citation-commit.py"),
 ("r38-drift-write-envelope", "python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool {B}/drift-4c257b7.py"),
 ("r38-drift-record", "python3 -B tests/fixtures/r38-drift-record.py"),
 ("r38-drift-mutants", "python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py"),
 ("r39-citation-rev", "python3 -B tests/fixtures/r39-citation-rev.py"),
 ("r39-drift-record-rules", "python3 -B tests/fixtures/r39-drift-record-rules.py"),
 # lane's own checks against the clone (git checkout)
 ("souji-registry-agreement (lane, list-rev b8cb4b3)", "python3 -B tools/souji-registry-agreement.py --root {CL} --rev {REV} --list-rev {PREREG}"),
 ("souji-landing-gate (lane, --round 41)", "python3 -B tools/souji-landing-gate.py --root {CL} --rev {REV} --round 41"),
 ("souji-landing-gate (lane, --round 42)", "python3 -B tools/souji-landing-gate.py --root {CL} --rev {REV} --round 42"),
 # r41 rows added after r40 (unchanged tools; counters read the tool at --rev)
 ("r41-freeze-check-cases", "python3 -B census/round-41/c2-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r41-refusal-sites", "python3 -B tests/fixtures/r41-refusal-sites.py --tool tools/souji-worktree-drift.py --work {SCR}"),
 ("r41-refusal-sites (c3-counter)", "python3 -B census/round-41/c3-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r41-drift-record-order", "python3 -B tests/fixtures/r41-drift-record-order.py --work {SCR}"),
 ("r41-drift-record-order (r1-counter)", "python3 -B census/round-41/r1-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r41-c1-corrections", "python3 -B census/round-41/c1-counter.py --root {CL} --rev {REV}"),
 ("souji-freeze-check on r41 prereg", "python3 -B tools/souji-freeze-check.py --root {CL} --prereg census/round-41/preregistration.txt --rev {REV}"),
 # tip-only rows (r42); expected red/absent at base
 ("souji-freeze-check on r42 prereg", "python3 -B tools/souji-freeze-check.py --root {CL} --prereg census/round-42/preregistration.txt --rev {REV}"),
 ("r42-freeze-check-selftest", "python3 -B tools/souji-freeze-check.py --selftest"),
 ("r42-c1-counter", "python3 -B census/round-42/c1-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r42-c2-counter", "python3 -B census/round-42/c2-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r42-c3-counter", "python3 -B census/round-42/c3-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 ("r42-drift-conditions", "python3 -B tests/fixtures/r42-drift-conditions.py --tool tools/souji-worktree-drift.py --work {SCR}"),
 ("r42-r1-counter", "python3 -B census/round-42/r1-counter.py --root {CL} --rev {REV} --scratch {SCR}"),
 # extra rows not in r41's 61
 ("r20-input-binding", "python3 tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812"),
 ("r29-c2-counter", "python3 -B census/round-29/c2-counter.py --root {CL} --rev {REV}"),
 ("r17-gate-replays (--gate-rev 5fa6017)", "python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --output {SCR}/gr.json"),
 ("c1-counter (r39) base-rev read", "python3 -B census/round-39/c1-counter.py --root {CL} --rev {REV} --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch {SCR}"),
 ("c2-counter (r39)", "python3 -B census/round-39/c2-counter.py --root {CL} --rev {REV} --base-rev {REV} --scratch {SCR}"),
 ("c3-counter (r39)", "python3 -B census/round-39/c3-counter.py --root {CL} --rev {REV} --base-rev {REV} --scratch {SCR}"),
]

SUMRE = re.compile(r"(SUMMARY|SELFTEST|selftest|cases=|check OK|fixture:|total=|killed=|mutants=|findings=|VERDICT|PASS|FAIL)")

def tree(k): return f"{S}/{k}"

def run(rev_key, idx, name, cmd, flags):
    rev = REVS[rev_key]
    tr = tree(rev_key)
    tmp = f"{S}/tmp/{rev_key}-{idx:02d}"
    if "V" in flags:
        tmp = f"/var/tmp/r42w2e01-{rev_key}-{idx:02d}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    c = cmd.format(B=B, CL=tr, REV=rev, SCR=tmp, PREREG=PREREG41)
    env = dict(os.environ, TMPDIR=tmp, PYTHONDONTWRITEBYTECODE="1")
    t = time.time()
    try:
        p = subprocess.run(["bash", "-c", c], cwd=tr, env=env, capture_output=True, text=True, errors="replace",
                           timeout=TIMEOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc = 124
        o = e.stdout or b""
        out = (o.decode(errors="replace") if isinstance(o, bytes) else o) + f"\nTIMEOUT {TIMEOUT}s"
    dt = time.time() - t
    os.makedirs(S + "/logs", exist_ok=True)
    lf = f"{S}/logs/{rev_key}-{idx:02d}.txt"
    open(lf, "w").write(f"$ cd {tr} && TMPDIR={tmp} {c}\n# rc={rc} wall={dt:.1f}s\n{out}")
    lines = [l for l in out.strip().splitlines() if l.strip()]
    summ = [l for l in lines if SUMRE.search(l)]
    last = (summ[-1] if summ else (lines[-1] if lines else ""))
    # normalized full output hash (paths/revs/tmp/time stripped)
    norm = out
    for a in (tr, tmp, BASE, TIP, BASE[:7], TIP[:7], S):
        norm = norm.replace(a, "<X>")
    norm = re.sub(r"\d+(\.\d+)?\s*(s|ms)\b", "<T>", norm)
    import hashlib
    h = hashlib.sha256(norm.encode()).hexdigest()[:12]
    shutil.rmtree(tmp, ignore_errors=True) if ("V" in flags or True) else None
    return dict(rev=rev_key, idx=idx, name=name, cmd=c, rc=rc, wall=round(dt, 1), log=lf, last=last.strip()[:260], nhash=h, nlines=len(lines))

if __name__ == "__main__":
    only = None; outname = "results"
    a = sys.argv[1:]
    while a:
        x = a.pop(0)
        if x == "--only": only = set(a.pop(0).split(","))
        elif x == "--out": outname = a.pop(0)
    jobs = []
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "6"))) as ex:
        for i, case in enumerate(CASES):
            if only and str(i) not in only: continue
            n, c = case[0], case[1]
            fl = case[2] if len(case) > 2 else ""
            for k in ("base", "tip"):
                jobs.append(ex.submit(run, k, i, n, c, fl))
        res = [j.result() for j in jobs]
    json.dump(res, open(f"{S}/{outname}.json", "w"), indent=1)
    for r in sorted(res, key=lambda r: (r["idx"], r["rev"])):
        print(r["idx"], r["rev"], r["rc"], r["wall"], r["name"], "|", r["last"][:150])
