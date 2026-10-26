# SwarmCritic09 — C1 item K11 falsification (r33 w1)

## Status
STATUS: PASS — verdict **HOLDS**. K11 (SCORECARD.md:166) reproduces at
2d9bca55a9f042a2c9ed60a797a8069e74c41f46; the frozen predicate is neither laxer nor stricter than the cell's stated
`4/0` outcome; the cell's only other count (`five pinned replay verdicts`) also re-derives. Two residual observations
(out-of-set: a `/var/tmp` pin in the executed fixture; a predicate class limit shared by all 24 C1 items) are
reported, not proposed as amendments (contract: frozen predicate, target, counter, item, leg are the L1's alone).

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r33/AuditK11/` (`mkdir -p`, `TMPDIR=<that>/tmp`). Clone:
`git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c" && git -C "$D/c" remote remove origin`,
`git -C "$D/c" rev-parse --show-toplevel` → `/fast/scratch/hyaku/souji-r33/AuditK11/c`,
`git -C "$D/c" checkout -q 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`, `rev-parse HEAD` → `2d9bca55…f46`,
`git status --porcelain | wc -l` → `0`. No commit, no jj, nothing written in the lane.

Item row (census/round-33/c1-items.tsv:25, read at list-rev):
`K11  166  0  \btotal=4\b && \bfailed=0\b || \b4/4\b  tests/fixtures/r19-carry-wrap.py,tools/souji-landing-gate.py  python3 tests/fixtures/r19-carry-wrap.py`

Cell text, `git show 6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md` line 166 (row under `## Capabilities`,
header at base line 143): capability cell states “strict branch keeps five pinned replay verdicts”; evidence cell states
“`tests/fixtures/r19-carry-wrap.py` 4/0 base-discriminating; `census/round-19/c1-carry.txt`”.

(1) Determinism — cwd = clone root, `python3 -B tests/fixtures/r19-carry-wrap.py`, two runs with fresh per-run
`TMPDIR` + one with `TMPDIR` unset (`env -u TMPDIR`):

```
=== run1 rc=0   === run2 rc=0   === run3(TMPDIR unset) rc=0
CASE	pass	changed/wrap-unmarked	exit=1 ids=['LG-SEAT-UNCARRIED']
CASE	discriminates	base/wrap-unmarked	exit=0 ids=[]
CASE	pass	changed/wrap-marked	exit=0 ids=[]
CASE	pass	base/wrap-marked	exit=0 ids=[]
CASE	pass	changed/wrap-complete	exit=0 ids=[]
CASE	pass	base/wrap-complete	exit=0 ids=[]
CASE	pass	changed/wrap-bullet-wrapped	exit=0 ids=[]
CASE	discriminates	base/wrap-bullet-wrapped	exit=1 ids=['LG-SEAT-UNCARRIED']
SUMMARY total=4 failed=0 base_discriminating=2
sha256 all three = 9e1112c1b70a5f3eaf7606fe6863d4143806fbc5560f92b9713318a2a40bc20b
```
Also: three concurrent runs → `par1 rc=0 par2 rc=0 par3 rc=0`, one unique sha256; run from `/` with the absolute
fixture path → identical output (`SUMMARY total=4 failed=0 base_discriminating=2`, one unique hash vs run1). The run is
cwd-independent and concurrency-safe.

TMPDIR causality caveat (not a determinism defect): the fixture overrides the caller's environment —
`tests/fixtures/r19-carry-wrap.py:41` `TMPDIR="/var/tmp"` and `tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir="/var/tmp")`.
Empirically: `TMPDIR=<fresh>` run left `0` entries in that fresh dir; `/var/tmp/souji-r19-carry-wrap.*` leftovers `0`.
So identical output across the three runs is by construction, not evidence of TMPDIR independence.

(2) Predicate fidelity. Cell: 4/0 = 4 changed cases, 0 failed → `total=4 && failed=0` (exit 0) is the cell's own
count. Checked on the base output: alternative 1 → True; alternative 2 (`\b4/4\b`) → False; `grep -c '4/4'` on the
output → `0` (dead alternative at base). The cell's third token, `base-discriminating`, is not in the predicate but is
pinned by it: `tests/fixtures/r19-carry-wrap.py:229-234` computes `total = passed + failed` then requires
`discriminators == {"wrap-unmarked","wrap-bullet-wrapped"}` else `failed += 1`; `failed=0` therefore forces
`base_discriminating=2`. Not lax, not strict.

(3) Other outcomes in the same cell text. `python3 -B census/round-17/gate-replays.py --scratch <D> --output <D>/replays-at-base.json`
at the clone (base): `r15-landing b410186 15 1 5 True | r13-admitted a31642d 13 0 0 True | r14-landing cc21683 14 0 0 True |
r16-landing 6ff91f5 16 0 0 True | r16-precarry 79bbe7a 16 1 29 True` → five verdicts, all match=True; rc=0. Record-internal
counts of the cited `census/round-19/c1-carry.txt` also re-derive at base: `SELFTEST pass=65 fail=0` (rc=0);
`SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0` (rc=0). The cited record is current, and the base
receipts it names (`gate-r18-strict-fleet.json`, `gate-r18-strict-fleet-confirm.json`, `{"exit": 0, "findings": []}`)
are present at base. No stale out-of-set count found. Attribution note: `WRAP_STRICT_FROM_ROUND = 18`
(tools/souji-landing-gate.py:126), so rounds 13-16 in the five replays exercise the non-strict branch; the cell's phrase
reads “the strict branch left the five verdicts unchanged”, which the replay confirms (5/5 True).

(4) Counter, exactly as assigned:
```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/AuditK11/cnt --only K11
ITEM	K11	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=4 failed=0 base_discriminating=2
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=0
```
(`partial=1` is only the `--only` marker: c1-counter.py:307.)

## Findings

1. **Deterministic, AGREE.** `tests/fixtures/r19-carry-wrap.py` at base is stable across fresh/unset TMPDIR, concurrent
   runs and foreign cwd (sha256 `9e1112c1…` ×3). Location: `tests/fixtures/r19-carry-wrap.py`.
2. **Predicate is a faithful reading of `4/0`**, with `base_discriminating` load-bearing via the vacuity check.
   Location: `tests/fixtures/r19-carry-wrap.py:229-234`.
3. **Second alternative `\b4/4\b` has no producer at base** (0 matches in the collapsed output). It is a
   rendering-equivalent escape (4 of 4 passed = 0 failed) rather than an exploitable lax seam; flagged as an observation
   only — I do not propose touching the frozen predicate.
4. **Residual (out-of-set for C1; relevant to C2 scope): the item's argv pins `/var/tmp`.** `r19-carry-wrap.py:41` sets
   `TMPDIR="/var/tmp"` and its `mkdtemp` uses `dir="/var/tmp"`, so K11 ignores the counter's fresh `--scratch` TMPDIR and
   needs a writable `/var/tmp` (writable here: `test -w /var/tmp` → yes; no residue left). `tests/fixtures/r19-carry-wrap.py`
   appears in no `census/round-33/c2-legs.tsv` leg, so C2 does not cover it. Blast radius is K11 only
   (`awk` over c1-items.tsv: sole row naming `r19-carry-wrap`). It is not stale now, but it is the one way this item can
   flip MISMATCH without any lane byte changing.
5. **Predicate class limit (shared by all 24 items, not K11-specific, not an amendment request):** an output-only
   predicate cannot distinguish a working tool from a stub that prints its expected line. Executed: replacing
   `tests/fixtures/r19-carry-wrap.py` with a 2-line printer (`SUMMARY total=4 failed=0 base_discriminating=2`, exit 0)
   yields rc=0. This is the standard limit of currency counters; the preregistration's controls target junk
   *restatements*, not junk tools.

## Attack log

| # | Attack | Result |
|---|---|---|
| A1 | Determinism: 2 runs fresh TMPDIR + 1 unset, 3 concurrent, foreign cwd | all rc=0, one sha256 — **HOLDS** |
| A2 | Tool regression, under-flagging: swap gate for an always-exit-0 stub (`--tool <stub0.py>`) | rc=1, `SUMMARY total=4 failed=4 base_discriminating=2` — predicate caught it |
| A3 | Tool regression, vacuous self-comparison: patch fixture copy so the base arm runs the current tool | rc=1, `CASE FAIL base-vacuity got=[] want=['wrap-bullet-wrapped','wrap-unmarked']`, `SUMMARY total=4 failed=1 base_discriminating=0` → `failed=0` unreachable; the unchecked `base_discriminating` is pinned |
| A4 | Lax-alternative probe: does `\b4/4\b` match base output? | 0 matches — dead alternative, no lax seam exercised |
| A5 | Fake-provenance probe on the cell's other count (`five pinned replay verdicts`) | gate-replays at base: 5/5 match=True; record-internal counts 65/0 and 400/562/842/0 reproduce — no false provenance |
| A6 | Predicate class limit: replace the fixture with a printing stub | rc=0 — limit confirmed, shared by all items, not a K11 defect |

Verdict: **HOLDS** (not LAX-PREDICATE, not STRICT-PREDICATE, not NONDETERMINISTIC). Smallest safe correction: none
required for C1; if the L1 ever wants the `/var/tmp` seam closed it is a C2-surface leg (Q71 scratch root from TMPDIR)
on `tests/fixtures/r19-carry-wrap.py`, which is outside this seat's authority to add.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic09.md` (this report).

Scratch removed: `rm -rf /fast/scratch/hyaku/souji-r33/AuditK11` (clone `c`, mutation copies `m1`-`m3`, stubs and
outputs all inside that tree; nothing left behind).
Tooling: none installed or upgraded (nothing needed; no pacman transaction attempted).
