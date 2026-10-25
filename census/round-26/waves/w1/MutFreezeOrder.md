# MutFreezeOrder — amendment-ordering mutation probe (souji round-26, w1)

Scope: verify the frozen claim that amendment 1 was logged BEFORE any seat scored
(freeze 12fd90b before red-receipts commit 89e0fce, both before wave spawn), then
mutation-test the counterfactual: pre-amendment green data vs the prereg's own rules.
Read-only seat; only this report written; no scratch dir created (nothing to remove);
no tools installed. All times UTC (git %ct epoch; local host is UTC-3).

## Status

STATUS: PASS — ordering claim VERIFIED from commit metadata; the counterfactual mutant
(pre-amendment green data escaping detection) SURVIVES the prereg's own rules, recorded
below as a coverage finding, not a contract change.

## Evidence

Commands (read-only, run 2026-10-25 ~17:32Z, at master, lane /home/vgpnk/Projects/shokunin/souji-shokunin):

1. `git show -s --format='%H %ct %at %s' 12fd90b 89e0fce`
   - `12fd90bcd9cdfab495e178023eeaa838a977fcbe` "round-26: preregistration freeze (C1
     calibration SCORECARD scaffold census, C2 coverage F1 trigger-set assimilation, C3
     operability axis-check instrument)" — commit 1792947870 = 2026-10-25T17:04:30Z,
     author 13:50:58Z, parent `0eca7c8` (lane base). First commit on the base.
   - `89e0fceeefcf28db313c94120be6d25e03c60094` "round-26: prereg amendment 1 (C2 K4
     literal corrected to base-derived grounded=7/kill_tested=7) + red-before receipts"
     — commit 1792948047 = 17:07:27Z, parent `12fd90b`.
2. `git merge-base --is-ancestor 12fd90b 89e0fce` → true (12fd90b IS ancestor of 89e0fce).
3. Spawn bound: `.ufo/waves/round-26/w1/` birth 17:15:19Z; `.ufo/waves/round-26/w1.ready.dispatched`
   birth 17:15:44Z. [INFERENCE] these directory-creation times are used as spawn proxies;
   no direct spawn record was read.
4. Receipts committed INSIDE 89e0fce (`git show 89e0fce:census/round-26/records/<f>.tsv`):
   - c1-before: rev=12fd90b…, rc=0, utc=2026-10-25T17:06:10Z
   - c2-before: rev=12fd90b…, rc=0, utc=2026-10-25T17:06:11Z
   - c3-before: rev=12fd90b…, rc=0, utc=2026-10-25T17:06:12Z
   - c2-k4-base: rev=0eca7c8…, rc=0, utc=2026-10-25T17:06:13Z
5. Amendment text `.ufo/waves/round-26/preregistration-amendment-1.txt` (opened this run):
   header "(2026-10-25, pre-data)"; footer: "No seat had scored any claim data at amendment
   time." Amendment is stricter-only literal correction (C2 K4 grounded=8→7 / kill_tested=6→7,
   control grounded=6→7, re-derived at base 0eca7c8); no predicate, target or case set relaxed.

## Findings

1. Ordering VERIFIED (location: lane `git log`, revs 12fd90b, 89e0fce). Freeze commit
   17:04:30Z precedes amendment+red-receipts commit 17:07:27Z (parent chain, not just
   timestamps); both precede wave spawn (~17:15:19Z, [INFERENCE] proxy). The red-arm
   receipts carried by 89e0fce were generated 17:06:10–17:06:13Z — after the freeze
   commit, before the amendment commit. Ordering claim holds on all three edges.
2. MUTANT SURVIVES — the prereg's own rules would NOT catch pre-amendment green data
   (locations: `.ufo/waves/round-26/preregistration.txt` AMENDMENT RULES section;
   `tools/souji-receipt-run.py:77`). The ordering rule is prose only — "any preregistration
   amendment must carry its red-arm receipts BEFORE any green after-data is scored" —
   enforced through commit order plus self-attested receipt fields:
   `HEADER_ORDER = ("receipt", "rev", "tool", "tool_sha256", "cmd", "rc", "utc")`.
   No frozen predicate compares any receipt `utc` against the amendment commit time, and
   none requires a green receipt's `rev` to equal the final landing tip; the round's own C3
   instrument (`tools/souji-axis-check.py`, rules R1–R4) checks axis/class/enumerate only.
   A seat that produced green data before the amendment and committed its red receipts
   afterward fails no frozen rule. The raw evidence to catch it exists in every receipt
   (`utc`, `rev`) but no kill rule consumes it — enforcement is by the honor of the same
   seat holding the data.
3. Live instance of receipt mutability (observed this run; location: `census/round-26/records/`,
   revs 89e0fce vs HEAD via e0f8dcd / d6c13b0). The red receipts c2-before and c3-before were
   REGENERATED mid-wave and recommitted: at 89e0fce rev=12fd90b… utc=17:06:11Z / 17:06:12Z;
   at HEAD rev=89e0fce… utc=17:29:54Z / 17:29:28Z (commit e0f8dcd 17:29:52Z, d6c13b0
   17:30:04Z). No rule flagged the swap. c1-before and c2-k4-base are unchanged between the
   two revs. Note also: the frozen literal "committed BEFORE after-data" is evidenced only by
   the 89e0fce copies — at HEAD, c2-before (utc 17:29:54Z) and c2-after (utc 17:29:55Z) sit in
   the SAME commit d6c13b0. [Observation only; not judged here.]

## Attack log

- MUT-1 (mutation of the frozen ordering claim): "amendment 1 logged before any seat scored"
  → assume a seat had already produced green claim data before amendment 1 landed.
  Expected detector (per prereg's own rules): the AMENDMENT RULES red-before-green clause
  or a receipt-binding kill rule should fail. Actual output: no rule or tool in the frozen
  contract consumes receipt `utc`/`rev` against the amendment commit (finding 2), and the
  observed mid-wave regeneration/recommit of c2-before/c3-before tripped nothing (finding 3).
  Verdict: SURVIVED — coverage finding; the contract is not mine to change.
- Baseline control: pristine ordering evidence (finding 1) reproduces the frozen claim, so
  the detector set is non-vacuous — the claim is checkable where it is true.

Revisions cited: 0eca7c8 (base), 12fd90b (freeze), 89e0fce (amendment 1 + red receipts),
e0f8dcd, d6c13b0 (mid-wave receipt landings), HEAD-at-read d6fe8a1.
