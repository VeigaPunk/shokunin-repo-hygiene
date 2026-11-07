# S320 draft row for corpus/SOURCES.md (round-76, scribe S76Scribe)

Insert immediately after the S319 row (currently `corpus/SOURCES.md:278`), inside `## Registry`.
11 columns, no `|` inside any cell, quote 18 words located at offset 2355 of the whitespace-normalized
capture (0-based, same convention as S318's offset 3807 — re-derived this round).

| S320 | git-check-ignore(1) at tag v2.56.0, OUTPUT, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc (sha256 940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208, fetched 2026-11-06, HTTP 200, 4159 bytes; capture census/round-76/srcs/git-check-ignore.adoc) | docs | A | which exclude source decided an ignore match as git reports it (scope: the --verbose and -z record fields and the form of the source field; pattern syntax and exit status not used) | OUTPUT, --verbose; quote at offset 2355 of the whitespace-normalized census/round-76/srcs/git-check-ignore.adoc (lines 81-82): "<source> is the pattern's source file, and <linenum> is the line number of the pattern within that source." | `--verbose` names the matching pattern, its source file and its line number, and the source field is an absolute path for `core.excludesFile` but repository-relative for `.git/info/exclude` or a per-directory exclude file (same page, OUTPUT), so a gate can attribute each ignored untracked path to a tracked versus an untracked `.gitignore` (r76 rows f7/f9/f10/f14, census/round-76/records/c1-after.txt) | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |

## Verification performed (all numbers re-derived, not copied)

- capture bytes: `sha256sum census/round-76/srcs/git-check-ignore.adoc` = 940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208; `wc -c` = 4159; 129 lines.
- live re-fetch of the cited URL (`curl -sS -o s320-fetch.adoc -w 'HTTP=%{http_code} size=%{size_download}'`,
  2026-11-06): `HTTP=200 size=4159`; sha256 940177c7…; `cmp` against the committed capture: identical.
- quote located: `<source> is the pattern's source file, and <linenum> is the line number of the pattern within that source.` at offset 2355 of the whitespace-normalized capture, 18 words, lines 81-82. The adjacent sentence at offset 2555 (`<source> will be an absolute path when referring to the file configured by core.excludesFile …`) is the absolute/relative split cited in the teaches cell as a paraphrase, not as quote bytes.
- neighbouring row shape copied from `corpus/SOURCES.md:277` (S318) and `:278` (S319).
