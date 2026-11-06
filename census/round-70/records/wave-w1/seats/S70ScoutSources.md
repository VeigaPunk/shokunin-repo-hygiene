# S70ScoutSources — round-70 sources re-opened live (S304 admit / S305 reject)

Scope: re-fetch https://git-scm.com/docs/git and /docs/gitglossary; verify S304/S305 in
corpus/SOURCES.md. Verdict is about the SOURCE rows only. No lane file was edited.
Receipts: `.ufo/waves/round-70/w1/S70ScoutSources/{fetch-receipts,offsets-receipt,rows-receipt}.txt`.

## 1. Fetch receipts (live, 2026-11-06 19:19 GMT)
`curl -sS -L -D hdr -o live-<u>.html -w 'http_code=… size_download=…' https://git-scm.com/docs/<u>`
| url | HTTP | bytes | sha256 | vs committed capture |
|---|---|---|---|---|
| git | 200 (0 redirects) | 244227 | 534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1 | IDENTICAL to census/round-70/srcs/git-manual.html |
| gitglossary | 200 (0 redirects) | 109997 | 216bc0df7f50dc17d331ea2a9873daf65a08a2afddd797f73a300cc2e15f0129 | IDENTICAL to census/round-70/srcs/gitglossary.html |
Both captures are byte-identical to the r69/S303 and r64/S296 captures (`git ls-files | xargs sha256sum`).
Page header still "git last updated in 2.56.0". AGREE with the recorded capture identity.

## 2. S304 located quote — AGREE on content, DISAGREE on the offset cell
Quote "Treat pathspecs literally (i.e. no globbing, no pathspec magic). This is equivalent to
setting the GIT_LITERAL_PATHSPECS environment variable to 1" is VERBATIM, 20 words (<=25), byte-
contiguous under whitespace normalisation, in section OPTIONS, in the dt `--literal-pathspecs` dd
(`git-manual.html` dt id `Documentation/git.txt---literal-pathspecs`).
**FINDING MEDIUM — the recorded offset 12133 does not locate the anchor it names.**
The only extraction that reproduces BOTH recorded offsets is: regex-strip tags to a space, KEEP
<script>/<style> content, html.unescape, collapse all whitespace, no strip (59452 chars). In that
text the dt term `--literal-pathspecs` is at 12014; 12133 is the token GIT_LITERAL_PATHSPECS *inside*
that dd's text ("…is equivalent to setting the GIT_LITERAL_PATHSPECS environment variable to 1"),
119 bytes late. Under either lane-committed strip recipe the numbers do not reproduce at all:
census/round-66/sources/recipe.py -> dt 11291 (quote 11311), env dt 46323; census/round-65/sources/
s297-tagstrip.py -> dt 11284 (quote 11304). Swept 1152+ recipe variants: ZERO place
`--literal-pathspecs` at 12133; the gap between the two anchors is 35032 in every variant that
yields 47046, never the recorded 34913. Wrong cell: SOURCES.md:263 anchor cell.

## 3. S305 reject reason — AGREE
The ENVIRONMENT VARIABLES dt+dd for GIT_LITERAL_PATHSPECS contains "glob" but NOT "magic"
(raw-block scan: `'magic' in blk` -> False). Its siblings do name magic (GIT_GLOB_PATHSPECS 'aka
"glob" magic', GIT_NOGLOB_PATHSPECS 'aka "literal" magic'), so scoping the reject to the
GIT_LITERAL_PATHSPECS entry is right. Minor LOW: the wording "speaks of glob patterns only"
understates it — the same entry also says "treat all pathspecs literally" and mentions literal
paths. The load-bearing claim (never names magic) holds exactly.

## 4. S304 teaches cell — three clauses checked against git(1)
SUPPORTED: "GIT_LITERAL_PATHSPECS=1 disables all pathspec magic" (OPTIONS: "Treat pathspecs
literally (i.e. no globbing, no pathspec magic). This is equivalent to setting the
GIT_LITERAL_PATHSPECS environment variable to 1"). SUPPORTED: "GLOB/NOGLOB/ICASE add glob, literal
or icase magic to every pathspec" (OPTIONS: 'Add "glob" magic to all pathspec', 'Add "literal"
magic to all pathspec', 'Add "icase" magic to all pathspec' — mapping exact).
NOT STATED BY THE PAGE (LOW): "a reader's `:(top)` becomes a literal path" — git(1) contains 0
occurrences of ':(top)' (gitglossary(7) also 0; S296 notes the spelling is composed by the reader).
It is corroborated by the r70 host probe and S296, not by the cited page — and the row's own scope
cell says "not the per-pattern magic words", so the teaches cell overstates its scope.

## 5. Registry row shape — AGREE
SOURCES.md:263 S304 = 11 columns, kind docs, tier A, status mined, used-by
corpus/knowledge/pathspec-env-scrub.md (exists at tip feb283ee, blob 48eaf5c). SOURCES.md:264 S305 =
11 columns, status rejected, used-by "—" (the convention for all 25 rejected rows).
`bash census/round-12/sources-census.sh` -> 228 rows, 0 malformed, mined=189 queued=14 rejected=25, EXIT=0.
LOW: census/round-70/srcs/gitglossary.html is a committed capture with no registry row and no
capture path cited in corpus/lessons/round-70.md Gate (it is byte-identical to
census/round-64/sources/s296-gitglossary.html).

## Commands run
curl -sS -L -D/-o/-w on both URLs; sha256sum + cmp on live vs census/round-70/srcs/; python3 tag-strip
recipe sweep (1152 variants: tag separator x script/style x comments x entity handling x whitespace
collapse x strip x pad) over census/round-70/srcs/git-manual.html; census/round-66/sources/recipe.py
and census/round-65/sources/s297-tagstrip.py applied to the r70 capture; raw dt/dd block scans;
git ls-tree at feb283ee; bash census/round-12/sources-census.sh; a fresh git 2.56.0 fixture
(mktemp -d under my scratch, `git rev-parse --show-toplevel` asserted before commit) re-running
`git ls-files -v -z ':(top)'` and `git ls-tree HEAD -- f` under each of the four variables.

## Tooling
No install, no upgrade, no pacman transaction: the task needed only python3 3.14.8, git 2.56.0,
curl and coreutils, all already present.

## Findings
- MEDIUM — SOURCES.md:263 anchor cell: recorded offset 12133 points at the GIT_LITERAL_PATHSPECS
  token inside the dd, 119 bytes past the dt `--literal-pathspecs` it names; and neither recorded
  offset (12133/47046) reproduces under either lane-committed strip recipe.
- LOW — S304 teaches cell asserts the `:(top)`-becomes-a-literal-path consequence that git(1) and
  gitglossary(7) never print, contradicting its own scope cell.
- LOW — S305 reject wording "speaks of glob patterns only" (the entry also says "literally").
- LOW — census/round-70/srcs/gitglossary.html: committed capture with no row and no Gate path.
No finding invalidates S304's admission or S305's rejection: both quotes are verbatim, correctly
sectioned, within the word limit, and the reject reason is true.
