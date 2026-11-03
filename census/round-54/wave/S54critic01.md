# S54critic01 — souji round 54 falsifier report (role: critic)

Seat: S54critic01, wave r54/w1, leaf member (no subagents; every probe run by me).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Read first: census/round-54/preregistration.txt
(freeze 3c394cab0cd406bbab72b8d365e0f3deed4ef98a; confirmed `git log --diff-filter=A` adds it at
3c394cab; lane HEAD = capture commit bfdbb336329e6afba3ab1ca83cbd6d9759271062).
Scope: falsify the two frozen claims AS DECLARED. I edited nothing outside my seat dir; no git/jj
mutation anywhere (read-only git only, GIT_OPTIONAL_LOCKS=0 on lane/fleet calls).

## Verdicts

- **C1 (calibration 7, census/round-54/c1-counter.py v3): SURVIVES.** Every frozen predicate
  holds on the committed bytes (evidence below). Frozen-byte wording defects found — named limits
  to route, never edits: N1 (docstring names a class the code never emits), N3 (prereg F11
  mechanism parenthetical false), N4 (control "filed=no is not printed" false), N5
  (SOURCES-RECOMPUTE-MISMATCH arm unexercised by committed fixtures).
- **C2 (coverage 8, census/round-54/c2-counter.py v3): SURVIVES.** Kills, greens, first-finding
  rule, branch fixtures and the fresh committed capture all hold. Frozen-byte defect routed: N2
  (kill rule cites a wrong-pin refusal "in the selftest" for --tool-sha256; the committed selftest
  has no such case — capability proven by my live probe, citation location false).

No kill rule fires on either claim; both survive the frozen predicates, controls and kill rules
against the committed bytes. Seven named limits (N1–N7) route to r55; none is fixable this round
(all cited bytes are frozen).

## Pins and freeze (task 0)

```
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py      (= prereg)
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py      (= prereg)
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  records/c1-selftest-expected.tsv   (= prereg)
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  records/c2-selftest-expected.tsv   (= prereg)
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  fixtures/build-fixtures.py         (= prereg)
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  fixtures/run-matrix.sh             (= prereg)
```
Also re-derived: `git show bfdbb336:tools/souji-fleet-root-census.py | sha256sum` →
`e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` (= base bytes, same at
fe12daad); record at base → `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30`
(= prereg pin); r53 v2 counters = `a7928d05…` / `6515b975…` (match the r53 verifier's recorded
digests — the control arm is the frozen r53 bytes).

## Task 1 — predicate vs code (selftests re-run with the pins)

