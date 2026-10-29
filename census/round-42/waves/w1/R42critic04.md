# R42critic04 — critic attack on C3 (coverage), round 42

Seat: R42critic04 (critic, leaf). Freeze commit afe17f416eec04dcf3f480b580a8f928de61d19d (lane tip scored by `score-candidate.sh`). Pinned tool sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (verified against the lane file and the scratch copy). No lane, fleet, or tracked file was written; no git/jj mutation; no tool was installed.

## Verdict

The frozen counter cannot tell a behaviour-observing fixture from one that never runs the tool. Four of the five attack candidates below reach the full C3 target (`killed=13`, `equiv_killed=0`, `pristine=ok`, `anchors=ok`) under `score-candidate.sh`, and so does the honest behaviour-only candidate K1. The C3 SUMMARY therefore does not establish the predicate "observes tool behaviour". The L1 must add the four outside checks in section 3 before landing; with them, only K1 passes. Two counter-level defects were also observed (section 4): the crash rule turns an honest diagnostic into a survivor (K6 scores 11/13), and the prior-battery gate `old_killed` flipped to 1 in 3 of 8 score runs without a reproducible cause.

## 1. Candidates and counter verdicts

All five candidates were scored with the frozen counter, `bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42critic04 tests/fixtures/r42-drift-conditions.py=<file>`. The SUMMARY lines are verbatim from `outputs/score-*.txt`.

