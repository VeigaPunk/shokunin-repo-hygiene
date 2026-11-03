# souji round 55, wave w1 — seat S55scribe01 (scribe)

Role: independent re-verification of the round's new SOURCES row **S278** (the Python
`str.splitlines()` documentation, the frontier-step source for the C1 v4 one-line model) and
drafting the round lesson's `## Gate` block, the `## Search log` line and the used-by
old→new line for the L1 to integrate.

Full report with every command and verbatim output: `.ufo/waves/round-55/w1/S55scribe01/S55scribe01-report.md`.
Receipts: `.ufo/waves/round-55/w1/S55scribe01/receipts/`.
Drafts: `.ufo/waves/round-55/w1/S55scribe01/draft/`.

Verdict: **PASS** on the source and the quotes. **One landing finding was raised (§3), accepted
by the L1, and closed — verified with the lane's own instrument after the landing commit.**
Nothing was landed by this seat; no lane file was written by this seat.

## 1. Frozen pins

All six pinned sha256s verified against the lane root before any probing — c1-counter, c2-counter,
build-fixtures, run-matrix, c1-selftest-expected, c2-selftest-expected. **All match.** The
frozen preregistration was read first.

## 2. Live re-open of S278 — PASS

```
$ curl -sSL -o s278.html -w '%{http_code} %{url_effective}\n' \
    'https://docs.python.org/3.12/library/stdtypes.html#str.splitlines'
200 https://docs.python.org/3.12/library/stdtypes.html#str.splitlines
```

`num_redirects=0`; `648964` bytes; sha256
`0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352` — **equal to the seat
spec's expected digest and byte-equal to the committed capture**
`census/round-55/sources/s278-python-stdtypes.html` (`cmp` exit 0).

All four located quotes re-checked with the recorded recipe (strip `script`/`style`, strip
tags, `html.unescape`, collapse whitespace runs) against the live bytes: recorded
`substring=True` and word counts **18 / 15 / 25 / 13** all match the measured values; all
four are ≤25 words. Page heading `Python 3.12.` present — full heading
`Python 3.12.16 documentation`. All four quotes sit in the `str.splitlines(keepends=False)`
section.

The scope sentence is grounded in the **frozen bytes**, not in prose: the v3 counter's
`hidden_lines()` numbers with `text.splitlines()`, the v4 counter's with `text.split('\n')` —
and `splitlines()` splits `'A\x0cB\x0c~~~fence\ncorrection\n'` into 4 lines where LF-only
splits it into 3. That is the r54 HIGH sentinel S1 mechanism the source documents.

## 3. Finding the L1 must act on before landing (Q62)

`corpus/knowledge/splitlines-line-model.md` (new, untracked) cites **S277** in its
front-matter `source:` line. `corpus/QUALITY.md` **Q62** requires the citation to be
bidirectional: an S-id an entry cites must be a row whose `used-by` lists that entry. S277's
`used-by` cell lists only the r54 entry, so the K1 arm of
`tools/souji-registry-agreement.py` prints — measured by replaying the tool's own K1 logic
read-only:

```
K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md
```

Absent at HEAD (2 pre-existing disagreements), present in the working tree (3) — the delta is
exactly that one line.

**Re-verified after the L1 landed `corpus/lessons/round-55.md` and the S278 row: the result
is unchanged.** The L1's landed lesson says at `corpus/lessons/round-55.md:38-40`:

> - Reuse: **S277** (CommonMark 0.31.2 §4.5/§4.6) and **S276** (gitignore PATTERN FORMAT) are
>   cited by the r54 knowledge entries and unchanged this round. **No status, recheck or
>   used-by cell of an existing row changed.**

That sentence was **incorrect as written**: Q62 is triggered by the *new entry's* `source:`
line, which cited S277, so S277's `used-by` cell had to change or the citation had to be
dropped.

**CLOSED — verified with the lane's own instrument after the L1's landing commit `913fa479`:**

```
$ python3 -B tools/souji-registry-agreement.py --root . \
    --rev 913fa4791115eb9e4f69dd729588ca84756d0828 \
    --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md
SUMMARY k1=2 k2=0 mismatches=2 rev=913fa4791115eb9e4f69dd729588ca84756d0828
RC=1
```

