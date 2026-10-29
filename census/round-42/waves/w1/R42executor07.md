# R42executor07 — C3 candidate fixture (executor, angle: r41 x01-x19 probes + D4)

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor07/r42-drift-conditions.py
sha256 3a0ea605356ab84cbd80c8c6cc64635cf2fd8e918bcc4a0223b29ed5b786c1ea, 10387 bytes, 15 cases.
Score receipt: .ufo/waves/round-42/w1/R42executor07/score-c3.txt (verbatim copy of the score-candidate.sh output).

## Commands run
1. Pristine run (tool only passed as --tool, work under scratch): `python3 -B <candidate> --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r42/R42executor07/w0`
   -> all 15 `case-*=PASS`, `SUMMARY cases=15 pass=15 fail=0`, exit 0, wall 43.5 s (host heavily loaded; the default-timeout case alone is ~40 s because the pristine tool waits out its 20 s list timeout twice).
2. `bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor07 tests/fixtures/r42-drift-conditions.py=<candidate>` -> exit 0, wall 175.7 s (whole 19-run counter).

## Score output (exit 0)
MUTANT B1 E2 E4 G2 G3 G4 G5 H1 H2 I1 J9 M1 D4: all `candidate=killed prior=-`
EQUIV B3 B4 E5 E7 E9 H4: all `candidate=survived prior=-`
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=15 tool_sha=b2a603cf4247

## Design (behaviour only; fixture never opens the tool source, the counter or any label)
- B1 FIFO record -> rc 2 REFUSAL RECORD-MALFORMED within 20 s (mutant blocks, subprocess timeout = fail).
- E2/E4 sibling dir sharing the root's string prefix (`root2`, `rootX/gd2`) -> RECORD-OUTSIDE-ROOT.
- G2 `--timeout 1` accepted (absent repo -> DRIFT ABSENT rc 1). G3 default timeout: FIFO-HEAD repo, no --timeout, elapsed >= 12 s (pristine waits >= 20 s; lower-bound only, loaded host can only lengthen it) plus list-timeout token. G4 `--timeout 1` FIFO HEAD -> `UNREACHABLE:list-timeout`, no Traceback. G5 empty `.git` dir -> `UNREACHABLE:list-rc=`.
- H1/H2 argparse `are required: ... --root` / `--record`, rc 2 (cwd = empty dir so a defaulted `.` cannot hit anything).
- I1 symlinked child pointing at a git repo not reported while the real unrecorded repo is.
- J9 `regs=10` -> `record=10 live=1`. M1 pre-existing 5000-byte file -> valid JSON (no stale tail).
- D4 (new): record row name holds raw byte 0xFF; a real directory named with the UTF-8 U+FFFD bytes (EF BF BD) is a git repo. Pristine (`replace`) matches it: rc 0, no ABSENT, no `\x` in stdout. `backslashreplace` yields the literal `bad\xffname` -> ABSENT drift rc 1 -> killed.
- Positive controls (clean run + valid JSON, drift exit 1) and root refusal (exit 2, non-root required).

## Residual risks
- G3 asserts a wall-clock lower bound (12 s vs the tool's 20 s wait); it is monotone-safe under load. Pristine total ~43 s on a loaded host, well under 120 s.
- No tools installed/upgraded.

## Verdict
Target met by this candidate in the scratch clone: SUMMARY above, exit 0. Seat score is advice; the L1 measures.
