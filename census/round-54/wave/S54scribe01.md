# Souji Round 54 — Seat S54scribe01 (scribe) report

- **Seat**: S54scribe01 (scribe)
- **Wave**: round-54 / w1 (12 seats; the L1 holds the canonical planner seat, SoujiR54)
- **Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only to this seat — no lane
  tracked file was written or modified)
- **Freeze commit**: `3c394cab0cd406bbab72b8d365e0f3deed4ef98a`; base `fe12daad2549f534650d406ebdbac9113d59313f`
- **Lane tip at measurement**: `bfdbb336329e6afba3ab1ca83cbd6d9759271062`
- **Scratch**: `/fast/scratch/hyaku/souji-r54/S54scribe01/` (deleted before yield)
- **Verdict**: **PASS** — the source was opened live today; all three located quotes are
  verbatim substrings of the tag-stripped capture; all five corpus drafts are written to
  this seat directory. Nothing was landed (the L1 integrates).

---

## 1. Live fetch evidence (CommonMark spec 0.31.2)

Command (run in the seat scratch; absolute paths only elsewhere):

```
$ curl -sSL -o s277-commonmark-spec.html -w '%{http_code} %{url_effective}' https://spec.commonmark.org/0.31.2/
200 https://spec.commonmark.org/0.31.2/
```

| fact | value |
|---|---|
| HTTP code | `200` |
| url_effective | `https://spec.commonmark.org/0.31.2/` (no redirect) |
| bytes | `514698` |
| sha256 | `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` |
| access date | 2026-11-03 |
| page's stated version | `Version 0.31.2 (2024-01-28)` |

The capture is copied byte-identically into this seat directory
(`s277-commonmark-spec.html`, sha256 `c85f56cc…f0d` — verified by `sha256sum` on the
copy). Receipt: `receipts/live-fetch.txt`.

Tag-stripped capture recipe (the **r53 S276 recipe**, so the L1 re-derives it identically):
strip `script`/`style`, strip tags, unescape entities, collapse whitespace.

## 2. The three located quotes (all verified)

Each quote is ≤25 words, each was located by me in today's capture, and each was checked
with a python one-liner against the tag-stripped capture. Full file:
`s277-located-quotes.txt`; receipt with the exact commands and verbatim output:
`receipts/quote-substring-check.txt`.

| # | section | quote | words | substring |
|---|---|---|---|---|
| a | § 4.5 Fenced code blocks | "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)." | 17 | **True** |
| b | § 4.5 Fenced code blocks | "same type as the code block began with (backticks or tildes), and with at least as many backticks or tildes as the opening code fence" | 25 | **True** |
| c | § 4.6 HTML blocks | "Start condition: line begins with the string <!--. End condition: line contains the string -->." | 15 | **True** |

Corroborating located sentences in § 4.5 (also verbatim substrings, also ≤25 words):
"The closing code fence must use the same character as the opening fence" (13 words) and
"The closing code fence must be at least as long as the opening fence" (14 words).

Verbatim check output (the exact one-liner is in the receipt):

```
a substring: True words: 17
b substring: True words: 25
c substring: True words: 15
exit=0
```

## 3. Drafted artifacts (all inside this seat directory)

