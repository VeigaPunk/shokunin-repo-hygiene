# S56revenger01 — routed-item audit of the round-55 record against the round-56 frozen bytes

Seat: S56revenger01 (revenger, routed-item audit). Role bounds: read-only to the lane; no
subagent dispatch; nothing committed; no mutating git/jj anywhere.
Measured (frozen) revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83`
(base `fafe371694fea41c5d23f63083865d5ccf3f1d36`). Post-freeze receipt commit inspected:
`148f39a6c902b27e997ac36d395735406d3ad9de`. Lane HEAD at audit time: `148f39a6`.
Scratch: `/fast/scratch/hyaku/souji-r56/S56revenger01/` (deleted before yield; receipts copied
to `receipts/`). Disk guard: `/fast/scratch/hyaku` 50% used, 406.5G free; `/tmp` 25%, 95.9G free.

Inputs read: `census/round-56/preregistration.txt`; `corpus/lessons/round-55.md` (§§ Routed to r56,
Errata, Named limits…, Mistakes, Addendum); `corpus/lessons/round-56.md`; frozen counters,
builder, runner, expected TSVs at `cce21b55`; committed dry-run matrices and probe receipts;
commit `148f39a6` receipts. No file in the lane was written outside
`.ufo/waves/round-56/w1/S56revenger01/` and the seat's named wave-root report path
`.ufo/waves/round-56/w1/S56revenger01.md`.

All eight pins verified before any probe (`receipts/pins.txt`):

```
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  census/round-56/c1-counter.py
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  census/round-56/c2-counter.py
2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a  census/round-56/fixtures/build-fixtures.py
a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3  census/round-56/fixtures/run-matrix.sh
48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb  census/round-56/records/c1-selftest-expected.tsv
90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3  census/round-56/records/c2-selftest-expected.tsv
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
EXIT=0
```

## 1. Intent check — new counter versions only; r55 bytes untouched

`git diff --stat fafe3716..cce21b55 -- census/round-55` is **empty** (no round-55 byte changed;
the v4 counters still hash to the pins in `census/round-55/preregistration.txt` lines 37/130).
The freeze diff adds exactly two counter files, `census/round-56/c1-counter.py` and
`census/round-56/c2-counter.py`, plus the round-56 builder/runner/prereg/records/controls/sources;
the only other paths are `corpus/SOURCES.md` (S277 `used-by`), the new knowledge entry and the
round-56 lesson (`receipts/intent-check.txt`):

```
# command: git diff --stat fafe3716..cce21b55 -- census/round-55
# (empty above = unchanged)
A	census/round-56/c1-counter.py
A	census/round-56/c2-counter.py
A	census/round-56/fixtures/build-fixtures.py
A	census/round-56/fixtures/run-matrix.sh
A	census/round-56/preregistration.txt
...
M	corpus/SOURCES.md
A	corpus/knowledge/correction-filing-html-comment-opener.md
A	corpus/lessons/round-56.md
EXIT=0
```

This matches the r55 lesson sentence "the frozen v4 bytes are not edited; fixes are a future
counter generation": the v5 pair is the only new counter generation, and the v4 pair is the
do-nothing before arm. `c1-tip-v4-before-arm.txt` and `c2-tip-v4-before-arm.txt` exist as the
before-arm receipts on the real lane. **No counter outside round 56 was added or modified.**

## 2. Item table

Classification policy (states the four assigned labels plus the compound case the routed list
itself uses): **INSTRUMENTED** = a committed r56 fixture/selftest arm/receipt demonstrates the
surface, named; **NAMED-LIMIT** = recorded as a limit in the r56 lesson's "Named limits carried
into r57" or in the frozen r56 counter docstrings' named-limits paragraphs; **OPEN** = no r56
fixture and no r56 limit text (r57 owner named); **REPAIRED-BY-DISCLOSURE** = closed by corrected
disclosure text (r55 erratum and/or r56 docstring), no counter behaviour change; **PARTIAL** =
subshapes of one id have different dispositions; the residual is listed in §3.
Ids that name one surface are merged in one row and both ids are shown.

Exit transitions below are computed from the committed dry-run matrices at `cce21b55`
(`receipts/matrix-setdiff.txt`); official matrices at `148f39a6` are byte-identical to them
(`receipts/official-receipts.txt`).

| # | id | status | evidence pointer |
|---|---|---|---|
| 1 | RD-A (receipt key first char digit/underscore; routed 1) | INSTRUMENTED | `FC1-UNDERSCORE-KEY`, `FC2-DIGIT-KEY`: v4 exit 0 → v5 exit 1 `RECEIPT-UNKNOWN-KEY` (dry-run matrices; `receipts/c2-selftest.txt` rows FC1/FC2). Grammar `c2-counter.py:115` `[A-Za-z0-9_][A-Za-z0-9_]*`; probe `# _KEY=x`/`# 1KEY=x` match (`receipts/grammar-probe.txt`). |
| 2 | N1 / D14 / D15 (pair filing hidden in fence/comment; routed 2) | INSTRUMENTED | `F24-PAIR-HIDDEN-FILING`: v4 exit 0 → v5 exit 1, first finding `UNFILED-SOURCES-ANNOTATION`, second `PAIR-FILING-HIDDEN`, `pairhidden=1` (`receipts/surfaces-v4-v5.txt`). Visible-filing filter `c1-counter.py:466`. |
| 3 | A09–A13 (fence closer + exotic whitespace; routed 3) | NAMED-LIMIT | r56 lesson "Named limits carried into r57" bullet 3: "Fence-closer lines are rstripped … (routed A09–A13 … not instrumented in v5)"; same in `c1-counter.py:117-119`. Probe: `~~~` + VT closes the fence (`hidden=[2]`, `receipts/grammar-probe.txt`). |
| 4 | E09 / E10 (fence inside a list item; routed 4) | OPEN | No r56 fixture, no r56 limit text. `hidden_lines()` recognises fences only after absolute 0–3 spaces (`c1-counter.py:233-235`); probe ``- ```text`` opens no fence and the later bare ``` run hides the following correction (`hidden=[4]`, `receipts/grammar-probe.txt`). Owner: r57 L1, C1 counter v6. |
| 5 | C04 / C07 (INERT check reads occurrence 1 only; routed 5) | OPEN | `c1-counter.py:405` `ok_tokens, straddle = zones[0]` for the INERT judgement while `stated` comes from the first in-zone token of any occurrence (`c1-counter.py:351-378`); r55 receipts `C04`/`C07` (`census/round-55/wave/w1/S55reviewer01.md:109,112`) still describe the false refusal. No r56 text. Owner: r57 L1, C1 v6. |
| 6 | N4 / PTR wording (ERRATUM-R55-2; routed 6) | REPAIRED-BY-DISCLOSURE | `corpus/lessons/round-55.md` ERRATUM-R55-2 (dot-before-colon + digit-after reading, `2.5:1` still exempts); v5 docstring `c1-counter.py:105-107` restates it; probe `2.5:1`/`v2.1:3`/`x.md:1` exempt (`receipts/grammar-probe.txt`). No counter change. |
| 7 | N2 (only the first pair annotation per line; routed 7) | OPEN | `PAIR_ANNOT_RE.search(ln)` `c1-counter.py:455`; probe `1 -> 2 rows then 999 -> 1000 rows` matches only `('1','2')` (`receipts/grammar-probe.txt`). No r56 text. Owner: r57 L1, C1 v6. |
| 8 | N3 (prose counts/separators invisible; routed 7) | OPEN | Grammar `c1-counter.py:159` is exactly `->`/`→` + optional `rows`; probe `999 => 1000`, `999 —> 1000`, `999 to 1000` all no-match. No r56 text. Owner: r57 L1, C1 v6. |
| 9 | D07 / D08 (separators `=>`, `—>`; routed 7) | OPEN | Same probe and regex as N3. No r56 text. Owner: r57 L1, C1 v6. |
| 10 | D12 (pair without the `corpus/` prefix; routed 7) | OPEN | Scan gate `'corpus/SOURCES.md' not in ln` `c1-counter.py:450`; probe `SOURCES.md 999 -> 1000 rows` matches the pair but carries no literal. No r56 text. Owner: r57 L1, C1 v6. |
| 11 | D16 (4-space-indented pair line over-refused; routed 7) | OPEN | `hidden_lines()` hides fences/comments only, so a 4-space pair line is scanned (`receipts/grammar-probe.txt`); no r56 text. Owner: r57 L1, C1 v6. |
| 12 | B07 (bare filing + trailing text unlexed; routed 7) | OPEN | `CORR_RE` `c1-counter.py:156` is anchored `\s*$`; probe `… recomputed=2 --> note` does not lex (while `… -->` does). No r56 text. Owner: r57 L1, C1 v6. |
| 13 | F01 (`\d` accepts non-ASCII digits; routed 7) | OPEN | `ANNOT_RE`/`CORR_RE`/`PAIR_ANNOT_RE` use `\d`; probe fullwidth `７８ -> 79` matches. No r56 text. Owner: r57 L1, C1 v6. |
| 14 | RD-B (KV receipt lines outside the key grammar; routed 8) | PARTIAL — INSTRUMENTED for `KEY=` (via S55-S5/FC3); OPEN residual for `KEY-1=`, `KEY.1=`, `KEY=x y` | Probe `# KEY=` matches (value `\S*`, `c2-counter.py:115`) and is refused as unknown; `# KEY-1=x`, `# KEY.1=x`, `# KEY=x y` are `NO-MATCH (silently ignored)` (`receipts/grammar-probe.txt`). Residual owner: r57 L1, C2 v6. |
| 15 | RD-C (capture header stricter than receipt; routed 8) | NAMED-LIMIT | v5 `c2-counter.py:74-76`: "unknown `# KEY=VALUE` lines in the CAPTURE header are still ignored (the routed items name the receipt only)". Header grammar `c2-counter.py:202` takes only `# KEY=value` (single space, exact case); probe `#  ENTRIES=3`, `# ENTRIES: 3`, `# entries=3` ignored (`receipts/grammar-probe.txt`). |
| 16 | RD-D (malformed expected TSV traceback, not rc 2; routed 8) | OPEN | `c2-counter.py:375` `int(f[1])` is unguarded; probe with `FZ-BAD\tnotanint\t-` → `ValueError` traceback, `EXIT=1` (`receipts/rd-d-malformed.txt`). No r56 text. Owner: r57 L1, both selftests. |
| 17 | RD-E (selftest `-` wildcard skips the finding check; routed 8) | OPEN | `c1-counter.py:574` and `c2-counter.py:399` `want_find in ('', '-')`; probe: F2 expected finding `-` while the counter printed `MULTIPLE-ANNOTATIONS` → pass (`receipts/rd-e-wildcard.txt`). No r56 text. Owner: r57 L1, both selftests. |
| 18 | selftest row-set assertion (mutation01 C2-17/C2-18; routed 9) | PARTIAL — INSTRUMENTED in C2; OPEN for C1 | C2: `c2-counter.py:403-413`; mutation receipt `row-omission-v5.txt` (drop FA9 → `SELFTEST-ROW-MISMATCH`, `SELFTEST fail cases=17`, EXIT=1) and my mutant dropping FC1 → same class (`receipts/c2-rowset-mutant.txt`). C1: no row-set loop (`c1-counter.py:554-578`); probe expected TSV + unrun `FZ-EXTRA-ROW` → `SELFTEST pass cases=33`, EXIT=0 (`receipts/rowset-extra-row.txt`). C1 residual owner: r57 L1, C1 v6. |
| 19 | S4 (builder `--work` accepts a relative path; routed 10) | OPEN | Builder `main()` `work = Path(ns.work); if not work.is_dir()` (no absolute-path guard); probe `build_one('F1-HONEST-TIP', Path('relbase'))` builds `relbase/relbase/F1-HONEST-TIP/.git` then `RuntimeError: fixture cmd failed … rev-parse` (`receipts/s4-relative-work.txt`). No r56 text. Owner: r57 L1, builder v3. |
| 20 | S5 (`PRISTINE FAIL` promised but not emitted; routed 10) | REPAIRED-BY-DISCLOSURE | v5 C1 docstring contains no `PRISTINE` token (grep over frozen bytes); C2 emits it honestly (`c2-counter.py:168` `PRISTINE FAIL FLEET-CENSUS-ABSENT`) and its exit legend names it (`c2-counter.py:82`). Observed `EXIT=1` on an absent capture (`receipts/c2-absent-capture.txt`). Docstring-only; no fixture. |
| 21 | N6 (revenger: exit-code legend as a named limit; routed 10) | REPAIRED-BY-DISCLOSURE | Exit legends now explicit: `c1-counter.py:125-127`, `c2-counter.py:82-83` ("Exit 1: any finding (including capture absent: PRISTINE FAIL). Exit 2: could-not-evaluate…"). No prereg named-limit line (r56 prereg has no Named-limits section) — recorded as a residual wording gap, not a behaviour gap. |
| 22 | receipt item / N15 (every cited receipt prints its exit code; routed 11) | INSTRUMENTED | Prereg C1 T8 / C2 T7. Committed receipts all end `EXIT=`: `c1-selftest.txt`, `c2-selftest.txt` (`EXIT=0`), `c1-tip.txt`, `c2-tip.txt` (`EXIT=0`), both before-arm files, `landing-suite-standing.txt` (`EXIT=2`), the untracked row-omission pair (`EXIT=0`/`EXIT=1`) — `receipts/official-receipts.txt`. Scoped note: the four matrix TSVs carry a per-row `exit` column and no `EXIT=` line; `run-matrix.sh` echoes `rc=` to stdout. |
| 23 | ERRATUM-R55-1 / form-feed shape (routed 12a) | INSTRUMENTED | `F7-FF2` (two `\x0c` lines above `~~~`): v4 and v5 both exit 1 `CORRECTION-IN-FENCE` (`receipts/surfaces-v4-v5.txt`); builder branch `elif name == 'F7-FF2'`. The r55 `F7-FF` fixture stays vertical tab (frozen; name/byte mismatch persists by design). |
| 24 | numstat LF-only parse (routed 12b) | INSTRUMENTED (hardening; not a reachable lane verdict) | `numstat_deletions` splits `stdout.decode(...).split('\n')` `c1-counter.py:287`; committed `census/round-56/records/quotepath-differential.txt` shows v4 `[('nel',1),…]` vs v5 `[('nel\x85name',1),…]`; prereg declares it a differential, not a claim row. |
| 25 | N5 (only two annotation sites) | NAMED-LIMIT | r56 lesson "Named limits carried into r57" bullet 1 ("The counters read two annotation sites (SCORECARD.md and census/round-51/preregistration.txt)…"). |
| 26 | N6 (critic: receipt lines outside the key grammar are silent) | PARTIAL — INSTRUMENTED for the empty-value subshape (FC3); OPEN residual for hyphen/colon/space-value | Same evidence as RD-B: probe `# KEY-1=x`, `# KEY.1=x`, `# ENTRIES: 999`, `# BUILD-HOST=fixture`, `# BUILD HOST=fixture` all `NO-MATCH (silently ignored)`; the C2 docstring does not name this receipt surface. Residual owner: r57 L1, C2 v6. |
| 27 | N7 (first unknown receipt key only) | NAMED-LIMIT | r56 lesson bullet 6 ("The receipt grammar still reports only the FIRST unknown key"). |
| 28 | N8 (beyond-zone sole annotation exits 2) | NAMED-LIMIT | v5 `c1-counter.py:104-106` ("a token wholly beyond it … still forces exit 2 when no other annotation exists on the line"); code path `c1-counter.py:360-362`. r56 lesson silent. |
| 29 | N9 (wording: "every occurrence" → "every in-zone annotation") | OPEN | v5 `line_zones` docstring still reads "Per-occurrence … after EVERY occurrence of the anchor on the line" (`c1-counter.py:243-247`); the lesson does not restate N9. Owner: r57 L1, C1 v6 docstring. |
| 30 | N10 (pair annotations outside LOG.md/README invisible) | NAMED-LIMIT | r56 lesson bullet 1 ("pair annotations in LOG.md and corpus/README.md only"). |
| 31 | N11 (v4 F10 SUMMARY count drift unlisted) | OPEN | Verified F10 SUMMARY is `mismatches=1 filed=1 … inert=1 straddle=1` under both arms (only the new `pairhidden=` field differs); no r56 lesson/prereg line records the v3→v4 count change. Owner: r57 L1, lesson/prereg named limits. |
| 32 | N12 (runner names a row by the second token, unchecked) | OPEN | `run-matrix.sh` `awk '/^FINDING /{print $2; exit}'` unchanged; its comment asserts the §5.2 rule but adds no id check; no r56 limit text. Owner: r57 L1, runner v2. |
| 33 | S55-S1 (NUL silent shape / binary numstat naming) | INSTRUMENTED | `F28` v4 exit 0 → v5 exit 1 `CORRECTION-FILE-BINARY` (`c1-counter.py:327`); `F27` v4 `DELETED-LINES deletions=-1` → v5 `DELETIONS-UNREADABLE-BINARY` (`c1-counter.py:433`). Both in the committed selftest and matrices. |
| 34 | S55-S2 (four-space comment opener regression) | INSTRUMENTED | `F26`: v4 exit 0 → v5 exit 1 `UNFILED-SOURCES-ANNOTATION`; opener rule `if indent <= 3 and stripped.startswith('<!--')` `c1-counter.py:237`; probe four-space opener hides nothing (`receipts/grammar-probe.txt`). |
| 35 | S55-S3 (corrections outside lexing tolerance never audited) | OPEN | Probe: 4-space-indented and tab-prefixed `R52-CORRECTION` lines do not lex (`CORR_RE=False`, `receipts/grammar-probe.txt`); the v5 named limits do not restate S55-S3. Owner: r57 L1, C1 v6. |
| 36 | S55-S4 (`__pycache__` written inside the lane without `-B`) | OPEN (low; mitigated) | No `dont_write_bytecode`/`sys.flags` guard in either v5 counter or the builder (grep); all committed invocations use `python3 -B` (prereg commands, runner). No r56 limit text. Owner: r57 L1, builder/counter hardening. |
| 37 | S55-S5 (unknown key with empty value silently ignored) | INSTRUMENTED | `FC3-EMPTY-VALUE-KEY`: v4 exit 0 → v5 exit 1 `RECEIPT-UNKNOWN-KEY`; regex value group `\S*` `c2-counter.py:115`; probe `# BUILDHOST=` matches as unknown. |
| 38 | ERRATUM-R55-3 (hand-written control labels) | REPAIRED-BY-DISCLOSURE | r55 lesson Mistakes fix column ("r56 controls print observed output only"); r56 controls `controls/c1-absent.txt`, `controls/c2-absent.txt` carry `observed-stderr:` and `observed-rc: 128` only. |
| 39 | ERRATUM-R55-4 (pre-flight wrong `--base`) | REPAIRED-BY-DISCLOSURE | r56 `c1-tip.txt` reads `base=fafe371694fe`, matching the prereg recompute command; no r56 pre-flight receipt with a foreign base exists. |
| 40 | ERRATUM-R55-5 (c2-tip scope / empty ENTRIES) | REPAIRED-BY-DISCLOSURE | r56 `c2-tip.txt` reads `entries=49 rows=49 … receipt=ok tool_pin=ok`, `EXIT=0`, over the corrected receipt pinned `479b2715…`; before-arm `c2-tip-v4-before-arm.txt` is byte-identical. |
| 41 | P1 (widen the receipt key charset to hyphens) | OPEN | Proposal not applied: probe `# BUILD-HOST=fixture` is `NO-MATCH (silently ignored)`; no r56 text. Owner: r57 L1, C2 v6. |

