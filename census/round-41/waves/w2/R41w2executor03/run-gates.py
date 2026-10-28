#!/usr/bin/env python3
"""R41w2executor03 gate runner: base/tip axis-harm audit. Scratch-only; writes under S."""
import os, subprocess, sys, time, json, re
from concurrent.futures import ThreadPoolExecutor

S = "/fast/scratch/hyaku/souji-r41/R41w2executor03"
REVS = {
    "base": ("7eebc183f2685d1ea9b004b4de22c09a8a4035a7", "40"),
    "tip": ("1d41c13574db80fdd9a4bde490b712da7ce2a85f", "41"),
}
B = S + "/blobs"
CL = S + "/clone.git"
# (name, command) ; {REV} {ROUND} {CL} {B} {SCR} substituted; cwd = extracted tree
CASES = [
 ("souji-verify selftest", "bash tools/souji-verify.sh --selftest"),
 ("souji-vault-verify selftest", "SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest"),
 ("souji-census selftest", "bash tools/souji-census.sh --selftest"),
 ("souji-quarantine selftest", "bash tools/souji-quarantine.sh --selftest"),
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
 ("souji-proc-census selftest", "bash tools/souji-proc-census.sh --selftest"),
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
 ("r29-registry-agreement fixture", "python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py"),
 ("r28-wave-evidence-capture", "bash tests/fixtures/r28-wave-evidence-capture.sh"),
 ("r30-landing-gate-discovery", "python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py"),
 ("r31-landing-gate-precision", "python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py"),
 ("r38-citation-commit", "python3 -B tests/fixtures/r38-citation-commit.py"),
 ("r38-drift-write-envelope", "python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool {B}/drift-4c257b7.py"),
 ("r38-drift-record", "python3 -B tests/fixtures/r38-drift-record.py"),
 ("r38-drift-mutants", "python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py"),
 ("r39-citation-rev", "python3 -B tests/fixtures/r39-citation-rev.py"),
 ("r39-drift-record-rules", "python3 -B tests/fixtures/r39-drift-record-rules.py"),
 # lane's own checks, against a bare no-local clone of the lane (read-only git)
 ("souji-registry-agreement (lane check)", "python3 -B tools/souji-registry-agreement.py --root {CL} --rev {REV} --list-rev {PREREG}"),
 ("souji-landing-gate (lane check)", "python3 -B tools/souji-landing-gate.py --root {CL} --rev {REV} --round {ROUND}"),
]

def run(rev_key, idx, name, cmd):
    rev, rnd = REVS[rev_key]
    G = os.environ.get("GIT") == "1"
    tree = f"{S}/{'g' if G else ''}{rev_key}"
    # tree dir is named base/tip; the cwd is inside the extracted tree
    tmp = f"{S}/tmp/{'g' if G else ''}{rev_key}-{idx:02d}"
    if os.environ.get("VARTMP") == "1":
        tmp = f"/var/tmp/r41w2e03-{'g' if G else ''}{rev_key}-{idx:02d}"
    os.makedirs(tmp, exist_ok=True)
    prereg = "b8cb4b31ce80e2e3314b88e85d40ea9873180804"
    c = cmd.format(B=B, CL=CL, REV=rev, ROUND=rnd, SCR=tmp, PREREG=prereg)
    env = dict(os.environ, TMPDIR=tmp, PYTHONDONTWRITEBYTECODE="1")
    t = time.time()
    try:
        p = subprocess.run(["bash", "-c", c], cwd=tree, env=env, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc = 124
        out = ((e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")) + "\nTIMEOUT 120s"
    dt = time.time() - t
    lf = f"{S}/logs/{'g' if G else ''}{'v' if os.environ.get('VARTMP')=='1' else ''}{rev_key}-{idx:02d}.txt"
    os.makedirs(S + "/logs", exist_ok=True)
    open(lf, "w").write(f"$ cd {tree} && TMPDIR={tmp} {c}\n# rc={rc} wall={dt:.1f}s\n{out}")
    if tmp.startswith("/var/tmp/r41w2e03-"):
        subprocess.run(["rm", "-rf", tmp])
    return dict(rev=rev_key, idx=idx, name=name, cmd=c, rc=rc, wall=round(dt, 1), log=lf, tail=out.strip().splitlines()[-3:])

if __name__ == "__main__":
    only = sys.argv[1:]
    jobs = []
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "6"))) as ex:
        for i, (n, c) in enumerate(CASES):
            if only and str(i) not in only:
                continue
            for k in ("base", "tip"):
                jobs.append(ex.submit(run, k, i, n, c))
        res = [j.result() for j in jobs]
    json.dump(res, open(S + "/results-%s%s%s.json" % ("g" if os.environ.get("GIT")=="1" else "", "v" if os.environ.get("VARTMP")=="1" else "", "-" + "_".join(only) if only else ""), "w"), indent=1)
    for r in sorted(res, key=lambda r: (r["idx"], r["rev"])):
        print(r["idx"], r["rev"], r["rc"], r["wall"], r["name"], "|", r["tail"][-1][:140] if r["tail"] else "")
