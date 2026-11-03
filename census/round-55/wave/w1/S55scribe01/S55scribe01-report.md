# Souji Round 55 — Seat S55scribe01 (scribe) — S278 independent re-verification + Gate draft

- **Seat**: S55scribe01 (scribe)
- **Wave**: round-55 / w1 (12 seats; the canonical planner seat is held by the L1, SoujiR55)
- **Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin` — **read-only to this seat**; no lane
  tracked file was written, modified or committed by this seat. The only writes were to this
  seat directory and to the seat scratch.
- **Freeze commit**: `e8f338674dea386c186aa7657ef2142cbb4b6d48`; base
  `f056aaa031bb65de27e7fa5daa38b0d4a443aedc`
- **Lane tip at the time of this seat's measurement**: `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`
- **Scratch**: `/fast/scratch/hyaku/souji-r55/S55scribe01/` — **deleted before yield**
  (receipts copied into the seat directory first)
- **Verdict**: **PASS** on the source and the quotes. The source was opened live today; all
  four located quotes are verbatim substrings of the tag-stripped capture with matching word
  counts; the page heading is present; the committed capture is byte-equal to the live fetch.
  **One landing finding was raised** (the S277 `used-by` cell must gain the new entry, per
  `corpus/QUALITY.md` Q62), reported in §6 with a reproduction receipt, **accepted by the L1
  and closed** — the closure is verified in §6.2 with the lane's own instrument
  (`tools/souji-registry-agreement.py`) at the landing commit `913fa479`. Nothing was landed
  by this seat (the L1 integrates).

---

## 1. Frozen pin verification (all six pins match — no stop-and-report)

`sha256sum` run from the lane root, before any probing:

| pinned file | expected sha256 | measured | match |
|---|---|---|---|
| `census/round-55/c1-counter.py` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | same | **yes** |
| `census/round-55/c2-counter.py` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | same | **yes** |
| `census/round-55/fixtures/build-fixtures.py` | `e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62` | same | **yes** |
| `census/round-55/fixtures/run-matrix.sh` | `ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315` | same | **yes** |
| `census/round-55/records/c1-selftest-expected.tsv` | `ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` | same | **yes** |
| `census/round-55/records/c2-selftest-expected.tsv` | `63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` | same | **yes** |

The frozen preregistration (`census/round-55/preregistration.txt`) was read first, as
instructed. Its C1/C2 targets, populations, controls and kill rules were not re-litigated by
this seat — this seat's scope is the S278 source re-verification and the Gate draft.

## 2. Live re-open of the S278 source — PASS

Command (run in the seat scratch; absolute paths elsewhere):

```
$ curl -sSL -o s278.html -w '%{http_code} %{url_effective}\n' \
    'https://docs.python.org/3.12/library/stdtypes.html#str.splitlines'
200 https://docs.python.org/3.12/library/stdtypes.html#str.splitlines
```

| fact | value |
|---|---|
| HTTP code | `200` |
| url_effective | `https://docs.python.org/3.12/library/stdtypes.html#str.splitlines` (no redirect) |
| redirects followed | `0` (measured separately with `%{num_redirects}` on both the follow and the no-follow request) |
| bytes | `648964` |
| sha256 | `0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352` |
| expected sha256 (seat spec) | `0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352` — **match** |
| access date | 2026-11-03 |

Byte-equality against the committed capture:

```
$ cmp s278.html /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-55/sources/s278-python-stdtypes.html
(no output; cmp exit 0)
```

The committed capture at HEAD (`3ce0ba03…`) also hashes to
`0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352`, and the committed
located-quote file at HEAD hashes to
`a4d9eb96998f46ca8072702e55e4bb431489c189df0b5564066668fdb1b55222` — the seat's re-read of
the working-tree file is the same bytes, so the seat verified the *committed* artifact, not a
locally edited copy.

Receipt: `receipts/quote-substring-check.txt` (the fetch, the digests, the cmp result and the
quote checks in one file).

## 3. The four located quotes — all verified

Recipe as recorded in the file header and inherited from the r53 S276 / r54 S277 lineage:
**strip `script`/`style`, strip tags, `html.unescape`, collapse whitespace runs.**

