# ReopenRefs — round-20 final source falsifier (S092, S090)

Disposition: no blocking defect. S092 agrees with its pinned page section and version, and its Gate quotation is verbatim in the reader's text of the page's OPTIONS paragraph. S090 is a retained rejection, dated 2026-10-21 in the registry and consistent with the Gate's "opened 2026-10-21" header, with its flip stated in both places. Its page quotation and version were not re-opened by this seat, because the git-filter-branch URL is outside this item. Four non-blocking notes follow. No registry, lesson, or source file was edited.

Author-side advisory only; not a non-author closure or promotion. No SHONEN marks.

Pinned basis: commit 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 (verified as a commit). Named files only: `corpus/SOURCES.md` (blob 0b8c6ccc0d4a034f6b426fdc6b1662681eb48616) and `corpus/lessons/round-20.md` (blob fd465ed8ce27918359ce67e3166958ea423f9f87). Public URL: https://git-scm.com/docs/git-for-each-ref.

## Axes checked
1. Quote fidelity: located words against the page text.
2. Registry fields: tier, status, used-by, and version statement, against the page and host git.
3. Primary fact versus lane policy.
4. Retention and dating: S090 neither backdated nor dropped.
5. Own confidence: each verdict tagged by how it was observed.

## Access record: https://git-scm.com/docs/git-for-each-ref
- Access date: 2026-10-21 (host UTC 09:54:50, same batch as the fetch).
- Method: reader rendering (text/html, native). Raw HTML was not separately opened, so the quote is verified in reader text only.
- Actual version: the page's version selector reads "git-for-each-ref last updated in 2.54.0". The 2.54.0 entry is dated 2026-04-20, and the list marks "2.55.0 → 2.56.0 no changes". Host `git --version`: git version 2.56.0 (read-only).
- Located quote (OPTIONS, `<pattern>...` paragraph; 11 words): "only refs are shown that match against at least one pattern". The reader wraps after "that"; the sentence renders as one.
- Same paragraph, not quoted by S092 or its Gate: "in the latter case matching completely or from the beginning up to a slash" (see N1).

## Commands run (all read-only)
- `read https://git-scm.com/docs/git-for-each-ref`: returned text/html via the reader.
- `date -u +%Y-%m-%dT%H:%M:%SZ` and `git -C <lane> cat-file -t 1988860…`: timestamp above; `commit`.
- `git -C <lane> show 1988860…:corpus/SOURCES.md` and `…:corpus/lessons/round-20.md`: full named files returned; then line-range reads of those outputs to locate rows.
- `git -C <lane> rev-parse --verify 1988860…^{commit}`, `rev-parse 1988860…:corpus/SOURCES.md`, `rev-parse 1988860…:corpus/lessons/round-20.md`: commit id and the two blob ids above.
- `git --version`: git version 2.56.0.
- `read skill://godspeed`: posture only.

Exit codes were not displayed by the tool; every call returned output with no error text. Nothing installed or updated (none needed). Nothing was mutated, so no before/after digests apply.

## S092 against the page

| Field | Pinned or Gate text | Page (observed) | Verdict and reason |
|---|---|---|---|
| Quote | Gate, round-20.md:41: "only refs are shown that match against at least one pattern" | Verbatim in the OPTIONS `<pattern>...` paragraph | AGREE, high. Exact words; the reader's line wrap is not part of the sentence. |
| Section | SOURCES.md:112 "OPTIONS <pattern>..."; Gate "OPTIONS / <pattern>..." | `## OPTIONS`, `*<pattern>*...` | AGREE. |
| Version | SOURCES.md:112 "last updated 2.54.0, unchanged through 2.56.0"; Gate "last updated 2.54.0" | Last updated 2.54.0; 2.55.0 → 2.56.0 no changes; host 2.56.0 | AGREE. |
| Scope | "filtering refs by explicit patterns, not durable authority assigned to a namespace" | Describes filtering only; says nothing about durability, roots or authority | AGREE. Narrow, and matches the page. |
| Teaches, page part | "supplied patterns restrict shown refs to at least one match" | Same sentence | AGREE. |
| Teaches, policy part | heads/tags/remotes as durable roots; jj grace-ref exclusion "are lane policy" | Page is silent on roots, durability and jj | AGREE that it is policy. Exclusion of refs/jj follows from the matching rule, not from any page statement. |
| Namespace selection | Not stated in S092 | Literal case: "from the beginning up to a slash" | AGREE but INCOMPLETE (N1). |
| Tier / status / used-by | A / mined / corpus/lessons/round-20.md; Registry-changes paragraph says "used-by this lesson" | Official upstream manual | AGREE. Tier A is plausible; the tier contract was not opened, so it is not re-derived. |
| Supersedes S080 | "supersedes S080", with the narrower teaches above | See N3 | AGREE with narrowing. |

