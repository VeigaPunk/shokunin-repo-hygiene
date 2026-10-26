# SwarmCritic13 — falsify C1 item K15 (SCORECARD.md:172, blob-bound receipts)

## Status
STATUS: PASS — K15 falsified: verdict **HOLDS** at measured rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46. The item is
deterministic, its frozen predicate `\b8/8\b` is a faithful reading of the cell's stated outcome for this command, and
no other count/outcome in the same cell is stale. One out-of-set residual (description-only refusal clause unbound by
the cited command) is reported below; it is not a predicate defect and needs no amendment.

## Evidence
Scratch: `/fast/scratch/hyaku/souji-r33/AuditK15/` (clone `c` at 2d9bca5, TMPDIR `tm*`), removed after the audit.

Row read at base (`git show 6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md | sed -n 172p`), inside
`## Capabilities` (section opens at line 143). Cell text quoted verbatim (no pipe characters):

> `tools/souji-receipt-run.py`; `tests/fixtures/r23-receipt-run.py` 8/8; `census/round-23/records/*.tsv`

**1. Determinism** — argv `python3 tests/fixtures/r23-receipt-run.py`, run from the clone root at 2d9bca5, fresh TMPDIR
per run (`tm1`, `tm2`):

```
run1 rc=0   run2 rc=0
selftest=8/8   (both runs, line 10)
case=1 ... got=<rc=0 header=v1/7 sha256=a62c58548f91... stdout=assertions=4 resolved=3 skipped=1 mismatches=0 label=two ... rc_probe=3>
case=8 ... got=<sha_equal=True cmd_equal=True utc_equal=False utc=[2026-10-26T16:56:52Z, 2026-10-26T16:56:54Z]>
```

Raw diff run1 vs run2 = one line, `case=8` only (`utc=[16:56:52Z,…:54Z]` vs `[16:56:55Z,…:56Z]`); case 8 *asserts* that
the utc differs, so the diff is the case's own subject and not variance in a verdict. With the utc field normalised the
outputs are byte-identical. Third run with `env -u TMPDIR` (no inherited TMPDIR): `rc=0`, `selftest=8/8`, empty stderr,
8 `case=` lines; normalised diff against run1 CLEAN. Deterministic.

**2. Predicate faithfulness** — fixture summary is derived, not hardcoded:
`print(f"selftest={passed}/{len(CASES)}")` and `return 0 if passed == len(CASES) else 1`
(`tests/fixtures/r23-receipt-run.py:549-550`), with 8 `CASES`. Hence item (`exit=0` AND `\b8/8\b`) ≡ "all eight fixture
cases green". Two mutations in the scratch clone test discrimination:

- M1, receipt records `rc=0` always (`tools/souji-receipt-run.py:295` `f"rc={proc.returncode}"` → `f"rc={0}"`):
  `rc=1`, `case=1 ... got=<rc-probe recorded rc=0 want=3>`, `selftest=7/8` → predicate FAILS. The count tracks a real
  mechanism (rc fidelity), not decoration.
- M2, drop the `git -C/--git-dir/--work-tree` refusal guard (line 143): fixture still `rc=0`, `selftest=8/8` → the
  fixture is blind to that regression. That clause lives in the row's *description* column ("refuses a `git -C`/…"), not
  in the cell's stated outcome for this command, so it is outside K15's item.

