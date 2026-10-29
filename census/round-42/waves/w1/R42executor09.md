# R42executor09 — C3 candidate (angle: speed)

Candidate: `.ufo/waves/round-42/w1/R42executor09/r42-drift-conditions.py`
sha256 `9d6e816580198c42018641c830d0042dce8049296210cdc0ffaadffc70e74289`, 12042 bytes, mode 0755.
Receipt of the final score: `.ufo/waves/round-42/w1/R42executor09/score-final.txt`.
The fixture never opens the tool source, counter, mutant table or any label; it runs `python3 -B <tool>` per case and asserts exit code / stdout / stderr tokens / the --json file parse. It refuses root (rc 2). Cases run concurrently in a thread pool, each in its own scenario dir under --work.

## Command and result
`bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor09 tests/fixtures/r42-drift-conditions.py=<candidate>` -> exit 0, wall 29.7 s (counter, 19 fixture runs):
```
MUTANT B1 killed / E2 killed / E4 killed / G2 killed / G3 killed / G4 killed / G5 killed / H1 killed / H2 killed / I1 killed / J9 killed / M1 killed / D4 killed
EQUIV B3 survived / B4 survived / E5 survived / E7 survived / E9 survived / H4 survived
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=14 tool_sha=b2a603cf4247
```
(first score, before fixing E2: killed=12, E2 survived — my E2 scenario made the sibling a real git repo, so the gitdir containment check refused it first; making the sibling nonexistent fixed it.)

## Pristine timing (pinned tool)
Whole fixture: 2.9 s wall (single run), 6 repeats + 8 concurrent runs all `cases=14 pass=14 fail=0`. Sequential per case: slow-git default-timeout 2.63 s, hung-git list-timeout 2.05 s, all other 12 cases 0.03-0.04 s.

## Cases -> mutants
- record-fifo-not-waited-on (FIFO record, no writer, 10 s guard; rc 2 + RECORD-MALFORMED) -> B1
- row-prefix-sibling-outside-root (row `../root2`, sibling nonexistent) -> E2
- gitdir-prefix-sibling-outside-root (`.git` file -> bare repo in `rootX`) -> E4
- timeout-one-is-valid (`--timeout 1` runs, ABSENT row, no REFUSAL) -> G2
- default-timeout-lets-slow-git-finish (HEAD is a FIFO; a thread serves the first open after 2.5 s then answers instantly; default timeout must let git finish, rc 0, no UNREACHABLE; no wall clock asserted, 8x margin vs default 20, 2.5x vs mutated 1) -> G3
- hung-git-reported-as-list-timeout (FIFO HEAD never served, `--timeout 1`; rc 1 + `UNREACHABLE:list-timeout`) -> G4
- failing-worktree-list-reported-as-list-rc (empty `.git` dir; `UNREACHABLE:list-rc=`) -> G5
- root-is-required / record-is-required (rc 2, "required" + flag name in stderr) -> H1 / H2
- symlinked-child-is-not-discovered (symlink to a repo is not reported UNRECORDED; real repo is) -> I1
- regs-holds-two-digits (`regs=10`, no refusal, `record=10`) -> J9
- json-overwrite-truncates (20000-byte pre-existing file; result must be one JSON doc and shorter) -> M1
- invalid-utf8-name-becomes-replacement-char (record row `al\xffpha`; directory named with U+FFFD bytes exists; replace handler resolves it: rc 0, no ABSENT; backslashreplace gives ABSENT) -> D4
- baseline-clean-run (positive control, rc 0) — no mutant.
No case touches --json-inside-measured-tree, set_blocking or gitdir/repo measurement distinctions, so the six EQUIV mutants survive.

## Verdict
Target met: `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok`, exit 0. Scratch dir removed before yield. Tools installed: none.
