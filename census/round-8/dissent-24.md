# dissent-24.md — S24 dissent & corrections record, round 8 (2026-10-18T19:57-03:00)

## Trigger

Assignment condition met on two of the three allowed axes: (a) judge-vs-judge
factual corrections — the co-judge freeze table no longer describes the field;
(b) rule/tool contradiction — gate2 as written is unpassable for the very
candidates the receipt engine calls SAFE. No seat disputes any receipt verdict;
no dispute exists over the round's claims (all three judges: MET).

## 1. Corrections to final-21 (S21) — freeze table superseded, winner unchanged

final-21 froze at 19:37:47-03:00. S24's judging-time re-runs (19:44–19:52)
supersede four of its field rows. **The O1 winner (impl-01) is unaffected** —
it was green at the freeze and green at judging time.

| row | final-21 said | S24 observed at judging time | cause |
|---|---|---|---|
| impl-03 (S03) | "assertion fails at freeze (exit 1)" | selftest **27/27 rc=0** on the SAME bytes (sha 19d424a3, mtime 19:35:21 — before the freeze) | environmental: /tmp quota exhaustion (13G/16G, "Disk quota exceeded" — final-21 itself flagged the pressure); not a code defect |
| impl-08 (S08) | "19/43 pass at freeze" | **44/44 rc=0** on bytes rewritten 19:39:48 — AFTER the freeze | S08 landed a fixed version post-freeze; seat-08 fragment still pending |
| impl-06 (S06) | sha 78db8572, "GREEN at final sweep" | GREEN 40/40, but bytes amended post-freeze (dd7bf896, 19:39:52) | seat-06.json documents the final version; selftest count matches; re-measure at integration |
| qrun-11 (S11) | "48 checks, 0 failed" | file of record says **checks=53, failed=0** | transcription slip in final-21 (S11's fragment and results/qrun-11.json agree on 53) |

Ruling: final-21's verdicts stand (its winner selection is triple-confirmed);
its freeze-table rows above are historical snapshots, not current facts. Any
parent summary should cite this file for the current field.

## 2. impl-02 is NOT defective — S24's own red run was quota corruption

S24's first impl-02 selftest run under the exhausted /tmp produced
`passed=60 failed=16` with T10 failures that read as fail-open
("tampered copy deleted without pass"). Re-derivation:

- clean-env rerun (TMPDIR=/var/tmp/s24-judging): **rc=0, 0 FAIL** — deterministic
  green; S02's 76/76 ×3 claim reproduces.
- forensic detail: the corrupted run's failures are all downstream of
  `copy-fd: write returned: Disk quota exceeded` — the record sidecar was never
  written, so `--verify-staged` correctly reported `no-valid-record` and
  `--retire` answered **RETIRE-REFUSED**: even with its fixture filesystem
  failing, the tool did not delete. Fail-closed held under environmental
  corruption. That is a positive safety datum, recorded here so no future
  reader mistakes the corrupted log for a defect.

## 3. Rule/tool contradiction adjudicated: gate2 vs untracked candidates

Independently surfaced by S18 (§2), S11 (F-2), S06 (gate2-dominance note), and
reproduced by S24 on its own fixture (untracked `.scratch/old.out`: engine
SAFE/stale; `git status --porcelain=v1 --untracked-files=all -- .scratch/old.out`
non-empty by definition). The r7 authorization rule therefore makes every
untracked stale candidate permanently unauthorized while the lane's own
engine calls it SAFE — a standing contradiction, not a safety feature (r7's
lore `.scratch` denial had three independent legs; only the clock/citation legs
are load-bearing).

**Ruling (recommended for parent adoption, not self-applied):** gate2' = "no
porcelain line touching the path except the candidate's own untracked entry."
Tracked modifications and any third-party path still fail. Until adopted,
untracked stale candidates remain NOT-AUTHORIZED — fail-closed wins ties.
Same ruling admits qrun-11 F-1 (gate1 unreachability for obsidian-class
tickets in zero-remote repos; both-digest ledger re-verification substitutes
for the unpushed half when refs/remotes is empty — fixture-proven by S11).

## 4. Second-check semantics: convergent findings, one required shape

qrun-23 (F1/F2), qrun-11 (F-4), qrun-13 (F1/F2 via final-21), S18 (§3), and
S24's own P1/P5 all converge: a pushed receipt cannot survive its own staging
commit; a second check that re-runs the tool on the copy is
necessary-but-not-sufficient; the required shape is **pre-move receipt
evidence of record + post-hold byte-identity + original-path gate stability**.
impl-01's prong1/prong2 split implements exactly this (S24 P1: `pin=ok
mtime=ok intro-blob=ok unpushed-touching=0 prong1-tolerated
class-not-path-local`). Requirement: both runbooks' execution sections fold
this in during parent integration (runbook-17 §1 A3's sha-diff form is
compatible but must add the gate re-derivation; runbook-18 §3 already states
it).

## 5. CLI divergence (S02's flag) — adjudicated

impl-01 (repo-anchored single flow, --list TSV receipt pins) is canonical:
r7-template-shaped, triple-judge verified, byte-stable. impl-02's --check /
--plan read-only modes and dual-engine gate3 (verify AND vault-verify) are
recorded as strengthening feature requests for a future revision. No live
behavior difference exists — every candidate's every probe ends
NOT-AUTHORIZED on today's fleet.

## 6. Unattributed candidates / open items (not dissent, parent queue)

- impl-04: green 37/37, no fragment. impl-07: syntax error line 107, no
  fragment. seat-08 fragment pending despite green tool. S16's full verdict
  set landed (RECONCILED with S15).
- /tmp quota: 13G/16G with per-user pressure caused in-round false-reds across
  at least three seats (S21, S24, and final-21's impl-03 row). Environmental,
  recurring risk for fixture-heavy rounds; recommend the parent's integration
  pass re-run any red selftest under a clean TMPDIR before calling code red
  (this round's precedent: impl-02, impl-03).
- LOG corrections for the append-only pass: "15× launch-*.json" → 16
  (S24 re-derived: 16 files incl. launch-tsukuroi.json); gd2d worktree/admin
  count re-stamps (S16 findings).

## Dissenting seats

None on substance. Corrections 1–2 are judge-vs-clock (facts moved after the
freeze), not seat-vs-seat; S21's and S22's verdicts are affirmed as of their
own timestamps. No seat needs to change its fragment.
