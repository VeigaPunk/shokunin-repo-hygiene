# ReopenDiff: round-20 final source falsifier (S093, Gate quote, S090)

Seat: SoujiR20-2.ReopenDiff. Leaf, source-only. No subagents, no registry changes, no page commands executed, no census, operator-sweep or private reads.
Pinned revision: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1. Named files were read only via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>`: `corpus/SOURCES.md` and `corpus/lessons/round-20.md`.

## 1. Access record

- Opened: `https://git-scm.com/docs/git-diff` in reader-text mode, and the same URL in raw-HTML mode (`:raw`). No other URL was opened.
- Access timestamp: 2026-10-21T09:55:12Z (UTC, from `date -u` in the same parallel batch as the fetch). The reader result carries no HTTP date.
- Actual version: the page's nav reads "Latest version ... git-diff last updated in 2.56.0" (raw HTML line 1333). The version dropdown lists 2.56.0 with the date 2026-09-28 beside that entry.
- Host context only: `git --version` returned `git version 2.56.0`. No git-diff command was run, so no behaviour was observed.

## 2. Primary page facts (exact quotes, each at most 25 words)

Line numbers are reader-text lines unless marked raw.

| ID | Section | Exact quote | Location |
|---|---|---|---|
| P1 | OPTIONS / --quiet | "Disable all output of the program. Implies --exit-code." (8 words) | reader 1103; raw 4209 |
| P2 | OPTIONS / --quiet | "Disables execution of external diff helpers whose exit code is not trusted" (12 words) | reader 1104-1105; raw 4210-4211 |
| P3 | OPTIONS / --exit-code | "it exits with 1 if there were differences and 0 means no differences." (13 words) | reader 1097-1099; raw 4203-4205 |
| P4 | DESCRIPTION, --no-index form | "This form implies --exit-code." (4 words) | reader 290-291; raw 3263-3264 |
| P5 | OPTIONS / --check | "Not compatible with --exit-code." (4 words) | reader 790-791 |
| P6 | CONFIGURATION / diff.trustExitCode | "Any other exit code causes Git to report a fatal error." (11 words). Concerns external helper exit codes only. | reader 1838-1843 (driver form 1946-1951) |

- OPTIONS (raw 3364) contains both --exit-code and --quiet (raw 4201-4211), before "Raw output format" (raw 4381).
- Page-wide: searching the page text for "exit" and "fatal" and for the number 128 found no git-diff exit status other than 0 and 1 (P3). P6 is about external helper programs, not git-diff's own exit status.

## 3. Pinned S093 row (`corpus/SOURCES.md` line 113)

kind docs | tier A | scope "--quiet output and --exit-code semantics; no completeness claim about supplied paths" | anchor "last updated 2.56.0 (2026-09-28), reopened 2026-10-21; OPTIONS --quiet and --exit-code" | status mined | opened 2026-10-21 | recheck on-release | used-by `corpus/lessons/round-20.md`.

Teaches (lane text): "supersedes S081 — --quiet disables output and implies --exit-code; status 1 denotes differences and 0 no differences. Complete measured-path discovery and failure classification are separate lane obligations."

## 4. Pinned Gate row (`corpus/lessons/round-20.md` line 42)

"https://git-scm.com/docs/git-diff, git2.56.0, OPTIONS / --quiet: “Disable all output of the program. Implies --exit-code.”" Decision: "admit/mined, supersedes S081's teaching: --exit-code documents1=differences,0=no differences; omitted paths remain omitted."

The quote is identical to P1. The version token matches the page's 2.56.0. The pinned bytes have no separator there ("git2.56.0").

## 5. Agree / disagree

