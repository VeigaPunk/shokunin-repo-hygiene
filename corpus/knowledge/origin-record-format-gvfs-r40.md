source: S254 GNOME/gvfs 1.62.0 daemon/trashlib/trashitem.c — https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c (tag 1.62.0, lines 158, 173, 180, 182, 193; snapshot census/round-40/sources/gvfs-trashitem-1.62.0.c sha256 3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b; opened 2026-10-28) — assimilated from the shokuknow campaign package `merge/souji/` (staged id S146), re-pointed by document to this lane's id space
verified-at: 2026-10-28 — GVFS tag 1.62.0; the file was fetched and the quoted lines read; the normative specification the lane already holds is S022 (FreeDesktop.org Trash Specification)
recheck: 365d — re-fetch the file at tag 1.62.0: `curl -sS https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c | sha256sum`
ground: F4 — restorable quarantine, file-system semantics (the per-item origin record's exact on-disk shape as a reference implementation reads it)

# A per-item origin record is a two-key key-file: a second reference implementation confirms it

## Claim (F4, sourced at a pinned revision)

GVFS's trash reader parses a per-item origin record as a GKeyFile with ONE group and TWO keys:

1. **The path template.** `trash_item_get_trashinfo()` builds it at line 158:
   `trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", trashpath, basename);` — the record sits at
   `info/<basename>.trashinfo` beside the `files/` payload directory.
2. **The group and the keys.** Line 173 reads `"Trash Info", "Path"` and line 193 reads
   `"Trash Info", "DeletionDate"` — one group, two keys.
3. **The path value is escaped and may be relative.** Line 180 is
   `decoded = g_uri_unescape_string (orig, NULL);` and line 182 is
   `if (g_path_is_absolute (decoded))` — an absolute path is taken as-is, a relative one is resolved
   against the top directory.

For souji this settles the READ side of the per-item origin record: a record must carry the original
path in ESCAPED form, the deletion date, and the base directory a relative path is read against.

## Why it is new ground, and what it is not

The lane already holds the normative specification (S022) and the write side (GLib's own writer,
S210 / `corpus/knowledge/origin-record-writer-r27.md`). GVFS contributes a SECOND, independent
reference implementation — one that only READS the record — and it agrees with the specification
rather than replacing it. That cross-check is the new ground; the constraints the lane already holds
(S022's write-first/`O_EXCL` ordering, S212's POSIX exclusive-creation guarantee) are unchanged and
are re-pointed here BY DOCUMENT, not by arithmetic: the staged package's ids for those documents
differ from this lane's ids, so the citations name S022 and S212 explicitly.

## What this does NOT establish

- **No writer.** GVFS's trashlib contains no writer of the record; the component that writes one is
  still open, and this entry does not claim a writer.
- **Not normative.** The FreeDesktop.org Trash Specification (S022) is; this row is the
  implementation cross-check, cited at a pinned tag.
- **No atomicity.** `O_EXCL` appears in neither GVFS nor this reader; the exclusive-creation rule
  comes from S212 and S022.
- **No lane behaviour change.** Nothing in the lane's tools was changed by this entry; it is a
  knowledge row about the record's shape.

## Provenance of the assimilation

Adopted from `/home/vgpnk/Projects/shokuknow/merge/souji/` (staged entry
`origin-record-format-gvfs-r26.md`, staged row id S146). The staged id space collides with the
lane's live registry on 58 ids (the package was built when the lane's registry held 108 rows; the
lane's own rounds have since opened rows with those ids for DIFFERENT documents), so the id was
re-pointed by document: this lane's id for the GVFS file is S254. The collision census and the L0
question it raised are in `corpus/lessons/round-40.md` `## Gate` and in
`.ufo/l0-questions.md` (`souji | round-40`).

## Round 40 wave-2 correction (append-only)

Wave-2 review found three overstatements above; read this block as superseding those sentences:

- The reader QUERIES `Path` and `DeletionDate`; it does not require both to be present. Missing
  `Path` is accepted and sets the returned original path to NULL (`S257`,
  `corpus/knowledge/origin-record-format-gvfs-read-boundary-r40.md`).
- The source is a corroborating implementation view on F4, not “new ground” outside the lane's
  already-held F4 ground.
- The package/live registry share 58 IDs, but 3 shared IDs name the same source document; staged
  S146 is free in the lane's ID set. S254 was selected because IDs are append-only and S254 was the
  next unused ID, not because S146 collided. The correction and operator question are recorded in
  `corpus/lessons/round-40.md` and `.ufo/l0-questions.md`.
