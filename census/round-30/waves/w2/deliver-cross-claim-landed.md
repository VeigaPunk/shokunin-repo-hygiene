# deliver-cross-claim-landed — souji round 30, wave 2 (seat SwarmConnector30)

Cross-claim map over the landed range `d4928ec..9dcd367`, verified by live re-runs of every frozen
counter at the landed commits. Extends wave-1 `census/round-30/waves/w1/deliver-cross-claim.md`
(sections 1–8 there) with post-landing measurements. All receipts in this directory named
`receipt-SwarmConnector30-*.txt`. Lane Python run with `python3 -B` on private clones (origin
removed), TMPDIR under `/fast/scratch/hyaku/souji-r30/SwarmConnector30` (scratch since removed).

## 1. C1 bytes read by C2's gate — landing-commit MISS reproduced; r29-D1 class recurred

The gate's citation scan (tools/souji-landing-gate.py@68447af, sources block) reads
`SKILL.md, SHONEN.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md, corpus/README.md`,
`corpus/lessons/round-<N>.md`, the round's verifier-spotcheck lesson, and every
`corpus/knowledge/*.md`. C1's landed SCORECARD block (7b16731) cites inside that set:

- `SCORECARD.md:322`@68447af: "Literal provenance per row: `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`"
  (19 words, bytes opened this run via `git show 68447af:SCORECARD.md`).

`.ufo/waves/round-N/` tokens resolve only through the committed capture `census/round-N/waves/`
(`CAPTURE_POINTER_RE`), which did not exist until the wave-1 capture commit aea0525 — one commit
after C2's landing commit 68447af. Re-runs:

- `c2-counter.py v1` at 68447af → `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same` (rc 1). Receipt: `receipt-SwarmConnector30-c2v1-68447af.txt`. The frozen kill rule (`dangling=0` at the landing commit) is missed; L1 reading reproduced byte-for-byte. `other=7` are the pre-carry LG-SEAT-UNCARRIED findings (section 6).
- `c2-counter.py v1` at tip 9dcd367 → `dangling=0 other=0` (rc 0). Receipt: `receipt-SwarmConnector30-c2v1-tip.txt`. Resolved at the capture commit, as the L1 recorded.

Mistake-class recurrence: r29 routed D1 ("cite only committed evidence") — C1's landed claim text
cited wave bytes committed nowhere at 7b16731 (gitignored `.ufo`, capture not yet run), and the
first instrument to read those bytes was C2's own gate, which scored the citation as
LG-DANGLING-PTR at C2's landing commit. Cross-claim commit-order race: C1 → C2(landing) → capture.

## 2. A1 v2 counter defect reproduced — strip_err tab-vs-space; v2 target unreachable

`census/round-30/c2-counter-v2.py@68447af` (`strip_err`): "re.sub(r"\terr=.*$", "", l) if
l.startswith("CASE\t")" — requires a TAB before `err=`. The gate's selftest CASE detail
(`tools/souji-landing-gate.py:1423`@68447af) is: "detail = "exit=%d ids=%s paths=%s fleet=%s err=%s""
— `err=` is SPACE-separated inside the detail field, so `strip_err` never strips it.

Re-runs: v2 at 68447af and at tip 9dcd367 both print
`SUMMARY-V2 ... bind=.. nocap=.. ptrarm=.. fixture=ok redarm=ok regress_full=differs`
(receipts `receipt-SwarmConnector30-c2v2-68447af.txt`, `receipt-SwarmConnector30-c2v2-tip.txt`;
at the tip every other leg is ok, so `regress_full=differs` is the sole failing leg).
Normalized selftest diff (BASE 9420341 vs REV 68447af, receipts
`receipt-SwarmConnector30-selftest-{base,rev}.txt`): exactly 2 of 66 lines differ, both CASE lines
whose `err=` tail carries the reworded no-reports message C2 was explicitly allowed to change —
e.g. BASE "err=no .md reports under .ufo/waves/round-18/ at" vs REV
"err=no .md reports under .ufo/waves/round-18/ or census/round-18/waves/ at". A space-tolerant
strip (` err=.*$`) makes the outputs identical (verified this run). The frozen A1 target
`regress_full=same` is therefore unreachable for the true C2 gate at any revision; the defect is
in the frozen counter, reportable only as an ATTACK, not fixable post-amendment.

