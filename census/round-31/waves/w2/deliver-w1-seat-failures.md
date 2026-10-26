# deliver-w1-seat-failures — round-31 wave-2 seat-failure carry

Seat SwarmScribe31 (scribe, leaf member), round 31 attempt 1, wave 2. Lane
`/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`;
preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; lane tip at every reading below
`2c16d018e40db7c23420a2c3bb546b52957bcc25`. No lane file was written or mutated by this seat;
the counters run here are the lane's own committed instruments, run serially.

## Land this — the only lane bytes in this delivery

Append the block between the two markers to the end of `corpus/lessons/round-31.md` (create the
file if it does not exist; the section is self-contained and needs no other lesson content).
Nothing else in this delivery is lane content.

<<<SECTION-START
## Seat-reported failures

Appended in round 31 (wave 2, SwarmScribe31); covers the wave-1 seat reports only. Detection is the landing gate's own channel: `seat_failure_lines` from `tools/souji-landing-gate.py` run over the bytes of `.ufo/waves/round-31/w1/Swarm*.md` at lane tip `2c16d018e40db7c23420a2c3bb546b52957bcc25` yields 7 failure STATUS lines over 38 reports (31 PASS, 1 FAIL, 6 PARTIAL); `checked_markers=7`, `carry_heading=0`, `findings=7 LG-SEAT-UNCARRIED` before this section is appended. Each bullet quotes one report's STATUS paragraph normalized exactly as the gate normalizes it (NFC, `*` and backticks dropped, whitespace collapsed) and carries one disposition: `open` where the stated defect or gap still stands at lane tip, or `resolved@<full 40-hex>` where a lane commit between base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` and tip demonstrably discharged it. The basis for every disposition is recorded in the wave-2 scribe delivery for this round; this section names no uncommitted path. Land it at or after the commit that carries the wave-1 capture under `census/round-31/waves/`: every report path below resolves through that capture mapping.

- `.ufo/waves/round-31/w1/SwarmCritic29.md` line 4 — open: STATUS: FAIL — the frozen C2 target is reached with rc=0 by two gates that read nothing (base-revision replay; 13-token allowlist), and the required prose / .captured / multi-section rules each hide a real defect; every reproduction is below.

- `.ufo/waves/round-31/w1/SwarmExecutor04.md` line 5 — open: STATUS: PARTIAL — 8 of 9 assigned items (L21-L28) are honestly bound and read MATCH twice at the proof revision; L29 has no honest binding under the frozen C1 record rule (its named record states the count as scalar fields, never as a two-integer literal), so unbound=1 remains and I did not force a row.

- `.ufo/waves/round-31/w1/SwarmExecutor06.md` line 5 — resolved@8024b540b04d677d47cf51a0d1132ec8705ef14a: STATUS: PARTIAL — the tool is implemented and delivered, and the C2 LANE leg reads the frozen target at base content (fp=0 real=2 cne=0 r26=495), with regress=same and every preserved fixture unchanged; the remaining C2 legs (FIXTURE, REDARM) are unmeasurable from my scratch commit because tests/fixtures/r31-landing-gate-precision.py is not committed yet (the counter reports FIXTURE absent fail / REDARM absent fail, exactly as this item predicted until the fixture seat lands it).

- `.ufo/waves/round-31/w1/SwarmReviewer25.md` line 4 — open: STATUS: PARTIAL — targets, controls, kill rules and axis/surface mapping are consistent (axis-check claims=3 flags=0), all three targets are unreachable by the do-nothing and junk controls, and C3 is genuine coverage (F1 frontier edge class). Two claim-sizing defects and one prose inconsistency: C2's universal clause "every ## Seat-reported failures section" is not enumerated by the counting command on the corpus (only synthetic fixture G3/G10 exercise it); C1's prose "23 literals have no observable beside them at all" disagrees with the frozen counter's base unbound=22; and C1's run-binding rows may restate an enumerated literal, so the clause "bound to an observable that shows it" is weaker than the text.

- `.ufo/waves/round-31/w1/SwarmReviewer26.md` line 4 — open: STATUS: PARTIAL — 6 junk states built and scored against the frozen counters (C1 x3, C2 x3 incl. the amended v2); one planned C3 state (fabricated provenance, J6c) designed but unrun within the L1's window. Headline: a C2 junk state (J5c-v4, rev 06d2e79ddd5dfa3c2e118404d9116124e11d84b1 in scratch) passes the AMENDED v2 counter with exit 0 — fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok — with no real tokenizer and a fixture that never executes the gate.

- `.ufo/waves/round-31/w1/SwarmScribe23.md` line 5 — resolved@1baf4da02b71b012ee2426ea7c309496c0c3aca0: STATUS: PARTIAL — all five requested skeleton blocks were delivered as fill-in placeholders; PASS is impossible for a skeleton seat because every after-value belongs to data the L1 has not yet produced (C3's entry is absent at the measured revision).

- `.ufo/waves/round-31/w1/SwarmSimplifier38.md` line 4 — open: STATUS: PARTIAL — five of six enumerated checks pass on the rendered plan (38 distinct seats and prompts, allowed roles only, flash 26/38 = 68.4 %, attack 10/38 = 26.3 %, every scratch path under /fast/scratch/hyaku/souji-r31/, no deliverable claimed by two items); the absolute-path/write-scope check fails for three items (C2Fixture, C3Fixture, C2Gate), and one cross-item landing gap (C3Snapshots vs EntryDraft) leaves the C3 snapshot/receipt record self-inconsistent until the L1 renames on landing.
SECTION-END>>>

The section is 17 lines: one `## Seat-reported failures` heading, a six-line preamble that cites
no uncommitted path, and seven bullets — one per failure STATUS line, quote first after the
disposition, exactly as the assignment prescribes (`- `.ufo/waves/round-31/w1/<file>` line <n> —
<disposition>: <normalized STATUS paragraph>`). Every quote is `tools/souji-landing-gate.py`'s own
`norm_line()` of the report's STATUS paragraph, emitted by a generator that reads the committed
bytes, so no transcription step exists to break the carry predicate.