The S277 disagreement is **gone**; the count is back to the 2 pre-existing disagreements
present at every earlier rev measured (`3ce0ba03`, the r55 freeze `e8f33867` — both
`k1=2 k2=0 mismatches=2`). The L1 accepted the finding and applied the **citation-drop**
closure: the new entry's `source:` line now cites only S278, with the S277 link kept as prose
(and S277 still named in the entry body). The S278 row's `recheck` cell was also set to
`on-release`, matching its sibling python-docs rows. The lesson's reuse sentence is now
accurate.

The other two K1 disagreements (`S146` cited-no-row, `S110` cited-not-in-used-by) are
**pre-existing at HEAD**, not caused by this round; named here only so they are not
misattributed.

## 4. Drafted fragments (in the seat directory; the L1 integrates)

- `draft/gate-block-s278.md` — the round-55 lesson `## Gate` block for S278: URL, access date
  2026-11-03, the four quotes with section location and word counts, tier A docs, the scope
  sentence, status `mined`, used-by `corpus/knowledge/splitlines-line-model.md`, the
  independent re-check and the frozen-bytes mechanism re-measurement.
- `draft/search-log-line.md` — the `corpus/SOURCES.md` `## Search log` line: question, where,
  date, counts (identified 1 / screened 1 / included 1 (S278) / excluded 0), the stop
  condition, and the counts spelled out — one page fetched, zero rejected.
- `draft/used-by-old-to-new.md` — the S277 used-by old→new line with the Q62 reason, the
  exact old/new cell values, and the house-shaped `## Gate` bullet.

## 5. Other observations for the L1

- The S278 registry row, the new knowledge entry and `corpus/lessons/round-55.md` are
  **landed** by the L1 at commit `913fa479`; this seat found them in place and wrote none.
  **Every verifiable fact in the landed Gate bullet matches this seat's independent
  measurement** — URL, access date, HTTP 200, "no redirect", 648964 bytes, the sha256, the
  capture path, the quote-file path, the recipe, "all `substring=True`", and the four word
  counts 18/15/25/13.
- The S278 row is census-clean: `awk -F'|' NF` = 13 (11 columns), no enum or tier-inflation
  violations, no mined row with a missing `used-by` path, no duplicate ids.
- `recheck=180d` → `on-release`: **closed by the L1** at `913fa479`, matching the sibling
  python-docs rows.
- The landed row's `scope` cell wording differs from this seat's assignment wording; the
  landed Gate bullet reads "scope: the line-boundary set", consistent with the row. The L1's
  wording is internally consistent — noted, no action required.

### 5.1 Two landing gaps still open at `913fa479` (reported to the L1)

1. **The r55 `## Search log` entry is not in `corpus/SOURCES.md`** —
   `git show HEAD:corpus/SOURCES.md | grep -c "Round-55 bounded source search"` → **0**. The
   section's latest entries are "Round-54 bounded source search", "Round-41", "Round-40"; r54
   landed its search-log line there. The landed r55 **lesson** carries the bullet
   (`corpus/lessons/round-55.md:41`, "identified 1, screened 1, included 1, excluded 0"), so
   the counts are in the lesson but the registry-side entry is missing. **The drafted line is
   ready to integrate**: `S55scribe01/draft/search-log-line.md`.
2. **No `corpus/README.md` frontier note for round 55** —
   `git show HEAD:corpus/README.md | grep -c "splitlines-line-model"` → **0**; the frontier
   sections stop at "## Round 54 frontier update".

Neither is a defect in the frozen bytes and neither is this seat's to close (leaf; no corpus
file written). Also noted, not a finding: no "Round-55 provenance" paragraph in
`corpus/SOURCES.md` — the provenance paragraphs run Round-13…Round-51 and r52/53/54 added
none, so it is not a strict house rule.

## 6. Honesty

No counter was executed and **no acceptance claim is made**; the counters' verdicts are the
L1's. No tool was installed or upgraded. Nothing outside the seat directory and the seat
scratch was written; no mutating git or jj command was run; the scratch tree was deleted
before this report was written.