## 3. C1 instrument chain is environment-sensitive — NEW mistake class (calibration axis)

Frozen v1 blob (d4928ec) at 7b16731, run three ways this run:

- Solo → `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10` (rc 0). Receipt:
  `receipt-SwarmConnector30-c1v1-solo.txt`. Reproduces the L1 reading (c1-after-v1.txt).
- Two concurrent counter processes (my own v1 and A3 runs launched together) → BOTH score
  `R14 rc=1 observed=selftest=13/15 MISMATCH kind=rc`, `k1=1 mismatches=1`. Receipt:
  `receipt-SwarmConnector30-c1v1-concurrent.txt`.
- Direct two-process race probe: two concurrent `tests/fixtures/r23-record-agreement.py` runs both
  crash "RuntimeError(f"git {' '.join(args)} failed: ...")" — receipts
  `receipt-SwarmConnector30-race-{a,b}.txt`.

Root cause: the R14 fixture hard-codes a shared root — `tests/fixtures/r23-record-agreement.py:67`
(7b16731): "SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"" — and rmtrees it at exit
(`:105`: "shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)"). Two overlapping executions delete
each other's synthetic repos mid-case; the verdict flips (15/15 → 13/15 → crash) with timing.
The other row fixtures are collision-safe: r12/r13 use `mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX`
/ `souji-r13-repo-structure.XXXXXX`; r28 uses `mktemp -d "$scratch_root/run.XXXXXX"`; r29 and the
gate/r16 use uniquified `tempfile.mkdtemp`. Only R14 (r23-record-agreement) is genuinely racy.
Wave-2 seats are instructed to attack the same counters concurrently, so any un-serialized k1
reading is unreliable in both directions: a concurrent run can fabricate a MISS (as it did here),
and a solo run can hide one. The L1's solo "C1 met" reading stands, but robustness of the frozen
instrument chain does not.

## 4. C3 bytes read by C2's gate — clean

