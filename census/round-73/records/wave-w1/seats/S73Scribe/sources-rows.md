# S73Scribe — r73 SOURCES rows S315, S316 (draft; L1 integrates)

Shape copied from `corpus/SOURCES.md` rows S312–S314 (11 columns, NF=13). Quotes located in
`census/round-73/srcs/*.txt`, offsets are character offsets in the decoded capture (the convention
S312/S313 use: `git-check-attr.txt` "Consider .gitattributes in the index only…" is at 2608,
`gitattributes.txt` "a long running process filter…" at 16953). No `|` inside any cell.

## Rows (insert after S314)

| S315 | git technical documentation racy-git.adoc at tag v2.56.0, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/technical/racy-git.adoc (sha256 f661ed2d4751096257be24fdf7f9c91e6eb00493e413116189ef166496eb84ad, fetched 2026-11-06, HTTP 200, 9121 bytes; re-fetched 2026-11-06 byte-identical; capture census/round-73/srcs/racy-git.adoc) | docs | A | how git decides a tracked file is unmodified from the index's cached stat information without reading its contents (scope: the stat shortcut and the page's own statement that it can be wrong; the racy-timestamp remedy is not used as ground) | Background, cached stat information; quote at offset 1435 of census/round-73/srcs/racy-git.txt (whitespace-normalized): "If some of these "cached stat information" fields do not match, Git can tell that the files are modified without even looking at their contents."; Racy Git, quote at offset 3539: "Git can incorrectly think files in the working tree are unmodified even though they actually are." | the index caches lstat(2) fields and git skips the content read when they match, so a rewritten stat entry can make changed worktree bytes read clean (measured: r73 rows FX1-FX3, census/round-73/probes/fx-index-stat.txt) | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |
| S316 | git-hash-object(1) DESCRIPTION, https://git-scm.com/docs/git-hash-object (sha256 b7e8f95355c38df94c9355d31b0ed985d5c22cb5ca7c4d640364c801100eb798, fetched 2026-11-06, HTTP 200, 29933 bytes; re-fetched 2026-11-06 byte-identical; page "git-hash-object last updated in 2.43.0", "2.43.1 → 2.56.0 no changes"; capture census/round-73/srcs/git-hash-object.html) | docs | A | what object id `git hash-object` reports for a named file (scope: the DESCRIPTION sentence and the OPTIONS `--path` filter sentence; object writing, `--literally` and `--stdin-paths` not claimed) | DESCRIPTION; quote at offset 2258 of census/round-73/srcs/git-hash-object.txt (tag-stripped, whitespace-normalized): "Computes the object ID value for an object with specified type with the contents of the named file"; OPTIONS, --path, quote at offset 3056: "the path is used to determine which Git filters should be applied to the object" | the id is computed from the named file's contents and the page says the path decides which filters apply, so raw worktree bytes and the index id are not the same question (measured: r73 FXc, census/round-73/probes/fx-honest.txt raw_equal=false) | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |

## Locator evidence (re-derived this seat)

- racy-git.txt char offsets: quote 1 at 1435 (25 words), quote 2 at 3539 (16 words). The 26-word
  sentence at 3374 ("the cached stat information the index entry records still exactly match …")
  is NOT used: over the 25-word cap.
- git-hash-object.txt char offsets: DESCRIPTION quote at 2258 (18 words), `--path` filter sentence
  at 3056 (15 words). Page banner "git-hash-object last updated in 2.43.0" at 1559,
  "2.43.1 → 2.56.0 no changes" at 1636.
- Both captures re-fetched 2026-11-06 by this seat: racy-git.adoc HTTP 200, 9121 bytes,
  sha256 f661ed2d…b84ad (identical); git-hash-object page HTTP 200, 29933 bytes,
  sha256 b7e8f953…eb798 (identical).
- `racy-git.adoc` is the raw asciidoc at tag v2.56.0 (first line "Use of index and Racy Git
  problem"); `racy-git.txt` is the whitespace-normalized text capture (headings flattened, line
  breaks collapsed), so the offsets above are valid for the `.txt` only.

## Note for the L1

The lane working tree already carries an uncommitted S315/S316 pair (mtime 19:15:51, not written by
this seat) whose S316 anchors OPTIONS `--no-filters` at offset 3431 and whose S315 anchors only the
3539 sentence. Both pairs cannot land (E03 duplicate id). This draft follows the seat spec
(S316 = DESCRIPTION). The `source:` header line must name whichever S316 scope lands.
