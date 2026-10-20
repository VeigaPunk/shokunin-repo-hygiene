STATUS: DONE — three append-only LOG.md correction drafts (R2 ×2 dangling-record pointers, R3 repo count) verified against b5763415cc67ecff1e8fe56c58c39a6fb106d7a3; LOG.md, SKILL.md, SCORECARD.md and corpus files not edited.

# Scope

Round 18, wave 1, seat ScribeLogCorrections. Judged on calibration. Text drafted here only; LOG.md is not written (append at the tail of LOG.md, which is 946 lines at b576341).

# Findings and evidence

## F1 (R2a) — `gate-replays-ddb7347.json` was never committed; the committed record is `gate-replays-4f48343.json`

Cited at: `LOG.md:916`, `SKILL.md:163`, `SKILL.md:165`.

Evidence:
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 census/round-17/` lists `gate-replays-4f48343.json`, `gate-replays-expected.json`, `gate-replays.py`, `c1-matrix-4f48343.json`, `c1-matrix.json`, `gate-landing.json`, `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`, `live-fleet.json`, `run-matrix.py`, `seat-audit-r16-replay-*.json`, `seat-audit-replay.py`, `transcript-manifest.py`. No `gate-replays-ddb7347.json`.
- `git log --all --oneline -- census/round-17/gate-replays-ddb7347.json` → empty (never in any ref).
- `stat census/round-17/gate-replays-ddb7347.json` → No such file or directory.
- `git show b5763415…:census/round-17/gate-replays-4f48343.json`: top-level `lane_head` `4f4834390ad4845b76804e94cc04d8f867ef9b54` (:13); the `r16-precarry` block starts at :151 and holds `exit` 1 (:154), `finding_count` 29 (:155), `checked_markers` 30 (:315), SUMMARY `findings=29 … checked_markers=30` (:310), and `"rev": "79bbe7a"` with `resolved_rev` `79bbe7a62199260694943ec7186fef6ebff9d41a` (:276-277). This matches the LOG.md:915-917 wording (30 markers, 29 uncarried, exit 1).
- `git log --all -1 -- census/round-17/gate-replays-4f48343.json` → `95519a7` (round-17 landed-rev evidence commit).
- `SKILL.md:163` names the record as `census/round-17/gate-replays-ddb7347.json (L1)`; `SKILL.md:165` names `census/round-17/gate-replays-ddb7347.json` as the record in the `r17-gate-replays` row ("(committed at ddb7347) and record `census/round-17/gate-replays-ddb7347.json` (L1)").

Verdict: **fails** as written (citations point to an uncommitted file). Holds for the substance: the 4f48343 record carries the same `r16-precarry` replay (exit 1, 29 findings, 30 markers).

Smallest fix (text in §Drafts, D1 and D2; SKILL.md edit is out of this seat's scope and is routed to the SKILL scribe).

## F2 (R2b) — `jj-receipts-ddb7347.txt` was never committed; the committed records are `jj-receipts-4f48343.txt` and `jj-receipts-base5fa6017.txt`

Cited at: `corpus/knowledge/jj-colocation-receipts.md:2, 44, 126, 148`.

Evidence:
- `ls-tree` at b5763415… (above): `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt` present; no `jj-receipts-ddb7347.txt`.
- `git log --all -- census/round-17/jj-receipts-ddb7347.txt` → empty; `git ls-files --error-unmatch` → pathspec did not match; `stat` → No such file.
- `git log --all -1 -- census/round-17/jj-receipts-4f48343.txt` → `95519a7`.
- Line-by-line: the committed `jj-receipts-4f48343.txt` carries the same verdicts at the line numbers the entry cites for the ddb7347 record: `:18-19` J1/J1-vault `verdict=NOT-SAFE`; `:22-24` J3/J3-vault/J3-quarantine `verdict=NOT-SAFE` (J3-quarantine `exit=3 result=DRY-RUN-BLOCKED`); `:31-32` J9-file/J9-worktree `verdict=NOT-SAFE`. The entry's cited `ddb7347.txt:18-19, 22-24, 31-32` therefore line-match the committed 4f48343 record.
- `jj-receipts-base5fa6017.txt` at the cited lines: `:15-16` J1/J1-vault `SAFE(metadata-prune)`; `:19-21` J3/J3-vault/J3-quarantine `SAFE(pushed)`; `:28-29` J9-file/J9-worktree `SAFE`. Matches `corpus/knowledge/jj-colocation-receipts.md:126` exactly.
- The committed record header (`jj-receipts-4f48343.txt:1-4`: `TOOL-DIR`, `TOOL-BASELINE`, `GIT 2.56.0`, `JJ 0.45.1`) does NOT state the revision the fixture ran at. The entry's phrase "run at landed revision ddb7347" (`:2`) is therefore not re-observed here: [INFERENCE] the 4f48343 record is the wave-2 state, not proof of a ddb7347 run.
- `git cat-file -t ddb7347` → `commit` (the code landing exists; the record does not).

Verdict: **fails** as written (four citations to an uncommitted file); the committed 4f48343 record supports the same verdicts at the same line numbers. Revision label for the run is unobserved and must not be restated as "observed at ddb7347".

Smallest fix: §Drafts D3 (LOG correction), with a note to the knowledge scribe to repoint `:2, 44, 126, 148` to `jj-receipts-4f48343.txt` (and `jj-receipts-base5fa6017.txt` where base is cited) and to replace "run at landed revision ddb7347" with the producing-revision statement that the record actually supports.

## F3 (R3) — the live-fleet census holds 21 repositories, not 22

Cited at: `SCORECARD.md:15` ("live fleet paired rows identical (22 repos)"). The only `22 repo` / `22 rows` string in SCORECARD.md at b5763415…; LOG.md has no `22 repo`/`22 rows` match.

Evidence:
- `git show b5763415…:census/round-17/live-fleet.json`: two arms — `"rev": "5fa6017"` (:7, `rows` opens :11) and `"rev": "4f48343"` (:213, `rows` opens :217). Each row entry is 9 lines: arm 1 `rows` entries at :12–209 (22 entries), arm 2 at :218–415 (22 entries).
- 22 entries per arm = 1 header row (`["repo","worktrees","unpushed","dirty","scratch_bytes","mtime_iso","verdict_flags"]`, :12-20 / :218-226 region) + 21 repository rows.
- `grep -c` of `/home/vgpnk/Projects/shokunin/…` row openers: 42 total across both arms = 21 per arm.
- `git show b5763415…:SCORECARD.md` line 15 contains `live fleet paired rows identical (22 repos)`.

Verdict: **fails** as written: 22 is the row count including the header; the repository count is 21. Correction text D4 below. The identity claim ("paired rows identical") is not evaluated here.

# Drafts (text for the tail of LOG.md; append-only; do not edit prior entries)

## D1 — `2026-10-20 — round 18 correction: the round-17 gate-replay record is gate-replays-4f48343.json, not gate-replays-ddb7347.json`

Correction to the citations of `census/round-17/gate-replays-ddb7347.json` at LOG.md:916 (the round-16 "29, not 28" correction), SKILL.md:163 and SKILL.md:165. That path was never committed: it is absent from `git ls-tree --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 census/round-17/`, no commit in any ref touches it (`git log --all -- …`), and it is not in the working tree. The committed record is `census/round-17/gate-replays-4f48343.json` (landed in `95519a7`). Its `r16-precarry` block (`:151-…`, rev `79bbe7a` at `:277`) records `exit` 1, 29 findings and `checked_markers` 30, which is what LOG.md:915-917 states. The record names the lane head `4f48343` (`lane_head`, :13); the earlier phrase "re-measured … at rev 79bbe7a" refers to the replayed rev, not the record's file name. The commit `ddb7347` is the round-17 code landing and is unchanged by this correction.

## D2 — (SKILL.md scribe) `SKILL.md:163,165`

Same record substitution as D1: `census/round-17/gate-replays-ddb7347.json` → `census/round-17/gate-replays-4f48343.json` in the `souji-landing-gate` row (:163) and the `r17-gate-replays` row (:165). Routed to the SKILL scribe; this seat does not edit SKILL.md.

## D3 — `2026-10-20 — round 18 correction: the jj receipt records cited by corpus/knowledge/jj-colocation-receipts.md are jj-receipts-4f48343.txt and jj-receipts-base5fa6017.txt`

Correction to the citations of `census/round-17/jj-receipts-ddb7347.txt` at `corpus/knowledge/jj-colocation-receipts.md:2, 44, 126, 148`. That path was never committed (no `ls-tree` entry at b5763415…, no commit in any ref, not in the working tree). The committed records are `census/round-17/jj-receipts-4f48343.txt` (landed in `95519a7`) and `census/round-17/jj-receipts-base5fa6017.txt`. The post-fix verdicts that §4 and F-1 cite are present in the committed 4f48343 record at the cited line numbers: J1 and J1-vault `NOT-SAFE` at `:18-19`; J3, J3-vault and J3-quarantine `NOT-SAFE` at `:22-24`; J9-file and J9-worktree `NOT-SAFE` at `:31-32`. The base-arm citations `base5fa6017.txt:15-16, 19-21, 28-29` match the committed base record. The committed record does not state the revision its fixture ran at, so the entry's statement that the fixture was "run at landed revision ddb7347" is not re-observed by this correction and must not be read as observed.

## D4 — `2026-10-20 — round 18 correction: the live-fleet census has 21 repositories, not 22`

Correction to "live fleet paired rows identical (22 repos)" in SCORECARD.md:15 (the r17 C1 row; the round-17 entry at LOG.md:944-946 does not repeat the figure). The figure counted the `rows` array, which holds 22 entries per arm including the `repo` header row. `census/round-17/live-fleet.json` has two arms (`rev` 5fa6017 at :7 and 4f48343 at :213); each arm's `rows` array has 22 entries (1 header + 21 repositories). The corrected figure is 21 repositories. This entry does not evaluate the "paired rows identical" claim.

# Checks run (all read-only; exact commands and results)

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 census/round-17/` → 14 names; no ddb7347 names.
- `git -C … grep -n "22 repo\|21 repo\|22 rows\|twenty-two" b5763415… -- SCORECARD.md` → `SCORECARD.md:15` only.
- `git show b5763415…:LOG.md | grep -n '22 repo\|22 rows'` → no output. `wc -l` → 946.
- `git show b5763415…:census/round-17/gate-replays-4f48343.json | grep -n 'r16-precarry\|checked_markers\|"exit"'` → exit 1 at :154, checked_markers 30 at :142/:315, block key at :151.
- `git show b5763415…:census/round-17/gate-replays-4f48343.json | grep -n '^    "[^"]*": {'` → r13-admitted :17, r14-landing :44, r15-landing :71, r16-landing :124, r16-precarry :151.
- `git log --all --oneline -- census/round-17/gate-replays-ddb7347.json census/round-17/jj-receipts-ddb7347.txt` → empty.
- `git cat-file -t ddb7347` → commit.
- `git show b5763415…:census/round-17/jj-receipts-4f48343.txt | grep -n 'J1\|J3\|J9'` and the base-record equivalent → verdict lines as in F2.
- `git -C … ls-files --error-unmatch census/round-17/gate-replays-ddb7347.json census/round-17/jj-receipts-ddb7347.txt` → pathspec did not match.
- `stat -c '%n %s %a'` on the two ddb7347 paths → No such file or directory; on the two 4f48343 paths → 16982 and 6381 bytes, mode 644.
- `git log --all -1 -- …4f48343…` → `95519a7`.
- `git show b5763415…:census/round-17/live-fleet.json` + `grep -n` on rev/rows/row-delimiters/`/home/vgpnk/Projects/shokunin/` openers → two arms, 22 entries each, 21 path rows each.
- `git show …:SCORECARD.md | sed -n '15p' | grep -o …` → `…live fleet paired rows identical (22 repos)…`.
- `git show …:corpus/knowledge/jj-colocation-receipts.md | sed -n '2p' | grep -o 'ddb7347[^)]*'` → `ddb7347 (census/round-17/jj-receipts-ddb7347.txt`.
- `git cat-file`, `git show` of blobs only; no `jj` invoked; no git write.

# Tooling

No tool installed or upgraded. Temporary dir `/var/tmp/souji-r18-ScribeLogCorrections/` created for a scratch copy of live-fleet.json and removed (`rm -rf`, confirmed). No process started or signalled.

# Out of scope / routed

- SKILL.md:163,165 edit → SKILL scribe (D2).
- `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` repoint and the "run at ddb7347" revision statement → knowledge scribe (D3 covers the correction; the knowledge file itself is not edited here).
- SCORECARD.md:15 "22 repos" → 21 → SCORECARD scribe (D4 covers the LOG record).
- Not evaluated: whether `jj-receipts-4f48343.txt` was produced at revision 4f48343 (no revision in the file header); whether the "paired rows identical" claim holds.

# Verdict

R2a, R2b and R3 all **fail** as written at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 and are corrected by D1, D3 and D4. The replacement records hold the cited verdicts at the cited line numbers (F1, F2). Holds: the 4f48343 replay and receipt records exist and match the cited content; the base citations match.
