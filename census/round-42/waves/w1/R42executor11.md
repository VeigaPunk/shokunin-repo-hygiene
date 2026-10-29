# R42executor11 - C3 candidate fixture (timeout family via PATH shim)

Verdict: TARGET MET in the scratch score. The candidate kills all 13 MUTANTS, kills none of the 6 EQUIV, pristine ok.

## Candidate
- Path: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42executor11/r42-drift-conditions.py
- sha256: 3e5232ed5eb234b78fe1d8b41dbdd38340df372ab54bdc9e98412dc531f4c147
- bytes: 14344 (328 lines), 14 cases (13 mutant-targeting + 1 clean control, all asserting exit code/tokens/--json parse)
- Wall time on the pristine tool: 6.7-7.2 s (largest part: the 5 s shim delay). Whole c3 score run: 44 s.

## Commands run and observed output
1. Pristine run (receipt: .ufo/waves/round-42/w1/R42executor11/pristine-run.txt):
   `python3 -B <candidate> --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r42/R42executor11/w`
   -> 14 x `case-<name>=PASS`, `SUMMARY cases=14 pass=14 fail=0`, exit 0, real 0m6.723s; the --work dir was empty afterwards (every case dir removed).
2. Score (receipt: .ufo/waves/round-42/w1/R42executor11/score-c3.txt):
   `bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor11 tests/fixtures/r42-drift-conditions.py=<candidate>` -> exit 0, wall 44 s:
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

## Design (what each case observes)
- Timeout family via shim (G3 timeout-default-over-one, G4 list-timeout-reported, G5 list-rc-reported): a Python `git` shim is written to `<case dir>/shim/git` under --work, put first on the PATH of that one tool subprocess only, forwards every git call except `worktree list` to the real git (resolved before the shim exists), and is deleted with the case dir (rmtree in `finally`). G3: shim sleeps 5 s, default timeout must wait (rc 0, unreachable=0). G4: shim sleeps 30 s against `--timeout 1` -> `DRIFT\tUNREACHABLE\tr\tUNREACHABLE:list-timeout`, no Traceback. G5: shim exits 3 -> `UNREACHABLE:list-rc=` and unreachable=1. The shim is a Python process (not `sh` + `sleep`) so the tool's kill reaches the sleeper and no orphan holds the pipe. All ratios >= 4x.
- G2: `--timeout 1` accepted on an ABSENT row (no git call, no timing risk), `--timeout 0` refused USAGE.
- B1: FIFO as --record, subprocess timeout 20 s; pristine refuses RECORD-MALFORMED at once, the mutant would block in open().
- E2: row `../root2` refused RECORD-OUTSIDE-ROOT both when root2 is missing and when it is a plain directory. Lesson learned: a first version made root2 a real repository; the gitdir containment (E4's condition) then refused it independently and E2 SURVIVED (score 12/13). The sibling must not be a repository.
- E4: `.git` file in root/s points at a bare repo in the sibling `rootX`.
- H1/H2: argparse "required" refusal naming `--root` / `--record` (H1 runs in an empty cwd so a `.` default cannot pass).
- I1: symlinked child skipped, real unrecorded child `u2` reported. J9: `regs=10` row -> `record=10 live=1`. M1: 100000-byte pre-existing --json target must parse as JSON afterwards.
- D4: record row `REPO\tal\xffpha...`; the --json drift row's `repo` must parse to `"al\ufffdpha"` (backslashreplace would give a literal `al\xffpha`).
- No case reads the tool source/bytes/labels; EQUIV mutants (B3 B4 E5 E7 E9 H4) are unobservable and all survived.

## Compliance and limits
- Did not open the tool source. Read c3-counter.py lines 1-104 (docstring/protocol, MUTANTS and EQUIV tables) because the assignment names the tables as the spec; the L1 may audit that. Behaviour probes of the tool (own throwaway scripts explore.py/ex2.py in scratch) only ran it and printed output.
- Non-root (uid 1000); the fixture also refuses uid 0 (exit 2). No git/jj mutation in the lane; git fixtures were created only under --work with `git init`, config nulled via env.
- Scratch /fast/scratch/hyaku/souji-r42/R42executor11 removed before yield. Nothing installed.
