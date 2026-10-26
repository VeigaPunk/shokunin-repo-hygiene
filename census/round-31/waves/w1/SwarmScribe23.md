# SwarmScribe23 — round 31 w1 record skeletons

## Status

STATUS: PARTIAL — all five requested skeleton blocks were delivered as fill-in placeholders; PASS is impossible for a skeleton seat because every after-value belongs to data the L1 has not yet produced (C3's entry is absent at the measured revision).

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, revision read `1b811368461785040e955f41f9c97e62f61fd67c` (`git log --oneline -3` prints `1b81136 round-31: C1 base output and M1 red-before receipt` on top of `ed17ff6` and `1d45496`). Worktree clean for my scope (`git status --porcelain` printed nothing).

Contract and inputs read this run: `census/round-31/records/preregistration.txt` (C1/C2/C3 paragraphs, G1-G10, MACHINE BLOCK, closing rule), `census/round-31/records/controls.tsv`, `census/round-31/records/amendments.txt`, `census/round-31/records/c1-before.txt`, `census/round-31/records/m1-red-before.txt`, `census/round-31/c1-cells.tsv` header, `tools/souji-capability-cells.py:1-40`, `SCORECARD.md:330-359`, `LOG.md:-60`, `SHONEN.md`, `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md`, wave siblings `deliver-c1-bind-L30-L41.md`, `deliver-sources-rows.md` (style only; not evidence).

Base literals copied verbatim from `census/round-31/records/controls.tsv`:

```
C1-do-nothing(base)	c1	SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
C2-do-nothing(base)	c2	SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
C3-do-nothing(base)	c3	SUMMARY legs=11 fail=10 f1_entries=3 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
C3-do-nothing(base)	c3v2	SUMMARY legs=12 fail=11 f1_entries=3 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
```

Independent base re-read of the C1 receipt (`census/round-31/records/c1-before.txt`): `grep -c "^ITEM"` → `41`; `grep -c UNBOUND` → `22`; tail → `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` then `rc=1`.

M1 receipt recount (`awk` over `census/round-31/records/m1-red-before.txt`): round 26 `findings=18 … checked_reports=466`, round 27 `findings=29 … checked_reports=94`, round 28 `findings=21` over `checked_reports=61`, of which 19 `LG-SEAT-UNCARRIED` and 2 `LG-DANGLING-PTR`.

Targets as written in `census/round-31/records/preregistration.txt`: C1 `unbound=0 mismatches=0` (items stay 41); C2 `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same`; C3 v1 `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=0 f1_entries=4` (A0 adds L12).

Revision held for every reading above: `1b811368461785040e955f41f9c97e62f61fd67c`. No measurement was executed by this seat, so nothing here is an execution claim.

Scratch: no scratch directory was created (no clone, fixture or download was needed); `/fast/scratch/hyaku/souji-r31/SwarmScribe23` therefore does not exist. No tool was installed or updated; pacman was not invoked.

## Findings

1. Delivery written: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-records-skeleton.md` (17726 bytes, five sections in the assigned order). Every after-value, landing commit, receipt filename and seat count is an explicit `<...>` placeholder; the before-values and targets are literal.
2. C1 fill rule matches the frozen counter, not the assignment prose: `tools/souji-capability-cells.py:11-18` accepts only the last row after the `--base` bytes of the form `| <id> | SCORECARD.md:<line> | <literal> | run: <argv> | <note> |` or `| ... | record: <path> | <note> |`, and the docstring states a row must carry at least two integers in the literal and no `-c/-h/--help/--version` argv token — the skeleton repeats those constraints so the L1 does not append a row the counter will score `BAD-ROW`.
3. Amendment field in the round-31 SCORECARD heading must cite `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc` unless wave 1 lands a stricter amendment: A0 is timestamped `2026-10-26T03:16:18-03:00` in `census/round-31/records/amendments.txt` with the reason "wave 1 not yet dispatched". `A0` changes the C3 target shape (v2 legs 11→12), so a heading that says only "preregistration" would understate the contract the claims were scored against.
4. C3 cannot be pre-filled: `corpus/knowledge/jj-dropped-keep-object-lifetime.md` is absent at `1b81136` (`ls` rc 2), so `f1_entries=4` and the fixture/record names are placeholders by necessity. The draft in `deliver-entry-jj-dropped-keep-object-lifetime.md` is not committed and was not treated as landed.
5. M1 numbers in the LOG skeleton are the receipt's, not the assignment's summary: round 27 carries 29 findings over `checked_reports=94` and round 28 shows `findings=21` = 19 uncarried + 2 dangling over 61 reports (`census/round-31/records/m1-red-before.txt`). The round-26 figure (18 over 466) is the one the preregistration quotes.
6. SCORECARD insertion point verified: the file is 359 lines and line 359 is the live `- **r31 (planned r30):**` bullet, so the three round-31 sections append after the last byte (no in-place edit), consistent with C1's append-only rule.
7. SHONEN has exactly four boxes (`SHONEN.md:5,7,9,11`); the report skeleton carries one line per box, each with a slot for the r31 pointer the L1 must supply.
8. No fleet-side cross-check was possible: `/home/vgpnk/Projects/shokunin/.ufo/waves/round-31/` did not exist at read time (`ls` rc 2), so the report skeleton's wave accounting is left to the L1's own capture.
9. Attack log: not applicable — this item is a documentation seat and asserts no counter claim. Nothing in this report proposes a predicate, target, counter or case-set change.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-records-skeleton.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/SwarmScribe23.md` (this report)
