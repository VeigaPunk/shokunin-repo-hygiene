# S72ScoutSources — re-open of census/round-72/srcs and registry rows S312/S313/S314

## 1. Fresh fetch receipts (re-derived, not trusted)
Re-fetched 2026-11-06 with curl 8.23.0 into scratch; HTTP status/bytes/sha256 recorded in
`fetch-receipts.json`; both live captures are byte-identical to the committed
`census/round-72/srcs/*.html` (and the gitattributes.html is byte-identical to the r71
`census/round-71/srcs/gitattributes.html`, so "same capture as S306" holds):

| url | HTTP | bytes | sha256 | == committed |
|---|---|---|---|---|
| https://git-scm.com/docs/git-check-attr | 200 | 34571 | 6fe0df4e…f400348d | yes (census/round-72/srcs/git-check-attr.html) |
| https://git-scm.com/docs/gitattributes | 200 | 131046 | 0a1e8015…d3a9665aee | yes (census/round-72/srcs/gitattributes.html) |

Version strings asserted in the rows are present in the live pages: "git-check-attr last updated in
2.52.0", "2.53.0 → 2.56.0 no changes"; gitattributes "last updated in 2.56.0".

## 2. The .txt normalisation is reproducible (offsets re-derived from committed bytes)
`gitattributes.txt` (r72) is reproduced **byte-for-byte** by: drop <script>/<style> blocks →
strip remaining tags → html.unescape → collapse whitespace → strip().  `git-check-attr.txt` likewise.
(The r71 `gitattributes.txt` follows a *different* recipe — it keeps script text — so the same
sentence has different offsets there; S313/S314 cite the r72 file explicitly, so they are unaffected.)
Word counts and offsets, character offsets into the cited .txt (byte offsets differ: 2679/20599/5210):

| row | cited offset | actual | exact at offset | unique | words |
|---|---|---|---|---|---|
| S312 | 2608 git-check-attr.txt | 2608 | yes | 1 | 10 |
| S313 | 20533 gitattributes.txt | 20533 | yes | 1 | 25 |
| S314 | 5164 gitattributes.txt | 5164 | yes | 1 | 20 |

Sections re-derived from the html headings: S312 quote (html 27537) inside OPTIONS → `--cached`;
S313 quote (html 80513) inside EFFECTS → Checking-out and checking-in → filter → Long Running
Filter Process (h4 80314); S314 quote (html 55073) inside DESCRIPTION (51143–56747).

## 3. Row shape / contract census (whole table, committed corpus/SOURCES.md @2ec8b63d)
malformed rows NF!=13: 0 · duplicate ids: none · enum/tier violations: none ·
mined rows whose used-by path is missing: none · rows 234→237 (additive only; diff candidate→after
shows only the three +lines, no pre-existing cell changed) · each of the three rows has 11
non-empty cells, kind=docs, tier=A, status=mined, opened=2026-11-06, recheck=180d (matches
S306–S311) · used-by `corpus/knowledge/filter-filemode-witness.md` exists at 2ec8b63d and does cite
S312/S313/S314 (lines 73–74), so status=mined is justified.
S312 vs S046 (same URL): S046 anchors §OUTPUT/§OPTIONS -z (record framing), S312 anchors
OPTIONS --cached — distinct scopes, no duplicate claim.

## 4. Verdict per row
* **S312 — AGREE.** Quote/offset/section/sha all re-derived; "--cached considers .gitattributes in
  the index only, ignoring the working tree" does support "an attribute read with --cached cannot
  see a worktree-only .gitattributes". Scope cell correctly disclaims status/writer reads.
* **S313 — DISAGREE (scope cell over-claims; teaches cell not carried by its quote).**
  (a) scope cell says "protocol details are the probe's, not the page's" and the Gate repeats it
  ("the pkt-line exchange is the probe's … not the page's"), but the page *does* document protocol
  detail: handshake "git-filter-client" welcome, "only version 2 is supported", capabilities
  "clean"/"smudge"/"delay", key=value list terminated by a flush packet, status=success/error/abort,
  exit-code rule, delay capability, and a full pkt-line example (html 81076/20989, 22438…).
  Wrong cell: the S313 **scope** cell (corpus/SOURCES.md:272) and Gate line corpus/lessons/round-72.md:47-48.
  (b) teaches cell asserts "configured only as `process` (no `clean` key) still filters content on
  check-in", which the cited sentence does not say. Better anchors exist in the same capture, ≤25 words:
  offset **16953** "a long running process filter is used in place of clean and/or smudge filters, then
  Git can process all blobs" (20 words) and offset **26756** "the worktree file is first converted with
  filter driver (if specified and corresponding driver defined)" (15 words).
  (c) LOW: the printed quote "filter. <driver> .process" carries tag-strip artefacts (spaces around
  `<em>`); the page renders `filter.<driver>.process`. S312's anchor cell states the normalisation,
  S313's/S314's do not.
* **S314 — DISAGREE at the committed revision (teaches cell ignores the checkout exception).**
  The quoted sentence is immediately followed by the opposite rule: "During checkout process,
  .gitattributes in the index is used and then the file in the working tree is used as a fall-back."
  (offset 5270, 22 words). So the page does NOT state a blanket "worktree first"; it states a
  general fallback direction and a checkout exception. The committed teaches cell ("the worktree
  `.gitattributes` is read first and the index copy only when the worktree file is missing") asserts
  the blanket form; the scope cell's "checkout order not claimed" hedges it, but the learner-facing
  cell is the unqualified one. Related over-reach attributed to this row: census/round-72/c1-counter.py:28
  ("status reads the worktree file, S314") and corpus/knowledge/filter-filemode-witness.md:74
  ("S314 the worktree file comes first") — the page never mentions `git status`.
  NOTE: the L1's *uncommitted* working-tree edit to corpus/SOURCES.md:273 already narrows this cell
  to "outside checkout … (the page states the reverse order for checkout) … (the page does not mention
  `git status`)". At the audited commit 2ec8b63d the narrowing is not in the tree.

## 5. Other observations
* corpus/lessons/round-72.md (the Gate that grounds S312–S314 under SOURCES-CONTRACT-v1 rule 1) is
  **untracked** at 2ec8b63d; a verifier working from committed bytes only cannot find it.
* corpus/SOURCES.md has no "Round-72 provenance" paragraph — consistent with r61–r71 (last one is
  Round-60, line 275), so this is lane-wide drift, not an r72 regression.
* No tools installed or upgraded this seat: curl 8.23.0, python3 3.14.8, git 2.56.0 (pre-existing).
