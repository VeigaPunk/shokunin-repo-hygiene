# Round 28 — Q57 pointer repair, POSIX F4 primitives, wave evidence capture

## Gate

Sources opened in this lane on 2026-10-25; byte snapshots and SHA256SUMS are in `census/round-28/sources/`.

| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |
|---|---|---|---|---|
| S212 `open()` | ADMIT | https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html; Issue 8 snapshot `census/round-28/sources/open.html` | § DESCRIPTION O_EXCL: “creation of the file if it does not exist shall be atomic with respect to other threads executing” (18 words; `census/round-28/records/posix-quotes.tsv`) | Grounds exclusive creation; row used by `origin-record-exclusivity-r28.md`. |
| S213 `rename()` | ADMIT | https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html; Issue 8 snapshot `census/round-28/sources/rename.html` | § DESCRIPTION: “If the <i>rename</i>() function fails for any reason other than [EIO], any file named by <i>new</i> shall be unaffected.” (19 words; quote is byte-exact including served markup) | Grounds atomic publication and failure boundary; row used by `origin-record-exclusivity-r28.md`. |
| S214 `fsync()` | ADMIT | https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html; Issue 8 snapshot `census/round-28/sources/fsync.html` | § RATIONALE: “system crash or other failure that all data up to the time of the <i>fsync</i>() call is recorded on the disk.” (21 words) | Grounds durability boundary; null implementation is explicitly noted. Row used by `origin-record-durability-r28.md`. |
| S119 zh-Hans `git-fetch(1)` edition | ADMIT as S215; no registry append | https://git-scm.com/docs/git-fetch/zh_HANS-CN, opened 2026-10-25 and pinned at `census/round-28/sources/git-fetch-zh-HANS-CN.html` sha256 `a7f4742d99fd515f1811a1abd830a61840939ebe3e12cf1e6792662181b574042` | `census/round-28/records/s119-disposition.tsv` records the located Chinese switch/default quote and the page's 2.56.0 version line. | Decision-time pin clears the prior version-alignment reason; however S215 would make the frozen C2 row counter 139, not 138, so the row is not appended. This leaves the source decision's registry landing incomplete and C2's frozen counter unmet. |
| Staged S216 near-duplicate-threshold paper | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, opened 2026-10-25 | `SwarmExecutor07.md` identifies S216 as the approximate-matching-threshold paper. | F3 duplicate-verdict scope, not F4 origin-record primitives; flip: reconsider under F3 when the duplicate-class decision opens. |
| Staged S138 Qiita Git-GC community note | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, opened 2026-10-25 | `SwarmExecutor07.md` identifies S138 as community Git-GC notes. | F1/F2 reclamation practice, not an F4 origin-record primitive; flip: reconsider only if an F4 consumer needs community corroboration of POSIX. |

No independent non-author spot-check is on record at this point. Wave reviewers are lane-dispatched advisory seats and do not satisfy the independent closure duty; admit/reject agreement remains unverified pending outside review.

## Findings

- C1 before at base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`: landing gate `findings=2`, `checked_reg=52` (`census/round-28/records/c1-before.tsv`). Q57's separate checker returned `q57=PASS`, masking that the landing gate independently parsed two cited prose tokens as missing paths (`corpus/QUALITY.md:141,143`). The Q57 selector list was moved into `census/round-28/q57-sites.txt`, and its mapping operand now points to committed `census/round-24/records/slice-verdicts.tsv`; Q59's prose token was reworded without changing its axis-class rule.
- C2 before: grounded F4 knowledge entries=4, SOURCES rows=135 (`census/round-28/records/c2-before.tsv`). Two F4 entries and three POSIX rows were added; F4 entries are 4→6. Source gate ran `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; fleet source census exit 0. The frozen registry-row counter is 139 because the separately admitted S119 decision yields S215; the frozen target 138 is missed. Coverage agreement at the revision read returned global `grounded=11 mapped=11 dangling=0 mismatches=0`; this is not the frozen C2's claimed F4-only `6/6`, so that sub-predicate is not verified.
- C3 captured round-26 and round-27 wave bytes and restored the 11 modified tracked r26 wave files to master; `.gitignore` contains `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`. Dirty `.ufo/waves` count went 163→0 and the directories remain present. The six-case fixture reports `cases=6 pass=6 control=TAMPER-REJECTED`. Limitation: independent `sha256sum -c census/round-26/waves/manifest.sha256` warns that two newline-containing filenames are improperly formatted (rc 0); tool-internal generation/recheck alone does not establish an independently consumable manifest for those paths. Round-27 manifest verifies cleanly.

## Receipts

- Frozen preregistration and controls: `census/round-28/records/preregistration.txt`, `c1/c2/c3-before.tsv`, `c1/c2/c3-control.tsv`, `axis-check-before.txt`.
- POSIX quote and source pins: `census/round-28/records/posix-quotes.tsv`, `census/round-28/sources/SHA256SUMS`.
- S119 decision and frozen-counter impact: `census/round-28/records/s119-disposition.tsv`, `s119-counter-impact.tsv`.
- C1 selectors: `census/round-28/q57-sites.txt`; capture receipts: `census/round-{26,27}/waves/`.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| stale-premise | base `c1-before.tsv` has landing-gate `findings=2` while the Q57 checker independently reports `q57=PASS` (`SwarmExecutor01.md`, `SwarmExecutor02.md`); `corpus/QUALITY.md:141,143` | none — no existing criterion required agreement between the checker and pointer gate | Keep selector data outside the criterion cell, point the checker at committed authority, and reword prose that is not a path. The fix can fail: the committed base produces the two named `LG-DANGLING-PTR` findings; the after counter is required to return 0 with no exemption. |

## Residuals

- C2 is an honest stop under its frozen claim: its 138-row target is missed at 139 after admitting S119/S215; the `6/6` F4-only coverage-agreement literal is not the tool's global output. No predicate or target was narrowed.
- C3's round-26 manifest has two malformed newline-path records under the standard `sha256sum -c` consumer; report this as an unresolved receipt defect, not a clean verification.
- Source-side package remains read-only. `considerthese/` is absent (confirmed at round start); no proposal was assimilated.

## Wave

One v2 wave `souji-r28-w1`, 64 seats dispatched; L1 performed the planner data-walk. Final role mix, dead seats, and last-error text are taken only from the dispatcher's `w1-results.json` when delivered; no result payload has yet been integrated into this lesson.
