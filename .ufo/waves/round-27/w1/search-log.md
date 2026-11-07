# Round 27 wave 1 — SOURCES Search log draft (for `## Search log` continuation)

Seat: ExecSearchLogRow. Measured 2026-10-25 at lane base `e78ac7c4837b81b634db4a927605a751a7f006ba`. No universal claims.

## F4 origin-record re-grounding (GLib tag 2.84.0)

- **Question.** Which GLib bytes define who writes a per-item origin record, and with which mechanisms?
- **Where searched.** raw.githubusercontent.com GNOME/glib tag 2.84.0 files: `gio/glocalfile.c`, `glib/gfileutils.c`. Date: 2026-10-25.
- **Identified 2, screened 2, included 2 (S210, S211), excluded 0.**
- **S210 — gio/glocalfile.c@2.84.0**: `g_local_file_trash` (lines 1993–2360; bound to `iface->trash` at :3147) is the writer of the per-item origin record: it builds the info payload and writes it via `g_file_set_contents_full`. Verbatim, :2352: `data = g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", original_name_escaped, delete_time);` Mechanisms: trash-dir selection (home data `Trash` / topdir `.Trash` / `.Trash-$uid`, :2075–2155); unique info filename `get_unique_filename` (:2254–2256); relative-origin path `try_make_relative` + `g_uri_escape_string` (:2337–2338); GDateTime deletion date (:2340–2350); atomic write, mode 0600 (:2357–2359); `g_unlink` rollback on write failure (:2361).
- **S211 — glib/gfileutils.c@2.84.0**: `g_file_set_contents_full` (:1327) is the write mechanism the writer calls: uniquely named temporary file, `fsync()`, then rename, under `G_FILE_SET_CONTENTS_CONSISTENT | G_FILE_SET_CONTENTS_ONLY_EXISTING`. Verbatim, :1341: `*  - %G_FILE_SET_CONTENTS_CONSISTENT: write to temp file, fsync() it, rename()`
- **Stop rationale.** The normative record format remains the FreeDesktop trash spec (Path + DeletionDate in `<name>.trashinfo`; info written first, atomically), already held as S022; the writer and its mechanism are located, so no further search is useful.

## Quarantine-slice re-open

- **Question.** Are the payloads behind the 8 quarantined source IDs now verifiable, so the carried-forward slice can be re-opened?
- **Where searched.** Lane `.ufo/waves/round-26/assimilation/quarantine-slice` (identical content in `census/round-22/attempt2/quarantine-slice` and `census/round-24/records/quarantine-slice`), current `corpus/SOURCES.md` rows, live probes of the cited URLs. Date: 2026-10-25.
- **Identified 8, screened 8, included 5 (S114, S118, S123, S124, S126), excluded 3 (S131, S133, S138).**
- Included: each cited URL returned HTTP 200 with a non-empty payload this run — S114 man7 statx(2) (33125 B), S118 Qiita `gc.auto` (129547 B), S123/S126 git-worktree(1) (98918 B), S124 gitrepository-layout(5) (64401 B).
- Excluded: S131 — cited own-work path `lanes/souji/round2/fixtures/r23-trigger-prune.sh` is still absent (lane and fleet root); S133 and S138 — no matching row exists in the current lane registry, so there is nothing to re-open.
- **Stop rationale.** The slice is a carried-forward artifact (unchanged across three copies); five of eight entries are fetchable today. Clearing or renaming those rows is a SOURCES write owned by the L1, outside this draft.
