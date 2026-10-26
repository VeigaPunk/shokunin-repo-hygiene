# Cross-claim analysis — souji round 31 wave 1 (SwarmConnector36)

Scope: where C1, C2, C3 and M1 touch the same bytes or assumptions, plus recurring mistake
classes from corpus/lessons/round-2[6-9].md and round-30.md. Read-only seat; lane base
9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525.
All claims below were observed this run (commands in SwarmConnector36.md ## Evidence).

## A. C1 appended rows vs the round's own SCORECARD measurement rows — mis-parse hazard is real but shape-specific

The C1 counter (tools/souji-capability-cells.py) defines an item's effective statement as
"the LAST row, in the part of SCORECARD.md after the --base bytes, of the form"
`| <id> | SCORECARD.md:<line> | <literal> | run: <argv> |` / `| <id> | SCORECARD.md:<line> | <literal> | record: <path> |`.
The tail scan is line-based with no table-context awareness: ROW matches any line in the append
tail, and `sup[id]` is overwritten per match, so LAST match wins for each item id.

Consequences:
1. A later `| Lnn |`-shaped row in ANY appended table — including a per-item measurement table a
   wave-2 seat or the L1 appends to record after-values — silently supersedes an earlier correct
   binding row. If that measurement row re-states the base command (e.g. L06 bound to
   `tools/souji-landing-gate.py --selftest`, which prints `SELFTEST pass=65 fail=0`, never
   `18/18`), the item flips to RUN-MISMATCH and C1 misses AT THE TIP even though the binding
   row was correct. A measurement row with a wrong line number becomes BAD-ROW (line-or-literal).
2. What is safe today: base SCORECARD.md contains zero `| L\d{2} | SCORECARD.md:<n> |` rows
   (grepped at HEAD); R30-CORRECTION lines are space-separated
   (`R30-CORRECTION SCORECARD.md:154 R03 rc=0 observed=...`) and do not match ROW — confirmed
   the "R30-CORRECTION lines do not count" rule is structural, not conventional; the r30/r31
   capability-row tables put the capability name in cell 1, so they cannot match.
3. Mitigation (L1 integration order): make the 41 C1 binding rows the last Lnn-shaped rows in
   SCORECARD.md, or keep any measurement table's first two cells distinct (e.g. `| item | base line |`).

## B. SCORECARD.md is a landing-gate pointer source — C1 rows live inside C2's scanner

check_pointers (tools/souji-landing-gate.py:962-971) scans SCORECARD.md on every round
evaluation. C1's appended rows put `tools/...`, `tests/fixtures/...` and `census/round-<K>/...`
tokens into that file; the run/record shape rules guarantee those paths are committed at the tip,
so the rows themselves are clean. The hazard is the NOTE cell: any `.ufo/waves/round-31/...`
token cited there dangles at every commit until the wave capture lands — this is exactly the
r30 reference-drift mistake ("cites the wave path `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`",
corpus/lessons/round-30.md ## Mistakes), and SCORECARD.md was the file that sank it. The C2 LANE
leg reads content at BASE, so C1 rows cannot move the frozen fp=0 leg; the exposure is the tip
gate and the landing-gate-per-commit process receipt. C1 row authors: cite only committed paths
(`census/round-K/records/...` or `.ufo/waves/round-K/...` with the capture already committed).

## C. C2's gate vs C1 items L06/L07/L40 — the one live axis-harm path

Measured with the frozen C1 counter at rev=base (per-item ITEM lines, census/round-31/records/c1-before.txt agrees):

- L06 (`SCORECARD.md:158`, `18/18`, basecmd `python3 tools/souji-landing-gate.py --selftest`):
  already RUN-MISMATCH at base — observed `SELFTEST pass=65 fail=0`. C2's REGRESS leg pins
  `--selftest` (rc, last digit-bearing line) equal between base and rev, so the selftest last
  line can never change to contain `18/18`. C1 MUST supersede L06 with an appended row; nothing
  C2 does can rescue the base binding.
- L07 (`SCORECARD.md:158`, `15/15`, basecmd `python3 tests/fixtures/r16-landing-gate.py`):
  already RUN-MISMATCH at base — observed `SUMMARY total=15 failed=0`. Same conclusion: C1 must
  supersede; C2 must keep the r16 fixture's 15 synthetic cases green under the changed gate or
  REGRESS prints differs (C2 miss) — the r16 fixture drives the gate on its own worlds, so any
  behavior change on single-section carries/standard pointers shows up there.
- L40 (`SCORECARD.md:355`, `cases=7 pass=7`, basecmd
  `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py`):
  MATCH at base. This is the coupling: if C2's fix breaks any of the r30 fixture's D1-D7 cases,
  REGRESS differs (C2 miss) AND L40's binding flips to RUN-MISMATCH at the tip with C1 unchanged —
  C1 misses through C2's edit. The binding constraint set is exactly D3-vs-G1/G2:
  D3 pins "both present, same relative report path, different bytes. The capture copy carries no
  STATUS line" → checked_reports=1, status_lines=1 (read the .ufo bytes); G1 pins the union
  (distinct capture-only relpaths counted, checked_reports=2); G2 pins dedupe of identical bytes.
  The unique implementation satisfying all three: union keyed by relative path, .ufo bytes
  preferred, capture bytes only for relpaths absent from the wave tree. A plain concatenation
  fails D3; wave-tree-wins-only fails G1.

## D. M1 carry sections vs C2's multi-section rule and the tip gate

- Lessons round-2{6,7,8}.md carry no `## Seat-reported failures` heading at base (heading lists
  verified). M1 appends ONE section at the end of each; the base first-section reader
  (failures_section_lines stops at the next heading after the first match) sees it, because it is
  the only section. So M1's own green state is verifiable with the BASE tool — no hard sequencing
  dependency on C2 for M1's claim.
- Denominator effect of C2's union fix on M1's rounds: round 26 checked_reports rises 466 → 495
  (verified: 466 force-added .ufo + 495 census .md − 466 overlapping relpaths = 495 distinct).
  I scanned all 29 capture-only round-26 reports for the gate's failure vocabulary: zero STATUS
  failure lines. So the union adds no new uncarried markers to round 26; rounds 27/28 are
  capture-only trees (ufo=0; census=94/61 — union inert there). M1's carry lists sized against
  the red-before receipt (18/29/19 UNCARRIED, census/round-31/records/m1-red-before.txt) stay
  sufficient at the tip.
- The 2 LG-DANGLING-PTR in round 28 (round-28-verifier-spotcheck.md:36,71 — extensionless
  `corpus/knowledge/registry` and a `.gitignore:fixture/` capture-name form) belong to C2's
  tokenizer classes (G8/G6), NOT to M1. Round 28 is green at the tip only when BOTH land.
- Multi-section reading matters for a different reason than M1's rounds: lessons 15/19/23/24/25
  carry their section MID-FILE; an append-only second section at the end is invisible to the
  base reader. The prereg routes those as residual unless C2 lands first — the G3-shaped fix
  (read every `## Seat-reported failures` section, union the entries) is what makes
  append-only carries to mid-file lessons decidable at all.
- Carry-section hygiene: lesson files are pointer-scan sources, so M1 bullets that quote report
  paths must use the `.ufo/waves/round-2N/...` form (resolves through the committed captures —
  safe for all of rounds 26/27/28's committed reports) or committed `census/round-2N/waves/...`
  paths. Disposition token: CARRY_TOKEN_RE is `(?i)\bopen\b|resolved@[0-9a-f]{7,}` — a
  `resolved@<full40>` disposition carries; `resolved@<short7>` also matches, so M1 authors should
  use the full 40-hex commit the claim text requires anyway.

## E. C3's fixture vs C1's enumeration — no shared bytes (verified negative)

census/round-31/c1-cells.tsv is frozen at list-rev and enumerates only r12-r30 literals and
commands; every item's record-round set is ⊆ {12..30}. C3's new bytes (corpus/knowledge/
jj-dropped-keep-object-lifetime.md, tests/fixtures/r31-jj-object-clock.sh,
census/round-31/records/jj-object-clock-run.txt, census/round-31/sources/*, SOURCES.md rows) are
outside the enumeration, outside the gate's REGRESS script set, and invisible to C2's LANE leg
(content at BASE). One live touch: the C3 entry is a corpus/knowledge/*.md file, hence a gate
pointer source at the tip — its snapshot:/record paths are committed with the claim and its
`source:` cells are https URLs (not pointer roots), so it is clean by construction; wave-2 edits
to the entry must keep every cited path committed.

## F. Recurring mistake classes across rounds 26-30 and this round's repeat vectors

| class | where mined | round-31 repeat vector |
|---|---|---|
| landing / uncarried seat STATUS failures | r30 ## Mistakes row 1 (r29 lesson had no heading; 7 lines uncarried) → mined as M1 | wave-2 reports landing after the round-31 lesson carry is authored re-create the class unless the per-landing-commit gate run (routed process item 5) catches them |
| reference-drift: wave path cited before capture lands | r29-verifier-spotcheck D1; r30 ## Mistakes row 2 (SCORECARD.md:322 `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv` absent at C2 landing) | any `.ufo/waves/round-31/` token in SCORECARD rows, C1 note cells, M1 carry bullets, C3's entry Gate — dangling at every commit before the capture; SCORECARD.md is scanned (see B) |
| number-drift: stated counts diverge from committed bytes | r29 ## Mistakes row 1 (LOG.md:1758 / SCORECARD.md:23 "two malformed" vs committed 152) | wave-2 SCORECARD measurement rows stating after-values the frozen counters do not reproduce at the tip; C1 rows citing a line ≠ the item's base line (BAD-ROW) |
| vacuous / always-zero controls | r29 rows 4-5; r30 rows 4-5 (stub gate + byte-recognising fixture; typed record + grounded stub) | recurrence needs a binding whose script prints the literal without exercising the row — the stem rule checks only the name on the base line; wave-2 should probe C1 run-bindings and a doctored r30-style fixture printing `cases=7 pass=7` |
| stale-premise: base record vs independent checker | r28 ## Mistakes; r30 row 3 (A1's own regress regex could never print its target leg) | receipts bound to pre-integration revs re-cited as tip evidence; counters re-run against stale receipts in wave 2 |
| scope: stray edits / origin push | r29 rows 5-6 (origin push to lane master; parked seat edited its tracked report) | parked seats woken by mis-addressed messages editing tracked reports; the wave contract's drop-origin rule is the fix — counters' clone code enforces toplevel equality |
| sentence-to-record overreach | r30 row 6 (jj-keep-ref-expiry entry: five sentences stronger than its record) | C3 L10 mechanizes only backticked RESULT spans; non-RESULT prose sentences remain uninstrumented (r30's own fix said "Not yet shown able to fail by an instrument") — the open wave-2 surface |
| attribution / axis honesty | r26-M1; r29 row 3 | the C1↔C2 REGRESS coupling in section C is the live instance: C2 can flip C1's L40 without C1 changing a byte |

## Bottom line for the L1

1. Order SCORECARD appends so C1's 41 binding rows are the last `| Lnn |`-shaped rows (or keep
   measurement tables' first two cells distinct).
2. C2's report-discovery fix must be union-by-relpath with .ufo-preferred bytes: it is the only
   shape satisfying D3 (r30 fixture, REGRESS+L40) and G1/G2 (r31 fixture) simultaneously.
3. M1 needs no C2 sequencing for its own green, but round-28-tip green needs C2's tokenizer too;
   keep M1 carry quotes to capture-resolvable or committed paths.
4. C3 is separable from C1/C2 byte-wise; its only shared surface is the tip gate's pointer scan.
