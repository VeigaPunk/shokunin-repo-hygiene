# R41w2reviewer04 — S258 live re-open (round 41, wave 2, falsify)

Seat: R41w2reviewer04 (reviewer, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Tip under review: 1d41c13 (`git rev-parse --short HEAD`). Scope: S258 source, its quotes, line citations, the :171-266 region claim, and the registry row shape/enums. No lane file was edited; no git mutation; no installs. Scratch: /fast/scratch/hyaku/souji-r41/R41w2reviewer04 (removed before yield).

## Commands run and observed output

1. Live fetch (both tags, raw GitHub):
```
curl -sSfL -o worktree-2.56.0.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c   # rc=0
curl -sSfL -o worktree-2.55.0.c https://raw.githubusercontent.com/git/git/v2.55.0/builtin/worktree.c   # rc=0
sha256sum worktree-2.56.0.c worktree-2.55.0.c
af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc  worktree-2.56.0.c
2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884  worktree-2.55.0.c
```
2. Against the lane snapshots and SHA256SUMS:
```
sha256sum census/round-41/sources/git-v2.56.0-builtin-worktree.c  -> af2bd523…babc
sha256sum census/round-41/sources/git-v2.55.0-builtin-worktree.c  -> 2c8e8a8e…e884
cat census/round-41/sources/SHA256SUMS -> af2bd523…babc git-v2.56.0-builtin-worktree.c ; 2c8e8a8e…e884 git-v2.55.0-builtin-worktree.c
cmp worktree-2.56.0.c  <snapshot>  -> SAME56 (identical bytes)
cmp worktree-2.55.0.c  <snapshot>  -> SAME55 (identical bytes)
wc -l -> 1541 (v2.56.0), 1493 (v2.55.0)
```
3. Quote location (`grep -n -F`):
```
grep -n -F 'prune missing working trees older than <time>' worktree-2.56.0.c  -> 255:  N_("prune missing working trees older than <time>")),   (one match)
grep -n -F ... worktree-2.55.0.c -> 255 (same string at same line in v2.55.0)
```
4. Cited lines, v2.56.0 (`sed -n` with line numbers):
- :171-177 = `static void prune_worktree(const char *id, const char *reason)` … closing `}` at :177. Matches the row's `prune_worktree() :171-177`.
- :212-246 = `static void prune_worktrees(void)` (:212) … closing `}` (:246). Matches `prune_worktrees() :212-246`.
- :229 = `\t\tif (should_prune_worktree(the_repository, d->d_name, &reason, &path, expire))`. Matches lesson text exactly.
- :254 = `OPT_EXPIRY_DATE(0, "expire", &expire,`; :255 = `N_("prune missing working trees older than <time>")),`. Matches `--expire (:255)`.
- :259 = `\texpire = TIME_MAX;` (inside the `cmd_worktree_prune` options block, before `parse_options`). Matches `default cutoff is TIME_MAX (:259)`.
- v2.55.0 counterparts: `OPT_EXPIRY_DATE` at :254, `expire = TIME_MAX;` at :259, `should_prune_worktree(d->d_name, …)` at :229 (no `the_repository`).

5. Region claim, `:171-266` (exact command from the lesson):
```
diff <(sed -n 171,266p worktree-2.55.0.c) <(sed -n 171,266p worktree-2.56.0.c)
59c59
<  		if (should_prune_worktree(d->d_name, &reason, &path, expire))
---
>  		if (should_prune_worktree(the_repository, d->d_name, &reason, &path, expire))
diff_rc=1
```
Same diff run on the committed snapshots (`census/round-41/sources/…`) gives the identical single-hunk output (rc=1). Only :229 differs in the region (59th line of the slice = file line 229). Note: the whole-file diff is 37 hunks; the row does not claim whole-file identity, so this is not a defect, only a scope fact.

6. Registry row shape (lane `corpus/SOURCES.md`):
```
sed -n 212p corpus/SOURCES.md | awk -F'|' '{print "NF="NF}'   -> NF=13 (11 cells + leading/trailing empties)
awk -F'|' '/^\| S[0-9]+ /{n++; if (NF!=13) bad++} END{print "rows="n" bad="bad+0}' -> rows=182 bad=0
```
7. CORPUS enum checks (the awk on fleet-root `CORPUS.md` lines 145/147 run against the lane registry): tier/status/kind check printed nothing (no violations). S258 cells: tier `A`, kind `code`, status `mined`, opened `2026-10-28`, recheck `on-release`. `recheck` values across the 182 rows all match `date|Nd|on-release|on-correction|on-change` (awk printed no `recheck-odd` line).
8. `used-by` for S258 = `corpus/lessons/round-41.md`; file exists (15739 bytes); `grep -c S258 corpus/lessons/round-41.md` = 7. Rule satisfied (mined requires a used-by path).
9. Append-only (CORPUS.md rule 2): `git show --numstat 31e4d3e` on corpus/SOURCES.md = `4 0` (4 insertions, 0 deletions). The diff adds the S258 row between S257 and `## Paths`, plus a search-log paragraph; no existing row changed. Commit 31e4d3e also adds `census/round-41/sources/git-v2.55.0-builtin-worktree.c` (1493 lines) and `…v2.56.0…` (1541 lines) and `SHA256SUMS` (2 lines).

Lesson Gate check: `corpus/lessons/round-41.md` line 17 row: URL matches, access date 2026-10-28, quote `"prune missing working trees older than <time>"` is 6 words (≤25), location `line 255` (verified), sha256 `af2bd523…babc` (verified), snapshot path (exists). The lesson's "Located and checked by hand" paragraph (lines 255, 229, 259 and the diff) reproduces exactly under item 3-5 above.

## Findings

F1 (calibration, moderate, teaches cell overreach — not a falsified sourced fact). S258 `teaches`: "what `git worktree prune` removes and how `--expire` gates it at git 2.56.0". The fetched builtin file shows only the call site: `prune_worktrees()` passes `expire` into `should_prune_worktree(...)` (:229) and calls `prune_worktree()` on a true result, which runs `delete_git_dir(id)` (:171-177). The eligibility predicate itself is not in this file (grep for its definition in the v2.56.0 builtin file: only the call at :229). So the builtin shows the default cutoff (:259) and the call, not what is removed nor how `--expire` gates the removal. The row's scope cell does state this ("the library's eligibility test `should_prune_worktree()` … is not read here"), so the claim is bounded by the scope column, but the teaches cell itself reads as a removal-behaviour claim. Recommended wording (for the scribe, not applied by me): "the builtin call site and the default `--expire` cutoff at git 2.56.0; the removal predicate is unread." Verdict on the row's facts: all located facts verified; the teaches phrasing is broader than what was read.

F2 (minor, scope note). The lesson says S009's v2.55.0 pin "whose own note says the v2.56.0 recheck is pending" (lesson line ~37 of the r41 section). Not opened by me (outside S258). Not verified here.

F3 (minor, location). The task text says "under CORPUS.md"; the lane has no `CORPUS.md`. The governing file is the fleet-root `/home/vgpnk/Projects/shokunin/CORPUS.md` (enum awk at its lines 144-147; rules at :86-125) and the contract `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md` (fleet root). I used those. The wording "valid under CORPUS.md" is therefore satisfied against the fleet-root copy.

F4 (minor, scope). The lesson/row claim "differs between tags only at :229" is correct for :171-266 only. The whole files differ in 37 hunks (`diff worktree-2.55.0.c worktree-2.56.0.c | grep -c '^[0-9]'` = 37). The row does not claim otherwise; flagged so any later "v2.56.0 re-pin of S009" wording does not widen it.

F5 (minor, provenance). The lesson's account that scribe R41scribe04 quoted the sha256 with transposed characters is historical and not re-checkable here; the figure the lesson and row now use (`af2bd523…babc`) matches my live hash.

## Verdict

S258 CONFIRMED on every located fact: both tags fetched live with the hashes recorded in `census/round-41/sources/SHA256SUMS`, `SOURCES.md` S258 and `lessons/round-41.md`; the quote is at line 255 (only match); :171-177, :212-246, :229, :254-255 and :259 are as cited; the :171-266 region differs between tags only at :229; the registry row has 13 awk fields (11 cells), tier A / kind code / status mined / valid dates and recheck, with `used-by` pointing to an existing lesson that cites S258; the registry change is a pure append (4 insertions, 0 deletions). One calibration defect remains (F1): the S258 teaches cell reads as a claim about what prune removes and how `--expire` gates removal, which the fetched builtin file does not establish; the scope column limits this but the teaches text should be narrowed. Admission of the row's located facts stands; the teaches wording is a recommended fix, not a falsification of C1 item I1.

Residual risk / gaps: the library `worktree.c` (`should_prune_worktree()`) was not fetched (out of scope by the row's own scope). Checks for the calibration of other lesson CORRECTION lines (I1, I3, I4) were not run.

Installs/updates: none.