Count: 41 rows covering every id named in the assignment (RD-A; N1/D14/D15; A09–A13; E09/E10;
C04/C07; N2; N3; N4/PTR; D07/D08; D12; D16; B07; F01; RD-B/C/D/E; selftest row-set; S4; S5; N6
(revenger); receipt item; form-feed; numstat; N5; N6 (critic); N7–N12; S55-S1..S55-S5; P1;
ERRATUM-R55-1..5). The compound families (A09–A13, D07/D08, E09/E10, C04/C07, N1/D14/D15,
RD-A…RD-E, S55-S1…S55-S5, ERRATUM-R55-1…5) share one row each and both ids are shown.
**Unclassified: 0.**

## 3. OPEN list (r57 owner named)

Residual OPEN rows and the C1 residual of row 18:

| id | open surface | r57 owner |
|---|---|---|
| E09, E10 | a fenced block inside a list item hides nothing (a correction rendered as code is judged visible); a later bare fence run then hides real content | r57 L1 — C1 counter v6 (container-indent model) |
| C04, C07 | INERT judgement reads `zones[0]` while `stated` comes from any occurrence (honest filing refused) | r57 L1 — C1 v6 |
| N2 | only the first pair annotation per line is scanned | r57 L1 — C1 v6 |
| N3, D07, D08 | `=>`, `—>`, `to` and prose counts are invisible to the pair grammar | r57 L1 — C1 v6 |
| D12 | a pair without the literal `corpus/SOURCES.md` is never scanned | r57 L1 — C1 v6 |
| D16 | a 4-space-indented pair line (indented code) is scanned, over-refusing | r57 L1 — C1 v6 |
| B07 | a bare filing followed by ` --> note` is silently unlexed (UNFILED with no FINDING id) | r57 L1 — C1 v6 |
| F01 | `\d` accepts non-ASCII digits in filings/annotations | r57 L1 — C1 v6 |
| RD-B residual (also critic N6 residual) | receipt lines `KEY-1=x`, `KEY.1=x`, `KEY=x y`, `KEY: value` are silently ignored | r57 L1 — C2 v6 |
| RD-D | a malformed expected TSV crashes the selftest with a traceback instead of rc 2 | r57 L1 — both selftests |
| RD-E | the expected-finding `-` wildcard skips the finding comparison | r57 L1 — both selftests |
| selftest row-set, C1 half | C1's selftest does not assert every expected row ran (`FZ-EXTRA-ROW` unrun → pass) | r57 L1 — C1 v6 |
| S4 | builder `--work` accepts a relative path and builds `rel/rel/<name>` | r57 L1 — builder v3 |
| N9 | docstring wording still says "every occurrence" instead of "every in-zone annotation" | r57 L1 — C1 v6 docstring |
| N11 | the v3→v4 F10 SUMMARY count drift is still not a named limit | r57 L1 — lesson/prereg named limits |
| N12 | the matrix taker does not validate that the second token is a finding id | r57 L1 — runner v2 |
| S55-S3 | corrections outside the lexing tolerance (4-space indent, tab, nested comment) are never audited | r57 L1 — C1 v6 |
| S55-S4 | `importlib`-exec'd builder writes `__pycache__` inside the lane without `-B` | r57 L1 — builder/counter hardening |
| P1 | hyphenated receipt keys are silently ignored | r57 L1 — C2 v6 |

