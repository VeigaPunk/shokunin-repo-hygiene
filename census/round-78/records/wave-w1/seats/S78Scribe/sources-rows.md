# S78Scribe — draft SOURCES rows S323/S324 (11 columns, Registry table shape)

Anchor verification run by this seat against the committed captures (2026-11-07):

- `census/round-78/srcs/git-config.adoc-v2.56.0` sha256 `a6e644cb…b2c9`, 21095 bytes; refetch of
  `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config.adoc` HTTP 200, 21095 bytes,
  same sha256. Heading `CONFIGURATION FILE` at line 1, `Includes` at line 85.
- `census/round-78/srcs/git-setup.c-v2.56.0` sha256 `8316b1ad…c589`, 83214 bytes; refetch of
  `https://raw.githubusercontent.com/git/git/v2.56.0/setup.c` HTTP 200, 83214 bytes, same sha256.
  `get_common_dir_noenv()` at line 321, `validate_headref()` at line 350.
- S323 quote occupies lines **99-100** (line 99 ends "as if they", line 100 carries "had been found at
  the location of the include directive."); 22 words after joining the line break, 0 `|` characters.
  The seat brief said "lines 99-101" — line 101 starts the next sentence ("variable is a relative
  path"), so 99-101 over-runs the quote by one line.
- S324 quote is lines **328-329** joined with whitespace normalization (the first line ends after
  `{`, the second is two-tab indented); 9 whitespace-separated tokens, 0 `|` characters. Lines 327-329
  quoted as one string would put `"%s/commondir"` — nested quotes — inside a table cell; the draft
  quotes 328-329 and names line 327 in the teaches cell instead.

Rows to append to the `## Registry` table. Chronology note: while this seat was drafting, the L1 landed
`bbd199da` ("round-78: I — integration part 1") with its own S323/S324 rows, so these drafts are a
comparison, not a first filing. Differences from the landed rows: the landed used-by cell names only
`corpus/knowledge/git-discovery-sources.md` while Q140 (same commit) cites S323/S324 — this draft adds
`corpus/QUALITY.md`; and the landed S324 anchor quotes lines 327-329 with nested `"%s/commondir"` quotes,
while this draft quotes 328-329 only and names line 327 in the teaches cell. The landed S323 anchor
(lines 99-100) agrees with this draft and with the bytes.

| S323 | git config documentation at tag v2.56.0, CONFIGURATION FILE / Includes, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config.adoc (sha256 a6e644cb2495df1f5e25f584e2cb7c06ec673e8b90acc52ae061a0fb6d42b2c9, fetched 2026-11-07, HTTP 200, 21095 bytes; capture census/round-78/srcs/git-config.adoc-v2.56.0) | docs | A | which further files git reads while it reads a config file (scope: include.path and includeIf.*.path, the relative-path base and tilde expansion; the conditional-include grammar not used) | Includes, lines 99-100 of census/round-78/srcs/git-config.adoc-v2.56.0 (whitespace-normalized, line break joined): "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." | a config file's `include.path` or `includeIf.*.path` names a further file git opens while reading that config, so every file an include names is a discovery source of every git command that reads that config: a relative value is resolved against the including file (lines 100-102) and a leading `~/` is expanded (line 97), and a FIFO at that path blocks the command inside open(2) (fifo(7), S062), so the pre-report gate follows include targets before its first git call (r78 rows g5-g7, census/round-78/records/c1-after.txt) | mined | 2026-11-07 | on-release | corpus/knowledge/git-discovery-sources.md, corpus/QUALITY.md |
| S324 | git setup.c at tag v2.56.0, get_common_dir_noenv(), https://raw.githubusercontent.com/git/git/v2.56.0/setup.c (sha256 8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589, fetched 2026-11-07, HTTP 200, 83214 bytes; capture census/round-78/srcs/git-setup.c-v2.56.0) | code | A | which files git opens while it discovers a repository, before any subcommand runs (scope: the commondir existence test and its read; HEAD validation by validate_headref at line 350 read but not quoted; the safe.directory logic not used) | get_common_dir_noenv(), lines 328-329 of census/round-78/srcs/git-setup.c-v2.56.0 (whitespace-normalized; line 327 is the strbuf_addf that builds the commondir path): "if (file_exists(path.buf)) { if (strbuf_read_file(&data, path.buf, 0) <= 0)" | git's discovery tests only that `$GIT_DIR/commondir` exists (file_exists) and then reads it with a plain blocking strbuf_read_file, so a FIFO at that path blocks discovery and with it every git command in that repository (fifo(7), S062); with S323 this is why a gate that runs git in a repository it does not own checks these paths are regular before its first git call (r78 rows g1-g4, g8-g11, census/round-78/records/c1-after.txt) | mined | 2026-11-07 | on-release | corpus/knowledge/git-discovery-sources.md, corpus/QUALITY.md |
