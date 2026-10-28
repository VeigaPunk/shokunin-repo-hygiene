# R41scribe05 — S258 draft row (round 41, wave 1, role scribe)

## Scope
Draft ONE corpus/SOURCES.md registry row, S258, anchored on git `worktree prune` at tag v2.56.0 (`builtin/worktree.c`). Read-only on the lane: the only file written is the draft under this seat directory. No tracked file, registry, lesson, census, tool or candidate directory was touched; no git or jj mutation was run.

## Commands run and observed output

1. Fetch the upstream file at tag v2.56.0 (scratch dir `/fast/scratch/hyaku/souji-r41/R41scribe05/`):
   `curl -fsSL -o .../worktree.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c` → exit 0 (fetch succeeded).
   `sha256sum worktree.c` → `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc`; `wc -l` → `1541`.

2. Fetch the v2.55.0 file for the what-changed comparison:
   `curl -fsSL -o worktree-v2.55.0.c https://raw.githubusercontent.com/git/git/v2.55.0/builtin/worktree.c` → exit 0.
   `sha256sum` → `2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884`; 1493 lines.

3. Read the lane's required context: `/home/vgpnk/Projects/shokunin/CORPUS.md` lines 60-120 (section `SOURCES.md — where a shokunin learns`). The section is NOT in the lane root: the lane has no CORPUS.md; the fleet-root file `/home/vgpnk/Projects/shokunin/CORPUS.md` holds it. Rules read: "A row is a claim", "Append-only", id `S` + 3 digits, no `|` in cells, tier A = primary source code at revision, `status` `mined` requires a used-by path, `opened`/`recheck` fields, Gate needs URL + access date + ≤25-word quote with location.

4. Read `corpus/SOURCES.md` S009 (line 38) and S232 (line 185); the table header is line 28 with 11 columns; the last row present is S257 (line 211), so S258 is the next unused id.
   S009: "git/git source at tag v2.55.0: builtin/gc.c, worktree.c, run-command.c, builtin/commit.c", anchor lines `worktree.c:954-956, :1001-1008`, teaches "worktree-prune (SCHEDULED and MANUAL) runs worktree prune --expire 3.months.ago; locked dirs skipped; missing worktrees prune once index mtime passes expiry".
   S232: the git-worktree(1) `prunable` label and LIST OUTPUT FORMAT (docs, not code). S258 does not duplicate either.

5. Locate lines in the v2.56.0 file:
   `sed -n '170,266p' worktree.c | nl -ba -v170` (listing) and `grep -n -E 'prune|expire|locked|prunable' worktree.c`. Results:
   - 149-162 `delete_git_dir`: `remove_dir_recursively` on `worktrees/<id>` under the common dir.
   - 171-177 `prune_worktree`: prints `Removing worktrees/<id>: <reason>` when `show_only || verbose`; calls `delete_git_dir(id)` only when `!show_only`.
   - 201-210 `prune_dups`: removes later entries with the same path, reason `"duplicate entry"`.
   - 212-246 `prune_worktrees`: iterates `worktrees/` entries; line 229 `if (should_prune_worktree(the_repository, d->d_name, &reason, &path, expire)) prune_worktree(d->d_name, reason.buf);` else keeps the path for dup detection; then `delete_worktrees_dir_if_empty` unless `show_only`.
   - 248-266 `prune`: `OPT__DRY_RUN` line 252 ("do not remove, show only"), `OPT__VERBOSE` line 253, `OPT_EXPIRY_DATE(0, "expire", ...)` lines 254-255 with help text `prune missing working trees older than <time>`; line 259 `expire = TIME_MAX;`.
   - `should_prune_worktree` is called at line 229 but NOT defined in this file (`grep -n should_prune_worktree` → only line 229). The lock decision for prune therefore is not visible in these bytes. The only lock references in prune's path are none; lock checks in this file (lines 329, 1025, 1072, 1203, 1239, 1339, 1451) belong to add/list/lock/unlock/move/remove.

6. Uniqueness of the quote:
   `grep -n -F 'prune missing working trees older than <time>' worktree.c` → `255:				N_("prune missing working trees older than <time>")),`
   `grep -c -F ...` → `1`.

