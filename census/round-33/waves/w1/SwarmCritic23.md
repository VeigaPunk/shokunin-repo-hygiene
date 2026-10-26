## Status

STATUS: PASS — K25 falsified as far as its frozen predicate allows: the item AGREES at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 and at the tip (fef88f2159f6380a4d1360f73365b3d595973a37), the argv is deterministic (two runs byte-identical to the record), and the frozen predicate is a faithful reading of its evidence cell. Two defects reported with reproduced states: a row-level LAX exposure (the same row claims runtime/version facts no item tests) and a non-reproducible out-of-set residual count.

## Evidence

Measured revision `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (list-rev), base `6017a482e7068d5afb7617640198fbb0fe743357`, tip `fef88f21…`. Measured tree materialized read-only: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive 2d9bca55… | tar -x -C $D/tree2d9`; scratch `D=/fast/scratch/hyaku/souji-r33/AuditK25`, `TMPDIR=$D/runN/tmp` fresh per run, `GIT_CONFIG_NOSYSTEM=1`.

Blob identity (so no drift between base, list-rev, tip):
`git rev-parse 6017a48:tests/fixtures/r32-jj-mtime-clock.sh 6017a48:census/round-32/records/jj-mtime-clock-run.txt` → `cd62dbc3d0dca225cf4b68d0a402e5a8fd9d2d55` / `6de8f4b80b2774215cd7c48360c7a41e7f332512`; identical at `2d9bca55` and at `HEAD`.

