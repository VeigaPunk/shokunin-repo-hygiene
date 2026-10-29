# R42reviewer03 — C3 group A re-derivation (B1 E2 E4 G2 G3 G4 G5)

Lane: souji-shokunin, freeze afe17f416eec04dcf3f480b580a8f928de61d19d (HEAD confirmed by `git -C <lane> rev-parse HEAD`).
Pinned tool: tools/souji-worktree-drift.py, sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (checked before and after the run; the lane was not written).
Counter: census/round-42/c3-counter.py (MUTANTS and EQUIV tables read at lines 60-103; main() at 161-253).
Toolchain used as found (no installs): git 2.56.0 (/usr/bin/git), Python 3.14.8 (/usr/bin/python3), timeout, bash. Uid 1000 (not root).

## Scope
Group A only: B1 E2 E4 G2 G3 G4 G5 (7 of the 13 MUTANTS). The six EQUIV mutants (B3 B4 E5 E7 E9 H4) are not in this assignment and were NOT examined here; no equivalence claim is made by this report for them.

## Mutant generation
Each `mut-<ID>.py` is the pinned tool with `str.replace(old, new)` applied to an in-memory copy; the script asserted `source.count(old) == 1` before each replacement and `ast.parse` succeeded on each output. Files: `.ufo/waves/round-42/w1/R42reviewer03/mut-<ID>.py`.

| ID | old -> new (one occurrence) | mutant sha256 (first 16) |
|---|---|---|
| B1 | `fd = os.open(path, os.O_RDONLY \| os.O_NONBLOCK)` -> `fd = os.open(path, os.O_RDONLY)` | 13a5d1189f815782 |
| E2 | `inside = os.path.commonpath([resolved, root_real]) == root_real` -> `...commonprefix(...)...` | 2c6e7842018f0afe |
| E4 | `gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real` -> `...commonprefix(...)...` | e8e997d99fef0adb |
| G2 | `if args.timeout < 1:` -> `if args.timeout <= 1:` | 83bdd007530897e9 |
| G3 | `default=20` -> `default=1` | 53b8ba7ed7f7d579 |
| G4 | `return None, None, "UNREACHABLE:list-timeout"` -> `raise` | 8b9fb73e4a268874 |
| G5 | `if listed.returncode != 0:` -> `if False:` | a9427147e01e7a93 |

Diff check (`diff tools/souji-worktree-drift.py mut-G4.py`): line 194 `return None, None, "UNREACHABLE:list-timeout"` -> `raise`; `diff ... mut-E2.py`: line 296 commonpath -> commonprefix. No other change.

## Frozen-instrument survey (prior fixtures)
Command (run from any cwd; scratch is /fast/scratch/hyaku/souji-r42/R42reviewer03):
`bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42reviewer03 tests/fixtures/r42-drift-conditions.py=census/round-42/controls/c3-stub-allpass.py`
Output saved verbatim at `.ufo/waves/round-42/w1/R42reviewer03/survey-c3-stub-allpass.txt`. Group-A lines:
```
MUTANT B1 candidate=SURVIVED prior=-
MUTANT E2 candidate=SURVIVED prior=-
MUTANT E4 candidate=SURVIVED prior=-
MUTANT G2 candidate=SURVIVED prior=-
MUTANT G3 candidate=SURVIVED prior=-
MUTANT G4 candidate=SURVIVED prior=-
MUTANT G5 candidate=SURVIVED prior=-
SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
exit=1
```
`prior=-` means no one of the eight PRIOR fixtures kills the mutant (the counter runs every prior fixture against every mutant regardless of `--survey`; `prior=8/8` shows all eight run clean on the pristine tool, so a `-` is not a crashed prior fixture masking a kill). `anchors=ok` confirms the population's anchor sha256 values match the MUTANTS old strings. The stub run also prints `exit=1` by design (target unmet: the stub kills nothing).

