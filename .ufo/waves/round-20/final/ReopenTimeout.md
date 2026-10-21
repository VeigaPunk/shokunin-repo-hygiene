# ReopenTimeout: final source falsifier for S094 (GNU timeout locator) and S090 (git-filter-branch reject)

Seat: SoujiR20-2.ReopenTimeout. Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Read-only. Report only: no registry, lesson, or production edits. No page command executed.
Sources read at pin only: `corpus/SOURCES.md` (blob `0b8c6ccc0d4a034f6b426fdc6b1662681eb48616`, 157 lines) and `corpus/lessons/round-20.md` (blob `fd465ed8ce27918359ce67e3166958ea423f9f87`, 278 lines), both via `git show`.
Author-side advisory finding. Not non-author closure or promotion. No SHONEN marks.

**Blocking status: none found. No leading `STATUS: PARTIAL` paragraph.** Two S094 defects (F1, F2) and two exactness or provenance defects (F3, F4) are non-blocking and listed under Findings. F1 must be corrected before any `-k` exit-code claim cites S094.

## 1. Access record

| Field | Value |
|---|---|
| URL opened, exact | https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html |
| Modes | reader text, then `:raw` original HTML of the same URL |
| Access date | 2026-10-21, UTC about 09:55 (`date -u` at the start of the batch: 2026-10-21T09:55:03Z) |
| Capture timestamp | 2026-09-19 21:28:56 UTC (Wayback `id_` = original bytes, `Content-Type: text/html`) |
| Actual version | GNU Coreutils 9.12. Evidence: `<title>timeout invocation (GNU Coreutils 9.12)</title>` and the raw HTML comment "This manual documents version 9.12 of the GNU core utilities" |
| Section | 23.6 `timeout`: Run a command with a time limit |

## 2. Located page quotes (exact, each at most 25 words)

| ID | Location | Quote | Words |
|---|---|---|---|
| P1 | 23.6, `-k duration` / `--kill-after=duration` | Ensure the monitored command is killed by also sending a ‘KILL’ signal. | 12 |
| P2 | 23.6, `--kill-after` | The specified duration starts from the point in time when timeout sends the initial signal to command | 17 |
| P3 | 23.6, Exit status block | 124 if command times out, and --preserve-status is not specified | 10 |
| P4 | 23.6, Exit status block | 137 if command or timeout is sent the KILL(9) signal (128+9) | 11 |
| P5 | 23.6, paragraph after Exit status block | timeout returns with exit status 137, regardless of whether that signal is sent to command or to timeout itself | 19 |
| P6 | 23.6, Examples, `timeout -s INT -k 3s 5s env --ignore-signal=INT sleep 20` | Hence, 'sleep' is forcefully terminated after about 8 seconds (5+3), and 'timeout' returns with an exit status of 137. | 19 |
| P7 | 23.6, `--foreground` | In this mode of operation, any children of command will not be timed out. | 14 |
| P8 | 23.6, paragraph after Exit status block | the command process may still be alive after timeout has forcefully been terminated | 13 |
| P9 | 23.6, Examples, `timeout -s INT 5 sleep 20` (no `-k`) | Returns after 5 seconds with exit status 124 to indicate the sending of the signal. | 15 |
| P10 | 23.6, `-s signal` | Send this signal to command on timeout, rather than the default ‘TERM’ signal. | 13 |

Also located: `--foreground` opens with "Don’t create a separate background program group" (P7 context). The duration rule for `0` is in the `--kill-after` paragraph.

## 3. S094 comparison: pinned registry and Gate against the page

Pinned S094 row: tier A, kind docs, status mined, opened 2026-10-21, recheck on-release, used-by `corpus/lessons/round-20.md`. Scope: "documented 9.12 --kill-after and timeout exit124 only; not descendant containment or reap authority". URL column: the live gnu.org address. Anchor: "reopened 2026-10-21 via Wayback 20260919212856id_ capture; page title GNU Coreutils9.12, §23.6 --kill-after and Exit status". Teaches: "supersedes S038 for the current-version locator only — --kill-after sends a subsequent KILL signal; timeout exit124 applies when command times out without --preserve-status. S038's 9.11 installed-info line numbers remain historical, not current anchors".

Gate in round-20.md (two places: the S094 table row and the "Additional located source correction" section) quotes P1 and P3 and gives the title as "timeout invocation (GNU Coreutils9.12)".