Every quote line of `census/round-55/sources/s278-located-quote.txt` was parsed and re-checked
against the live fetch (not against the committed capture — the two are byte-equal, but the
live bytes are what was checked):

| # | recorded `substring` | recorded words | measured `substring` | measured words | match |
|---|---|---|---|---|---|
| 1 | True | 18 | **True** | **18** | yes |
| 2 | True | 15 | **True** | **15** | yes |
| 3 | True | 25 | **True** | **25** | yes |
| 4 | True | 13 | **True** | **13** | yes |

The two remaining lines of the file are the two `#` header lines (the recipe header and the
page/heading header) — they carry no `substring=`/`words=` fields and are not quote rows.
All four quotes are ≤25 words, as the source contract requires.

Quote texts and their section location (the nearest preceding signature in the tag-stripped
text is `str.splitlines(keepends=False)¶ Return a list of the lines in the string, …` for all
four, so all four sit inside the `str.splitlines(keepends=False)` section):

1. **18 words** — "This method splits on the following line boundaries. In particular, the
   boundaries are a superset of universal newlines"
2. **15 words** — "Line breaks are not included in the resulting list unless keepends is given
   and true."
3. **25 words** — "\v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d
   Group Separator \x1e Record Separator \x85 Next Line (C1 Control Code)"
4. **13 words** — "Changed in version 3.2: \v and \f added to list of line boundaries"

### Page heading

`'Python 3.12.' present in tag-stripped text:` **True**; the full heading found is
**`Python 3.12.16 documentation`** (the raw `<title>` reads
`Built-in Types — Python 3.12.16 documentation`). The located-quote file's header line records
the same heading string, so file and capture agree.

Receipt: `receipts/quote-substring-check.txt`.

## 4. The mechanism the Gate's scope sentence rests on — re-measured from the frozen bytes

The Gate scope is "the line-boundary superset that makes `splitlines()`-based line numbering
diverge from LF-only numbering". This seat re-measured the divergence **from the frozen
counter bytes**, not from prose:

| counter | sha256 | `hidden_lines()` numbering expression |
|---|---|---|
| `census/round-54/c1-counter.py` (v3) | `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e` | `text.splitlines()` |
| `census/round-55/c1-counter.py` (v4) | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | `text.split('\n')` |

The language-level divergence on the exact shape the r54 sentinel S1 defect used:

```
fixture text repr: 'A\x0cB\x0c~~~fence\ncorrection\n'
splitlines() -> 4 lines: ['A', 'B', '~~~fence', 'correction']
split('\n')  -> 3 lines: ['A\x0cB\x0c~~~fence', 'correction', '']
diverges: True
```

So the v3 counter numbered its hidden-line set with a breaker that also splits on `\x0c`
(form feed) while its own correction line number counted only `\n` — the r54 HIGH. The v4
counter uses one breaker everywhere. This is exactly what the S278 quote grounds: the docs
state the boundary set that `splitlines()` uses, which is a strict superset of universal
newlines and therefore wider than the LF-only model.

The v4 counter's `splitlines()` calls that survive are on **git numstat output** and on the
**expected-TSV reader**, not on any filing text — so the one line model holds for the filing
surface. (Read from the frozen bytes; no counter was executed by this seat.)

Receipt: `receipts/quote-substring-check.txt` (probe section) and the seat scratch probe
`probe_line_model.py`.

## 5. Drafted fragments (all inside this seat directory; the L1 integrates)