## S090: retained rejection and flip
- Registry, SOURCES.md:110: tier A; scope "rejection of history rewrite as Souji cleanup authority, not a replacement-tool endorsement"; status rejected; opened 2026-10-21; recheck on-release; used-by corpus/lessons/round-20.md. AGREE: retained, dated, used-by matches.
- Gate, round-20.md:39: "**reject** as Souji cleanup/history-rewrite authority; flip only through separately scoped operator history work to its owner, never a cleanup receipt." AGREE: same decision and flip as the registry.
- Not invented: S079–S088 (SOURCES.md:99–108) all remain `mined`. The lesson declines to backfill a round-19 reject, and the standing S032 reject (SOURCES.md:52, opened 2026-10-19) is still `rejected`. AGREE that S090 is an actual round-20 reject.
- Primary versus policy: the only page-level fact S090 relies on is the WARNING wording (Gate quotation: "its use is not recommended."). The reject itself rests on lane scope: "outside this lane", no replacement endorsement, and an operator flip. It is a scope decision, not a finding about the page.
- Flip mismatch (non-blocking): S032 flips only when git drops the WARNING and the operator moves history rewrite into Souji's province. S090 flips on operator scope alone. Both are retained; the difference should be stated, not reconciled by edit here.
- NOT VERIFIED by this seat: S090's quotation, its version statement ("last updated 2.44.0, unchanged through 2.56.0"), and its access record. No agree or disagree verdict is given for those fields.
- Discernment note: as a specimen, S090 tests the lane's scope decision more than the page's reading. A source-grounded reject would rest on a page fact alone.

## Non-blocking notes (for L1; no edits made)
N1. Literal-prefix clause missing from S092. The same OPTIONS paragraph says literal patterns match "in the latter case matching completely or from the beginning up to a slash" (14 words). The lane's selector uses bare namespace prefixes (`refs/heads refs/tags refs/remotes`), which is exactly that literal case. Neither S092 nor its Gate cites it, so the single quotation does not by itself show that a bare `refs/heads` covers `refs/heads/<name>`. S092 claims no such thing, so this is incomplete rather than wrong. If any consumer relies on it, cite this clause.

N2. Root refs not mentioned. `--include-root-refs` is described as listing "root refs (`HEAD` and pseudorefs) apart from regular refs" (9 words). The option text implies they are not listed without the flag; default output was not tested. This matters to a consumer expecting HEAD or pseudorefs in pattern output, not to the heads/tags/remotes selection.

N3. Supersession narrows S080. S080's clause that `%(*objectname)` yields a peeled tag target is page-supported: the FIELD NAMES section says "a fieldname prefixed with an asterisk (`*`) expands to the fieldname value of the peeled object" (16 words). After "supersedes S080", no other row carries that clause (checked by reading the registry), and S080 stays `mined` with its original teaches. Not a defect; a consumer using `*` fields should cite S080 or a new row.

N4. Documentation hygiene. (a) round-20.md drops spaces in several cells: "git2.56.0" (lines 38, 40, 42), "unchanged through2.56.0" (line 39), "last updated2.54.0" (line 41), and "tierA" in the Registry-changes paragraph. The quoted sentences are unaffected. (b) SOURCES.md's header has provenance paragraphs for rounds 13, 14, 16–19 but none for round 20 (none for round 15 either). The S089–S095 provenance lives in round-20.md's Gate and Search log.

## Calibration summary
- High (observed in pinned bytes or page text): the S092 quote, section, version and registry fields; S090 presence, status, dates, used-by and flip; no duplicate S090 or S092 ID (registry read in full, lines 1–157); S079–S088 status; the S080 clause's support on the page.
- Medium: exact punctuation and wrapping of the quote, since only reader text was checked.
- Not verified, asserted nowhere: S090's quotation and version; the tier contract; the `tools/souji-rev-pin.py` comment citing S092 (outside the named subpaths); whether the git-filter-branch WARNING names a replacement tool (the S090 scope does not depend on the answer).

## Limits
- No page command executed; no build, test, lint, smoke, or target run.
- Reads limited to the named subpaths and the godspeed skill; no census, operator-sweep, transcript, or fleet path opened.
- No subagents dispatched. Only this report was written.

Trailer: `.ufo/waves/round-20/final/ReopenRefs.md` (relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`).