Commands (mine, from the lane; scratch under /fast/scratch/hyaku/souji-r54/S54critic01):
`python3 -B census/round-54/c1-counter.py --selftest --work S/pin --builder-sha256 ae5881f8… --expected-sha256 4e73c495…` → rc=0
`python3 -B census/round-54/c2-counter.py --selftest --work S/pin --builder-sha256 ae5881f8… --expected-sha256 e32f7934…` → rc=0
Verbatim key lines (diff vs the committed receipts `records/c1-selftest.txt` / `c2-selftest.txt`
shows only the committed files' trailing `EXIT=0` marker; every case line is byte-identical):

```
SELFTEST-CASE F7-TILDE-FENCE pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F8-BT4-PARITY pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F9-HTML-COMMENT pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F10-STRADDLE pass rc=1 want_rc=1 finding=ZONE-TOKEN-STRADDLES-EDGE want_finding=ZONE-TOKEN-STRADDLES-EDGE
SELFTEST-CASE F11-BOGUS-RECOMP pass rc=1 want_rc=1 finding=BOGUS-RECOMPUTED want_finding=BOGUS-RECOMPUTED
SELFTEST-CASE F12-LOG-UNFILED pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F12b-LOG-FILED pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST pass cases=13
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF want_finding=CAPTURE-CRLF
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=class want_finding=-
SELFTEST pass cases=10
```
Every finding id the prereg's predicate sentences name is emitted by the code on its committed
fixture. No predicate names a finding the code cannot emit. (FA8's TSV row declares `-` = any
finding; the counter's generic `class … want …` problem line is consistent with the prereg, which
claims no named class for FA8.)

## Task 2 — one-sentence agreement table (prereg vs expected TSV vs my run)

C1 (my selftest + fresh v2/v3 matrix arms; all v2-arm rows from my fresh `c1-matrix-v2.tsv`):

| fixture | prereg expectation | expected TSV | my selftest | my fresh v2-arm |
|---|---|---|---|---|
| F1-HONEST-TIP | green (discrimination control) | 0 / - | pass rc=0 - | exit 0 (carry) |
| F2-MULTI-ANNOT | v2 kill kept | 1 MULTIPLE-ANNOTATIONS | pass | exit 1 same id |
| F3-INERT | v2 kill kept | 1 INERT-CORRECTION | pass | exit 1 same id |
| F4-FENCE | v2 kill kept | 1 CORRECTION-IN-FENCE | pass | exit 1 same id |
| F5-REWRITE | v2 kill kept (--base) | 1 DELETED-LINES | pass | exit 1 same id |
| F6-RECORD-DRIFT | v2 kill kept | 1 RECORD-SHA-MISMATCH | pass | exit 1 same id |
| F7-TILDE-FENCE | v3 refuses, v2 accepted | 1 CORRECTION-IN-FENCE | pass | exit 0 (accepts) |
| F8-BT4-PARITY | v3 refuses, v2 parity-misparsed | 1 CORRECTION-IN-FENCE | pass | exit 0 |
| F9-HTML-COMMENT | v3 refuses, v2 accepted | 1 CORRECTION-IN-FENCE | pass | exit 0 |
| F10-STRADDLE | v3 refuses straddle, v2 blind | 1 ZONE-TOKEN-STRADDLES-EDGE | pass | exit 0 (multi=0 — v2 ignored it; SITE lines show stated=78, filed=yes both sites) |
| F11-BOGUS-RECOMP | v3 refuses, v2 silent | 1 BOGUS-RECOMPUTED | pass | exit 0 mismatches=1 filed=1 unfiled=0 (see N3) |
| F12-LOG-UNFILED | v3 refuses, v2 never read LOG/README | 1 UNFILED-SOURCES-ANNOTATION | pass | exit 0 |
| F12b-LOG-FILED | green under both arms | 0 / - | pass | exit 0 |

C2 (my selftest + fresh arms): FH 0/-, FH2 0/-, FA1 1 ROWS-UNSORTED, FA2 1 COMMENT-AMBIGUOUS-NAME,
FA3 1 CAPTURE-RECEIPT-MISMATCH (all carry-over, both arms agree); FA4 1 COMMENT-AMBIGUOUS-NAME
(v2-arm exit 0), FA5 1 RECEIPT-UNKNOWN-KEY (v2-arm exit 0), FA6 1 CAPTURE-CRLF **first finding**
(v2-arm exit 1 but first finding CAPTURE-RECEIPT-MISMATCH — the disclosed cascade), FA7 1
CAPTURE-RECEIPT-MISMATCH (both arms), FA8 exit 1 class rule (both arms). Prereg sentence, TSV row
and selftest result agree on every row.

## Task 3 — control audit

(a) Absent-instrument re-derived (my own `git cat-file -e` at base fe12daad…):
```
fatal: path 'census/round-54/c1-counter.py' exists on disk, but not in 'fe12daad2549f534650d406ebdbac9113d59313f'  → rc=128
fatal: path 'census/round-54/c2-counter.py' exists on disk, but not in 'fe12daad2549f534650d406ebdbac9113d59313f'  → rc=128
```
Right base, right paths; the controls name exactly these.
(b) v2-arm acceptance re-derivation: I rebuilt all 23 fixtures with the frozen builder and ran
`bash census/round-54/fixtures/run-matrix.sh <scratch> <out>`:
- `diff` committed vs fresh manifest (name,base,tip,record_sha256): **MANIFEST-REVS-IDENTICAL** —
  every fixture rev reproduces (R10 determinism proven live, not just asserted).
- `diff` committed vs fresh: c1-matrix-v2 **IDENTICAL**, c1-matrix-v3 **IDENTICAL**, c2-matrix-v2
  **IDENTICAL**, c2-matrix-v3 **IDENTICAL**.
- Control embedded rows vs my fresh v2 rows (field-cut diff): **C1-CONTROL-ROWS-MATCH-FRESH-V2**,
  **C2-CONTROL-ROWS-MATCH-FRESH-V2** — the controls' dry-run rows (e.g. F7 rev 2daa874557c2, FA4
  e0aabc60013d) equal the revs my rebuild produced.
(c) Last lines: `tail -1` of both control files → `EXIT=1` / `EXIT=1`. ✓
Wrong-pin refusals (controls §2) reproduced: wrong builder pin (C1) and wrong expected pin (C2)
both → `CANNOT-EVALUATE PIN-MISMATCH …`, rc=2, matching the embedded lines.

