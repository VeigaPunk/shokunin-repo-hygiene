# W2Inherited — re-check of the inherited round-23 late seat updates

Seat: L1Souji24.W2Inherited (scout, wave 2). Scope: the two uncommitted round-23 seat reports `.ufo/waves/round-23/w2/W2K1.md` and `W2D3.md`, compared against `.ufo/waves/round-24/w1/ScoutInherited.md`, plus the commit-or-leave recommendation under the round-24 prompt's §6 item 5.

## Status
STATUS: PASS. Both files are byte-for-byte as wave 1 found them. Nothing in the round-23 tree has been written for about 30 minutes. Wave 1's "leave" recommendation is **falsified**: the inherited-state rule allows only commit or revert. Recommendation: **commit both files in one separate, labelled commit under round-24's LOG entry. Do not leave them, and do not revert them.**

## Evidence
All commands were read-only against the lane. Times are -0300. No scratch was created.

1. **Tip.** `git rev-parse master` returns `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, not the assigned `ca7fc1c`. `git merge-base --is-ancestor ca7fc1c master` succeeds, and the only commit after it is `c3ca7ad 06:35:24 round-24: wave-1 seat reports, drafts and registry (38 seats)`. `git diff --name-only ca7fc1c master` lists 46 files, none under `round-23`. `git diff --name-only a65fac9 master` shows no `round-23` or `corpus/lessons` path either, so nothing landed since the lane base touches the inherited files.
2. **`git status --porcelain` at 06:38:28.**
   - ` M .ufo/waves/round-23/w2/W2D3.md`
   - ` M .ufo/waves/round-23/w2/W2K1.md`
   - ` M .ufo/waves/round-24/make-spec.py` (new since wave 1)
   - ` M corpus/QUALITY.md` (new since wave 1)
   - `??` entries: `.ufo/waves/round-24/w2-dispatch.json`, `w2-dispatched.txt`, `w2-spec.json`, `w2-validate.err`, `w2/`, and `census/operator-sweep-20261019/`. The census directory is operator-owned and was not read.
3. **Committed blobs have not moved.** `git show <rev>:<path> | sha256sum` (first 16 hex digits) gives the same values at `a65fac9`, `f9db218`, `ca7fc1c` and `master`: W2K1 `2718710ff151d9e6`, W2D3 `8ebdc4d3bca9e826`. `git diff master -- <both>` and `git diff f9db218 -- <both>` both hash to `e5a60644838e88eb…`, so the worktree diff is identical whether measured against wave 1's HEAD or the current tip.
4. **The worktree diff matches what wave 1 recorded.** `git diff --numstat`: W2D3 `12 1`, W2K1 `88 131`. This is the same as ScoutInherited Evidence 2 ("+88/−131" and "+12/−1"). Current worktree sha256: W2K1 `b959e86bd88318522c1dd5df22dfcf3635ce66df160706c056ec25dcd84c2f2b` (6401 B), W2D3 `fdea4dca1aac34e7cf66d9a5fb6f640e2ddd2f550d2e22b414a3a02850840cd9` (18731 B). Wave 1 recorded no worktree digest; I treat the files as unchanged because the numstat and mtimes match and both mtimes are earlier than wave 1's report (06:21:37).
5. **Is the round-23 seat still writing? No write since 06:09:40.**
   - `stat`: W2K1 `06:08:37.430`, W2D3 `06:09:40.820`. Clock at check: `2026-10-25T06:39:36-03:00`.
   - `find .ufo/waves/round-23 corpus/lessons -newermt 2026-10-25T09:04:05Z` (that is, after round-23 `complete`) returns only W2D3 06:09:40, W2K1 06:08:37, and `corpus/lessons/round-23-verifier-spotcheck.md` 06:06:28. The spot-check file is committed and not dirty.
   - `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:1289`: "2026-10-25T06:04:05-03:00 complete souji round=23; hyaku-inline attempt=1". `:1296` launches round 24. There is no `lane-dead-no-report souji round=24` line (grep `souji`, last 5 lines).
   - `L1Souji23.W2K1` and `L1Souji23.W2D3` are not in my visible peer roster. A live /proc census is out of bounds.
6. **What the late text adds (re-read this run).** W2D3 replaces one line (the verdict) and appends section A6. In A6, `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w2/W2D3.md` (diff hunk @@ -160): "M3c is the same class as W2K1's open F2 (`0a5c2cd3`: wrong C1-row tuples bound elsewhere, a correct decoy at the receipt rev, M=0)". W2K1's worktree headings now read `### F1 — closed by c872eec`, `### F3 — closed by c872eec`, and `### F4 (MEDIUM) — last-match parsing accepts a trailing shadow after stdout`. W2D3's `STATUS:` line 1 is unchanged, so `corpus/lessons/round-23.md:189`, which quotes it, still matches.
7. **The rules (opened this run).**
   - `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-24.md:331-332`: "Uncommitted lane-authored leftovers → resolve per PROTOCOL (commit under this round's entry or revert) and name them in the report."
   - `/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/PROTOCOL.md:192-194`: "uncommitted *lane-authored* changes it finds are uncommitted round work under the landed-means-committed rule — the new lane resolves them (commit-under-its-entry or revert)".
   - `PROTOCOL.md:137-139`, on filed reports: "an erratum appended after the filed bytes in a new commit and naming the text it supersedes — never a rewrite of the filed bytes".
   - Precedent, `/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md:1608`: "D1: the seven inherited round-22 leftovers are committed here", in commit `4765250`.
