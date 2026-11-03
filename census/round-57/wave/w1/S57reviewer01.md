# ATTACK-FOUND — S57reviewer01, C1 v6

Axes: calibration correctness (hidden filing rejection and visible filing acceptance); operability (replayable receipts). Recommendation only; no admission, integration, or frozen-byte edits.

## Exact commands and environment

```sh
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57reviewer01 /fast/scratch/hyaku/souji-r57/S57reviewer01
uv venv /fast/scratch/hyaku/souji-r57/S57reviewer01/venv
uv pip install --python /fast/scratch/hyaku/souji-r57/S57reviewer01/venv/bin/python markdown-it-py==4.2.0
env TMPDIR=/fast/scratch/hyaku/souji-r57/S57reviewer01 PYTHONDONTWRITEBYTECODE=1 /fast/scratch/hyaku/souji-r57/S57reviewer01/venv/bin/python -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57reviewer01/attack.py
```

Observed run: 32 shapes; 10 HARM token observations, 16 OVER-HIDE, 37 AGREE, 1 NO-LITERAL-TOKEN. These are 64 token observations, not 64 fixtures. At fixture level: **5 HARM, 8 OVER-HIDE, 18 AGREE, 1 split-token lexical limit**. One OVER-HIDE fixture is the deliberately fenced-code control: its tokens render as code but are intentionally ineligible as filings, so it is **not a defect**. Thus 7 actual OVER-HIDE fixtures (14 tokens), plus 1 intentional code-policy mismatch (2 tokens).

Installed only in scratch: markdown-it-py 4.2.0 and dependency mdurl 0.1.2 via `uv pip`, in a CPython 3.15.0 `uv venv`; purpose independent CommonMark oracle. No host tool updates. Scratch removed after receipts were preserved.

Renderer: `MarkdownIt('commonmark').render(SCORECARD_bytes.decode())`. Strip actual HTML comments from its output with `re.compile(r'<!--(?:>|->|[\s\S]*?(?:--!?>|\Z))')`, then search for each complete correction token. This accounts for HTML abrupt empty comments and `--!>` browser terminators; it does not strip escaped `&lt;!--` text. `render.html` preserves the renderer output before stripping; `visible.html` preserves the result. This is rendered-HTML comment visibility, not a browser screenshot, and code-text visibility is explicitly distinguished from filing eligibility. No network URL in fixtures was fetched.

Each fixture is a new scratch git repository. The driver verifies its toplevel before configuration/add/commit; every git call names an absolute `-C`. Each has two stale annotations and two honest corrections except the split-token fixture, which intentionally breaks the first correction's lexical token. Counter measures committed tip with base=tip, isolating parsing from append-only deletion findings. All raw commands, full revision ids, instrument output and `EXIT=` lines are in the per-fixture `v6.txt` files. Scratch repos were deleted; retained SCORECARD bytes and driver reconstruct them (new commit identities may differ). `attacks.json` contains all observed verdicts; `differential.json` contains all 72 differential command/output pairs.

LSP unavailable: `read xd://lsp` returned `No such tool`; no status/references/definition/diagnostics endpoint exists here. Caller inspection therefore used literal grep fallback, **not semantic proof**. Read-only actual frozen v5→v6 diff reviewed. Git-show blobs at freeze d749f7ee081ec1b382b2f92577eb22bfba1c7761 matched the executed working-file bytes: v5 sha256 975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179; v6 sha256 e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4.

## Findings, by severity

### High — second opener skipped (new surviving HARM)

Cases 04, 05, 30 and 31 all render both honest correction tokens inside the second comment, but v6 exits 0, `filed=2 unfiled=0 fenced=0`, with no FINDING. `hidden_lines`, census/round-57/c1-counter.py:292–297 consumes a block opener's entire line; :322–329 jumps to the line after the first inline closer. Neither resumes scanning the closer's suffix. A second comment beginning on that line is never opened. This is not merely a partially hidden correction-line issue: the correction lines are wholly hidden on subsequent lines.

Named limit **SECOND-COMMENT-SUFFIX**: resume tokenization immediately after each closer, including block-close suffixes; process every opener on the same line and on closing lines. Catch with all four retained shapes. Case 05's first block consumes one line, but the following paragraph still contains a genuine second comment in the render.

### High — lazy four-space continuation (previously disclosed HARM)

