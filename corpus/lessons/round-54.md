# Round 54 — the annotation and capture counters amended (v3): the r53 routed surfaces instrumented

Fresh-start reading: not applicable (round 54 of a lane with no streak block). The r53
non-author verifier spot-check (`corpus/lessons/round-53-verifier-spotcheck.md`, verdict
ok/admitted) routed: §6.1 (report count), §6.2 (wave-results pointer, integrator-owned),
§6.3 (prereg wording), §6.4 (S4 oracle/builder pinning). §6.1 and §6.3 and §6.4 are answered
below; §6.2 stays with the protocol integrator.

Claims (frozen in `census/round-54/preregistration.txt`, freeze
`3c394cab0cd406bbab72b8d365e0f3deed4ef98a`; base `fe12daad2549f534650d406ebdbac9113d59313f`):
- C1 calibration 7 (the lowest non-retired axis): the annotation-agreement counter is
  amended to v3 (`census/round-54/c1-counter.py`) to instrument the r53 routed filing
  surfaces — the tilde / 4-backtick-parity / HTML-comment hidden-filing grammar, the
  zone-edge straddle refusal, the bogus-recomputed refusal, and the LOG/README
  SOURCES-pair annotation scan — over thirteen committed fixtures (F1–F6 carry the r53
  matrix; F7–F12b are new).
- C2 coverage 8: the capture counter is amended to v3 (`census/round-54/c2-counter.py`) to
  instrument the widened `#`-row shape, unknown receipt keys, the named CAPTURE-CRLF class,
  the `--tool-sha256` argument pin, and the branch fixtures FA7/FA8/FH2, over ten committed
  fixtures plus the fresh committed round-54 capture (commit
  `bfdbb336329e6afba3ab1ca83cbd6d9759271062`, fleet HEAD `3b0d5329147d3b05d3aec5e908c75405ae3bc05a`).
No exploratory claim. No assimilation: `shokuknow`'s `merge/souji/` package stays held by the
open r46 L0 question on mass id drift; `considerthese/` does not exist in this lane
(`ls | grep -ci consider` → 0, rc 1, re-checked 2026-11-03).

## Gate

