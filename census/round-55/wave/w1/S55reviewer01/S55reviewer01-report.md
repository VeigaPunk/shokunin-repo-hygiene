# S55reviewer01 — C1 counter v4 attack report (souji round 55, wave w1)

Target: `census/round-55/c1-counter.py` sha256 `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` (frozen, read only).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, lane tip at dispatch `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`.
Seat dir: `.ufo/waves/round-55/w1/S55reviewer01/` (receipts/ holds one file per state, 66 total).

## Verdict

- 66 attack states, every one run through the frozen counter (exit and first FINDING recorded per state). Classes: 41 CommonMark-consistent or counter-internal, 17 routed-defect-proposal, 7 named-limit-confirmed, 1 render-inconclusive.
- Kill rule, literal reading: no attack exits 0 on the acceptance fixtures' replicas (F7-FF = A01, F13 = C01/C02/C03, F14 = D01, F15 = D04, F16 = D05, F20 = B03, F21 = B01, F22 = D19 all exit 1 as specified). The real F1/F12b/F12c/F17/F18/F19 builds still pass the selftest (27/27 at the pinned bytes). Variant bypasses exist in five families (below); the kill rule's literal scope does not cover them, so I flag them for the L1 rather than call the rule violated.
- One-line model (question 1): the LF-only numbering holds for every separator tested. `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, `\u2028`, `\u2029` and a trailing CR all put the hidden-set and correction numbers on the same physical line (A01-A07, e.g. A03 correction at SCORECARD.md:11 on the physical line 11). No numbering divergence was found.
- The divergence the attacks did find is a different mechanism in the same family as the r54 S1 HIGH. `hidden_lines()` strips closers with Python `str.rstrip()` (which removes `\x0b \x0c \x1c-\x1f \x85 \u2028 \u2029`), while CommonMark allows only spaces and tabs after a closing fence. A closer `~~~` followed by an exotic separator therefore closes the fence in the counter but not in CommonMark. The corrections after it count as visible filings (exit 0), while commonmark.js 0.31.2 renders them as code (A09-A13, routed as FENCE-CLOSER-EXOTIC-WS). The L1 should decide whether this blocks C1; I recommend treating it as HIGH.
- Two more bypass families are the same shape as the r54 over-hide repairs but reversed: a pair filing inside a code fence or an HTML comment counts as a filing (D14, D15; PAIR-FILING-IN-FENCE), and a list-item fence hides nothing (E09, E10; FENCE-IN-LIST-ITEM). The R52 corrections in the same places are refused (F4, F9 shapes), so the pair grammar and the list grammar are inconsistent with the rest of the counter.

## Method

- Pins verified before any probe (all six sha256s match the preregistration). `c1-counter.py --selftest` with the builder and expected pins: `SELFTEST pass cases=27` (`selftest-c1.txt`).
- Real lane at the dispatch tip `3ce0ba03`, with the frozen recompute arguments: exit 0, `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0` (`realtip-c1.txt`). The content-tip leg at `4b10ddd1` was not re-run here; it is the other seat's surface.
- Fixtures: built in scratch with the committed builder's helpers (`init_repo`, `write`, `commit_all`, `RECORD_BODY`, `REGISTRY_3ROWS`, `sc_base_lines`, pinned `T0`/`T1`), imported from the committed `build-fixtures.py` (never edited). Each state's base commit holds the record, SCORECARD, preregistration and a marker; the tip commit adds LOG.md and corpus/SOURCES.md when a state needs them, plus a marker. Commits are additions only, so DELETED-LINES cannot fire and every FINDING is the attack's own. Record bytes are the unchanged RECORD_BODY (pinned sha `d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf`). The driver is `attack.py`; the state builder asserts `git rev-parse --show-toplevel` on each fixture before its first commit.
- Counter invocation, from the lane root with TMPDIR in scratch: `python3 -B census/round-55/c1-counter.py --root <state dir> --rev <tip> --base <base> --record-sha256 d55ffd7f… --sources-rev-before <tip> --sources-rev-after <tip> --scratch <scratch>`. Each receipt in `receipts/` carries the full command, exit, first FINDING, stdout verbatim, and the complete fixture tree at tip (every line shown with `repr`, so `\x0b` and `\r` are visible).
- CommonMark reference for the classification: commonmark.js 0.31.2 (`bun add commonmark@0.31.2` into scratch, npm channel, scratch-only; removed at yield). `check.js` renders every fixture's tip and classifies each correction or pair-annotation line as PROSE, CODE, COMMENT or ABSENT; output in `cm-classes.tsv`. The CommonMark rule statements in this report are my reading of the 0.31.2 spec; the spec page was not opened live in this seat, and the parser behaviour is what I checked against.
- Tool record: commonmark@0.31.2 via bun/npm into scratch (reason: independent reference parser for the fence claims). No pacman, no global install, nothing written to PATH directories.

## Answers to the probe list

(1) Exotic separators. Covered by A01-A07 and A08 (CRLF honest control) and F02 (CR-only file). Numbering holds for all separators. Divergence only in the closer strip (A09-A13). The vertical tab and form feed cases match the F7-FF shape exactly when they sit above the fence (A01, A02), so the acceptance behaviour is intact.

(2) Prefix lexing. Covered by B01-B12. Three leading spaces plus a one-line wrapper is refused IN-FENCE (B01; BOGUS-RECOMPUTED first when the value is bogus, B03). Four leading spaces never lex (B04, B05: UNFILED, no FINDING id). A wrapper with text after `-->` does not lex (B06, B07). Tab and NBSP prefixes do not lex (B10, B11).

(3) Dual anchors. Covered by C01-C07. Three occurrences where occurrence 3 lies are refused ANCHOR-ALIAS-MISMATCH (C01; C03 where occurrence 2 agrees). A second occurrence with two tokens is refused MULTIPLE-ANNOTATIONS (C02). A straddling token on occurrence 2 is refused ZONE-TOKEN-STRADDLES-EDGE (C05). Two defects surfaced in the INERT check: it reads the first occurrence only, so an honest filing is refused INERT when occurrence 1 is plain or beyond the zone and occurrence 2 carries the annotation (C04, C07; routed ANCHOR-OCC1-INERT).

(4) Pair grammar. Covered by D01-D06 and D19. PAIR-FILING-INERT fires when both the stale pair and the recomputed pair differ (D01). The recomputed pair of an INERT filing is never evaluated (named-limit analog to AF3a). Recomputed-only mismatch gives SOURCES-RECOMPUTE-MISMATCH (D02). The `row` singular (D04) and the arrow with no unit word (D05) are both refused UNFILED. The F22 timestamp shape is refused (D19).

(5) Fence starts. Covered by E01-E12. The 5-space indent is correctly not a fence (E01, E02: both readings visible and code respectively, consistent with CommonMark). Tilde fence with backticks in the info string is a fence (E03). A closer longer than the opener closes (E04). A closer indented 3 closes (E05); indented 4 does not (E06). A closer with info text does not close (E07). A paragraph-interrupting fence at 3 spaces hides (E12).

(6) PTR near-misses. Covered by D09-D11. `a.md:1`, `./x.py:2` and `x.md:99999` all exempt the overstating line (exit 0). These are the pointer-shaped class the preregistration names as a disclosed limit; they are confirmed, not new.


## Routed defects (proposals; nothing applied, frozen bytes untouched)

| proposed class | states | mechanism (counter lines, frozen file) | CommonMark 0.31.2 reference | severity | direction for the owner (not applied) |
|---|---|---|---|---|---|
| FENCE-CLOSER-EXOTIC-WS | A09-A13 | `hidden_lines()` strips the fence line with Python `ln.rstrip()` (line 163) and checks the closer on that stripped text (line 172-174); the separators `\x0b \x0c \x1c-\x1f \x85 \u2028 \u2029` are removed | closer may be followed only by spaces or tabs; commonmark.js renders the corrections as CODE | HIGH candidate (same family as S1: exotic separator, hide goes dark; exit 0 on corrections that are code) | strip only spaces and tabs in the opener and closer checks; add A09-A13 as acceptance-class fixtures before the claim |
| PAIR-FILING-IN-FENCE | D14, D15 | `pair_filings` is built from every `R53-CORRECTION` match in SCORECARD (lines 266-269) with no hidden-set check; the R52 branch does check (line 354) | pair filing inside a fence renders as CODE (D14); inside a comment as COMMENT (D15) | MEDIUM-HIGH: a pair filing the counter counts as honest is not rendered as a filing | apply the same hidden-set refusal (CORRECTION-IN-FENCE) to CORR2 matches |
| FENCE-IN-LIST-ITEM | E09, E10 | fences are recognised only at 0-3 spaces of absolute indentation (line 178); list-item containers are not modelled | fenced code inside a list item renders as CODE | MEDIUM: a correction rendered as code inside a list item counts as filed | model container indentation (list item content column) before the fence check, or refuse fences that open after a list marker |
| PAIR-SEPARATOR-SET | D07, D08 | `PAIR_ANNOT_RE` matches only `->` and `→` (line 109) | the overstatement is prose in both cases | MEDIUM: overstatement written with `=>` or an em-dash arrow is invisible | widen the separator set to the forms the registry text actually uses; add fixtures |
| PAIR-PATH-LITERAL | D12 | a line is scanned only when it contains the literal `corpus/SOURCES.md` (line 377) | prose | MEDIUM-LOW: `SOURCES.md 999 -> 1000 rows` is invisible | match the basename `SOURCES.md` with an optional directory prefix |
| ANCHOR-OCC1-INERT | C04, C07 | the INERT check takes `zones[0]` only (line 337) while the stated value takes the first in-zone token of any occurrence (lines 290-319) | n/a (counter-internal) | MEDIUM-LOW (false refusal of honest filings) | evaluate the INERT check against the same occurrence that defines `stated` |
| CORRECTION-TRAILING-TEXT-UNLEXED | B07 | `CORR_RE` requires `\s*$` after the optional `-->` (line 106-107) | a bare filing followed by ` --> note` is visible PROSE; the counter refuses it | LOW (over-refusal, silent) | allow trailing text after a bare filing, or name the refusal |
| CORRECTION-UNLEXED (named refusal) | B04, B05, B06, B10, B11, E02, F02, B07 | a refused filing produces UNFILED with no FINDING id | n/a | LOW but relevant to the r54 §5.2 rule: a counted kill row must name its finding, and these refusals name none | emit a named finding for an unlexed correction on a site that needs one |
| PAIR-SCAN-INDENTED-CODE | D16 | `hidden_lines()` hides fences and comments only; an indented code block in LOG.md is scanned (over-refusal) | indented code renders as CODE | LOW | include indented code in the pair-scan hide set |
| DIGIT-ASCII-ONLY | F01 | `\d` and `int()` accept non-ASCII decimal digits in CORR, CORR2 and ANNOT | prose | LOW | use `[0-9]` in the annotation and filing patterns |

## Named limits confirmed (disclosed in the preregistration; behaviour matches the disclosure)

- PTR pointer shapes: D09 (`a.md:1`), D10 (`./x.py:2`), D11 (`x.md:99999`). The exemption is line-level and shape-only, as disclosed.
- AF4c file scope: D18 (overstatement in SCORECARD.md, outside the pair sites).
- CR-only line endings: F02 (one line to the counter).
- Zone straddle: C05 behaves as specified.
- AF3a analog: D01 (an INERT pair filing is never recomputed).

## Verification gaps and residual risk

- The CommonMark reading is checked by commonmark.js 0.31.2, not by the spec page, which I did not open in this seat.
- B11 (NBSP-prefixed filing) has an inconclusive render check on the paragraph-start line (search artifact); its refusal is recorded regardless.
- The v3 counter was not re-run over the attack states; the brief asked only for the v4 surface.
- The real-lane leg was run at the dispatch tip `3ce0ba03` only (exit 0). The content-tip leg `4b10ddd1` and the C2 counter are other seats' surfaces.
- Attack fixtures are synthetic. They exercise the grammar, not the real LOG.md or SCORECARD.md content beyond the 27 committed fixtures and the real-lane run.

## Scratch and cleanup

Receipts, the driver (`attack.py`), the classifier (`classify.py`), `cm/check.js`, `cm-classes.tsv`, `classification.tsv`, `realtip-c1.txt` and `selftest-c1.txt` are copied into the seat directory. The scratch tree (fixtures, commonmark install, selftest runs) is deleted before yield.

## Classified table (66 states)

Columns: state, predicted, exit, first FINDING (`-` = no FINDING line), class, evidence. Receipts: `receipts/<state>.txt`.

| state | predicted | exit | first FINDING | class | evidence |
|---|---|---|---|---|---|
| A01-SEP-VT-x2 | IN-FENCE (F7-FF replica, \x0b) | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | F7-FF replica (acceptance); numbering matches physical line |
| A02-SEP-FF-x2 | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | form feed; LF-only numbering holds |
| A03-SEP-FS-GS-RS | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:11 (site SCORECARD.md:5) | CommonMark-consistent | U+001C/1D/1E; LF-only numbering holds |
| A04-SEP-NEL-x2 | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | U+0085; LF-only numbering holds |
| A05-SEP-LS-x2 | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | U+2028; LF-only numbering holds |
| A06-SEP-PS-x2 | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | U+2029; LF-only numbering holds |
| A07-CR-TRAILING-FENCE | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) | CommonMark-consistent | CR-trailing opener/closer; CM CODE; refused |
| A08-CRLF-HONEST | exit0 filed (control) | 0 | - | CommonMark-consistent | control: CRLF honest filings, CM PROSE, exit 0 |
| A09-CLOSER-VT | exit0 (CM: fence still open, corrections are code) | 0 | - | routed-defect-proposal FENCE-CLOSER-EXOTIC-WS | closer ~~~ + VT: CM says not a closer (CODE); counter closes fence, corrections visible, exit 0 |
| A10-CLOSER-FF | exit0 (CM: still open) | 0 | - | routed-defect-proposal FENCE-CLOSER-EXOTIC-WS | closer + FF: CM CODE, counter exit 0 |
| A11-CLOSER-NEL | exit0 (CM: still open) | 0 | - | routed-defect-proposal FENCE-CLOSER-EXOTIC-WS | closer + NEL: CM CODE, counter exit 0 |
| A12-CLOSER-LS | exit0 (CM: still open) | 0 | - | routed-defect-proposal FENCE-CLOSER-EXOTIC-WS | closer + LS: CM CODE, counter exit 0 |
| A13-CLOSER-FS | exit0 (CM: still open) | 0 | - | routed-defect-proposal FENCE-CLOSER-EXOTIC-WS | closer + FS: CM CODE, counter exit 0 |
| A14-CLOSER-TAB-CONTROL | exit0 consistent (control) | 0 | - | CommonMark-consistent | control: tab-suffixed closer is CM-legal, PROSE, exit 0 |
| B01-3SP-WRAPPER-HONEST | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5) | CommonMark-consistent | 3-space + wrapper: CM COMMENT, refused IN-FENCE |
| B02-3SP-BARE-CONTROL | exit0 (control) | 0 | - | CommonMark-consistent | control: 3-space bare lexes, PROSE, exit 0 |
| B03-3SP-WRAPPER-BOGUS | BOGUS-RECOMPUTED | 1 | FINDING BOGUS-RECOMPUTED SCORECARD.md:5 recomputed=83 but record count is 79 | CommonMark-consistent | 3-space + wrapper bogus: BOGUS first, CM COMMENT |
| B04-4SP-BARE | no FINDING, unfiled (must NOT lex) | 1 | - | CommonMark-consistent | 4-space must not lex: CM CODE; refused UNFILED with no FINDING id |
| B05-4SP-WRAPPER | no FINDING, unfiled (must NOT lex) | 1 | - | CommonMark-consistent | 4-space wrapper: CM CODE; refused UNFILED with no FINDING id |
| B06-WRAPPER-TRAILING-TEXT | no FINDING, unfiled | 1 | - | CommonMark-consistent | wrapper + trailing text: CM COMMENT; refused UNFILED, no FINDING id |
| B07-BARE-TRAILING-TEXT | no FINDING, unfiled | 1 | - | routed-defect-proposal CORRECTION-TRAILING-TEXT-UNLEXED | bare filing + " --> note": CM PROSE (visible filing), counter silently unlexed, UNFILED no FINDING id (over-refusal) |
| B08-VT-AFTER-OPENER | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5) | CommonMark-consistent | VT after <!-- lexed by \s; CM COMMENT; IN-FENCE |
| B09-NOSPACE-WRAPPER | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5) | CommonMark-consistent | no-space wrapper; CM COMMENT; IN-FENCE |
| B10-TAB-PREFIX | no FINDING, unfiled | 1 | - | CommonMark-consistent | tab-prefixed: CM CODE (indented code); refused silently |
| B11-NBSP-PREFIX | no FINDING, unfiled | 1 | - | CM-render-inconclusive | NBSP prefix; line 7 render check ambiguous (search artifact at paragraph start); refused silently, low |
| B12-MULTILINE-COMMENT-TRAILING | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:7 (site SCORECARD.md:5) | CommonMark-consistent | multi-line comment, closer with text; CM COMMENT; IN-FENCE |
| C01-THREE-ANCHORS-OCC3-LIES | ANCHOR-ALIAS-MISMATCH | 1 | FINDING ANCHOR-ALIAS-MISMATCH SCORECARD.md line 5 anchor occurrence 3 reads 78, occurrence 1 reads 79 | CommonMark-consistent (counter-internal) | ANCHOR-ALIAS-MISMATCH at occ3 as specified |
| C02-OCC2-MULTI-TOKEN | MULTIPLE-ANNOTATIONS | 1 | FINDING MULTIPLE-ANNOTATIONS SCORECARD.md line 5 zone tokens 79,80 | CommonMark-consistent (counter-internal) | MULTIPLE-ANNOTATIONS at occ2 as specified |
| C03-ALIAS-OCC2-AGREES-OCC3-LIES | ANCHOR-ALIAS-MISMATCH | 1 | FINDING ANCHOR-ALIAS-MISMATCH SCORECARD.md line 5 anchor occurrence 3 reads 79, occurrence 1 reads 78 | CommonMark-consistent (counter-internal) | ANCHOR-ALIAS-MISMATCH at occ3 when occ2 agrees |
| C04-BEYOND-ZONE-FIRST-TOKEN | INERT-CORRECTION (first occurrence zone empty) | 1 | FINDING INERT-CORRECTION SCORECARD.md:5 line 5 of SCORECARD.md annotation count 0 | routed-defect-proposal ANCHOR-OCC1-INERT | honest filings refused INERT: stated value comes from first in-zone token (occ2) but INERT check reads zones[0] only (false refusal) |
| C05-OCC2-STRADDLE | ZONE-TOKEN-STRADDLES-EDGE | 1 | FINDING ZONE-TOKEN-STRADDLES-EDGE SCORECARD.md line 5 a count token starts inside the 32-char zone and ends beyond it | named-limit-confirmed (zone straddle) | ZONE-TOKEN-STRADDLES-EDGE as specified |
| C06-OCC2-PLAIN-CONTROL | exit0 (control) | 0 | - | CommonMark-consistent (counter-internal) | control: occ2 plain, exit 0 |
| C07-OCC1-PLAIN-OCC2-78 | INERT-CORRECTION | 1 | FINDING INERT-CORRECTION SCORECARD.md:5 line 5 of SCORECARD.md annotation count 0 | routed-defect-proposal ANCHOR-OCC1-INERT | same INERT first-occurrence defect as C04 (occ1 plain, occ2 annotated) |
| D01-PAIR-INERT-BOTH-DIFFER | PAIR-FILING-INERT | 1 | FINDING PAIR-FILING-INERT LOG.md:2 filing stale=3->5 does not match the annotated pair 3->4 | named-limit-confirmed (AF3a analog) | PAIR-FILING-INERT first; the inert filing recomputed pair is never evaluated |
| D02-PAIR-RECOMPUTE-DIFFERS | SOURCES-RECOMPUTE-MISMATCH | 1 | FINDING SOURCES-RECOMPUTE-MISMATCH LOG.md:2 filing recomputed=3->6 but the census grep recomputes 3->3 | CommonMark-consistent (counter-internal) | SOURCES-RECOMPUTE-MISMATCH as specified |
| D03-PAIR-HONEST-CONTROL | exit0 (control, F12b shape) | 0 | - | CommonMark-consistent (counter-internal) | control: F12b shape, exit 0 |
| D04-PAIR-ROW-SINGULAR-NOFILING | UNFILED-SOURCES-ANNOTATION | 1 | FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it | CommonMark-consistent (counter-internal) | F15 variant, "row" singular: UNFILED as specified |
| D05-PAIR-ARROW-NOROWS-NOFILING | UNFILED-SOURCES-ANNOTATION | 1 | FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it | CommonMark-consistent (counter-internal) | F16 variant without unit word: UNFILED as specified |
| D06-PAIR-ARROW-NOROWS-FILED-CONTROL | exit0 (control) | 0 | - | CommonMark-consistent (counter-internal) | control: arrow no-rows with honest filing, exit 0 |
| D07-PAIR-FATARROW-SEP | exit0 (not matched: separator grammar is -> / → only) | 0 | - | routed-defect-proposal PAIR-SEPARATOR-SET | => overstatement invisible to the pair grammar (only -> and → match), exit 0 |
| D08-PAIR-EMDASH-ARROW-SEP | exit0 (not matched) | 0 | - | routed-defect-proposal PAIR-SEPARATOR-SET | —> overstatement invisible, exit 0 |
| D09-PTR-FAKE-A.MD:1 | exit0 (named limit: pointer-shaped fake exempt) | 0 | - | named-limit-confirmed (PTR) | a.md:1 pointer-shaped fake exempts the line (disclosed), exit 0 |
| D10-PTR-DOTSLASH-X.PY:2 | exit0 (named limit: ./x.py:2 matches pointer shape) | 0 | - | named-limit-confirmed (PTR) | ./x.py:2 matches path:digit shape, exempt (disclosed class), exit 0 |
| D11-PTR-X.MD:99999 | exit0 (named limit: x.md:9 prefix matches) | 0 | - | named-limit-confirmed (PTR) | x.md:99999 matches x.md:9 prefix, exempt (disclosed class), exit 0 |
| D12-PATHLESS-SOURCES | exit0 (path literal; registry not named) | 0 | - | routed-defect-proposal PAIR-PATH-LITERAL | SOURCES.md 999 -> 1000 rows without corpus/ is never scanned, exit 0 (not a disclosed limit) |
| D13-PAIR-IN-HTML-COMMENT | exit0 (comment invisible, CM-consistent) | 0 | - | CommonMark-consistent | pair in HTML comment: CM COMMENT, skipped by R6 hide rule; comment invisible |
| D14-PAIR-FILING-IN-FENCE | exit0 (predicted BYPASS: pair filings are not hide-checked) | 0 | - | routed-defect-proposal PAIR-FILING-IN-FENCE | pair filing inside ```text fence in SCORECARD counts as filed (CORR2 is not hide-checked); CM CODE; LOG overstatement passes, exit 0. BYPASS |
| D15-PAIR-FILING-IN-COMMENT | exit0 (predicted BYPASS) | 0 | - | routed-defect-proposal PAIR-FILING-IN-FENCE | pair filing inside <!-- --> counts as filed; CM COMMENT; exit 0. BYPASS (R52 analog refused IN-FENCE) |
| D16-PAIR-4SP-CODE-IN-LOG | UNFILED (over-refusal; CM: indented code) | 1 | FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it | routed-defect-proposal PAIR-SCAN-INDENTED-CODE | 4-space overstatement in LOG.md: CM CODE, counter UNFILED (over-refusal) |
| D17-PAIR-FENCED-LOG-CONTROL | exit0 (control, F19 shape) | 0 | - | CommonMark-consistent | control: fenced LOG example skipped, exit 0 |
| D18-PAIR-IN-SCORECARD-OUTSIDE-SITES | exit0 (named limit: pair scan covers LOG/README only) | 0 | - | named-limit-confirmed (AF4c) | overstatement in SCORECARD outside PAIR_SITES invisible, exit 0 |
| D19-F22-TIMESTAMP-CONTROL | UNFILED-SOURCES-ANNOTATION (acceptance F22 shape) | 1 | FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 999 -> 1000 rows but the registry holds 3; no pair-form filing names it | CommonMark-consistent (counter-internal) | control: F22 shape, UNFILED as specified |
| E01-5SP-FENCE-VISIBLE-CONTROL | exit0 consistent (indented code; corrections at col 0) | 0 | - | CommonMark-consistent | 5-space fence after blank = CM indented code; corrections at col 0 visible; exit 0 |
| E02-5SP-FENCE-CORR-INDENT5 | no FINDING, unfiled (CM: code) | 1 | - | CommonMark-consistent | 5-space indented corrections: CM CODE; refused silently |
| E03-TILDE-BACKTICK-INFO | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) | CommonMark-consistent | tilde fence with backticks in info: CM CODE; IN-FENCE |
| E04-CLOSER-LONGER | exit0 consistent | 0 | - | CommonMark-consistent | closer longer than opener: CM closes; exit 0 |
| E05-CLOSER-3SP | exit0 consistent | 0 | - | CommonMark-consistent | closer indented 3: CM closes; exit 0 |
| E06-CLOSER-4SP | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | closer indented 4 does not close: CM CODE; IN-FENCE |
| E07-CLOSER-WITH-INFO | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5) | CommonMark-consistent | closer with info text does not close: CM CODE; IN-FENCE |
| E08-TILDE-4SP-CONTROL | exit0 consistent (indented code) | 0 | - | CommonMark-consistent | control: 4-space tilde is indented code; corrections at col 0 visible, exit 0 |
| E09-LIST-BULLET-FENCE | exit0 (predicted BYPASS: CM fence inside list item) | 0 | - | routed-defect-proposal FENCE-IN-LIST-ITEM | - ```text with corrections at 2 spaces: CM CODE inside list item; counter exit 0. BYPASS |
| E10-LIST-ORDERED-TILDE | exit0 (predicted BYPASS: CM fence inside list item) | 0 | - | routed-defect-proposal FENCE-IN-LIST-ITEM | 1. ~~~ with corrections at 3 spaces: CM CODE; counter exit 0. BYPASS |
| E11-BLOCKQUOTE-FENCE-COL0 | exit0 consistent | 0 | - | CommonMark-consistent | blockquote fence ended by col-0 corrections: CM PROSE, exit 0 |
| E12-PARA-INTERRUPT-3SP-FENCE | IN-FENCE | 1 | FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site SCORECARD.md:5) | CommonMark-consistent | fence interrupting a paragraph at 3 spaces: CM CODE; IN-FENCE |
| F01-UNICODE-DIGITS-SITE | exit0 (routed low: \d accepts fullwidth digits) | 0 | - | routed-defect-proposal DIGIT-ASCII-ONLY | fullwidth (７８) read as 78 by \d + int(), exit 0 (low) |
| F02-CR-ONLY-FILE | no FINDING, unfiled (named limit: CR-only is one line) | 1 | - | named-limit-confirmed (CR-only) | CR-only file is one line to this counter; unfiled, no FINDING id (disclosed) |