**3. Other outcomes in the same cell** — `census/round-23/records/*.tsv` still resolves: 6 `.tsv` files present at base
and at 2d9bca5 (`agreement-after`, `declared-evidence-after`, `gate-check-at-first-landing`, `gate-check-at-lane-base`,
`gate-check-c3`, `uncommitted-exemptions`). The bare span `tools/souji-receipt-run.py` states no outcome (excluded by the
enumeration rule). The R3 footnote ("the digest binds the labelled file's committed bytes and the recorded argv label,
not the executed program") still matches tool behaviour: digest is sha256 of the tool bytes in the measured tree and is
checked against the committed blob, and `RECEIPT-TOOL-NOT-IN-ARGV` binds the label to `cmd=` text, not to what ran —
probed below. The description's refusal clauses were re-derived by execution at 2d9bca5 in a probe repo
(`probe/tools/tiny-counter.py`, rev 33fb6dfd864c47da938b2fa7321175c19b4ef89a`), all exit 2:

```
git -C . rev-parse HEAD            -> GIT-DIRECTED-COMMAND  a -C/--git-dir/--work-tree command escapes the measured tree
git --git-dir .git rev-parse HEAD  -> GIT-DIRECTED-COMMAND  (same)
git fsck --lost-found              -> WRITE-SIDE-EFFECT     git fsck --lost-found writes into the repository
git gc                             -> MUTATING-SUBCOMMAND   git gc is not a counter
git status --porcelain             -> TOOL-NOT-IN-ARGV      tools/tiny-counter.py is not an argv element of the command
```

So no stale outcome, and the description is currently true — only unbound by the enumerated command.

**4. Counter** — `python3 -B census/round-33/c1-counter.py --root <lane> --rev 2d9bca5… --list-rev 2d9bca5… --scratch
AuditK15/cnt --only K15`:

```
ITEM	K15	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest=8/8
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=0
```

Same command with `--rev 6017a482e7068d5afb7617640198fbb0fe743357` (base): identical `ITEM K15 AGREE … last=selftest=8/8`,
`SUMMARY … mismatches=0 … rev=6017a48…`, rc=0. (`partial=1` is the counter's `--only` subset flag,
`census/round-33/c1-counter.py:307`.)

**No drift to hide a measurement**: SCORECARD.md at base and at 2d9bca5 are byte-identical (`diff` → IDENTICAL), and both
`tools/souji-receipt-run.py` and `tests/fixtures/r23-receipt-run.py` are SAME bytes at the two revs; no commit between them
touches either file.

## Findings
1. K15 predicate `\b8/8\b` + `exit 0` is exactly the cell's stated outcome ("8/8") and is bound to the fixture's derived
   `passed/len(CASES)` summary; M1 shows a mechanism regression turns it red. Not laxer, not stricter.
   Location: `SCORECARD.md:172` (evidence cell), `tests/fixtures/r23-receipt-run.py:549-550`, `census/round-33/c1-items.tsv:29`.
2. Output is deterministic across fresh-TMPDIR runs and with TMPDIR unset; the only byte variance is `case=8`'s utc pair,
   which the case exists to observe. Location: `tests/fixtures/r23-receipt-run.py` case 8.
3. Out-of-set residual, NOT stale, NOT an amendment request: the row's description promises `git -C`/`--git-dir`/
   `--work-tree`, mutating-subcommand and `--lost-found` refusals, and no enumerated item cites a command for them; M2
   (guard removed) still prints `8/8`, so the count does not bind that clause. The clause does hold today (probe, exit 2
   codes above). Location: `SCORECARD.md:172` description column; guard at `tools/souji-receipt-run.py:141-151`.
4. The cell's record glob is live (6 `.tsv`), and the R3 footnote's digest/label semantics match the tool. No stale
   count or outcome in the cell. Location: `census/round-23/records/`, `tools/souji-receipt-run.py:290-306,367`.

## Attack log
- Attack A (nondeterminism): run argv 3× (2 fresh TMPDIR, 1 TMPDIR unset) — all `rc=0`, `selftest=8/8`; only `case=8` utc
  values move. **Failed to break.**
- Attack B (lax predicate via substring): `\b8/8\b` could in principle match a `got=` field rather than the summary, but
  the item also requires exit 0, and exit is 0 only when `passed == len(CASES)`; no `got=` field in any case emits
  `/8`. **Failed to break.**
- Attack C (lax predicate via regressed tool): M1 (hardcoded recorded rc) → `selftest=7/8`, rc=1. **Failed to break.**
  M2 (guard removal) → still `8/8`, rc=0: succeeds only against the *description's* refusal clause, which the frozen
  item set does not enumerate → reported as residual finding 3, not as a K15 defect.
- Attack D (stale ancillary outcome): records glob and R3 footnote re-derived — both hold. **Failed to break.**

Verdict: **HOLDS**.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic13.md` (this report)

Tooling: no installs or upgrades. Scratch `/fast/scratch/hyaku/souji-r33/AuditK15` created and removed (verified absent);
no lane git/jj mutation; `/tmp` used only by the assignment-mandated TMPDIR-unset run, whose fixture scratch is removed by
its own atexit cleanup (no `/tmp/r23*`/`/tmp/tmp*` residue; `/tmp` entry count unchanged at 397).