## 4. New findings from this audit (receipts embedded)

**F1 (LOW, documentation, ATTACK-FOUND).** The frozen v5 C1 docstring's named-limits paragraph
contradicts the implemented HTML-comment rule and the round's own F29 fixture:

> `c1-counter.py:113-116`: "… a line whose prose merely mentions `<!--` still opens a region —
> the real lane's own SCORECARD.md hides its tail this way, disclosed"

The same docstring states at line 51 "v5 over-hide repair (F29): an HTML comment region opens only
on a line that begins with `<!--`", and `hidden_lines()` at lines 207-210 says "a prose sentence
that mentions `<!--` mid-line opens no region (v5 F29 repair); a one-line comment hides only its
own line". Behaviour and the committed probe agree with the repair, not the named-limit
sentence: F29 is exit 0 under v5, and `census/round-56/records/probe-real-scorecard-hidden-tail.txt`
records `hidden_v4=14 hidden_v5=0` (v4 hides line 1378→EOF: True; v5: False). Direct probe:

```
prose-midline-mention (F29 class)          hidden=[]
four-space comment opener (F26 class)      hidden=[]
three-space comment opener                 hidden=[1, 2, 3]
EXIT=0
```
(`receipts/grammar-probe.txt`; F29 row in `receipts/c1-selftest.txt`.) No claim predicate moves;
the frozen named-limit text is wrong and will mislead a reader of the v5 bytes. Route: correction
note append-only (frozen bytes cannot be edited) or the r57 lesson.

