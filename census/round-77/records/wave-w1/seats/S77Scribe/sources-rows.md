# S77Scribe — SOURCES rows S321/S322 (drafts for the L1 to integrate after S320)

Provenance check run before drafting: both URLs re-fetched live with `curl -sSL` (2026-11-06 local,
2026-11-07 UTC): HTTP 200 both; `git-dir.c` 115474 bytes sha256 53e5ed2b…20a6, `git-add.adoc` 16586 bytes
sha256 42089b80…65db; `cmp` against `census/round-77/srcs/` equal for both. Offsets below are the byte
offset of the quote in the whitespace-normalized capture; the method reproduces S320's published offset
2355 exactly.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S321 | git dir.c at tag v2.56.0, add_patterns(), https://raw.githubusercontent.com/git/git/v2.56.0/dir.c (sha256 53e5ed2b3b65409331021ec0075d9405fdd690598ba96cc5ec8077c03b6220a6, fetched 2026-11-06, HTTP 200, 115474 bytes; capture census/round-77/srcs/git-dir.c-v2.56.0) | code | A | how git opens an exclude source before any type is known (scope: add_patterns()' open call and the single fstat that sizes the read; pattern parsing, the untracked cache and attributes not used, S064 holds attributes) | add_patterns(); quote at offset 27673 of the whitespace-normalized census/round-77/srcs/git-dir.c-v2.56.0 (lines 1164-1167): "if (flags & PATTERN_NOFOLLOW) fd = open_nofollow(fname, O_RDONLY); else fd = open(fname, O_RDONLY);"; the only fstat follows at line 1169 | per-directory `.gitignore`/`.gitattributes` open with O_NOFOLLOW and `info/exclude`/`core.excludesFile` without it; add_patterns never tests the opened source for regularity (this file's two `S_ISREG` uses, :2361 and :2385, are d_type helpers), so a FIFO source blocks inside open(2) before any type is known (fifo(7), S062), and the base gate hangs on n1-n7 and n10 (census/round-77/controls/c1-K-a-do-nothing.txt: mismatches=9 hangs=8) | mined | 2026-11-06 | on-release | corpus/knowledge/filter-filemode-witness.md |
| S322 | git-add(1) at tag v2.56.0, OPTIONS --force, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-add.adoc (sha256 42089b80b378a7e9711dde024b7ec94a6863378164ea434a34c6af07632e65db, fetched 2026-11-06, HTTP 200, 16586 bytes; capture census/round-77/srcs/git-add.adoc-v2.56.0) | docs | A | whether an ignored file can be committed at its own path (scope: -f/--force on an explicitly named ignored path; submodule ignore and --sparse not used) | OPTIONS `-f`/`--force`; quote at offset 2581 of the whitespace-normalized census/round-77/srcs/git-add.adoc-v2.56.0 (line 78): "Allow adding otherwise ignored files." | an ignore rule does not stop an explicitly named ignored file from being tracked: the lane helper records named files with `jj file track --include-ignored` (scripts/hyaku/jj-lane.sh:654), while a named directory is tracked like `git add <dir>` and ignored content under it stays out; round 77 captures the four local-only pointers at the exact paths the rows cite (commit 6690cb5a; census/round-77/records/c2-after.txt) | mined | 2026-11-06 | on-release | corpus/knowledge/self-assessment-pointer-resolution.md |

Notes for integration:

- Dates: the round's other rows and the commits say 2026-11-06; the host's UTC date is already 2026-11-07
  (local 2026-11-06 23:19). I use the local date, which matches S319/S320 and the round chronology. Either
  value passes `validate` (E08 compares with `date -u +%F`).
- The live worktree already carries a draft of these two rows at `corpus/SOURCES.md:280-281` saying
  "fetched 2026-11-07" and opening the same day; their text differs from this draft only in the wording
  above and in the two corrections recorded in the report (no regularity test exists in add_patterns; the
  helper's directory caveat).
