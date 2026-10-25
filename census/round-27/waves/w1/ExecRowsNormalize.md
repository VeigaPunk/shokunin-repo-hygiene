# ExecRowsNormalize — round-27 w1 report

## Status
STATUS: PASS — normalized 11-column SOURCES rows S152/S210/S211 delivered as draft append block (`.ufo/waves/round-27/w1/rows-append.md`) and verified against the fleet census: `sources-census.sh validate` rc 0 with no E findings, registry rows 132→135, all three rows `awk -F'|' NF==13`.

## Evidence
- Staged source read: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:50` (S152), `:108` (S210), `:109` (S211) — raw rows carried status=mined, opened 2026-10-23/24, recheck prose `365d — re-fetch …`, and S152 cells with escaped pipes `O_CREAT\|O_EXCL`.
- Anchor re-verification by own fetch this run (GLib tag 2.84.0 raw files):
  - `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c:2250-2395` shows `fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);`, `(void) g_close (fd, NULL);`, `g_uri_escape_string (original_name, "/", FALSE);`, `g_strdup_printf ("[Trash Info]\nPath=%s\nDeletionDate=%s\n", …)`, `if (g_rename (local->filename, trashfile) == -1)` with `g_unlink (infofile);` — matches staged anchors 2261/2256/2340/2354/2359/2383/2288/2363/2387.
  - `https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c:1035-1048,1360-1375,1690-1700,1100-1115` shows `rename_file()` `g_rename (old_name, new_name)`, `%s.XXXXXX` template, `g_mkstemp_full (tmp_filename, O_RDWR | O_BINARY | O_CLOEXEC, mode)`, `g_mkstemp_full` passing `flags | O_CREAT | O_EXCL`, and the `G_FILE_SET_CONTENTS_ONLY_EXISTING` lstat/ENOENT block — matches staged anchors 1041/1367/1369/1697/1108. No anchor re-pointing needed.
- Normalization applied (raw → delivered): `opened` → 2026-10-25 (admission date); `recheck` prose stripped to `365d`; S152 escaped pipes → `/` (`O_CREAT/O_EXCL`); `teaches` condensed to 23/25/25 words (≤25); stage URL/anchor evidence kept verbatim; `used-by` = `corpus/knowledge/origin-record-writer-r27.md` (S152) and `corpus/knowledge/origin-record-mechanism-set-r33.md` (S210/S211).
- Census verification (byte-exact delivered rows inserted after S132 in a `/var/tmp` mirror of the lane, origin-record files present):
  - `sources-census.sh validate --file …/corpus/SOURCES.md --today 2026-10-25` → rc 0; no E findings; only `W04 S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes` (warning, exit unaffected; S152/S210 share the pinned tag URL under different scopes, so no E04).
  - `sources-census.sh census --file …` → `file rows 135`, `tier.A 128`, `status.mined 111`.
  - prereg count regex `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 135 (base 132).
  - `awk -F'|'` on the 3 rows → NF=13 each (11 columns + fence pipes); no literal or escaped `|` inside any cell (grep -F '\|' on rows → no match).

## Findings
1. Staged S152 carried an escaped pipe inside two cells (`O_CREAT\|O_EXCL` in anchor and teaches). The census row parser splits on `|`, so an escaped pipe still splits and raises E01; replaced with `/` in both cells (deliverable rows-append.md).
2. Staged `recheck` cells were cadence-plus-prose (`365d — re-fetch …`). E09 rejects non-ISO/non-cadence/non-symbolic values; stripped to plain `365d` per instruction.
3. Staged `opened` (2026-10-23/24) reset to 2026-10-25, today's ISO date per instruction; passes E08 (present, not future).
4. Staged `teaches` cells exceeded 25 words; condensed (23/25/25) preserving the grounded claims: exclusive create, URI-escaped Path, info-before-payload ordering, rollback unlink (S152); reservation-vs-write, empty-record window (S210); temp-file O_EXCL + ONLY_EXISTING destination flag (S211).
5. `used-by` targets (origin-record-writer-r27.md, origin-record-mechanism-set-r33.md) do not yet exist in the lane's `corpus/knowledge/` (they are staged in `/home/vgpnk/Projects/shokuknow/merge/souji/` awaiting C2 admission). E11 therefore fires until C2 lands them; verified clean in the mirror with the staged files present. Integrator should land C2 entries alongside these rows in one commit.
6. S210 shares the S152 URL (same pinned tag file) under a different scope — W04 warning only; no E04.

## Attack log
No attack raised. Counters, predicates and case sets were used as frozen; no gameable counter observed in the rows scope.