8. **Prior citations.** `corpus/lessons/round-23.md:144-147` (committed): "switched counts parsing to last-wins so a pre-fence summary line cannot shadow the measured output. All three holes now have fixture cases". `:197` lists W2K1 as "STATUS: (none) — wave-2 verdict: mixed". The preregistration and amendment-1 do not mention `inherit`, `round-23/w2`, `W2K1`, `W2D3`, `trailing` or `shadow` (rg returned no hits), so committing these files does not touch any C1/C2/C3 case set.

## Findings
1. **No change since wave 1.** The committed blobs, the worktree diff and the mtimes all match what ScoutInherited saw (Evidence 3–5). Its Findings 1–3 still apply as written.
2. **The round-23 seat is quiescent, but I cannot prove it is dead.** Its last write was at 06:09:40, more than 30 minutes before this check. No round-23 path has been written since, and its round is closed (watchdog.log:1289). [INFERENCE] The seat finished just after round-23 `complete` and its final write was never collected. Its process state is still unknown (no /proc census). Mitigation: re-run `git status --porcelain` on these two paths just before the round-24 report commit. Any new dirty bytes would mean a later write that needs its own disposition.
3. **ATTACK, wave-1 recommendation falsified.** ScoutInherited Finding 5 says "leave both files for their authors". Both files were written by a souji seat (L1Souji23.W2K1 / L1Souji23.W2D3), so they are lane-authored. They are not operator sweeps, `round-*-aggregator-*`, or `round-*-verifier-spotcheck.md`. Under §6 item 5 and PROTOCOL.md:192-194 (Evidence 7), lane-authored leftovers must be committed under this round's entry or reverted before the report is filed. "Leave" is not an allowed outcome. If they stay dirty, the round-24 report would file with uncommitted lane round work.
4. **Commit, not revert.** Reverting would discard verified content that no committed byte holds:
   - W2K1 F4, the trailing-shadow false green, which ScoutInherited reproduced independently (its Evidence 6, M-a).
   - W2D3 A6's statement that M3c is "still false green" at `eb1aa49`.
   - W2K1's F1/F3 closure notes.

   Committing loses nothing, because the superseded text stays addressable at `2f96bf4`. The precedent at LOG.md:1608 is the same disposition, applied one round earlier.
5. **How to commit it.** Apply PROTOCOL.md:137-139 by analogy [INFERENCE: that rule names filed lane reports, not wave seat reports]. A rewrite must be disclosed as superseding the earlier text.
   - Make one separate commit containing **only** the two paths. Suggested label: `round-24: inherited round-23 late seat updates (W2K1 06:08:37, W2D3 06:09:40; written after round-23 complete 06:04:05; supersede 2f96bf4 text; not round-24 claim evidence)`.
   - Add a round-24 `LOG.md` entry that names the commit, the supersession and this report.
   - Do not fold in `make-spec.py` or `corpus/QUALITY.md` (Finding 6), and do not fold the files into a claim commit.
   - W2D3 is nearly append-only (one verdict line replaced, A6 appended). W2K1 is a full body rewrite (+88/−131). The supersession note matters most for W2K1.
   - A stricter alternative is to restore W2K1's committed bytes and append the late text as a dated erratum section. That keeps the record append-only, at the cost of editing a seat's file. This choice belongs to the L1.
6. **Two new dirty files are not inherited state.** `.ufo/waves/round-24/make-spec.py` (mtime 06:36:58; the diff adds `wave2()` with `TIP = "ca7fc1cb…"`) and `corpus/QUALITY.md` (mtime 06:38:04; adds `## Round 24 criteria` / Q56) were written after `c3ca7ad`, during this wave. [INFERENCE] They are the live round-24 L1's own work in progress, so they need no inherited disposition. They must still be committed under round 24 before the report.
7. **The round-23 lesson is contradicted, and the fix belongs in round-24 bytes.** `corpus/lessons/round-23.md:144-147` claims last-wins closes shadowing and that "All three holes now have fixture cases". The late W2K1 F4, and ScoutInherited's M-a reproduction, show a trailing post-stderr shadow that still gives a false green. Per PROTOCOL.md:137-139, record the correction in round 24's own report or lesson, citing the inherited commit. Do not rewrite the published round-23 lesson.
8. **The assigned tip is stale by one commit.** The seat goal names `ca7fc1c` as the lane tip, but master is `c3ca7ad`, which adds only wave-1 reports (Evidence 1). This does not affect the inherited files.

## Attack log
| # | target | attack | result |
|---|---|---|---|
| A1 | ScoutInherited "unchanged inherited state" | Hash the committed blobs at 4 revisions, hash the diff against 2 bases, compare numstat and mtimes | survives (no change) |
| A2 | "seat may still be writing" | `find -newermt` after round-23 complete; clock vs mtime; watchdog | survives as quiescent (no write in 30 min); liveness unresolved |
| A3 | ScoutInherited Finding 5 "leave" | Check against prompt §6 item 5 and PROTOCOL.md:192-194 | **falsified**: leave is not an allowed outcome for lane-authored leftovers |
| A4 | "committing rewrites a cited record" (wave-1 reason) | Check which committed bytes cite the changed text (lesson :189 quotes W2D3 STATUS, unchanged; :197 has no W2K1 quote; preregistration has no reference) | reason weakened: only lesson :144-147's claim is contradicted, and that is fixed in round-24 bytes |

## Tooling
None installed or updated. Used git and python3 already on the host (wave-1 recorded git 2.56.0). No scratch directory was created.
