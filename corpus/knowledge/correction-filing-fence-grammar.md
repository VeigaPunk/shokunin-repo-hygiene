source: S277 — CommonMark spec 0.31.2, § 4.5 Fenced code blocks and § 4.6 HTML blocks (https://spec.commonmark.org/0.31.2/; anchor "§ 4.5 Fenced code blocks; § 4.6 HTML blocks"; page states "Version 0.31.2 (2024-01-28)"; served bytes sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d, 514698 bytes, curl -sSL HTTP 200, no redirect, accessed 2026-11-03; capture census/round-54/sources/s277-commonmark-spec.html; located quote census/round-54/sources/s277-located-quote.txt, 17 words); second source S276 — gitignore(1) manual, PATTERN FORMAT, comment lines (https://git-scm.com/docs/gitignore; anchor section "PATTERN FORMAT"; accessed 2026-11-03), cited for the C2 `#`-row tab-rule refusal only; the annotation-agreement counter census/round-54/c1-counter.py (v3) and the capture counter census/round-54/c2-counter.py (v3)
verified-at: 2026-11-03 — the CommonMark page fetched live (HTTP 200, 514698 bytes, sha256 c85f56cc…f0d); the three located quotes re-checked as verbatim substrings of the tag-stripped capture (a 17 words, b 25 words, c 15 words — all True); the v3 grammar read from the frozen counter bytes census/round-54/c1-counter.py (sha256 f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e) and census/round-54/c2-counter.py (sha256 84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09), both pinned in census/round-54/preregistration.txt
recheck: python3 -B census/round-54/c1-counter.py --root LANE --rev FULL40 --base fe12daad2549f534650d406ebdbac9113d59313f --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR (the real lane at the content tip exits 0 with `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0`)

# Correction-filing hidden-line grammar (v3 fences, zone edge, recomputed, SOURCES pair scan)

## What this entry is

The grammar the souji correction-filing counters use to decide which lines of a correction
file are **hidden from filing** — and therefore which count annotations are visible at all.
It is the grammar the round-54 counter v3 instruments (the r53 routed surfaces), and it is
grounded in the CommonMark specification for what a fence and an HTML comment are. The
CommonMark text grounds *what the classes are*; the lane's frozen counter bytes decide
*which exact shapes the instrument recognises*, and where those two differ, the difference is
a named limit below, not a defect to be edited into the frozen bytes.

## The v3 grammar, surface by surface

### 1. Hidden lines: fences and HTML comments (the r53 R1 class)

A fenced code block is a run of at least three backtick characters **or** tildes — the two
characters are alternatives, not a pair. CommonMark 0.31.2, § 4.5 Fenced code blocks,
located quote (17 words, in `census/round-54/sources/s277-located-quote.txt`):

> A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).

The same section states the closing-fence parity rule (located quote, 25 words):

> same type as the code block began with (backticks or tildes), and with at least as many backticks or tildes as the opening code fence

and, in the same section, the two sentences that make the rule operational (13 and 14 words,
also verbatim substrings of the same capture):

> The closing code fence must use the same character as the opening fence

> The closing code fence must be at least as long as the opening fence

An HTML comment is a region between a `<!--` start and a `-->` end. CommonMark 0.31.2,
§ 4.6 HTML blocks, located quote (15 words):

> Start condition: line begins with the string <!--. End condition: line contains the string -->.

The v3 counter's `hidden_lines()` in `census/round-54/c1-counter.py` implements these three
classes over the correction file (`SCORECARD.md`) — and is defeatable by exotic line separators
(named limit S1, HIGH, below; reproduced by the L1 in `census/round-54/records/s1-formfeed-reproduction.txt`):

