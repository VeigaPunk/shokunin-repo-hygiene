# S57scribe01 — souji round 57, wave 1: source re-open and the inline-comment knowledge entry

Seat: `S57scribe01`, role scribe, leaf member (no subagent dispatch, no background job, no counter run).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Freeze read: `d749f7ee`; the lane advanced to
`80548212` **during** this seat (observed, authored by others, listed under Findings F6).

Verdict on my own scope: **AGREE** — all four acceptance items produced with re-derived numbers, and
the one count defect I could reproduce is reported rather than repeated (F1).

## Behaviour (what I ran)

### 1. Three sources re-opened live

```
curl -sSL -o <scratch>/s<N>.html -w '%{http_code} %{url_effective}' --max-time 60 <url>
```

| source | HTTP | effective URL | bytes | sha256 | vs committed capture |
|---|---|---|---|---|---|
| S279 `https://html.spec.whatwg.org/multipage/syntax.html` | 200 | same URL (no redirect) | 89196 | `ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1` | `cmp -s` BYTE-IDENTICAL |
| S280 `https://spec.commonmark.org/0.31.2/` | 200 | same URL (no redirect) | 514698 | `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` | BYTE-IDENTICAL |
| S281 `https://developer.mozilla.org/en-US/docs/Web/HTML/Comments` | 200 | `…/Web/HTML/Guides/Comments` (redirect) | 175824 | `2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba` | BYTE-IDENTICAL |

Digests equal the pins in `census/round-57/preregistration.txt` and the claims in
`records/source-quotes.txt`. Receipt: `fetches.txt`.

### 2. Located quotes verified with my own normalizer

`quote-verify.py` (written for this seat; imports no lane tool): drop `<script>/<style>` bodies, drop
markup comment spans, replace every tag with **one space**, `html.unescape`, collapse whitespace runs,
strip. Result, four of four quotes verbatim, each inside its anchor's section (nearest preceding
heading reported): `S279 "13.1.6 Comments"`, `S280 "6.6 Raw HTML"`, `S281 "Using HTML comments"`.

| source | quotes | verbatim | words (`split()` == `wc -w`) | committed claim | reproduced |
|---|---|---|---|---|---|
| S279 | quote-1 | yes | 11 | 11 | yes |
| S279 | quote-2 | yes | **19** | **17** | **NO** (F1) |
| S280 | quote-1 | yes | 24 | 24 | yes |
| S281 | quote-1 | yes | 25 | 25 | yes |

All four are ≤25 words. Receipt: `quotes.txt`, `quote-verify.json`.

### 3. Independent render of the four shapes

`render-probe.py`: markdown-it-py **4.2.0** (already installed at `/usr/lib/python3.14/site-packages`,
Python 3.14.8 — **nothing installed or upgraded this seat**), `MarkdownIt('commonmark')`; blocks
transcribed from the frozen builder `census/round-57/fixtures/build-fixtures.py` (B4/C4/C6/F29 +
`base_corrections`); "visible" = text/code tokens, `html_inline`/`html_block` dropped.

```
F29-PROSE-COMMENT-MENTION  visible_R52_CORRECTION=2  hidden_token_types=[]
B4-INLINE-NBSP-OPENER      visible_R52_CORRECTION=0  hidden_token_types=["html_inline"]
C4-INLINE-CLOSED-COMMENT   visible_R52_CORRECTION=0  hidden_token_types=["html_inline"]
C6-INLINE-SAME-LINE        visible_R52_CORRECTION=2  hidden_token_types=["html_inline"]
CONTROL-NO-COMMENT         visible_R52_CORRECTION=2  hidden_token_types=[]
```

F29 renders the `<` escaped (`&lt;!--`): no closer, so literal text. Receipt: `render-probe.txt`.

### 4. Counter evidence read, not re-run

From `records/matrix-dryrun/c1-matrix-v{5,6}.tsv` (36 rows each) and `records/c1-selftest-expected.tsv`:

