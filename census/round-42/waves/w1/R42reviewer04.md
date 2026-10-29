# R42reviewer04 — C3 group B mutant re-derivation (round 42, wave 1)

Seat: R42reviewer04 (reviewer). Scope: H1 H2 I1 J9 M1 D4 (non-equivalent) and B3 B4 E5 E7 E9 H4 (EQUIV),
from `census/round-42/c3-counter.py` MUTANTS and EQUIV. Pristine tool `tools/souji-worktree-drift.py`
at freeze commit afe17f416eec04dcf3f480b580a8f928de61d19d, sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6
(matches PRISTINE_SHA256 and `git show afe17f4:tools/souji-worktree-drift.py`). Frozen files were not edited.
B1 is not in the assigned group B list but sits in the same MUTANTS table; it was also probed and checked against the PRIOR fixtures, and §1 covers it.

Seat directory: `.ufo/waves/round-42/w1/R42reviewer04/`
- `mut-<ID>.py` — 13 mutants, each `source.replace(old, new)` applied once to a copy of the pristine tool
  (generator run: `python3 -B gen_mutants.py`, not kept; every `old` asserted to occur exactly once, all printed
  `occurrences=1 differs=True`; each file differs from pristine by exactly the one line shown in the diff).
- `pristine-tool.py` — byte copy of the pristine tool used by the probes (sha256 b2a603cf…3e34dc6).
- `probe_lib.py`, `probe-<ID>.py` (7 non-equivalent probes), `probes-run.txt` (their output).
- `equiv_scan.py`, `equiv-scan.txt` (6 EQUIV mutants × 29 scenarios), `equiv-control.txt` (positive controls).
- `prior_survey.py`, `prior-survey.txt` (each PRIOR fixture × pristine and × the 7 non-equivalent mutants).
- `survey-c3-stub-allpass.out/.err` (counter survey path, run through `score-candidate.sh`).

## 1. Non-equivalent mutants (probe = pristine vs mutant, same scenario)

| mutant | observable pristine vs mutant? | probe path | notes |
|---|---|---|---|
| B1 | YES. pristine rc=2 `REFUSAL RECORD-MALFORMED: record.fifo is not a regular file` in 0.03 s; mutant hangs (killed at 8 s timeout, `hang=True`) | `.ufo/waves/round-42/w1/R42reviewer04/probe-B1.py` | FIFO record with no writer. Blocking open on the mutant. |
| H1 | YES. pristine rc=2 argparse `the following arguments are required: --root`; mutant rc=0 and a `SUMMARY … drift_rows=0` line | `probe-H1.py` | run from inside a fleet with no `--root`. |
| H2 | YES. pristine rc=2 argparse `required: --record`; mutant rc=1 with `TypeError: open: path should be string, bytes or os.PathLike object, not NoneType` traceback | `probe-H2.py` | traceback is a crash, not a refusal. |
| I1 | YES. pristine rc=0, SUMMARY only, no UNRECORDED row; mutant rc=1 `DRIFT UNRECORDED link live regs=1 prunable=0` | `probe-I1.py` | fleet/link is a symlink to a repo outside root. |
| J9 | YES. pristine rc=1 `DRIFT REGS-CHANGED alpha record=10 live=2`; mutant rc=2 `REFUSAL RECORD-MALFORMED: line 1 does not match the census schema` | `probe-J9.py` | record row `regs=10`, TOTAL consistent. |
| M1 | YES (file bytes). `--json` target pre-filled with 4096 bytes: pristine file 230 bytes, `json.loads` OK; mutant file 4043 bytes, `json.loads` fails, tail `xxxxxxxxxxxx` | `probe-M1.py` | same rc=0 and stdout on both. |
| D4 | YES (stdout bytes). record name `alp\xffha`: pristine prints `alp\ufffdha` (EF BF BD); mutant prints literal `alp\xffha` | `probe-D4.py` | both rc=1, `DRIFT ABSENT`. |

Prior fixtures (eight PRIOR files frozen at afe17f4, run directly through `prior_survey.py`): every one of the
8 × 8 cells (pristine + the 7 mutants) is `rc=0 … fail=0`, `kill=False` (see `prior-survey.txt`). Every
non-equivalent group-B mutant survives all eight PRIOR fixtures. Matches the counter's survey (`prior=-` for
all 13 MUTANT rows and all EQUIV rows) in `survey-c3-stub-allpass.out`.