- a fence opens on a line whose stripped form begins with `` `{3,} `` or `~{3,}`; the fence
  remembers its character and its opening length;
- a line closes that fence only if it consists **solely** of the opening character and is at
  least as long as the opening run — the parity rule above, applied per character;
- a `<!--` on a line opens an HTML-comment region that ends at a later `-->`; a one-line
  comment hides only its own line.

**Which r53 routed item this partly answers: R1.** The r53 wave found that the frozen v2 counter
recognised only backtick fences, so a correction hidden in a `~~~` tilde fence, or inside a
4-backtick fence past a 3-backtick content line, was accepted as a filing; HTML comments
were a named limit. v3 answers the fence-shape part of R1 with three committed fixtures, each expected to exit 1
with `CORRECTION-IN-FENCE`: `F7-TILDE-FENCE`, `F8-BT4-PARITY`, `F9-HTML-COMMENT`
(`census/round-54/records/c1-selftest-expected.tsv`). The v2 arm of the same counter exits 0
on all three — that is the round's before-state, and it is what makes the claim non-vacuous.

What R1 still carries (reviewer01 AF1e2 and AF1e3, routed to r55, not fixed): a correction-shaped
line behind a one-line `<!--` wrapper, or with two or three leading spaces, never lexes as a
filing; `hidden_lines()` is audited only against parsed filings, so a bogus correction on an
agreeing site exits 0 under v2 and v3 alike.

### 2. The zone edge (the r53 R2 class)

The count annotation is read from a frozen 32-character zone after the anchor. A token that
**starts inside** the zone and **ends beyond** it is refused rather than truncated:
`ZONE-TOKEN-STRADDLES-EDGE`. The r53 wave found that v2 truncated such a token (or ignored
it), so a planted count was invisible to the agreement check. v3 answers the single-straddle case of R2 with the
committed fixture `F10-STRADDLE` (expected exit 1, finding `ZONE-TOKEN-STRADDLES-EDGE`).

What R2 still carries (reviewer01 AF2d and AF2b, routed to r55): a second annotated anchor on a
site line is not judged, so a wrong count after it exits 0; and a second straddling token on one
line is not reported separately (the flag is per line).

### 3. The recomputed value (the r53 R3 class)

A correction whose site already reads the recomputed value and which claims a *different*
`recomputed=` number is refused: `BOGUS-RECOMPUTED`. The r53 wave found v2 exited 0
silently here — its filed tuple never matched, but `mismatches=0 unfiled=0` hid the cause.
v3 answers the matched-site case of R3 with the committed fixture `F11-BOGUS-RECOMP` (expected exit 1, finding
`BOGUS-RECOMPUTED`).

What R3 still carries (reviewer01 AF3d, routed to r55): a pair-form `R53-CORRECTION` filing whose
stale pair differs from the annotated pair is silently ignored (exit 0); there is no INERT analogue
for pair filings.

### 4. The SOURCES-pair annotation scan (the r53 Mistakes row 5 class)

`LOG.md` and `corpus/README.md` are scanned line by line for a `corpus/SOURCES.md <A> -> <B>
rows` annotation whose pair **overstates the registry**: `max(A,B)` is greater than the
registry row count at the measured revision. The registry is append-only, so a true count
never exceeds the current count; an overstating pair is therefore a misread count (the r53
class: two r52 records carried S-id numbers as a row count). Such an annotation must carry
a pair-form filing naming it, or the counter refuses it with
`UNFILED-SOURCES-ANNOTATION`; a filed annotation whose recomputed pair disagrees with the
counts recomputed at the two pinned revisions is refused with
`SOURCES-RECOMPUTE-MISMATCH`. v3 answers the r53 Mistakes row 5 with the committed fixture
`F12-LOG-UNFILED` (expected exit 1, finding `UNFILED-SOURCES-ANNOTATION`) and holds the
honest-handling arm `F12b-LOG-FILED` green (expected exit 0).

**The pointer exemption.** The scan is line-based, and a line that carries a `path:line`
pointer is exempt: a meta-reference that quotes an annotation is not itself an annotation.
This is why a correction filing that names `LOG.md:2527` is not read as a second
annotation.

**The `>current-count` rule.** An annotation whose pair does **not** exceed the current
registry count is a historical note; the instrument does not re-derive it. Only an
overstating pair is in scope.

### 5. The `#`-row tab rule (the r53 R4 class) — grounded on S276

This is the C2 surface, and its grounding is the other source, **S276** (gitignore(1),
PATTERN FORMAT):

> A line starting with # serves as a comment.

A capture grammar that defines no escaping cannot carry a `#`-leading name: such a line is
a comment in the reference grammar, so a `#`-leading data row is ambiguous and is refused
fail-closed with `COMMENT-AMBIGUOUS-NAME`. The r53 wave found the v2 matcher
`^#\S*(\t\S+){5}$` fired only on a `#`-leading row whose name has **no whitespace**, so a
name containing a space was swallowed as a free-form comment and could be made consistent.
v3 partly answers R4 by refusing on **tab count** rather than on the name's whitespace: any
`#`-leading line carrying five or more tabs is refused as data-shaped, so a
space-in-name row now fails too. The committed fixture `FA4-SPACE-NAME` carries that shape
(expected exit 1, finding `COMMENT-AMBIGUOUS-NAME`), and `FA2-COMMENT` keeps the
no-whitespace shape killed.