Case 14 has a paragraph followed by `    <!--`, both corrections and a closer. Renderer keeps the indented opener in the paragraph and hides both filings. V6 exits 0 with `filed=2 unfiled=0 fenced=0`. The unconditional `indent <= 3` checks at :292 and :298 ignore paragraph state. Named limit **LAZY-PARAGRAPH-INDENT4**: decide indented-code eligibility using block/paragraph context, not leading-space count alone. Already disclosed in v6 docstring :148–150; this independently demonstrates its consequence, not a new frozen-claim failure.

### Medium — raw-source opener is not necessarily an HTML comment (new OVER-HIDE regression class)

Cases 22 (code span), 23 (backslash escape), 24 (link destination), 32 (code span after a block) render both corrections visibly, but v6 exits 1 with two `CORRECTION-IN-FENCE hidden_by=inline` findings. The blind `raw.find('<!--', pos)` at :302 cannot distinguish parsed inline tokens. Named limits **CODE-SPAN-OPENER**, **ESCAPED-OPENER**, **LINK-DESTINATION-OPENER**: derive comments from parsed inline tokens, respecting code spans, escapes and destinations before scanning HTML. Code-span cases are two arrangements of the same limit. These are visible paragraph filings, unlike the fenced-code policy control.

### Medium — abrupt block comment terminators over-hide (carry-over)

Cases 08 (`<!-->`) and 09 (`<!--->`) close on their own line in rendered HTML, but v6 block branch :292–295 searches only for a later `-->`, hiding both visible corrections to EOF. Both exit 1 with two `hidden_by=block` findings. Named limit **ABRUPT-BLOCK-CLOSE**: handle abrupt empty-comment close forms in block branch as inline branch already does at :306–308.

Case 19's `--!>` terminates the rendered HTML comment, but the block state at :282 only recognizes `-->`, so both visible corrections are refused. Named limit **HTML-BANG-CLOSE**: if browser-visible filing is the contract, recognize HTML comment tokenizer's bang-close transition. This specifically concerns the HTML post-render layer; CommonMark block termination itself uses `-->`. Do not claim it refutes the preregistered CommonMark-only approximation.

## Complete shape table

A/B are the SCORECARD and preregistration correction tokens respectively. AGREE means comment visibility vs hidden-filing decision agrees; it does not imply overall exit 0. Every receipt directory has fixture bytes, render excerpt/full HTML, stripped HTML, exit/findings and full command.