## Detection — re-derived this run

`seat_failure_lines` (the gate's failure channel: a `STATUS:` line outside fences and table rows
whose first value word is in the failure vocabulary) imported from
`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` with
`python3 -B -c` over the 38 files matching `.ufo/waves/round-31/w1/Swarm*.md` yields exactly 7
failure lines in 7 distinct reports:

| report | line | first value word |
|---|---|---|
| SwarmCritic29.md | 4 | FAIL |
| SwarmExecutor04.md | 5 | PARTIAL |
| SwarmExecutor06.md | 5 | PARTIAL |
| SwarmReviewer25.md | 4 | PARTIAL |
| SwarmReviewer26.md | 4 | PARTIAL |
| SwarmScribe23.md | 5 | PARTIAL |
| SwarmSimplifier38.md | 4 | PARTIAL |

Status vocabulary over all 38 reports: 31 `pass`, 1 `fail`, 6 `partial` — 38 STATUS lines, one per
report, so the 7 hits are exactly the non-PASS lines and no report hides a second STATUS line.
Basis-control for the vocabulary: none of the 31 PASS lines is in the failure set and none of the
7 is missing from it.

Red before (gate at the lane tip, no round-31 lesson):
`python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25
--round 31 --fleet-root /home/vgpnk/Projects/shokunin` prints 7 `LG-SEAT-UNCARRIED` lines (one per
report above) and
`SUMMARY findings=7 checked_reg=63 checked_changed=0 checked_pins=13 checked_measured=3
checked_markers=7 status_lines=39 carry_heading=0 checked_reports=60`.
Without `--fleet-root` the same run adds 3 `LG-DANGLING-PTR` lines for the fleet-only
`../.ufo/waves/hyaku/jj-w1/...` pointers in `corpus/README.md:217` and
`corpus/knowledge/jj-colocation-receipts.md:148`; they are fleet paths, not round-31 findings.

## Disposition basis

Rule used: `resolved@<full 40-hex>` only where a lane commit in
`9f17a1e..2c16d018e40db7c23420a2c3bb546b52957bcc25` demonstrably discharged every defect the
report's STATUS paragraph asserts, and the discharge still reads at the tip; `open` otherwise. A
report whose paragraph asserts several defects gets `open` if any one still stands.

### SwarmCritic29.md line 4 — open
8 findings. Closed by later commits: finding 1 (base-revision replay) and finding 3 (13-token
allowlist) are the two cheats amendment A3's SHIFT leg was built against
(`26153a421374db2497e451230f33b2af78b3d128`, `census/round-31/c2-counter-v2.py:33`), and finding 7
(heading inside a fenced block) is the gate patch logged inside the same amendment. Still standing
at the tip: finding 2 (the FIXTURE leg reads only the fixture's printed verdicts — the counter runs
the fixture and greps `cases=/pass=/control=` lines, `census/round-31/c2-counter.py:134-150`; A3
discloses "the fixture leg trusts the fixture's own verdict lines"), findings 4-5 (the prose and
`.captured` blind spots are disclosed and contracted in A3, not fixed), finding 6 (`r26=495` still
mandates counting the 384 non-report markdown files), finding 8 (the LANE leg still never scores
the tool's exit status: `census/round-31/c2-counter-v2.py:197` and `-v3.py:211` gate on
`fp/real/cne/r26/fixture/redarm/same/shift` only, and `SHIFT`'s own `sok`
(`-v2.py:192`) is `got == want and no COULD-NOT-EVALUATE`).

