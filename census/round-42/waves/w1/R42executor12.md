# R42executor12 — C3 candidate fixture (executor)

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor12/r42-drift-conditions.py
sha256 fcb89e398d9683d93e5e5441312d5537248b83d9beff00278195b094bce75c5a, 10477 bytes.
Score receipt (full counter output): .ufo/waves/round-42/w1/R42executor12/score-c3.txt

## Commands run
1. `python3 -B tools/souji-worktree-drift.py --help` (CLI shape only; tool source never opened).
2. Fixture on the pristine tool: `python3 -B <candidate> --tool <lane>/tools/souji-worktree-drift.py --work <scratch>/p`
   -> 14 `case-*=PASS` lines, `SUMMARY cases=14 pass=14 fail=0`, exit 0, wall 10.5 s.
3. `bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor12 tests/fixtures/r42-drift-conditions.py=<candidate>` -> exit 0, wall 57.3 s (19 parallel runs):

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

## Design (14 cases, each its own scenario, tool run as subprocess)
- B1: FIFO record, 15 s timeout, expects exit 2 REFUSAL RECORD-MALFORMED (mutant blocks in open -> timeout -> FAIL).
- E2/E4: row `../root2` and a gitdir in `rootX` sibling -> REFUSAL RECORD-OUTSIDE-ROOT.
- G2/G3: `--timeout 1` accepted; default-timeout case runs the tool with a PATH-shim `git` (python, sleeps 2.5 s then execs the real git) and expects a clean exit 0 (default 20 passes, default 1 yields UNREACHABLE:list-timeout). No wall-clock assertion.
- G4/G5: FIFO `.git/HEAD` with `--timeout 1` -> `UNREACHABLE:list-timeout` row and no traceback; empty `.git` dir -> `UNREACHABLE:list-rc=`.
- H1/H2: omit `--root` (cwd empty dir) / `--record`: exit 2, "required" and the option name in stderr.
- I1: symlinked child to an unrecorded repo: `UNRECORDED u2` reported, `UNRECORDED lnk` absent.
- J9: `regs=10` row -> exit 1 `record=10 live=1`.
- M1: `--json` over a 5000-byte `x` file -> exit 0 and the file parses as JSON with summary and empty drift.
- D4 (new probe): record row name `al\xffpha`, tool run with PYTHONIOENCODING=utf-8; stdout must hold ABSENT, the bytes `al\xef\xbf\xbdpha` (U+FFFD) and no literal `\xff` backslash text.
Hermetic: no network, git config nulled, TMPDIR per scenario, refuses to run as root, exceptions are reported as FAIL (no traceback on stderr). Fixture never opens the tool source, counter, labels or digests.

## Verdict
Target met by this candidate under the seat score: 13/13 killed, 6/6 equivalents survived, pristine ok, fixture wall 10.5 s on the pristine tool. Not the L1's measurement. Scratch dir removed. No tools installed.