## 2. EQUIV mutants (search for any observable difference)

Harness: `equiv_scan.py`. Each of 29 scenarios builds two identical fresh trees (one per tool), runs the tool,
and compares rc, hang flag, stdout, stderr (base paths normalised) and a snapshot of the whole tree after the
run (non-.git file contents by sha256; .git by name only; `.git/objects` excluded because commit hashes embed
the commit time). Scenarios cover: plain runs; drift; `--json` inside root, inside a measured repo, inside its
gitdir, inside a linked worktree's gitdir, equal to the record, hardlinked to the record, hardlinked outside,
`""`, a sibling sharing a name prefix, root itself a repo, symlink in root to outside and to inside a repo,
root directory as target, a missing parent, a FIFO target, a pre-filled longer target (2 scenarios), record row
outside root, gitdir outside root, a 2000-row record, a directory as record, a symlinked record, an empty
record, non-UTF-8 and multibyte names, a repo outside root as target, and `--timeout 1`. rc distribution across
the 29 scenarios: {0: 10, 1: 4, 2: 15}.

| mutant | observable? | probe path | notes |
|---|---|---|---|
| B3 | NO difference found in 29 scenarios | `equiv_scan.py` (`equiv-scan.txt`) | O_NONBLOCK has no effect on read() of a regular file on Linux; the fstat S_ISREG check runs before the removed line in both. |
| B4 | NO difference found in 29 scenarios | `equiv_scan.py` | same argument for write() on the regular fd returned by open_nofollow. |
| E5 | NO difference found in 29 scenarios | `equiv_scan.py` | every entry of `measured` is root_real or a path already checked inside root_real; the first iteration (`measured[0] == root_real`) produces the same refusal text as the pristine loop, so messages are identical too. |
| E7 | NO difference found in 29 scenarios | `equiv_scan.py` | gitdir is refused with RECORD-OUTSIDE-ROOT unless inside root_real; the root_real entry still guards the same JSON targets. |
| E9 | NO difference found in 29 scenarios | `equiv_scan.py` | `resolved` is refused unless inside root_real; same subsumption as E7. |
| H4 | NO difference found in 29 scenarios | `equiv_scan.py`; `--help` identical (see §3) | `args.json` is read only at `if args.json:` and `os.path.realpath(os.path.abspath(args.json))`; `""` is falsy like None and `json_target` stays None. |

Positive controls (same harness, mutants known to be observable, `equiv-control.txt`):
- D4 detected in 1 of 29 scenarios (S25, stdout bytes differ).
- M1 detected in 2 of 29 scenarios (S28, S29, file tree differs).
So the harness does detect byte-level and stdout differences; the EQUIV null result is not from a harness that
cannot see the effect in question.

**No EQUIV mutant was found observable.** The equivalence guard holds for B3 B4 E5 E7 E9 H4 under the 29
scenarios. Timing was not benchmarked separately; for B3/B4 the only timing-relevant change is the O_NONBLOCK
flag on a regular file, which the kernel ignores for read/write on regular files.

## 3. Commands run and their observed output

