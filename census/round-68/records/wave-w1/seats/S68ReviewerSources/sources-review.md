# sources-review.md — S68ReviewerSources (souji r68, wave 1)

Attack target: round-68 replace-ref source claim. Fresh fetches 2026-11-05, read-only.

## Fetch provenance (pinned artifacts in /fast/scratch/hyaku/souji-r68/S68ReviewerSources/)
- `curl -fsS -H 'Cache-Control: no-cache' -D git-replace.headers -o git-replace.html https://git-scm.com/docs/git-replace`
  - sha256 `70ca75f4baa4bcbb2f5ebdb9fe510036ce54c653ccb044424521f26fbfeedec0`, 38351 bytes
  - headers: `date: Thu, 05 Nov 2026 17:58:02 GMT`, `last-modified: Thu, 05 Nov 2026 04:35:24 GMT`, `cf-cache-status: HIT`, `age: 506`
- `curl -fsS -H 'Cache-Control: no-cache' -D git.headers -o git.html https://git-scm.com/docs/git`
  - sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`, 244227 bytes
  - headers: `date: Thu, 05 Nov 2026 17:58:02 GMT`, `last-modified: Thu, 05 Nov 2026 04:35:25 GMT`, `cf-cache-status: HIT`, `age: 8512`
- Method note: byte offsets below are raw byte offsets into the pinned fetched bytes (first byte of the quote's first character); line numbers counted by `\n`. Matching tried exact-bytes first, then whitespace-collapsed, then tag-stripped + whitespace-collapsed (offset mapped back to raw bytes via a position-preserving map).

## Point 1 — quotes in git-replace(1) and the git(1) entry
- (a) `Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck).`
  - PRESENT. Method: whitespace-normalized match (NOT exact: the raw HTML contains one internal newline, `...by all Git commands\nexcept those...`; no tags inside the sentence).
  - First char `R` at raw byte offset **28209** (line 1680) of git-replace.html; exactly 1 occurrence (raw-text count of "Replacement references" in the file is 1).
- (b) `The GIT_NO_REPLACE_OBJECTS environment variable can be set to achieve the same effect as the --no-replace-objects option.`
  - PRESENT. Method: tag-stripped + whitespace-normalized match (NOT exact: raw is `The <span class='synopsis'><code>GIT_NO_REPLACE_OBJECTS</code> environment variable ... the <code>--no-replace-objects</code> option.`).
  - First char `T` at raw byte offset **29118** (line 1708) of git-replace.html; exactly 1 normalized occurrence (end of the DESCRIPTION, immediately before `OPTIONS`).
- git(1) literal `GIT_NO_REPLACE_OBJECTS` entry: PRESENT in git.html at raw byte offset **220857** (line 5777), as an environment-variable `<dt>`/`<dd>` entry. First sentence, verbatim: `Setting and exporting this environment variable tells Git to ignore replacement refs and do not replace Git objects.`
  - (The other `GIT_NO_REPLACE_OBJECTS` occurrence in git.html is the `--no-replace-objects` option description at raw byte offset 101967 (line 4045) — "This is equivalent to exporting the GIT_NO_REPLACE_OBJECTS environment variable with any value." — not the env-var entry.)

## Point 2 — git-replace version header vs fetched page
Claim under review: header shows 2.56.0 "no changes", last updated 2.55.0.
- Fetched page: `<span class="light d-flex">git-replace last updated in 2.55.0</span>` at raw byte offset 17430 (line 1328); dropdown list top entry `<li class="no-change"><span>2.56.0 no changes</span></li>` at raw byte offset 17699 (line 1334).
- VERDICT: PASS — no difference. The fetched page states exactly "2.56.0 no changes" as the newest entry and "git-replace last updated in 2.55.0".

## Point 3 — S68Scribe registry-row-S301.md schema check
- Draft exists (first seen 15:01, single line). Checks (char-wise, split on `|`): 13 segments → exactly **11 cells** between the boundary pipes; **`|` count inside every cell = 0**; single-line row (1 trailing newline).
- Anchor (cell 2): `git-replace(1) — https://git-scm.com/docs/git-replace` — names the page (title + URL).
- Version: named in cell 6 — "served page is the git-replace 2.56.0 manual, whose header reads 'git-replace last updated in 2.55.0' and whose version list reads '2.56.0 no changes'" — page AND version present.
- Provenance cross-check (beyond the three asked, supports the row): cell 6's `38351 bytes html, sha256 70ca75f4…` equals my fresh fetch byte-for-byte (full sha256 `70ca75f4baa4bcbb2f5ebdb9fe510036ce54c653ccb044424521f26fbfeedec0`). The row's "tag-stripped text 6975 bytes, sha256 96d141fd…" reproduces exactly with the lane's own frozen stripper `census/round-66/sources/recipe.py` (`bytes=6975 sha256=96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4`, byte-identical to the scout capture `S68ScoutReplace/captures/git-replace-recipe.txt`). The row's cited located-quote offsets **2896 and 3383 (byte 2953 and 3440)** verify character-for-character at those very offsets in that 96d141fd text: (a) begins at char 2896 (byte 2953, line 197), (b) begins at char 3383 (byte 3440, line 207); each exactly once in that text.
- VERDICT: **PASS** on all three schema checks (11 columns; no `|` inside cells; anchor names page and version). The row's digest/offset provenance also reproduces.

