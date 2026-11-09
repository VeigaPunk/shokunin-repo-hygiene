# R99ExecC1b — C1 do-nothing controls (frozen-file substitute)

Seat: R99ExecC1b (godspeed). Lane: souji @ c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b.
Scratch: /fast/scratch/hyaku/souji-r99/R99ExecC1b/ (deleted before yield).

## Blocker / deviation: round-99 runner + frozen file not present
At control time (2026-11-09, after L1 freeze window) the assigned inputs were absent from the lane:
- `census/round-99/declared-shapes.py` — NOT PRESENT
- `census/round-99/shapes.tsv` — NOT PRESENT
- `census/round-99/` contained only `c1-survivor-search.py` (the r98 hook, byte-identical to
  `census/round-98/c1-survivor-search.py` per `diff` — "identical", HOOK length 6909).

Controls were therefore run with the closest available equivalent: the r98 runner
`census/round-98/declared-shapes.py` (hard-coded SHAPES table, kinds identical to the frozen shapes
expected in shapes.tsv) + `--scripts census/round-98/shapes` (the 17 shapes) + `--search <hook>`.
The expected verdicts are stated against that substitute below; the L1 re-run against the real
`--freeze census/round-99/shapes.tsv` should reproduce them exactly, since hook HOOK strings are
unchanged and kinds are identical (see declared-shapes.expected).

## Commands run

All from `/home/vgpnk/Projects/shokunin/souji-shokunin`, each with a fresh empty `--work` dir.

1. r95 hook:
```
python3 census/round-98/declared-shapes.py --search census/round-98/controls/c1-r95-search.py --scripts census/round-98/shapes --work /fast/scratch/hyaku/souji-r99/R99ExecC1b/ctrl-r95
```
EXIT=1
```
SHAPE t1-catch-module-falloff.py kind=declared plain=0 hooked=70 MISMATCH
SHAPE t4-reraise-at-module.py kind=declared plain=0 hooked=70 MISMATCH
SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=70 MISMATCH
SHAPES-SUMMARY shapes=17 mismatched=3
```
(q1i present as expected. All other 14 rows ok.)

2. r97 hook:
```
python3 census/round-98/declared-shapes.py --search census/round-98/controls/c1-r97-search.py --scripts census/round-98/shapes --work /fast/scratch/hyaku/souji-r99/R99ExecC1b/ctrl-r97
```
EXIT=1
```
SHAPE q1o-save-then-bare-raise.py kind=crash plain=1 hooked=1 MISMATCH
SHAPE q1q-caught-then-direct.py kind=crash plain=1 hooked=1 MISMATCH
SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=70 MISMATCH
SHAPES-SUMMARY shapes=17 mismatched=3
```
(q1o, q1q present as expected; plus q1i. All other 14 rows ok.)

3. Reference — r98 frozen hook (`census/round-99/c1-survivor-search.py`, hook identical to r98):
```
python3 census/round-98/declared-shapes.py --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work /fast/scratch/hyaku/souji-r99/R99ExecC1b/ctrl-fresh
```
EXIT=0
```
SHAPES-SUMMARY shapes=17 mismatched=0
```
(All 17 rows ok, including t1/t4/q1i hooked=0 and x1/x2/q1o/q1q hooked=70.)

## Verdict
- r95 control: mismatched=3, exit 1. MATCHES expectation (mismatched>=3, q1i among them). NOT falsified.
- r97 control: mismatched=3, exit 1. MATCHES expectation (mismatched>=2, q1o, q1q among them). NOT falsified.
- No control reached mismatched=0 under the substitute frozen table. No FALSIFIED control.
- Reference r98 hook: mismatched=0, exit 0 — the two negative controls are meaningfully weaker than the current hook.

## Findings
1. (blocker for the literal task) `census/round-99/declared-shapes.py` and `census/round-99/shapes.tsv`
   did not exist when this seat ran. Reproducer: the `ls` output above (No such file or directory).
   The L1/integration owner must confirm the frozen-file runner landed, and re-run this seat's two
   controls verbatim with `--freeze census/round-99/shapes.tsv` before claiming C1.
2. Stall-note: both control runs required fresh-empty `--work` dirs; first r97 attempt inherited a
   leftover `ctrl-r97/hook` from an earlier aborted invocation and was re-run after `rm -rf` +
   `mkdir -p` — final reported results are from the clean runs.

## Risk
The substitute runner hard-codes kinds instead of reading shapes.tsv, so a frozen-file-specific
bug (bad parse, wrong column) would not be caught by this seat. Expected kinds match
`declared-shapes.expected`, but the `--freeze` path itself is unexercised here.

Tooling: none installed. Nothing mutated in git.
