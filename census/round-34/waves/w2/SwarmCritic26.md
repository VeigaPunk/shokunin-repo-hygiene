# SwarmCritic26 — w2 seat findings (AttackC2W2Timeout)

Leaf critic seat, read-only. Full report: `.ufo/waves/round-34/w2/AttackC2W2Timeout.md`.

## Status

W1 finding CONFIRMED with framing corrections. Executed reproduction (frozen bytes, load <3):
full 20-case W2 fixture inside the counter's exact envelope fails exactly `R15CFG-01` with
`exit=124` at the 90 s fixture kill, `SUMMARY total=20 failed=1` — byte-exact match of
`census/round-34/records/feasibility-final.txt:2`. Same run + `--proc /proc`: 20/20 PASS in 68 s.

## Evidence (all executed this seat, 2026-10-27, scratch /fast/scratch/hyaku/souji-r34/AttackC2W2Timeout/)

- Byte-identity: `tools/souji-census.sh` (sha256 `1eab92fb…`) and `tests/fixtures/r15-census-config.py`
  (sha256 `703c05b0…`) identical 9c76c72→adac8bb (HEAD); `c2-counter.py`/`c2-legs.tsv` identical
  2b0171e→60def78. W2 ran byte-identical content in every recorded reading.
- P0: envelope `/proc` probe — namespace pid 3 reads host `pool_workqueue_release` without
  `--proc`, `sleep` with it (`c2-counter.py:122-127` omits `--proc /proc`).
- P1: R15CFG-01, envelope, no `--proc` → FAIL `exit=124`, 90.45 s wall, load 1.55.
- P2: same + `--proc /proc` → PASS, 7.19 s, load 2.68.
- P3: R15CFG-01 uncontained (scrubbed env, TMPDIR scratch) → PASS, 6.53 s, load 4.13.
- P4: full 20 cases, envelope, no `--proc` → R15CFG-01 FAIL `exit=124`, 19/19 others PASS,
  `SUMMARY total=20 failed=1`, rc 1, 225 s, load ~2. == committed W2 line.
- P5: full 20 cases, envelope + `--proc /proc` → 20/20 PASS, rc 0, 68 s, load 2.89.

## Findings

1. Timeout cause = bwrap pid-namespace/procfs boundary (counter envelope omits `--proc /proc`),
   which makes `tools/souji-census.sh:1599-1614` poll a live host kernel thread as its worker.
2. External load FALSIFIED: reproduced at load 1.55–2.89; committed failure at load 6.87;
   recorded passes at load 10.15 (pre-A6) and 49.82 (w1 SwarmExecutor17).
3. Fixture behavior FALSIFIED as defect: fixture passes uncontained and with correct procfs;
   its 90 s kill (`tests/fixtures/r15-census-config.py:848-852`) is correct detection.
4. Frozen leg CAN pass without changing the pinned fixture: P5 passes with a one-flag counter
   repair (`census/round-34/c2-counter.py` is C2-owned per the prereg touched-set; A6 precedent).
5. Intermittency is a pid-collision lottery (host kthreads at 2–8/15/20/25/30/50, absent 9–14);
   deterministic on the current host for case 01 (P1 and P4 within minutes).

## Attack log

A1 envelope repro (P1/P4); A2 load falsification (P1/P4 vs recorded passes); A3 fixture
falsification (P2/P3); A4 repair control (P5); A5 benign-explanation sweep (TMPDIR exonerated,
fixture scratch resolves under sandbox TMPDIR; only `/proc` is broken).

## Deliveries

`AttackC2W2Timeout.md` and this file. Probe logs `run01/full-noproc.log`, `run01/full-proc.log`.
No lane edits, no frozen changes, no clone, scratch <1 MB, no installs.
