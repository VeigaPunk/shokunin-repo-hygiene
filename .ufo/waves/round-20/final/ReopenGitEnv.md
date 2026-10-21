# ReopenGitEnv: round-20 final source falsifier (S089, S090)

Read-only. Named URL: https://git-scm.com/docs/git. Pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`: `corpus/SOURCES.md` (blob `0b8c6ccc0d4a034f6b426fdc6b1662681eb48616`) and `corpus/lessons/round-20.md` (blob `fd465ed8ce27918359ce67e3166958ea423f9f87`). No page command was run. No private, census, or operator-sweep path was opened. No registry or lesson edit was made. No build, test, install, or subagent was used. The only write is this report.

Blocking finding: none. Non-blocking items are in section 4. No STATUS marker is warranted.

## 1. Access record

- Access date: 2026-10-21 (host clock via `date -u`, 09:55:50Z, taken after the fetch). The reader response carries no fetch timestamp.
- Reader capture of https://git-scm.com/docs/git (method native): artifact://36953.
- Raw HTML capture of the same URL (method raw): artifact://37279.
- Actual version on the page: git 2.56.0. Banner "git last updated in 2.56.0" at artifact://37279 line 1358. The version list's first entry is 2.56.0, dated 2026-09-28; the raw date is at line 1391.
- Commands run, all exit 0:
  - `git -C <lane> cat-file -t 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` gave `commit`.
  - `git -C <lane> rev-parse --verify --quiet 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1^{commit}` gave the full commit id.
  - `git -C <lane> rev-parse <commit>:corpus/SOURCES.md <commit>:corpus/lessons/round-20.md` gave the two blob ids above.
  - `git -C <lane> show <commit>:<path>` on each file.
  - `date -u +%Y-%m-%dT%H:%M:%SZ`.
- Page checks were regex searches over the two captures only.

## 2. S089: AGREE on quote, version, anchors, page-fact teaches, and tier/status/used-by. One teaches clause is lane inference, not page text.