C3's landing (76c94eb) edited PROVINCE.md, SKILL.md, corpus/README.md, corpus/SOURCES.md and added
`corpus/knowledge/jj-keep-ref-expiry.md` — all inside the gate's citation-scan set. Every
`.ufo/waves` token in those files is historical (round-14/17/20/24) or capture-resolving; the
committed M1 receipt (`census/round-30/records/m1-r29-carry-red-before.txt`@9dcd367) shows the gate
at 76c94eb printing only the 7 LG-SEAT-UNCARRIED findings (no LG-DANGLING-PTR), and my v1/v2 C2
re-runs at the tip show `dangling=0`. C3's own fixture is TMPDIR-disciplined with a lane-path
refusal guard (`tests/fixtures/r30-jj-keep-expiry.sh:29-33`@76c94eb: "TMPDIR is unset or empty;
refusing to run").

## 5. C3 rows vs the C1 counter — clean both directions

C1's enumerated set (c1-rows.tsv@d4928ec) reads only SCORECARD.md, SHONEN.md and the frozen row
list; C3's SOURCES rows (S220/S221, used-by on S054/S063) cannot enter it. The one instrument that
does read SOURCES used-by agreement is row R17 (`tests/fixtures/r29-registry-agreement.py`): my
solo v1 run at the tip scores `R17 ... cases=20 pass=20 control=FALSE-GREEN-REJECTED MATCH` and
`SUMMARY k1=0 k2=0 mismatches=0` (receipt `receipt-SwarmConnector30-c1v1-tip.txt`) — C3's
committed edits are registry-consistent. C1's landing measurement (rev 7b16731) predates C3, and
SCORECARD/SHONEN are untouched after 7b16731, so the causal-separability clause holds.

## 6. r29 lesson carry (936efc8) vs the r29 gate — verified

Committed receipt (`census/round-30/records/m1-r29-carry-red-before.txt`@9dcd367): gate `--round 29`
at 76c94eb → 7× LG-SEAT-UNCARRIED, `carry_heading=0`, rc 1; at 936efc8 → `findings=0`,
`carry_heading=1`, rc 0. The r30 lesson append is read by the r29 gate (r29 lesson is in the scan
set for `--round 29`), so the append is itself a cross-claim byte surface; it introduces no new
pointers and its carry-wrap passed (findings=0). Verbatim spot-check this run: carried
`census/round-29/waves/w1/SwarmCritic49.md` line 5 quote equals the committed bytes at
df6afe817d096e4ad71ba2b9cc21a83f126eb658: "STATUS: PARTIAL — the claim is real but its
instrumentation is not: a restatement pair reaches every".

## 7. Mistake-class recurrence (corpus/lessons/round-2[5-9].md `## Mistakes` → round 30)

| class (origin) | round-30 recurrence | status |
|---|---|---|
| vacuous counter / K2-empty-marker (r29) | wave-1: no-op gate + byte-recognising fixture (Critic25), `python3 -c pass` row bypass (Critic24) | addressed pre-landing by A1–A3 + controls-amended (02aea48); NEW residual: A1 strip_err tab/space defect (section 2) |
| number-drift (r25, r29) | none observed: BIND pins `reports=86` to the committed census/round-29/waves count, verified `reports=86 expected=86` at 68447af and tip | not recurring |
| stale-premise / cross-instrument disagreement (r28) | recurs as the C1→C2 commit-order race (section 1): C1's citation uncommitted at C2's landing commit vs the gate reading committed bytes | recurring, new shape |
| attribution — self-ruled miss (r29) | corrected pattern: L1 recorded the C2 landing-commit MISS honestly; C2 v1 meets the target at the tip | not recurring |
| scope — clone origin push (r29) | r30 wave contracts mandate `remote remove origin` immediately after clone | fix carried, not recurring |
| r29 routed D1 "cite only committed evidence" | RECURRED: C1's landed SCORECARD cites `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`, committed nowhere until aea0525; first reader was C2's gate scoring it dangling | recurring, material (caused the C2 landing-commit MISS) |
| environment-sensitivity / shared-path race (new) | C1 chain: r23 fixture fixed `/var/tmp` SCRATCH_ROOT flips R14 under concurrent execution (solo k1=0 → concurrent k1=1, race-crash proven) | NEW this round |

## 8. Axis impact

- calibration (7, lowest): harmed unless counter readings are serialized — the frozen C1 instrument
  chain is non-deterministic under concurrent host activity (section 3). The landing verdicts
  themselves are unaffected when run solo. Also carries the C2 landing-commit MISS attribution (operability).
- operability (8): the A1 v2 target is unreachable for the true gate (section 2); the frozen v1
  target is met at the tip and missed only at the sandwiched landing commit (section 1).
- coverage (8): unaffected; C3 v1/v2 reproduced green (receipts
  `receipt-SwarmConnector30-c3v1.txt` `legs=9 fail=0 f1_entries=3`;
  `receipt-SwarmConnector30-c3v2.txt` `e1=ok e2=ok e3=ok e4=ok f1_exact=3`).

## 9. Proposed move (one, bounded)

Mine three mistakes into `corpus/lessons/round-30.md` `## Mistakes` when the L1 writes it (the
frontier step's planned single candidate already covers the uncarried r29 failures; these three
are independent, evidenced, and within the hygiene lane): (a) cross-claim commit-order race +
r29-D1 recurrence — a claim's landed text cited bytes committed only by a later commit, and the
next claim's gate scored it (red-before: `receipt-SwarmConnector30-c2v1-68447af.txt`); (b) C1
chain shared `/var/tmp` root — concurrent counter runs flip R14 (red-before/after:
solo vs concurrent receipts, race-crash receipts); (c) A1 `strip_err` tab/space counter defect —
frozen counter cannot print `regress_full=same` for the true gate (diff receipts). No counter,
predicate or target is changed; readings only. Verification: the receipts named above, all
committed into `.ufo/waves/round-30/w2/`.
