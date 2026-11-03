# S56scribe01 — S277 re-open verification (souji round 56, w1)

VERDICT: VERIFIED

Seat: scribe (leaf, no subagent dispatch). Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Measured revision `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`).
All lane bytes read with `git -C <lane> show <rev>:<path>`; working tree confirmed clean vs that rev for the
four claim files (R10). Nothing in the lane was edited.

## Behavior

Re-fetched CommonMark 0.31.2 live twice, located the two Gate quotes in the tag-stripped, entity-decoded,
whitespace-collapsed text, word-counted them, checked the Gate block's access record, ran the knowledge
entry's `recheck` line verbatim from the lane root, and diffed the S277 `SOURCES.md` row across the base and
freeze revisions. All four verification targets are exact.

## Target 1 — live fetch

| fact | claimed | observed |
|---|---|---|
| HTTP status | 200 | 200 |
| url_effective | `https://spec.commonmark.org/0.31.2/` (no redirect) | same; `num_redirects=0` |
| bytes | 514698 | 514698 |
| sha256 | `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` | identical |
| capture `census/round-56/sources/s277-commonmark-0.31.2.html` | same digest | `git show` at cce21b55 → 514698 B, same digest; `cmp` vs live **IDENTICAL** |

Two independent fetches (R2, R3) returned the same 514698 bytes and the same digest; `cmp` against the
committed capture was byte-identical in both. Content-Type `text/html; charset=utf-8`. This is a stronger
result than the Gate records (it records one fetch; two agree).

## Target 2 — located quotes and Gate block

Tag-strip pipeline exactly as specified (strip `<script>`/`<style>`, strip tags, `html.unescape`, collapse
whitespace) over the live bytes (R5):

| quote | substring of stripped live text | words | Gate's stated count |
|---|---|---|---|
| Q1 "The block begins with a line that meets a start condition (after up to three optional spaces of indentation)." | True | 19 | 19 ✓ |
| Q2 "Start condition: line begins with the string <!--" | True | 8 | 8 ✓ |

`"Version 0.31.2 (2024-01-28)"` is present in the stripped live text, so the Gate's "served page states"
parenthetical is accurate. The Gate block in `corpus/lessons/round-56.md` at cce21b55 states the access date
(2026-11-03, today), the URL, the status (`200`, no redirect), the byte count and the sha256 correctly, and
cites the capture path that exists at the freeze rev with that digest.

## Target 3 — knowledge entry `corpus/knowledge/correction-filing-html-comment-opener.md` at cce21b55

- `source:` cites **S277**, the URL `https://spec.commonmark.org/0.31.2/`, and the anchor **§4.6 HTML blocks**.
  The live page carries `id="html-blocks"` and the heading text `4.6 HTML blocks` (TOC entry `4.6HTML blocks`),
  so the section reference resolves. Both located quotes, the capture path and the digest are in the same line.
- `verified-at:` line present (2026-11-03, HTTP 200, no redirect, 514698 bytes, sha equal to capture, both
  quotes re-checked as verbatim substrings). Every element of that sentence was reproduced above.