| Shape / receipt directory | A | B | v6 exit |
|---|---|---|---:|
| [ 01-block ](S57reviewer01/01-block/v6.txt) | AGREE | AGREE | 1 |
| [ 02-block-three-spaces ](S57reviewer01/02-block-three-spaces/v6.txt) | AGREE | AGREE | 1 |
| [ 03-inline ](S57reviewer01/03-inline/v6.txt) | AGREE | AGREE | 1 |
| [ 04-two-inline-openers ](S57reviewer01/04-two-inline-openers/v6.txt) | HARM | HARM | 0 |
| [ 05-two-block-openers ](S57reviewer01/05-two-block-openers/v6.txt) | HARM | HARM | 0 |
| [ 06-opener-in-fence ](S57reviewer01/06-opener-in-fence/v6.txt) | AGREE | AGREE | 0 |
| [ 07-closer-following-correction ](S57reviewer01/07-closer-following-correction/v6.txt) | AGREE | AGREE | 1 |
| [ 08-abrupt-block-bang ](S57reviewer01/08-abrupt-block-bang/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 09-abrupt-block-dash ](S57reviewer01/09-abrupt-block-dash/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 10-abrupt-inline-bang ](S57reviewer01/10-abrupt-inline-bang/v6.txt) | AGREE | AGREE | 0 |
| [ 11-abrupt-inline-dash ](S57reviewer01/11-abrupt-inline-dash/v6.txt) | AGREE | AGREE | 0 |
| [ 12-unclosed-block ](S57reviewer01/12-unclosed-block/v6.txt) | AGREE | AGREE | 1 |
| [ 13-unclosed-inline ](S57reviewer01/13-unclosed-inline/v6.txt) | AGREE | AGREE | 0 |
| [ 14-lazy-indent4 ](S57reviewer01/14-lazy-indent4/v6.txt) | HARM | HARM | 0 |
| [ 15-indent4-after-blank ](S57reviewer01/15-indent4-after-blank/v6.txt) | AGREE | AGREE | 0 |
| [ 16-crlf-inline ](S57reviewer01/16-crlf-inline/v6.txt) | AGREE | AGREE | 1 |
| [ 17-nested-block ](S57reviewer01/17-nested-block/v6.txt) | AGREE | AGREE | 1 |
| [ 18-closer-before-opener ](S57reviewer01/18-closer-before-opener/v6.txt) | AGREE | AGREE | 1 |
| [ 19-bang-closer-block ](S57reviewer01/19-bang-closer-block/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 20-bang-closer-inline ](S57reviewer01/20-bang-closer-inline/v6.txt) | AGREE | AGREE | 0 |
| [ 21-split-token ](S57reviewer01/21-split-token/v6.txt) | NO-LITERAL-TOKEN | AGREE | 1 |
| [ 22-inline-code-opener ](S57reviewer01/22-inline-code-opener/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 23-escaped-opener ](S57reviewer01/23-escaped-opener/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 24-link-destination ](S57reviewer01/24-link-destination/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 25-list-container ](S57reviewer01/25-list-container/v6.txt) | AGREE | AGREE | 1 |
| [ 26-tab-lazy ](S57reviewer01/26-tab-lazy/v6.txt) | AGREE | AGREE | 1 |
| [ 27-fence ](S57reviewer01/27-fence/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |
| [ 28-fence-vt-closer ](S57reviewer01/28-fence-vt-closer/v6.txt) | AGREE | AGREE | 0 |
| [ 29-one-line-wrapper ](S57reviewer01/29-one-line-wrapper/v6.txt) | AGREE | AGREE | 1 |
| [ 30-empty-comment-then-block ](S57reviewer01/30-empty-comment-then-block/v6.txt) | HARM | HARM | 0 |
| [ 31-second-opener-closer-line ](S57reviewer01/31-second-opener-closer-line/v6.txt) | HARM | HARM | 0 |
| [ 32-block-then-inline-code ](S57reviewer01/32-block-then-inline-code/v6.txt) | OVER-HIDE | OVER-HIDE | 1 |

Case 07 covers closer and following correction on the same line: renderer shows it, but it is not a lexed filing (`--> R52...` does not match anchored CORR_RE); overall exit 1 comes from SUMMARY `unfiled=1`, with no FINDING emitted. Case 21's split token becomes visually joined after comment removal but is absent as a contiguous literal correction in source; v6 likewise exits 1 with SUMMARY `unfiled=1` and no FINDING. Named limit **RENDERED-TOKEN-LEXING**: if rendered corrections count, tokenize visible text before matching corrections. These are not falsely reported as HARM. Case 28's exotic fence closer leaves tokens rendered inside code; v6 accepts, matching literal visibility but not code eligibility. This is the already-disclosed exotic rstrip fence limitation (:154–157), not a new comment defect.

## Per-mismatch receipts

All HARM cases exit 0 with no finding; all OVER-HIDE cases below exit 1 with actual emitted findings. Fixture bytes are retained exactly, including CRLF for case 16. Render excerpts below are the relevant final lines (full renderer output linked).

### 04-two-inline-openers

[Exact fixture](S57reviewer01/04-two-inline-openers/SCORECARD.md), [render](S57reviewer01/04-two-inline-openers/render.html), [stripped render](S57reviewer01/04-two-inline-openers/visible.html), [full command and exit receipt](S57reviewer01/04-two-inline-openers/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>prose <!-- one --> <!-- two
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--></p>
```

```text
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f35fab01b2b5 base=f35fab01b2b5
EXIT=0
```

### 05-two-block-openers

[Exact fixture](S57reviewer01/05-two-block-openers/SCORECARD.md), [render](S57reviewer01/05-two-block-openers/render.html), [stripped render](S57reviewer01/05-two-block-openers/visible.html), [full command and exit receipt](S57reviewer01/05-two-block-openers/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<!-- one --> <!-- two
<p>R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--&gt;</p>
```

```text
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=1fa1c5f076f4 base=1fa1c5f076f4
EXIT=0
```

### 08-abrupt-block-bang

[Exact fixture](S57reviewer01/08-abrupt-block-bang/SCORECARD.md), [render](S57reviewer01/08-abrupt-block-bang/render.html), [stripped render](S57reviewer01/08-abrupt-block-bang/visible.html), [full command and exit receipt](S57reviewer01/08-abrupt-block-bang/v6.txt).

```html
<p>| row | note |
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<!-->
<p>R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=block
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=block
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=e02b24cc0afc base=e02b24cc0afc
EXIT=1
```

### 09-abrupt-block-dash

[Exact fixture](S57reviewer01/09-abrupt-block-dash/SCORECARD.md), [render](S57reviewer01/09-abrupt-block-dash/render.html), [stripped render](S57reviewer01/09-abrupt-block-dash/visible.html), [full command and exit receipt](S57reviewer01/09-abrupt-block-dash/v6.txt).

```html
<p>| row | note |
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<!--->
<p>R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=block
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=block
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=dfb4652397e1 base=dfb4652397e1
EXIT=1
```

### 14-lazy-indent4

[Exact fixture](S57reviewer01/14-lazy-indent4/SCORECARD.md), [render](S57reviewer01/14-lazy-indent4/render.html), [stripped render](S57reviewer01/14-lazy-indent4/visible.html), [full command and exit receipt](S57reviewer01/14-lazy-indent4/v6.txt).

```html
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>paragraph
<!--
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--></p>
```

```text
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=19d3f652c753 base=19d3f652c753
EXIT=0
```

### 19-bang-closer-block

[Exact fixture](S57reviewer01/19-bang-closer-block/SCORECARD.md), [render](S57reviewer01/19-bang-closer-block/render.html), [stripped render](S57reviewer01/19-bang-closer-block/visible.html), [full command and exit receipt](S57reviewer01/19-bang-closer-block/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<!--
--!>
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site SCORECARD.md:5) hidden_by=block
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site census/round-51/preregistration.txt:3) hidden_by=block
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=23db5083a3d5 base=23db5083a3d5
EXIT=1
```

### 22-inline-code-opener

[Exact fixture](S57reviewer01/22-inline-code-opener/SCORECARD.md), [render](S57reviewer01/22-inline-code-opener/render.html), [stripped render](S57reviewer01/22-inline-code-opener/visible.html), [full command and exit receipt](S57reviewer01/22-inline-code-opener/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>prose <code>&lt;!--</code>
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--&gt;</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=inline
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=inline
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=e48d663479e7 base=e48d663479e7
EXIT=1
```

### 23-escaped-opener

[Exact fixture](S57reviewer01/23-escaped-opener/SCORECARD.md), [render](S57reviewer01/23-escaped-opener/render.html), [stripped render](S57reviewer01/23-escaped-opener/visible.html), [full command and exit receipt](S57reviewer01/23-escaped-opener/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>prose &lt;!--
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--&gt;</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=inline
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=inline
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=b35bb5b91b94 base=b35bb5b91b94
EXIT=1
```

### 24-link-destination

[Exact fixture](S57reviewer01/24-link-destination/SCORECARD.md), [render](S57reviewer01/24-link-destination/render.html), [stripped render](S57reviewer01/24-link-destination/visible.html), [full command and exit receipt](S57reviewer01/24-link-destination/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p><a href="https://example.invalid/%3C!--">link</a>
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--&gt;</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=inline
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=inline
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=584bd37577a5 base=584bd37577a5
EXIT=1
```

### 27-fence

[Exact fixture](S57reviewer01/27-fence/SCORECARD.md), [render](S57reviewer01/27-fence/render.html), [stripped render](S57reviewer01/27-fence/visible.html), [full command and exit receipt](S57reviewer01/27-fence/v6.txt).

```html
<p>| row | note |
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<pre><code>R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
</code></pre>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=fence
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=fence
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=ca90585ff6b1 base=ca90585ff6b1
EXIT=1
```

### 30-empty-comment-then-block

[Exact fixture](S57reviewer01/30-empty-comment-then-block/SCORECARD.md), [render](S57reviewer01/30-empty-comment-then-block/render.html), [stripped render](S57reviewer01/30-empty-comment-then-block/visible.html), [full command and exit receipt](S57reviewer01/30-empty-comment-then-block/v6.txt).

```html
|---|---|
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>prose <!----> <!--
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--></p>
```

```text
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=634e57fe9dbc base=634e57fe9dbc
EXIT=0
```

### 31-second-opener-closer-line

[Exact fixture](S57reviewer01/31-second-opener-closer-line/SCORECARD.md), [render](S57reviewer01/31-second-opener-closer-line/render.html), [stripped render](S57reviewer01/31-second-opener-closer-line/visible.html), [full command and exit receipt](S57reviewer01/31-second-opener-closer-line/v6.txt).

```html
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<p>prose <!-- first
--> <!-- second
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--></p>
```

```text
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=db394c748190 base=db394c748190
EXIT=0
```

### 32-block-then-inline-code

[Exact fixture](S57reviewer01/32-block-then-inline-code/SCORECARD.md), [render](S57reviewer01/32-block-then-inline-code/render.html), [stripped render](S57reviewer01/32-block-then-inline-code/visible.html), [full command and exit receipt](S57reviewer01/32-block-then-inline-code/v6.txt).

```html
| C1 | command <code>grep -c &quot;^ADDED&quot; census/round-51/records/ws-drift-vs-r46.tsv</code> (78) recomputed below |</p>
<!-- first -->
<p><code>&lt;!--</code>
R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79
R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79
--&gt;</p>
```

```text
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site SCORECARD.md:5) hidden_by=inline
FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site census/round-51/preregistration.txt:3) hidden_by=inline
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=no
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=no
SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=f0bcfc12f155 base=f0bcfc12f155
EXIT=1
```

## Differential — AGREE with frozen matrix predicate

All 36 committed C1 fixture repositories rebuilt using the frozen round-57 builder, and both v5 and v6 executed against identical committed bytes. Full ordered FINDING ids extracted, not only first finding. Results: v5 10 exit-0; v6 8 exit-0. Only B4-INLINE-NBSP-OPENER and C4-INLINE-CLOSED-COMMENT moved (0→1, no findings→two CORRECTION-IN-FENCE). **No carry-over row moved** (all 33 retained rows identical exit and ordered finding-id lists); C6 remained 0. Detail strings are deliberately not claimed byte-identical because v6 adds hidden_by. Complete outputs and exact per-arm commands: [differential.json](S57reviewer01/differential.json).

| Fixture | v5 exit / full ordered ids | v6 exit / full ordered ids |
|---|---|---|
| F1-HONEST-TIP | 0 / - | 0 / - |
| F2-MULTI-ANNOT | 1 / MULTIPLE-ANNOTATIONS,INERT-CORRECTION | 1 / MULTIPLE-ANNOTATIONS,INERT-CORRECTION |
| F3-INERT | 1 / INERT-CORRECTION | 1 / INERT-CORRECTION |
| F4-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F5-REWRITE | 1 / DELETED-LINES | 1 / DELETED-LINES |
| F6-RECORD-DRIFT | 1 / RECORD-SHA-MISMATCH,DELETED-LINES,DELETED-LINES | 1 / RECORD-SHA-MISMATCH,DELETED-LINES,DELETED-LINES |
| F7-TILDE-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F8-BT4-PARITY | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F9-HTML-COMMENT | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F10-STRADDLE | 1 / ZONE-TOKEN-STRADDLES-EDGE,INERT-CORRECTION | 1 / ZONE-TOKEN-STRADDLES-EDGE,INERT-CORRECTION |
| F11-BOGUS-RECOMP | 1 / BOGUS-RECOMPUTED | 1 / BOGUS-RECOMPUTED |
| F12-LOG-UNFILED | 1 / UNFILED-SOURCES-ANNOTATION | 1 / UNFILED-SOURCES-ANNOTATION |
| F12b-LOG-FILED | 0 / - | 0 / - |
| F7-FF | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F12c-LOG-POINTER-EXEMPT | 0 / - | 0 / - |
| F8b-BT4-SHORT-RUN | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F13-DUAL-ANCHOR | 1 / ANCHOR-ALIAS-MISMATCH | 1 / ANCHOR-ALIAS-MISMATCH |
| F14-PAIR-STALE-FILING | 1 / PAIR-FILING-INERT | 1 / PAIR-FILING-INERT |
| F15-PAIR-NOROWS | 1 / UNFILED-SOURCES-ANNOTATION | 1 / UNFILED-SOURCES-ANNOTATION |
| F16-PAIR-ARROW | 1 / UNFILED-SOURCES-ANNOTATION | 1 / UNFILED-SOURCES-ANNOTATION |
| F17-INDENT4-FENCE | 0 / - | 0 / - |
| F18-BTINFO-FENCE | 0 / - | 0 / - |
| F19-PAIR-IN-FENCE | 0 / - | 0 / - |
| F20-R1-INDENT-SWALLOW | 1 / BOGUS-RECOMPUTED,BOGUS-RECOMPUTED | 1 / BOGUS-RECOMPUTED,BOGUS-RECOMPUTED |
| F21-R1-ONELINE-SWALLOW | 1 / BOGUS-RECOMPUTED,CORRECTION-IN-FENCE,BOGUS-RECOMPUTED,CORRECTION-IN-FENCE | 1 / BOGUS-RECOMPUTED,CORRECTION-IN-FENCE,BOGUS-RECOMPUTED,CORRECTION-IN-FENCE |
| F22-PTR-TIMESTAMP | 1 / UNFILED-SOURCES-ANNOTATION | 1 / UNFILED-SOURCES-ANNOTATION |
| F23-SOURCES-RECOMP | 1 / SOURCES-RECOMPUTE-MISMATCH | 1 / SOURCES-RECOMPUTE-MISMATCH |
| F7-FF2 | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| F24-PAIR-HIDDEN-FILING | 1 / UNFILED-SOURCES-ANNOTATION,PAIR-FILING-HIDDEN | 1 / UNFILED-SOURCES-ANNOTATION,PAIR-FILING-HIDDEN |
| F26-INDENT4-COMMENT-OPENER | 1 / UNFILED-SOURCES-ANNOTATION | 1 / UNFILED-SOURCES-ANNOTATION |
| F27-BINARY-NUMSTAT | 1 / DELETIONS-UNREADABLE-BINARY | 1 / DELETIONS-UNREADABLE-BINARY |
| F28-NUL-CORRECTION-UNCHANGED | 1 / CORRECTION-FILE-BINARY | 1 / CORRECTION-FILE-BINARY |
| F29-PROSE-COMMENT-MENTION | 0 / - | 0 / - |
| B4-INLINE-NBSP-OPENER | 0 / - | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| C4-INLINE-CLOSED-COMMENT | 0 / - | 1 / CORRECTION-IN-FENCE,CORRECTION-IN-FENCE |
| C6-INLINE-SAME-LINE | 0 / - | 0 / - |

## Affected callers and residual risks / verification gaps

Canonical counter logic, not an alternate implementation, decides filings: `measure` computes correction hidden lines at :427, emits CORRECTION-IN-FENCE at :511–514, uses the same map to filter pair filings at :556 and to set filed status at :596–597. `hidden_lines` also suppresses pair annotation sites at :536–539, so over-hide can suppress a real annotation rather than just reject a filing. The attack receipts exercise R52 filing and final status; propagated R53/pair-site impacts are code-path inferences, not independently exercised attacks. No C2, resume, routing identity, runtime saturation or integration admission claim is made; those are outside this seat's scope.

The bounded 36-fixture C1 target survives this differential, but a universal renderer-equivalence claim would be false. The new SECOND-COMMENT-SUFFIX HARM and visible-source-context over-hide shapes are outside that frozen population and should be routed as named limits, not repaired in frozen bytes. The lazy indent and exotic fence limits are already disclosed. No selftest, real-lane measurement, browser GUI, or unrelated suite was run; the requested direct 36-row differential and 32-shape attack were run. HTML visibility is determined by retained CommonMark output plus explicit comment stripping, not a full HTML DOM/CSS implementation. No production/source files changed.

Self-evaluation: accuracy 4/5 (explicit HTML postprocessing rather than browser DOM); completeness 4/5 (32 shapes and complete differential, pair-form propagation unexercised); clarity 4/5 (literal-render visibility distinguished from code eligibility); actionability 4/5 (exact bytes and commands retained, scratch repos intentionally removed); conciseness 4/5 (per-mismatch raw receipts deliberately verbose for auditability). Overall 4.0/5. Improvements: browser-tokenizer corroboration and separate pair-form tests would reduce residual oracle/caller uncertainty without altering frozen instruments. Would the user agree? Evidence is replayable, limitations are explicit, and no green frozen-matrix result is substituted for adversarial coverage.