**F2 (LOW–MEDIUM, harness, ATTACK-FOUND).** The routed selftest row-set item was instrumented in
C2 only. The C1 selftest can print a pass while an expected row never ran:

```
$ python3 -B c1-counter.py --selftest --work … --expected c1-expected-extra-row.tsv
… (33 fixture cases pass; FZ-EXTRA-ROW never runs)
SELFTEST pass cases=33
EXIT=0
```
(`receipts/rowset-extra-row.txt`; the expected copy appends `FZ-EXTRA-ROW\t1\tSOME-FINDING`.) The
C2 check kills the equivalent mutation (`receipts/c2-rowset-mutant.txt`:
`SELFTEST-ROW-MISMATCH expected row did not run: FC1-UNDERSCORE-KEY`, `SELFTEST fail cases=17`,
`EXIT=1`). Listed as the C1 residual in §3. No frozen claim is touched (C1 T6 asserts only
`SELFTEST pass cases=33`, which holds).

**F3 (INFO, receipt format).** C1 T8's literal `EXIT=` line holds for the selftest/tip/before-arm/
standing receipts but not for the four matrix TSVs (per-row `exit` column; runner echoes `rc=` to
stdout, not captured in the TSV). If T8 is read as "every receipt the claim cites", the v4 arm TSV
cited as the C1 control is the one exception; the per-row exit column is stronger evidence than a
single line, so this is recorded as scope, not a kill.

