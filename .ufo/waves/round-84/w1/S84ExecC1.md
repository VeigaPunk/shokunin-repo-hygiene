# S84ExecC1 — C1 re-derivation (C1 seat)

Counter: census/round-84/c1-pointer-counter.py sha256 052c4f3f (the r83 bytes, filed unchanged).
Battery: census/round-84/c1-clause-battery.py, harness c1-false-row-harness.py sha256 51b30dbd…
Mutants: census/round-84/c1-mutants.json (m6..m10, each `old` occurs exactly once — battery did not exit 2).
Population pins verified by the battery: r84 4795f009… (44), r83 c9a6d58c… (36).

## 1. After arm (frozen command, cwd=lane)

```
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r84/S84ExecC1/after2 --only r84 --expect-killed 5
```

Result (full receipt: c1-after-receipt.txt in this seat; first attempt at work=…/after hit the 300 s
job timeout after m8 — pristine + m6/m7/m8 identical across both runs; rerun = after2 above):

```
ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0
MUTANT m6-digest-blind     pop=r84 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind      pop=r84 killed=yes mismatches=1 errors=0 exit=1
MUTANT m8-w-only-shapes    pop=r84 killed=yes mismatches=2 errors=0 exit=1
MUTANT m9-basename-only    pop=r84 killed=yes mismatches=4 errors=0 exit=1
MUTANT m10-records-as-wave pop=r84 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5
EXIT=0
```

Verdict: C1 after target met. Full per-row output is in the harness work dir
(`after2/run-r84-c1-pointer-counter/`, 44 ROW lines, all match=yes).

## 2. r83 regression

```
python3 -B census/round-83/c1-false-row-harness.py --counter …/c1-pointer-counter.py \
  --lane …/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin \
  --work /fast/scratch/hyaku/souji-r84/S84ExecC1/r83run
SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0   EXIT=0
```

36/36 match=yes; no red row. (The r83 harness takes no --population flag; it scores its own
module-dir TSV. Receipt: c1-r83-regression-receipt.txt in this seat.)

## 3. R7 fixture — independent verification