What R4 still carries (reviewer02 NL-1 and NL-2, routed to r55): a `#`-leading row with four tabs
is silently dropped as a free-form comment (the ≥5-tab rule never sees it), and a legitimate prose
comment with five tabs is refused as data-shaped.

## Named limits (disclosed, not fixed) — verbatim from census/round-54/preregistration.txt

> The zone stays frozen at 32 chars (a token wholly beyond it is still not an
> annotation); the SOURCES scan is line-based and exempts lines carrying a
> path:line pointer (meta-references quoting an annotation are not
> annotations); annotations whose pair does not exceed the current count are
> historical notes the instrument does not re-derive; the registry's
> append-only monotonicity is assumed; unknown `# KEY=VALUE` lines in the
> CAPTURE header are still ignored (the routed item names the receipt only);
> ENTRIES remains the tool's own count; the receipt binds capture-to-receipt
> consistency and bytes, not execution or the capture's path; FLEET_HEAD
> remains format-checked, not resolved. HTML fence class inside CORR_FILE uses
> the line-level `<!--`/`-->` grammar, not full CommonMark HTML blocks.

Two consequences worth naming for the next round, both measured from the frozen counter
bytes on 2026-11-03 (read-only; no counter byte was edited):

- The counter's fence class is **line-level**, not a full CommonMark block parser. Its
  `hidden_lines()` strips leading spaces before matching the fence opener, so a fence
  indented by four or more spaces is still read as a fence (CommonMark reads that shape as
  an indented code block, and an indented code block does not open a fence). The CommonMark
  text and the counter therefore disagree on that shape; the counter's reading is the
  conservative one for a *refusal* (it hides more, not less), and the CommonMark text does
  not make the counter wrong for filing purposes.
- The counter recognises a `<!--` anywhere on a line, while the CommonMark type-2 start
  condition is a line that **begins** with `<!--`. Again the counter's reading is the
  conservative one for a refusal (it hides more).
- The CommonMark closing-fence rule permits up to three spaces of indentation before the
  closing fence and only spaces or tabs after it. The counter accepts a closing fence line
  of the same character at least as long as the opener, with trailing spaces stripped. A
  closing fence followed by other text is therefore not a closing fence for the counter
  either — the two readings agree on that case.

The spec grounds the *classes*; the counter decides the *shapes*. Where they differ, the
difference is disclosed here rather than edited into the frozen bytes.

## What this entry does not claim

- It does not claim the CommonMark specification is the lane's authority over filing
  grammar. It is the external grounding for what a fence and an HTML comment are; the
  lane's own frozen predicate (`census/round-54/preregistration.txt`, claim C1) is the
  authority for what the counter does.
- It does not claim the v3 counters are complete. The five routed r53 surfaces are
  instrumented; the named limits above are the disclosed remainder, and the three below are
  found by the round's attacks and are NOT disclosed by the frozen prereg.

**S1 (HIGH, sentinel01; reproduced by the L1).** `hidden_lines()` numbers the file with
`str.splitlines()`, which also breaks on `\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029`, while the
correction's own line number counts only `\n`. Two form-feed lines directly above a `~~~` fence
turn the committed F7 shape from exit 1 (`fenced=2`) into exit 0 (`filed=2 unfiled=0 fenced=0`).
The fence refusal is therefore not robust against exotic separators. Routed to r55 as counter v4
(one line model) with a red-before fixture committed first.

**S2 (MEDIUM, sentinel01; reproduced by inspection).** The pair scan matches only the ASCII `->`
form. LOG.md:1845 and LOG.md:1858 carry `corpus/SOURCES.md N → M rows` lines written with the
Unicode arrow (the same idiom; both pairs are below the registry count, so this is a coverage
gap, not a live misread), which the scan never reads.

**PTR (MEDIUM, connector01; measured).** `PTR_RE` exempts any `<token>:<digit>`, not only a
path-like pointer, so a timestamp (`10:15`) on an overstating pair line evades
`UNFILED-SOURCES-ANNOTATION`. The disclosed limit names a `path:line` pointer; the regex is broader.
- It does not claim any acceptance run. The counters' acceptance is the L1's, at the
  measured revision; this entry records the grammar and its grounding only.