```
v5 rows=36 exit0=10 ; v6 rows=36 exit0=8
diff of (fixture|exit|findings_all) v5 vs v6 → only rows 34-35:
  < B4-INLINE-NBSP-OPENER|0|-
  < C4-INLINE-CLOSED-COMMENT|0|-
  > B4-INLINE-NBSP-OPENER|1|CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
  > C4-INLINE-CLOSED-COMMENT|1|CORRECTION-IN-FENCE,CORRECTION-IN-FENCE
```

Expected rows: `F29…0 -`, `B4…1 CORRECTION-IN-FENCE,CORRECTION-IN-FENCE`,
`C4…1 CORRECTION-IN-FENCE,CORRECTION-IN-FENCE`, `C6…0 -`. v6 B4/C4 SUMMARYs carry
`filed=0 unfiled=2 fenced=2`. I did not execute either counter.

### 5. Deliverables drafted and checked

- `inline-html-comment-visibility-r57.md` — provenance trio first (`source:` S279+S280 with URL/anchor
  and both capture digests; `verified-at:`; `recheck:`), the WHATWG-vs-CommonMark distinction, the
  B4/C4/C6/F29 table with three separated evidence classes, nine named limits, and a "what this does
  not claim" close.
- `sources-rows.md` — the three rows (11 columns, no pipe in any cell), S279/S280 `kind=spec` `tier=A`,
  S281 `kind=docs` `tier=B` with `teaches` opening `REJECTED: … ; flip: …`, every `used-by` =
  `corpus/knowledge/inline-html-comment-visibility-r57.md`.
- Row grammar verified on a scratch fleet root (my rows + the entry as the used-by target):

```
souji-shokunin  ok  <scratch>/fleetroot/souji-shokunin/corpus/SOURCES.md     validate_rc=0
souji-shokunin  rows 3 ; tier.A 2 ; tier.B 1 ; status.mined 2 ; status.rejected 1 ; missing 0
```

- Render safety: both drafts parse with **0** `html_inline`/`html_block` tokens (every comment token is
  inside a code span), so neither draft swallows text in a rendered view.

## Gates

| gate | command | observed |
|---|---|---|
| fetch identity | `cmp -s <live> <committed capture>` ×3 | BYTE-IDENTICAL ×3, HTTP 200 ×3 |
| quote substrings | `python3 -B quote-verify.py <scratch>` | `FAILURES 0`, 4/4 verbatim |
| row grammar | `sources-census.sh validate --root <scratch>/fleetroot souji-shokunin --today 2026-11-03` | `ok`, rc 0 |
| row population | `sources-census.sh census …` | rows 3, tier.A 2, tier.B 1, mined 2, rejected 1 |
| draft render safety | `markdown-it-py` parse of both drafts | 0 raw-HTML tokens each |
| lane untouched | `git -C <lane> status --porcelain` before/after my reads | my writes appear nowhere; the tree changed only by other seats' commits/receipts |

## Touched surfaces

Created (all inside the seat directory): `fetches.txt`, `quotes.txt`, `quote-verify.py`,
`quote-verify.json`, `render-probe.py`, `render-probe.txt`, `render-probe.json`,
`rows-render-check.txt`, `inline-html-comment-visibility-r57.md`, `sources-rows.md`, and this report.
Scratch `/fast/scratch/hyaku/souji-r57/S57scribe01/` used for fetches, the render probe and the scratch
fleet root; deleted at exit. **No** write to `corpus/`, `census/`, `.ufo/state/`, the fleet root, or a
sibling lane; no `git`/`jj` mutation anywhere (read-only `log/show/status/ls-files/diff` only); no
`pacman`, no service touched, no tool installed.

## Findings

**F1 — the committed quote count for S279 quote-2 does not reproduce; it has landed in `corpus/`.**
`printf '%s' 'the text must not start with the string " > ", nor start with the string " -> "' | wc -w`
→ `19`; `len(quote.split())` → `19`; alphanumeric-token count → `13`. `records/source-quotes.txt:7`
claims `(17 words)`, and the committed entry
`corpus/knowledge/inline-html-comment-visibility-r57.md` repeats `Second located quote (17 words)`.
Both are ≤25 words, so no rule is violated; the number is simply not reproducible. My rows say
`11 and 19 words`.

