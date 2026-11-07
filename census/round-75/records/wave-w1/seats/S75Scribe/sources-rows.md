# S75Scribe — round-75 SOURCES rows (draft for L1 integration)

Draft only. Neither row is in the committed registry (`git show HEAD:corpus/SOURCES.md` carries no
`gitignore.adoc` or `git-ls-files.adoc` raw URL); the worktree already holds two uncommitted S318/S319
rows written by another seat — see the note at the end.

## Provenance paragraph (place at the end of the provenance block, immediately before `## Paths`)

Round-75 provenance: new S318 and S319 were opened live on 2026-11-06 by wave-1 seat S75Scribe for the C1 ignore-source claim; S318 is gitignore(5) at tag v2.56.0 (DESCRIPTION, where a pattern belongs) and S319 is git-ls-files(1) at the same tag (EXCLUDE PATTERNS, which sources `--exclude-standard` adds). Both captures are byte-identical to the upstream raw files re-fetched 2026-11-06 (HTTP 200, 9535 and 12123 bytes; the sha256 in each row is the capture's and the re-fetch's), and both quotes are located by byte offset in those captures and are 20 and 12 words. URL, access date and the located quote are in each row; no existing row's status, recheck or used-by cell changed, and neither URL was in the registry before this round.

## Rows (append after S317, which is the last row of the `## Registry` table)

| S318 | gitignore(5) at tag v2.56.0, DESCRIPTION, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitignore.adoc (sha256 338221577b4f47ea61b10eb6e57e7b0aab71e3f7ff8ce8bc067676aede805e71, fetched 2026-11-06, HTTP 200, 9535 bytes; capture census/round-75/srcs/gitignore.adoc) | docs | A | which ignore sources are the repository's declared policy and which are local to one repository or one user (scope: where the page sends each kind of pattern; pattern syntax, negation and precedence between sources not used) | DESCRIPTION, where patterns belong; quote at byte offset 1699 of census/round-75/srcs/gitignore.adoc (whitespace-normalized): "Patterns which are specific to a particular repository but which do not need to be shared with other related repositories" | the page sends patterns meant to be version-controlled and distributed to `.gitignore` files, repository-specific patterns that need not be shared with other clones to `$GIT_COMMON_DIR/info/exclude`, and per-user patterns to `core.excludesFile`, so the source of an ignore rule decides whether a clean status rests on declared repository policy | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |
| S319 | git-ls-files(1) at tag v2.56.0, EXCLUDE PATTERNS, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-ls-files.adoc (sha256 56af3aad88df8849f2e9b428b60768f040b4825590ddd5c6733dee7ac5eda74b, fetched 2026-11-06, HTTP 200, 12123 bytes; capture census/round-75/srcs/git-ls-files.adoc) | docs | A | which exclude sources `git ls-files --others --ignored` reads under `--exclude-standard` and which `--exclude-per-directory` alone leaves out (scope: source selection only; output formats and index status tags not used) | EXCLUDE PATTERNS; quote at byte offset 11681 of census/round-75/srcs/git-ls-files.adoc (whitespace-normalized): "To emulate what `--exclude-standard` specifies, you can give `--exclude-per-directory=.gitignore`, and then specify:" | `--exclude-standard` is the per-directory `.gitignore` files plus the user's global exclusion file and `$GIT_COMMON_DIR/info/exclude`, and the page makes a caller who gives only `--exclude-per-directory=.gitignore` add the other two sources by hand, so the set difference of the two listings is the untracked content hidden only by a local, unversioned ignore source | mined | 2026-11-06 | 180d | corpus/knowledge/filter-filemode-witness.md |

## Verification performed on this draft

- captures: `sha256sum census/round-75/srcs/*.adoc` = 338221577b4f47ea61b10eb6e57e7b0aab71e3f7ff8ce8bc067676aede805e71 / 56af3aad88df8849f2e9b428b60768f040b4825590ddd5c6733dee7ac5eda74b; `curl -sSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/{gitignore,git-ls-files}.adoc` re-fetched 2026-11-06, HTTP 200, byte-identical to the captures.
- anchors: offset 1699 begins `Patterns which are specific to a particular repository…` in gitignore.adoc; offset 11681 begins `To emulate what \`--exclude-standard\` specifies…` in git-ls-files.adoc. Quote word counts 20 and 12, both ≤25. No `|` appears in any cell.
- shape: 11 columns, matching S315–S317 (`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`).
- census: see `census-validate.txt` in this directory (rows appended after S317 to a copy of the committed corpus).

## Note for the L1 (integration hazard)

`corpus/SOURCES.md` in the worktree already carries uncommitted S318/S319 rows (and
`corpus/knowledge/filter-filemode-witness.md` an uncommitted r75 section) from another seat; the
anchors those rows cite (offset 1699 and offset 11681) resolve in the same captures, so the two drafts
agree on ground and differ only in wording. Do not append both sets: S318/S319 are single ids.
