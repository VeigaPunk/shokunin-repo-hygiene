# AttackG24 — w2 adversarial falsification of W1's G24 finding

Seat SwarmCritic07, round 34 souji w2. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `9c76c7222a8abff027af42e37f0d160d52526bba`; C1 item list frozen at `2b591924f607940febbb99f922cc9bb090508eb6`
(byte-identical at `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` and at tip `adac8bbc79a7ed77b632b309e70fd2a91b45dbd9`;
verified by `git diff` over `census/round-34/c1-items.tsv` — empty). Read-only; no lane files edited, nothing committed.

## Status

**W1 finding PARTIALLY FALSIFIED.** W1's defect analysis of the frozen item stands (every cell-level defect it
named is real and independently reproduced), but its load-bearing conclusion — "No amendment is proposed
here", "The item cannot reach AGREE under the frozen bytes", "no honest row exists" — is **refuted by
executed emulation**: at least one rule-conforming restatement row passes the frozen judge for G24 at both
candidate list revisions, and a second shape also passes. The value-drift route is confirmed dead exactly as
W1 argued. Whether the surviving route is *honest* is a tradeoff the canonical judge/L1 must adjudicate; it
is not the absolute impossibility W1 claimed.

## Evidence

Frozen item (c1-items.tsv:40):

```
G24  SKILL.md:249  0  SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10  tools/souji-capability-agreement.py  9420341d9a814cb6089c25fb03a4cc9b23dc0d1b  python3 -B tools/souji-capability-agreement.py --root . --rev 9420341d… --base 9420341d… --list-rev d4928ec…
```

Executed (all commands run this seat, output abridged):

- E1 script absent at the pinned `at`: `git cat-file -e 9420341d…:tools/souji-capability-agreement.py` →
  `fatal: path … exists on disk, but not in '9420341d…'` (rc=128). Confirms W1.
- E2 script introduction: `git log --diff-filter=A -- tools/souji-capability-agreement.py` → `d4928ec…`
  (2026-10-26 01:22:27). `9420341d…` is 2026-10-26 01:11:10 — the pin predates the script by ~11 min.
  Ancestry: `9420341d ⊂ d4928ec ⊂ base 9c76c72`; also `f7329785 ⊂ 2b591924`, `f7329785 ⊂ 2b0171e2`,
  but `f7329785 ⊄ d4928ec` (all via `git merge-base --is-ancestor`).