- `recheck:` line present. The executable part run **once, verbatim, from the lane root** (R6):
  `python3 -B -c "import re,html;t=re.sub(...)..."` → `True True`, exit 0. The expected value `(expected: True True)`
  matches. The trailing prose clause ("re-run the round-56 C1 counter over committed fixtures with
  run-matrix.sh") was not executed by this seat: the matrix is the C1 seats' instrument and re-running it is
  outside this verification (named limit, not a failure).
- Pointer claims checked against frozen bytes (R9): `F26-INDENT4-COMMENT-OPENER` and
  `F29-PROSE-COMMENT-MENTION` are real fixture names in `build-fixtures.py` (lines 180/591/610), and both dry-run
  TSVs named in the entry exist at the freeze rev.

## Target 4 — registry row S277 in `corpus/SOURCES.md`

Column map from the header (line 34): `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.
Character-level diff base → freeze (R7) yields **one opcode only**:

```
insert: base[1142:1142]='' -> freeze[1142:1201]=', corpus/knowledge/correction-filing-html-comment-opener.md'
```

So at cce21b55: `id=S277`, `kind=docs`, `tier=A`, `status=mined`, `opened=2026-11-03`, `recheck=on-release`,
`used-by=` `corpus/knowledge/correction-filing-fence-grammar.md, corpus/knowledge/correction-filing-html-comment-opener.md`.
That is exactly the Gate's stated change (old single entry → both entries), and id/kind/tier/status are
unchanged versus fafe3716. `opened` was not re-written (same value in both revs), as the Gate states.

## Claims in the entry not supported by the two located quotes (named per task item 3)

None of these contradicts the live source; they are outside the two located quote strings.

1. **"A four-space-indented `<!--` is indented code, not a comment."** The negative (no comment region) follows
   from Q1's ≤3-space limit; the positive classification "is indented code" belongs to §4.4 indented code
   blocks and appears in neither located quote. The lesson's Gate itself limits the admitted basis to "a
   four-space-indented opener opens no region" — the entry states more than the Gate admitted.
2. **"A region still runs to the first line that contains `-->`."** The end condition is verbatim on the page
   (`End condition: line contains the string -->`, visible in the R5 Q2 context) but is **not** one of the two
   located quotes; the Gate and the entry's `source:` line cite only the start condition and its indentation
   limit.
3. **"type 2" / "types 1, 3, 4, 5, 6 and 7".** The page says "There are seven kinds of HTML blocks" and numbers
   the start conditions; the located quotes carry neither the numeral 2 nor the enumeration.
4. **Paraphrase "a line whose non-space text begins with `<!--`, indented by at most three spaces".** The
   task's suggested contrast ("at most three leading spaces" vs "after up to three optional spaces of
   indentation") is **not** a discrepancy — "at most three" and "up to three" are the same bound. The imprecise
   word is **"non-space text"**: the spec says "line begins with the string `<!--`" after up to three optional
   spaces, while "non-space text" would also admit a tab-indented opener (`"   \t<!--"`). The frozen counter
   rejects that case (`indent = len(raw) - len(raw.lstrip(' '))`; a leading tab stays in `ln`, so
   `stripped.startswith('<!--')` is False — R11), and CommonMark §2.2 tab expansion would make it 4 columns →
   indented code. The counter's own docstring is stricter and more accurate ("line begins with `<!--`, at most
   three leading spaces"). Documentation imprecision, not a source error.
5. **"a mid-line opener that also closes on the same line hides only its own line"** (entry, "What is not
   claimed"). For a genuine mid-line mention v5 hides **nothing** — no region opens and the line is not added
   to `hidden` (R11). "Hides only its own line" is true only for a **line-begin** opener that self-closes; the
   counter's docstring says exactly "a one-line comment hides only its own line". Wording defect in the entry;
   the entry's earlier bullet states the mid-line rule correctly.

Item 5 is a wording defect against the frozen counter, not against the source, and the verdict axis here is the
S277 sourced claim; it is routed as an r57 entry correction (the entry is frozen bytes and was not edited).
Items 1–4 are scope boundaries of the two located quotes, which the lesson's Gate already respects.

## Findings

- The round's sourced claim survives a live re-open byte-for-byte, including a second independent fetch.
- The Gate's access record is accurate in every stated field (date, URL, status, redirect count, bytes, digest),
  and its word counts 19/8 recompute exactly.
- The registry change is exactly one cell: `used-by` gains the second knowledge entry. No other cell moved.
- Reconciliation note: the *row's* `capture`/`anchor` cell still points at the round-54 capture
  (`census/round-54/sources/s277-commonmark-spec.html`) and the 17-word fence quote. That is expected — the
  round-56 capture is recorded in the Gate and the entry, and the Gate states the row is not re-written on
  re-open. The round-54 and round-56 captures share the same URL and digest, so the row stays truthful.
- No counter was executed and no matrix was re-run by this seat; the task's re-open surface is source-level.

## Touched surfaces

- Read-only: `census/round-56/{c1,c2}-counter.py`, `census/round-56/fixtures/*`, `census/round-56/records/*`,
  `census/round-55/*-counter.py`, `corpus/lessons/round-56.md`, `corpus/knowledge/correction-filing-html-comment-opener.md`,
  `corpus/SOURCES.md`, `census/round-56/sources/s277-commonmark-0.31.2.html` (all via `git show` at cce21b55).
- Written: this report, `S56scribe01-receipts.txt` (same directory), and the scoped copy at
  `.ufo/waves/round-56/w1/S56scribe01.md`. Scratch under `/fast/scratch/hyaku/souji-r56/S56scribe01/` was
  deleted after the receipts were copied here.
- No lane file edited; no git/jj mutation anywhere; no fleet-root tracked file touched.

## Out of scope / named limits

- The C1/C2 matrices (v4/v5, post-freeze official matrices) were not run or adjudicated here — C1/C2 seats own
  them. The entry's trailing `recheck` prose hint ("re-run the round-56 C1 counter ... with run-matrix.sh") is
  therefore unexecuted by this seat.
- The two located quotes do not cover the comment **end** condition, the HTML block type numbering, or §4.4;
  claims resting on those are named above and are true of the page, not of the located strings.
- Only the CommonMark page was fetched (two identical fetches). No CDN/cache-buster variant was probed, so the
  digest's stability is evidenced within this host/session, not globally.
- Tooling: nothing installed or upgraded (R13); pacman untouched.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56scribe01/S56scribe01-report.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56scribe01/S56scribe01-receipts.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56scribe01.md`

## Receipts

R1 pins (8/8 match) · R2 fetch #1 · R3 fetch #2 + `cmp` · R4 capture at cce21b55 · R5 quote location and word
counts · R6 recheck verbatim (`True True`, rc 0) · R7 row char-diff (single insert) · R8 column map · R9
fixture/receipt pointers · R10 worktree clean vs HEAD · R11 counter opener implementation · R12 disk guard
(405.1G free on scratch) · R13 no tool installs. Full text in `S56scribe01-receipts.txt`; each receipt block
ends with its `EXIT=<rc>` line, and the command-level exit codes are 0 throughout.

EXIT=0