## Corroborated corpus claims (read-only, for the accuracy attack)
- Writer pin claim: at the freeze commit, `tools/souji-receipt-write.py` candidate bytes hash to `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` (`git show 8b393b19:tools/souji-receipt-write.py | sha256sum` → same digest); `env["GIT_NO_REPLACE_OBJECTS"] = "1"` sits at line 104 inside the single `git()` helper (lines 95–106, scrub of GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR at line 99); the by-name refusal of `GIT_REPLACE_REF_BASE` sits at line 325 (`RECEIPT-ENV-REDIRECT-SET`, row E6). `census/round-68/mutate-writer.py` (sha256 `23e19b8e01023018ab957314caba465b70f9db09ed8d1078c229b7928f0f5cf0`, byte-verified at the freeze commit) names K6 as exactly the line-104 pin; `census/round-68/battery/SHA256SUMS` row `battery/K6.py` = `698fedc2…` as the knowledge entry cites.
- The knowledge entry's phrase "match byte-for-byte in the recipe-stripped page text" (knowledge-replace-ref-receipt-writer.md, claim section) is accurate for the 96d141fd text — in the RAW HTML the sentences are NOT contiguous bytes (internal newline in (a); `<span class='synopsis'><code>` wraps in (b)), so the entry's wording is correctly scoped; only someone reading it as a raw-HTML claim would err. Both quotes occur exactly once in both forms.

## Verdicts
- Point 1 quote (a): PASS (whitespace-normalized in raw HTML; exact-in-recipe-text at char 2896 / byte 2953, line 197).
- Point 1 quote (b): PASS (tag-stripped + whitespace-normalized in raw HTML; exact-in-recipe-text at char 3383 / byte 3440, line 207).
- Point 1 git(1) entry: PASS (literal entry present; first sentence quoted above).
- Point 2 version header: PASS (claim matches fetched page; no difference).
- Point 3 registry row S301: PASS (11 columns; no `|` inside cells; anchor names page and version; cited offsets and digests reproduce against my fresh fetch and the lane recipe).

## Findings
- LOW: quote (a) is not an exact-byte match in the fetched HTML (internal line break); any report claiming "exact" for the raw HTML would be wrong — whitespace-normalized is the correct claim for the raw form.
- LOW: quote (b) requires tag stripping, not just whitespace normalization, in the raw HTML; reports should say "tag-stripped + whitespace-normalized" for the raw form and may say exact for the lane-recipe text.
- LOW: the git(1) page contains a second, different `GIT_NO_REPLACE_OBJECTS` sentence (inside the `--no-replace-objects` option description at raw byte 101967, line 4045 of git.html; and the option-text occurrence of git-environment.txt at byte 10850, line 485); a report that cites only "byte offset 10850/46311" without naming which occurrence could silently cite the wrong one. The r66 quotes.tsv rows correctly cite the ENVIRONMENT VARIABLES entry (occurrence 2, byte 46311, line 1413).
- No HIGH or MEDIUM findings.

## One more note for the Scribe (a missing citation, not a defect in mine)
- The knowledge entry quotes the git(1) sentence `Setting and exporting this environment variable tells Git to ignore replacement refs and do not replace Git objects.` and cites it via S298, which is correct — but the sentence is TWO quotes' worth of source (the entry-titled blockquote row `GIT_NO_REPLACE_OBJECTS` at offset 46311 where it is the block_text prefix, and the sentence row at offset 46334, both in quotes.tsv lines 12–13); citing either is fine, and both sit in the same section. No action needed.