| # | Check | Registry or Gate says | Page says | Verdict |
|---|---|---|---|---|
| C1 | Locator and section | §23.6, --kill-after and Exit status | Both are in §23.6 | Agree |
| C2 | Version | documented 9.12 | title and raw comment: 9.12 | Agree |
| C3 | Quote P1 | exact, located at --kill-after | verbatim, curly quotes as on the page | Agree |
| C4 | Quote P3 | exact, located at Exit status | verbatim | Agree |
| C5 | Teaches clause "--kill-after sends a subsequent KILL signal" | | P1 and P2: KILL is sent after the duration counted from the initial signal | Agree |
| C6 | Teaches clause "timeout exit124 applies when command times out without --preserve-status" | | P3 is this rule. P4 and P5 say that when KILL(9) is delivered the status is 137 regardless. P6 is a `-k 3s` run that returns 137. P9 is a no-`-k` run that returns 124 | Agree for runs with no KILL(9). Disagree for `--kill-after` runs where KILL lands (F1) |
| C7 | Scope "timeout exit124 only" | | The page documents 124, 125, 126, 127 and 137 | Agree as a lane narrowing. The narrowing omits 137, which F1 needs |
| C8 | Scope "not descendant containment or reap authority" | | The page is silent on descendants and reaping. P8 is conditional on timeout itself being KILLed. P7 implies group-level reach (F2) | Agree as lane policy, not as a page fact |
| C9 | "current-version" | current | Capture dated 2026-09-19. Live gnu.org not opened by this seat | Agree as of the capture. Currency at the access date is unverified (F3) |
| C10 | URL column and capture | live gnu.org URL; capture named by timestamp only | The page was read only through the Wayback capture | Provenance gap (F3) |
| C11 | Title spelling | anchor "GNU Coreutils9.12"; Gate title "timeout invocation (GNU Coreutils9.12)" | title reads "GNU Coreutils 9.12" | Disagree on spacing only (F4) |
| C12 | "supersedes S038 for the current-version locator only" | S038 is the installed 9.11 info row, used-by round-14 lesson | The page repeats S038's two teaches clauses for 9.12. S038 is not edited | Agree on supersession. S038 carries the same C6 gap (F1) |
| C13 | Tier A | A | GNU manual is primary documentation. Sibling rows S024 and S025 are also A | Agree. Tier contract not opened (not named) |
| C14 | Status mined, used-by, recheck | mined; round-20 lesson; on-release | Consistent with the Gate's use of P1 and P3 | Agree as recorded |
| C15 | Wording of the anchor | "reopened" | Accounting says absent→opened/mined. S034 records that the live fetch of this same URL timed out | Trivial. "opened" is the accurate verb |

## 4. Findings (non-blocking)

**F1. Precision defect in the teaches cell (moderate). Inherited by S034 and S038.** The clause "timeout exit124 applies when command times out without --preserve-status" holds only when no KILL(9) is delivered (P9). Once `--kill-after`'s KILL lands, the page says 137 regardless (P5), and its own `-k 3s` example returns 137 (P6). Confidence: high, because this is a direct page contradiction in a sub-case. Impact: the round-20 Gate admits only P1 and P3 as quotes, so the locator correction and its quotes are right. No round-20 claim asserts a `-k` exit code, so this does not block the admission. Any consumer that reads S094, S038 or S034 for `-k` exit codes would be wrong. Suggested route for L1, not done by me: a dated correction row (the lane's pattern, as S094 is for S038) that narrows the 124 clause to "no KILL(9) delivered" and adds 137 for KILL(9), including the `--kill-after` path. S034 and S038 are immutable and need that route.

**F2. Scope label is lane policy, not a page fact (low).** The page never states a descendant rule. P7 says children are not timed out in `--foreground` mode, and the `--foreground` paragraph says the default mode creates a separate background program group. [INFERENCE] Together these imply the default mode times out group members, which is group-level reach, not tree-level reach. Escape from the group is not discussed. The lane's exclusion matches P8 and the lane's own measured S072, but those are not statements of this page. Suggested route: mark the exclusion "lane policy" or cite S072 for it.

**F3. Provenance and currency (low).** The URL column is the live gnu.org address, but this seat read only the Wayback capture. The anchor records a timestamp but not the full capture URL; the full URL appears only in the Gate. "current-version" therefore describes the 2026-09-19 capture. Corroboration is limited to lane rows S024 and S025, opened 2026-10-19, which name "online manual GNU Coreutils 9.12". Those are lane records and I did not re-verify them. I did not open live gnu.org because the item named only the Wayback URL.

