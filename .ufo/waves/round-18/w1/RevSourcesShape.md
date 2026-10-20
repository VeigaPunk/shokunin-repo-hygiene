STATUS: DONE — Confirmed the next source ID, frozen row contract, and validator warning/error semantics.

## Scope and finding

Calibration review only; no source was opened for a proposed S064 row and no registry row is being proposed. The current `corpus/SOURCES.md` ends at S063 (SOURCES.md:79), so the next unused, never-reused ID is **S064**. Add rows inside `## Registry`; the table header fixes the column order (CORPUS.md:76-89; SOURCES.md:13-16).

## Exact row template

```markdown
| S064 | <title> — <canonical URL or DOI> | <kind> | <tier> | <scope> | <exact anchor and revision> | <one grounded learner benefit> | <status> | <opened ISO date> | <recheck date or cadence> | <repo-relative used-by path(s), comma-separated, or —> |
```

This is one Markdown table row with **11 cells** (13 pipe-delimited fields including the outer delimiters). Do not put a literal `|` inside a cell. `opened` must be the date the author actually opened the source in the round writing the row; round-18's round lesson Gate must record that row's URL, access date, and a located quote of no more than 25 words that grounds `teaches` (CORPUS.md:89-115). The anchor must identify an exact section/heading/page/line and a version, commit, or publication date; a bare homepage is insufficient (CORPUS.md:98-100).

Allowed values and meaning:

- `kind`: `spec`, `docs`, `paper`, `code`, `tool`, `dataset`, `talk`, `book`, `community`, or `own-work`.
- `tier`: `A`, `B`, or `C`, scoped to the stated claim; `community` must not be tier A. Tier C is lead-only, not sole support for an admitted entry.
- `status`: exactly `queued`, `mined`, or `rejected`. `queued` is opened and worth mining; `mined` is cited by at least one `used-by` path; `rejected` preserves a reason. Rejected `teaches` begins `REJECTED: <reason>; flip: <what would change the verdict>`.
- `recheck`: an ISO date or cadence; documented examples include `90d`, `180d`, and `on-release`. The validator accepts a real `YYYY-MM-DD`, digits followed by lowercase `d`, or a symbolic string matching `[A-Za-z][A-Za-z0-9 _-]*` (sources-census.sh:663-666; contract at CORPUS.md:103-108). Prefer a truthful, intentionally chosen cadence.
- `used-by`: repo-relative knowledge-entry or lesson paths, comma-separated, or `—`. For `mined`, use at least one citing path and ensure every path exists in the lane tree (CORPUS.md:107-108; sources-census.sh:538-569). For a not-yet-used `queued` or `rejected` row, `—` is appropriate.

## W04 and clean validation

`W04` is a warning, not an error: if the validator finds the same extracted/normalized URL under a different scope, it emits `W04 <id> duplicate url <url> across scopes`; W-codes do not change clean-lane status or the final exit code (sources-census.sh:31-37, 600-605, 644-645, 739-745, 803-806). Normalization removes the scheme, fragment, and one trailing slash, and lowercases the host; the path remains case-sensitive. The validator's fixture explicitly expects a cross-scope W04 and exit 0 (sources-census.sh:355-365).

Do not confuse that with a same-URL, same-scope duplicate: `E04` is an error when an earlier row for that normalized URL+scope is non-rejected and the new row is also non-rejected, unless the new row's `teaches` includes `supersedes S0NN` (sources-census.sh:643-653; rejected-pair fixture at :366-382). To keep the overall `validate` result at exit 0, avoid all E findings: exactly 11 cells; valid unique `S064`; row in `## Registry`; valid kind/tier/status; no community+A; `opened` a valid date not in the future; valid recheck; no unhandled same-scope duplicate; and, for a mined row, existing `used-by` paths. Validator errors are E01-E12; warnings W01-W04 are emitted but do not set failure (sources-census.sh:24-37, 634-674, 739-745, 803-806). W01/W02/W03/W04 may still be undesirable as curation, even though they do not make validation nonzero. In particular, W03 is a mined row with `used-by = —`, contrary to the contract's meaning of `mined`.

## Evidence and verification limits

- Read `corpus/SOURCES.md` (lines 1-113): latest ID S063; registry header and current row shape.
- Read `CORPUS.md` (lines 64-148): frozen contract, enums, append-only/new-row Gate requirements, and manual census checks.
- Read `scripts/sources-census.sh` (lines 538-569, 599-688, 739-806) and literal search for `W04`, `E04`, and cadence terms: used-by validation, URL normalization, duplicate tests, exit handling, and cadence predicate. This is source inspection, not execution evidence.
- `read xd://lsp` returned `No such tool: xd://lsp` and the mounted-device listing contained no LSP device. No LSP-backed checks were available; the search was only literal source-location evidence, not semantic proof.
- No shell command or validator run was performed; the lane probe rules do not authorize executing `sources-census.sh`. Therefore exit-0 behavior is stated from the validator source and its committed fixture assertions, not a fresh run.