## Probes (pristine vs mutant, identical arguments)
Each `probe-<ID>.sh` builds its scenario under /fast/scratch/hyaku/souji-r42/R42reviewer03/probe-<ID>/ (removed by an EXIT trap), runs `python3 -B` on the pristine tool and on `mut-<ID>.py`, and appends rc/stdout/stderr to `receipts/probe-<ID>.txt`. Helpers: `probe-lib.sh`. Command run: `for id in B1 E2 E4 G2 G3 G4 G5; do bash .ufo/waves/round-42/w1/R42reviewer03/probe-$id.sh; done` (run twice; the second run's receipts are the ones kept; all seven exited 0).

| mutant | observable on pristine vs mutant? | probe path | receipt | notes |
|---|---|---|---|---|
| B1 | YES. Pristine: rc 2, `REFUSAL RECORD-MALFORMED: .../rec.fifo is not a regular file`, immediate. Mutant: rc 124 (killed by `timeout 5`), no output; `os.open` blocks on the FIFO. | probe-B1.sh | receipts/probe-B1.txt | FIFO with no writer. A candidate fixture must bound the tool itself (subprocess timeout) and print its SUMMARY, because the counter's `run()` returns `cases=None` on a 300 s hang and `killed()` is then false. |
| E2 | YES, two ways. Case 1 (row refusal): pristine `REFUSAL RECORD-OUTSIDE-ROOT: ../fleet-sib resolves outside ...`; mutant rc 2 with `REFUSAL RECORD-OUTSIDE-ROOT: ../fleet-sib gitdir resolves outside ...` (row check passes, the unchanged gitdir check refuses). Case 2 (success path): pristine rc 2 refused; mutant rc 0 with `SUMMARY ... live_repos=1 ... drift_rows=0`. | probe-E2.sh | receipts/probe-E2.txt | Case 1 alone is invisible to an rc-only check (both rc 2, same class prefix); only the message text or the case-2 success path distinguishes. |
| E4 | YES. Pristine rc 2 `REFUSAL RECORD-OUTSIDE-ROOT: alpha gitdir resolves outside ...`; mutant rc 0 with `SUMMARY ... live_repos=1 live_regs=1 drift_rows=0`. | probe-E4.sh | receipts/probe-E4.txt | alpha is `git init --separate-git-dir=<fleet-store/alpha.git>`; the gitdir shares the string prefix `<root>` but is not under it. |
| G2 | YES. `--timeout 1`: pristine rc 0 SUMMARY (clean); mutant rc 2 `REFUSAL USAGE: --timeout must be >= 1`. Control `--timeout 0`: both rc 2 (identical). | probe-G2.sh | receipts/probe-G2.txt | Deterministic, no timing. |
| G3 | YES. With a PATH git wrapper that sleeps 2 s on `worktree list` and no `--timeout`: pristine (default 20) rc 0 clean; mutant (default 1) rc 1 `DRIFT UNREACHABLE alpha UNREACHABLE:list-timeout`, SUMMARY unreachable=1. Controls: pristine `--timeout 1` gives the same UNREACHABLE row; mutant `--timeout 20` is clean, so the default is the only difference. | probe-G3.sh | receipts/probe-G3.txt | Kill needs a stall in (1 s, 20 s) on a git call with no explicit `--timeout`; real git on a healthy repo is too fast to observe the default, so the fixture needs a stalling git (wrapper on PATH, as here). |
| G4 | YES. `--timeout 1` with 2 s stall: pristine rc 1 `DRIFT UNREACHABLE alpha UNREACHABLE:list-timeout` + SUMMARY unreachable=1; mutant rc 1 with no DRIFT line, no SUMMARY, and an uncaught `subprocess.TimeoutExpired` traceback on stderr. | probe-G4.sh | receipts/probe-G4.txt | Exit code is the same (1) for both; the kill must read stdout (DRIFT/SUMMARY present) or the traceback. |
| G5 | YES. Wrapper makes `worktree list` exit 3 with no output; record regs=1: pristine rc 1 `DRIFT UNREACHABLE alpha UNREACHABLE:list-rc=3`; mutant rc 1 `DRIFT REGS-CHANGED alpha record=1 live=0` (list treated as 0 registrations). | probe-G5.sh | receipts/probe-G5.txt | Exit code identical (1); kill must check the drift class / SUMMARY counters. |

Probe receipt excerpts (verbatim, from receipts/):
- B1: `=== pristine rc=2 ...` / `REFUSAL RECORD-MALFORMED: ... rec.fifo is not a regular file`; `=== mutant rc=124 ...` (empty output).
- E2 case2: `=== case2-pristine rc=2 ...` `REFUSAL RECORD-OUTSIDE-ROOT: ../fleet-sib2 resolves outside ...`; `=== case2-mutant rc=0 ...` `SUMMARY record=... record_repos=1 record_regs=1 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=0 unreachable=0`.
- E4: `=== pristine rc=2 ...` `REFUSAL RECORD-OUTSIDE-ROOT: alpha gitdir resolves outside ...`; `=== mutant rc=0 ...` SUMMARY with drift_rows=0.
- G2: `=== pristine rc=0`; `=== mutant rc=2 ...` `REFUSAL USAGE: --timeout must be >= 1`.
- G3: `=== pristine rc=0 ...` SUMMARY drift_rows=0; `=== mutant rc=1 ...` `DRIFT	UNREACHABLE	alpha	UNREACHABLE:list-timeout`; `=== mutant-timeout20 rc=0 ...`.
- G4: `=== pristine rc=1 ...` `DRIFT	UNREACHABLE	alpha	UNREACHABLE:list-timeout`; `=== mutant rc=1 ...` empty stdout, traceback ending `subprocess.TimeoutExpired: Command '[... 'worktree', 'list', '--porcelain']' timed out after 1 seconds`.
- G5: `=== pristine rc=1 ...` `DRIFT	UNREACHABLE	alpha	UNREACHABLE:list-rc=3`; `=== mutant rc=1 ...` `DRIFT	REGS-CHANGED	alpha	record=1 live=0`.

## Verdict
- All seven group-A mutants are NON-equivalent: each has an observable difference (rc, stdout/SUMMARY, stderr refusal text, or a traceback) between the pristine tool and the mutant under the probe scenario shown above. None is an EQUIV mutant, and none is observable only by bytes.
- All seven survive the eight PRIOR fixtures (`prior=-` for each, `prior=8/8` pristine-clean). The survey supports the C3 population claim for group A.
- Kill-predicate cautions for the L1 and the candidate author (these follow from `killed()` in c3-counter.py lines 151-153, not from any frozen-file defect):
  1. B1 hangs the mutant; a fixture that does not bound the tool with its own timeout and print a SUMMARY with fail>0 will NOT count as a kill.
  2. E2 case 1 and G4/G5 keep the exit code unchanged (E2 rc 2, G4/G5 rc 1); the kill has to read the refusal text, the drift class, or the SUMMARY counters. A fixture asserting only the exit code kills none of them.
  3. G3 needs a stalling git on PATH (a 1 s to 20 s stall); an unstalled fixture cannot observe the default.
- No defect was found in the frozen counter, population, or pinned tool for group A. Nothing was edited in a frozen file.
- Not verified by this report: the candidate fixture tests/fixtures/r42-drift-conditions.py itself (not in scope for this seat); the six EQUIV mutants (not in group A).

## Limits
- Probes use scenarios I built; they show observability of each mutant, not that the candidate fixture kills them.
- Survey uses the always-pass stub, so `candidate=SURVIVED` is by construction; only the `prior=` column carries information here.