**F4. Exactness (low, but the Gate's quoted title is not exact).** The page title reads "timeout invocation (GNU Coreutils 9.12)". The S094 anchor and the Gate's quoted title read "GNU Coreutils9.12". Byte check: a grep of both pinned blobs for non-breaking, thin, zero-width and BOM code points returned no matches, so the missing space is literal. The same run-together pattern recurs in round-20.md and SOURCES.md, for example "Opened on2026-10-21:", "tierA within scope", "Identified1", "man-pages6.19". The quoted sentences P1 and P3 are not affected.

## 5. S090: retained rejection and flip

Pinned registry row S090: tier A, kind docs, status rejected, opened 2026-10-21, recheck on-release, used-by `corpus/lessons/round-20.md`. Teaches: "REJECTED: history rewriting is outside this lane and the official warning does not recommend this tool; flip: an operator separately scopes history work to its owner, never a Souji cleanup receipt".

Gate row (round-20.md): quoted WARNING "its use is not recommended." and decision "**reject** as Souji cleanup/history-rewrite authority; flip only through separately scoped operator history work to its owner, never a cleanup receipt".

| Check | Verdict | Reason |
|---|---|---|
| Rejection retained in the pin | Agree | Row present with status rejected. The Gate lists the same decision and flip in matching substance |
| Not an invented historical reject | Agree | Row and Gate both date it 2026-10-21. The round-20 lesson expressly declines to backdate a round-19 reject: "cannot be repaired by inventing a rejected S079–S088 row or relabelling the standing S032 reject" |
| Quote "its use is not recommended." | Not verified by this seat | The item named only the GNU URL. Public docs are opened only when the item names the exact URL, so I did not open https://git-scm.com/docs/git-filter-branch. The wording matches S032's earlier paraphrase, which is lane-internal consistency only |
| "last updated 2.44.0, unchanged through 2.56.0" | Not verified by this seat | Same reason |

Further observations (non-blocking):
- **S1, duplication.** S090 and S032 share one URL and one substantive decision: filter-branch is not a Souji cleanup authority. S090 adds a 2026-10-21 re-open and a version stamp. It is not a new decision. As the round-20 "actual current reject" discernment sample, it re-tests the S032 decision rather than a new one.
- **S2, flip divergence.** S032 flips only if git drops the WARNING and the operator moves history rewrite into Souji's province (both conditions). S090 flips only through operator scoping and does not depend on the page. These are consistent by scope, but the registry now holds two flip conditions for one URL. Suggested route: reconcile in a correction row.

Primary facts vs lane policy for S090: page fact (per the Gate, not verified here): the WARNING says its use is not recommended. Lane policy: history rewriting is outside this lane; the flip conditions; "not a replacement-tool endorsement"; PROVINCE.md § Refuses, cited by S032 and not opened.

## 6. Primary facts vs lane policy for S094

- Page facts: P1 to P10. Section 23.6. Documented version 9.12. Exit codes 124, 125, 126, 127 and 137, with 137 governing KILL(9).
- Lane policy: the "current-version locator" framing; "supersedes S038 … only"; "not descendant containment or reap authority" (F2); recheck on-release; tier A and mined status; the used-by entry.

## 7. Confidence and limits

- High confidence: P1 to P10, the version, the section, and the C3, C4 and C6 comparisons, from direct reads of the page.
- High confidence: F4, from the byte grep.
- Medium: F2, which rests on an inference about the default group.
- No confidence claimed on the S090 page quote or its "last updated" stamps (not verified here).
- Not opened: live gnu.org (not named); installed coreutils 9.11 info and timeout(1) man page behind S034 and S038 (not named); the tier contract SOURCES-CONTRACT-v1 and corpus/QUALITY.md (not named); round-13, round-14 and round-20 lessons other than the named Gate; any knowledge entry that might cite the timeout rows (so F1's downstream exposure is unknown); https://git-scm.com/docs/git-filter-branch (not named).
- Held boundaries: no process inspection, signal, cleanup, deletion, host, package or service action. `census/operator-sweep-20261019/` was not accessed. Certification OFF, K5 HELD and F5 reap and NAMESPACE held were not touched.

## 8. Commands and reads executed

1. `read skill://godspeed`: skill file returned.
2. `read` of the exact Wayback URL: reader text returned (Method native).
3. `read` of the same URL with `:raw`: original HTML returned (Method raw).
4. `date -u +%Y-%m-%dT%H:%M:%SZ`, `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`, and `git -C … show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:corpus/SOURCES.md`: returned 2026-10-21T09:55:03Z, `commit`, and the full registry.
5. `git -C … show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:corpus/lessons/round-20.md`: returned the full lesson.
6. `grep` of `S038|S034|S094|S090|S032` over the SOURCES artifact: matches recorded in sections 3 and 5.
7. `grep` of non-breaking, thin, zero-width and BOM code points over both artifacts: no matches.
8. `grep` of `Coreutils ?9\.12|Coreutils9` over both artifacts: S024 has "Coreutils 9.12"; S094 and the Gate have "Coreutils9.12".
9. `read` of the SOURCES artifact lines 56 to 60: full S034 and S038 rows.
10. `git rev-parse --verify 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1^{commit}`, `git rev-parse` of the two blob paths, and `git show … | wc -l`: pin confirmed; blob ids and line counts as above.

No command output showed an error. The tool outputs did not report exit codes, so I do not claim any.

## 9. Verdict

- S094 locator, version, §23.6 location, quotes P1 and P3, and the scope's 124 clause as quoted: **agree**.
- S094 teaches clause on 124 for `--kill-after` runs where KILL lands: **disagree** (F1). Non-blocking for the round-20 locator correction, blocking for any `-k` exit-code use.
- S094 scope exclusion of containment and reap: **agree as lane policy**, not as a page fact (F2).
- S094 title spelling and provenance wording: **disagree or qualify** (F3, F4).
- S090 retained rejection and flip, and "not invented historical reject": **agree**.
- S090 page quote and "last updated" stamps: **not verified here**. Duplicate of S032 with a divergent flip (S1, S2).
- Blocking findings: none. `STATUS: PARTIAL` not used.
