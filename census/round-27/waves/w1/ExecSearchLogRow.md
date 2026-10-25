# ExecSearchLogRow — SOURCES Search log draft, round 27 wave 1

## Status

STATUS: PASS — both PRISMA blocks drafted with grounded counts; delivery files written under `.ufo/waves/round-27/w1/` only.

## Evidence

- Rev: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba` (frozen base). Read-only; no git writes.
- Frozen contract: `.ufo/waves/round-27/preregistration.txt` C2 names the re-grounding (`gio/glocalfile.c`, `glib/gfileutils.c`, tag 2.84.0, own access date, ≤25-word quotes) and the S152/S210/S211 rows.
- GLib snapshots opened this run from raw.githubusercontent.com GNOME/glib 2.84.0:
  - `gio/glocalfile.c`: `g_local_file_trash` :1993–2360; unique-name loop :2254–2256; relative-origin + URI-escape :2337–2338; record payload :2352; content write :2357–2359; rollback :2361; interface binding :3147. Quote (:2352): `data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", original_name_escaped, delete_time);` (7 words).
  - `glib/gfileutils.c`: `g_file_set_contents_full` :1327; flags doc :1341. Quote (:1341): `*  - %G_FILE_SET_CONTENTS_CONSISTENT: write to temp file, fsync() it, rename()` (10 words).
- Slice probes (2026-10-25): `curl -sL -o /dev/null -w '%{http_code} %{size_download}'` → man7.org statx(2) `200 33125`; qiita.com `gc.auto` `200 129547`; git-scm.com git-worktree `200 98918`; git-scm.com gitrepository-layout `200 64401`.
- Slice reads: `.ufo/waves/round-26/assimilation/quarantine-slice` contains 8 rows; identical content observed in `census/round-22/attempt2/quarantine-slice` and `census/round-24/records/quarantine-slice`. `corpus/SOURCES.md` has rows S114/S118/S123/S124/S126/S131; `grep` for S133/S138 rows → no match.
- S131 path probe: `test -e /home/vgpnk/Projects/shokunin/lanes/souji/round2/fixtures/r23-trigger-prune.sh` → ABSENT.
- Tools installed: none.

## Findings

1. Writer located: `g_local_file_trash` in `gio/glocalfile.c@2.84.0` (:1993–2360, bound at `iface->trash` :3147) writes each per-item origin record (Path + DeletionDate, :2352–2359) via `g_file_set_contents_full` (S210). The atomic-consistent write primitive is `g_file_set_contents_full` in `glib/gfileutils.c@2.84.0` (:1327, flags doc :1341) (S211). Both included; excluded 0.
2. The quarantine-slice file is carried forward byte-identical across `census/round-22/attempt2/`, `census/round-24/records/`, and `.ufo/waves/round-26/assimilation/`; its S133/S138 entries have no current lane registry row (stale).
3. Five of eight slice entries (S114, S118, S123, S124, S126) returned HTTP 200 with non-empty payloads this run; S131's cited path remains absent; re-opening/clearing those rows is a SOURCES write owned by the L1.

## Attack log

None — this item is a draft note, not a counter; no predicate, target, counter or case set touched.