### SwarmExecutor04.md line 5 — open
The seat's PARTIAL is confirmed at the tip, not answered: my run of the current counter,
`python3 -B tools/souji-capability-cells.py --root <lane> --rev
2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
--list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, with `rc=1`, prints
`ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND` and
`SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`. The landed block holds 40
`| L` rows and no `| L29` row, and amendment A4's pre-landing reading recorded the same miss. C1's
frozen target `unbound=0 mismatches=0` is therefore missed by one item, exactly as this seat said.

### SwarmExecutor06.md line 5 — resolved@8024b540b04d677d47cf51a0d1132ec8705ef14a
The paragraph's only defect is that the FIXTURE and REDARM legs were unmeasurable because
`tests/fixtures/r31-landing-gate-precision.py` was not committed. It is committed in the C2
landing (`git cat-file -e 8024b540b04d677d47cf51a0d1132ec8705ef14a:tests/fixtures/r31-landing-gate-precision.py`
exits 0), the lane receipt `census/round-31/records/c2-after-v3.txt` reads
`FIXTURE ... ok` / `REDARM ... ok` at that exact revision, and my own run of the fixture at the
tip against the landed gate ends `cases=10 pass=10 control=FALSE-GREEN-REJECTED` (`rc=0`) with all
ten case verdicts PASS. The fixture's independence from the tool is a different, still-open item
(Critic29 finding 2 / Reviewer26 below), not part of this seat's paragraph.

### SwarmReviewer25.md line 4 — open
Three assertions. Finding 3 (prose "23" vs counter `unbound=22`) was corrected in amendment A4
(`6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3`, "Prereg prose correction ... should read 22").
Findings 1 and 2 stand at the tip: the counting command's SUMMARY carries no
`LG-SEAT-UNCARRIED` or section-count field at all (`fp real cne r26 fixture redarm regress` plus
`shift` in `census/round-31/c2-counter-v3.py`), so "every `## Seat-reported failures` section" is
still exercised only by the synthetic fixture cases G3/G10, and the claim sentence "bound to an
observable that shows it" is still weaker than the counter's effective-statement rule (A2 records
the disagreement as the claim's reading; A4 leaves it).

### SwarmReviewer26.md line 4 — open
Assertions: (a) J5c-v4 passes the amended v2 counter; (b) one planned C3 junk state (J6c) is
designed but unrun; (c) the passing junk state had "no real tokenizer and a fixture that never
executes the gate". (a) is answered by amendment A5 at the tip
(`2c16d018e40db7c23420a2c3bb546b52957bcc25`, `census/round-31/c2-counter-v3.py`, probes drawn at
random per run; `census/round-31/records/c2-after-v3.txt` shows two passing runs at the C2 landing
commit and a failing base-gate control). (b) still stands — A5 discloses J6c as "designed but
unrun" and wave 2 is expected to re-fetch every source. (c) still stands — see the FIXTURE-leg
disclosure cited under Critic29. Two of three unanswered keeps the disposition `open`.

### SwarmScribe23.md line 5 — resolved@1baf4da02b71b012ee2426ea7c309496c0c3aca0
The paragraph's PASS-blocking condition is that the C3 entry is absent at the measured revision
and every after-value is data the L1 had not yet produced. The C3 landing carries
`corpus/knowledge/jj-dropped-keep-object-lifetime.md`
(`git cat-file -e 1baf4da0...:corpus/knowledge/jj-dropped-keep-object-lifetime.md` exits 0), and my
own re-run of the frozen v1 counter at that revision,
`python3 -B census/round-31/c3-counter.py --root <lane> --rev
1baf4da02b71b012ee2426ea7c309496c0c3aca0 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`,
prints `L1 PASS f1_entries=4`, `L4 PASS snapshots=3 bad=[]`, `L8 PASS run_record=present
results=17`, `L9 PASS replays=[(0, 17, True), (0, 17, True)]` and
`SUMMARY legs=11 fail=0 f1_entries=4`, `rc=0`. C1 and C2 landed after it, so the skeleton's other
after-values exist too; the skeleton content itself is the seat's own deliverable, not a defect.