| path | what it is |
|---|---|
| `s277-located-quotes.txt` | the three located quotes with sections, word counts and substring verdicts, plus the re-runnable one-liner |
| `s277-commonmark-spec.html` | the live capture (514698 bytes, sha256 `c85f56cc…f0d`) for the L1 to land as `census/round-54/sources/s277-commonmark-spec.html` |
| `s277-row.tsv` | the drafted SOURCES registry row S277 — one pipe-row, 11 columns (`awk -F'|' NF` = 13), no `|` inside any cell |
| `draft/corpus/knowledge/correction-filing-fence-grammar.md` | the drafted knowledge entry |
| `draft/corpus/lessons/round-54.md` | the drafted round-54 lesson skeleton (## Gate, spot-check placeholder, empty ## Mistakes table) |
| `draft/LOG.md.round-54-entry.md` | the drafted LOG.md round-54 entry skeleton |
| `draft/corpus-README.round-54-frontier-note.md` | the drafted corpus/README.md frontier-note skeleton |
| `receipts/live-fetch.txt`, `receipts/quote-substring-check.txt` | command receipts |

### S277 row shape check

`grep -oE '^\| *S[0-9]+' corpus/SOURCES.md | sort | tail -3` → `S274`, `S275`, `S276`
(`S277` absent, count 0) — so **S277 is the next unused id**. The drafted row is
`| S277 | CommonMark spec 0.31.2 — fenced code blocks + HTML blocks — https://spec.commonmark.org/0.31.2/ | docs | A | souji correction-filing hidden-line grammar (C1 v3 fences) | … | … | queued | 2026-11-03 | on-release | corpus/knowledge/correction-filing-fence-grammar.md |`.
`awk -F'|' NF` = 13 → 11 columns, matching the contract census check. `kind=docs`,
`tier=A`, `status=queued` are all inside the census enum
(`census/round-12/sources-census.sh`). The URL does not yet appear in `corpus/SOURCES.md`
(`grep -c 'spec.commonmark.org' corpus/SOURCES.md` → 0), so no duplicate-URL warning is
raised for S277.

### The C1 v3 LOG/README SOURCES-pair scan (the constraint on the LOG/README drafts)

The v3 counter scans `LOG.md` and `corpus/README.md` line by line; a line that carries the
registry path token **and** a `<N> -> <M> rows` pair, with no path:line pointer, is a
candidate `UNFILED-SOURCES-ANNOTATION`. I checked my two skeletons against that rule by
replaying the counter's own regexes (`PAIR_ANNOT_RE`, `PTR_RE`) over the drafted text:

```
LOG draft      path-token-lines=0  UNFILED candidates: none
README draft   path-token-lines=0  UNFILED candidates: none
lesson draft   path-token-lines=0  UNFILED candidates: none
S277 row       path-token-lines=0  UNFILED candidates: none
```

Both skeletons therefore carry the registry count as `registry rows <N> -> <M>` with the
registry path token kept **off** that line, and each carries the instruction for the L1 to
keep it that way.

## 4. What the knowledge entry claims, and how each claim is grounded

- The v3 grammar (tilde / 4-backtick-parity / HTML-comment hidden-line fences, the
  zone-edge straddle refusal, the bogus-recomputed refusal, the LOG/README SOURCES-pair
  scan with the `>current-count` rule and the path:line-pointer exemption) is read from
  the **frozen counter bytes**, not asserted:
  `census/round-54/c1-counter.py` sha256 `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e`
  and `census/round-54/c2-counter.py` sha256 `84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09`
  — both equal the prereg's instrument pins (re-verified by `sha256sum`).
- The r53 routed items each check answers are named with their fixture ids and expected
  findings, read from `census/round-54/records/c1-selftest-expected.tsv` and
  `c2-selftest-expected.tsv`: R1 → F7/F8/F9 (`CORRECTION-IN-FENCE`), R2 → F10
  (`ZONE-TOKEN-STRADDLES-EDGE`), R3 → F11 (`BOGUS-RECOMPUTED`), r53 Mistakes row 5 → F12
  (`UNFILED-SOURCES-ANNOTATION`, with F12b the green honest arm), R4 → FA4
  (`COMMENT-AMBIGUOUS-NAME`).
- The named limits are quoted **verbatim** from `census/round-54/preregistration.txt`
  ("Named limits carried into v3 (disclosed, not fixed)").
- The S276 dependency is marked: the C2 `#`-row tab-rule refusal grounds on S276's
  gitignore comment rule, cited as the entry's second source, and the lesson records
  S276's used-by change old→new.

### Measured divergences between the CommonMark text and the frozen counter (disclosed, not edited)

I exercised the frozen `hidden_lines()` read-only (import of the committed file; no byte
written) and compared it with the located spec sentences. Two places where the counter's
line-level grammar is **more conservative** than the spec text (it hides more, so it
refuses more):

1. The counter strips leading spaces before matching a fence opener, so a fence indented by
   four or more spaces is read as a fence; CommonMark reads that shape as an indented code
   block, which does not open a fence.
2. The counter recognises a `<!--` anywhere on a line; CommonMark's type-2 start condition
   is a line that **begins** with `<!--`.

On the closing fence the two readings agree on the case that matters: a closing fence
followed by other text is not a closing fence for either. These are recorded in the entry
under "Named limits" as measured statements, and they are **not** edits to the frozen
bytes. Probe receipt (the frozen file's own sha256, the exact probe and its verbatim
output): `receipts/divergence-probe.txt`.

## 5. Honesty statement

- The source was opened live by this seat on 2026-11-03; the fetch, byte count, digest and
  the page's stated version are recorded above and in `receipts/`.
- All three quotes were verified with a runnable python one-liner against today's capture;
  the output is pasted verbatim in `receipts/quote-substring-check.txt`.
- I did **not** run either counter and make **no** acceptance claim. The counters' verdict
  is the L1's at the measured revision. The drafts carry the L1's measurement placeholders
  (the lesson's `## Mistakes` table is empty; the LOG/README counts are placeholders).
- No finding was invented. The `## Mistakes` table in the drafted lesson is empty by
  construction, and the Gate's "rejected: none-yet" carries the sweep-honesty note.
- No tool was installed or upgraded by this seat (no install to record).
- Nothing outside this seat directory and the seat scratch was written. No git or jj
  mutating command was run anywhere; the only git calls were read-only (`log`, `show`,
  `rev-parse`, `status`) with `GIT_OPTIONAL_LOCKS=0`.

## 6. Limits of this seat's work

- The L1 verifies the three quotes against the capture before landing them; the capture is
  here for that purpose (`s277-commonmark-spec.html`).
- The drafted SOURCES row is `queued`, not `mined`; the L1 sets the landed status.
- The drafted lesson and LOG/README skeletons carry the L1's measurement placeholders
  (claim evidence, wave findings, routed defects, standing checks, registry counts) — I
  did not fill them, because the measurements are the L1's and the wave's.
