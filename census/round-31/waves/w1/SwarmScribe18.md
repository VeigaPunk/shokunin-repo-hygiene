# SwarmScribe18 — M1 carry draft for round 26 (wave 1, round 31)

## Status

STATUS: PASS — the append-only `## Seat-reported failures` section for
`corpus/lessons/round-26.md` is drafted byte-exactly and proven in a scratch
clone: base gate red at 18 `LG-SEAT-UNCARRIED` over 466 reports, green
(`findings=0`, `carry_heading=1`, `checked_markers=18`) after the append, the
gate-blind capture-only arm 8/8 carried, and a mutation control that flips the
gate to exactly one finding when a disposition is deleted.

## Evidence

All runs in `/fast/scratch/hyaku/souji-r31/M1CarryR26/` (clone of the lane,
`origin` removed, toplevel verified before the first commit). Gate bytes:
`tools/souji-landing-gate.py` blob `51f98ed7f9b6cf834e93be94c6bbdd9e392e17a6`,
identical at base `9f17a1e` and tip `1b81136`; the "base gate" is that blob
extracted with `git show 9f17a1e:tools/souji-landing-gate.py`.

1. Red-before, base content, base gate (`--rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round 26 --fleet-root /home/vgpnk/Projects/shokunin`):

```
rc=1
SUMMARY	findings=18	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=69	carry_heading=0	checked_reports=466
18x LG-SEAT-UNCARRIED, no other finding id
```

2. Red-before, capture-only arm (gate functions imported from the base gate by path; `seat_failure_lines` + `status_paragraph` + `carries`):

```
before(base lesson) cap_only_reports=29 paragraphs=8 carried=0 uncarried=8
```

3. Append + commit in the clone (`1b81136…` → `3656eac2b73ef50b62bed4a7083fd70663aaba3a`,
message `round-26: append-only Seat-reported failures carry section (26 paragraphs, 9 resolved, 17 open)`), base gate at that rev:

```
rc=0
SUMMARY	findings=0	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=69	carry_heading=1	checked_reports=466
```

Zero `LG-SEAT-UNCARRIED`. Same rev, capture-only arm:

```
after(carry commit) cap_only_reports=29 paragraphs=8 carried=8 uncarried=0
```

4. Mutation control `9aac35839e62c18ec8dcb84dfb48868a98aef6ac` (one bullet loses its
` — open` disposition; all 26 quote texts untouched) at `--round 26`:

```
rc=1
LG-SEAT-UNCARRIED	.ufo/waves/round-26/w1/CritAmendNeed.md	line 5: STATUS: PARTIAL — all three holes are real, and they
SUMMARY	findings=1	...
```

5. Disposition basis, re-checked at lane tip `1b81136` (read-only):

```
souji-receipt-run.py verify census/round-26/records/c1-before.tsv -> rc=2
souji-receipt-run.py verify census/round-26/records/c2-before.tsv -> rc=2
souji-receipt-run.py verify census/round-26/records/c3-before.tsv -> rc=2
souji-receipt-run.py verify census/round-26/records/c2-k4-base.tsv -> rc=0
bash -n <blob 9f17a1e:.ufo/waves/round-26/w1/verify-loop.sh> -> rc=2
```

Counts in the drafted section: 26 bullets = 18 gate-visible + 8 capture-only;
17 `open`, 9 `resolved@<full40>` (1× `07f83e6…`, 7× `50443f5…`, 1× `c594901…`).

## Findings

1. The round-26 lesson has no failure-carry section: `corpus/lessons/round-26.md`
   (96 lines at `9f17a1e`) carries `## Gate`, `## Findings`, `## Residuals`,
   `## Receipts`, `## Mistakes table` only; the base gate prints
   `carry_heading=0` with 18 uncarried failure paragraphs. Fix drafted, not landed
   (read-only seat); the L1 holds the append.
2. The failing channel is wider than the gate can see:
   `tools/souji-landing-gate.py` `check_carry` reads one tree only —
   `.ufo/waves/round-N/` when committed, else `census/round-N/waves/` — so the 29
   capture-only `.md` under `census/round-26/waves/` contribute 8 failure paragraphs
   that no gate SUMMARY line can ever count (line `check_carry`, the `if not reports:`
   fallback). The drafted section carries them anyway, but the coverage gap stands
   for any round whose capture kept extra reports.
3. `LOG.md` has no round-26 entry at all: headings run `## 2026-10-25 — Round 25 …`,
   then `## 2026-10-25 — Round 27 attempt 2 …` (`LOG.md:1743`) with nothing for round
   26 between them; the ScribeLogR26 draft's block never landed. Its two named
   blockers are fixed (`33e6807`, `c594901`), so that bullet reads `resolved`, but
   the log gap itself is open.
4. Round-26 receipts still refuse verification at tip: `census/round-26/records/`
   `c1-before.tsv`, `c2-before.tsv`, `c3-before.tsv` each exit 2 under
   `tools/souji-receipt-run.py verify` (RECEIPT-COUNTS-ABSENT), so the r26 prereg
   clause "each verify=ok" is still unearned. Basis for `open` on
   `LabReceiptVerify.md:5`, `RevC2Scope.md:9`, `SentBounds.md:3`.
5. `.ufo/waves/round-26/w1/verify-loop.sh` is committed but not shell-parseable at
   base (`bash -n` rc 2: `line 320: unexpected EOF while looking for matching` a
   double quote);
   the ExecVerifyLoop seat's fix was an uncommitted worktree edit and never landed.
   Basis for `open` on that bullet.
6. The carry section is load-bearing, not decorative: deleting a single disposition
   returns exactly one `LG-SEAT-UNCARRIED` for that report, so the green in (3) is
   produced by the bullets and not by the gate's pass-through.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-m1-carry-r26.md` — the exact block to append
  (heading, provenance line, 26 bullets), red-before/after gate runs, mutation
  control, per-entry disposition basis, limits.

No tool installs or upgrades (none needed). Scratch
`/fast/scratch/hyaku/souji-r31/M1CarryR26/` removed after the delivery file was
written. No lane write, no git/jj mutation in the lane, no sibling-lane or fleet touch.
