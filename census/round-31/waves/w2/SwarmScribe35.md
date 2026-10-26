# SwarmScribe35 — round 31 wave 2, QUALITY.md Q67-Q69 and SKILL.md gate-registry rows

## Status

STATUS: PASS — Q67, Q68 and Q69 are drafted against the landed state (not the wave-1 draft's pre-landing
state), each cites `corpus/lessons/round-31.md`, each carries a command this seat ran at the tip; the three
assigned gate-registry rows are drafted; one criterion-level defect in the C1 counter (green reachable by
substitution) and one disclosed reading limit (letters-only paths) are reproduced and reported, not papered over.

## Evidence

Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`,
tip read `2c16d018e40db7c23420a2c3bb546b52957bcc25` (branch master). Scratch
`/fast/scratch/hyaku/souji-r31/w2-SwarmScribe35` with its own `TMPDIR`, removed at the end. Nothing installed,
nothing upgraded, no package transaction; no write in the lane except this report and
`.ufo/waves/round-31/w2/deliver-quality-rows.md`.

Contract and amendments read first (`census/round-31/records/preregistration.txt`,
`census/round-31/records/amendments.txt`, A0-A5 and the append-only correction block).

### Landed state re-derived

1. C1, A2+A4 tool at the tip:
   `python3 -B tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`
   -> `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=2c16d018e40db7c23420a2c3bb546b52957bcc25`,
   rc 1, 40 s. The single mismatch is `ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND`.
2. C1, v1 tool (`git show 1d45496:tools/souji-capability-cells.py`) at the tip: same SUMMARY, rc 1. The L1's
   landing reading therefore holds at the tip under both tool versions.
3. Append discipline: base `SCORECARD.md` blob (61 956 B) is a byte prefix of the tip blob (73 035 B); the
   appended part holds 40 lines starting `| L`, and no row for L29 (`rows_in_appended_part: 40`, `L29_rows: []`).
4. L29's record shape: `census/round-21/remote-source-after.json` contains zero occurrences of `18/18` and
   states `"matched_command_count": 18`, which is the honest-miss ground the SCORECARD preamble states.
5. C2, A5 counter at the tip:
   `python3 -B census/round-31/c2-counter-v3.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin`
   -> `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok`, rc 0, 25 s. Leg lines:
   `LANE round=26 rc=1 reports=495 cne=0`; `FIXTURE rc=0 line='cases=10 pass=10 control=FALSE-GREEN-REJECTED'`;
   `REDARM rc=1 base_cases=[G1 FAIL, G2 PASS, G3 FAIL, G4 FAIL, G5 FAIL, G6 FAIL, G7 FAIL, G8 FAIL, G9 PASS, G10 PASS]`;
   four `REGRESS … same` lines (selftest 65/0, r16 15/0, r30 7/7, r19-carry-wrap 4/0); `SHIFT rc=1` with the
   four real tokens matched exactly; the run's random probes are printed on a `SHIFT-PROBES` line, e.g.
   `census/round-%d/bepbxkgwqw/` and `corpus/knowledge/quovbnhk.md:230–231`.
6. C2 fixture standalone at the tip:
   `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` ->
   `cases=10 pass=10 control=FALSE-GREEN-REJECTED`, rc 0, every `CASE G1..G10 PASS` (G1 `reports=2 … uncarried=1`,
   G9 `dangling=6`, G10 `uncarried=1`).
7. C2 red arm, same fixture against the base blob (`git show 9f17a1e:tools/souji-landing-gate.py`) ->
   `cases=10 pass=3 control=FALSE-GREEN-REJECTED`, rc 1, failing exactly G1 G3 G4 G5 G6 G7 G8 with G2 G9 G10 green.
8. C3, A1 counter at the tip:
   `python3 -B census/round-31/c3-counter-v3.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`
   -> L1..L13 all PASS, `L10 PASS result_spans=6 not_in_record=[]`,
   `L12 PASS rc=0 results_equal=True jj_calls=26 git_calls=111 missing=[]`,
   `L13 PASS M1:rc=0,lines=17,differs=True,no=0<4=True M2:rc=0,lines=17,differs=True,no=0<4=True`,
   `SUMMARY legs=13 fail=0 f1_entries=4`, rc 0, 4.8 s.
9. C3 fixture standalone: `TMPDIR=$D/tmp bash tests/fixtures/r31-jj-object-clock.sh` -> rc 0, 19 lines
   (`jj-version: jj 0.45.1-7c41cdeb…`, `git-version: git version 2.56.0`, 17 `RESULT` lines); `diff` against
   `census/round-31/records/jj-object-clock-run.txt` is empty (whole file identical). `TMPDIR= bash
   tests/fixtures/r31-jj-object-clock.sh` -> `ERROR: TMPDIR is unset or empty; refusing to run`, rc 2.
10. M1 carry at the tip: `python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d01… --round 26
    --fleet-root /home/vgpnk/Projects/shokunin` (and 27, 28) -> each `SUMMARY findings=0 …` with
    `carry_heading=1`, zero `LG-SEAT-UNCARRIED`, rc 0; round 26 `checked_reports=495`, round 27 94, round 28 61.
11. Carry token width: `tools/souji-landing-gate.py:113` (`CARRY_TOKEN_RE`) accepts `open` or `resolved@` plus
    seven or more hex characters, so a 7-hex token passes the gate; the criterion
    therefore requires a full 40 that resolves (recorded in Q68, from the wave-1 draft's disclosed limit 3,
    re-read here).
12. Fence-aware carry reading: `tools/souji-landing-gate.py:417-428` toggles `in_fence` and only matches
    `FAILURES_HEADING_RE` when `not in_fence` ("fenced block is text, not a section boundary").

## Findings

1. **C1's counter cannot refuse a substitution binding; its frozen target is reachable without an honest
   binding.** Location `tools/souji-capability-cells.py` record rule (docstring lines 28-32, A4 rules at 43-52);
   the rule checks round-set membership, blob equality, integer multiset and literal occurrence, but never that
   the record is the one the cell's occurrence names. Reproduced in a scratch clone at the tip: appending
   `| L29 | SCORECARD.md:170 | 18/18 | record: census/round-21/final-code-verification.json | … |` and running
   `--only L29` prints `ITEM L29 … superseded binding=record MATCH census/round-21/final-code-verification.json`
   and `SUMMARY items=1 bound_run=0 bound_record=1 unbound=0 mismatches=0 partial=1`, rc 0 — i.e. 41/41 green at
   the tip. Axis harmed: calibration (the claim's own axis), because a green run does not show what the target
   says it shows. The landed claim is *not* harmed: it left L29 UNBOUND and disclosed the miss before landing
   (A4 pre-landing reading, re-derived here). Q67 therefore states the honest-binding rule and says green is
   audited item by item; the counter itself should gain an occurrence-level rule (reported, not amended).
2. **The honest arm of the same item is refused, which fixes the direction of the repair.** Same scratch repo,
   row changed to the record the cell actually names: `--only L29` prints
   `ITEM L29 … RECORD-MISMATCH census/round-21/remote-source-after.json`, rc 1. So the only green repair is the
   dishonest one; a reviewer must never accept it. Axis: calibration.
3. **The letters-only prose rule hides a genuinely absent letters-only path.** Location
   `tools/souji-landing-gate.py:169-171` (`LETTERS_ONLY_RE`) and `:882-890` (`_prose_pointer`). Direct call on
   the committed tool: `_prose_pointer('corpus/authority')` True, `_prose_pointer('census/waves')` True,
   `_prose_pointer('census/round-3/garbage-census.out')` False, `_prose_pointer('tools/__pycache__/')` False.
   End to end: a synthetic round-19 lesson citing `census/waves` and `census/waves/` (both absent) yields one
   `LG-DANGLING-PTR` for `census/waves/` and none for `census/waves`; a control absent path with an extension
   is flagged. Axis: operability — a real missing directory named in words alone is invisible to the gate.
   Disclosed by A3 ("cannot tell `corpus/authority` from a real dangling `census/waves`"); Q68 now carries the
   limit in the criterion instead of leaving it to the amendment file.
4. **`corpus/lessons/round-31.md` is absent at the tip, and all three rows cite it.**
   `git cat-file -e 2c16d01:corpus/lessons/round-31.md` fails; the committed `corpus/lessons/` tree holds 47
   files and none of them is round-31; `git status --porcelain` is empty (no untracked lesson). Under Q65 the rows
   can only land at or after the lesson commit, or their citations must name a committed path. Axis:
   calibration (a record row citing an uncommitted path is the defect Q65 exists to prevent).
5. **The wave-1 draft's registry rows for the C2 and C3 counters are stale.** `.ufo/waves/round-31/w1/
   deliver-quality-q67-q69.md` pins `r31-c2-counter` to `fixture=ok redarm=ok regress=same` (no `shift`) and
   `r31-c3-counter` to `legs=11`/`legs=12`, both of which stopped being the certifying target at A1 (v3
   `legs=13`) and A3/A5 (v2/v3 `shift=ok` with random probes). Axis: operability (a registry that misdescribes
   a gate's target tells the next round to accept a weaker reading). Not redrafted here (outside this seat's
   three assigned rows); routed to the integration owner in the delivery.
6. **Known limits I did not re-derive** (so they are not evidence of health): C3's L4 fetch receipts are
   self-attested (A1 discloses that a fabricated snapshot plus its own hash passes) — this seat verified only
   that `L4 PASS snapshots=3 bad=[]` holds against the committed SHA256SUMS and receipt rows, not that the
   upstream bytes are what the registry rows describe; `reflog_hits` is a fixture-reported column that no leg
   re-derives; C1's record bindings are dated, never re-run. Axis: coverage/calibration, all disclosed.

## Attack log

- **A1 — substitution green (C1).** Scratch clone at the tip
  (`git clone -q --no-local … ; remote remove origin`, `rev-parse --show-toplevel` = scratch path, throwaway
  `user.name`/`user.email` via `git -C <scratch> config`), one appended row binding L29 to
  `census/round-21/final-code-verification.json`, commit `e2774c0c6b9fbbbda4d45044c7c1a961b75d217e`, then
  `--only L29` -> `bound_record=1 unbound=0 mismatches=0`, rc 0. Result: the target is gameable.
- **A2 — honest arm (control).** Same clone, record changed to `census/round-21/remote-source-after.json`,
  commit `65bf5b0b147852b7390d1994c97264a8f45614aa`, `--only L29` -> `RECORD-MISMATCH`, rc 1. The counter's
  direction is: refuse the truth, accept the substitute.
- **A3 — letters-only probe (C2).** Synthetic git world built with the committed fixture's own `Repo` and
  `git_env` helpers under my scratch `TMPDIR`; lesson cites `census/waves`, `census/waves/` and
  `corpus/knowledge/missing-prose-probe.md`; real gate at the tip -> rc 2 (world has no registry, so
  could-not-evaluate) with pointer findings retained: `LG-DANGLING-PTR census/waves/` and
  `LG-DANGLING-PTR corpus/knowledge/missing-prose-probe.md`, and none for `census/waves`. Blind spot reproduced
  on the committed tool.
- **A4 — counter re-derivation instead of trust (C1, C2, C3, M1).** All four claim readings were re-run at the
  tip rather than copied: C1 A2+A4 and v1, C2 v3 (random SHIFT), C3 v3 with L12/L13 details, and the landing
  gate for rounds 26, 27 and 28. All agree with the L1's landing readings.
- **A5 — fixture red arm (C2).** The precision fixture run against the base gate blob fails exactly the seven
  defect cases its contract names and passes the three controls, so the fixture is not a false-green emitter on
  the pre-C2 tool.
- Not attacked, by design: the counters' kill rules and targets (frozen), the other seats' claims, and the
  fleet outside this lane.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-quality-rows.md` — Block A (`## Round 31 criteria`, Q67-Q69 with the file's own
  column headers) and Block B (three `## Gate registry` rows: `souji-capability-cells`,
  `r31-landing-gate-precision`, `r31-jj-object-clock`), plus ten numbered corrections against the wave-1 draft
  and four integration dependencies (lesson absence, wave-2 capture path, C1's missed target, no tool claim).
- `.ufo/waves/round-31/w2/SwarmScribe35.md` — this report.
- Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe35` removed after the deliveries were written; no raw
  output is left behind except the excerpts quoted above.
