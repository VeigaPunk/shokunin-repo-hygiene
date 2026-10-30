# R43sentinel01 — frozen instrument write-envelope audit

Axes: operability, coverage, write-envelope containment, provenance.
Verdict: four scoped checks pass; C3 has a reproducible low-severity `--scratch` containment defect. No remediation applied to frozen instruments.

## Evidence and execution

All evidence below is under `.ufo/waves/round-43/w1/R43sentinel01/` (abbreviated `A`). `audit.py` contains the exact commands, fixture bytes, per-command identity environment, and scratch cleanup. `output.txt` is the captured output; `run-receipt.txt` preserves the tool result. Instrument copies in A were obtained with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/<name>` for `score-candidate.sh`, `c1-counter.py`, `c2-counter.py`, `c3-counter.py`, and `c2-hidden-audit.py`.

Executed:
```
strace -f -e trace=%file -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43sentinel01/file-trace.txt python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43sentinel01/audit.py
```
Observed exit 0, uid=1000, final `scratch_removed=True`. The large trace was reduced to retained `trace-excerpt.txt`; command stdout is in `output.txt`. No tools installed or upgraded. Existing `strace` was used.

The live master had advanced to `8dfad888d7b7673de41cdcd92f30244c16e38519`, so harness probes used a scratch-only source clone pinned to assigned base `13de0e84b45efd1113f077d58fc1e89bc586a013`. Driver asserts that this base's harness equals the frozen harness bytes. All explicit fixture mutations assert fixture repository root first. No lane git mutation, candidate scoring result, or current-master readiness is claimed.

## 1. Harness destination envelope — PASS for requested destinations

Command pattern actually executed (expanded argv for every invocation is retained in `output.txt`):
```
bash "$S/harness-repo/census/round-43/score-candidate.sh" c2 "$S/scores" "$dest=$A/c2-counter.py"
```
Here the driver's literal `S` is `/fast/scratch/hyaku/souji-r43/R43sentinel01`. Tested destinations and observed stderr, all exit 2:
```
score-candidate: dest census/round-43/c2-counter.py is not on the allowlist
score-candidate: dest census/round-43/c3-survivors.tsv is not on the allowlist
score-candidate: dest census/round-43/preregistration.txt is not on the allowlist
score-candidate: dest ../escape is not on the allowlist
score-candidate: dest /absolute is not on the allowlist
```
Then the scratch source clone alone committed an allowlisted leaf symlink for `tools/souji-freeze-check.py`, pointed its scratch master at that fixture commit, and invoked the same harness. Observed exit 2:
```
score-candidate: dest tools/souji-freeze-check.py is a symlink in the clone
symlink-victim='CANARY\n'
```
Frozen harness lines 36–40 perform exact allowlisting and leaf `-L` refusal before copying. This verifies leaf symlinks, not a general directory-symlink/race sandbox. Refusal still creates and cleans a scratch clone; zero scratch mutation was not claimed.

## 2. C2 synthetic builders and HOME — PASS, scoped to builders

Exact Python calls in `audit.py`:
```
os.environ['HOME'] = S + '/home'
for name, mut in c2.CASE_BUILDERS.items():
    d, tip, _ = c2.build(S + '/c2', name, mut)