**F4 (MEDIUM, record accuracy; cross-referenced to critic01).** `census/round-56/records/landing-suite-standing.txt`
at `148f39a6` records the standing-check attempt failing, not passing:

```
usage: c1-counter.py [-h] --root ROOT --rev REV [--work WORK]
c1-counter.py: error: unrecognized arguments: --scratch /fast/scratch/hyaku/souji-r56/L1/off/c1
EXIT=2
```

while the prereg's standing-checks section says "The standing landing-suite counter
census/round-46/c1-counter.py at the round tip (exit 0)". The r46 CLI takes `--work`, not
`--scratch`. The lane is already correcting this during the wave (an untracked
`landing-suite-dirty-refusal.txt` records `COULD-NOT-EVALUATE dirty worktree at run time: 2
unexpected rows`, `EXIT=2`); critic01 routed the same item. Standing checks are "reported, not
claimed", so no claim predicate moves. Recorded here for completeness, not claimed as a new kill.

**F5 (INFO, [INFERENCE]).** The r56 lesson says "freeze commit in LOG.md", but `LOG.md` at
`cce21b55` contains no r56 freeze row. The r55 precedent (`f9da665e`, "round-55: wave w1 evidence …
lesson wave findings …") lands the LOG row at round close, so this is a forward pointer rather
than a divergence. Not a defect.

**F6 (INFO).** `row-omission-v4.txt` (v4 selftest with FC1–FC3 absent from the run list) prints
`SELFTEST pass cases=14`, `EXIT=0`; `row-omission-v5.txt` kills the omission by name
(`SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN`, `EXIT=1`). Both were
untracked working-tree receipts at audit time (sha256 `ace7a189…`, `1e417702…`); my independent
scratch mutant reproduces the v5 behaviour (`receipts/c2-rowset-mutant.txt`).

## 5. Claim evidence re-verified (for the table's INSTRUMENTED rows)

Pinned selftests at frozen bytes (builder + expected pins), reproduced byte-for-byte against the
committed receipts:

```
$ python3 -B c56/c1-counter.py --selftest --work … --builder-sha256 2f26d6aa… --expected-sha256 48a7cc0e…
SELFTEST pass cases=33
EXIT=0
$ python3 -B c56/c2-counter.py --selftest --work … --builder-sha256 2f26d6aa… --expected-sha256 90517c4d…
SELFTEST pass cases=18
EXIT=0
```

(`receipts/c1-selftest.txt`, `receipts/c2-selftest.txt`; both `cmp`-identical to
`148f39a6:census/round-56/records/{c1,c2}-selftest.txt`.) Set comparison from the committed
dry-run matrices:

```
c1 v4-exit0 -> v5-nonzero: ['F24-PAIR-HIDDEN-FILING', 'F26-INDENT4-COMMENT-OPENER', 'F28-NUL-CORRECTION-UNCHANGED']
c1 v4-nonzero -> v5-exit0: ['F29-PROSE-COMMENT-MENTION']
c1 identical exit+finding: 28/33
c1 same-exit finding-changed: [('F27-BINARY-NUMSTAT', ('1','DELETED-LINES'), ('1','DELETIONS-UNREADABLE-BINARY'))]
c2 v4-exit0 -> v5-nonzero: ['FC1-UNDERSCORE-KEY', 'FC2-DIGIT-KEY', 'FC3-EMPTY-VALUE-KEY']
c2 v4-nonzero -> v5-exit0: []
c2 identical exit+finding: 13/16
EXIT=0
```

This is C1 T1/T2/T3/T4/T5 and C2 T1/T2/T3 exactly as written. Real-lane receipts: `c1-tip.txt`
`unfiled=0 … pairhidden=0 recomputed=79 rev=cce21b555a61 base=fafe371694fe EXIT=0` (T7 fields
present); `c2-tip.txt` `entries=49 rows=49 … receipt=ok sorted=ok tool_pin=ok EXIT=0` (T5).
Official matrices at `148f39a6` are byte-identical to the committed dry-runs (all four).

## 6. Confidence and limits of this audit

- **High** for every INSTRUMENTED/REPAIRED row: frozen bytes read at `cce21b55`, probes run from
  scratch copies with `-B` and `TMPDIR` under the seat scratch, receipts embedded.
- **Medium** for the NAMED-LIMIT/OPEN split: the assignment's NAMED-LIMIT definition names the
  r56 lesson or a prereg Named-limits section; the r56 prereg has no such section, so limit text
  found only in the frozen counter docstrings is labelled NAMED-LIMIT with the exact pointer
  (N8, RD-C) and flagged in the row. A stricter reading of the assignment would make those two
  OPEN (docstring-only), which does not change the verdict (both are classified either way).
- **Inference** is marked once (F5, LOG convention).
- No frozen byte was edited; no lane git/jj mutation was run; the only fixture git commands were
  executed by the committed builder inside the seat scratch (allowed by the L1's bounds
  clarification), with every fixture root under `/fast/scratch/hyaku/souji-r56/S56revenger01/`.
- Tools: none installed or upgraded. Python 3.14 stdlib (`python3 -B`), git read-only
  (`show`, `diff`, `rev-parse`, `status`), coreutils (`sha256sum`, `cmp`, `diff`). No pacman,
  no network.

VERDICT: COMPLETE
SEAT-DISPOSITION: ATTACK-FOUND
