# R42executor08 — C3 candidate fixture

Candidate: `.ufo/waves/round-42/w1/R42executor08/r42-drift-conditions.py` (13098 bytes, sha256 `aca10eff081967c5c1a8a1ac622355fb5e655ed8d9f0ec6228af4c0ccff2bd72`), 14 cases, no tool-source read, no hash, no label search.
Receipt: `.ufo/waves/round-42/w1/R42executor08/score-final.txt` (scorer output).

## Probes (one per mutant, behaviour only)
- B1: FIFO record -> exit 2 + `REFUSAL RECORD-MALFORMED` (mutant blocks; 60 s subprocess timeout = FAIL).
- E2: repo dir `root-sibling` (name-prefix of root) whose gitdir is inside root -> `RECORD-OUTSIDE-ROOT`. (First attempt used a sibling whose gitdir was also outside, so the gitdir check masked it; E2 survived. Fixed.)
- E4: `root/r/.git` -> gitdir in `root-gd` -> `RECORD-OUTSIDE-ROOT`.
- G2: `--timeout 1` accepted (rc 0/1, no REFUSAL).
- G3: git shim on PATH sleeps 2 s; default timeout must complete (rc 0, no UNREACHABLE).
- G4: shim hangs on `worktree list`, `--timeout 1` -> rc 1, UNREACHABLE reported, no Traceback.
- G5: shim exits 128 on `worktree list` -> rc 1 and UNREACHABLE.
- H1/H2: missing `--root` / `--record` -> rc 2, argparse "required" text naming the flag, no REFUSAL/Traceback.
- I1: symlink child of root to an outside repo, no `--skip-unrecorded` -> rc 0, no UNRECORDED.
- J9: `regs=10` row -> rc 1 REGS-CHANGED, not RECORD-MALFORMED.
- M1: pre-existing 20000-byte `X` file as `--json` target -> afterwards valid JSON, no `XXXX` tail.
- D4: record name `bad\xffname`, directory `bad\xef\xbf\xbdname` exists -> rc 0, no ABSENT (replace maps to U+FFFD; backslashreplace spells `bad\xffname` -> ABSENT).
- baseline-clean-run: two repos + TOTAL row -> rc 0 (scaffold sanity).

## Commands and output
Pristine run: `python3 -B <cand> --tool tools/souji-worktree-drift.py --work $S/w` -> `SUMMARY cases=14 pass=14 fail=0`, rc 0, wall 7.7 s.

Score: `bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor08 tests/fixtures/r42-drift-conditions.py=<cand>` (wall 76.6 s):
```
MUTANT B1 candidate=killed prior=-
MUTANT E2 candidate=killed prior=-
MUTANT E4 candidate=killed prior=-
MUTANT G2 candidate=killed prior=-
MUTANT G3 candidate=killed prior=-
MUTANT G4 candidate=killed prior=-
MUTANT G5 candidate=killed prior=-
MUTANT H1 candidate=killed prior=-
MUTANT H2 candidate=killed prior=-
MUTANT I1 candidate=killed prior=-
MUTANT J9 candidate=killed prior=-
MUTANT M1 candidate=killed prior=-
MUTANT D4 candidate=killed prior=-
EQUIV B3 candidate=survived prior=-
EQUIV B4 candidate=survived prior=-
EQUIV E5 candidate=survived prior=-
EQUIV E7 candidate=survived prior=-
EQUIV E9 candidate=survived prior=-
EQUIV H4 candidate=survived prior=-
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=14 tool_sha=b2a603cf4247
```
Scorer exit: the final counter exit was not captured directly (the `rc=0` echoed after the run was the subshell's); the SUMMARY line equals the frozen target, which the counter documents as exit 0. First (pre-fix) score: killed=12, E2 survived, exit 1.

## Notes
- Fixture refuses root (exit 2), cleans its work dir in `finally`, scenario errors become FAIL cases (no traceback), per-subprocess timeout 60 s, git shim sleeps are 2 s against a 20 s default (10x margin).
- Scratch dir deleted. No tools installed.

## Verdict
PASS: target SUMMARY reached, 13/13 mutants killed, 6/6 equivalent survived, pristine ok.