(1) Argv, twice, fresh TMPDIR, plus TMPDIR unset (this host: `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, `git version 2.56.0`, bash 5.3.20, python 3.14.8):
```
bash tests/fixtures/r32-jj-mtime-clock.sh   # run1 rc=0, run2 rc=0, 24 stdout lines, 22 RESULT lines
diff out1.txt out2.txt            -> identical
cmp out1.txt census/round-32/records/jj-mtime-clock-run.txt -> identical ("cmp ok")
grep -v '^RESULT ' out1.txt -> jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
                               git-version: git version 2.56.0
env -u TMPDIR bash tests/fixtures/…      -> rc=2, stderr "ERROR: TMPDIR is unset or empty; refusing to run"
TMPDIR= (empty)                          -> rc=2
TMPDIR=<lane root>                       -> rc=2, "is inside the lane; refusing to run"
```
Deterministic: yes, on this host, for both the 22 RESULT lines and the full 24-line replay.

(4) Canonical counter:
```
python3 -B …/census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/AuditK25/cnt --only K25
ITEM	K25	AGREE	original	rc=0 expect_exit=0 predicate holds (RESULT lines 22/22 equal) last=git-version: git version 2.56.0
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46   (rc=0)
```
Same reading at the tip: `rev=fef88f2159f6380a4d1360f73365b3d595973a37`, `AGREE`, rc=0.

## Findings

1. **The frozen predicate is exactly the evidence cell's stated outcome, and it holds.** SCORECARD.md:488 (at 6017a48) evidence cell: "22 `RESULT` lines equal to `census/round-32/records/jj-mtime-clock-run.txt`". The record carries 22 `RESULT` lines (`grep -c '^RESULT '`) and the run reproduces them in order, rc 0; the counter's `RESULTS:…:22` also refuses a record whose RESULT count differs from 22. Not stricter, not laxer than the cell as written. Location: `census/round-33/c1-items.tsv:39`, `SCORECARD.md:488`.

2. **Row-level LAX exposure (ATTACK, reproduced): the same row claims runtime facts no item tests.** SCORECARD.md:488 description cell: "the record replays byte-identically and a PATH shim proves the binaries ran" and "real jj 0.45.1 + git 2.56.0". Neither reaches the predicate (`RESULTS:` compares `RESULT` lines only). Executed counterexamples: (a) version drift — fixture run with a PATH shim whose `jj --version` prints `jj 0.46.0-0123456789abcdef0123456789abcdef01234567` and `git --version` prints `git version 2.55.0`: rc=0, RESULT lines identical to the record, full output differs only in the two version lines; feeding that stdout to the counter's own `frozen_pred` returns `(True, 'predicate holds (RESULT lines 22/22 equal)')`, yet the row's version clause and "byte-identically" are false. (b) non-measuring tool — fixture replaced by `cat census/round-32/records/jj-mtime-clock-run.txt; exit 0` (no `jj`, `git` or `touch` invoked), committed in a scratch clone as `c205fae5db79ffe9ea4d0513faa20d1637125ae8`; counter prints `ITEM K25 AGREE … rc=0`. That is the exact attack `census/round-32/c3-counter-v2.py:4` says amendment A1 was written for ("a fixture that issues the shimmed calls, ignores their results and prints RESULT lines from constants"), so the lane has already paid for this class; the C1 item inherits the weak half. Impacted axis: calibration (7), label C1-CURRENCY. Location: `SCORECARD.md:488`; `census/round-33/c1-items.tsv:39`; `census/round-32/c3-counter-v2.py:4`.

3. **Out-of-set residual, not stale but not reproducible: the shim call counts.** The same cell points at `census/round-32/records/c3-after-v2.txt`, whose L12 line reads `L12 PASS rc=0 results_equal=True jj_calls=32 git_calls=366 touch_calls=16 missing=[]`. Re-deriving the shim run (log-and-forward `jj`/`git`/`touch`, same fixture bytes) gave `jj=32 git=367 touch=16`, then `32/366/16`, then `32/370/16`, with the 22 RESULT lines identical in all three; the variation sits in `verify-pack` calls (7, 6, 10 pack indexes scanned by `where()`). So 366 is one draw, not a value; an exact-count predicate on this surface would be flaky. The row itself states no counts, so this is a receipt residue, not a stale row claim. Location: `census/round-32/records/c3-after-v2.txt:13`; `tests/fixtures/r32-jj-mtime-clock.sh:112-118`.

4. **Residuals re-derived and current (not stale):** "real jj 0.45.1 + git 2.56.0" holds on this host (run1 lines 1-2; exact jj build hash matches the record). "the record replays byte-identically" holds: three independent runs are byte-identical to the committed record (`cmp` ok on out1/out5/out6/out7). Arms/where claims hold: record has 5 arms (recent, old, mixed, never, nocruft) and `where` ∈ {loose, cruft, absent}. No stale residual found.

5. **Refusal guards keep their refusals (Q74):** TMPDIR unset, empty, and inside the lane each exit 2 with the fixture's own message; the frozen argv's `TMPDIR={SCRATCH}` is therefore load-bearing and the counter creates that dir. No defect.

6. **The argv is a pure function of the environment, not of lane state:** the fixture writes only under `$TMPDIR`, refuses the lane and fleet roots both before and after `mktemp`, and its output contains no run-varying token (verified: two runs' 24 lines byte-identical). No NONDETERMINISTIC finding for the item's predicate on this host.

## Attack log

Target: C1 item K25 (`census/round-33/c1-items.tsv:39`, SCORECARD.md:488 at 6017a48).

- (1) Determinism: rc 0 twice, 22 RESULT lines, byte-identical full replay; `TMPDIR` unset → rc 2. Deterministic.
- (2) Predicate fidelity: the frozen predicate is the evidence cell's stated outcome exactly, and nothing more. Faithful. **LAX against the row's own description cell** — two executed counterexamples (version drift; constants-echo fixture), both still `AGREE`. Sustained as a row-level attack, not an item-predicate mismatch.
- (3) Other stated outcomes in the same row: 22 RESULT lines (covered and true), "byte-identically" (true, proven by `cmp`), versions (true today), PATH-shim proof (no reproducible count; 366 is one sample of 366–370), 5 arms / 3 `where` values (true).
- (4) Canonical counter: `SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55…`, rc 0.

**Verdict: HOLDS** (item faithful to its evidence cell at 2d9bca55 and at the tip, deterministic, AGREE reproduced). **ATTACK sustained at row level: LAX** — the row's version/byte-identity/PATH-shim clauses are unverified by the frozen predicate and are demonstrably false-able while the item still AGREEs. Not NONDETERMINISTIC, not STRICT-PREDICATE.

Smallest safe correction (L1's call, not mine to make; no file edited):
- K25 needs **no restatement** — it already AGREEs at base, at 2d9bca55 and at the tip; an appended row for K25 would be a needless BAD-CAUSE risk (no cause commit can show the original statement failing).
- If the row's version clause is to be covered, the only stricter-only move is an amendment adding the two conjuncts K24 already carries (`jj-version: jj 0\.45\.1` && `git-version: git version 2\.56\.0`) to K25's predicate, logged in `census/round-33/records/amendments.txt` before the first seat scores. Verified inert here: every run of this fixture on this host prints those two exact lines, so the item would still AGREE. Otherwise record the limit in the C1 landing receipt.
- Never make the shim call counts (32/366/16) a predicate: they vary 366–370 across identical RESULT runs.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic23.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK25` removed after copying these receipts; no tree left behind. No lane file, index, jj state or process touched; the only commit made was `c205fae5…` inside the scratch clone (throwaway identity `scratch <scratch@invalid>`). No tools installed or upgraded.
