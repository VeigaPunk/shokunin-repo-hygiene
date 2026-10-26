# SwarmCritic17 — falsify C1 item K19 (SCORECARD.md:313)

STATUS: PASS — K19's frozen outcome reproduces deterministically in 3/3 runs at
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; the frozen predicate is the cell's stated outcome
verbatim; the two other counts in the same cell re-derive fresh. One reproduced predicate laxity
(ATTACK A1) is recorded; it does not move the counter's AGREE.

VERDICT: **HOLDS** (currency). Laxity confined to the cell's prose clause "read only committed
bytes" (ATTACK A1) and to byte-exactness (A2); the enumerated outcome is earned and every
plausible regression of the tool's four stated detection arms is caught (M1/M2/M3/M6, below).

## Evidence

Base `6017a482e7068d5afb7617640198fbb0fe743357`; list-rev `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`;
lane HEAD at read time `fef88f2159f6380a4d1360f73365b3d595973a37`. Scratch clone
`/fast/scratch/hyaku/souji-r33/AuditK19/c` (`--no-local`, origin removed, `rev-parse --show-toplevel`
printed the clone, detached at the list-rev).

Row bytes are identical at base, list-rev and tip (`sed -n 313p` sha256 prefix `f2b5a6d1ad02fc58`),
and `grep -n 'Round 33 capability currency'` is absent at the tip, so K19 is measured on its
original row (counter agrees: `restated=0`).

### (1) Determinism of the frozen argv