```
Observed nine successful `C2 built .../c2/<case> tip=<40hex>` records and `HOME files=[]`. Printed child environment has TMPDIR under that scratch and global/system git configuration set to `/dev/null`; HOME and caller identity are not inherited. Frozen `build` lines 119–175 construct all writes below its scratch/name, check repository root, and route every git call through `-C` and the explicit fixture environment. No synthetic-builder HOME/global-config write observed. This is not a claim that arbitrary candidate code is sandboxed or that the entire C2 score was run; its full r42/selftest legs were not run.

## 3. C3 fixture cwd and generated files — PARTIAL PASS; F1 containment defect

Exact canonical-runner call from `audit.py`:
```
c3.run_fixture(fx, A + '/c3-counter.py', S + '/c3/fixture', S + '/c3')
```
`fx` is the retained benign fixture byte string which writes relative `cwd-canary`, prints cwd, then `SUMMARY cases=1 pass=1 fail=0`. Observed exit 0, no timeout, copied fixture below explicit scratch, cwd and canary value both `.../R43sentinel01/c3`. `trace-excerpt.txt` records the relative `openat(..., "cwd-canary", O_WRONLY|O_CREAT|O_TRUNC...)`. Thus canonical `run_fixture` pins cwd to scratch, not lane. Static frozen code at lines 303–317, 358–395 places rev tool, mutant files, prior fixture copies and shim files below `work = mkdtemp(dir=scratch)`. Full population scoring was not run.

### F1 — LOW: C3 discrimination selftest ignores `--scratch`

Attacks: frozen `census/round-43/c3-counter.py`, `stderr_discrimination_selftest` lines 248–272, called unconditionally at line 401.

Local failure path: supply an ambient TMPDIR different from the explicit `--scratch`. Unlike the other generated fixture/tool files, this function calls `tempfile.mkdtemp(prefix="r43c3disc-")` without `dir=scratch`; it also invokes its children without the counter's sanitized environment or explicit cwd. This direct reproduction did not modify the module or monkeypatch tempfile:
```
TMPDIR=/fast/scratch/hyaku/souji-r43/R43sentinel01/ambient strace -f -e trace=%file -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43sentinel01/c3-direct-trace.txt python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43sentinel01/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 13de0e84b45efd1113f077d58fc1e89bc586a013 --scratch /fast/scratch/hyaku/souji-r43/R43sentinel01/explicit
```
Observed exit 1 (baseline target unmet), with `stderr_discrimination=ok anchors=ok population=ok`. `c3-direct-output.txt` contains the full command/output. `c3-direct-writes.txt` preserves successful mkdir/open syscalls, including these exact out-of-`--scratch` write targets:
```
/fast/scratch/hyaku/souji-r43/R43sentinel01/ambient/r43c3disc-52vsck84/fixture.py
/fast/scratch/hyaku/souji-r43/R43sentinel01/ambient/r43c3disc-52vsck84/tool.py
```
These are observed target strings, not references to surviving scratch evidence. Both directories used for reproduction remained inside this seat's allowed scratch, and were deleted afterwards. Impact: standalone C3 CLI does not honor the promised explicit scratch envelope for all tool/fixture copies; it can create files in an ambient temp directory while reporting a healthy discrimination leg. Harness callers that set ambient TMPDIR to their scratch mask this defect. No lane escape, privilege escalation, arbitrary-code exploit or persistent write was attempted or observed.

Smallest remediation for L1 after frozen scoring: pass scratch into `stderr_discrimination_selftest`, use `mkdtemp(..., dir=scratch)`, and pass explicit scratch cwd/environment to its subprocesses. Frozen files left unchanged.

## 4. Hidden audit global git canary — PASS for write-state check

Exact calls in `audit.py`:
```
os.environ['GIT_CONFIG_GLOBAL'] = S + '/global.gitconfig'
hidden.main(['--tool', S + '/freeze-tool.py', '--work', S + '/hidden'])
```
Canary was `[sentinel]\n\tvalue = untouched\n`; tool bytes came from assigned base. Observed `SUMMARY scenarios=10 pass=5 fail=5`, return 1, and:
```
global_canary_unchanged=True sha256=eb6f20ff8051422cace1cedb2a2f2306469233b99d9e02e8c721e303cc7ee383
```
The five scenario failures concern the uncorrected base tool, not global-state leakage; they are not counted as passes. Frozen audit normally forces git global/system configuration to `/dev/null`. Its line 152 `git add` inherits the caller environment (unlike other git calls), but this run did not change the canary. The verdict is no observed global mutation, not complete environment isolation. Audit removed its work directory; driver removed remaining scratch.

## 5. C1 rederive kinds execute no repository code — PASS for named rederive surface

Exact calls in `audit.py`: load frozen required TSV with git show, then call `c1.rederive(row['kind'], row, S, L)` for all three registered rows, recording each `c1.git` argv. Observed:
```
C1 rederive census-rows (True, 'rows=174')
C1 rederive census-w04 (True, 'W04=48')
C1 rederive receipt-header-rev (True, 'others=[]')
```
`output.txt` records four git-show reads for the census rows/W04 kinds, one receipt git-show read, and `git diff --name-only <derived> <rev> -- census tools tests` for receipt-header-rev. Frozen lines 146–182 use committed blob bytes and in-process counters only; no eval/import/exec of repository code occurs in these branches. This does not extend to all C1 main: its separate append-only leg intentionally executes the BASE-pinned declared-evidence tool (lines 265–275).

## Limits and cleanup

No main `resume_continuity_v1` route is part of this assigned instrument surface. No other runtime invoked, no instrument remediation, no root execution, no PATH-directory writes, no process signalling, no scoring integration. Required scratch was removed after both runs. Retained files are audit evidence, not production candidates. Full C2/C3 population/regression scores were intentionally not represented as exercised verification.
