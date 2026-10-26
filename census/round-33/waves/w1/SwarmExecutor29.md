# SwarmExecutor29 — r33 w1, C2 leg O2 (tests/fixtures/r15-census-config.py scratch root)

## Status
STATUS: PASS — repair patch delivered and executed: O2 PASS at repair commit 5bfcc3308b4506976c59b2483402cd9e73b26780 (counter rc=0), O2 FAIL at red-before 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; G4 red is the declared frozen-pin step owned by the L1's regenerate.py re-pin.

## Evidence

Patch applies to 2d9bca5 (`git apply --check` OK in a second scratch clone); post-apply blob sha256 `62e310ca…a81d27` equals the repair commit's blob; base blob `790024c9…2ecb82e`. Diff: 1 file, 5 hunks, 7+/7-. Delivered patch sha256 `bcb3aa85…6559f524` (identical to `git -C <clone> diff 2d9bca5…`).

Candidate `--only O2,G6`:
```
LEG	O2	sandbox-nt	PASS	base=rc0:SUMMARY total=20 failed=0	sbox=rc0:SUMMARY total=20 failed=0
LEG	G6	guard	PASS	base=rc0:SUMMARY total=29 failed=0	rev=rc0:SUMMARY total=29 failed=0
SUMMARY legs=2 pass=1 fail=0 harm=0 partial=1 rev=5bfcc3308b4506976c59b2483402cd9e73b26780
candidate rc=0
```
Red-before (`--rev 2d9bca5`):
```
LEG	O2	sandbox-nt	FAIL	base=rc0:SUMMARY total=20 failed=0	sbox=rc2:r15-census-config: cannot create /var/tmp fixture: [Errno 30] Read-only file system: '<TMP>'
LEG	G6	guard	PASS	base=rc0:SUMMARY total=29 failed=0	rev=rc0:SUMMARY total=29 failed=0
SUMMARY legs=2 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
```
Q73 frozen guards at candidate (`--only G4,G5`, rc=1):
```
LEG	G4	guard	FAIL	base=rc0:frozen_files: 3	rev=rc2:finding snapshot_tampered: 'tests/fixtures/r15-census-config.py': pinned=<HEX> observed=<HEX>
LEG	G5	guard	PASS	base=rc0:fixture: 8/8 checks passed	rev=rc0:fixture: 8/8 checks passed
```
Q73 consumer set: `git -C <clone> grep -l tests/fixtures/r15-census-config.py -- tests/fixtures census` = 135 paths at both 2d9bca5 and 5bfcc33, `diff` empty. Registered gate row SKILL.md:211 command at base 6017a48 `rc=0`, last line `SUMMARY	total=20	failed=0`; at 5bfcc33 `rc=0`, same last line. G6 guard `SUMMARY total=29 failed=0` both sides.

Q74 refusals, base vs candidate identical (uid 1000): `--tool /nonexistent/tool.sh` rc2 `tool not readable: /nonexistent/tool.sh`; `--case R15CFG-99` rc2 `unknown case id: R15CFG-99`; `--bogus-flag` rc2 argparse usage. Root-user refusal not exercisable at uid 1000 (untested).

Q71: `TMPDIR=<scratch>/probe/` (trailing slash) → `tempfile.gettempdir()` = `/fast/scratch/hyaku/souji-r33/FixO2/run-tmp/probe`, mkdtemp child inside it. Candidate runs left no `/var/tmp/r15-census-config.*`; base-side runs inside the counter create and remove theirs (two live dirs at 14:51/14:52 gone afterwards).

All runs in `/fast/scratch/hyaku/souji-r33/FixO2/` clones with `TMPDIR` under that tree; scratch tree removed after receipts were copied.

## Findings
1. Repair, tests/fixtures/r15-census-config.py: child env `TMPDIR` (line 828) → `tempfile.gettempdir()`; `mkdtemp` drops `dir="/var/tmp"` (line 1545); die message names the resolved root (line 1547); docstring claims made true at lines 74-76 and 106. No `/var/tmp` literal remains (`grep -n 'var/tmp'` rc1). Nothing else changed (Q71).
2. Leg differential, census/round-33/c2-counter.py O2 (`sandbox-nt`): FAIL at 2d9bca5 (`cannot create /var/tmp fixture` under read-only `/var/tmp`), PASS at 5bfcc33 with the base run's exact exit and SUMMARY `total=20 failed=0` — the fixture now creates its world under the caller's `TMPDIR`, which the sandbox leaves writable.
3. Q73 pin: `tests/fixtures/r15-preservation-frozen/record.json` pins the old fixture digest, so G4 reads `snapshot_tampered` at the repair commit (harm=1, declared by the preregistration). The re-pin must be `tests/fixtures/r15-preservation-frozen/regenerate.py --rev <rev>` as its own commit by the L1; G5 green, consumer set unchanged.
4. Doc drift outside my patch, SKILL.md:211 last cell: `isolated `/var/tmp`; no real store or live fleet probe` is now false. Proposed doc-only text: ``isolated `$TMPDIR`; no real store or live fleet probe``. No leg measures it; left to the L1's SKILL landing because the item scoped the patch to the fixture.
5. Q74 antecedent absent: the fixture has no write-scope guard over the scratch root (only usage / unknown-case / root-user / tool-unreadable refusals) and takes no write target, so no refusal was lost. Removal scope is the fresh mkdtemp child only (`cleanup()` at tests/fixtures/r15-census-config.py:1487-1494), so a caller-controlled `TMPDIR` is never the removal target.
6. Leak observed, not mine to remove: `/var/tmp/r15-census-config.{3tk6qehq,psjsbayp,xec8q0wl}` (~10-12 MB each) with frozen mtimes 14:03-14:15 from runs killed before their `finally`. Outside this seat's write scope and of indeterminate ownership; flagged only.
7. C1 separability holds: no row of census/round-33/c1-items.tsv exercises this fixture (files column), so the repair cannot move a C1 item.

## Deliveries
- `.ufo/waves/round-33/w1/deliver-c2-O2.patch`
- `.ufo/waves/round-33/w1/deliver-c2-O2.md`