7. v2.55.0 vs v2.56.0 prune region:
   `diff <(sed -n '/^static void prune_worktree(/,/^static char \*junk_work_tree/p' v2.55.0) <(... v2.56.0)` → one hunk: `59c59` `if (should_prune_worktree(d->d_name, ...` vs `if (should_prune_worktree(the_repository, d->d_name, ...`; exit 1 (difference). Same check for the delete_git_dir..delete_worktrees_dir_if_empty span → exit 0 (identical).
   Function line numbers identical in both files (delete_git_dir 149, prune_worktree 171, prune_cmp 179, prune_dups 201, prune_worktrees 212, prune 248); `awk 'NR>=171 && NR<=266'` on both files → single `diff`: `59c59` only (line 229 in file terms).
   `grep -n TIME_MAX|OPT_EXPIRY_DATE` on v2.55.0 → 254, 259 (same as v2.56.0 lines).
   Whole-file `diff` (v2.55.0 → v2.56.0, 37 hunks) shows other changes (`the_repository` threading, `worktree_basename_dup`, `advise_disambiguating_remotes`, `dwim_branch(&opts, ...)`). Filtering hunk start lines to 165-270 (`diff ... | grep -E '^[0-9]' | awk -F'[acd,]' '{print $1}' | sort -n | awk '$1>=165 && $1<=270'`) leaves only `229`, the same should_prune_worktree call; no other hunk touches the prune functions.

8. Row shape check:
   `grep '^| S258 ' S258-row.md | awk -F'|' '{print NF-2}'` → `cells=11`; `grep -c '^| S258 '` → `1`.

9. Receipts copied into this seat directory (the citable copies; the scratch dir is removed):
   `sha256sum receipt-builtin-worktree-v2.56.0.c` → `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc`
   `sha256sum receipt-builtin-worktree-v2.55.0.c` → `2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884`
   `grep -n -F 'prune missing working trees older than <time>' receipt-builtin-worktree-v2.56.0.c` → `255:...`; count `1`.
   `rm -rf /fast/scratch/hyaku/souji-r41/R41scribe05` → removed.

Tool installs/updates: none. Nothing installed, upgraded or invoked beyond `curl`, `sha256sum`, `grep`, `diff`, `awk`, `sed`, `nl`, `wc`.

## Evidence pointers
- Draft row and Gate: `.ufo/waves/round-41/w1/R41scribe05/S258-row.md`
- Upstream receipt (v2.56.0, sha256 af2bd523…babc, 1541 lines): `.ufo/waves/round-41/w1/R41scribe05/receipt-builtin-worktree-v2.56.0.c`
- Comparison receipt (v2.55.0, sha256 2c8e8a8…e884, 1493 lines): `.ufo/waves/round-41/w1/R41scribe05/receipt-builtin-worktree-v2.55.0.c`
- Quote: `builtin/worktree.c` line 255 at tag v2.56.0.

## Gate values (for the L1's lesson Gate)
- URL: https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c
- Access date: 2026-10-28
- Line: 255
- Quote (7 words, verbatim): "prune missing working trees older than <time>"

## Findings for the L1 (not edits)
1. The lock skip that S009 teaches ("locked dirs skipped") is decided in `should_prune_worktree()`, which lives outside `builtin/worktree.c`. This file cannot anchor the locked-entry claim; S258's row therefore disclaims the lock check rather than asserting it. S009's `worktree.c:954-956, :1001-1008` anchors (lib-level file) were not fetched by this seat and remain unverified here.
2. The S009 `teaches` text ("worktree-prune ... runs worktree prune --expire 3.months.ago") concerns gc's caller in `builtin/gc.c`, not this file. S258 does not restate it.
3. The `used-by` value `corpus/lessons/round-41.md` must exist when the row lands, since the row's status is `mined`; the lesson is written by the L1 or another seat in this round.
4. The lesson CORRECTION line for S009 is not in this seat's scope (C1 is another seat's item).

## Verdict
PASS for the drafted row and its evidence: the upstream fetch succeeded, the sha256 and line 255 quote were observed with the commands above, the quote occurs exactly once, the row has 11 cells, and the v2.55.0→v2.56.0 prune-region comparison is recorded. The lock-skip claim in the task is NOT anchored by this file and is explicitly excluded from S258 (finding 1); it is not claimed as passed.