- Admitted: **S277** — CommonMark spec 0.31.2, §4.5 Fenced code blocks and §4.6 HTML blocks.
  URL https://spec.commonmark.org/0.31.2/; access date 2026-11-03; `curl -sSL -o
  s277-commonmark-spec.html -w '%{http_code} %{url_effective}'` → `200
  https://spec.commonmark.org/0.31.2/` (no redirect), 514698 bytes, sha256
  `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`; the page states
  "Version 0.31.2 (2024-01-28)". Capture: `census/round-54/sources/s277-commonmark-spec.html`
  (cmp-exact to the seat's fetch). Located quotes (≤25 words each), in
  `census/round-54/sources/s277-located-quote.txt`:
  - §4.5, 17 words — "A code fence is a sequence of at least three consecutive backtick
    characters (`) or tildes (~)." (a fence may open with backticks OR tildes)
  - §4.5, 25 words — "same type as the code block began with (backticks or tildes), and
    with at least as many backticks or tildes as the opening code fence" (the parity rule)
  - §4.5, 13 and 14 words — "The closing code fence must use the same character as the
    opening fence" / "The closing code fence must be at least as long as the opening fence"
  - §4.6, 15 words — "Start condition: line begins with the string <!--. End condition: line
    contains the string -->." (the HTML-comment start and end conditions)
  Independent re-check by the L1 (tag-strip recipe of r53 S276; `html.unescape`, whitespace
  collapsed): all five `substring: True`, word counts 17/25/13/14/15, and the version heading
  `True`. The seat's own check agreed.
- Reuse (no new row, used-by cell changed): **S276** — gitignore(1), PATTERN FORMAT, "A line
  starting with # serves as a comment." (9 words). Grounds the C2 `#`-row refusal, as in r53.
  Status changes old→new, logged here as required: S276 `used-by`
  `corpus/knowledge/fleet-root-capture-receipt-grammar.md` →
  `corpus/knowledge/fleet-root-capture-receipt-grammar.md, corpus/knowledge/correction-filing-fence-grammar.md`
  (the new entry cites S276 as its second source). S277 landed as `mined` in the same commit
  that lands its citing entry (`correction-filing-fence-grammar.md`); `queued` → `mined`.
  No other existing row's status, recheck or used-by cell changed.
- Search log: one bounded search (the CommonMark spec, sections 4.5 and 4.6), recorded in
  `corpus/SOURCES.md` `## Search log` with identified/screened/included/excluded counts.
- Knowledge entry admitted: `corpus/knowledge/correction-filing-fence-grammar.md` (source
  S277 and S276; provenance trio first). It states the v3 grammar surface by surface, which
  r53 routed item each check answers, and the named limits verbatim from the prereg. It
  includes two line-level divergences from the CommonMark text (indented fences and a `<!--`
  that is not at line start); both are disclosed as conservative-for-refusal, not defects.
- Rejected this round: none. Sweep honesty: the round opened exactly one new page (S277).
  Nothing else was screened, so there is no reject sample to report; the same shape as r52 and
  r53.
- Spot-check result: pending the round's non-author closure (LEARNING.md). The lane does not
  claim it.

## Claim evidence

C1 (calibration). Before (v2 arm, the frozen r53 counter run over the same 13 rows):
`census/round-54/records/c1-matrix-v2.tsv` — exit 1 on 5 of 13 rows (F2–F6, the r53 kills);
exit 0 on F7, F8, F9, F10, F11, F12 and F12b. After (v3):
`census/round-54/records/c1-matrix-v3.tsv` — exit 1 on 11 of 13 rows, each with its named
finding (F7→CORRECTION-IN-FENCE, F8→CORRECTION-IN-FENCE, F9→CORRECTION-IN-FENCE,
F10→ZONE-TOKEN-STRADDLES-EDGE, F11→BOGUS-RECOMPUTED, F12→UNFILED-SOURCES-ANNOTATION); F1 and
F12b stay green. Counting command: `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}'
census/round-54/records/c1-matrix-v{2,3}.tsv` → `5` then `11`. Selftest with pins:
`census/round-54/records/c1-selftest.txt` → `SELFTEST pass cases=13`, EXIT=0. Real lane at the
capture commit: `census/round-54/records/c1-tip.txt` → exit 0, `unfiled=0 record_sha=ok
appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0`. Controls:
`census/round-54/controls/c1-control-donothing.txt` (absent-instrument control at base; the
v2-arm acceptance rows; the wrong-pin refusal; EXIT=1).

C2 (coverage). Before (v2 arm): `census/round-54/records/c2-matrix-v2.tsv` — exit 1 on 6 of 10
rows (FA1, FA2, FA3, FA6, FA7, FA8); exit 0 on FA4 (space-in-name `#` row) and FA5 (unknown
receipt key); FA6 (CRLF) exits 1 but its first finding is a spurious
`CAPTURE-RECEIPT-MISMATCH`. After (v3): `census/round-54/records/c2-matrix-v3.tsv` — exit 1 on
8 of 10 rows, FA4→COMMENT-AMBIGUOUS-NAME, FA5→RECEIPT-UNKNOWN-KEY, FA6→CAPTURE-CRLF as the
first finding; FH and FH2 stay green. Counting command: `awk -F'\t' 'NR>1 && $5==1{n++}
END{print n+0}' census/round-54/records/c2-matrix-v{2,3}.tsv` → `6` then `8`. Selftest with
pins: `census/round-54/records/c2-selftest.txt` → `SELFTEST pass cases=10`, EXIT=0. Real lane
at the capture commit: `census/round-54/records/c2-tip.txt` → exit 0, `receipt=ok sorted=ok
tool_pin=ok` over the fresh capture. Pin behaviour on the real lane: wrong 64-hex pin →
`FINDING TOOL-SHA-ARG-MISMATCH`, rc 1 (critic and reviewer02, independently).

Pre-freeze fixture and instrument work is disclosed here, not hidden: the first v3 selftest
run failed 1 of 13 (`F12b-LOG-FILED` exit 1) because the registry-row regex used POSIX classes
(`[[:space:]]`) that Python's `re` reads as a nested set; the regex was corrected before the
freeze and the selftest then passed 13/13. The first draft of F11 filed both stale sites
with `recomputed=83`; v2 killed it through the unfiled path (exit 1, `unfiled=2`), so it did
not isolate R3. It was redesigned before the freeze to the routed R3 shape (the site already
reads 79, the correction claims recomputed=83), where v2 exits 0 silently.

## Wave findings (the 12-seat wave: attacks and what they changed)

Wave shape: one v1 wave, 12 seats (scout ×1, executor ×3, scribe ×1, reviewer ×2, critic ×1,
mutation-tester ×1, sentinel ×1, connector ×1, revenger ×1). Attack roles by the protocol
definition (reviewer, critic, mutation-tester, labrat): 4 of 12 = 33% (≥25%). The prereg's
"5 of 12 (42%)" counted the revenger as an attack seat; the 33% figure is the definition
applied here. Connectors: 1 (≤2). Band 8–16. Seat outputs are copied into
`census/round-54/wave/` (the `.ufo/waves/` directory is gitignored; the spec, dispatch and
seat reports are committed there as wave evidence). Results file:
`.ufo/waves/round-54/w1/swarm-registry.json` and the dispatch at `.ufo/waves/round-54/w1-dispatch.json`.

Seat-by-seat (verdict · what it attacked · what it changed):

- **executor01** (C1 reproduction): AGREE 13/13 against `c1-selftest-expected.tsv`; the
  builder run twice gives identical (name, base, tip) columns for all 23 fixtures; real lane
  byte-identical to `c1-tip.txt`. Risk notes (no defect): F4/F7/F8/F9 print two
  `CORRECTION-IN-FENCE` findings and also set `unfiled=2`; F10 prints both the straddle and
  `INERT-CORRECTION` on one line. No change made.
- **executor02** (C2 reproduction): AGREE 10/10; FA4/FA5 exit 0 under v2; FA6 pair shown
  (v2 spurious first line, v3 `CAPTURE-CRLF` first); pin refusal and pass both shown; real lane
  `receipt=ok sorted=ok tool_pin=ok`. No change made.
- **executor03** (standing receipts at the capture commit): 11/11 green; r53 c1/c2 green at
  the tip; r52 c1/c2 green (r52 c2 takes no `--capture` flag, its capture path is compiled in);
  r51 c1/c2 green with `--base-rev`/`--scratch`; the v3 selftests re-run with pins green;
  negative pins exit 2 as specified; census v1 receipt verify ok.
- **scout01** (repo recon): tip state and the zone checks at the tip; the append-only check
  (deletions 0 on the frozen files); the freeze-commit audit (all six pins equal the prereg);
  `fe12daad`→`bfdbb336` ancestry; the registry count at both pinned revisions 198 and 199.
- **revenger01** (routed items): §6.1 RED — the r53 report's "six rows" is wrong; the table has
  seven body rows (see Mistakes row 4). §6.3 GREEN — the r54 prereg avoids the r53 "close the
  five named limits" pattern and names the two control artifacts distinctly. §6.4 GREEN — the
  r54 prereg pins all four instruments and the selftests verify the pins before exec. The
  R53-CORRECTION filings resolve at the tip (LOG.md:2527 and corpus/README.md:870 carry the
  stale 274 → 275 pair; the filings name them). The fleet-root LOG.md carries no round-53
  souji entry (misroot cleared). §6.2 UNRESOLVED — integrator-owned, outside the frozen claims.
- **scribe01** (S277): live fetch (HTTP 200, 514698 bytes, sha256 as above); the five quotes
  located; the S277 row and the knowledge entry drafted. The L1 re-verified the quotes and the
  row's 11-column shape.
- **critic01** (falsification): both claims SURVIVE the frozen predicates, controls and kill
  rules. Seven named limits (N1–N7, below). Its vacuity probes: the v2 arm kills none of F7–F12b
  or FA4/FA5 (not vacuous); the C2 real lane is red at base (the capture is new work); the
  C1 real lane is already green at base (disclosed, the r53 filings predate the round).
  Its wrong-tool-pin probe on the real lane gives `TOOL-SHA-ARG-MISMATCH` (pin shown able to fail).
- **reviewer02** (attack on C2 v3): zero routed defects against the frozen claims; five named
  limits (NL-1 to NL-5). The attack `A1a-4TAB` (a `#`-row with four tabs and a consistent
  ENTRIES) is silently dropped by both arms; `A1c` (a legitimate prose comment with five tabs)
  is refused by v3 and accepted by v2; `A2a` (lowercase unknown key), `A2b` (`#  KEY=` with
  two spaces) evade `RECEIPT-UNKNOWN-KEY`; `A3` (63-, 65- and uppercase-hex pins) exits 2, not a
  mismatch. A disclosed runner error (its first three lane runs passed the fixture's capture path
  instead of the round's; the receipt binding caught it: `CAPTURE_SHA256` mismatch) is the seat's
  own, and the corrected runs are the results.
- **mutation01** (kill-power on the new v3 checks): 9 of 12 mutants killed by committed fixtures
  (M1 F7, M3 F9, M4 F10, M5 F11, M6 F12, M8 FA4, M9 FA5, M10 FA6, M12 FH2 and FA8). Three
  survivors, all coverage gaps and none equivalent: **M2** (the closing-fence length rule — no
  committed fixture has a bare shorter run inside a longer fence), **M7** (the pointer
  exemption — the honest real lane's `LOG.md:2578` depends on it; no fixture carries a pointer),
  **M11** (the `--tool-sha256` mismatch branch — the selftest passes `None` for the pin, so no
  committed fixture reaches it). Determinism: the builder's manifests are identical across two
  builds and across two directories.
- **reviewer01** (attack on C1 v3, 60 counter runs over 31 distinct attack states): the frozen
  13/13 selftest passes and the carry-over F2–F6 kills hold; no attack makes v3 exit 0 on F1 or
  F12b, or exit 1 on the real green lane. **Six routed defect classes** (new states the frozen
  fixture matrix does not cover; each a named limit for r55, none edited here):
  - **R1** hidden-correction swallow: a correction-shaped line behind a one-line `<!--` wrapper
    or with 2–3 leading spaces never lexes as a filing, and `hidden_lines()` is audited only
    against parsed filings; on an agreeing site the bogus correction exits 0 (AF1e2, AF1e3).
    v2 inherits it. The 4-space indent and the one-line wrap that also trip unfiled exit 1 by
    side effect only.
  - **R2** dual-anchor aliasing: only the first anchor occurrence per site line is judged; a
    second annotated anchor's wrong count is invisible, exit 0 (AF2d). v2 inherits it.
  - **R3** pair-filing stale drop: an R53-CORRECTION pair filing whose stale pair differs from
    the annotated pair is silently ignored, exit 0 (AF3d) — there is no INERT analogue for pairs.
  - **R4** rows-word dodge: `corpus/SOURCES.md <A> -> <B>` without the word `rows` escapes the
    UNFILED scan, exit 0 (AF4b). The r53 misread class carried the word; this shape did not.
  - **R5** fence over-hide against CommonMark 0.31.2: a 4-space-indented fence is refused though
    the spec reads it as indented code (AF1f2), and a backtick inside a backtick fence's info
    string is refused (AF1g). The conservative direction for a refusal; still a divergence.
  - **R6** the PAIR_SITES scan does not hide-fence: a pair annotation inside a fenced example in
    LOG.md raises UNFILED, exit 1 false positive (AF4d).
  Confirmed as named limits by attack, behaviour matching the disclosure: AF4a (pointer
  exemption), AF4c (two-file scope), AF3e (historical notes), AF2c (a token wholly beyond the
  zone is ignored: exit 2 CANNOT-EVALUATE, not acceptance). Carry-over and the v2-arm control
  are clean. One observation corrected the seat's own prediction: `rstrip()` strips trailing
  tabs, so a close with a trailing tab is CommonMark-correct and accepted.
- **sentinel01** and **connector01**: findings incorporated below when they land.

Named-limit findings from the attacks (routed to r55 — none edits the frozen bytes):

- N1 (critic) — the v3 docstring names `SOURCES-ANNOTATION-DRIFT`, which no code path emits; a
  stale pair that mismatches its annotation is refused as `UNFILED-SOURCES-ANNOTATION`.
  Docstring-vs-code defect.
- N2 (critic, mutation M11) — the C2 kill rule says a wrong `--tool-sha256` pin is "shown able
  to fail by a wrong-pin refusal in the selftest". The committed selftest has no pin arm (the
  harness passes `None`). The refusal is real on the real lane; the cited demonstration location
  is false as written. **This is a false statement in the frozen prereg.**
- N3 (critic) — the prereg's F11 mechanism clause ("mismatches=0/unfiled=0 hid the cause") is
  wrong: the v2 F11 summary is `mismatches=1 filed=1 unfiled=0`. The cause is the matched but
  unfiled S1 tuple. **Also a false statement in the frozen prereg.**
- N4 (critic) — the C1 control's line "filed=no is not printed" is false: the v2 arm on F11
  prints `SITE path=SCORECARD.md line=5 stated=79 recomputed=79 status=match filed=no`.
  **A false statement in the frozen control file.** Erratum below.
- N5 (critic) — the `SOURCES-RECOMPUTE-MISMATCH` refusal has no committed-fixture coverage (the
  same branch-coverage shape as r53 M-F1/M-F2). Functional on a probe; kill-power not pinned.
- N6 (critic) — R12 (exit-code ambiguity: exit 1 PRISTINE FAIL versus exit 2 bad revision) has no
  named-limit line in the prereg; only the docstring describes it. A disclosure gap; R11 is
  disclosed.
- N7 (critic) — the r53 verifier §6.1 count discipline binds this round's report; addressed below.
- NL-1 (reviewer02) — `#`-leading capture lines with at most four tabs are silently dropped;
  the field-count rule never evaluates them. Both arms blind.
- NL-2 (reviewer02) — the ≥5-tab rule is shape-only: a prose comment with five tabs is refused.
- NL-3 (reviewer02) — `RECEIPT-UNKNOWN-KEY` is uppercase-only; lowercase unknown keys pass.
- NL-4 (reviewer02) — unknown-key detection anchors exactly `# ` after strip; `#  KEY=` and
  `#KEY=` evade it while leading-space variants are caught (a strip asymmetry).
- NL-5 (reviewer02) — `--tool-sha256` takes lowercase 64-hex only; other shapes exit 2.
- M2, M7, M11 (mutation01) — the three coverage gaps above.
- Dead predicate (reviewer02 observation): in v3 the `DATA_LIKE_COMMENT` fullmatch is subsumed by
  the `count('\t') >= 5` test; kept for v2 parity; harmless.

Corrections filed (append-only, this lesson, because the frozen prereg and control files
cannot be edited):

- ERRATUM-R54-1 — `census/round-54/preregistration.txt`, claim C2's kill rule, the clause
  "shown able to fail by a wrong-pin refusal in the selftest": the committed selftest has no
  `--tool-sha256` case. The refusal is shown on the real lane (critic: `FINDING
  TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783`, rc 1; reviewer02 3d).
  Corrected reading: the pin is demonstrated on the real lane, not in the selftest. The
  selftest arm is routed to r55 as FA9 (see Named limits).
- ERRATUM-R54-2 — `census/round-54/preregistration.txt`, claim C1, F11 mechanism clause:
  v2 on F11 reads `mismatches=1 filed=1 unfiled=0`, not `mismatches=0/unfiled=0`; the cause is
  the matched S1 tuple left unfiled.
- ERRATUM-R54-3 — `census/round-54/controls/c1-control-donothing.txt`, the line "filed=no is not
  printed": the v2 arm on F11 prints `filed=no` on the SCORECARD SITE line (critic N4). The
  control's conclusion (v2 accepts F11 with exit 0) stands.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a frozen predicate's kill-rule sentence names a selftest demonstration the selftest does not run: the `--tool-sha256` wrong-pin refusal is cited as "shown able to fail ... in the selftest", but the selftest passes `None` for the pin and no committed fixture reaches the branch | `census/round-54/preregistration.txt` (C2 kill rule); `.ufo/waves/round-54/w1/S54mutation01/report.md` §3 and §5 (M11: the branch is unreachable from `--selftest`); critic N2; reviewer02 §3. | none — the prereg was written from the real-lane probe; no step checked that each cited demonstration location runs | ERRATUM-R54-1 (this lesson); the selftest arm is routed to r55 as FA9 and the fix is **not yet shown able to fail**, so it does not count as fixed this round |
| a frozen prereg's mechanism clause misstates the instrument's summary line: "mismatches=0/unfiled=0 hid the cause" for F11, when v2 prints `mismatches=1 filed=1 unfiled=0` | `census/round-54/preregistration.txt` (C1, F11 row); `census/round-54/records/c1-matrix-v2.tsv` F11 row; critic N3 | none — the clause was written before the v2 F11 summary line was printed (the matrix ran after the freeze) and was not checked against it | ERRATUM-R54-2; the r55 prereg must quote summary lines verbatim from the matrix receipt |
| a do-nothing-control disclosure asserts a printed field the instrument does not print ("filed=no is not printed") | `census/round-54/controls/c1-control-donothing.txt`; critic N4 (the v2 arm prints `filed=no` on the SITE line) | none — the control was written before the matrix was run, and not re-read against the printed output | ERRATUM-R54-3; the control's conclusion stands |
| the r53 report's Mistakes count: the report says "six rows"; the table has seven. The naive count `grep -c '^| '` returns eight because it counts the header row | `.ufo/reports/round-53/souji.md:193` ("six rows"); `corpus/lessons/round-53.md` `## Mistakes`: header + separator + 7 body rows; `awk '/^## Mistakes/{f=1;next} /^## /{f=0} f && /^\| /' corpus/lessons/round-53.md \| tail -n +2 \| wc -l` → `7`; `grep -c '^| '` → `8` (revenger01 item 1; r53 verifier §6.1) | none — the r53 verifier recomputed the SOURCES count but not the Mistakes count | the counting command above (header excluded by `tail -n +2`), with a red arm shown: the naive command gives 8, the claimed 6, the true 7. This round's report counts its own table the same way. |
| the first v3 selftest failed 1 of 13 cases on F12b (exit 1, expected 0): the registry-row regex used POSIX classes `[[:space:]]` inside a Python `re` pattern, which reads as a nested set | selftest run before the freeze: `FutureWarning: Possible nested set` then `SELFTEST fail cases=13` with `F12b-LOG-FILED fail rc=1 want_rc=0` | the selftest (the fixture caught it) | regex corrected to `[ \t]`; selftest green 13/13. Red-before shown (the F12b case), so the fix counts as shown able to fail |
| a reviewer-seat fixture run used the fixture's capture path where the round's capture path was required (a seat-side mispairing; the receipt binding flagged the mismatch as `CAPTURE_SHA256` and `FLEET_HEAD` differences) | reviewer02 §9 ("disclosed runner defect"); the three invalid outputs are preserved in that seat's `runs/` | the receipt binding (`CAPTURE-RECEIPT-MISMATCH`) — it did what it is for | corrected runs are the results; the seat's three invalid runs are kept, not deleted |

## Named limits carried into r55 (consolidated)

- The prereg's own disclosed v3 limits (`census/round-54/preregistration.txt`, "Named limits
  carried into v3"): the zone stays frozen at 32 chars; the SOURCES scan is line-based and
  exempts pointer lines; annotations at or below the current registry count are not re-derived;
  registry monotonicity is assumed; unknown capture-header keys are ignored; ENTRIES is the
  tool's own count; the receipt binds bytes and consistency, not execution or path; FLEET_HEAD
  is format-checked, not resolved; the fence class is line-level, not full CommonMark.
- N1, N5, N6 (critic) and NL-1 to NL-5 (reviewer02) above. N2–N4 are errata, not limits.
- The mutation survivors M2, M7 and M11 (coverage gaps) — the r55 fixtures they name: `F8b-BT4-SHORT-RUN`
  (a ```` ```` ```` fence with a bare ` ``` ` content line; v3 must hide the corrections), `F12c-LOG-POINTER-EXEMPT`
  (a LOG pair line with a `path:line` pointer, no filing, must stay green), and `FA9-WRONG-TOOL-PIN`
  (a selftest arm passing a wrong digest that must yield `TOOL-SHA-ARG-MISMATCH`, rc 1).
- Standing holds, unchanged: certification OFF, K5 HELD, NAMESPACE and reap holds, execution-audit
  attribution open; the two open L0 rulings (credential-shaped names refuse-vs-redact; the
  `ignored`-column derivation) and the r46 mass-id-drift L0 (assimilation held); the r48 census
  conf-form (this host: conf form rc 0, recorded).