| # | Claim (location) | Page evidence | Verdict |
|---|---|---|---|
| A1 | Gate located quote (lesson l.42) | P1, exact | AGREE |
| A2 | --quiet disables output (S093) | P1 | AGREE |
| A3 | --quiet implies --exit-code (S093, Gate) | P1 | AGREE |
| A4 | status 1 = differences, 0 = no differences (S093 teaches; Gate "documents ...") | P3 | AGREE on substance. DISAGREE on sourcing: the Gate quotes only P1, so the exit-code half has no located quote there. This seat located it at P3. |
| A5 | Version 2.56.0 (S093 anchor; Gate "git2.56.0") | nav stamp, host git 2.56.0 | AGREE |
| A6 | "(2026-09-28)" in S093 anchor, phrased "last updated 2.56.0 (2026-09-28)" | Date is printed beside the 2.56.0 dropdown entry. The page's own last-updated text names only the version. | Date AGREES with the dropdown. The "last updated" phrasing overstates it. Calibrate. |
| A7 | Scope "no completeness claim about supplied paths" | Page is silent on completeness | AGREE (absence only) |
| A8 | --quiet also prevents running external helpers whose exit code is untrusted | P2 and P6 | OMITTED from S093 teaches and from the Gate. Non-blocking. It matters only if a measured repository configures an external diff driver. This seat did not inspect any repository's configuration. |
| A9 | "omitted paths remain omitted" (Gate) | Page is silent | LANE POLICY, not page text. The Gate puts it beside page quotes without a label. |
| A10 | "Complete measured-path discovery and failure classification are separate lane obligations" (S093) | Page is silent | LANE POLICY, correctly labelled in the row |
| A11 | S081 (superseded) teaching: any other nonzero exit is a refusal | Page assigns only 0 and 1 to git-diff's own --exit-code. P6 concerns helper programs. | Not a page fact. S093 correctly drops it. S081 row unchanged. |

Confidence: quotes high (exact match in two renderings). Version high (page stamp, and host git 2.56.0 matches). A8 materiality medium (depends on repository configuration, not inspected).

## 6. S090: retained rejection and flip

The git-filter-branch URL is not in this item's named-URL list, so that page was not opened. Checks below use the pinned named files only.

- Registry (`SOURCES.md` line 110): tier A | status rejected | opened 2026-10-21 | used-by `corpus/lessons/round-20.md` | scope "rejection of history rewrite as Souji cleanup authority, not a replacement-tool endorsement" | flip "an operator separately scopes history work to its owner, never a Souji cleanup receipt".
- Gate (`round-20.md` line 39): "**reject** as Souji cleanup/history-rewrite authority; flip only through separately scoped operator history work to its owner, never a cleanup receipt." The flip wording matches the registry row.
- Date and absence of back-dating: S090 appears in the named files only at SOURCES l.110 and l.139 (search log: "rejected 1 cleanup-authority candidate") and at lesson l.39, l.46 and l.50. Lesson l.50 calls it the "actual current reject" and states that the round-19 gap is not back-filled. No earlier S090 reject and no S079–S088 reject row appear in either file. Verdict: retained, dated 2026-10-21, not an invented historical reject.
- Page quote "its use is not recommended." (lesson l.39): NOT VERIFIED here. Corroboration only: S032 (SOURCES l.52, installed git 2.55.0 man page) describes the same WARNING as saying "its use is not recommended". That is a paraphrase in a teaches cell, not a located quote.
- "last updated 2.44.0, unchanged through 2.56.0": NOT VERIFIED here.
- Curation note (no change made): S032 and S090 both reject the same URL, with different reversal conditions. S032's flip: git drops the WARNING and history rewrite moves into Souji's province. S090's flip: an operator scopes history work to its owner. The header keeps rejected rows (S030, S032, S044, S048), so a second row is allowed. The two flips are not aligned.

## 7. Other non-blocking observations

- Run-together tokens in the pinned lesson: "git2.56.0", "last updated2.44.0", "unchanged through2.56.0", "documents1=differences", "opened2026-10-21", and "at most25 words" in the Gate intro. Cosmetic, but they make the version and the 25-word check harder to read.
- SOURCES.md header has provenance paragraphs for rounds 13, 14, 16, 17, 18 and 19, and none for round 20. Round-20 access records live only in the lesson Gate and the search log.
- S093 has no located quote for its --exit-code half (see A4).

## 8. Verdict

- S093: every page-attributed claim agrees with the page. The version is right, and the located quote is exact. Calibration gaps for L1 (non-blocking, not applied here):
  (a) add the P3 --exit-code quote to the Gate;
  (b) add the P2 untrusted-helper clause, or state that it is out of scope;
  (c) label "omitted paths remain omitted" as lane policy;
  (d) reword the anchor so "(2026-09-28)" is not presented as a last-updated stamp.
- S090: the retained rejection and flip are present and consistent across the registry row and the Gate. No earlier reject is back-dated in the named records. Its page quote and version claim remain unverified by this seat. Verifying them needs a seat named for the git-filter-branch URL.
- No registry changes. No installs. Tool installs: none. No page command executed. No private, census or operator-sweep access.