- Located quote (10 words): "Set the path to the root of the working tree." It is the GIT_WORK_TREE entry under `## Environment Variables` / `### The Git Repository` (artifact://36953 line 1553; artifact://37279 line 5307). The wording is verbatim in both captures.
- Scoped tier/status/used-by: tier A; status mined; used-by `corpus/lessons/round-20.md`; recheck on-release. The Gate row reads "admit/mined", which matches.
- Pinned teaches cell, verbatim: "GIT_DIR overrides the default repository base; GIT_WORK_TREE sets the worktree root; GIT_COMMON_DIR and GIT_INDEX_FILE redirect their respective stores. A supplied -C directory alone is not a repository-selection guarantee"

| Clause | Pinned record | Page evidence | Verdict |
|---|---|---|---|
| Version | "git manual last updated 2.56.0 (2026-09-28)" | 2.56.0, dated 2026-09-28 | Agree. The Gate spells it "git2.56.0" (missing space). |
| Anchor | "ENVIRONMENT VARIABLES GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_INDEX_FILE" | Web headings are "Environment Variables" (h2) and "The Git Repository" (h3). All four variables are present. | Agree. The uppercase label is the man-page convention that S006, S036, and S049 also use. |
| GIT_DIR | "overrides the default repository base" | "specifies a path to use instead of the default .git for the base of the repository." (artifact://36953 lines 1547-1548; backticks stripped) | Agree. |
| GIT_WORK_TREE | "sets the worktree root" | Located quote above. | Agree. |
| GIT_COMMON_DIR, GIT_INDEX_FILE | "redirect their respective stores" | INDEX_FILE: "This environment variable specifies an alternate index file." (artifact://36953 lines 1518-1519). COMMON_DIR: "Worktree-specific files such as HEAD or index are taken from $GIT_DIR." and "This variable has lower precedence than other path variables such as GIT_INDEX_FILE" (artifact://37279 lines 5346-5351). | Agree in substance. Gap: the row omits that COMMON_DIR leaves HEAD and index in $GIT_DIR and yields to GIT_INDEX_FILE. |
| -C clause | "A supplied -C directory alone is not a repository-selection guarantee" | No such wording in either capture. A case-insensitive sweep for "guarantee", "reproducib", and "repository-selection" returned zero matches. Page premises: "Run as if git was started in <path> instead of the current working directory." (artifact://37279 lines 3903-3904), and GIT_DIR or --git-dir "turns off the repository discovery" (lines 4005-4006). | Lane inference, not page text. Sound from the page premises, but it must be labelled as inference. |
| Scope | "not full environment reproducibility" | Not page text. The page supports only a caution: "they may be used/overridden by SCMS sitting above Git" (artifact://37279 lines 5258-5259). | Lane scope policy. The Gate's "not complete" has the same meaning. |

- Overall S089 verdict: AGREE on the located quote, version, anchors, the GIT_DIR, GIT_WORK_TREE, and GIT_INDEX_FILE teaches, and the scope caution. DISAGREE only with the unlabelled -C clause and the omitted COMMON_DIR detail. Both are non-blocking.
- Page facts: the four variable definitions, the -C and discovery text, the SCMS caution, and the version.
- Lane policy or inference: the -C "not a guarantee" clause, the "reproducibility" scope, tier A, and recheck on-release (SOURCES-CONTRACT-v1 policy, not opened).

## 3. S090: AGREE at record level. The retained rejection and flip are consistent and not backdated. The page quote and version are NOT verified by this seat.

- Access date: not verified by this seat. Retained record: 2026-10-21.
- Located quote: none located by this seat. Retained Gate quote: "its use is not recommended." (5 words).
- Actual version: not verified. Retained record: "last updated 2.44.0, unchanged through 2.56.0".
- Scoped tier/status/used-by (retained): tier A; status rejected; used-by `corpus/lessons/round-20.md`.

Retained records at the pinned commit:
- Registry row S090. Teaches, verbatim: "REJECTED: history rewriting is outside this lane and the official warning does not recommend this tool; flip: an operator separately scopes history work to its owner, never a Souji cleanup receipt"
- Gate row S090 in round-20.md: "**reject** as Souji cleanup/history-rewrite authority; flip only through separately scoped operator history work to its owner, never a cleanup receipt"
- The "Registry changes" paragraph in round-20.md says "S090 rejected".
- The "Missing round-19 catalogue" section in round-20.md calls S090 an "actual current reject" and disclaims any round-19 row.
- The round-20 search entry in SOURCES says "rejected 1 cleanup-authority candidate (S090)" and that "neither this new rejection nor the older S032 rejection is relabelled as a missing round-19 decision."
- No retained record dates S090 to round 19 or earlier.
- Consistency: status, scope, flip, date, and used-by agree across all records. The only wording difference is "Souji cleanup receipt" in the registry versus "cleanup receipt" in the Gate. That difference is trivial.

Not verified here:
- The git-filter-branch page itself. The item named only the git(1) URL. So "its use is not recommended", "last updated 2.44.0, unchanged through 2.56.0", and "opened 2026-10-21" are unchecked by this seat.
- [INFERENCE] The phrase matches the S032 row's quote from the installed git 2.55.0 man page (roff line 46: "its use is not recommended"). That is a different artifact, and I did not re-open it.
- round-19.md was not opened, because it is outside the named subpaths. The no-backdating conclusion rests on round-20.md's own statement and on the row dates.

Page facts versus lane policy:
- The decisive ground is lane policy: outside this lane. The page would supply only the warning, and that is unverified here.
- The S090 row does not cite PROVINCE.md § Refuses, which S032 cites for the same refusal. That is a cross-reference gap.
- The flip is an authority-scope condition, not a source-revision condition. No source change can satisfy it. That is coherent, but the row should be counted as a policy decision, not as new source evidence.
- S090 and S032 share a URL and the same warning under different scopes. "1 rejected" is a new row, not independent corroboration.

## 4. Non-blocking items for L1 (no edits made here)

1. The S089 teaches clause "A supplied -C directory alone is not a repository-selection guarantee" is lane inference in a teaches cell. The S086 to S088 corrections removed lane policy from teaches cells for this reason, so S089 is inconsistent with that standard. Relabel it or move it to scope. The round-20 source-only finding says the current helper cites S089 (round-20.md, SourceRefs bullet), so the clause may reach code comments. I did not open the helper.
2. S089 omits the COMMON_DIR precedence and HEAD/index sentences. Add them or accept the gap.
3. S089 shares git(1)'s URL with S006 (queued), S036 (mined), and S049 (mined). S049's round-16 provenance note is the precedent for disclosing such a share, and S089 has no note. The scopes differ, so this is not a duplicate. The URL should not count as new source diversity.
4. S090 lacks the PROVINCE.md cross-reference that S032 carries.
5. Typography in round-20.md, with no content change to the quotes: Gate row S089 has "git2.56.0"; Gate row S090 has "last updated2.44.0, unchanged through2.56.0"; the Registry-changes paragraph has "absent→opened2026-10-21" and "tierA"; the Gate header has "at most25 words".
6. SOURCES.md has no Round-20 provenance paragraph at the top. Earlier rounds, for example Round-19, have one. The round-20 record sits in the Gate and the search log.

## 5. Calibration ledger

| Claim | Confidence | Basis |
|---|---|---|
| S089 quote is verbatim | Very high | Matches in the reader and raw captures. |
| Version 2.56.0, dated 2026-09-28 | Very high | Raw banner and version list. |
| GIT_DIR, GIT_INDEX_FILE, GIT_COMMON_DIR page facts | High | Reader capture; raw capture confirms COMMON_DIR. |
| The -C clause is not page text | Very high | Zero matches for policy wording. |
| The -C clause is a sound inference | Moderate-high | Premises are on the page; the conclusion is the lane's. |
| S090 retained record is consistent and not backdated | High | Direct reads and complete-capture searches of the pinned files. |
| S090 page quote, version, and opened date | Unverified | Page not opened; no confidence assigned. |
| No round-19 S090 claim exists anywhere | Moderate-high | round-20.md read in full; SOURCES.md searched across its complete capture (display elided mid-file); round-19.md not read. |

## 6. Remaining unknowns

- S090 page text and version. This needs a seat named for https://git-scm.com/docs/git-filter-branch.
- SOURCES-CONTRACT-v1 tier definitions. Not opened.
- Whether the helper's code comment carries the S089 -C clause. The helper was not opened.