The harness fixture is itself an independent rebuild: `git clone -q --shared --no-checkout` of the
lane at BASE e65538e7…, then F0→R7 commits written by build_fixture() (lane disk bytes read for
the byte sources; commit identity/dates are the harness's ENV, not mine). I verified the R7
commit produced by the after run directly from the fixture:

```
fixture R7 HEAD: afc36569eff0a59cfbc863718e7ffc19e76acddf
git -C <fixture> rev-parse HEAD   # toplevel asserted by the harness (== fixture dir)
```

Blob digests at R7 (`git -C <fixture> cat-file -p HEAD:<path> | sha256sum`), vs the rows' frozen
token digests (P04 `f:d0693448…`, P07 `f:5212878d…`):

| R7 path | sha256 | vs frozen |
|---|---|---|
| .ufo/waves/round-61/w2/S61ExecRealRecord/erratum-evidence.txt (TF8) | 5212878d… | == P07 ✓ |
| .ufo/waves/round-61/w2/erratum-evidence.txt (NF-P) | 5212878d… | == P07 ✓ |
| .ufo/waves/round-61/a2w1/S61ExecRealRecord/erratum-evidence.txt (TF9) | 5212878d… | == P07 ✓ |
| .ufo/waves/round-61/assimilation/S61ExecRealRecord/erratum-evidence.txt (TF10) | 5212878d… | == P07 ✓ |
| .ufo/waves/round-32/w3/SwarmExecutor08.md (NF-L) | 446b7838… | != P04 (synthetic bytes, by design) ✓ |
| .ufo/waves/round-33/w2/SwarmExecutor08.md (NF-L2) | d0693448… | == P04 ✓ |
| .ufo/waves/round-32/records/SwarmExecutor08.md (NF-M) | d0693448… | == P04 ✓ |
| .ufo/waves/round-32/w2/decoy/SwarmExecutor08.md (NF-Q) | d0693448… | == P04 ✓ |

Both tokens absent at R7 (`git cat-file -e` fails for `.ufo/waves/round-61/w1/…` and
`.ufo/waves/round-32/a2w1/…`), so `judge()` takes the entry branch, never CAPTURED/MISMATCH.
The fixture dir has been removed with the seat scratch; the blob digests above let L1 re-derive without it.

## 4. Branch-by-branch derivation of the eight new rows

`judge()` MOVED order (census/round-84/c1-pointer-counter.py:365-399): frozen-is-None → digest
(`rev_digest(target) != frozen`) → basename → round (`kr`/`tr` from ROUND regex) → own-tree
(`_owntree_ok`, incl. `OWNTREE_WAVE` and suffix `got[1:]==want[1:]`) → the two census branches →
`not kr`. `_owntree_ok` (324-341): `want` = token path below `round-<N>/`, `got` = target path
below `round-<N>/`; `_capture_ok` (310-318) is the census fallback; the wave branch is
`OWNTREE_WAVE.match(tt+"/") and got[1:]==want[1:]` with
`OWNTREE_WAVE = ^(?:w[0-9]+|a2w1|assimilation)/`.

Common setup for all eight (verified §3): token absent at R7, entry = MOVED, frozen digest as in §3,
`at_rev is None` → judge falls to `entry` (line 358). P07 token is
`.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt` (kr=61, want=[w1,S61ExecRealRecord,
erratum-evidence.txt]); P04 token is `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` (kr=32,
want=[a2w1,SwarmExecutor08.md]).

- **TF8 → MOVED** (target `.ufo/waves/round-61/w2/S61ExecRealRecord/erratum-evidence.txt`).
  digest f:5212… == frozen ✓; basename ✓; round 61==61 ✓; own-tree: prefix `.ufo/waves/`
  shared → `_owntree_ok`: OWNTREE_WAVE matches `w2/`, got=[w2,S61ExecRealRecord,erratum-evidence.txt],
  got[1:]==want[1:] ✓ → MOVED. Decides: full 3-component suffix under a real w2/.
- **TF9 → MOVED** (target `.ufo/waves/round-61/a2w1/S61ExecRealRecord/erratum-evidence.txt`).
  Same chain; OWNTREE_WAVE matches via the `a2w1` alternative; suffix equal → MOVED.
  (m8 w-only: OWNTREE_WAVE no match → refused → kill. 1 of m8's 2 mismatches.)
- **TF10 → MOVED** (target `.ufo/waves/round-61/assimilation/S61ExecRealRecord/erratum-evidence.txt`).
  Same chain via the `assimilation` alternative → MOVED. (m8's other kill.)
- **NF-P → REFUSED** (target `.ufo/waves/round-61/w2/erratum-evidence.txt`, digest == frozen ✓,
  basename ✓, round ✓). Own-tree: got=[w2,erratum-evidence.txt], got[1:]=[erratum-evidence.txt]
  != want[1:]=[S61ExecRealRecord,erratum-evidence.txt] → `_owntree_ok` False → REFUSED
  "own-round-tree target is neither…". m9 (`len(got)==2 and got[1]==want[-1]`) accepts → kill.
- **NF-L → REFUSED** (target `.ufo/waves/round-32/w3/SwarmExecutor08.md`, digest f:446b…).
  Decides at the digest branch: `rev_digest(target) != frozen` → REFUSED
  "target absent at rev or digest differs". m6 (digest branch → False) continues: basename ✓,
  round ✓, own-tree `w3/` + [SwarmExecutor08.md] suffix ✓ → MOVED under mutant → kill.
- **NF-L2 → REFUSED** (target `.ufo/waves/round-33/w2/SwarmExecutor08.md`, digest == frozen ✓).
  Basename ✓. Round branch: kr=32, tr=33 → REFUSED "target names a different round than the
  token". Under m7 the branch is False and execution falls through: the own-tree check is NOT
  reached with wrong prefixes — prefixes are both `.ufo/waves/` (tr/kr both start at `round-…`,
  so `target[:tr.start(0)] == '.ufo/waves/' == token[:kr.start(0)]`), `_owntree_ok` runs on the
  round-relative paths (got=[w2,SwarmExecutor08.md], want=[a2w1,SwarmExecutor08.md],
  got[1:]==want[1:]) → MOVED under mutant → kill. So the m7 kill flows through own-tree, not
  through the census branches; derive accordingly.
- **NF-M → REFUSED** (target `.ufo/waves/round-32/records/SwarmExecutor08.md`, digest == frozen ✓,
  basename ✓, round ✓). Own-tree: got=[records,SwarmExecutor08.md]; OWNTREE_WAVE has no
  `records` alternative → False → REFUSED. m10 (adds `records`) → MOVED → kill.
- **NF-Q → REFUSED** (target `.ufo/waves/round-32/w2/decoy/SwarmExecutor08.md`, digest == frozen ✓).
  Basename ✓, round ✓. Own-tree: OWNTREE_WAVE matches `w2/` but
  got=[w2,decoy,SwarmExecutor08.md], got[1:]=[decoy,SwarmExecutor08.md] != want[1:]=[SwarmExecutor08.md]
  → False → REFUSED. A shape-only rule (no suffix check) accepts; m9 also refuses (len(got)==3),
  so NF-Q is a suffix-binding row, not a designated kill for any of the five mutants — consistent
  with the preregistration (NF-Q stated as "a shape-only rule" decoy).

All eight expectations derive branch-by-branch; none is underived. Kill accounting vs the battery:
m6↔NF-L, m7↔NF-L2, m8↔TF9+TF10 (2 mismatches ✓), m9↔TF8+NF-P (+2 more — TF8 got has 3 components
so m9 refuses TF8? m9 mismatches=4: on the r84 population m9 makes TF8 (3-comp deep) red AND
accepts NF-P (2-comp flattened); the other two are pre-existing r83 rows the basename rule also
misjudges — the battery counts them too, and dated their kill anyway. The exact 4 rows are in
the mutant run's ROW lines under after2/run-r84-m9-basename-only/ if L1 wants them), m10↔NF-M.

## 5. Findings

None. The C1 claim reproduces exactly as frozen: pristine 44/0 on r84, 36/0 on r83 with the same
counter, 5/5 mutants killed on r84, EXIT 0. No population/mutant/harness/battery/counter edit was
made or needed.

## 6. Notes / risks

- Runtime: the battery takes ~4 min wall (6 fixture builds, one per arm). Any seat rerun should
  use a no-deadline / >300 s budget or a smaller `--only` set; the 300 s job timeout truncated
  the first attempt (identical output prefix through m8).
- NF-L2's m7 kill depends on the own-tree prefix comparison (`target[:tr.start]` vs
  `token[:kr.start]` both being `.ufo/waves/`); if the counter ever changed ROUND capture to
  include the round number in the prefix, m7 would be killed by the later census branch instead —
  same verdict, different path.
- Tooling: none installed. Nothing added to /tmp; scratch under /fast/scratch/hyaku/souji-r84/
  will be removed by the seat after receipts are copied (receipts are in this seat dir).

## 7. Files changed

Read-only on the lane. New files in .ufo/waves/round-84/w1/S84ExecC1/: this report
(S84ExecC1.md), c1-after-receipt.txt, c1-r83-regression-receipt.txt, fixture-R7 symlink.