| run | TMPDIR | rc | stdout |
|---|---|---|---|
| 1 | `/fast/scratch/hyaku/souji-r33/AuditK19/tmp/run1` | 0 | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` |
| 2 | `.../AuditK19/tmp/run2` | 0 | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` |
| 3 | unset (`env -u TMPDIR`) | 0 | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` |

`cmp` run1/run2/run3 stdout: byte-identical; stderr empty in all three. **Deterministic.**

TMPDIR is not an independent variable for this fixture: it hardcodes its scratch root —
`tests/fixtures/r29-registry-agreement.py:18` `BASE = '/var/tmp/souji-r29-c1-fixture'` — and
:181-182 `os.makedirs(BASE, exist_ok=True)` + `tempfile.mkdtemp(prefix='c1.', dir=BASE)`.
A grep for `tempfile|TMPDIR|getenv|environ|BASE` on the fixture returns only `BASE` (:18), the
`cwd=BASE` of the two tool runs (:142, :163), :181-182 and the `K2BASE` case bodies: the fixture
never reads `TMPDIR`, so the counter's per-item `TMPDIR` (`census/round-33/c1-counter.py:164`) is
bypassed for K19.

### (4) Frozen counter for K19

```
$ python3 -B census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/AuditK19/cnt --only K19
ITEM	K19	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=20 pass=20 control=FALSE-GREEN-REJECTED
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
COUNTER rc=0
```

The counter's clone is `--no-checkout` then `checkout -qf --detach rev` (c1-counter.py:156-160),
i.e. a clean worktree at `rev` — which is why A1 is invisible to it as well as to a human run.

### Out-of-set counts in the same cell, re-derived

Cell text at 313 (fields 3-5): `python3 -B tests/fixtures/r29-registry-agreement.py`
`cases=20 pass=20 control=FALSE-GREEN-REJECTED` `(v1 tool 8/20); base mismatches=10 -> 0`.

- `(v1 tool 8/20)`: v1 bytes = blob `b8cb4b31ce80e2e3314b88e85d40ea9873180804:tools/souji-registry-agreement.py`,
  sha256 `51131fe74faa95a1488ad6957d90b272a22c52171c257d9b97bb27c305b09801` (matches
  `census/round-29/records/frozen-digests.txt:1`). `... --tool <v1 blob> --no-control` →
  `cases=20 pass=8 control=TOLERATED`, rc 1, 12 FAIL lines. **8/20 reproduces.**
- `base mismatches=10 -> 0`: `tools/souji-registry-agreement.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
  --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` → `SUMMARY k1=6 k2=4 mismatches=10`, rc 1;
  at `--rev 1dc678500c92164b0b2bea82b934dd03d1dfbf38` → `SUMMARY k1=0 k2=0 mismatches=0`, rc 0;
  still `mismatches=0` at `--rev 2d9bca5…` and at `--rev fef88f2…` with the frozen stale list.
  **No stale out-of-set count in this cell.**

## Findings

Items 1-3 answer question (2); items 4-5 answer question (3) and the hygiene check.

1. **Predicate faithfulness (not stricter).** The frozen predicate string is exactly the cell's
   stated outcome, matched whitespace-collapsed; it adds nothing the cell does not state. Exit 0 is
   implied by the fixture's own contract (`tests/fixtures/r29-registry-agreement.py:197-198`:
   `return 0 if passed == len(CASES) and ok else 1`). Location: `census/round-33/c1-items.tsv` K19;
   `SCORECARD.md:313`.

2. **Predicate tightness against tool regressions.** Each single-arm regression of the four
   capabilities the cell states is caught (mutants run against the clone's 20-case fixture):
   M1 delete `cited-not-in-used-by` → `cases=20 pass=18`, rc 1; M2 drop the derivation-source
   requirement in K2 → `pass=19`, rc 1 (`FAIL k2-facts-without-source-path`); M3 drop the
   used-by citation test → `pass=19`, rc 1 (`FAIL used-by-no-cite`); M6 reads the working tree
   unconditionally → `pass=19`, rc 1 (`FAIL row-deleted`). Location: `tools/souji-registry-agreement.py:64-93`.

3. **The control conjunct is load-bearing, not cosmetic.** A fixture whose `check()` always returns
   True prints `cases=20 pass=20 control=TOLERATED` and exits 1, so the `control=FALSE-GREEN-REJECTED`
   conjunct cannot be satisfied by a gutted case oracle (mutant M4). Independently, the always-zero
   emitter run through the fixture gives `cases=20 pass=3`, rc 1, 17 FAIL lines — the control name
   is earned, not asserted. Location: `tests/fixtures/r29-registry-agreement.py:161-172`.

4. **Scratch-discipline residual (out of set, for the L1).** The fixture pins its scratch to
   `/var/tmp` and never consults TMPDIR, the same defect class as C2 legs O1-O3, but it is not one
   of C2's five legs. After three runs `/var/tmp/souji-r29-c1-fixture` exists and is empty: the
   parent is created at :181 and never removed (`rmtree` covers only `work`). On a host with a
   read-only `/var/tmp` K19 would return rc 2 (COULD-NOT-EVALUATE → MISMATCH under the C1 kill
   rule). Location: `tests/fixtures/r29-registry-agreement.py:18,181-182`.

5. **The row is true for the tool at HEAD.** Every tree read goes through `git cat-file blob
   rev:path` (`tools/souji-registry-agreement.py:36-38`, also :94-96 `blobbytes`), so the cell's
   "committed bytes" clause is a true statement about the tool; the fixture simply does not prove
   it (A1).

## Attack log

**A1 — the 20-case set cannot separate committed-bytes reads from worktree reads.** Reproduced:
a tool whose `blob()` reads the worktree when `rev` equals the repo's `HEAD` prints
`cases=20 pass=20 control=FALSE-GREEN-REJECTED`, rc 0 — the exact frozen tuple, from a tool that
violates the cell's first clause ("read only committed bytes and report every SOURCES", 9 words,
copied from `SCORECARD.md:313` at the list-rev). Why the fixture misses it: every case measures a
revision whose worktree is clean (the `rows2`/`files2` stages are committed with `git add -A`
before measurement, :128 and :137), and the counter's clone is likewise checked out at `rev` with no
dirty path. Impacted axes: calibration only; kills nothing (AGREE stands, `mismatches=0`).
Smallest safe correction, fixture-only and predicate-preserving: add one case that writes an
uncommitted edit to a measured path after the commit and requires the output to stay unchanged —
that case turns A1 red without touching the frozen predicate, predates any use if added by the L1
in its own commit. Not proposed as an amendment; the L1 owns that call.

**A2 — byte-exactness is not exercised.** Reproduced: a tool that compares the append-only
prefix as `str` decoded with `errors='replace'` instead of bytes prints the exact frozen tuple,
`cases=20 pass=20 control=FALSE-GREEN-REJECTED`, rc 0 (all 20 fixture bodies are ASCII literals, so
text and bytes coincide). The tool's own contract says "append-only by bytes"
(`tools/souji-registry-agreement.py:16`). Same class as A1; smallest safe correction: one K2
case carrying a non-UTF-8 byte in the appended region.

**A3 — recorded as a non-defect.** M4 shows a gutted oracle cannot pass the predicate; the control
conjunct supplies real teeth. No change proposed.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic17.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r33/AuditK19` (clone, mutants, counter clone) removed after the
receipts above were copied. No lane mutation, no commit, no `rm` outside scratch. No package was
installed or upgraded: `git`, `python3`, `sha256sum`, `cmp` sufficed.