### SwarmSimplifier38.md line 4 — open
Two assertions: (a) the absolute-path/write-scope check fails for three plan items (`C2Fixture`,
`C3Fixture`, `C2Gate`); (b) the `C3Snapshots`/`EntryDraft` gap leaves the C3 snapshot/receipt
record self-inconsistent "until the L1 renames on landing". (b) was discharged at the C3 landing:
snapshots are committed at `census/round-31/sources/{SHA256SUMS,gc.adoc,git-compatibility.md,git-reflog.adoc}`
and the receipts at `census/round-31/records/fetch-receipts.tsv`, which is what the frozen counter
reads (`census/round-31/c3-counter.py:17-19`), and my re-run reads `L4 PASS snapshots=3 bad=[]`.
(a) still stands: the plan is committed as captured bytes
(`census/round-31/waves/w1-dispatch.json`) and still carries the three flagged strings — task 5
(`SwarmExecutor06`) "Implement C2 in the landing gate /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py",
task 6 (`SwarmExecutor07`) "Write the frozen C2 fixture tests/fixtures/r31-landing-gate-precision.py",
task 7 (`SwarmExecutor08`) "Write tests/fixtures/r31-jj-object-clock.sh" — and no commit in
`9f17a1e..2c16d018` edits that file (it enters the tree only with the wave-1 capture at the tip).
Disclosed, not a discharge: the wave-2 plan does not repeat the class — searching the committed
`census/round-31/waves/w2-dispatch.json` (36 tasks) for those four phrasings returns 0 hits, so
`make-spec-w2.py`, committed at the tip, renders absolute write targets. The wave-1 bytes the seat
measured are unchanged, no seat actually wrote outside the lane, and the finding is plan text: it
harms no axis at landing but is not answered in the bytes that carry it.

## Verification of this section

Clone `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe31/c` (`git clone -q --no-local`, `origin`
removed, `rev-parse --show-toplevel` verified, throwaway identity in the clone only), HEAD
`2c16d018e40db7c23420a2c3bb546b52957bcc25`, then:

1. `corpus/lessons/round-31.md` = a short scratch header + this section; commit `02fecb1`; the gate
   at that rev with `--fleet-root /home/vgpnk/Projects/shokunin` prints
   `SUMMARY findings=0 checked_reg=63 checked_changed=0 checked_pins=13 checked_measured=3
   checked_markers=7 status_lines=39 carry_heading=1 checked_reports=60` and `rc=0`. Zero
   `LG-SEAT-UNCARRIED`, zero `LG-DANGLING-PTR`.
2. Negative control: the same file with the SwarmReviewer26 bullet deleted, committed, reads
   `findings=1`, one `LG-SEAT-UNCARRIED` naming `census/round-31/waves/w1/SwarmReviewer26.md` line
   4. The section is load-bearing and each bullet carries exactly its own report.
3. The scratch clone reads the committed wave-1 capture under `census/round-31/waves/w1/`. All 38
   `.ufo/waves/round-31/w1/Swarm*.md` files are byte-identical to
   `census/round-31/waves/w1/<same name>` (sha256 of every pair equal), so the union reading the
   final-tip gate performs on the wave dir resolves to the same bytes.

## Landing notes for the L1

1. Land the section at or after the commit that carries `census/round-31/waves/`; the bullets cite
   `.ufo/waves/round-31/w1/<file>` and the gate resolves those pointers only through the capture
   mapping. A first draft of this section cited the wave-2 delivery path; the gate flagged it
   `LG-DANGLING-PTR` because `.ufo/waves/round-31/w2/` has no committed blob, so that citation was
   removed and the preamble names no uncommitted path.
2. This section covers wave 1 only. At read time (13 `Swarm*.md` in `.ufo/waves/round-31/w2/`)
   three wave-2 reports already carry failure STATUS lines — `SwarmCritic18.md` line 5,
   `SwarmCritic21.md` line 9, `SwarmScout19.md` line 4, all PARTIAL. They need their own carry in
   the same section (or a second `## Seat-reported failures` section, which the tip gate reads) or
   the final-tip gate will report them `LG-SEAT-UNCARRIED`.
3. The dispositions are checkable one by one: `open` bullets are reread by the wave-2 reviewers for
   this round; each `resolved@` names a commit whose artifact and reading are cited above.
