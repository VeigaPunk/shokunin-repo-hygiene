W2Readme — attack on `corpus/README.md` § "Round 23 — record agreement, blob-bound
receipts, F2 read side" (README.md:452–500) plus the F2 rows it touches (:40, :47, :68).

Method: re-ran every counting command the section names, at the lane tip, against the
bytes the file commits. Lane was live-mutating during review: I observed tips
1026900 → 1dd8b1e → 5378018 → 3b72bea → cfd5d79 → 466f539 (last commit "round-23:
entry-1 corrections", 05:57). All verdicts below are at tip 466f539 unless stated;
several cells were falsified at the earlier landing commits and then repaired by
wave-2 seats — those are reported as landed-then-fixed, because they prove the
section shipped false numbers before falsification.

=====================================================================
VERDICT: the section does not fully survive. Four cells/lines need fixing or
disclosure; the claim directions survive and two cells were repaired mid-review.
=====================================================================

----------------------------------------------------------------------
F1 — C1 before cell was falsified at 1026900; fixed at 1dd8b1e. RESOLVED-at-tip.
----------------------------------------------------------------------
README.md:456 at 1026900 read `mismatches=20` at the base revision.

Re-runs of the named command, all quoted verbatim:

  $ python3 -B tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --root .
  keys=4 records=3 occurrences=13 mismatches=8      (K1 1, K2 3, K3 2, K4 2 live-worktree)

  $ python3 -B tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --no-worktree --root .
  keys=4 records=3 occurrences=13 mismatches=6      (K4 arm off)

  Committed control the same README cell cites (`agreement-control-base.txt`,
  `--no-worktree`): keys=4 records=3 occurrences=13 mismatches=6.
  Committed worktree arm (`agreement-control-base-worktree.txt`): mismatches=29.

`mismatches=20` matched none of them. Peer L1Souji23.W2C1Ctl traced it to the
333-line pre-hardening tool blob `e41db304…e596`, which exists in no commit — the
exact D3 shape C2 claims to close, inside C1's own table. A wave-2 seat corrected
the cell to 6 at 1dd8b1e; tip now reads `mismatches=6`, which re-runs green.
Residual: LOG.md:1576 still carried `mismatches=20` alongside the correct
`agreement-control-base.txt` citation at 1026900; the same fix touched it at
3b72bea ("…the same tool bytes at base: keys=4 records=3 occurrences=13
mismatches=6, rc 1"). Verified at tip.

----------------------------------------------------------------------
F2 — C1 after cell: value now receipt-bound, but the counting command printed in
     the cell does not produce its value. PERSISTS at 466f539.
----------------------------------------------------------------------
README.md:456 names `python3 -B tools/souji-record-agreement.py --rev <full40>`
and claims `0` at the landing tip.

That command reads the live worktree for K4 (tools/souji-record-agreement.py:278–303:
`git status --porcelain`, every non-exempt path is one mismatch; the exemptions file
is the only escape, pinned to `census/operator-sweep-20261019/`). At 466f539:

  $ python3 -B tools/souji-record-agreement.py --rev 466f53994c6cfca9e983909983fa3e7493e87686 --root .
  keys=4 records=4 occurrences=17 mismatches=3      (K4: W2Census.md, W2Q54.md, tests/fixtures/__pycache__/)

Earlier the same command at ~1026900 printed 0, then 10, and a peer printed 20 at
05:47 — it is worktree-noise by construction, a fact README.md:475 itself discloses
("K4 is a worktree observation, so C1's K4 is not revision-reproducible").

  $ … --no-worktree --root .
  keys=4 records=4 occurrences=17 mismatches=0      rc=0   ← the arm the cell's value needs

The after value is now bound: `agreement-after.tsv` was regenerated (verify=ok,
rev=3b72beacfbcc05b2e38ef246e22787b052e34b8d, rc=0, mismatches=0) — but that receipt
was taken with `--no-worktree`, and its rev is cfd5d79's parent, not the tip. The
committed SCORECARD.md C1 row already prints the command WITH `--no-worktree`;
README.md:456 does not. FIX: add `--no-worktree` to the counting-command cell (as
SCORECARD does) and say the live-K4 arm is reported separately, or accept that the
printed command prints whatever the tree holds at run time.

----------------------------------------------------------------------
F3 — fixture sentence wrong twice over. PERSISTS at 466f539.
----------------------------------------------------------------------
README.md:468: "rejects an always-zero emitter on eight of its nine cases."

Committed fixture at 466f539 has 11 cases (CASES table: 2 green-on-clean —
`repaired`, `exempted-dirty` — and 9 non-zero-expectation cases). Running the
committed blob in own scratch:

  selftest=11/11   control=FALSE-GREEN-REJECTED   rc=0

So an always-zero emitter is rejected on 9 of 11 cases, not "eight of nine".
Both number and denominator are stale (the file grew 9→11 cases when a wave-2 seat
added `class-missing` and `tally-stale-log`). Same class, cross-file: LOG.md
(fixed version) says "ten of its eleven cases" — also wrong; it is 9 of 11.
FIX: set both to "nine of its eleven cases".

----------------------------------------------------------------------
F4 — F2 coverage-map row (:40) is stale and contradicts the round's own claim.
     PERSISTS at 466f539.
----------------------------------------------------------------------
README.md:40 (coverage map): "F2 repository size census | frontier, no entry
(…sweep: `ls corpus/knowledge | grep -ciE 'size|structure|sizer'` → 0, 2026-10-19) | —".

  $ ls corpus/knowledge | grep -ciE 'size|structure|sizer'
  2

The same file's :68 says the read side now holds three entries and C3's cell says
"F2 entries 1 → 3". :40 is the exact string the preregistration quoted as F2's
state ("frontier, no entry"); it is superseded in writing by the "## Round 13
current coverage (supersedes the r12 F2 row)" heading at :65 — but the round
added its r23 note to :68 only and left the status row asserting "no entry" with a
re-runnable sweep that now returns 2. Under C1's own calibration axis the file
disagrees with itself. FIX: amend :40's status (e.g. "superseded by :68 r23") or
disclose; the dated sweep string can stay as a dated observation.

----------------------------------------------------------------------
F5 — "F2 entries 1 → 3" is prose-only; the row's evidence column still shows one.
     PERSISTS at 466f539.
----------------------------------------------------------------------
README.md:68's entries column lists `knowledge/git-repo-structure-readonly.md`
plus tool, fixture and census JSON — one knowledge entry — while its own bold note
says three. A mechanical count of knowledge entries from the row gives 1 → 1.
The two r23 entries are named only in prose. LOW: complete the column with
`knowledge/repo-size-census-readonly.md`, `knowledge/count-objects-garbage-readings-r25.md`
(their S-ids already name them in the prose) so the counter the cell quotes
re-derives from the row.

----------------------------------------------------------------------
F6 — § Frontier "not reading" overstates; the frontier status itself is not
     overclaimed. PERSISTS at 466f539.
----------------------------------------------------------------------
README.md:486: "the read side now has entries; what remains is actable work, not
reading". The r25 entry's own Gate carries a REJECT whose flip is a reading task:
"a JA source that glosses the `garbage` field itself and states its unit"
(corpus/knowledge/count-objects-garbage-readings-r25.md, last Gate row). "not
reading" is only true if flips are excluded from "remains". LOW: qualify as
"actable work plus the Gate flips" or scope to "no reading for the admitted claim".

Frontier status: not overclaimed. :68 keeps "wider size attribution remains
frontier"; the § Frontier bullet lists F2 under `### Frontier (r23)` with owed
work (write-safety fixture, lane-bound measurement, colocated/plain precondition
— the r17 section does carry the colocated/plain caveat at :217,:233). No row
declares F2 closed.

Fleet figure: clean. Both entries explicitly disclaim ("No fleet figure. This lane
holds no measured fleet `garbage` census…" / "No fleet repository was censused for
this entry"); the only numbers present are the gc.auto 6700 default, fetch byte
counts, and sha256 digests — none is a fleet size figure. The staged package's
own-work fleet census row is rejected in the r25 Gate ("evidence lives outside
this repository"), matching README.md:481–482.

----------------------------------------------------------------------
RESOLVED-at-tip (was false when first reviewed)
----------------------------------------------------------------------
- `snapshotted under … with sha256` (README.md:479): at 1026900 no digest for the
  five snapshots existed anywhere (grep for the computed digests → nothing). Tip
  commits `census/round-23/sources/SHA256SUMS`; `sha256sum -c` verifies all five
  (qiita-gc-auto.raw was also re-extracted — digest 7d2298c1→3274d936). Now true.
- C1 after value: at 1026900 the only after receipt (`agreement-after.tsv`) recorded
  rc=1 mismatches=1 at 4765250, contradicting the cell; regenerated at tip with
  rc=0 mismatches=0, verify=ok.

----------------------------------------------------------------------
WHAT SURVIVES (re-verified at 466f539, commands quoted)
----------------------------------------------------------------------
- C2 row: `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → 5 (before: 0,
  `git grep -cE … 1208bfb -- census/` → no match). All five `verify=ok`; every
  receipt rev is an ancestor of master (9301d98, a211e4d, 1208bfb, 4765250,
  3b72bea — all durable). Digest refusal fires: substituting the r22 stale digest
  into a receipt gives `RECEIPT-TOOL-DIGEST-MISMATCH`, rc 2 — matching
  `census/round-23/records/refusal-stale-digest.txt`. Disclosed limit confirmed: a
  receipt with altered stdout but intact digest passes `verify=ok` (typed receipt).
  One receipt (`agreement-control-base.txt`) uses `tool-digest=` not `tool_sha256=`
  and is excluded from the count; its file is also not a v1 receipt
  (`RECEIPT-MALFORMED` under verify) — disclosed in its own note; acceptable, but
  worth one line since the README calls it "the do-nothing control" receipt.
- C3 counters: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
  → exit 0 (W04 duplicate-URL warnings only, no E-codes); gate-check →
  `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`; registry rows 114 → 119,
  S115–S119 all present once, resolving to the two entries.
- C1 direction: base `mismatches=6` (K4-off) / `29` (K4-on mid-round) → tip
  `mismatches=0` (`--no-worktree`, rc 0) — survives; the instrument is the
  contract and every mismatch class has a covering repair.
- Corrections section: the in-place tally fix (:440 now "2 present, 0 refused")
  matches `census/round-22/attempt2/slice-verdicts.tsv`; LOG.md "Round22 attempt2
  corrections" names both superseded cells with numbers, as :499–500 says, and the
  filed occurrence survives — verified against LOG.md:1524–1548.

----------------------------------------------------------------------
RESIDUAL RISK / VERIFICATION GAPS
----------------------------------------------------------------------
- The lane tip and worktree moved continuously during review (six tips observed;
  peers landing wave-2 fixes and writing seat reports). Numbers above are pinned
  to 466f539; the frozen C1 command is inherently unstable by K4 design, so any
  value quoted for it (including the cell's `0`) is a momentary reading unless the
  `--no-worktree` arm is named. This instability is the substance of F2.
- K4's live-worktree arm cannot stay 0 while wave seats write `.ufo/waves/**`;
  at tip it reports the seat reports themselves. Whether `.ufo/` should be inside
  K4's "round work" scope is a design question the round may accept (it is the
  frozen contract), but README.md:465's phrasing "K4 no uncommitted round work
  outside the exemptions" is only true of the K4-off arm.
- Community pages were not re-fetched live here; their extract claims were
  checked through gate-check's quote-absent-from-snapshot test (ok=2) and
  SHA256SUMS, not against today's pages.
- The `agreement-after.tsv` receipt binds rev 3b72bea (a strict ancestor of tip,
  not the tip itself) — the "landing tip" wording in SCORECARD/LOG is loose by
  one commit; the K1–K3 content it measures is unchanged between them (tool
  digest identical, occurrences identical). ACCEPT-or-clarify, not a defect.