Real-lane recompute commands (prereg's, with absolute --root): C1 → rc=0, output identical to
`records/c1-tip.txt` (sites=2 mismatches=2 filed=2 unfiled=0 … straddle=0 bogus=0 logunfiled=0
logrecomp=0; filings re-derived: LOG.md:2527 and corpus/README.md:870 carry the stale `274 -> 275`
annotations; SCORECARD.md:1268,1270 carry `R53-CORRECTION … stale=274->275 recomputed=198->199`).
C2 → rc=0 `… receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e` over the fresh capture
(capture absent at base, rc=128 — new work this round); FLEET_HEAD 3b0d5329147d… resolves in the
fleet repo (`git -C <fleet> cat-file -e` → rc=0; fleet HEAD has since moved on).

## Task 4 — routed-items ledger (R1–R13 + verifier items 1/3/4)

| item | disposition this round |
|---|---|
| R1 fence grammar (tilde/bt4-parity/HTML) | CLOSED — F7/F8/F9; v3 CORRECTION-IN-FENCE; v2 arm accepts all three |
| R2 zone edge | CLOSED (straddle: F10 ZONE-TOKEN-STRADDLES-EDGE) + named-limit-disclosed ("the zone stays frozen at 32 chars (a token wholly beyond it is still not an annotation)") |
| R3 bogus recomputed | CLOSED — F11 BOGUS-RECOMPUTED (mechanism wording defect N3 routed) |
| R4 `#`-shape (space names) | CLOSED — FA4; matcher widened to any `#`-line with ≥5 tabs |
| R5 receipt extras + CRLF naming | CLOSED — FA5 RECEIPT-UNKNOWN-KEY, FA6 CAPTURE-CRLF printed first; capture-side unknown keys still ignored — named-limit-disclosed ("the routed item names the receipt only") |
| R6 tool pin by argument | CLOSED — `--tool-sha256`; TOOL-SHA-ARG-MISMATCH probe below; tip receipt passes pin. Kill-rule citation defect N2 routed |
| R7 branch coverage M-F1/M-F2 | CLOSED — FA7/FA8/FH2 committed; both arms kill FA7/FA8, both keep FH2 (my fresh matrices) |
| R8 builder hardening | CLOSED — builder `run()` has timeout=120 and every git call carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null` (read in frozen bytes); rebuild clean |
| R9 oracle/builder pinning (verifier item 4) | CLOSED — prereg pins both digests; selftest verifies pins BEFORE exec; wrong-pin rc=2 refusals reproduced |
| R10 fixture rev determinism | CLOSED — GIT_*_DATE pinned; my rebuild reproduced all 23 revs exactly |
| R11 receipt binds bytes not path | NAMED-LIMIT-DISCLOSED — prereg: "the receipt binds capture-to-receipt consistency and bytes, not execution or the capture's path" ✓ |
| R12 exit-code ambiguity | DISCLOSED-IMPLICITLY ONLY — no named-limit line in the r54 prereg; only the c2 docstring documents exit 1 (PRISTINE FAIL) vs exit 2 (bad rev). Disclosure gap → N6 |
| R13 wording (verifier item 3) | CLOSED — see task 6 |
| verifier item 1 (report Mistakes-row count discipline) | UNADDRESSED at freeze — binds the r54 closure report (round in flight); no r54 artifact yet → N7 carried |
| verifier item 2 | not the lane's (protocol integrator); out of my ledger per assignment |

## Task 5 — vacuity probes

(a) **v2 arm kills no NEW attack.** My fresh v2-arm runs: exit 0 on all of F7, F8, F9, F10, F11,
F12, F12b (C1) and FA4, FA5 (C2) — byte-identical to the committed v2 matrices. Not vacuous.
(b) **Honest state at base.** C1: already green at base — my probe
`c1-counter.py v3 --rev fe12daad… --base 9bf9234a…` → rc=0, `unfiled=0 … logunfiled=0 logrecomp=0`
(the r53 filings predate the round). Disclosed only implicitly ("the r52 filing … stays filed";
"keep their pair filings") — unlike r53, whose control carried the explicit line; strength note,
not a defect. C2: not green at base — capture+receipt absent at fe12daad (rc=128); the round-54
capture is new committed work (bfdbb336). No claim rests on a pre-green state being new.

Probes beyond the frozen fixtures (all my own, scratch-only):
- Wrong `--tool-sha256` on the real capture → `FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000
  observed=e7e79952f783`, `tool_pin=FAIL`, rc=1. The pin is able to fail — but see N2.
- logrecomp arm: F12b copy with filing `recomputed=1->2` → `FINDING SOURCES-RECOMPUTE-MISMATCH
  LOG.md:2 filing recomputed=1->2 but the census grep recomputes 3->3`, rc=1. Works, but **no
  committed fixture exercises it** (N5).
- stale-pair arm: filing `stale=1->2` for a `3 -> 4 rows` annotation → refused as
  UNFILED-SOURCES-ANNOTATION, rc=1. The docstring's `SOURCES-ANNOTATION-DRIFT` class is never
  emitted (N1).
- Standing spot-check (one of the set, reported-not-claimed): frozen r53 c2 counter verifies the
  r53 capture at a1156d8579847dccc9185cc677c4e23e277e7123 → rc=0 `receipt=ok sorted=ok`.

## Task 6 — wording

Confirmed. C1 title: "…the annotation-agreement counter v3 **instruments** the r53 routed filing
surfaces"; C1 target: "**adds** four named surfaces"; C2 title: "…**instruments** receipt grammar,
CR naming, and argument pinning". The only "closes" in the prereg is inside the wording-discipline
sentence itself (line 23). The two control artifacts are named distinctly throughout:
"absent-instrument control" (the PRISTINE FAIL receipt) vs "v2-arm acceptance control" (the frozen
r53 counters' rows). R13 and verifier item 3 are closed by these bytes.

## Named limits / defects found (route to r55; bytes frozen, never edited)

- **N1** c1 v3 docstring (line 28) names `SOURCES-ANNOTATION-DRIFT`; grep over the frozen bytes
  shows no code path emits it — a filing whose stale pair mismatches its annotation is refused as
  UNFILED-SOURCES-ANNOTATION (my probe-stale receipt). Docstring-vs-code defect.
- **N2** C2 kill rule: "the --tool-sha256 pin passing with wrong tool bytes (shown able to fail by
  a wrong-pin refusal in the selftest)". The committed c2-selftest.txt contains no --tool-sha256
  case (the selftest harness passes no pin for any of the 10 fixtures); the committed wrong-pin
  refusals are --builder-sha256 (C1 control) and --expected-sha256 (C2 control). The refusal is
  real (my probe: rc=1, TOOL-SHA-ARG-MISMATCH, tool_pin=FAIL) — but the prereg's cited
  demonstration location is false as written.
- **N3** C1 prereg F11 parenthetical "…but mismatches=0/unfiled=0 hid the cause": the actual v2
  F11 SUMMARY (committed control row AND my fresh run) is `mismatches=1 filed=1 unfiled=0` — the
  cause is hidden by the matched-but-unfiled S1 tuple, not by mismatches=0. Mechanism clause false.
- **N4** C1 control (4): "filed=no is not printed" — v2 on F11 verbatim prints
  `SITE path=SCORECARD.md line=5 stated=79 recomputed=79 status=match filed=no`. False as written.
- **N5** The SOURCES-RECOMPUTE-MISMATCH refusal arm has zero committed-fixture coverage (the r53
  M-F1/M-F2 shape again). Functional per my probe; kill-power not pinned by the selftest. Route as
  a branch-coverage item.
- **N6** R12 (exit-code ambiguity) has no named-limit line in the r54 prereg; behavior is only
  described in the c2 docstring (exit 1 PRISTINE FAIL vs exit 2 bad rev). Disclosure gap vs R11,
  which is explicitly disclosed.
- **N7** r53 verifier item 1 (report count accuracy: counts carry their command; re-count next
  time) is unaddressed by any committed r54 artifact — it binds the r54 closure report, still in
  flight at my read.

## Honesty / coverage of my own run

- Exercised: both selftests with pins; all four matrix arms fresh over my rebuilt fixtures;
  control re-derivations ((a)(b)(c) + both wrong-pin refusals); both real-lane recompute commands;
  v3-at-base probe; wrong-tool-pin probe; logrecomp + stale-pair probes; v2 raw SITE inspection on
  F10/F11; pin/sha re-derivations; r53-c2 standing spot-check.
- Not exercised (standing checks reported-not-claimed by the round, not mine to claim): r52
  counters, r53 c1 standing re-run, r46 landing suite, census gates.
- Tooling: no installs/upgrades (operator authorization unused); host `python3` and `git` only.
- Scratch: /fast/scratch/hyaku/souji-r54/S54critic01/ — receipts copied to
  .ufo/waves/round-54/w1/S54critic01/receipts/, then deleted before yield (deletion verified in
  the yield record).