- E3 the frozen `where` is correct at the r34 list revisions: `git show 2b591924:SKILL.md` (and `2b0171e2:`, and
  base) line 249 = the `| souji-capability-agreement | gate | …` row (811 chars). Caveat: at `d4928ec` (the
  script's own r30 prereg) line 249 is **blank** — `d4928ec` is not the C1 item list revision and must not be
  used to eyeball the row.
- E4 row authorship: `git log -S '<the exact 811-char line 249 text>' -- SKILL.md` → exactly one commit,
  `f732978506f3fa8ef32d4af1b4ee5bc962603aaf`. W1's claimed cause is the true, sole author of the row's line.
- E5 outcome column (base `9c76c72:SKILL.md:249`, same at both list revs):
  `0 \`SUMMARY k1=0 k2=0 mismatches=0\`; 1 any \`MISMATCH\` row or unresolved SHONEN pointer …; 2 could-not-evaluate`.
  A `k1=12 mismatches=12` line maps to exit **1**; the frozen exit cell says **0**. Confirms W1.
- E6 bounded probe (this seat, scratch `/fast/scratch/hyaku/souji-r34/SwarmCritic07/`): extracted the script at
  `9c76c72` (the A3-reading version, read-only on `--root` per its docstring) and ran the frozen argv semantics
  against the live lane:
  `python3 -B souji-capability-agreement.py --root <lane> --rev 9420341d… --base 9420341d… --list-rev d4928ec…`
  → **rc=1**; output tail: `SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10 rev=9420341d…` followed by
  `KINDS value=4 shape=7 rc=1 (diagnostic; not part of the target)`. Reproduces W1's executed claim exactly,
  and additionally shows the run's **last digit-bearing line is the KINDS line, not the SUMMARY line**
  (script print order at base: SUMMARY at tools/souji-capability-agreement.py:240, KINDS at :241).
- E7 judge emulation (executed): imported the frozen `census/round-34/c1-counter.py` via importlib and called
  `judge()` directly for G24 with crafted restatement rows, `rev=adac8bbc…` (tip), at both list revisions.
  Results:
  - ROUTE-BLOB — corrected argv `{BLOB:9c76c72…:tools/souji-capability-agreement.py} --root . --rev {REV} --base {REV} --list-rev d4928ec…`, restated exit `1`, statement `` `KINDS value=4 shape=7 rc=1 (diagnostic; not part of the target)` ``, cause `f7329785…`:
    `('G24', True, "rc=1 expect_exit=1 statement is the run's last digit-bearing line …", 'restated')` — **AGREE** at `2b591924` and at `2b0171e2`.
  - ROUTE-FILT — same `{BLOB}` argv piped through `| grep '^SUMMARY'`, restated exit `0` (the frozen cell), statement = the full SUMMARY line: **AGREE** at both list revisions.
  - ROUTE-SAME — value drift, `same`, cause `d4928ec…`: `BAD-CAUSE(original at parent=False at cause=False; need True/False)` at both list revisions — dead, matching W1's mechanism.
- E8 Q76: no restatement row binds G24. `git show 9c76c72:SCORECARD.md | grep -n 'G24\|Round 34 registry restatements'` → empty; at tip the section exists (SCORECARD.md:527) with only E04/E18/E23a. The r30 capability row carrying the same SUMMARY text (base SCORECARD.md:344, `### Round 30 measurements`) is not a restatement row. Confirms W1.
- E9 do-nothing record: `census/round-34/records/controls-c1-do-nothing.txt:24` → `ITEM G24 MISMATCH original rc=2 expect_exit=0 predicate fails last=python3: can't open file '…': [Errno 2] …`; the tracked pre-data summary `census/round-34/records/controls.txt` reports `SUMMARY items=60 agree=35 mismatches=25 restated=0` (list `2b591924`). Consistent with E1.
- E10 committed corroboration of the red-arm quantity: `census/round-30/records/c1-before.txt` ends
  `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d…` + `KINDS value=7 shape=5 rc=1` (v1
  reading); base `SKILL.md:249` documents the A3 reading `k1=12`, which E6 reproduced byte-for-byte.

## Findings

1. **W1's defect analysis is accurate (all reproduced).** (a) `at=9420341d` predates the script's introduction
   `d4928ec` (E1/E2), so the frozen argv can never start at the pinned checkout — the committed do-nothing
   record (E9) and the W1 deliverable agree on the exact failure. (b) The frozen exit cell `0` contradicts
   the row's own committed outcome column, which maps a `k1=12 mismatches=12` line to exit `1` (E5). (c) No
   Q76 prior row binds G24 (E8). (d) Addendum W1 did not state: the frozen predicate can never match *any* run
   of the script, because the counter matches a bare regex against the run's **last** digit-bearing line and
   the script always prints `KINDS …` after `SUMMARY …` (E6; print order at base script :240-:241). At base,
   with the script present, the item would still MISMATCH twice over.
2. **W1's impossibility conclusion is falsified — a rule-conforming route exists (E7).** The frozen counter's
   own substitution table supports `{BLOB:<rev>:<path>}` — `git show` extraction of any revision's file into
   the per-run scratch (c1-counter.py:174-192). A restated row whose corrected argv materializes the row's own
   script via `{BLOB:9c76c72…:tools/souji-capability-agreement.py}`, names that file (basename rule,
   c1-counter.py:~297), carries exit `1` per the row's outcome column, quotes the genuine last digit-bearing
   line, and names `f7329785…` as cause passes `judge()` at **both** candidate list revisions. Every clause
   checks out under the frozen bytes: the cause wrote the row's exact line (E4), is an ancestor of the list
   rev (E2), and "the row's argv already failed at the cause" holds trivially because every evaluation clone
   is pinned to `9420341d` (E1). The measurement itself is genuine and reproducible (E6, E10): the script's
   inputs are rev-pinned git reads, so the run measures exactly the red-arm quantity the row documents.
3. **The value-drift route is dead exactly as W1 said (E7 ROUTE-SAME).** `rrun == "same"` requires the frozen
   (exit, predicate) to hold at the cause's parent; both holds probes run in a clone checked out at `9420341d`
   (`checkout_rev`, c1-counter.py:170-171; run_item :200-207), so `held=False`, `stops=False` →
   `BAD-CAUSE(… need True/False)` at both list revisions. No `same`-shape row can pass for G24.
4. **Honesty adjudication of the surviving route (labeled assessment, not execution).** The {BLOB} route is
   letter-conforming and fully disclosable: cause is true provenance (E4), exit correction is grounded in the
   row's own committed outcome column (E5), the statement is a real execution's last line (E6), and the reason
   column can state plainly that the `at` pin predates the script and that the script is imported from its
   A3-era state. The residual objection — the measured checkout does not contain the executable, so the run
   certifies a counterfactual for the pinned revision, and the "argv already failed at the cause" clause is
   vacuous for this item since the frozen argv fails at *every* cause — is a real tradeoff, but it is the
   tradeoff the frozen bytes themselves permit (the {BLOB} mechanism and the clause are both frozen design).
   ROUTE-FILT (exit `0` via grep) is closer to gaming the statement rule and is **not** recommended; ROUTE-BLOB
   (exit `1`) is the honest candidate. This is a fixable-defect-vs-tradeoff call for the canonical judge/L1,
   not the "no honest row exists" absolute W1 asserted.
5. **Corrections to W1's minor claims (W1 is right on each after full inspection).** (a) "the correct row at
   the list revision" — true at the r34 list revs (`2b591924`/`2b0171e2`) and base; only at `d4928ec` is
   SKILL.md:249 blank (E3). (b) "`f7329785` first wrote the row's line text" — confirmed by full-line pickaxe,
   sole commit (E4). My initial attempts to contradict (a) and (b) used `d4928ec`/the bare SUMMARY string and
   are withdrawn. (c) W1's refusal of the `git show … > tools/…` workaround remains correct: it mutates the
   measured checkout, and it is also unnecessary — the frozen counter provides the non-mutating `{BLOB}` path.
6. **Family note (out of seat scope, labeled inference).** G23 and G26 share the same script/`at`-pin shape per
   the frozen list and W1's G24 header ("Same flocked run as G23"); the {BLOB} technique should transfer.
   G23/G26 are other seats' targets; flagged for the L1 only.

## Attack log

1. Read W1 deliverable `w1/deliver-c1-G24.md`, frozen row (c1-items.tsv:40), preregistration, counter source.
2. Verified W1's git facts (E1-E5) — all reproduced; attempted contradictions of W1's where/cause claims
   initially succeeded at `d4928ec` and were then shown to be an artifact of inspecting the wrong revision
   (the script's `--list-rev` is not the C1 item list revision). Corrected; W1 stands.
3. Ran the bounded base-semantics probe (E6) — confirmed W1's rc=1 + SUMMARY claim; discovered the KINDS
   last-line fact (finding 1d).
4. Searched for routes W1 missed: found the counter's `{BLOB}` substitution (c1-counter.py:180-192). First
   emulation round misused the list revision (`d4928ec`) — counter correctly refused
   (`COULD-NOT-EVALUATE … c1-items.tsv absent`); established item-list identity across `2b591924`/`2b0171e2`/tip.
5. Second emulation round used the list rev as cause — all routes died at cause checks; diagnosed the mistake.
6. Third emulation round with the correct cause (`f7329785`, E4) at both list revs (E7): ROUTE-BLOB and
   ROUTE-FILT **AGREE**; ROUTE-SAME dead as W1 predicted. Scratch cleaned (0 bytes left in `tmp/`).

## Deliveries

- This report: `.ufo/waves/round-34/w2/AttackG24.md` (required path, written).
- Scoped seat report: `.ufo/waves/round-34/w2/SwarmCritic07.md` (required path, written).
- Probe artifacts (scratch, not lane): `/fast/scratch/hyaku/souji-r34/SwarmCritic07/run-base.out` (E6 full
  output), `judge-probe.py` (E7 emulation), `souji-capability-agreement.py` (extracted copy). Scratch usage
  well under the 50 MB ceiling; the lane was never written (script is read-only on `--root`; judge emulation
  called `judge()` read-only with `root=<lane>`; two transient evaluation clones were created under
  `/fast/scratch/…/judge-work` and deleted by the probe).
- No lane files edited; no commits; no other repositories touched.