```
# pristine sha
$ sha256sum tools/souji-worktree-drift.py  ->  b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6
$ git -C .../souji-shokunin cat-file -p HEAD:tools/souji-worktree-drift.py | sha256sum  ->  b2a603cf…3e34dc6  -
$ git -C .../souji-shokunin rev-parse HEAD  ->  afe17f416eec04dcf3f480b580a8f928de61d19d

# mutant generation (str.replace once; asserts occurrences==1)
$ python3 -B gen_mutants.py
B1 occurrences=1 mut_sha=13a5d1189f81 differs=True
H1 occurrences=1 mut_sha=a8e0e997ab67 differs=True
H2 occurrences=1 mut_sha=a5fab3fb3009 differs=True
I1 occurrences=1 mut_sha=3cda5726acd9 differs=True
J9 occurrences=1 mut_sha=ee30b05f2a4e differs=True
M1 occurrences=1 mut_sha=6a79956cd3ea differs=True
D4 occurrences=1 mut_sha=bcb94bcd0b89 differs=True
B3 occurrences=1 mut_sha=37c4bec93d9b differs=True
B4 occurrences=1 mut_sha=9425d6ab04a4 differs=True
E5 occurrences=1 mut_sha=f0e992791063 differs=True
E7 occurrences=1 mut_sha=9a8a7980ace0 differs=True
E9 occurrences=1 mut_sha=1267347659f0 differs=True
H4 occurrences=1 mut_sha=8b327d8459ee differs=True

# counter survey path (required command)
$ bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42reviewer04 \
    tests/fixtures/r42-drift-conditions.py=census/round-42/controls/c3-stub-allpass.py
MUTANT B1 candidate=SURVIVED prior=-      (also E2 E4 G2 G3 G4 G5 H1 H2 I1 J9 M1 D4 SURVIVED prior=-)
EQUIV B3 candidate=survived prior=-      (also B4 E5 E7 E9 H4 survived prior=-)
SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
rc=1
# (stub fixture is not a real candidate: killed=0 is expected for the stub; the prior= column is the used signal)

# non-equivalent probes
$ python3 -B probe-<ID>.py   (ID in B1 H1 H2 I1 J9 M1 D4)  -> probes-run.txt
VERDICT B1..D4: OBSERVABLE (pristine != mutant) for all seven; exit 0 each

# direct prior-fixture check
$ python3 -B prior_survey.py   -> prior-survey.txt : 64 rows, all rc=0 fail=0 kill=False

# EQUIV scan and controls
$ python3 -B equiv_scan.py B3 B4 E5 E7 E9 H4   -> equiv-scan.txt
EQUIV B3/B4/E5/E7/E9/H4: no difference found in 29 scenarios
$ python3 -B equiv_scan.py D4 M1               -> equiv-control.txt
EQUIV D4: OBSERVABLE DIFFERENCE in 1 of 29 scenarios (S25); EQUIV M1: OBSERVABLE DIFFERENCE in 2 of 29 (S28, S29)

# --help parity for the EQUIV mutants (each copied to tool.py so argparse prog name is equal)
pristine --help rc=0 lines=10; B3 B4 E5 E7 E9 H4: rc=0 identical=True
```

Harness development notes (for the L1, honest record): the first equivalence run reported differences on every
scenario. That was the harness, not the tool: commit object file names embed the commit time, so the tree
snapshot now excludes `.git/objects`. A second harness error (scenarios writing `--json` into a non-existent
`out/` directory) produced a false rc=2 on many rows; fixed by creating `out/`. S25 first held valid UTF-8
(a literal `\xff` escape was never a raw byte); fixed to a raw 0xFF byte. Only the final run is the receipt
(`equiv-scan.txt`, `probes-run.txt`, `prior-survey.txt`). The first probe scripts were written to the wrong
directory and moved; no lane path was written.

## 4. Verdict

- Non-equivalent group-B mutants (H1 H2 I1 J9 M1 D4, and B1 in the population): **all observable** pristine vs
  mutant by a concrete probe, and **none is killed by any of the eight PRIOR fixtures** (prior=- in the counter,
  confirmed per fixture in `prior-survey.txt`). Consistent with C3's population claim for these seven.
- EQUIV mutants (B3 B4 E5 E7 E9 H4): **no observable difference** in 29 scenarios covering exit code, stdout,
  stderr, file bytes and whole-tree snapshot; plus static arguments in §2. **No EQUIV mutant was found
  observable**, so the equivalence guard of C3 is not broken by this scan.
- Not evaluated here: whether the candidate fixture `tests/fixtures/r42-drift-conditions.py` kills the
  non-equivalent mutants (it is not at the freeze tip; only the stub control was run through the counter).

## 5. Residual / gaps

- Timing was not measured; the B3/B4 timing argument is kernel-semantic and was not benchmarked.
- EQUIV scan covers 29 hand-chosen scenarios on Linux (python 3.14.8, git 2.56.0); it is not exhaustive.
- The positive controls prove the harness can see byte and stdout differences; they do not prove it can see
  timing differences.
- Cosmetic: `probe_lib.py` defines `SEAT` twice with the same value (harmless).

## 6. Tooling and hygiene

- Tools installed or upgraded: none. Python 3.14.8 and git 2.56.0 were used as present.
- Lane writes: none. The lane was read only (`git show`, `git rev-parse`, `cat-file`, and the counter's own
  `git clone --shared` in scratch via `score-candidate.sh`). No git mutation, no commit, no push.
- Scratch `/fast/scratch/hyaku/souji-r42/R42reviewer04` was removed after the receipts were copied into the seat
  directory. The probes and `equiv_scan.py` recreate scratch paths on demand (`fresh()` uses `makedirs`).
- No subagents spawned (leaf member).