| path | what it is |
|---|---|
| `draft/gate-block-s278.md` | the round-55 lesson `## Gate` block for S278 — URL, access date 2026-11-03, the four quotes with their section location and word counts, tier A docs, the scope sentence, status `mined`, used-by `corpus/knowledge/splitlines-line-model.md`, plus the independent re-check and the frozen-bytes mechanism re-measurement |
| `draft/search-log-line.md` | the `corpus/SOURCES.md` `## Search log` line — question, where, date, identified/screened/included/excluded counts (1/1/1/**0**), the stop condition, and the counts spelled out (one page fetched, zero rejected) |
| `draft/used-by-old-to-new.md` | the used-by old→new line for **S277**, with the Q62 reason, the exact old and new cell values, the house-shaped `## Gate` bullet, and the two pre-existing (not-this-round) K1 disagreements |
| `receipts/quote-substring-check.txt` | the fetch/digest/cmp receipt, the four quote checks with recorded-vs-measured values, the heading check, and the section-location measurement |
| `receipts/k1-bidirectional-receipt.txt` | the K1 bidirectional-citation replay: baseline at HEAD vs working tree, the delta, and the S277 `used-by` cell in both states |

## 6. Finding — the S277 `used-by` cell must gain the new entry before landing (Q62)

**This is the one thing that blocks a clean landing of the S278 work.** It is a named limit /
finding with a reproduction receipt, not an edit of frozen bytes — this seat changed nothing.

`corpus/knowledge/splitlines-line-model.md` (the new r55 entry, still untracked in the working
tree) cites **S277** in its front-matter `source:` line:

```
source: S278 — Python 3.12 library reference, str.splitlines (…). Consumer of the fence
grammar admitted in S277 (corpus/knowledge/correction-filing-fence-grammar.md), which it
extends to one line model.
```

`corpus/QUALITY.md` **Q62** makes the citation bidirectional: *every S-id an entry's
front-matter `source:` lines cite must be a row that lists that entry in `used-by`*. The
instrument is `tools/souji-registry-agreement.py` (arm K1). S277's `used-by` cell in the
current `corpus/SOURCES.md` lists only the r54 entry, so at the landing revision K1 prints:

```
K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md
```

Measured by replaying the tool's own K1 logic read-only (the tool itself reads committed revs
only, and the new entry is not yet committed, so the tool could not be pointed at it). The
delta is exactly one line:

```
== BASELINE at HEAD (no S278 row, no new entry) ==
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md
(disagreements: 2)

== WORKING TREE (S278 row drafted + new entry present) ==
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md
K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md
(disagreements: 3)

== delta introduced by the r55 S278 work ==
NEW: K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md
```

**Required landing change** (drafted in `draft/used-by-old-to-new.md`):

- old: S277 `used-by` = `corpus/knowledge/correction-filing-fence-grammar.md`
- new: S277 `used-by` = `corpus/knowledge/correction-filing-fence-grammar.md,
  corpus/knowledge/splitlines-line-model.md`

**House precedent confirmed**: the r54 landing did exactly this for S276 — commit
`0fada8b3` ("…+ registry row S277 and S276 used-by old→new + search-log note"). The S276
`used-by` cell at the r54 *freeze* commit `3c394cab` and at the r54 landing commit
`bfdbb336` was still the one-path value; the two-path value landed with the row+entry commit
`0fada8b3`. So the change belongs in the same commit that lands the S278 row and the new
entry — which is where this round's L1 is landing them.

### 6.1 Re-verified against the L1's landed lesson — the lesson's text is wrong on this point

While this seat was finishing, the L1 landed `corpus/lessons/round-55.md` and the S278
registry row. **The seat re-ran the K1 replay against that updated tree; the result is
unchanged** — the S277 disagreement is still the one NEW line, and the two pre-existing
disagreements are still the only others (receipt `receipts/k1-bidirectional-receipt.txt`,
final section).

The L1's landed lesson says, at `corpus/lessons/round-55.md:38-40`:

> - Reuse: **S277** (CommonMark 0.31.2 §4.5/§4.6) and **S276** (gitignore PATTERN FORMAT)
>   are cited by the r54 knowledge entries and unchanged this round. **No status, recheck or
>   used-by cell of an existing row changed.** The S278 row's used-by is
>   `corpus/knowledge/splitlines-line-model.md`.

**That sentence is not correct as written, and this seat's finding is the disagreement.**
Q62's rule is triggered by the *new entry's* `source:` line, which cites S277 — so S277's
`used-by` cell **must** change, whether or not the lesson says the rows were "unchanged".
The lesson's own S278 bullet already records that the S278 row's `used-by` is
`corpus/knowledge/splitlines-line-model.md`; the S277 row needs the reciprocal cell, and the
K1 arm of `tools/souji-registry-agreement.py` will print the disagreement line above at the
landing revision if it does not.

**The L1's action** (this seat does not make it — the row is the L1's to change):

- S277 `used-by`: `corpus/knowledge/correction-filing-fence-grammar.md` →
  `corpus/knowledge/correction-filing-fence-grammar.md, corpus/knowledge/splitlines-line-model.md`
- and the lesson's `## Gate` reuse bullet must be rewritten to log the old→new change, as the
  r54 lesson did for S276 (the exact bullet is drafted in `draft/used-by-old-to-new.md`).

Two ways this could be closed instead, if the L1 prefers one of them — **either is a lane
decision, not this seat's**:

- (a) make the cell change above and log it (the r54 precedent, and what Q62 asks for); or
- (b) drop the S277 citation from the new entry's `source:` line (it is a *consumer*
  relationship, and the entry already names S277 in its prose and in its "does not establish"
  section, so the S277 fence-grammar citation would still be legible) — but then the new
  entry's `source:` line names only S278, and Q62's K1 arm goes quiet.

This seat does not pick between them: the L1 owns the landing. What this seat asserts, with
a receipt, is that **the current state prints the K1 disagreement, and the current lesson
text denies that any used-by cell changed.**

### 6.2 L1 disposition — accepted; closure verified with the lane's own instrument

The L1 (seat SoujiR55) acknowledged the finding by message: *"K1 is correct and my Gate reuse
bullet was wrong. Taking option (a): S277 used-by gains
`corpus/knowledge/splitlines-line-model.md`, logged old→new in the lesson; S278 recheck set to
`on-release` to match its sibling python-docs rows. Applying now."*

The finding was **accepted, not disputed**. The L1's landing commit is `913fa479`. Measured
after that commit, with **the lane's own instrument**
(`tools/souji-registry-agreement.py`, not this seat's replay):

```
$ python3 -B tools/souji-registry-agreement.py --root . \
    --rev 913fa4791115eb9e4f69dd729588ca84756d0828 \
    --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md
SUMMARY k1=2 k2=0 mismatches=2 rev=913fa4791115eb9e4f69dd729588ca84756d0828
RC=1
```

**The S277 disagreement is gone.** The count is back to the 2 pre-existing disagreements that
are present at every earlier rev measured (`3ce0ba03`, the r55 freeze `e8f33867` — both
`k1=2 k2=0 mismatches=2`). Receipt: `receipts/k1-closure-receipt.txt`.

**The closure the L1 actually applied is option (b), not option (a)** — the committed bytes
show the entry's front-matter `source:` line now cites **only S278**, with the S277 link kept
as prose ("The fence grammar this entry extends is
`corpus/knowledge/correction-filing-fence-grammar.md`"), and **S277's `used-by` cell is
unchanged**. The entry's body still names S277 in its "What this entry does not establish"
section, so the fence-grammar link stays legible and traceable. This is the second of the two
closures this seat offered; both are valid under Q62, and the outcome — the K1 arm going
quiet — is the same. This seat records the difference between the L1's stated option and the
committed bytes as a factual note, not a dispute: **the finding is closed.**

The §7 item 3 `recheck` observation is closed too: the S278 row's `recheck` cell is
`on-release` at HEAD, matching its sibling python-docs rows S272–S274 and S277.

With the citation dropped, the L1's lesson sentence ("No status, recheck or used-by cell of
an existing row changed") is now **accurate**: no existing row's cell changed. The seat's
§6.1 objection was to the state at the time of that landing attempt, and it is resolved.

**One residual, for the L1's awareness (not a defect in the landed bytes):** the round-55
preregistration is silent on which of the two closures applies, so the landed state is
self-consistent under Q62. But the r54 lesson's house pattern for this situation (the S276
reuse bullet, `corpus/lessons/round-54.md`) *logs the used-by old→new change explicitly*; the
r55 lesson's reuse bullet names S277 and S276 as "cited by the r54 knowledge entries and
unchanged this round", which is true under the applied closure. No discrepancy remains.

**The other two K1 disagreements are pre-existing lane state**, present at HEAD
`3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f` before any r55 S278 work. This round touches
neither row nor entry; they are named here only so the L1 does not attribute them to the
S278 work. Routing them is the L1's call and is outside this seat's scope.

## 7. Other observations for the L1 (not findings against the frozen bytes)

1. **The S278 registry row and the new knowledge entry are landed** (L1 commit `913fa479`).
   At the earlier HEAD `3ce0ba03` the registry had no `S278` row; the L1 landed the row, the
   entry `corpus/knowledge/splitlines-line-model.md`, and `corpus/lessons/round-55.md`. This
   seat did not write any of them.
2. **Row shape is census-clean.** The S278 row has `awk -F'|' NF` = 13 (11 columns, the
   contract's shape). The full `census/round-12/sources-census.sh` check set run over the
   tree prints: rows `202`; malformed rows `0`; **no** enum or tier-inflation violations;
   **no** mined row with a missing `used-by` path; **no** duplicate ids. The row's
   `kind=docs`, `tier=A`, `status=mined` are all inside the census enums.
3. **`recheck` — closed by the L1.** The row was drafted `recheck=180d`; the sibling
   Python-docs rows S272–S274 and S277 carry `on-release`. The L1 set it to `on-release` at
   commit `913fa479`, which is what this seat's §7 observation asked for. `180d` remains an
   in-use enum value (11 other rows carry it, including S276), so the draft was not a contract
   breach — a consistency point, now settled.
4. **Scope wording — noted, not a defect.** The landed S278 row's `scope` cell reads "the
   line-boundary set that the frozen C1 v4 counter's hidden-line numbering must agree with
   (the r54 sentinel S1 mechanism)". This seat's assignment wording for the scope was "the
   line-boundary superset that makes splitlines()-based line numbering diverge from LF-only
   numbering". The landed Gate bullet in `corpus/lessons/round-55.md` reads "scope: the
   line-boundary set" — consistent with the row. The seat's drafted Gate fragment carries the
   assignment wording and flags the difference inline; the **landed** wording is the L1's
   choice and is internally consistent. No action required.
5. **Registry count.** The registry reads `202` rows (201 at the r55 freeze plus S278). The
   preregistration's "the current registry at base is 201 rows" is consistent.
6. **The new entry's provenance trio is present** (`source:`, `verified-at:`, `recheck:` — the
   r54 house shape). Its `recheck:` line names the real-lane v4 recompute command and the
   "re-check the S278 quotes against a fresh fetch" step — which this seat's §3 satisfies.
7. **`corpus/lessons/round-55.md` was landed by the L1 while this seat was measuring.** The
   seat re-read the landed lesson: its `## Gate` carries an S278 bullet with the URL, access
   date, the fetch result, the digest, the capture path, the four quotes with their word
   counts, the scope, the tier and the used-by. **Every verifiable fact in that bullet agrees
   with this seat's independent measurement** — the URL, the access date, the HTTP 200, "no
   redirect", 648964 bytes, the sha256, the capture path, the quote file path, the recipe
   description, "all `substring=True`", and the four word counts 18/15/25/13. The seat's
   independently drafted Gate fragment is therefore **redundant with the landed text**; it is
   kept in the seat directory as the re-verification record (measured word counts, section
   locations, the byte-equality receipt, the frozen-bytes mechanism measurement) and was
   **not** applied over the L1's text. This seat wrote none of these files.

### 7.1 Two landing gaps still open at commit `913fa479` (for the L1)

Both were checked against the **committed** bytes at `913fa479`, not the working tree:

1. **The `## Search log` entry for r55 is not in `corpus/SOURCES.md`.**
   `git show HEAD:corpus/SOURCES.md | grep -c "Round-55 bounded source search"` → **0**. The
   search-log section's most recent entries are "Round-54 bounded source search", "Round-41",
   "Round-40". The r54 round — the immediately preceding round to open a source — landed its
   search-log line there (as `census/lessons/round-54.md` also records: *"Search log: one
   bounded search … recorded in `corpus/SOURCES.md` `## Search log` with
   identified/screened/included/excluded counts"*). The landed r55 **lesson** has the search-log
   bullet (`corpus/lessons/round-55.md:41`: "Search log: one bounded fetch … identified 1,
   screened 1, included 1, excluded 0"), so the counts are stated in the lesson but the
   `corpus/SOURCES.md` entry the contract points at is missing.
   **The drafted line is ready to integrate**: `draft/search-log-line.md` — question, where,
   date, identified 1 / screened 1 / included 1 (S278) / excluded 0, the stop condition, one
   page fetched and zero rejected. This is exactly the fragment this seat was asked to draft.
2. **No `corpus/README.md` frontier note for round 55.**
   `git show HEAD:corpus/README.md | grep -c "splitlines-line-model"` → **0**, and the
   frontier sections stop at "## Round 54 frontier update" (the r54 precedent landed one, and
   it named the new entry, its source id and the registry count). The r55 frontier note is
   still owed.
3. **No "Round-55 provenance" paragraph in `corpus/SOURCES.md`.** The provenance paragraphs
   run Round-13 … Round-51 (Round-52/53/54 did not add one, so this is not a strict house
   rule — **noted for the L1's awareness only**, not a finding).

Neither gap is a defect in the frozen bytes, and neither is this seat's to close — the corpus
files are the L1's to write. This seat is a leaf and wrote no corpus file.

## 8. Honesty statement

- The source was opened live by this seat on 2026-11-03; the fetch, byte count, digest, the
  redirect count and the byte-equality against the committed capture are recorded above and
  in `receipts/quote-substring-check.txt`.
- All four quotes were re-verified with a runnable script against the **live** bytes; the
  recorded `substring`/`words` values and the measured ones are printed side by side in the
  receipt. The seat's own check and the committed file agree.
- The page heading `Python 3.12.` was confirmed present, with the full heading string
  `Python 3.12.16 documentation`.
- **No counter was executed and no acceptance claim is made.** The counters' verdicts at the
  measured revision are the L1's. The §4 divergence is a read of the frozen bytes plus a
  language-level probe, not a counter run.
- The §6 finding was **measured**, not inferred: the K1 replay shows the disagreement is
  absent at HEAD and present in the working tree, and the house precedent commit is named.
- No finding was invented. The two pre-existing K1 disagreements are named as pre-existing,
  not attributed to this round.
- **No tool was installed or upgraded by this seat** — no install to record. The seat used
  only the pre-installed `curl`, `python3`, `sha256sum` and `cmp`.
- Nothing outside this seat directory and the seat scratch was written. No git or jj mutating
  command was run anywhere; the only git calls were read-only (`show`, `log`, `status`,
  `diff`, `ls-tree`, `cat-file`) with `GIT_OPTIONAL_LOCKS` unset but no write intent. The
  scratch tree was deleted before this report was written.
- The §6 finding was sent to the L1 (seat SoujiR55) by message, because it contradicts a
  sentence in the lesson the L1 landed while this seat was measuring. The finding is stated
  as a finding with its receipt and two possible closures; the choice of closure is the L1's.
  A second message reported the two residual landing gaps of §7.1. **Both messages went to
  the L1 only** — no broadcast, no other peer was messaged, and no subagent was dispatched
  (this seat is a leaf).
- The `M SCORECARD.md` entry visible in `git status` at the end of this seat's work is the
  L1's concurrent edit, not this seat's. This seat's only writes in the lane tree are
  `.ufo/waves/round-55/w1/S55scribe01/` and `.ufo/waves/round-55/w1/S55scribe01.md`.

## 9. Limits of this seat's work

- The L1 verifies the four quotes and the Gate fragment against the capture before landing
  them; the capture and the located-quote file are committed at HEAD already, and the seat's
  re-fetch is byte-equal to them.
- The §6 finding is **closed**: accepted by the L1 and verified gone at the landing commit
  `913fa479` with the lane's own instrument (`receipts/k1-closure-receipt.txt`). This seat
  changed nothing; the closure was the L1's.
- The two gaps of §7.1 are **open and are the L1's to close** — the `corpus/SOURCES.md`
  `## Search log` line (drafted and ready: `draft/search-log-line.md`) and the
  `corpus/README.md` round-55 frontier note. This seat is a leaf and wrote no corpus file.
- The Gate draft carries the L1's measurement placeholders for the round's claim evidence,
  wave findings, standing checks and registry counts — this seat did not fill them, because
  those measurements are the L1's and the wave's.
- The `recheck=` observation of §7 item 3 is **closed** by the L1 (`180d` → `on-release`); the
  `scope=` wording of §7 item 4 is the L1's landed wording and is internally consistent.