| candidate | SUMMARY (verbatim) | reaches target? | the gap |
|---|---|---|---|
| K1 `k1-behaviour.py` (honest: runs the tool, asserts rc, refusal class, DRIFT rows, JSON) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | yes | none found. Passes all four outside checks (section 3). Residual: time-sensitive (B1 uses a 15 s bound, G3/G4 use a 2 s fake git against `--timeout 1`/default 20); not exercised under sustained load. |
| K2 `k2-anchor-sniff.py` (hard-codes the 13 condition lines, never runs the tool) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=1 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (run 1); two quiet re-scores gave `old_killed=0` with the other fields identical (`outputs/rescore-k2-run{1,2}.txt`) | yes (apart from the `old_killed` flake, section 4) | reads bytes, never executes. The six equivalents survive only because none of their edits touches the 13 lines. Caught by: execution-count shim (0 invocations); rewrite check (behaviour-identical rewrite of the pristine tool fails 13/13); static audit (BYTE-READ / TOOL-USE, line 35). Not caught by rename check (byte-based). |
| K3 `k3-id-keyed.py` (never runs the tool; fails the case whose ID equals the `--tool` basename `mut-<ID>.py`) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | yes | keys on the counter's file naming. Caught by: execution-count shim (0 invocations); rename check (0/13 killed); static audit (3 findings). Not caught by rewrite check. |
| K4 `k4-keyed-behaviour.py` (K1 plus a name key on each case; the key never changes a verdict under the frozen mutants because behaviour already kills the 13) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=1 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (run with old_killed=1; the flake, section 4) | yes | a hybrid that invokes the tool and still reads the `--tool` name. Passes the execution-count shim (13/13 invocations) and the rename check (13/13). Caught only by the static audit (TOOL-USE and MUT-LITERAL, line 24). |
| K5 `k5-hybrid-keyed.py` (K1, but case B1 is decided by the file name alone, after the tool has run) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | yes | passes the execution-count shim (13 invocations) and is caught by the rename check (B1 becomes clean: `TALLY killed=12/13`). Static audit: 2 findings. |
| K6 `k6-forwards-traceback.py` (K1, but a tool traceback is written to the fixture's stderr) | `SUMMARY mutants=13 killed=11 survived=2 pristine=ok prior=8/8 old_killed=1 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | NO — honest candidate fails the counter | counter defect (section 4.2): `MUTANT G4 candidate=SURVIVED`, `MUTANT H2 candidate=SURVIVED`. Under the harness both mutants give `crash=True` with a correct FAIL. |

## 2. Commands run and key output

Setup and pinning:
- `git --version` 2.56.0; `python3 --version` 3.14.8; `sha256sum` of lane tool and scratch copy: both `b2a603cf…34dc6`.
- Fresh-repo probes (`git worktree list --porcelain`, `prune --dry-run -v`, `rev-parse --absolute-git-dir`) confirmed that `regs=1 prunable=0` for a fresh `git init` and that a `.git` file pointing at a missing gitdir gives `rc 128`.

Fixture iteration:
- `attack-harness.py --fixture k1-behaviour.py --mode verdicts`: first run had E2 `killed=12/13` (E2 survived). Cause: my E2 setup made the sibling a git repo, so the gitdir containment check, not the row check, refused the mutant's path. Fixed by making the sibling a plain directory. Second run: `TALLY killed=13/13 equiv_killed=0/6 pristine_clean=True`. (Fixture defect fixed by me before scoring; not a counter defect.)

Harness modes, outputs under `outputs/` (all with the frozen counter's `run`/`killed`/`clean` and tables loaded read-only from the lane):

| candidate | verdicts | count (invocations) | rename | rewrite | static audit |
|---|---|---|---|---|---|
| K1 | `TALLY killed=13/13 equiv_killed=0/6 pristine_clean=True` | `PRISTINE-INVOCATIONS 13 (cases=13)`, `TALLY killed=13/13 equiv_killed=0/6` | `TALLY killed=13/13 equiv_killed=0/6` | `TALLY killed=13/13 equiv_killed=0/6 pristine_clean=True` | 0 findings |
| K2 | `TALLY killed=13/13 equiv_killed=0/6` | `PRISTINE-INVOCATIONS 0`; pristine FAILs (wrapper bytes also trip the byte read, so this is confounded) | `TALLY killed=13/13 equiv_killed=0/6` (byte-keyed, not caught) | `PRISTINE killed` (pristine-rewritten fails 13/13); `TALLY killed=13/13 equiv_killed=6/6 pristine_clean=False` | 1 finding (`args.tool` at line 35) |
| K3 | `TALLY killed=13/13 equiv_killed=0/6` | `PRISTINE-INVOCATIONS 0`; `TALLY killed=13/13` | `TALLY killed=0/13 equiv_killed=0/6` | `TALLY killed=13/13 equiv_killed=0/6 pristine_clean=True` (not caught) | 3 findings (incl. "mut-" in docstring, a false positive) |
| K4 | `TALLY killed=13/13 equiv_killed=0/6` | `PRISTINE-INVOCATIONS 13 (cases=13)`; `TALLY killed=13/13` (passes shim) | `TALLY killed=13/13 equiv_killed=0/6` (passes rename) | `TALLY killed=13/13 equiv_killed=0/6 pristine_clean=True` | 2 findings (line 24) |
| K5 | `TALLY killed=13/13 equiv_killed=0/6` | `PRISTINE-INVOCATIONS 13 (cases=13)`; `TALLY killed=13/13` (passes shim) | `TALLY killed=12/13` (caught) | not run | 2 findings (line 87) |
| K6 | `TALLY killed=11/13 equiv_killed=0/6 pristine_clean=True` (G4, H2 `other`, `crash=True`) | not run | not run | not run | not run |

Static audit: `python3 -B static-audit.py k1 k2 k3 k4 k5` gives K1 0; K2 1; K3 3; K4 2; K5 2 (`outputs/static-audit.txt`). Its BYTE-READ label is approximate; the TOOL-USE and MUT-LITERAL findings are the reliable ones.

## 3. Outside-the-counter checks the L1 needs (ranked by what they catch)

1. Static audit (`static-audit.py`): flags any use of the `--tool` path outside a subprocess argv or the binding assignment, and any literal containing `mut-`. Catches K2, K3, K4, K5. Limit: a rename of the keyed variable defeats a naive grep, so the AST walk is required; it does not prove behaviour, only that the path is never read.
2. Execution-count shim (the lead's proposal): wrap `--tool` so each invocation appends to a log; require invocations ≥ cases. Catches K2 and K3 (0 invocations). Does NOT catch K4 or K5, which invoke the tool once per case. Limit: the wrapper changes the tool's bytes, which confounds any byte-reading fixture.
3. Rename invariance: run each mutant under a neutral name; a verdict that changes with the name is name-keyed. Catches K3 and K5. Does not catch K4 (behaviour kills, so the key is dead under the frozen mutants) or K2 (byte-keyed).
4. Rewrite invariance: rewrite the 19 anchors into behaviour-identical forms (`outputs/k*-rewrite.txt`); the fixture must still be clean on the pristine rewrite and kill the same mutants. Catches K2 (pristine-rewritten fails 13/13). Does not catch K3, K4, K5 (name-keyed, pristine name unchanged).

Consequence: the four checks together separate K1 (passes all) from K2 (count, rewrite, static), K3 (count, rename, static), K4 (static only), K5 (rename, static). K4 is the one that only static audit catches; the L1 must not rely on the shim alone.

## 4. Counter-level defects (frozen; reported, not edited)

4.1 Outcome-only kill rule. `census/round-42/c3-counter.py` scores SUMMARY and exit code only, so byte-keyed and name-keyed fixtures reach the target (K2–K5). The preregistration's rule 3 disqualification ("reads the counter, the mutant table or a label") has no automated check; the L1 must run section 3.

4.2 Crash rule turns an honest diagnostic into a survivor. `killed()` requires `not crash`, and `crash` is set when the fixture's stderr contains `Traceback`. K6 forwards the tool's traceback to its own stderr, so G4 (`raise` in `measure`) and H2 (`parse_record(None)`) are scored SURVIVED although the fixture fails them. Result: K6 `killed=11 survived=2`. This rewards fixtures that hide tool tracebacks. Recommendation for the L1: count a tool traceback as a kill when the fixture reports the failing case, or make the crash rule apply only to the fixture's own traceback.

4.3 Prior-battery gate is unstable. `old_killed` should be 0. In 3 of 8 scored runs a prior fixture killed one population mutant: r36 killed H2 (K2 run 1), M1 (K4), and G5 (K6). Quiet rescores of K2 (×2) gave 0, and K1, K3, K5 gave 0. Attempts to reproduce failed: 16 parallel `r36` runs against M1/H2 with a fresh env; 6 parallel against G5/M1/H2; 24 runs through the counter's own `run()` (8 parallel, ×3 mutants) with `GIT_CONFIG_*`/`LC_ALL` env; all 12/12 pass. Cause not identified; the counter discards the fixture's stdout, so the failing case could not be captured. [INFERENCE] The likely factor is load from concurrent seats during those score runs, but no evidence confirmed it. The L1 should re-measure at the landed tip in quiet conditions and capture r36's FAIL line before accepting `old_killed=0` or ≠0.

## 5. Notes

- No "memorised pinned output" candidate was built. [INFERENCE] Without executing the tool, memorised outputs can only separate mutants by bytes or name, which reduces to K2/K3.
- The harness reads a copy of the pinned tool from the scratch path `/fast/scratch/hyaku/souji-r42/R42critic04/pristine.py` (sha verified `b2a603cf…`). That scratch dir is removed at yield; to reproduce, copy the lane tool to that path and re-check the sha.
- Installed tools: none. Mutating git/jj in lane or fleet: none.

## Files (seat-relative, all under `.ufo/waves/round-42/w1/R42critic04/`)

- Candidates: `k1-behaviour.py`, `k2-anchor-sniff.py`, `k3-id-keyed.py`, `k4-keyed-behaviour.py`, `k5-hybrid-keyed.py`, `k6-forwards-traceback.py`
- Tools: `attack-harness.py` (modes verdicts/count/rename/rewrite), `static-audit.py`
- Receipts: `outputs/score-*.txt` (SUMMARY lines), `outputs/rescore-k2-run{1,2}.txt`, `outputs/*-{verdicts,count,rename,rewrite}.txt`, `outputs/k5-*.txt`, `outputs/k6-forwards-traceback-verdicts.txt`, `outputs/static-audit.txt`

## Verdict line

C3 as scored by the frozen counter does not establish behaviour observation: 5 of 6 candidates reach the SUMMARY target (K1 honest; K2–K5 attack), and K6 (honest) misses it because of the crash rule. Only K1 passes all four outside checks. Land only with checks 1–4 in section 3 applied, and treat the `old_killed` flake and the crash rule as open counter defects.