**F2 — the committed S279 row does not quote the page verbatim.**
`corpus/SOURCES.md:239` teaches cell begins `"Comments must have the following format: The string
' <!-- '."` — single quotes inside a double-quoted located quote. The page reads
`The string " <!-- ".` (double quotes), and the rendered cell keeps the single-quote form
(`rows-render-check.txt`). My draft carries the verified form.

**F3 — committed S280 row kind.** `corpus/SOURCES.md:240` has `docs`; the seat assignment specifies
`spec` (the census enum accepts both: `E05` enum is
`spec|docs|paper|code|tool|dataset|talk|book|community|own-work`). My draft says `spec`.

**F4 — committed S281 row `used-by`.** `corpus/SOURCES.md:241` ends `| — |`; the assignment requires
the exact entry path `corpus/knowledge/inline-html-comment-visibility-r57.md`, which now exists on disk
(`E11` would pass). My draft carries the path.

**F5 — the committed S280 row erases its own quote in a rendered table (measured).**
`rows-render-check.txt` (markdown-it-py 4.2.0 with the table rule, header + delimiter + the three
committed rows): the S280 teaches cell renders 190 visible characters and **all three** comment tokens
are gone — the reader sees `An HTML comment consists of  ,  , or  , and -->`. My draft keeps them
(390 visible characters, all three tokens visible) because the quote sits in a code span. A cell that
carries `<!--` but no `-->` (the committed S279 cell) is escaped instead and renders literally, so the
failure needs both in one cell. Text readers (census parser, grep) are unaffected either way.

**F6 — the lane advanced mid-seat.** At my first read the tree was `d749f7ee` with `M corpus/SOURCES.md`
and an untracked `corpus/knowledge/inline-html-comment-visibility-r57.md`; it is now `80548212`
("sources S279/S280 admitted + S281 rejected, inline-comment visibility entry, QUALITY Q115/Q116, …"),
with the entry and rows committed and new receipts landed (`c1-tip.txt`, `c1-matrix-v{5,6}.tsv`,
`c1-hidden-class.txt`, `probe-*.txt`, `corpus/lessons/round-57.md`). I authored none of it. Its
measured claims agree with my independent render (0/0/2/2); the entry's earlier dangling citation to
`corpus/lessons/round-57.md ## Wave findings` is now backed by a file that exists in the working tree.
Consequence for Main: integration is no longer "append my draft" but "reconcile two texts", and my
draft's additions are the exact fixture lines, the exit-0 population (10→8 of 36), the matrix diff, the
measured-render row check, the quote-count correction (F1), and four extra limits (code spans,
closer-line tail, line-start `<!-->` in the block class, evidence-scope wording).

**F7 — two of my named limits are already reproduced by the L1's own probe receipts** (read, not
authored by me, both untracked at this revision): `records/probe-code-span-overhide.txt` shows v6
refusing two filings (`CORRECTION-IN-FENCE … hidden_by=inline`, `EXIT=1`) where the render paints both;
`records/probe-second-opener-harm.txt` shows `filed=2 unfiled=0`, `EXIT=0` where the render hides both.
They corroborate limits 2 and 4 of my entry and give the first rendered `hidden_by=inline` lines the
freeze set lacks.

## Not done / out of scope

Counters v5/v6 and c2-counter not executed (that is the executor/mutation seats' evidence); no claim
receipt, no C1/C2 verdict, no admission decision. No `corpus/` or `census/` write; no lesson edit; no
git/jj mutation; no tool install or upgrade (markdown-it-py 4.2.0 and Python 3.14.8 were already
installed, `curl`/`awk`/`sha256sum` are host-provided). The render probe reproduces the builder's
correction blocks, not a whole fixture repository — stated in the entry as a limit.

## Artifacts

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/fetches.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/quotes.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/quote-verify.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/quote-verify.json`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/render-probe.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/render-probe.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/render-probe.json`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/rows-render-check.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/inline-html-comment-visibility-r57.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57scribe01/sources-rows.md`
